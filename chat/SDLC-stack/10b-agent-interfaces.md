# 2026-05-14：SDLC 栈 / Agent 集成接口与产品供给侧改造 (D6.6) 层深度研究

> 系列子报告：软件开发栈 Pre-Coding-Agent vs Post-Coding-Agent。本篇覆盖 **D6.6（Agent 集成接口层）**——同时合并了原 L10b（MCP 协议本体 + dev 工具 MCP server 生态）与 L13（GUI 产品的 CLI / MCP / 浏览器化供给侧改造）两个相邻层。理由：协议本身、产品如何主动暴露、第三方如何被迫强 wrap，三件事是同一个"Agent 集成接口"问题的三个剖面，分两层会割裂叙事。代码索引（D8.5）见同目录 `10a-code-index.md`，**不在本篇范围**。

这一层在 Pre-Agent 时代严格意义上**不存在**——存在的是它的远房表亲 iPaaS / EAI + 各家 SaaS 散点式的 REST API 与 CLI。MCP（Model Context Protocol）2024-11-25 由 Anthropic 开源 [[1]](https://www.anthropic.com/news/model-context-protocol)；到 2025-12-09 已由 Anthropic 捐赠给 Linux Foundation 旗下新成立的 Agentic AI Foundation (AAIF) 进入中立治理，与 Block 的 goose、OpenAI 的 AGENTS.md 共同作为奠基项目，Google / Microsoft / AWS / Cloudflare / Bloomberg 列为支持方 [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) [[3]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)。同期官方公布 MCP SDK 月下载量达 9700 万次、活跃 server 超过 10000 个 [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)。短短 12 个月，一个协议从一家公司的设计稿走到了基金会托管 + 多巨头背书，速度上对位 2014 年的 Kubernetes 而非 2010 年的 OAuth 2.0（⚠ 解读，依据：MCP 一年内进 LF + 多家 hyperscaler 同步 endorse，比 K8s 进 CNCF 用时更短）。

但协议本身只是骨架。这一层真正的全貌还包含两块：（a）SaaS 产品方主动改造对外接口以服务 Agent——CLI 升级、自建 MCP server、配 Agent Skills；（b）当产品方不动手时，第三方社区强 wrap（OpenCLI 标准化 / CLI-Anything universal wrapper / Vercel agent-browser 跨 agent CLI 桥 / 各种浏览器 Agent 兜底）。

## 1. Pre-Agent 时代产品对外接口的三圈

Pre-Agent SaaS 默认是"GUI-first"。把对外接口画成三个同心圆：

- **核心圈：GUI**（人通过浏览器或 App 点击）。流量主路径，营销 / SEO / 转化漏斗 / NPS / 留存都围绕它建。
- **中间圈：REST / GraphQL API**。给企业集成、给 Zapier / MuleSoft / Workato 喂数据。是"集成层"的输入，但不是"主入口"。
- **外圈：CLI**。少数 SaaS 主动做。代表是 GitHub CLI 1.0（2020-09，beta 期内已被用于创建 250K+ PR、350K+ merge、20K+ issues [[4]](https://github.blog/2020-09-17-github-cli-1-0-is-now-available/)）、Stripe CLI（2019-11 发布，主打 webhook 转发 + 实时 API 日志 + 对象 CRUD [[5]](https://stripe.com/blog/stripe-cli)）、`aws` (2013)、`gcloud` (2014)、`kubectl` (2014)、Vercel CLI 等。

外圈在 Pre-Agent 时代是**开发者偏好**而非战略层——做了加分，不做不死。Bubble Tea（Charm.sh TUI 框架）的 23k stars、4000+ 应用、11,682 个 importing projects、被 AWS / NVIDIA / Microsoft Azure 内部使用 [[6]](https://charm.land/blog/the-next-generation/) 说明 CLI/TUI 在 2024 之前已经在悄悄复兴，但还不是企业级 SaaS 的必选项。

集成本身的代价昂贵：

- **重量级 EAI / iPaaS**：MuleSoft 企业起步价约 80K USD/年，全栈 API-led 架构落地价 500K–2M USD 以上 [[7]](https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/)；Workato 月费 500–2000 USD，年化 10K–150K+ USD/客户 [[7]](https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/)。
- **轻量级 no-code 自动化**：Zapier 个人版 20–599 USD/月 [[7]](https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/)。
- 一个 SaaS 集成项目典型耗时 4–6 周工程时间，复杂字段映射可到 8 周 [[8]](https://prismatic.io/blog/cut-saas-integration-dev-time-with-embedded-ipaas/)。

整个三圈结构的底层假设是"**调用方是人或人写的脚本**"。流量、定价、rate limit、风控全部围绕这个假设建。

## 2. Agent 时代流量模式突变

四个独立来源的数据指向同一个事实——**自动化流量 2025 年第一次超过人类**：

- **Imperva 2025 Bad Bot Report**：自动化流量首次过半（51% of all web traffic），其中坏 bot 37%、好 bot 14%。坏 bot 占比从 2024 年 32% 升到 2025 年 37%，连续第 6 年上升 [[9]](https://www.imperva.com/blog/2025-imperva-bad-bot-report-how-ai-is-supercharging-the-bot-threat/) [[10]](https://www.businesswire.com/news/home/20250415432215/en/Artificial-Intelligence-Fuels-Rise-of-Hard-to-Detect-Bots-That-Now-Make-up-More-Than-Half-of-Global-Internet-Traffic-According-to-the-2025-Imperva-Bad-Bot-Report)。
- **Cloudflare Radar 2025 Year in Review**：bot 流量占 30% 全球 web traffic；AI 爬虫单独占 4.2% HTML 请求，Googlebot 另占 4.5%；非 AI bot 全年生成 50% HTML 请求，比人类生成多 7%、峰值多 25% [[11]](https://blog.cloudflare.com/radar-2025-year-in-review/) [[12]](https://www.infoq.com/news/2025/12/cloudflare-2025-ai-bots/)。
- **HUMAN Security 2026 State of AI Traffic**：agentic AI 流量同比增长 **+7,851%**，2025 年月度量从 1 月到 12 月增长 187%（接近年化三倍）[[13]](https://www.humansecurity.com/learn/blog/ai-traffic-growth-2025-key-findings/)。
- **CSA 2025 API 安全报告**：以前一天几百次调用的 API 现在被 AI workload 拉到每分钟几千次 [[14]](https://cloudsecurityalliance.org/blog/2025/09/09/api-security-in-the-ai-era)。
- **企业用例侧**：78% 企业 AI 团队的 Agent 已经在生产环境里跑 MCP-backed 工具栈 [[15]](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol)。

⚠ **解读**：这些数字混合了"AI 训练爬虫 + 推理时 Agent + 传统 bot"三类，区分质量参差。但从 SaaS 视角看，**调用方不再是人**已经是事实而非预言。每家 SaaS 收到的请求里，越来越多来自 Claude Code / Devin / Operator / Manus / 自建 Agent。

LLM agent 在 SaaS 上操作时碰到三个硬约束：（i）**没法 click**——agent 看不见浏览器 UI，只能调 API，但 SaaS 的 API 文档一般是给人读、给后端集成写代码用的，agent 直接读 OpenAPI 文件等于把上千个 endpoint 全灌进 prompt——Cloudflare 自己的 API 暴露成原始 MCP 工具会消耗超过 100 万 token 上下文 [[16]](https://blog.cloudflare.com/code-mode-mcp/)；（ii）**N×M 爆炸**——N 个 agent × M 个 SaaS = N×M 个对接；（iii）**运行时上下文**——agent 调用工具前需要语义元数据（"这个 tool 能干什么、参数是什么、返回什么"），不是死的 OpenAPI 定义。

由此**每个 SaaS 现在被迫维护两套 UI——给人的（网页 / app）和给 agent 的（CLI / MCP / 浏览器友好 DOM）**。前者形态 20 年没大变，后者从零开始且增长曲线极陡。

## 3. MCP 协议层

### 3.1 协议本体

**三类原语**（Resources / Tools / Prompts）[[17]](https://modelcontextprotocol.io/docs/learn/architecture)：

- **Tools**：模型主控，可被 agent 自主调用的函数（执行查询、写文件、发请求）。
- **Resources**：数据源，可由模型或用户主控；文件内容、数据库记录、API 响应。
- **Prompts**：用户主控的可复用模板，把 few-shot 例子或多步任务封装成"slash command 风格"快捷方式。

每个原语都有标准的 `*/list`、`*/get`、（Tools 额外）`tools/call` 方法 [[17]](https://modelcontextprotocol.io/docs/learn/architecture)。

**两种传输**：

- **stdio**：本地 server，命令行启动子进程，stdio JSON-RPC。Claude Desktop / Cursor 的本地 server 走这条。
- **Streamable HTTP**（2025 年从 SSE 演进而来）：远程 server，长连接，单向流推送。Sentry / Supabase 远程 MCP、Cloudflare AI Gateway 后台的 MCP Server Portal 都走这条 [[18]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/) [[19]](https://blog.cloudflare.com/enterprise-mcp/)。

**Tasks primitive（SEP-1686）** 2026 路线图的新增重点 [[20]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)：把长周期 / 异步任务从"一个 tool call 等回包"升级成 lifecycle 状态机（pending → running → succeeded/failed/cancelled），并补 retry 语义和过期策略。这是从"远程函数调用"向"长时跑 job + 可观测"演进的关键拐点。

**2026 路线图四个优先方向** [[20]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)：（a）Streamable HTTP 转无状态、能跑在负载均衡 + 横向扩展下；（b）Tasks primitive 补齐 lifecycle 缺口；（c）治理成熟化、正式 contributor ladder；（d）企业就绪——审计 / SSO / gateway 模式标准化。

**注册中心数量爆炸**：官方 MCP registry 季度滚动——Q1 2025 末 ~1200、Q3 末 3400、年末 6800，2026-04 中过 **9400+**；非官方 mcp.so 单点索引 16,670（2025-09）[[15]](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol)。SEP-1649（与后续 SEP-2127）规定 server 在 `/.well-known/mcp/server-card.json` 暴露 capability metadata，让爬虫和注册中心可发现而不必先连接 [[21]](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649)。IETF 一侧已有 `draft-morrison-mcp-dns-discovery` 草案探讨基于 DNS TXT 的发现机制 [[22]](https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/)。

### 3.2 三种 Gateway / Aggregator 范式

收敛 N×M 关系到 1×M 的"协议级 toll booth"，市面上已分化出三种切法：

| 范式 | 代表 | 立场 | 收费模型 |
|---|---|---|---|
| **企业 IAM 外挂式** | SAP Joule MCP Gateway [[23]](https://community.sap.com/t5/technology-blog-posts-by-sap/connecting-custom-joule-agents-to-mcp-servers-a-poc-architecture-for/ba-p/14356644) | 把 MCP gateway 长在 BTP Destination Service + Cloud Identity 上，所有 tool 调用进 SAP Audit Log。复用既有企业 IAM。 | 企业订阅，绑大客户 |
| **开源中立 registry** | `mcp-gateway-registry`（agentic-community）[[24]](https://github.com/agentic-community/mcp-gateway-registry) | Keycloak / Entra OAuth + 统一 audit + dynamic tool discovery。开放部署、可自托管。 | 不收费 / 服务化二次包装 |
| **聚合器 + Code Mode** | Composio Tool Router [[25]](https://composio.dev/blog/introducing-tool-router-(beta)) / Cloudflare Code Mode [[16]](https://blog.cloudflare.com/code-mode-mcp/) | 一个 endpoint 后接 1000+ toolkits、按任务动态加载工具子集；Cloudflare 进一步把 API MCP 压缩成两个工具 `search()` + `execute()`，agent 写 JS 调用 OpenAPI——1 百万 token 的 API 表面压到 1000 token。 | Composio 按 session/订阅；Cloudflare 按 Worker / Gateway 流量 |

三家分别答了三个不同的问题：SAP 答"怎么把 MCP 接进既有合规体系"，开源 registry 答"怎么不被任一厂商锁死"，Composio / Cloudflare 答"工具列表撑爆 context window 怎么办"。它们不互斥，企业可能同时用三种——SAP 管内网、Cloudflare 管公网出口、Composio 管 agent 编程。

### 3.3 认证 / 审计 / 合规栈

server 一多，安全债集体到期：

- **认证标准化**：MCP 2026-03-15 规范强制 OAuth 2.1，PKCE 必走，RFC 8707 resource indicator 防止 token 跨 server replay [[26]](https://dasroot.net/posts/2026/04/mcp-authorization-specification-oauth-2-1-resource-indicators/)。
- **Row-level / scope-level 权限**：Sentry / Linear 按 project + 操作类型细粒度 scope；Postgres MCP 早期 SQL injection CVE 后，read-only DSN 成事实最低线 [[27]](https://toolradar.com/blog/best-mcp-servers-2026)。
- **Audit log**：SOC 2 要求 ≥1 年、HIPAA ≥3 年、FINRA ≥7 年。专用 audit DB + Postgres row-level security 阻止 update/delete 是合规默认配方 [[28]](https://www.practical-devsecops.com/mcp-oauth-2-1-implementation/)。
- **Rate limit + DLP**：Cloudflare Gateway 把 MCP 流量当 HTTP 流量做日志、DLP 扫描、Shadow MCP 探测（发现员工私接非授权远程 MCP）[[29]](https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/mcp-portals/)。

## 4. 三条产品供给路径

产品方面对 Agent 流量，至少要做一条："给 Agent 长一张脸"。三条主路径——CLI、MCP server、让 Agent 用浏览器——分别对应"低改造低能力"、"中改造高能力"、"零改造低可靠"。

### 4.1 CLI 路径——老技术新身位

Pre-Agent CLI 服务开发者；Agent 时代 CLI 同时服务 Coding Agent。Claude Code / Devin / Codex CLI 之所以能跑通，部分原因是宿主操作系统里已经有 `gh`、`stripe`、`vercel`、`aws`、`gcloud`、`kubectl` 这层稳定接口——agent 只需要拼 shell 命令而不必学每家 SaaS 的 SDK。

#### 4.1.1 既有官方 CLI 矩阵

GitHub CLI、Stripe CLI、AWS CLI、`gcloud`、`kubectl`、Vercel CLI 已经是十年量级的稳定基础设施；Agent 时代它们的边际价值反而上升——延迟 100ms 量级、几乎 0 token 成本、命令稳定。

#### 4.1.2 Agent SDK 升级

- **Stripe Agent Toolkit**（2024-11 发布，2026-02 已到 0.7.0）：在 Stripe CLI 之上加一层 LangChain / Vercel AI SDK / CrewAI / OpenAI Agents SDK 适配，把 PaymentIntent / Customer / Invoice / Subscription / Payment Link / Refund 包装成可被 function call 的工具；强制要求 Restricted API Key (`rk_*`) 而非 secret key，做粒度授权 [[30]](https://stripe.dev/blog/adding-payments-to-your-agentic-workflows) [[31]](https://thelettertwo.com/2024/11/15/stripe-releases-sdk-enabling-payment-and-billing-capabilities-for-ai-agents/)。
- **Vercel AI SDK 5**（2025-07-31）增强 tool 能力：dynamic tools、provider-executed functions、lifecycle hooks、`stopWhen` / `prepareStep` 控制 agentic loop [[32]](https://vercel.com/blog/ai-sdk-5)。**AI SDK 6 beta**（2025-10 Vercel Ship AI）引入 `ToolLoopAgent` 抽象与 `needsApproval: true` 的 human-in-the-loop 审批 gate [[33]](https://vercel.com/blog/ai-sdk-6) [[34]](https://www.infoq.com/news/2025/10/vercel-ship-ai/)。
- Bubble Tea / Gum / Charm 生态的扩张让 TUI 同时服务人和 agent——agent 通过子进程 stdio 调用，人通过键盘交互，**同一个二进制双 UI** [[6]](https://charm.land/blog/the-next-generation/)。

#### 4.1.3 OpenCLI——CLI 的 OpenAPI

**OpenCLI Specification (OCS)**：CLI 世界的"OpenAPI"——平台/语言无关的 JSON / YAML schema，描述 CLI 工具的命令、参数、子命令，让 agent 不需要读 man page 或 `--help` 就能调用任意 CLI [[35]](https://github.com/spectreconsole/open-cli) [[36]](https://opencli.org/)。Pre-Agent 时代的 CLI 是"开发者用 help / 文档摸索"，Agent 时代的 CLI 必须**机器可读**才能被流水化调用，OCS 正在填补这层。**官方 CLI = 人可用；CLI + OCS = 人 + agent 都可用**——这把"补 CLI"的边际工作量降到几乎为零。

#### 4.1.4 CLI-Anything——社区强 wrap

**CLI-Anything**（HKUDS，2025，约 21K GitHub stars）：直接走另一条路——**把任意 GUI 应用（GIMP / Blender / LibreOffice / OBS / Audacity ...）封装成结构化 CLI**，agent 一行命令驱动整个应用，无需 GUI 自动化、无需 API、无需厂商配合 [[37]](https://github.com/HKUDS/CLI-Anything) [[38]](https://clianything.cc/)。配套 **CLI-Hub** 是 agent-friendly CLI registry（类似 npm 之于 Node），用 `pip install cli-anything-hub` 一行搜索 / 安装 / 卸载 CLI harness。这是"产品方什么都不做、社区把它做成 agent-native"的极端范式。和浏览器 Agent 路径竞争——同样不需要产品方动手，但延迟与可靠性都显著优于截屏识别。

#### 4.1.5 Vercel agent-browser——CLI 桥到浏览器

**agent-browser**（Vercel Labs，Rust CLI）：把浏览器自动化做成 **跨 agent 的 CLI 子集**——Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / Goose / OpenCode / Windsurf 都能通过相同命令调用浏览器；默认引擎 Chrome for Testing，`--engine` 切到 lightpanda（Zig 写的轻量级浏览器）[[39]](https://github.com/vercel-labs/agent-browser)。这是 CLI 路径和浏览器 Agent 路径的桥梁：**用 CLI 接口包装浏览器能力**，每个 Coding Agent 不需要各自集成 Playwright / Puppeteer。

同名社区项目 **abhinav-nigam/agent-browser** 走 MCP 路线，74 个 browser tool 通过 MCP server 暴露 [[40]](https://github.com/abhinav-nigam/agent-browser)——两条路径殊途同归。

⚠ **解读**：CLI 路径门槛最低（很多 SaaS 已经有）、对存量改造最小。原本"暴露能力面窄"的弱点正在被 **OpenCLI 标准化 + CLI-Anything 社区力量** 双向补偿：协议化让 CLI 变得 agent 可解析，universal wrapper 让没有 CLI 的 GUI 应用也能被强制 CLI 化。CLI 路径的赢家不只是已有官方 CLI 的厂商，**还有第三方 wrapper（CLI-Anything 这类）**——它们绕开了产品方"做不做 MCP" 的决策权。

### 4.2 MCP 路径——产品方主动暴露 server

#### 4.2.1 SaaS 主流玩家时间线

- **GitHub MCP**：2025-04 由 GitHub 接管为官方 server，取代 Anthropic 维护的 reference 版本 [[41]](https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/)。Claude Code 直接 `list_issues`、`create_pull_request`、`search_code`。Anthropic 官方实测显示"代码优先"的 MCP 调用模式比传统 REST/JSON 拉取节省 98% token [[42]](https://github.com/orgs/modelcontextprotocol/discussions/629)。
- **Cloudflare Remote MCP**（2025-04-07）：第一个支持远端 MCP server 部署的平台，配套 `workers-oauth-provider`、`McpAgent` 类、`mcp-remote` adapter、Workers AI playground 作为 MCP client；后续放出 13 个官方 server [[43]](https://www.cloudflare.com/press/press-releases/2025/cloudflare-accelerates-ai-agent-development-remote-mcp/) [[44]](https://blog.cloudflare.com/thirteen-new-mcp-servers-from-cloudflare/) [[45]](https://blog.cloudflare.com/remote-model-context-protocol-servers-mcp/)。
- **Atlassian Remote MCP**（2025-05-01 beta）：Jira + Confluence Cloud 用户从 Anthropic 直接 summarize / create issue / 多步 action，权限完全继承产品侧 ACL [[46]](https://www.atlassian.com/blog/announcements/remote-mcp-server)。
- **Notion 3.0 Agents + Notion MCP**（2025-09-18 "Make with Notion"）：first-party 集成 Lovable / Perplexity / Mistral / HubSpot；Cursor 可拉 Notion 中的 spec、写代码、再回写状态 [[47]](https://www.notion.com/releases/2025-09-18)。
- **Figma Dev Mode MCP server**（2025）：远端访问开放，agent 可读 design context、可写 frame / component / variable / auto layout，用 design system 作 source of truth；现 beta 免费，未来 usage-based 计费 [[48]](https://www.figma.com/blog/introducing-figma-mcp-server/) [[49]](https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/)。
- **Slack RTS API + MCP**（2025-10-13 GA）：query-based 实时检索 Slack 对话数据，**数据不离开 Slack 基础设施**，权限按已有 ACL [[50]](https://www.reworked.co/digital-workplace/slacks-rts-api-and-mcp-server-hit-general-availability/)。
- **Sentry MCP**：暴露 16 个工具、支持 OAuth + Streamable HTTP / SSE [[18]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/)。在 IDE 里把 agent 指到一个 issue ID，agent 拉异常 stack + 最近 release + 关联 commit，反推根因生成 fix patch——全程不开 Sentry UI。
- **Stripe MCP server**：是 Agent Toolkit 的另一种暴露面（function-call 与 MCP 并行）[[30]](https://stripe.dev/blog/adding-payments-to-your-agentic-workflows)。
- **Postgres MCP**：read-only DSN 喂给 agent，让其在写代码前先 `EXPLAIN` 一条查询、看真实 schema；写 DSN 是公认 footgun [[27]](https://toolradar.com/blog/best-mcp-servers-2026)。
- **Linear MCP**：让 agent 合 PR 时自动挂工单 ID、状态推到 In Review。
- **Context7（Upstash）**：解决 LLM 训练数据过时——在 prompt 末尾加 `use context7`，server 注入最新版库文档 [[51]](https://upstash.com/blog/context7-mcp)。
- **Apify MCP**：把 Apify Store 3000+ Actors（爬虫 / 自动化）包装成 MCP tools 暴露给 agent [[52]](https://github.com/apify/apify-mcp-server)。

#### 4.2.2 Anthropic Agent Skills——高频 workflow 的标准封装

**Anthropic Agent Skills**（2025-10 公布，2025-12 转为开放标准）是 MCP 路径上的关键封装层 [[53]](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) [[54]](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/) [[55]](https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/)。Skill = 一个目录 + `SKILL.md`，把"打开 Figma、找 design system、读出 token、生成代码"这种 GUI workflow 打包成可被 agent **渐进发现 + 按需加载**的能力；首批合作伙伴 Atlassian / Canva / Cloudflare / Figma / Notion / Ramp / Sentry [[55]](https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/)。Simon Willison 评价"可能比 MCP 还重要" [[56]](https://simonwillison.net/2025/Oct/16/claude-skills/)。这是产品方第一次有"把自己的高频 workflow 用极少 token 暴露给 agent"的标准做法。

### 4.3 浏览器 Agent 路径——把 GUI 当 API 用

当 SaaS 不肯出 MCP 也没 CLI、或者 agent 需要跨多家 SaaS 但每家都没标准接口时，**让 agent 用浏览器**就成为最后的兜底。

#### 4.3.1 大模型平台

- **Anthropic Computer Use**（2024-10-22 public beta，Claude 3.5 Sonnet）[[57]](https://www.anthropic.com/news/3-5-models-and-computer-use)。OSWorld（screenshot-only）发布时 14.9%（次优 7.8%），多步 22.0%。
- **OpenAI Operator**（2025-01-23 research preview，ChatGPT Pro $200/月）。基于 Computer-Using Agent (CUA) 模型，自带浏览器、自纠错重试 [[58]](https://techcrunch.com/2025/01/23/openais-agent-tool-will-be-available-to-users-paying-200-per-month-for-pro/) [[59]](https://www.technologyreview.com/2025/01/23/1110484/openai-launches-operator-an-agent-that-can-use-a-computer-for-you/)。

#### 4.3.2 基础设施 / SDK 中间层

- **Browserbase**：headless 浏览器即服务。2025-04 Series B $40M，估值 $300M（约前轮 4x），累计 $67.5M [[60]](https://www.upstartsmedia.com/p/browserbase-raises-40m-and-launches-director) [[61]](https://www.builtinsf.com/articles/browserbase-announces-40m-series-b-funding-20250618)。
- **Stagehand**（Browserbase 开源 SDK，MIT licensed）：natural language + code 混合写 browser agent，对抗 page 改版 [[62]](https://github.com/browserbase/stagehand)。多语言 SDK：TypeScript / Python / Go / Ruby / C# .NET。
- **browser-use**（开源 Python lib，2025-Q1 YC W25 批次）：2025-03 Seed $17M，领投 Felicis 的 Astasia Myers，参投 Paul Graham / A Capital / Nexus Venture Partners [[63]](https://techcrunch.com/2025/03/23/browser-use-the-tool-making-it-easier-for-ai-agents-to-navigate-websites-raises-17m/)。YC 描述其"近 3 个月获得 40k stars，最大的开源 web agent 项目" [[64]](https://www.ycombinator.com/companies/industry/open-source)。
- **agent-browser 双版本**：Vercel Labs 的 Rust CLI 版（跨 8 个 Coding Agent）[[39]](https://github.com/vercel-labs/agent-browser) 与 abhinav-nigam 的 MCP 版（74 个 browser tool）[[40]](https://github.com/abhinav-nigam/agent-browser)——见 §4.1.5。

#### 4.3.3 应用层 / 替代 RPA

- **Skyvern**：开源，LLM + 计算机视觉处理 auth / 表单 / CAPTCHA / 下载；声称复杂 benchmark 85.8% 成功率；2025-12 Seed $2.7M（创始团队 11 人，2026-01 数据）[[65]](https://www.skyvern.com/blog/skyvern-we-raised-2-7m-to-fix-browser-automation-open-source/) [[66]](https://tracxn.com/d/companies/skyvern/__joZNwZnvPpp5SWng14qfKwxCqqwKRt699DxAC4T5pfI)。
- **Manus AI**（Butterfly Effect 出品）：2025-03 上线全自主 AI agent；2025-04 Benchmark 领投 $75M，估值 ~$500M（前轮 $100M 的 5x）[[67]](https://techcrunch.com/2025/04/25/chinese-ai-startup-manus-reportedly-gets-funding-from-benchmark-at-500m-valuation/) [[68]](https://siliconangle.com/2025/04/25/chinese-startup-behind-manus-reportedly-raises-75m-funding/)；8 个月年化营收过 $100M、run rate 超 $125M [[69]](https://www.cnbc.com/2025/12/30/meta-acquires-singapore-ai-agent-firm-manus-china-butterfly-effect-monicai.html)；2025-12 Meta 宣布 ~$2B 收购 [[70]](https://techcrunch.com/2025/12/29/meta-just-bought-manus-an-ai-startup-everyone-has-been-talking-about/)；2026-04 中国 NDRC 否决该交易 [[71]](https://techcrunch.com/2026/04/27/china-vetoes-metas-2b-manus-deal-after-months-long-probe/)。

#### 4.3.4 OSWorld-Verified benchmark 演进

OSWorld（screenshot-only 屏幕代理基准）从 2024-10 Computer Use 发布时的 14.9% 到 2026-05 Claude Opus 4.7 在 OSWorld-Verified 78.0%、Mythos Preview 79.6% [[72]](https://llm-stats.com/benchmarks/osworld-verified)——**18 个月内 5x 提升**。但 78% 也意味着 22% 失败率，浏览器 Agent 当前还到不了"可以无监督跑生产"的可靠性。

### 4.4 三路径技术对比

| 路径 | 延迟 | 成本 / 调用 | 可靠性 | 改产品的成本 |
|---|---|---|---|---|
| CLI | 100ms 量级 | 几乎 0 | 高（命令稳定） | 低（已有 CLI 加 wrapper） |
| MCP | 100–500ms | 低（token 友好） | 中–高 | 中（要新做 server + auth） |
| 浏览器 Agent | 5–60s | 高（截图 + 推理） | 低–中（页面改了就崩） | 0（产品不用改） |

⚠ **解读依据**：延迟和成本是 Claude Code / Operator 用户社区经验值；可靠性来自 OSWorld 78% 即代表 22% 失败率 [[72]](https://llm-stats.com/benchmarks/osworld-verified)，比 MCP 工具调用 95%+ 成功率显著低。

## 5. 新需求：选型、定价、反 Bot 经济学反转

**产品方选型**：dev 工具型 SaaS（GitHub / Stripe / Vercel / Sentry / Linear）三条都做，CLI + MCP + 配 Skills 文档；非 dev 但有结构化数据（Notion / Atlassian / Figma / Slack）优先 MCP；面向消费者 / 长尾电商 / 政府门户基本上没法主动改造，被迫接受被浏览器 Agent 当 GUI 用。

**定价**：人类 per-seat 模型在 agent 时代被打穿——**1 个 seat 可能驱动 100x 流量**。Bain / Deloitte / Glean 2025 报告均指 SaaS 在转 "subscription + consumption" 混合 [[73]](https://www.bain.com/insights/will-agentic-ai-disrupt-saas-technology-report-2025/) [[74]](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/saas-ai-agents.html)。但 **per-call 也踩坑**：Salesforce Agentforce $2/conversation 模式被客户骂到改版 [[75]](https://www.getmonetizely.com/blogs/the-doomed-evolution-of-salesforces-agentforce-pricing)。Metronome 2025 报告：78% 实施 UBP 的公司是过去 5 年内才上的 [[76]](https://metronome.com/state-of-usage-based-pricing-2025)。

**反 Bot 经济学反转**：Cloudflare 2025-07 把 AI 爬虫 **默认屏蔽** [[77]](https://www.technologyreview.com/2025/07/01/1119498/cloudflare-will-now-by-default-block-ai-bots-from-crawling-its-clients-websites/)，同步推 **pay-per-crawl** 市场（HTTP 402 Payment Required + 请求头携带 payment intent）[[78]](https://blog.cloudflare.com/introducing-pay-per-crawl/)。配套 **AI Crawl Control** 提供白名单 + 计费 + 审计 [[79]](https://blog.cloudflare.com/introducing-ai-crawl-control/)。这是产品方第一次有标准化路径"**对友 Agent 收钱、对恶 Agent 屏蔽**"。⚠ **解读**：这本质是把 robots.txt 的礼貌层升级到经济激励层；如果 Cloudflare 押对，每条 HTTP 请求都会带 micropayment header，bot 流量从"被防御"变成"被定价"。反 Bot 系统从 **cost center 变 revenue center**——这一资金流向的反转是 Agent 时代供给侧最隐蔽的商业模式重构。

**vendor 主动 vs 第三方被迫 wrap 双轨制**：MCP / Skills 是产品方主动出让控制权换流量；CLI-Anything / browser-use / Skyvern / Operator 是第三方在产品方不动手时强制把它们 agent 化。两套体系并行——产品方做主动派的预期是"我能定义自己被怎么用 + 收哪种钱"；做不到时，第三方会替它定义，且收益归第三方。

**GUI 双 UI 设计**：产品 UI 同时给人和 Agent 看，需要：（a）稳定的 ARIA / `data-testid` / 语义化 DOM 让浏览器 Agent 可定位；（b）`/.well-known/mcp/server-card.json` 让爬虫不连接就能发现能力（SEP-1649 [[21]](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649)）；（c）`llms.txt` / Skills 目录给静态文档化暴露。

## 6. 具体配置 / 代码示例

### 6.1 Claude Desktop MCP 配置

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

Cursor（`~/.cursor/mcp.json`）格式同上 [[80]](https://mcpplaygroundonline.com/blog/complete-guide-mcp-config-files-claude-desktop-cursor-lovable)。Claude Desktop 只在启动时读一次配置，改完必须完整退出后再开。

### 6.2 Stripe Agent Toolkit（function call 风格）

```python
from stripe_agent_toolkit.langchain.toolkit import StripeAgentToolkit
toolkit = StripeAgentToolkit(
    secret_key="rk_test_...",   # Restricted API Key，仅授权指定 endpoint
    configuration={
        "actions": {
            "payment_links": {"create": True},
            "customers":     {"create": True, "read": True},
        }
    }
)
# toolkit.get_tools() 直接喂给 LangChain / OpenAI Agents SDK
```

要点：`rk_*` 锁死 agent 不能升级到 secret-key 范畴；toolkit 不直接管理 idempotency，agent 自己负责 [[30]](https://stripe.dev/blog/adding-payments-to-your-agentic-workflows)。

### 6.3 Cloudflare Remote MCP（Workers 部署）

```bash
npx create-cloudflare@latest mcp-demo \
  --template=cloudflare/ai/demos/remote-mcp-authless
cd mcp-demo && npx wrangler deploy
# 部署到 mcp-demo.<your>.workers.dev，Streamable HTTP transport
```

`workers-oauth-provider` 处理 OAuth flow；`McpAgent` 类把 Workers Durable Object 当 session 状态机；Claude / Cursor 在 client 端通过 `mcp-remote` adapter 连接 [[43]](https://www.cloudflare.com/press/press-releases/2025/cloudflare-accelerates-ai-agent-development-remote-mcp/) [[45]](https://blog.cloudflare.com/remote-model-context-protocol-servers-mcp/)。

### 6.4 browser-use（浏览器 Agent 路径）

```python
from browser_use import Agent
from langchain_openai import ChatOpenAI

agent = Agent(
    task="去 Linear 把 Bug 标签下所有 high priority 工单导出 CSV",
    llm=ChatOpenAI(model="gpt-4o"),
)
result = await agent.run()
```

agent 直接打开 Chromium、截图、点击、填表，**Linear 完全不知道对面是 agent**——这是浏览器 Agent 路径的全部价值：**对产品方零改造**。代价是延迟、不稳定（页面改 UI 就崩）、成本（每步都要截图 + 视觉模型推理）。

## 7. 几条本质判断

**判断 1：MCP 把"集成"从工程项目变成商品。** Pre-Agent 时代，单 SaaS 集成 4–8 周 + 50K–200K USD [[7]](https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/) [[8]](https://prismatic.io/blog/cut-saas-integration-dev-time-with-embedded-ipaas/) 是常态；MCP 化以后，接一个新工具趋近于"JSON 加 4 行 + 配一个 token"。集成工程师这个岗位的稀缺性正在被磨平（⚠ 解读）——Zapier / Workato / MuleSoft 的长期定价权根基是"专业字段映射 + 私有连接器"，两者都被协议层击穿。Pre-Agent 的"集成层"（iPaaS / Zapier / MuleSoft）**被双面挤压**——上面被 MCP 商品化，下面被浏览器 Agent 兜底；中间 60–200K USD/年的集成项目利润空间被压缩。

**判断 2：5 年后 web 产品仍以 GUI 为主入口的判断会被推翻。** ⚠ 解读，依据：Imperva 51% / Cloudflare 30% 非人类流量 [[9]](https://www.imperva.com/blog/2025-imperva-bad-bot-report-how-ai-is-supercharging-the-bot-threat/) [[11]](https://blog.cloudflare.com/radar-2025-year-in-review/)、HUMAN +7,851% 同比 [[13]](https://www.humansecurity.com/learn/blog/ai-traffic-growth-2025-key-findings/) 已经把"主流量来自人"这个假设打掉。但 GUI 不会消失，它会变成"**人审批 + agent 执行**"的最后一公里，类似于 GitHub UI 不消失但开发者主战场迁到 CLI / IDE。

**判断 3：API-first 已经演化成 Agent-first。** ⚠ 解读，依据：Stripe / Vercel / Figma / Notion / Atlassian / Slack 2025 都按"先发 MCP server / Agent toolkit、再发新 API"的顺序工作；API 是给开发者的，MCP 是给 agent 的，**两者目标读者已经不同**。Anthropic Agent Skills 是这一转向的标准化层。dev SaaS 的"双 UI 失血"传导链是真实的——任何不出 MCP server 的 dev SaaS（项目管理 / 监控 / CI / feature flag / analytics）在 12–24 个月内会被绕过（⚠ 解读，依据：MCP registry 12 个月从 1200 增到 9400+ [[15]](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol) + 主流 dev SaaS 已普遍出官方 server [[41]](https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/) [[18]](https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/)）。2026-02 以来的"SaaSpocalypse"行情（Anthropic Claude Cowork 发布触发单日 2850 亿美元软件股市值蒸发 [[81]](https://www.cnbc.com/2026/02/06/ai-anthropic-tools-saas-software-stocks-selloff.html)）即同一传导链的市场表达。

**判断 4：三路径终局——MCP 赢协议层，CLI 赢 dev 工具，浏览器 Agent 赢长尾。** ⚠ 解读。MCP 在结构化 SaaS（Atlassian / Notion / Stripe / Figma）已是事实标准。CLI 在 dev 圈不会被取代——cost / latency / reliability 三方面都最优；OpenCLI + CLI-Anything 让它的劣势（能力面窄、覆盖少）被社区补齐。浏览器 Agent 是面向"永远不会主动出 MCP"的长尾网站的兜底（政府门户、小电商、遗留 ERP）；Operator / Manus / browser-use / Skyvern 四家分摊。三路径互补而非替代。

**判断 5：未来 3 年最重要的协议级机会是 gateway / registry / aggregator 这三层。** ⚠ 解读，依据：单点 server 已商品化、参考 [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) 与 SAP / Composio / Cloudflare 三种 gateway 已同步出现 [[23]](https://community.sap.com/t5/technology-blog-posts-by-sap/connecting-custom-joule-agents-to-mcp-servers-a-poc-architecture-for/ba-p/14356644) [[25]](https://composio.dev/blog/introducing-tool-router-(beta)) [[16]](https://blog.cloudflare.com/code-mode-mcp/)。真正稀缺的不是"我有一个 GitHub MCP server"，而是"把 N 个 agent × M 个 server 关系收敛成 1×M 的中间层"。这一层对位的不是 Zapier，而是 **Okta + Cloudflare + npm registry 的合体**——身份、边界、审计、发现、计费。2027 年前会出现至少一个独角兽（⚠ 作者预测）。

**判断 6：MCP 进入 Linux Foundation 是协议层"商品化"的关键加速器。** ⚠ 解读，依据：AAIF 由 Anthropic / Block / OpenAI 共同创立、Google / MS / AWS / Cloudflare 背书 [[2]](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) [[3]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)。一年内从"一家公司发的 spec"变成"多家 hyperscaler 共同治理"，类似 Kubernetes 进 CNCF 的剧本，但更快。中立化是 SaaS 厂商敢于全力做 MCP server 的政治前提——只要 MCP 还在 Anthropic 一家手里，Salesforce / Atlassian 都会保留观望。捐赠之后这层博弈消失。下一步可能是 ISO / IETF 标准化（⚠ 推测，DNS-discovery 已有 IETF draft [[22]](https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/)）。

**判断 7：Streamable HTTP 无状态化是远程 MCP 大规模商用的最后一公里。** ⚠ 解读，依据：2026 路线图把它列为优先级 1 [[20]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)。目前主流远程 MCP 是有状态长连接，和 CDN / L7 负载均衡天然不合；Cloudflare / Render / Fly.io 这一类 edge 玩家正等着这一条落地以便把 MCP server 当 Worker 部署。一旦 stateless 化通过，"remote MCP 当成边缘 serverless 函数跑"会成默认部署形态，本地 stdio server 退化成开发 / 内网兜底（⚠ 推测）。

**判断 8：反 Bot 经济学是 SaaS 商业模式重构的隐线。** Cloudflare default block + pay-per-crawl + AI Crawl Control 把"区分友 Agent / 恶 Agent"商品化 [[78]](https://blog.cloudflare.com/introducing-pay-per-crawl/) [[79]](https://blog.cloudflare.com/introducing-ai-crawl-control/)。⚠ **解读**：Cloudflare 在做的是把 HTTP 402 这个 1997 年规范但从没用起来的状态码激活成"每条请求 micropayment"的基础设施；这层一旦立起来，SaaS 不再需要纠结 per-call vs per-seat，转移到"按 agent 调用 path 收钱"。给传统集成赛道留了**短窗口**：在浏览器 Agent 可靠性达到 95% 之前（当前 OSWorld-Verified 78% [[72]](https://llm-stats.com/benchmarks/osworld-verified)）还有 12–24 个月的弹性。

## 信源

[1] Anthropic, "Introducing the Model Context Protocol," *Anthropic News*, Nov. 25, 2024. [Online]. Available: <https://www.anthropic.com/news/model-context-protocol>

[2] Linux Foundation, "Linux Foundation Announces the Formation of the Agentic AI Foundation (AAIF)," Dec. 9, 2025. (奠基项目 MCP / goose / AGENTS.md；Google / Microsoft / AWS / Cloudflare / Bloomberg 背书；MCP SDK 月下载 9700 万、活跃 server 10,000+。) [Online]. Available: <https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation>

[3] Anthropic, "Donating the Model Context Protocol and establishing the Agentic AI Foundation," *Anthropic News*, Dec. 9, 2025. [Online]. Available: <https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation>

[4] GitHub Engineering, "GitHub CLI 1.0 is now available," *GitHub Blog*, Sep. 17, 2020. (Beta 期内 250K+ PR、350K+ merge、20K+ issues created via CLI.) [Online]. Available: <https://github.blog/2020-09-17-github-cli-1-0-is-now-available/>

[5] Stripe, "Introducing the Stripe CLI," *Stripe Blog*, Nov. 2019. [Online]. Available: <https://stripe.com/blog/stripe-cli>

[6] Charm, "The Next Generation of the Command Line," *Charm Blog*, 2025. (Bubble Tea 23k stars, 4000+ apps, 11,682 importing projects.) [Online]. Available: <https://charm.land/blog/the-next-generation/>

[7] Software Pricing Guide, "MuleSoft vs Boomi vs Workato Pricing 2026," 2026. (MuleSoft 起步 80K USD/yr、企业 API-led 500K–2M USD；Workato 500–2K USD/月、10K–150K+ USD/yr；Zapier 20–599 USD/月。) [Online]. Available: <https://softwarepricingguide.com/mulesoft-vs-boomi-vs-workato-pricing-2026-the-real-cost-of-ipaas-apis-and-automation/>

[8] Prismatic, "Cut SaaS Integration Dev Time with Embedded iPaaS," *Prismatic Blog*. (典型单 SaaS 集成 4–6 周工程时间，复杂映射可到 8 周。) [Online]. Available: <https://prismatic.io/blog/cut-saas-integration-dev-time-with-embedded-ipaas/>

[9] Imperva, "2025 Imperva Bad Bot Report: How AI is Supercharging the Bot Threat," Apr. 2025. (Bad bot 37%, automated 51% of all web traffic.) [Online]. Available: <https://www.imperva.com/blog/2025-imperva-bad-bot-report-how-ai-is-supercharging-the-bot-threat/>

[10] Thales / Imperva, "AI Fuels Bots That Now Make up More Than Half of Global Internet Traffic," *BusinessWire*, Apr. 15, 2025. [Online]. Available: <https://www.businesswire.com/news/home/20250415432215/en/Artificial-Intelligence-Fuels-Rise-of-Hard-to-Detect-Bots-That-Now-Make-up-More-Than-Half-of-Global-Internet-Traffic-According-to-the-2025-Imperva-Bad-Bot-Report>

[11] Cloudflare, "The 2025 Cloudflare Radar Year in Review," *Cloudflare Blog*, Dec. 2025. (Bot 30% global traffic; AI crawler 4.2% HTML; non-AI bot 50% HTML requests.) [Online]. Available: <https://blog.cloudflare.com/radar-2025-year-in-review/>

[12] InfoQ, "Cloudflare Year in Review: AI Bots Crawl Aggressively," Dec. 2025. [Online]. Available: <https://www.infoq.com/news/2025/12/cloudflare-2025-ai-bots/>

[13] HUMAN Security, "Measuring the AI-Driven Internet — 2026 State of AI Traffic & Cyberthreat Benchmark Report," 2026. (Agentic AI 流量 +7851% YoY；2025 月度 +187%.) [Online]. Available: <https://www.humansecurity.com/learn/blog/ai-traffic-growth-2025-key-findings/>

[14] Cloud Security Alliance, "API Security in the AI Era: Best Practices for AI-Driven APIs," Sep. 9, 2025. (Hundreds/day → thousands/min AI workloads.) [Online]. Available: <https://cloudsecurityalliance.org/blog/2025/09/09/api-security-in-the-ai-era>

[15] Digital Applied, "MCP Adoption Statistics 2026: Model Context Protocol," 2026. (Registry Q1 1200 → Q3 3400 → year-end 6800 → 2026-04 9400+；mcp.so 16,670；78% 企业 AI 团队生产用 MCP-backed agent.) [Online]. Available: <https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol>

[16] Cloudflare, "Code Mode: give agents an entire API in 1,000 tokens," *Cloudflare Blog*, 2026. (原始 MCP 工具暴露需 >1M token；Code Mode 压缩到 search()+execute() 两个工具、约 1000 token。) [Online]. Available: <https://blog.cloudflare.com/code-mode-mcp/>

[17] Model Context Protocol, "Architecture overview," *MCP Docs*. (三原语 Tools / Resources / Prompts；每个原语 */list、*/get、tools/call 方法。) [Online]. Available: <https://modelcontextprotocol.io/docs/learn/architecture>

[18] Sentry, "Yes, Sentry has an MCP Server (...and it's pretty good)," *Sentry Blog*. (16 tool call、OAuth、Streamable HTTP / SSE。) [Online]. Available: <https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/>

[19] Cloudflare, "Scaling MCP adoption: Our reference architecture for simpler, safer and cheaper enterprise deployments of MCP," *Cloudflare Blog*, 2026. (AI Gateway + MCP Server Portals + Cloudflare Gateway 三件套。) [Online]. Available: <https://blog.cloudflare.com/enterprise-mcp/>

[20] Model Context Protocol Blog, "The 2026 MCP Roadmap," Mar. 2026. (四优先方向：Streamable HTTP 无状态化、Tasks primitive lifecycle、治理成熟化、企业就绪。) [Online]. Available: <https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/>

[21] modelcontextprotocol, "SEP-1649: MCP Server Cards - HTTP Server Discovery via .well-known," *GitHub Issue*. [Online]. Available: <https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649>

[22] Internet Engineering Task Force, "draft-morrison-mcp-dns-discovery-02 — Discovery of Model Context Protocol Servers via DNS TXT Records," IETF Datatracker. [Online]. Available: <https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/>

[23] SAP Community, "Connecting custom Joule Agents to MCP servers: A POC Architecture for Enterprise HR Intelligence," 2026. [Online]. Available: <https://community.sap.com/t5/technology-blog-posts-by-sap/connecting-custom-joule-agents-to-mcp-servers-a-poc-architecture-for/ba-p/14356644>

[24] agentic-community, "mcp-gateway-registry," *GitHub*. (Keycloak / Entra OAuth + 统一 audit + dynamic tool discovery。) [Online]. Available: <https://github.com/agentic-community/mcp-gateway-registry>

[25] Composio, "Introducing Tool Router (Beta)," *Composio Blog*, Oct. 1, 2025. (Tool Router 一个 endpoint 接 1000+ toolkits；2025-10-01 上线。) [Online]. Available: <https://composio.dev/blog/introducing-tool-router-(beta)>

[26] Das Root, "The New MCP Authorization Specification," Apr. 2026. (2026-03-15 spec：OAuth 2.1 + PKCE + RFC 8707 resource indicators。) [Online]. Available: <https://dasroot.net/posts/2026/04/mcp-authorization-specification-oauth-2-1-resource-indicators/>

[27] Toolradar, "Best MCP Servers in 2026: 25 You Should Install Now," 2026. (Postgres write-DSN footgun；read-only DSN 是事实底线。) [Online]. Available: <https://toolradar.com/blog/best-mcp-servers-2026>

[28] Practical DevSecOps, "MCP OAuth 2.1 Security: Authentication Best Practices for AI Tool Integrations," 2026. (audit log SOC 2 ≥1y, HIPAA ≥3y, FINRA ≥7y。) [Online]. Available: <https://www.practical-devsecops.com/mcp-oauth-2-1-implementation/>

[29] Cloudflare, "MCP server portals," *Cloudflare One Docs*. (Shadow MCP 检测、DLP 扫描、Gateway 路由。) [Online]. Available: <https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/mcp-portals/>

[30] Stripe, "Adding payments to your LLM agentic workflows," *Stripe Dot Dev Blog*, Nov. 2024. [Online]. Available: <https://stripe.dev/blog/adding-payments-to-your-agentic-workflows>

[31] The Letter Two, "Stripe Launches SDK for AI Agents to Enable Payments," Nov. 15, 2024. [Online]. Available: <https://thelettertwo.com/2024/11/15/stripe-releases-sdk-enabling-payment-and-billing-capabilities-for-ai-agents/>

[32] Vercel, "AI SDK 5," *Vercel Blog*, Jul. 31, 2025. [Online]. Available: <https://vercel.com/blog/ai-sdk-5>

[33] Vercel, "AI SDK 6," *Vercel Blog*, Oct. 2025. (ToolLoopAgent, needsApproval gate.) [Online]. Available: <https://vercel.com/blog/ai-sdk-6>

[34] InfoQ, "Vercel Ship AI 2025 Key Announcements," Oct. 2025. [Online]. Available: <https://www.infoq.com/news/2025/10/vercel-ship-ai/>

[35] Spectre Console, "OpenCLI Specification (OCS) draft," *GitHub*, 2025. (平台/语言无关的 CLI schema 规范，灵感来自 OpenAPI；JSON/YAML 文档描述 CLI 命令树.) [Online]. Available: <https://github.com/spectreconsole/open-cli>

[36] OpenCLI, "OpenCLI Specification," *opencli.org*, 2025. (官方主页与多版本规范.) [Online]. Available: <https://opencli.org/>

[37] HKUDS, "CLI-Anything: Making ALL Software Agent-Native," *GitHub*, 2025. (开源把 GIMP / Blender / LibreOffice / OBS / Audacity 等 GUI 应用封装成结构化 CLI；约 21K stars.) [Online]. Available: <https://github.com/HKUDS/CLI-Anything>

[38] CLI Anything Hub, "Agent-friendly CLI registry," *clianything.cc*, 2025. (CLI-Hub 包管理器：`pip install cli-anything-hub` 一行搜索 / 安装 / 卸载 CLI harness.) [Online]. Available: <https://clianything.cc/>

[39] Vercel Labs, "agent-browser: Browser automation CLI for AI agents," *GitHub*, 2025. (Rust CLI，跨 Claude Code / Codex / Cursor / Gemini CLI / Copilot / Goose / OpenCode / Windsurf 调用浏览器；默认引擎 Chrome for Testing，`--engine` 切 lightpanda.) [Online]. Available: <https://github.com/vercel-labs/agent-browser>

[40] A. Nigam, "agent-browser: 74 browser automation tools via MCP," *GitHub*, 2025. (同名社区项目，走 MCP 路线，74 个 browser tool.) [Online]. Available: <https://github.com/abhinav-nigam/agent-browser>

[41] GitHub, "github-mcp-server is now available in public preview," *GitHub Changelog*, Apr. 2025. [Online]. Available: <https://github.blog/changelog/2025-04-04-github-mcp-server-public-preview/>

[42] modelcontextprotocol, "Production Results: MCP Server for GitHub Validates Anthropic's Code-First Pattern (98% Token Reduction)," *GitHub Discussion #629*, 2025. [Online]. Available: <https://github.com/orgs/modelcontextprotocol/discussions/629>

[43] Cloudflare, "Cloudflare Accelerates AI Agent Development With The Industry's First Remote MCP Server," *Press Release*, Apr. 7, 2025. [Online]. Available: <https://www.cloudflare.com/press/press-releases/2025/cloudflare-accelerates-ai-agent-development-remote-mcp/>

[44] Cloudflare, "Thirteen new MCP servers from Cloudflare you can use today," *Cloudflare Blog*, 2025. [Online]. Available: <https://blog.cloudflare.com/thirteen-new-mcp-servers-from-cloudflare/>

[45] Cloudflare, "Build and deploy Remote Model Context Protocol (MCP) servers to Cloudflare," *Cloudflare Blog*, Apr. 2025. [Online]. Available: <https://blog.cloudflare.com/remote-model-context-protocol-servers-mcp/>

[46] Atlassian, "Introducing Atlassian's Remote Model Context Protocol (MCP) Server," May 1, 2025. [Online]. Available: <https://www.atlassian.com/blog/announcements/remote-mcp-server>

[47] Notion, "September 18, 2025 – Notion 3.0: Agents," 2025. [Online]. Available: <https://www.notion.com/releases/2025-09-18>

[48] Figma, "Introducing our Dev Mode MCP server: Bringing Figma into your workflow," *Figma Blog*, 2025. [Online]. Available: <https://www.figma.com/blog/introducing-figma-mcp-server/>

[49] Figma, "Agents, Meet the Figma Canvas," *Figma Blog*, 2025. [Online]. Available: <https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/>

[50] Reworked, "Slack's Real-Time Search API and MCP Server Are Now Live," Oct. 13, 2025. [Online]. Available: <https://www.reworked.co/digital-workplace/slacks-rts-api-and-mcp-server-hit-general-availability/>

[51] Upstash, "Context7 MCP: Up-to-Date Docs for Any Cursor Prompt," *Upstash Blog*. [Online]. Available: <https://upstash.com/blog/context7-mcp>

[52] Apify, "apify-mcp-server," *GitHub*. (3000+ Actors 通过 MCP 暴露给 agent。) [Online]. Available: <https://github.com/apify/apify-mcp-server>

[53] Anthropic, "Equipping agents for the real world with Agent Skills," *Anthropic Engineering*, Oct. 2025. [Online]. Available: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>

[54] The New Stack, "Agent Skills: Anthropic's Next Bid to Define AI Standards," Oct. 2025. [Online]. Available: <https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/>

[55] SiliconANGLE, "Anthropic makes agent Skills an open standard," Dec. 18, 2025. [Online]. Available: <https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/>

[56] S. Willison, "Claude Skills are awesome, maybe a bigger deal than MCP," *simonwillison.net*, Oct. 16, 2025. [Online]. Available: <https://simonwillison.net/2025/Oct/16/claude-skills/>

[57] Anthropic, "Introducing computer use, a new Claude 3.5 Sonnet, and Claude 3.5 Haiku," Oct. 22, 2024. (OSWorld screenshot-only 14.9% / 多步 22.0%.) [Online]. Available: <https://www.anthropic.com/news/3-5-models-and-computer-use>

[58] TechCrunch, "OpenAI may preview its agent tool for users on the $200-per-month Pro plan," Jan. 23, 2025. [Online]. Available: <https://techcrunch.com/2025/01/23/openais-agent-tool-will-be-available-to-users-paying-200-per-month-for-pro/>

[59] MIT Technology Review, "OpenAI launches Operator—an agent that can use a computer for you," Jan. 23, 2025. [Online]. Available: <https://www.technologyreview.com/2025/01/23/1110484/openai-launches-operator-an-agent-that-can-use-a-computer-for-you/>

[60] Upstarts Media, "Browserbase Raises $40M Series B, Launches AI Automation Tool," Apr. 2025. (估值 $300M.) [Online]. Available: <https://www.upstartsmedia.com/p/browserbase-raises-40m-and-launches-director>

[61] Built In SF, "Browserbase Secures $40M Series B Round," Jun. 18, 2025. (累计 $67.5M.) [Online]. Available: <https://www.builtinsf.com/articles/browserbase-announces-40m-series-b-funding-20250618>

[62] Browserbase, "Stagehand — The SDK for Browser Agents," *GitHub*, 2025. [Online]. Available: <https://github.com/browserbase/stagehand>

[63] TechCrunch, "Browser Use, the tool making it easier for AI 'agents' to navigate websites, raises $17M," Mar. 23, 2025. [Online]. Available: <https://techcrunch.com/2025/03/23/browser-use-the-tool-making-it-easier-for-ai-agents-to-navigate-websites-raises-17m/>

[64] Y Combinator, "Open Source Startups funded by Y Combinator," 2026. (browser-use "近 3 月获 40k stars".) [Online]. Available: <https://www.ycombinator.com/companies/industry/open-source>

[65] Skyvern, "We raised $2.7M to fix browser automation (open source)," 2025. [Online]. Available: <https://www.skyvern.com/blog/skyvern-we-raised-2-7m-to-fix-browser-automation-open-source/>

[66] Tracxn, "Skyvern — 2026 Company Profile," Jan. 31, 2026. (11 员工, 复杂 benchmark 85.8% 成功率.) [Online]. Available: <https://tracxn.com/d/companies/skyvern/__joZNwZnvPpp5SWng14qfKwxCqqwKRt699DxAC4T5pfI>

[67] TechCrunch, "Chinese AI startup Manus reportedly gets funding from Benchmark at $500M valuation," Apr. 25, 2025. [Online]. Available: <https://techcrunch.com/2025/04/25/chinese-ai-startup-manus-reportedly-gets-funding-from-benchmark-at-500m-valuation/>

[68] SiliconANGLE, "Chinese startup behind Manus reportedly raises $75M in funding," Apr. 25, 2025. [Online]. Available: <https://siliconangle.com/2025/04/25/chinese-startup-behind-manus-reportedly-raises-75m-funding/>

[69] CNBC, "Meta acquires intelligent agent firm Manus," Dec. 30, 2025. (Manus 年化营收 $100M+，run rate $125M+.) [Online]. Available: <https://www.cnbc.com/2025/12/30/meta-acquires-singapore-ai-agent-firm-manus-china-butterfly-effect-monicai.html>

[70] TechCrunch, "Meta just bought Manus, an AI startup everyone has been talking about," Dec. 29, 2025. [Online]. Available: <https://techcrunch.com/2025/12/29/meta-just-bought-manus-an-ai-startup-everyone-has-been-talking-about/>

[71] TechCrunch, "China vetoes Meta's $2B Manus deal after months-long probe," Apr. 27, 2026. [Online]. Available: <https://techcrunch.com/2026/04/27/china-vetoes-metas-2b-manus-deal-after-months-long-probe/>

[72] LLM Stats, "OSWorld-Verified Benchmark Leaderboard," 2026. (Claude Mythos Preview 79.6%, GPT-5.5 78.7%, Claude Opus 4.7 78.0%.) [Online]. Available: <https://llm-stats.com/benchmarks/osworld-verified>

[73] Bain & Company, "Will Agentic AI Disrupt SaaS? — Technology Report 2025," 2025. [Online]. Available: <https://www.bain.com/insights/will-agentic-ai-disrupt-saas-technology-report-2025/>

[74] Deloitte Insights, "SaaS meets AI agents: 2026 TMT Predictions," 2026. [Online]. Available: <https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/saas-ai-agents.html>

[75] Monetizely, "The Doomed Evolution of Salesforce's Agentforce Pricing," 2025. ($2/conversation 引发客户反弹.) [Online]. Available: <https://www.getmonetizely.com/blogs/the-doomed-evolution-of-salesforces-agentforce-pricing>

[76] Metronome, "State of Usage-Based Pricing 2025 Report," 2025. (78% UBP 公司过去 5 年内才上.) [Online]. Available: <https://metronome.com/state-of-usage-based-pricing-2025>

[77] MIT Technology Review, "Cloudflare will now block AI bots from crawling its clients' websites by default," Jul. 1, 2025. [Online]. Available: <https://www.technologyreview.com/2025/07/01/1119498/cloudflare-will-now-by-default-block-ai-bots-from-crawling-its-clients-websites/>

[78] Cloudflare, "Introducing pay per crawl: Enabling content owners to charge AI crawlers for access," *Cloudflare Blog*, 2025. (HTTP 402 + payment intent header.) [Online]. Available: <https://blog.cloudflare.com/introducing-pay-per-crawl/>

[79] Cloudflare, "The next step for content creators in working with AI bots: Introducing AI Crawl Control," *Cloudflare Blog*, 2025. [Online]. Available: <https://blog.cloudflare.com/introducing-ai-crawl-control/>

[80] MCP Playground, "The Complete Guide to MCP Config Files — Claude Desktop, Cursor, Lovable, and More," 2026. [Online]. Available: <https://mcpplaygroundonline.com/blog/complete-guide-mcp-config-files-claude-desktop-cursor-lovable>

[81] *CNBC*, "AI fears pummel software stocks: Is it 'illogical' panic or a SaaS apocalypse?" Feb. 6, 2026. (2026-02-03 Claude Cowork 发布触发 SaaSpocalypse，单日 $285B 软件股市值蒸发.) [Online]. Available: <https://www.cnbc.com/2026/02/06/ai-anthropic-tools-saas-software-stocks-selloff.html>
