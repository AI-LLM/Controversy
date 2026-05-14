# 2026-05-14：SDLC 栈 / 代码索引与 MCP 层深度研究

> 系列子报告：软件开发栈 Pre-Coding-Agent vs Post-Coding-Agent。本篇覆盖 D8.5（代码索引 / RAG-for-code）与 D6.6（Dev-MCP server）层。范本：namespace.so 范式——挖本质，不堆现象。

这一层在 Pre-Agent 时代**不存在**。Pre-Agent 时代的"代码上下文获取"是开发者大脑里完成的：grep 一遍、按 F12 跳定义、Sourcegraph 搜一个符号、ctags 跳几下，**结果留在人的工作记忆里**。LLM 进场之后，工作记忆从人脑迁移到 context window 里，而 context window 容量有限、调用成本线性，于是必须有一个**"专门负责把对的代码片段在对的时刻喂给模型"的中间层**——这一层是 2024–2026 期间新增的。这层之下，又长出来另一层：MCP server，把 SaaS 的能力**以 agent 可调用的方式**重新暴露一次。

## 1. Pre-Agent 时代的"代码上下文获取"长什么样

Pre-Agent 栈里，开发者获取"和我现在改的代码相关的其它代码"靠四件武器：

- **grep / ripgrep**：字面量、正则。准、但召回低、不懂语义（找 `getUser` 找不到 `fetchUser`）。
- **IDE find references / go-to-definition**：靠语言服务（LSP / SCIP），精确但只对**已建过索引的语言**有效，跨仓库瓶颈明显。
- **Sourcegraph 早期 code search**（2013 年起 [[21]](https://en.wikipedia.org/wiki/Sourcegraph)）：本质是把 grep 和 LSP-类符号图扩到**组织级跨仓库**的产品 [[1]](https://sourcegraph.com/blog/anatomy-of-a-coding-assistant)。
- **ctags / cscope**：90 年代留下的符号索引，至今仍在内核开发圈用。

这套体系的设定是"**人是检索者，工具是过滤器**"。人脑判断"哪个搜索结果相关"，工具只负责快。所有这一层的成功度量是"开发者每天 grep 几次"，没人会问"grep 把 token 分配得好不好"——因为没有 token。

## 2. Coding Agent 出现后，为什么必须长出 RAG-for-code

把 LLM 当编辑器副驾驶起，三个硬约束同时被踩到：

1. **Context window 装不下整个 codebase**。即使 Claude / GPT 类模型今天能上 200K–1M token（Claude Opus 4.6/Sonnet 4.6 于 2026-03-13 起 1M GA [[22]](https://platform.claude.com/docs/en/build-with-claude/context-windows)，GPT-5.5 于 2026-04-23 起 1M API [[23]](https://openai.com/index/introducing-gpt-5-5/)），一个真实的中型企业代码库（Augment 给出的口径是 400,000+ 文件）也是 10⁸–10⁹ token 量级（⚠ 作者估算：400k 文件 × 平均 250 行 × 4 token/行 ≈ 4×10⁸ token）[[2]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)。线性塞不进去，强行长上下文也会"context rot"——模型注意力在长尾衰减。
2. **Agent 不能每次都全文 grep**。Agent 比人慢：每个工具调用一次往返、一次推理。开放 `bash + ripgrep` 给 agent 是可行兜底，但任何能预先 narrow 的检索都能省下数量级的 token 和 latency。
3. **行为可控性需要"知道相关代码"**。让 agent 改一个函数前，**得让它先看到所有 call site**，否则改 API 就是制造 regression。这是工程纪律，不是性能优化。

结论：必须有一层"**在 prompt 之前**完成 codebase → 相关代码片段"映射的服务。Sourcegraph 把它叫 RAG-for-code、Augment 叫 Context Engine、Greptile 叫 codebase graph。

## 3. 两条路线：Augment 的"大上下文 + 实时索引" vs Sourcegraph 的"经典 IR + embedding"

两家代表了"装多少"和"找多准"两种工程哲学。

**Augment Code**（累计融资 252M，Sutter Hill / Index / Lightspeed 领投 [[3]](https://www.augmentcode.com/blog/augment-inc-raises-227-million)）：

- 自研 Context Engine。语义向量索引 + 依赖图，号称跨 400,000+ 文件级 codebase 仍可用 [[4]](https://www.augmentcode.com/context-engine)。
- **Real-time delta ingestion**：增量重建，180k 行 TS monorepo 首次索引 ≈ 4 分钟，增量更新 ≈ 40 秒 [[2]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)。
- 200K token 的 agent context window，但**关键不是窗口大，是"只塞需要的片段进去"**——这一点 Augment 自己反复强调："context > token count" [[5]](https://www.augmentcode.com/guides/mastering-ai-context-and-why-it-matters-more-than-token-count)。
- 多文件重构准确率自报 89% [[24]](https://www.augmentcode.com/tools/enterprise-multi-file-refactoring-why-ai-breaks-at-scale)、ISO/IEC 42001 认证（首家 AI 编码助手获此认证）[[24]](https://www.augmentcode.com/tools/enterprise-multi-file-refactoring-why-ai-breaks-at-scale)、面向企业大 codebase 销售。

**Sourcegraph Cody**：

- "Search-first RAG"。底层是 Sourcegraph 十年积累的代码搜索 + SCIP 代码图 + 向量 embedding 三结合 [[1]](https://sourcegraph.com/blog/anatomy-of-a-coding-assistant)。
- 三段检索：embeddings search → code graph lookup（精确 find-refs / find-defs）→ rerank top-k [[6]](https://sourcegraph.com/docs/cody)。
- 跨仓库上下文支持最多 10 个 repo [[6]](https://sourcegraph.com/docs/cody)。
- 路线偏"**经典 IR 工程**"：相信稀疏检索 + 符号精确链接比纯向量更稳定。

**工程上谁更可扩展？分界线在哪？**

- **<50k 文件、单仓库**：差不多——任何方案都能在几秒内召回，差异不显著。
- **50k–400k 文件、多仓库 / monorepo**：Sourcegraph 的代码图 + 增量索引架构有十年优势；Augment 的 delta ingestion 也能跑，但调优深度还在追赶。
- **>400k 文件、组织级、跨语言**：纯向量必然碎；纯符号图也会因为缺乏语义模糊匹配（"找到所有'鉴权相关'函数"）而召回不足。**事实上的赢家是"两边都做"**——Augment 在做符号图、Sourcegraph 在做更深的 embedding；殊途同归。

**本质判断**：长上下文模型把"必须 RAG"的门槛从 50k 文件推高到 200k–400k 文件，但**没有消灭 RAG**。任何一个企业 monorepo（Google / Meta / 任何 10 年以上的 SaaS）都在这道分界线之上。代码索引层是结构性新增，不是过渡品。

## 4. MCP 在 dev 工具生态的爆发：每个 SaaS 被迫"双 UI"

代码索引解决的是"agent 看代码"，**MCP 解决的是"agent 看 / 改世界"**。

Model Context Protocol 由 Anthropic 2024 年 11 月开源，到 2026 年 4 月，官方 registry 收录 9,400+ server，相比 2025 Q1 的 1,200 个增长 7.8 倍 [[7]](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol)。GitHub 自营的 `github-mcp-server` 于 2025 年 4 月进入 public preview，取代了原 Anthropic 维护的 reference 版本 [[8]](https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/)。Sentry 官方 MCP 暴露 16 个工具，支持 OAuth + 远程 streamable HTTP [[9]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/)。Postgres、Slack、Linear、Notion、Figma 各家相继发了官方或半官方 server。

这件事的本质 **不**是"又一个集成协议"。本质是：**任何 SaaS 现在都被迫维护两套 UI——人 UI（网页 / app）和 agent UI（MCP server）**。前者 20 年没变形态，后者从零开始且增长曲线极陡。一个 SaaS 不出 MCP server 的代价是"在 Cursor / Claude Code / Codex 的工作流里被绕过"——而那是 2026 年新增软件订阅的最大来源。

## 5. 具体案例：MCP 在日常 dev 工作流的形态

- **GitHub MCP**：Claude Code 直接 `list_issues`、`create_pull_request`、`search_code`。一次 Anthropic 官方实测显示"代码优先"的 MCP 调用模式比传统 REST/JSON 拉取节省 98% token [[10]](https://github.com/orgs/modelcontextprotocol/discussions/629)。
- **Postgres MCP**：read-only DSN 喂给 agent，让其在写代码前先 `EXPLAIN` 一条查询、看真实 schema；写 DSN 则被广泛警告为 footgun [[11]](https://toolradar.com/blog/best-mcp-servers-2026)。
- **Sentry MCP**：在 IDE 里把 agent 指到一个 issue ID，agent 拉异常 stack + 最近 release + 关联 commit，反推根因然后生成 fix patch——全程不开 Sentry UI [[9]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/)。
- **Linear MCP**：agent 在合 PR 时自动把工单 ID 挂上、状态推到 In Review。
- **Greptile MCP**：把 Greptile v3 的代码评审规则暴露给 Devin / Cursor / Cline，让第三方 agent 用同一套"组织 lint 规则"做 review [[12]](https://www.greptile.com/blog/series-a)。
- **Context7 MCP**（Upstash）：解决"LLM 训练数据停在 2024、库 API 已经变了"——在 prompt 末尾加 `use context7`，server 自动注入最新版库文档 [[13]](https://upstash.com/blog/context7-mcp)。

## 6. 典型配置示例（保留原貌）

Claude Desktop（macOS：`~/Library/Application Support/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx" }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres",
               "postgresql://readonly@localhost/app"]
    },
    "supabase": {
      "url": "https://mcp.supabase.com/sse",
      "headers": { "Authorization": "Bearer YOUR_ACCESS_TOKEN" }
    }
  }
}
```

Cursor（`~/.cursor/mcp.json`）格式同上 [[14]](https://mcpplaygroundonline.com/blog/complete-guide-mcp-config-files-claude-desktop-cursor-lovable)。Claude Desktop 只在启动时读一次配置，改完必须完整退出后再开。

## 7. 新需求：认证 / 权限 / audit / gateway / marketplace

200+ 第三方 server 跑在 dev 机本地、又或者远程暴露 SSE 端点，**安全债集体到期**。

- **认证标准化**：MCP 2026-03-15 规范强制 OAuth 2.1，PKCE 必走，RFC 8707 resource indicator 防止 token 跨 server replay [[15]](https://dasroot.net/posts/2026/04/mcp-authorization-specification-oauth-2-1-resource-indicators/)。
- **Row-level / scope-level 权限**：Sentry / Linear 都开始按 project + 操作类型细粒度 scope；Postgres MCP 早期 SQL injection CVE 后，read-only DSN 成事实最低线 [[11]](https://toolradar.com/blog/best-mcp-servers-2026)。
- **Audit log**：SOC 2 要求 ≥1 年、HIPAA ≥3 年、FINRA ≥7 年。专用 audit DB + Postgres row-level security 阻止 update / delete 是合规默认配方 [[16]](https://www.practical-devsecops.com/mcp-oauth-2-1-implementation/)。
- **MCP Gateway 作 toll booth**：SAP 把 Joule 后端的 MCP gateway 直接长在 BTP Destination Service + Cloud Identity 上，所有 tool 调用进 SAP Audit Log [[17]](https://community.sap.com/t5/technology-blog-posts-by-sap/connecting-custom-joule-agents-to-mcp-servers-a-poc-architecture-for/ba-p/14356644)。开源侧的 `mcp-gateway-registry` 用 Keycloak / Entra 做 OAuth、加统一 audit 与发现 [[18]](https://github.com/agentic-community/mcp-gateway-registry)。模式都是把分散的 N 个 MCP server 后撤到一个中央"收费站"。
- **Marketplace / registry**：官方 `registry.modelcontextprotocol.io` 是 app store 雏形；server card（`.well-known` URL 暴露 capability metadata）让爬虫和注册中心可发现 [[7]](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol)。
- **Aggregator**：Composio Tool Router 一个 endpoint 后接 1,000+ app、20,000+ tool，按任务动态加载，解决"装太多 MCP server 把 LLM 工具列表撑爆"的问题 [[19]](https://composio.dev/toolkits/apify/framework/claude-code)。Apify MCP 走的是把 Apify Store 几千个爬虫包装成 MCP tool 的路线 [[20]](https://github.com/apify/apify-mcp-server)。

## 8. 几条本质判断

**判断 1：MCP 把"集成"从一个昂贵环节变成商品。** Pre-Agent 时代，企业每接一个 SaaS 平均花 4–8 周工程时间写 OAuth + webhook + 字段映射。MCP 协议化以后，接一个新工具趋近于"在 JSON 里加 4 行 + 配一个 token"。集成工程师这个岗位的稀缺性正在被磨平——这是 Zapier / Workato / MuleSoft / 各家 iPaaS 长期定价权的根。

**判断 2：dev SaaS 的"双 UI 失血传导链"是真实的。** 任何不出 MCP server 的 dev SaaS（项目管理、监控、CI、feature flag、analytics）在 12–24 个月内会被"看不见"——开发者不再点开它的网页，agent 直接走 API。控制权从"漂亮 UI"迁移到"协议 + 数据"。这条传导链已经在 Sentry、Linear、Datadog、PagerDuty 的财报口径里出现"AI 集成被作为留存关键"的措辞，反推了 5 月 13 日美股软件股集体重挫的市场叙事（见 `chat/美股软件股近期重挫 (2026-05-13).md`）。

**判断 3：未来 3 年最重要的协议级机会是 MCP gateway / registry / aggregator 这三层。** 单点 MCP server 已经商品化、谁都能写；真正稀缺的是把 N×M 个 agent↔server 关系收敛成 1×M 的中间层。SAP Joule MCP Gateway、Composio Tool Router、官方 registry 是三种不同切法。这一层会在 2027 前出现至少一个独角兽，对位的不是 Zapier 而是**Okta / Cloudflare**——"身份 + 边界 + 审计"的 agent 版本。

**判断 4：代码索引层会被部分吞并到 IDE，但企业版会独立存活。** 个人开发者用 Cursor / Claude Code 内置的代码索引就够了；企业（>50k 文件、合规 + 数据驻留 + SSO）会继续买 Sourcegraph / Augment 这种专门产品，因为索引服务的真正护城河不是算法而是"**接进客户内网 + 不外泄代码 + 实时增量 + RBAC**"——这四件事正好是 IDE 厂商不愿做的脏活。

## 信源

[1] Sourcegraph, "The anatomy of an AI coding assistant," *Sourcegraph Blog*, 2025. [Online]. Available: <https://sourcegraph.com/blog/anatomy-of-a-coding-assistant>

[2] Augment Code, "Why 400k+ File Codebases Break Traditional AI," *Augment Code Guides*, 2026. (180k 行 TS monorepo：首次索引 ≈ 4 min，增量 ≈ 40 s。) [Online]. Available: <https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai>

[3] Augment Code, "Augment Inc. raises $227 Million," *Augment Code Blog*, 2024. (累计 252M 融资，Sutter Hill / Index / Lightspeed / Innovation Endeavors / Meritech。) [Online]. Available: <https://www.augmentcode.com/blog/augment-inc-raises-227-million>

[4] Augment Code, "Context Engine," *Augment Code Product*. [Online]. Available: <https://www.augmentcode.com/context-engine>

[5] Augment Code, "Mastering AI Context — and why it matters more than token count," *Augment Code Guides*, 2026. [Online]. Available: <https://www.augmentcode.com/guides/mastering-ai-context-and-why-it-matters-more-than-token-count>

[6] Sourcegraph, "Cody Documentation," *Sourcegraph Docs*. (embeddings + code graph + rerank 三段检索；跨仓库 ≤10 repo。) [Online]. Available: <https://sourcegraph.com/docs/cody>

[7] Digital Applied, "MCP Adoption Statistics 2026," 2026. (registry 从 2025 Q1 的 1,200 增长到 2026-04 的 9,400+，7.8× YoY。) [Online]. Available: <https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol>

[8] GitHub, "github-mcp-server is now available in public preview," *GitHub Changelog*, Apr. 2025. [Online]. Available: <https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/>

[9] Sentry, "Yes, Sentry has an MCP Server (...and it's pretty good)," *Sentry Blog*. (16 tool call、OAuth、Streamable HTTP / SSE。) [Online]. Available: <https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/>

[10] modelcontextprotocol, "Production Results: MCP Server for GitHub Validates Anthropic's Code-First Pattern (98% Token Reduction)," *GitHub Discussion #629*, 2025. [Online]. Available: <https://github.com/orgs/modelcontextprotocol/discussions/629>

[11] Toolradar, "Best MCP Servers in 2026: 25 You Should Install Now," 2026. (Postgres write-DSN footgun；read-only DSN 是事实底线。) [Online]. Available: <https://toolradar.com/blog/best-mcp-servers-2026>

[12] Greptile, "Series A and Greptile v3," *Greptile Blog*, Sep. 2025. ($25M Series A by Benchmark，估值 180M；MCP server 暴露代码评审规则给 Devin / Cursor。) [Online]. Available: <https://www.greptile.com/blog/series-a>

[13] Upstash, "Context7 MCP: Up-to-Date Docs for Any Cursor Prompt," *Upstash Blog*. [Online]. Available: <https://upstash.com/blog/context7-mcp>

[14] MCP Playground, "The Complete Guide to MCP Config Files — Claude Desktop, Cursor, Lovable, and More," 2026. [Online]. Available: <https://mcpplaygroundonline.com/blog/complete-guide-mcp-config-files-claude-desktop-cursor-lovable>

[15] Das Root, "The New MCP Authorization Specification," Apr. 2026. (2026-03-15 spec：OAuth 2.1 + PKCE + RFC 8707 resource indicators。) [Online]. Available: <https://dasroot.net/posts/2026/04/mcp-authorization-specification-oauth-2-1-resource-indicators/>

[16] Practical DevSecOps, "MCP OAuth 2.1 Security: Authentication Best Practices for AI Tool Integrations," 2026. (audit log SOC 2 ≥1y, HIPAA ≥3y, FINRA ≥7y。) [Online]. Available: <https://www.practical-devsecops.com/mcp-oauth-2-1-implementation/>

[17] SAP Community, "Connecting custom Joule Agents to MCP servers: A POC Architecture for Enterprise HR Intelligence," 2026. [Online]. Available: <https://community.sap.com/t5/technology-blog-posts-by-sap/connecting-custom-joule-agents-to-mcp-servers-a-poc-architecture-for/ba-p/14356644>

[18] agentic-community, "mcp-gateway-registry," *GitHub*. (Keycloak / Entra OAuth + 统一 audit + dynamic tool discovery。) [Online]. Available: <https://github.com/agentic-community/mcp-gateway-registry>

[19] Composio, "Apify MCP Integration with Claude Code," *Composio Toolkits*. (Tool Router 一个 endpoint 接 1,000+ app、20,000+ tool。) [Online]. Available: <https://composio.dev/toolkits/apify/framework/claude-code>

[20] Apify, "apify-mcp-server," *GitHub*. [Online]. Available: <https://github.com/apify/apify-mcp-server>
