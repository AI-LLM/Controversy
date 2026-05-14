# 2026-05-14：SDLC 栈 / Dev MCP server 与 Agent 集成协议 (D6.6) 层深度研究

> 系列子报告：软件开发栈 Pre-Coding-Agent vs Post-Coding-Agent。本篇覆盖 D6.6（Dev-MCP server / Agent 集成协议）层。范本：namespace.so 范式——挖本质，不堆现象。代码索引（D8.5）见同目录 `10a-code-index.md`，**不在本篇范围**。

这一层在 Pre-Agent 时代严格意义上**不存在**——存在的是它的远房表亲 iPaaS / EAI。MCP（Model Context Protocol）2024 年 11 月 25 日由 Anthropic 开源 [[1]](https://www.anthropic.com/news/model-context-protocol)，到 2025 年 12 月 9 日已由 Anthropic 捐赠给 Linux Foundation 旗下新成立的 Agentic AI Foundation (AAIF) 进入中立治理，与 Block 的 goose、OpenAI 的 AGENTS.md 共同作为奠基项目，Google / Microsoft / AWS / Cloudflare / Bloomberg 列为支持方 [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) [[3]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)。同期官方公布 MCP SDK 月下载量达 9700 万次、活跃 server 超过 10000 个 [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)。短短 12 个月，一个协议从一家公司的设计稿走到了基金会托管 + 多巨头背书，速度上对位 2014 年的 Kubernetes 而非 2010 年的 OAuth 2.0（⚠ 解读，依据：MCP 一年内进 LF + 多家 hyperscaler 同步 endorse，比 K8s 进 CNCF 用时更短）。

## 1. Pre-Agent 时代的"集成层"：EAI / iPaaS

Agent 出现之前，企业要把两个 SaaS 接起来（Salesforce → Jira、Slack → ServiceNow、HubSpot → Postgres），主路径只有两条：

- **重量级 EAI / iPaaS**：MuleSoft、Boomi、Workato。MuleSoft 企业起步价约 8 万美金/年，全栈 API-led 架构落地价 50 万–200 万美金以上 [[4]](https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/)；Workato 月费 500–2000 美金，年化 10K–150K+ 美金/客户 [[4]](https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/)。
- **轻量级 no-code 自动化**：Zapier、Make.com。Zapier 个人版 20–599 美金/月 [[4]](https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/)。

底层假设是"**人会预先定义触发器 + 映射 + 流程图**"：一个 SaaS 集成项目典型耗时 4–6 周工程时间，复杂字段映射可到 8 周 [[5]](https://prismatic.io/blog/cut-saas-integration-dev-time-with-embedded-ipaas/)。"集成工程师"是个有岗位、有简历、有招聘市场的工种。Pre-Agent 集成层是**贵的**、**慢的**、**人工设计的**。

## 2. Agent 时代为什么需要协议层："双 UI"压力

LLM agent 替开发者操作 SaaS 时碰到三个硬约束：

1. **没法 click**。agent 看不见浏览器 UI，只能调 API。但 SaaS 的 API 文档一般是给人读、给后端集成写代码用的，agent 直接读 OpenAPI 文件等于把上千个 endpoint 全灌进 prompt——Cloudflare 自己的 API 暴露成原始 MCP 工具会消耗超过 100 万 token 上下文 [[6]](https://blog.cloudflare.com/code-mode-mcp/)。
2. **N×M 爆炸**。N 个 agent × M 个 SaaS = N×M 个对接。每家 SaaS 给每家 agent 厂家单写 adapter 不现实。
3. **运行时上下文**。agent 调用工具前需要语义元数据（"这个 tool 能干什么、参数是什么、返回什么"），不是死的 OpenAPI 定义；工具调用之间需要中间态（resource 引用、错误回滚）。

结论：任何不出 MCP server 的 SaaS 在 12–24 个月内会被"看不见"（⚠ 解读，依据：MCP 一年内 registry 收录 10000+ server [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) + 主流 dev SaaS 已普遍出官方 server [[7]](https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/) [[8]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/)）——开发者不再点开它的网页，agent 直接走协议。**每个 SaaS 现在被迫维护两套 UI——给人的（网页 / app）和给 agent 的（MCP server）**。前者形态 20 年没大变，后者从零开始且增长曲线极陡。

## 3. MCP 协议本体：三原语 + 双传输 + 一新 primitive

**三类原语**（Resources / Tools / Prompts）[[9]](https://modelcontextprotocol.io/docs/learn/architecture)：

- **Tools**：模型主控，可被 agent 自主调用的函数（执行查询、写文件、发请求）。
- **Resources**：数据源，可由模型或用户主控；文件内容、数据库记录、API 响应。
- **Prompts**：用户主控的可复用模板，把 few-shot 例子或多步任务封装成"slash command 风格"快捷方式。

每个原语都有标准的 `*/list`、`*/get`、（Tools 额外）`tools/call` 方法 [[9]](https://modelcontextprotocol.io/docs/learn/architecture)。

**两种传输**：

- **stdio**：本地 server，命令行启动子进程，stdio JSON-RPC。Claude Desktop / Cursor 的本地 server 走这条。
- **Streamable HTTP**（2025 年从 SSE 演进而来）：远程 server，长连接，单向流推送。Sentry / Supabase 远程 MCP、Cloudflare AI Gateway 后台的 MCP Server Portal 都走这条 [[8]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/) [[10]](https://blog.cloudflare.com/enterprise-mcp/)。

**Tasks primitive（SEP-1686）** 2026 路线图的新增重点 [[11]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)：把长周期 / 异步任务从"一个 tool call 等回包"升级成 lifecycle 状态机（pending → running → succeeded/failed/cancelled），并补 retry 语义和过期策略。这是从"远程函数调用"向"长时跑 job + 可观测"演进的关键拐点。

**2026 路线图四个优先方向** [[11]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)：（a）Streamable HTTP 转无状态、能跑在负载均衡 + 横向扩展下；（b）Tasks primitive 补齐 lifecycle 缺口；（c）治理成熟化、正式 contributor ladder；（d）企业就绪——审计 / SSO / gateway 模式标准化。同时 server-card（SEP-1649、SEP-2127）规定 server 在 `/.well-known/mcp/server-card.json` 暴露 capability metadata，让爬虫和注册中心可发现而不必先连接 [[12]](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649)。

## 4. 代表 server 与实战形态

- **GitHub MCP**：2025 年 4 月由 GitHub 接管为官方 server，取代 Anthropic 维护的 reference 版本 [[7]](https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/)。Claude Code 直接 `list_issues`、`create_pull_request`、`search_code`。一次 Anthropic 官方实测显示"代码优先"的 MCP 调用模式比传统 REST/JSON 拉取节省 98% token [[13]](https://github.com/orgs/modelcontextprotocol/discussions/629)。
- **Postgres MCP**：read-only DSN 喂给 agent，让其在写代码前先 `EXPLAIN` 一条查询、看真实 schema；写 DSN 是公认 footgun [[14]](https://toolradar.com/blog/best-mcp-servers-2026)。
- **Sentry MCP**：暴露 16 个工具、支持 OAuth + Streamable HTTP / SSE [[8]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/)。在 IDE 里把 agent 指到一个 issue ID，agent 拉异常 stack + 最近 release + 关联 commit，反推根因生成 fix patch——全程不开 Sentry UI。
- **Linear MCP / Notion MCP / Atlassian MCP / Slack MCP**：项目管理 / 文档 / 工单 / 沟通的 agent 端口。Linear MCP 让 agent 合 PR 时自动挂工单 ID、状态推到 In Review。
- **Context7（Upstash）**：解决 LLM 训练数据过时——在 prompt 末尾加 `use context7`，server 注入最新版库文档 [[15]](https://upstash.com/blog/context7-mcp)。
- **Apify MCP**：把 Apify Store 3000+ Actors（爬虫 / 自动化）包装成 MCP tools 暴露给 agent [[16]](https://github.com/apify/apify-mcp-server)。

## 5. 配置示例（保留原貌）

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
    "sentry": {
      "url": "https://mcp.sentry.dev/sse",
      "headers": { "Authorization": "Bearer YOUR_OAUTH_TOKEN" }
    },
    "supabase": {
      "url": "https://mcp.supabase.com/sse",
      "headers": { "Authorization": "Bearer YOUR_ACCESS_TOKEN" }
    }
  }
}
```

Cursor（`~/.cursor/mcp.json`）格式同上 [[17]](https://mcpplaygroundonline.com/blog/complete-guide-mcp-config-files-claude-desktop-cursor-lovable)。Claude Desktop 只在启动时读一次配置，改完必须完整退出后再开。

## 6. 新增的运行时需求：认证 / 权限 / 审计 / rate limit / registry

server 一多，安全债集体到期：

- **认证标准化**：MCP 2026-03-15 规范强制 OAuth 2.1，PKCE 必走，RFC 8707 resource indicator 防止 token 跨 server replay [[18]](https://dasroot.net/posts/2026/04/mcp-authorization-specification-oauth-2-1-resource-indicators/)。
- **Row-level / scope-level 权限**：Sentry / Linear 按 project + 操作类型细粒度 scope；Postgres MCP 早期 SQL injection CVE 后，read-only DSN 成事实最低线 [[14]](https://toolradar.com/blog/best-mcp-servers-2026)。
- **Audit log**：SOC 2 要求 ≥1 年、HIPAA ≥3 年、FINRA ≥7 年。专用 audit DB + Postgres row-level security 阻止 update/delete 是合规默认配方 [[19]](https://www.practical-devsecops.com/mcp-oauth-2-1-implementation/)。
- **Rate limit + DLP**：Cloudflare Gateway 把 MCP 流量当 HTTP 流量做日志、DLP 扫描、Shadow MCP 探测（发现员工私接非授权远程 MCP）[[20]](https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/mcp-portals/)。
- **Registry + server-card**：`registry.modelcontextprotocol.io` 是官方 app store 雏形；SEP-1649 的 `.well-known/mcp/server-card.json` 让爬虫和注册中心无需建连即可枚举 capability [[12]](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649)。

## 7. 三种 Gateway 范式对比

收敛 N×M 关系到 1×M 的"协议级 toll booth"，市面上已分化出三种切法：

| 范式 | 代表 | 立场 | 收费模型 |
|---|---|---|---|
| **企业 IAM 外挂式** | SAP Joule MCP Gateway [[21]](https://community.sap.com/t5/technology-blog-posts-by-sap/connecting-custom-joule-agents-to-mcp-servers-a-poc-architecture-for/ba-p/14356644) | 把 MCP gateway 长在 BTP Destination Service + Cloud Identity 上，所有 tool 调用进 SAP Audit Log。复用既有企业 IAM。 | 企业订阅，绑大客户 |
| **开源中立 registry** | `mcp-gateway-registry`（agentic-community）[[22]](https://github.com/agentic-community/mcp-gateway-registry) | Keycloak / Entra OAuth + 统一 audit + dynamic tool discovery。开放部署、可自托管。 | 不收费 / 服务化二次包装 |
| **聚合器 + Code Mode** | Composio Tool Router [[23]](https://composio.dev/blog/introducing-tool-router-(beta)) / Cloudflare Code Mode [[6]](https://blog.cloudflare.com/code-mode-mcp/) | 一个 endpoint 后接 1000+ toolkits、按任务动态加载工具子集；Cloudflare 进一步把 API MCP 压缩成两个工具 `search()` + `execute()`，agent 写 JS 调用 OpenAPI——1 百万 token 的 API 表面压到 1000 token。 | Composio 按 session/订阅；Cloudflare 按 Worker / Gateway 流量 |

三家分别答了三个不同的问题：SAP 答"怎么把 MCP 接进既有合规体系"，开源 registry 答"怎么不被任一厂商锁死"，Composio / Cloudflare 答"工具列表撑爆 context window 怎么办"。它们不互斥，企业可能同时用三种——SAP 管内网、Cloudflare 管公网出口、Composio 管 agent 编程。

## 8. 几条本质判断

**判断 1：MCP 把"集成"从工程项目变成商品。** Pre-Agent 时代，单 SaaS 集成 4–8 周 + 5 万–20 万美金 [[4]](https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/) [[5]](https://prismatic.io/blog/cut-saas-integration-dev-time-with-embedded-ipaas/) 是常态；MCP 化以后，接一个新工具趋近于"JSON 加 4 行 + 配一个 token"。集成工程师这个岗位的稀缺性正在被磨平（⚠ 解读）——Zapier / Workato / MuleSoft 的长期定价权根基是"专业字段映射 + 私有连接器"，两者都被协议层击穿。

**判断 2：dev SaaS 的"双 UI 失血"传导链是真实的**（⚠ 解读，依据：MCP registry 12 个月从 1200 增到 10000+ server [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) + 主流 dev SaaS 已普遍出官方 server [[7]](https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/) [[8]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/)）**。** 任何不出 MCP server 的 dev SaaS（项目管理 / 监控 / CI / feature flag / analytics）在 12–24 个月内会被绕过——开发者只看 agent 输出，不再点 SaaS 网页。控制权从"漂亮 UI"迁移到"协议 + 数据"。2026 年 2 月以来的"SaaSpocalypse"行情（Anthropic Claude Cowork 发布触发单日 2850 亿美元软件股市值蒸发 [[24]](https://www.cnbc.com/2026/02/06/ai-anthropic-tools-saas-software-stocks-selloff.html)）即同一传导链的市场表达；5 月 13 日的延续性重挫见 `chat/美股软件股近期重挫 (2026-05-13).md`。

**判断 3：未来 3 年最重要的协议级机会是 gateway / registry / aggregator 这三层**（⚠ 解读，依据：单点 server 已商品化、参考 [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) 与 SAP / Composio / Cloudflare 三种 gateway 已同步出现 [[21]](https://community.sap.com/t5/technology-blog-posts-by-sap/connecting-custom-joule-agents-to-mcp-servers-a-poc-architecture-for/ba-p/14356644) [[23]](https://composio.dev/blog/introducing-tool-router-(beta)) [[6]](https://blog.cloudflare.com/code-mode-mcp/)）**。** 真正稀缺的不是"我有一个 GitHub MCP server"，而是"把 N 个 agent × M 个 server 关系收敛成 1×M 的中间层"。这一层对位的不是 Zapier，而是 **Okta + Cloudflare + npm registry 的合体**——身份、边界、审计、发现、计费。2027 年前会出现至少一个独角兽（⚠ 作者预测）。

**判断 4：MCP 进入 Linux Foundation 是协议层"商品化"的关键加速器**（⚠ 解读，依据：AAIF 由 Anthropic / Block / OpenAI 共同创立、Google / MS / AWS / Cloudflare 背书 [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) [[3]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)）**。** 一年内从"一家公司发的 spec"变成"多家 hyperscaler 共同治理"，类似 Kubernetes 进 CNCF 的剧本，但更快。中立化是 SaaS 厂商敢于全力做 MCP server 的政治前提——只要 MCP 还在 Anthropic 一家手里，Salesforce / Atlassian 都会保留观望。捐赠之后这层博弈消失。下一步可能是 ISO / IETF 标准化（⚠ 推测，DNS-discovery 已有 IETF draft [[25]](https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/)）。

**判断 5：Streamable HTTP 无状态化是远程 MCP 大规模商用的最后一公里**（⚠ 解读，依据：2026 路线图把它列为优先级 1 [[11]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)）**。** 目前主流远程 MCP 是有状态长连接，和 CDN / L7 负载均衡天然不合；Cloudflare / Render / Fly.io 这一类 edge 玩家正等着这一条落地以便把 MCP server 当 Worker 部署。一旦 stateless 化通过，"remote MCP 当成边缘 serverless 函数跑"会成默认部署形态，本地 stdio server 退化成开发 / 内网兜底（⚠ 推测）。

## 信源

[1] Anthropic, "Introducing the Model Context Protocol," *Anthropic News*, Nov. 25, 2024. [Online]. Available: <https://www.anthropic.com/news/model-context-protocol>

[2] Linux Foundation, "Linux Foundation Announces the Formation of the Agentic AI Foundation (AAIF)," Dec. 9, 2025. (奠基项目 MCP / goose / AGENTS.md；Google / Microsoft / AWS / Cloudflare / Bloomberg 背书；MCP SDK 月下载 9700 万、活跃 server 10,000+。) [Online]. Available: <https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation>

[3] Anthropic, "Donating the Model Context Protocol and establishing the Agentic AI Foundation," *Anthropic News*, Dec. 9, 2025. [Online]. Available: <https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation>

[4] Software Pricing Guide, "MuleSoft vs Boomi vs Workato Pricing 2026," 2026. (MuleSoft 起步 80K USD/yr、企业 API-led 500K–2M USD；Workato 500–2K USD/月、10K–150K+ USD/yr；Zapier 20–599 USD/月。) [Online]. Available: <https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/>

[5] Prismatic, "Cut SaaS Integration Dev Time with Embedded iPaaS," *Prismatic Blog*. (典型单 SaaS 集成 4–6 周工程时间，复杂映射可到 8 周。) [Online]. Available: <https://prismatic.io/blog/cut-saas-integration-dev-time-with-embedded-ipaas/>

[6] Cloudflare, "Code Mode: give agents an entire API in 1,000 tokens," *Cloudflare Blog*, 2026. (原始 MCP 工具暴露需 >1M token；Code Mode 压缩到 search()+execute() 两个工具、约 1000 token。) [Online]. Available: <https://blog.cloudflare.com/code-mode-mcp/>

[7] GitHub, "github-mcp-server is now available in public preview," *GitHub Changelog*, Apr. 2025. [Online]. Available: <https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/>

[8] Sentry, "Yes, Sentry has an MCP Server (...and it's pretty good)," *Sentry Blog*. (16 tool call、OAuth、Streamable HTTP / SSE。) [Online]. Available: <https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/>

[9] Model Context Protocol, "Architecture overview," *MCP Docs*. (三原语 Tools / Resources / Prompts；每个原语 */list、*/get、tools/call 方法。) [Online]. Available: <https://modelcontextprotocol.io/docs/learn/architecture>

[10] Cloudflare, "Scaling MCP adoption: Our reference architecture for simpler, safer and cheaper enterprise deployments of MCP," *Cloudflare Blog*, 2026. (AI Gateway + MCP Server Portals + Cloudflare Gateway 三件套。) [Online]. Available: <https://blog.cloudflare.com/enterprise-mcp/>

[11] Model Context Protocol Blog, "The 2026 MCP Roadmap," Mar. 2026. (四优先方向：Streamable HTTP 无状态化、Tasks primitive lifecycle、治理成熟化、企业就绪。) [Online]. Available: <https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/>

[12] modelcontextprotocol, "SEP-1649: MCP Server Cards - HTTP Server Discovery via .well-known," *GitHub Issue*. [Online]. Available: <https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649>

[13] modelcontextprotocol, "Production Results: MCP Server for GitHub Validates Anthropic's Code-First Pattern (98% Token Reduction)," *GitHub Discussion #629*, 2025. [Online]. Available: <https://github.com/orgs/modelcontextprotocol/discussions/629>

[14] Toolradar, "Best MCP Servers in 2026: 25 You Should Install Now," 2026. (Postgres write-DSN footgun；read-only DSN 是事实底线。) [Online]. Available: <https://toolradar.com/blog/best-mcp-servers-2026>

[15] Upstash, "Context7 MCP: Up-to-Date Docs for Any Cursor Prompt," *Upstash Blog*. [Online]. Available: <https://upstash.com/blog/context7-mcp>

[16] Apify, "apify-mcp-server," *GitHub*. (3000+ Actors 通过 MCP 暴露给 agent。) [Online]. Available: <https://github.com/apify/apify-mcp-server>

[17] MCP Playground, "The Complete Guide to MCP Config Files — Claude Desktop, Cursor, Lovable, and More," 2026. [Online]. Available: <https://mcpplaygroundonline.com/blog/complete-guide-mcp-config-files-claude-desktop-cursor-lovable>

[18] Das Root, "The New MCP Authorization Specification," Apr. 2026. (2026-03-15 spec：OAuth 2.1 + PKCE + RFC 8707 resource indicators。) [Online]. Available: <https://dasroot.net/posts/2026/04/mcp-authorization-specification-oauth-2-1-resource-indicators/>

[19] Practical DevSecOps, "MCP OAuth 2.1 Security: Authentication Best Practices for AI Tool Integrations," 2026. (audit log SOC 2 ≥1y, HIPAA ≥3y, FINRA ≥7y。) [Online]. Available: <https://www.practical-devsecops.com/mcp-oauth-2-1-implementation/>

[20] Cloudflare, "MCP server portals," *Cloudflare One Docs*. (Shadow MCP 检测、DLP 扫描、Gateway 路由。) [Online]. Available: <https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/mcp-portals/>

[21] SAP Community, "Connecting custom Joule Agents to MCP servers: A POC Architecture for Enterprise HR Intelligence," 2026. [Online]. Available: <https://community.sap.com/t5/technology-blog-posts-by-sap/connecting-custom-joule-agents-to-mcp-servers-a-poc-architecture-for/ba-p/14356644>

[22] agentic-community, "mcp-gateway-registry," *GitHub*. (Keycloak / Entra OAuth + 统一 audit + dynamic tool discovery。) [Online]. Available: <https://github.com/agentic-community/mcp-gateway-registry>

[23] Composio, "Introducing Tool Router (Beta)," *Composio Blog*, Oct. 1, 2025. (Tool Router 一个 endpoint 接 1000+ toolkits；2025-10-01 上线。) [Online]. Available: <https://composio.dev/blog/introducing-tool-router-(beta)>

[24] *CNBC*, "AI fears pummel software stocks: Is it 'illogical' panic or a SaaS apocalypse?" Feb. 6, 2026. (2026-02-03 Claude Cowork 发布触发 SaaSpocalypse，单日 $285B 软件股市值蒸发。) [Online]. Available: <https://www.cnbc.com/2026/02/06/ai-anthropic-tools-saas-software-stocks-selloff.html>

[25] Internet Engineering Task Force, "draft-morrison-mcp-dns-discovery-02 — Discovery of Model Context Protocol Servers via DNS TXT Records," IETF Datatracker. [Online]. Available: <https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/>
