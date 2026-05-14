# 2026-05-14：SDLC 栈 / GUI 产品的 CLI / MCP / 浏览器化 (L13) 层深度研究

> 系列子报告：软件开发栈 Pre-Coding-Agent vs Post-Coding-Agent。本篇覆盖 **L13（GUI app / SaaS 网站 → Agent 可调用界面的供给侧改造）**。L10b 写的是协议（MCP 本体 + dev 工具的 MCP server），本篇写的是**被迫供给一侧的产品**——所有 SaaS（不止 dev）如何在 2024–2026 这 18 个月内被推上"必须给 Agent 长一张脸"的台子。

这一层在 Pre-Agent 时代**没有"层"的概念**：SaaS 只需要做 GUI，API 是开发者集成的副产品，CLI 是少数极客的偏好。Agent 时代之后流量结构突变，强迫每家产品在三条路径里至少做一条：CLI（命令行）、MCP server（协议化）、或者让 Agent 用浏览器点（Computer Use / Operator）。**问题不再是"要不要做"而是"做哪一条 + 怎么收钱 + 怎么和反 Bot 系统兼容"**。

## 1. Pre-Agent 时代 SaaS 的"对外接口"三圈

Pre-Agent SaaS 默认是"GUI-first"。把对外接口画成三个同心圆：

- **核心圈：GUI**（人通过浏览器或 App 点击）。流量主路径，营销 / SEO / 转化漏斗 / NPS / 留存都围绕它建。
- **中间圈：REST / GraphQL API**。给企业集成、给 Zapier / MuleSoft / Workato 喂数据。是"集成层"的输入，但不是"主入口"。
- **外圈：CLI**。少数 SaaS 主动做。代表是 GitHub CLI 1.0（2020 年 9 月，beta 期内已被用于创建 25 万+ PR、35 万+ merge [[1]](https://github.blog/2020-09-17-github-cli-1-0-is-now-available/)）、Stripe CLI（2019 年 11 月发布，主打 webhook 转发 + 实时 API 日志 + 对象 CRUD [[2]](https://stripe.com/blog/stripe-cli)）、`aws` (2013)、`gcloud` (2014)、`kubectl` (2014)、Vercel CLI 等。

外圈在 Pre-Agent 时代是**开发者偏好**而非战略层——做了加分，不做不死。Bubble Tea（Charm.sh TUI 框架）的 23k stars、4000+ 应用、被 AWS / NVIDIA / Microsoft Azure 内部使用 [[3]](https://charm.land/blog/the-next-generation/) 说明 CLI/TUI 在 2024 之前已经在悄悄复兴，但还不是企业级 SaaS 的必选项。

整个三圈结构的底层假设是"**调用方是人或人写的脚本**"。流量、定价、rate limit、风控全部围绕这个假设建。

## 2. Agent 时代流量模式怎么变了

四个独立来源的数据指向同一个事实——**自动化流量 2025 年第一次超过人类**：

- **Imperva 2025 Bad Bot Report**：自动化流量首次过半（51% of all web traffic），其中坏 bot 37%、好 bot 14%。坏 bot 占比从 2024 年 32% 升到 2025 年 37%，连续第 6 年上升 [[4]](https://www.imperva.com/blog/2025-imperva-bad-bot-report-how-ai-is-supercharging-the-bot-threat/) [[5]](https://www.businesswire.com/news/home/20250415432215/en/Artificial-Intelligence-Fuels-Rise-of-Hard-to-Detect-Bots-That-Now-Make-up-More-Than-Half-of-Global-Internet-Traffic-According-to-the-2025-Imperva-Bad-Bot-Report)。
- **Cloudflare Radar 2025 Year in Review**：bot 流量占 30% 全球 web traffic；AI 爬虫单独占 4.2% HTML 请求，Googlebot 另占 4.5%；非 AI bot 全年生成 50% HTML 请求，比人类生成多 7%、峰值多 25% [[6]](https://blog.cloudflare.com/radar-2025-year-in-review/) [[7]](https://www.infoq.com/news/2025/12/cloudflare-2025-ai-bots/)。
- **HUMAN Security 2026 State of AI Traffic**：agentic AI 流量同比增长 **7,851%**，2025 年月度量从 1 月到 12 月增长 187%（接近年化三倍）[[8]](https://www.humansecurity.com/learn/blog/ai-traffic-growth-2025-key-findings/)。
- **CSA 2025 API 安全报告**：以前一天几百次调用的 API 现在被 AI workload 拉到每分钟几千次 [[9]](https://cloudsecurityalliance.org/blog/2025/09/09/api-security-in-the-ai-era)。

⚠ **解读**：这些数字混合了"AI 训练爬虫 + 推理时 Agent + 传统 bot"三类，区分质量参差。但从 SaaS 视角看，**调用方不再是人**已经是事实而非预言。每家 SaaS 收到的请求里，越来越多的来源是 Claude Code / Devin / Operator / Manus / 自建 Agent。流量结构的拐点已经过了。

## 3. 三条供给路径：CLI、MCP、浏览器 Agent

### 3.1 CLI 路径——老技术新身位

Pre-Agent CLI 服务开发者；Agent 时代 CLI 同时服务 Coding Agent。Claude Code / Devin / Codex CLI 之所以能跑通，部分原因是宿主操作系统里已经有 `gh`、`stripe`、`vercel`、`aws`、`gcloud`、`kubectl` 这层稳定接口——agent 只需要拼 shell 命令而不必学每家 SaaS 的 SDK。

代表性升级：

- **Stripe Agent Toolkit**（2024-11 发布，2026-02 已到 0.7.0）：在 Stripe CLI 之上加一层 LangChain / Vercel AI SDK / CrewAI / OpenAI Agents SDK 适配，把 PaymentIntent / Customer / Invoice / Subscription / Payment Link / Refund 包装成可被 function call 的工具；强制要求 Restricted API Key (`rk_*`) 而非 secret key，做粒度授权 [[10]](https://stripe.dev/blog/adding-payments-to-your-agentic-workflows) [[11]](https://thelettertwo.com/2024/11/15/stripe-releases-sdk-enabling-payment-and-billing-capabilities-for-ai-agents/)。
- **Vercel AI SDK 5**（2025-07-31）增强 tool 能力：dynamic tools、provider-executed functions、lifecycle hooks、`stopWhen` / `prepareStep` 控制 agentic loop [[12]](https://vercel.com/blog/ai-sdk-5)。**AI SDK 6 beta**（2025-10 Vercel Ship AI）引入 `ToolLoopAgent` 抽象与 `needsApproval: true` 的 human-in-the-loop 审批 gate [[13]](https://vercel.com/blog/ai-sdk-6) [[14]](https://www.infoq.com/news/2025/10/vercel-ship-ai/)。
- Bubble Tea / Gum / Charm 生态的扩张让 TUI 同时服务人和 agent——agent 通过子进程 stdio 调用，人通过键盘交互，**同一个二进制双 UI**。

⚠ **解读**：CLI 路径门槛最低（很多 SaaS 已经有）、对存量改造最小，但暴露的能力面也最窄（只能跑 SaaS 想暴露的子集）。CLI 路径的赢家是已经有官方 CLI 的厂商；后来者直接做 MCP 而非补 CLI 更划算。

### 3.2 MCP 路径——产品方主动暴露 server

L10b 已经覆盖了 MCP 协议本体与 dev 工具 server。本篇视角不同：**所有非 dev SaaS 也在被迫做 MCP server**。2025 年关键节点：

- **Atlassian Remote MCP**（2025-05-01 beta）：Jira + Confluence Cloud 用户从 Anthropic 直接 summarize / create issue / 多步 action，权限完全继承产品侧 ACL [[15]](https://www.atlassian.com/blog/announcements/remote-mcp-server)。
- **Cloudflare Remote MCP**（2025-04-07）：第一个支持远端 MCP server 部署的平台，配套 `workers-oauth-provider`、`McpAgent` 类、`mcp-remote` adapter、Workers AI playground 作为 MCP client；后续放出 13 个官方 server [[16]](https://www.cloudflare.com/press/press-releases/2025/cloudflare-accelerates-ai-agent-development-remote-mcp/) [[17]](https://blog.cloudflare.com/thirteen-new-mcp-servers-from-cloudflare/)。
- **Notion 3.0 Agents + Notion MCP**（2025-09-18 "Make with Notion"）：first-party 集成 Lovable / Perplexity / Mistral / HubSpot；Cursor 可拉 Notion 中的 spec、写代码、再回写状态 [[18]](https://www.notion.com/releases/2025-09-18)。
- **Figma Dev Mode MCP server**（2025）：远端访问开放，agent 可读 design context、可写 frame / component / variable / auto layout，用 design system 作 source of truth；现 beta 免费，未来 usage-based 计费 [[19]](https://www.figma.com/blog/introducing-figma-mcp-server/) [[20]](https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/)。
- **Slack RTS API + MCP**（2025-10-13 GA）：query-based 实时检索 Slack 对话数据，**数据不离开 Slack 基础设施**，权限按已有 ACL [[21]](https://www.reworked.co/digital-workplace/slacks-rts-api-and-mcp-server-hit-general-availability/)。
- **Stripe MCP server**：是 Agent Toolkit 的另一种暴露面（function-call 与 MCP 并行）[[10]](https://stripe.dev/blog/adding-payments-to-your-agentic-workflows)。

**注册中心数量爆炸**：官方 MCP registry 季度滚动——Q1 2025 末 ~1200、Q3 末 3400、年末 6800，2026-04 中过 9400+；非官方 mcp.so 单点索引 16,670（2025-09）[[22]](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol)。

**Anthropic Agent Skills**（2025-10 公布，2025-12 转为开放标准）是 MCP 路径上的关键封装层 [[23]](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) [[24]](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/) [[25]](https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/)。Skill = 一个目录 + `SKILL.md`，把"打开 Figma、找 design system、读出 token、生成代码"这种 GUI workflow 打包成可被 agent **渐进发现 + 按需加载**的能力；首批合作伙伴 Atlassian / Canva / Cloudflare / Figma / Notion / Ramp / Sentry [[25]](https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/)。Simon Willison 评价"可能比 MCP 还重要" [[26]](https://simonwillison.net/2025/Oct/16/claude-skills/)。这是产品方第一次有"把自己的高频 workflow 用极少 token 暴露给 agent"的标准做法。

### 3.3 浏览器 Agent 路径——把 GUI 当 API 用

当 SaaS 不肯出 MCP 也没 CLI、或者 agent 需要跨多家 SaaS 但每家都没标准接口时，**让 agent 用浏览器**就成为最后的兜底。三类玩家：

**底层模型 / 大平台：**

- **Anthropic Computer Use**（2024-10-22 public beta，Claude 3.5 Sonnet）[[27]](https://www.anthropic.com/news/3-5-models-and-computer-use)。OSWorld（screenshot-only）发布时 14.9%（次优 7.8%），多步 22.0%；到 2026-05 Claude Opus 4.7 在 OSWorld-Verified 78.0%，Mythos Preview 79.6% [[28]](https://llm-stats.com/benchmarks/osworld-verified)——**18 个月内 5x 提升**。
- **OpenAI Operator**（2025-01-23 research preview，ChatGPT Pro $200/月）。基于 Computer-Using Agent (CUA) 模型，自带浏览器、自纠错重试 [[29]](https://techcrunch.com/2025/01/23/openais-agent-tool-will-be-available-to-users-paying-200-per-month-for-pro/) [[30]](https://www.technologyreview.com/2025/01/23/1110484/openai-launches-operator-an-agent-that-can-use-a-computer-for-you/)。

**基础设施 / SDK 中间层：**

- **Browserbase**：headless 浏览器即服务。2025-04 Series B $40M，估值 $300M（约前轮 4x），累计 $67.5M [[31]](https://www.upstartsmedia.com/p/browserbase-raises-40m-and-launches-director) [[32]](https://www.builtinsf.com/articles/browserbase-announces-40m-series-b-funding-20250618)。
- **Stagehand**（Browserbase 开源 SDK，MIT licensed）：natural language + code 混合写 browser agent，对抗 page 改版 [[33]](https://github.com/browserbase/stagehand)。多语言 SDK：TypeScript / Python / Go / Ruby / C# .NET。
- **browser-use**（开源 Python lib，2025-Q1 YC W25 批次）：2025-03 Seed $17M，领投 Felicis 的 Astasia Myers，参投 Paul Graham / A Capital / Nexus Venture Partners [[34]](https://techcrunch.com/2025/03/23/browser-use-the-tool-making-it-easier-for-ai-agents-to-navigate-websites-raises-17m/)。YC 描述其"近 3 个月获得 40k stars，最大的开源 web agent 项目" [[35]](https://www.ycombinator.com/companies/industry/open-source)。

**应用层 / 替代 RPA：**

- **Skyvern**：开源，LLM + 计算机视觉处理 auth / 表单 / CAPTCHA / 下载；声称复杂 benchmark 85.8% 成功率；2025-12 Seed $2.7M（创始团队 11 人，2026-01 数据）[[36]](https://www.skyvern.com/blog/skyvern-we-raised-2-7m-to-fix-browser-automation-open-source/) [[37]](https://tracxn.com/d/companies/skyvern/__joZNwZnvPpp5SWng14qfKwxCqqwKRt699DxAC4T5pfI)。
- **Manus AI**（Butterfly Effect 出品）：2025-03 上线全自主 AI agent；2025-04 Benchmark 领投 $75M，估值 ~$500M（前轮 $100M 的 5x）[[38]](https://techcrunch.com/2025/04/25/chinese-ai-startup-manus-reportedly-gets-funding-from-benchmark-at-500m-valuation/) [[39]](https://siliconangle.com/2025/04/25/chinese-startup-behind-manus-reportedly-raises-75m-funding/)；8 个月年化营收过 $100M、run rate 超 $125M [[40]](https://www.cnbc.com/2025/12/30/meta-acquires-singapore-ai-agent-firm-manus-china-butterfly-effect-monicai.html)；2025-12 Meta 宣布 ~$2B 收购 [[41]](https://techcrunch.com/2025/12/29/meta-just-bought-manus-an-ai-startup-everyone-has-been-talking-about/)；2026-04 中国 NDRC 否决该交易 [[42]](https://techcrunch.com/2026/04/27/china-vetoes-metas-2b-manus-deal-after-months-long-probe/)。

**技术路线对比（解读）**：

| 路径 | 延迟 | 成本 / 调用 | 可靠性 | 改产品的成本 |
|---|---|---|---|---|
| CLI | 100ms 量级 | 几乎 0 | 高（命令稳定） | 低（已有 CLI 加 wrapper） |
| MCP | 100–500ms | 低（token 友好） | 中–高 | 中（要新做 server + auth） |
| 浏览器 Agent | 5–60s | 高（截图 + 推理） | 低–中（页面改了就崩） | 0（产品不用改） |

⚠ **解读依据**：延迟和成本是 Claude Code / Operator 用户社区经验值；可靠性来自 OSWorld 78% 即代表 22% 失败率，比 MCP 工具调用 95%+ 成功率显著低。

## 4. 新需求：选型、定价、反 Bot

**产品方选型**：dev 工具型 SaaS（GitHub / Stripe / Vercel / Sentry / Linear）三条都做，CLI + MCP + 配 Skills 文档；非 dev 但有结构化数据（Notion / Atlassian / Figma / Slack）优先 MCP；面向消费者 / 长尾电商 / 政府门户基本上没法主动改造，被迫接受被浏览器 Agent 当 GUI 用。

**定价**：人类 per-seat 模型在 agent 时代被打穿——**1 个 seat 可能驱动 100x 流量**。Bain / Deloitte / Glean 2025 报告均指 SaaS 在转 "subscription + consumption" 混合 [[43]](https://www.bain.com/insights/will-agentic-ai-disrupt-saas-technology-report-2025/) [[44]](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/saas-ai-agents.html)。但 **per-call 也踩坑**：Salesforce Agentforce $2/conversation 模式被客户骂到改版 [[45]](https://www.getmonetizely.com/blogs/the-doomed-evolution-of-salesforces-agentforce-pricing)。Metronome 2025 报告：78% 实施 UBP 的公司是过去 5 年内才上的 [[46]](https://metronome.com/state-of-usage-based-pricing-2025)。

**反 Bot 经济学**：Cloudflare 2025-07 把 AI 爬虫 **默认屏蔽** [[47]](https://www.technologyreview.com/2025/07/01/1119498/cloudflare-will-now-by-default-block-ai-bots-from-crawling-its-clients-websites/)，同步推 **pay-per-crawl** 市场（HTTP 402 Payment Required + 请求头携带 payment intent）[[48]](https://blog.cloudflare.com/introducing-pay-per-crawl/)。这是产品方第一次有标准化路径"**对友 Agent 收钱、对恶 Agent 屏蔽**"。⚠ **解读**：这本质是把 robots.txt 的礼貌层升级到经济激励层；如果 Cloudflare 押对，每条 HTTP 请求都会带 micropayment header，bot 流量从"被防御"变成"被定价"。

**GUI 双 UI 设计**：产品 UI 同时给人和 Agent 看，需要：（a）稳定的 ARIA / `data-testid` / 语义化 DOM 让浏览器 Agent 可定位；（b）`/.well-known/mcp/server-card.json` 让爬虫不连接就能发现能力（L10b SEP-1649 [[49]](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649)）；（c）`llms.txt` / Skills 目录给静态文档化暴露。

## 5. 具体案例与配置示例

### 5.1 Stripe Agent Toolkit（function call 风格）

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

要点：`rk_*` 锁死 agent 不能升级到 secret-key 范畴；toolkit 不直接管理 idempotency，agent 自己负责 [[10]](https://stripe.dev/blog/adding-payments-to-your-agentic-workflows)。

### 5.2 Cloudflare Remote MCP（Workers 部署）

```bash
npx create-cloudflare@latest mcp-demo \
  --template=cloudflare/ai/demos/remote-mcp-authless
cd mcp-demo && npx wrangler deploy
# 部署到 mcp-demo.<your>.workers.dev，Streamable HTTP transport
```

`workers-oauth-provider` 处理 OAuth flow；`McpAgent` 类把 Workers Durable Object 当 session 状态机；Claude / Cursor 在 client 端通过 `mcp-remote` adapter 连接 [[16]](https://www.cloudflare.com/press/press-releases/2025/cloudflare-accelerates-ai-agent-development-remote-mcp/) [[50]](https://blog.cloudflare.com/remote-model-context-protocol-servers-mcp/)。

### 5.3 browser-use（浏览器 Agent 路径）

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

## 6. 本质判断

1. **5 年后 web 产品仍以 GUI 为主入口的判断会被推翻**——⚠ 解读，依据：Imperva 51% / Cloudflare 30% 非人类流量、HUMAN +7,851% 同比已经把"主流量来自人"这个假设打掉。但 GUI 不会消失，它会变成"**人审批 + agent 执行**"的最后一公里，类似于 GitHub UI 不消失但开发者主战场迁到 CLI / IDE。

2. **API-first 已经演化成 Agent-first**——⚠ 解读，依据：Stripe / Vercel / Figma / Notion / Atlassian / Slack 2025 都按"先发 MCP server / Agent toolkit、再发新 API"的顺序工作；API 是给开发者的，MCP 是给 agent 的，**两者目标读者已经不同**。Anthropic Agent Skills 是这一转向的标准化层。

3. **三路径终局：MCP 赢协议层，CLI 赢 dev 工具，浏览器 Agent 赢长尾**——⚠ 解读。MCP 在结构化 SaaS（Atlassian / Notion / Stripe / Figma）已是事实标准。CLI 在 dev 圈不会被取代——cost / latency / reliability 三方面都最优。浏览器 Agent 是面向"永远不会主动出 MCP"的长尾网站的兜底（政府门户、小电商、遗留 ERP）；Operator / Manus / browser-use 三家分摊。

4. **反 Bot 经济学是 SaaS 商业模式重构的隐线**——Cloudflare default block + pay-per-crawl + AI Crawl Control 把"区分友 Agent / 恶 Agent"商品化 [[48]](https://blog.cloudflare.com/introducing-pay-per-crawl/) [[51]](https://blog.cloudflare.com/introducing-ai-crawl-control/)。⚠ **解读**：Cloudflare 在做的是把 HTTP 402 这个 1997 年规范但从没用起来的状态码激活成"每条请求 micropayment" 的基础设施；这层一旦立起来，SaaS 不再需要纠结 per-call vs per-seat，转移到"按 agent 调用 path 收钱"，反 Bot 系统从 cost center 变 revenue center。

5. **Pre-Agent 的"集成层"（iPaaS / Zapier / MuleSoft）被双面挤压**——上面被 MCP 商品化（L10b），下面被浏览器 Agent 兜底；中间 60–200K USD/年的集成项目利润空间被压缩。这条流向已在 L10b 验证，本层补充的是"**SaaS 不一定要做 MCP server——它也可以选择不做、被浏览器 Agent 当 GUI 用**"。这给传统集成赛道留了**短窗口**：在浏览器 Agent 可靠性达到 95% 之前（当前 OSWorld-Verified 78%）还有 12–24 个月的弹性。

## 信源

[1] GitHub Engineering, "GitHub CLI 1.0 is now available," *GitHub Blog*, Sep. 17, 2020. (Beta 期内 250K+ PR、350K+ merge、20K+ issues created via CLI.) [Online]. Available: <https://github.blog/2020-09-17-github-cli-1-0-is-now-available/>

[2] Stripe, "Introducing the Stripe CLI," *Stripe Blog*, Nov. 2019. [Online]. Available: <https://stripe.com/blog/stripe-cli>

[3] Charm, "The Next Generation of the Command Line," *Charm Blog*, 2025. (Bubble Tea 23k stars, 4000+ apps, 11,682 importing projects.) [Online]. Available: <https://charm.land/blog/the-next-generation/>

[4] Imperva, "2025 Imperva Bad Bot Report: How AI is Supercharging the Bot Threat," Apr. 2025. (Bad bot 37%, automated 51% of all web traffic.) [Online]. Available: <https://www.imperva.com/blog/2025-imperva-bad-bot-report-how-ai-is-supercharging-the-bot-threat/>

[5] Thales / Imperva, "AI Fuels Bots That Now Make up More Than Half of Global Internet Traffic," *BusinessWire*, Apr. 15, 2025. [Online]. Available: <https://www.businesswire.com/news/home/20250415432215/en/Artificial-Intelligence-Fuels-Rise-of-Hard-to-Detect-Bots-That-Now-Make-up-More-Than-Half-of-Global-Internet-Traffic-According-to-the-2025-Imperva-Bad-Bot-Report>

[6] Cloudflare, "The 2025 Cloudflare Radar Year in Review," *Cloudflare Blog*, Dec. 2025. (Bot 30% global traffic; AI crawler 4.2% HTML; non-AI bot 50% HTML requests.) [Online]. Available: <https://blog.cloudflare.com/radar-2025-year-in-review/>

[7] InfoQ, "Cloudflare Year in Review: AI Bots Crawl Aggressively," Dec. 2025. [Online]. Available: <https://www.infoq.com/news/2025/12/cloudflare-2025-ai-bots/>

[8] HUMAN Security, "Measuring the AI-Driven Internet — 2026 State of AI Traffic & Cyberthreat Benchmark Report," 2026. (Agentic AI 流量 +7851% YoY；2025 月度 +187%.) [Online]. Available: <https://www.humansecurity.com/learn/blog/ai-traffic-growth-2025-key-findings/>

[9] Cloud Security Alliance, "API Security in the AI Era: Best Practices for AI-Driven APIs," Sep. 9, 2025. (Hundreds/day → thousands/min AI workloads.) [Online]. Available: <https://cloudsecurityalliance.org/blog/2025/09/09/api-security-in-the-ai-era>

[10] Stripe, "Adding payments to your LLM agentic workflows," *Stripe Dot Dev Blog*, Nov. 2024. [Online]. Available: <https://stripe.dev/blog/adding-payments-to-your-agentic-workflows>

[11] The Letter Two, "Stripe Launches SDK for AI Agents to Enable Payments," Nov. 15, 2024. [Online]. Available: <https://thelettertwo.com/2024/11/15/stripe-releases-sdk-enabling-payment-and-billing-capabilities-for-ai-agents/>

[12] Vercel, "AI SDK 5," *Vercel Blog*, Jul. 31, 2025. [Online]. Available: <https://vercel.com/blog/ai-sdk-5>

[13] Vercel, "AI SDK 6," *Vercel Blog*, Oct. 2025. (ToolLoopAgent, needsApproval gate.) [Online]. Available: <https://vercel.com/blog/ai-sdk-6>

[14] InfoQ, "Vercel Ship AI 2025 Key Announcements," Oct. 2025. [Online]. Available: <https://www.infoq.com/news/2025/10/vercel-ship-ai/>

[15] Atlassian, "Introducing Atlassian's Remote Model Context Protocol (MCP) Server," May 1, 2025. [Online]. Available: <https://www.atlassian.com/blog/announcements/remote-mcp-server>

[16] Cloudflare, "Cloudflare Accelerates AI Agent Development With The Industry's First Remote MCP Server," *Press Release*, Apr. 7, 2025. [Online]. Available: <https://www.cloudflare.com/press/press-releases/2025/cloudflare-accelerates-ai-agent-development-remote-mcp/>

[17] Cloudflare, "Thirteen new MCP servers from Cloudflare you can use today," *Cloudflare Blog*, 2025. [Online]. Available: <https://blog.cloudflare.com/thirteen-new-mcp-servers-from-cloudflare/>

[18] Notion, "September 18, 2025 – Notion 3.0: Agents," 2025. [Online]. Available: <https://www.notion.com/releases/2025-09-18>

[19] Figma, "Introducing our Dev Mode MCP server: Bringing Figma into your workflow," *Figma Blog*, 2025. [Online]. Available: <https://www.figma.com/blog/introducing-figma-mcp-server/>

[20] Figma, "Agents, Meet the Figma Canvas," *Figma Blog*, 2025. [Online]. Available: <https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/>

[21] Reworked, "Slack's Real-Time Search API and MCP Server Are Now Live," Oct. 13, 2025. [Online]. Available: <https://www.reworked.co/digital-workplace/slacks-rts-api-and-mcp-server-hit-general-availability/>

[22] Digital Applied, "MCP Adoption Statistics 2026: Model Context Protocol," 2026. (Registry Q1 1200 → Q3 3400 → year-end 6800 → 2026-04 9400+；mcp.so 16,670.) [Online]. Available: <https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol>

[23] Anthropic, "Equipping agents for the real world with Agent Skills," *Anthropic Engineering*, Oct. 2025. [Online]. Available: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>

[24] The New Stack, "Agent Skills: Anthropic's Next Bid to Define AI Standards," Oct. 2025. [Online]. Available: <https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/>

[25] SiliconANGLE, "Anthropic makes agent Skills an open standard," Dec. 18, 2025. [Online]. Available: <https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/>

[26] S. Willison, "Claude Skills are awesome, maybe a bigger deal than MCP," *simonwillison.net*, Oct. 16, 2025. [Online]. Available: <https://simonwillison.net/2025/Oct/16/claude-skills/>

[27] Anthropic, "Introducing computer use, a new Claude 3.5 Sonnet, and Claude 3.5 Haiku," Oct. 22, 2024. (OSWorld screenshot-only 14.9% / 多步 22.0%.) [Online]. Available: <https://www.anthropic.com/news/3-5-models-and-computer-use>

[28] LLM Stats, "OSWorld-Verified Benchmark Leaderboard," 2026. (Claude Mythos Preview 79.6%, GPT-5.5 78.7%, Claude Opus 4.7 78.0%.) [Online]. Available: <https://llm-stats.com/benchmarks/osworld-verified>

[29] TechCrunch, "OpenAI may preview its agent tool for users on the $200-per-month Pro plan," Jan. 23, 2025. [Online]. Available: <https://techcrunch.com/2025/01/23/openais-agent-tool-will-be-available-to-users-paying-200-per-month-for-pro/>

[30] MIT Technology Review, "OpenAI launches Operator—an agent that can use a computer for you," Jan. 23, 2025. [Online]. Available: <https://www.technologyreview.com/2025/01/23/1110484/openai-launches-operator-an-agent-that-can-use-a-computer-for-you/>

[31] Upstarts Media, "Browserbase Raises $40M Series B, Launches AI Automation Tool," Apr. 2025. (估值 $300M.) [Online]. Available: <https://www.upstartsmedia.com/p/browserbase-raises-40m-and-launches-director>

[32] Built In SF, "Browserbase Secures $40M Series B Round," Jun. 18, 2025. (累计 $67.5M.) [Online]. Available: <https://www.builtinsf.com/articles/browserbase-announces-40m-series-b-funding-20250618>

[33] Browserbase, "Stagehand — The SDK for Browser Agents," *GitHub*, 2025. [Online]. Available: <https://github.com/browserbase/stagehand>

[34] TechCrunch, "Browser Use, the tool making it easier for AI 'agents' to navigate websites, raises $17M," Mar. 23, 2025. [Online]. Available: <https://techcrunch.com/2025/03/23/browser-use-the-tool-making-it-easier-for-ai-agents-to-navigate-websites-raises-17m/>

[35] Y Combinator, "Open Source Startups funded by Y Combinator," 2026. (browser-use "近 3 月获 40k stars".) [Online]. Available: <https://www.ycombinator.com/companies/industry/open-source>

[36] Skyvern, "We raised $2.7M to fix browser automation (open source)," 2025. [Online]. Available: <https://www.skyvern.com/blog/skyvern-we-raised-2-7m-to-fix-browser-automation-open-source/>

[37] Tracxn, "Skyvern — 2026 Company Profile," Jan. 31, 2026. (11 员工, 复杂 benchmark 85.8% 成功率.) [Online]. Available: <https://tracxn.com/d/companies/skyvern/__joZNwZnvPpp5SWng14qfKwxCqqwKRt699DxAC4T5pfI>

[38] TechCrunch, "Chinese AI startup Manus reportedly gets funding from Benchmark at $500M valuation," Apr. 25, 2025. [Online]. Available: <https://techcrunch.com/2025/04/25/chinese-ai-startup-manus-reportedly-gets-funding-from-benchmark-at-500m-valuation/>

[39] SiliconANGLE, "Chinese startup behind Manus reportedly raises $75M in funding," Apr. 25, 2025. [Online]. Available: <https://siliconangle.com/2025/04/25/chinese-startup-behind-manus-reportedly-raises-75m-funding/>

[40] CNBC, "Meta acquires intelligent agent firm Manus," Dec. 30, 2025. (Manus 年化营收 $100M+，run rate $125M+.) [Online]. Available: <https://www.cnbc.com/2025/12/30/meta-acquires-singapore-ai-agent-firm-manus-china-butterfly-effect-monicai.html>

[41] TechCrunch, "Meta just bought Manus, an AI startup everyone has been talking about," Dec. 29, 2025. [Online]. Available: <https://techcrunch.com/2025/12/29/meta-just-bought-manus-an-ai-startup-everyone-has-been-talking-about/>

[42] TechCrunch, "China vetoes Meta's $2B Manus deal after months-long probe," Apr. 27, 2026. [Online]. Available: <https://techcrunch.com/2026/04/27/china-vetoes-metas-2b-manus-deal-after-months-long-probe/>

[43] Bain & Company, "Will Agentic AI Disrupt SaaS? — Technology Report 2025," 2025. [Online]. Available: <https://www.bain.com/insights/will-agentic-ai-disrupt-saas-technology-report-2025/>

[44] Deloitte Insights, "SaaS meets AI agents: 2026 TMT Predictions," 2026. [Online]. Available: <https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/saas-ai-agents.html>

[45] Monetizely, "The Doomed Evolution of Salesforce's Agentforce Pricing," 2025. ($2/conversation 引发客户反弹.) [Online]. Available: <https://www.getmonetizely.com/blogs/the-doomed-evolution-of-salesforces-agentforce-pricing>

[46] Metronome, "State of Usage-Based Pricing 2025 Report," 2025. (78% UBP 公司过去 5 年内才上.) [Online]. Available: <https://metronome.com/state-of-usage-based-pricing-2025>

[47] MIT Technology Review, "Cloudflare will now block AI bots from crawling its clients' websites by default," Jul. 1, 2025. [Online]. Available: <https://www.technologyreview.com/2025/07/01/1119498/cloudflare-will-now-by-default-block-ai-bots-from-crawling-its-clients-websites/>

[48] Cloudflare, "Introducing pay per crawl: Enabling content owners to charge AI crawlers for access," *Cloudflare Blog*, 2025. (HTTP 402 + payment intent header.) [Online]. Available: <https://blog.cloudflare.com/introducing-pay-per-crawl/>

[49] Model Context Protocol, "SEP-1649 server-card .well-known discovery," *GitHub Issue*, 2025. [Online]. Available: <https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649>

[50] Cloudflare, "Build and deploy Remote Model Context Protocol (MCP) servers to Cloudflare," *Cloudflare Blog*, Apr. 2025. [Online]. Available: <https://blog.cloudflare.com/remote-model-context-protocol-servers-mcp/>

[51] Cloudflare, "The next step for content creators in working with AI bots: Introducing AI Crawl Control," *Cloudflare Blog*, 2025. [Online]. Available: <https://blog.cloudflare.com/introducing-ai-crawl-control/>
