# 2026-05-14：SDLC 栈 / 文档与 IDP (M1) 层深度研究

文档（M1）与内部开发者平台（M3，IDP）在 2024 年以前都被归类为"开发者体验"的卫星问题——文档归技术写作者管，IDP 归平台工程小队管，预算来自"DevEx 满意度"。到 2026 年中，这两层都发生了**本体论级别的转换**：docs 与 service catalog 不再是"被读对象"，而是变成 **Agent 的工具集**——通过 MCP 端点被 LLM 主动调用、检索、甚至修改。这与 L01（搜索 / 入口层）"读者从人变成 Agent"的流量级转换同源，但 L12 多一层 L01 没有的东西：**docs / catalog 自身就是工具，不只是被读的内容**。

理解这一层错位最干净的视角是一个复合变量：**agent-consumable context fidelity = (catalog 数据真实性 × docs 与代码同步延迟 × machine-readable artifact 覆盖率 × MCP endpoint 可达性)**。四个因子任一接近 0，Agent 就会生成错代码、调错服务、踩错 owner，整条 Coding Agent 流水线被这一层掐死。

## 1. 旧痛点压缩：为什么 L12 的本质不是"流量"

Pre-Agent 时代 docs / IDP 有四个老痛点：(a) **文档滞后于代码**——PR 作者绝大多数不会同步更新 docs（⚠ 解读：估算值，缺乏公开 benchmark；依据是 Swimm 等厂商把"docs lag code"列为产品立项的核心痛点 [[1]](https://swimm.io/blog/sync-dont-sink-why-we-built-swimm-for-dev-teams)），Swimm 自 2019 年起即以"code-coupled docs"切入这一问题 [[1]](https://swimm.io/blog/sync-dont-sink-why-we-built-swimm-for-dev-teams), [[27]](https://techcrunch.com/2021/11/08/swimm-nabs-27-6m-series-a-to-include-up-to-date-documentation-in-every-release/)；(b) **no one reads it**，Confluence / Notion 搜索体验差；(c) **service catalog 维护成本**，Backstage `catalog-info.yaml` 必须人工维护、owner 字段过时是常态 [[2]](https://backstage.io/docs/features/software-catalog/descriptor-format/)；(d) **DevEx 难量化**，DORA 四指标 [[28]](https://dora.dev/guides/dora-metrics-four-keys/) 覆盖交付效能，却对"工具是否真的被用"沉默（⚠ 解读）。

L01（搜索 / 入口）的转换是**流量级的**：Agent 接管检索后，Google / Stack Overflow 的人类点击下降，docs 站点的访问被 LLM 后台调用替代——这是"读者切换"叙事的核心。但 L12 不仅仅如此。**L01 的资产形态没有变**——网页仍然是网页，只不过被另一种读者抓。L12 的资产形态本身在变：

- Mintlify 的 docs 站点同时是 **MCP server**——Agent 不"打开"它，而是"调用"它 [[11]](https://www.mintlify.com/docs/ai/model-context-protocol)。
- Backstage RFC #33575 提议把 docs / rules / skills 升级为 Catalog 里的 **`AIContext` 实体**——它不是给人看的页面，而是给 Agent 取用的结构化对象 [[17]](https://github.com/backstage/backstage/issues/33575)。
- Roadie 的 Decorator 允许 LLM **反向修改** Catalog entity [[18]](https://roadie.io/blog/ai-cometh/)——这已经不是"读"，是"写"。

L01 是"同一份网页被换了读者"，L12 是"同一份知识被换了存在形式"——从 page 变成 tool，从 document 变成 endpoint。这是为什么"读者切换"虽然方向对，但太浅：它只描述了表层现象，没有触及 docs / catalog 作为 agent tool 的本体论转换。本报告以下四节即围绕这一转换展开。

## 2. 从"被读"到"被调用"：docs / catalog 作为 agent tool 的本体论转换

Coding Agent（Cursor、Claude Code、Windsurf、Copilot Workspace、Devin）在 2025 年下半年完成了一件关键事：**在每次生成代码之前主动检索 docs / catalog**，并把命中片段塞进 prompt。Mintlify 把这一现实总结为一句话：*Documentation is your AI interface* [[3]](https://www.mintlify.com/blog/docs-as-ai-interface)。但更精确的表述是：documentation **becomes** an AI tool——它不再被打开，而是被注册到 Agent 的工具栏。

这一转换体现为四个新硬性约束：

- **MCP-accessible**：Agent 通过 Model Context Protocol 直接 query，docs 站点必须暴露 MCP endpoint；
- **Machine-readable**：除 HTML 渲染外提供干净 Markdown，同 URL 通过 `Accept: text/markdown` 谈判返回 `.md`；
- **与代码强同步**：Agent 拿到的不能是六个月前的旧示例；
- **包含可复制 example**：Agent 倾向于 copy 而非 reason，working snippet 命中率显著高于纯散文（⚠ 解读：业内共识，无单一权威 benchmark）。

`llms.txt` 规范由 Jeremy Howard（Answer.AI）于 2024 年 9 月提出，一份放在站点根目录的 Markdown 索引文件 [[5]](https://llmstxt.org/)：

```
# Project Name
> 一句话项目摘要

## Docs
- [Quick Start](https://...): 入门指南
- [API Reference](https://...): 完整 API

## Optional
- [Changelog](https://...): 可选，上下文紧时可跳过
```

配套 `llms-full.txt` 把全站正文拼成长 Markdown，方便整段塞进上下文窗口。Anthropic 自家 docs 同时提供 `llms.txt`（约 8.4K tokens）与 `llms-full.txt`（约 48 万 tokens）[[6]](https://searchengineland.com/llms-txt-proposed-standard-453676)。BuiltWith 截至 2025 年 10 月统计已有 **84.4 万站点** 部署 `llms.txt`，但同样存在批评："没有一家主流 LLM 厂商公开声明会读这个文件" [[7]](https://medium.com/@kaispriestersbach/the-llms-txt-is-dead-more-precisely-a-dud-ab7bee4f469c)。

⚠ 解读：`llms.txt` 是 docs 工具化的**弱形式**（静态、只读、爬虫消费），MCP server 是**强形式**（stateful、可执行、session 内被反复调用）。两个机制并行冗余，但 MCP 的赢面更大——它就是工具，`llms.txt` 顶多算工具的产品说明书。

DORA 2025 数据印证了 Agent 作为新"重度调用者"的事实：使用 AI 的开发者每天接触的 PR 上下文增加 **67.4%**，任务上下文增加 17.7%，但 PR 评审中位时间暴涨 **441%**、31% 的 PR 在无人 review 下被 merge [[4]](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025)。人不读，Agent 在读——确切说是在调。

## 3. 保鲜战争：Autopilot / Magellan / Decorator 谁先免维护

一旦 docs / catalog 成为 Agent 工具，**数据新鲜度**就从"维护卫生问题"升级为"产品核心 SLO"。腐烂的 catalog 让 Agent 调错服务，过期的 docs 让 Agent 写错 API call。围绕"让 fidelity 自动保持"，三条产品路线开打：

**Mintlify Autopilot Agent**：监听 codebase，每次 ship 自动起 PR 更新 docs，并从 merge 进来的 PR 草拟 changelog [[8]](https://www.mintlify.com/blog/autopilot)。Autopilot 仅在 **$300/月起** 的 Pro 与企业版开放 [[9]](https://ferndesk.com/blog/mintlify-pricing)。配套自动生成 `llms.txt` / `llms-full.txt` / `skill.md`，每个站点开箱自带 [[10]](https://www.mintlify.com/docs/ai/llmstxt)；同一 URL 通过 content negotiation 返回干净 Markdown；每个 docs 站点自动开 MCP server，Claude / Cursor / Windsurf / ChatGPT 一键 add server [[11]](https://www.mintlify.com/docs/ai/model-context-protocol)。买家也随之位移：技术写作者只是文档编辑者，决定要不要付 $300/月 的是**平台工程团队**——他们要的是 Agent 能否拿到正确的 SDK 示例 [[12]](https://ferndesk.com/blog/mintlify-review)。

**Cortex Magellan**：自家 AI 引擎，负责自动 catalog import、ownership 发现、discovery audit。2026 年初 Cortex 把自己从 IDP 重塑为 **EngOps 平台** [[20]](https://www.cortex.io/post/the-business-case-for-internal-developer-portals-in-2026)。

**Roadie Decorator**：2025 末上线 6 个 MCP servers 覆盖 Backstage catalog、scaffolder、tech docs，beta 中允许 Decorator 通过 LLM **反向修改** Catalog entity [[18]](https://roadie.io/blog/ai-cometh/)——这是把"保鲜"从外部任务变成 catalog 自身的一项工具能力。

**Swimm /ask** 走的是另一条互补路线：放弃漂亮公开门户，专吃**内部代码库文档**。文档块通过 snippet ID 绑定到具体函数，重构改名时 doc 自动标记 stale，CI 卡 PR；2026 年把 `/ask Swimm` 上线为 contextual AI coding assistant，索引 codebase 生成 "Generate Documents"，再用 auto-sync 维护新鲜度 [[13]](https://swimm.io/blog/meetask-swimm-your-teams-contextual-ai-coding-assistant)。

⚠ 解读：这场保鲜战争的赢家不是"docs 更漂亮"或"catalog 更全"的一方，而是"在 fidelity 公式四个因子上同时把维护成本压到 0"的一方。Mintlify 在 docs 同步上领先，Roadie / Cortex 在 catalog 自更新上领先；中期看会出现"docs 厂商往 catalog 扩、catalog 厂商往 docs 扩"的相向挤压。

## 4. MCP 分发位争夺：Mintlify vs Backstage vs Cortex 的渠道战

Agent 的 IDE / chat 客户端里能挂的 MCP server 数量有限——单个项目通常不超过 10–20 个 active server（⚠ 解读：基于 Claude Code / Cursor / Windsurf 默认 UI 与 token budget 的工程常识，无公开统计）。谁先占住这个 slot，谁就是 Agent 工作流的默认入口。

**Mintlify 路线**：每个 docs 站点自动是一个 MCP server [[11]](https://www.mintlify.com/docs/ai/model-context-protocol)。这是 per-product 分发——开发者在用 Stripe 时挂 Stripe docs MCP，用 Vercel 时挂 Vercel docs MCP。Mintlify 把渠道押在"每个 SaaS 都用 Mintlify 做 docs"，是 horizontal play。

**Backstage 路线**：Spotify 在官方 Portal 上线 **MCP Actions Backend**，把每个 Backstage 插件的能力注册到 Actions Registry 并聚合成**一个** MCP server endpoint [[16]](https://backstage.spotify.com/docs/portal/core-features-and-plugins/mcp/)。AiKA、Claude Code、Cursor、VS Code Copilot 通过同一组 MCP tool 访问 catalog。这是 per-org 分发——一个公司挂一个 Backstage MCP，覆盖该公司所有服务。RFC #33575 进一步提议把 docs / rules / skills 升级为 Catalog 里的 `AIContext` 实体 [[17]](https://github.com/backstage/backstage/issues/33575)，把"docs as tool"内化为 Catalog schema 的一部分。

**Cortex / OpsLevel / Roadie 路线**：托管 IDP 阵营的 MCP 都是聚合型——Cortex 把 Catalog、Scorecards、组织知识全部通过 MCP 暴露 [[20]](https://www.cortex.io/post/the-business-case-for-internal-developer-portals-in-2026)；OpsLevel MCP Server 让 Copilot / Cursor / Claude 直接查 catalog，明确指出 "AI assistant 的效果上限就是 IDP 数据质量" [[21]](https://www.opslevel.com/resources/opslevels-new-mcp-server-powers-your-ai-assistant-with-real-time-context)；Roadie 把 MCP + AI Search 列为 2026 主线 [[18]](https://roadie.io/blog/ai-cometh/)。

**Fern**：API spec → SDK + docs + `llms.txt` 一体化生成，machine-readable artifact 是默认输出 [[14]](https://buildwithfern.com/learn/docs/ai-features/llms-txt)。Postman 在 2026 年 1 月**收购 Fern**，标志 API 平台正式把"AI 可消费的 docs"纳入护城河 [[15]](https://www.infoworld.com/article/4115502/postman-snaps-up-fern-to-reduce-developer-friction-around-api-documentation-and-sdks.html)。**ReadMe** Owlbert 支持 `llms.txt` 与 MCP 生成；**Stoplight** 几乎缺席这一轮 AI 化，无公开 Agent 或 MCP 能力——这是它从竞争对照中掉队的直接原因。

⚠ 解读：MCP slot 争夺的最终格局大概率是 **per-product (Mintlify) + per-org (Backstage / Cortex) 共存**——开发者会同时挂"我用的 SaaS docs MCP"和"我公司 catalog MCP"。Port 喊出"Backstage is dead"主张未来 IDP 必须是 **Agentic Engineering Platform**——人、Agent、基础设施共享同一控制面 [[19]](https://www.port.io/blog/backstage-is-dead)；Humanitec Platform Orchestrator 把核心问题重新表述为"当 Agent 在你的基础设施上操作，会发生什么？"——guardrail、policy、回滚要先于 Agent 行动 [[23]](https://humanitec.com/products/platform-orchestrator)。这两家代表的是"MCP slot 之外还要有 policy plane"的下一步竞争。

## 5. Scorecard SKU 重构与 DevEx telemetry

Scorecard 在 Pre-Agent 时代考核"服务健康"——SLO、test coverage、on-call hygiene。Post-Agent 时代它考核**服务对 Agent 友好程度**：是否暴露 OpenAPI、是否有 MCP endpoint、docs 是否 machine-readable、ownership 数据是否新鲜。这是 IDP 这一代的 SKU 转折——Cortex 直接把 "AI readiness" 列为新一类 scorecard 指标 [[20]](https://www.cortex.io/post/the-business-case-for-internal-developer-portals-in-2026)。

对应到 DevEx 度量：DORA 2025 报告引入显式的 *AI measurement layer*，建议跟踪 *AI-assisted / AI-generated 在 merged code 中的占比* [[4]](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025)。DX、GetDX、Faros 等厂商把 **Agent 接受率（acceptance rate）**、**Agent 启动到 merge 的中位时长**、**被 Agent 触发的 PR 比例** 列为新指标 [[24]](https://getdx.com/blog/dora-metrics-tools/)。InfoQ 援引 DORA 2026 报告："AI 是放大器，回报来自组织系统而非工具本身"——没有底层（catalog、文档、guardrail）的团队会出现"AI 局部高产出 + 下游混乱"的悖论 [[25]](https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/)。

产品形态变化：IDP 自身必须有 **Agent UI**——开发者在 Cursor 或 Claude Code 里直接调起 self-service action，而不是去 IDP 网页点按钮。Backstage AI Gateway [[26]](https://backstage.spotify.com/docs/portal/core-features-and-plugins/ai-gateway/)、Cortex Magellan、Roadie AI Search 都在这个方向走。Port 自称从 IDP 进化为 *Agentic Engineering Platform*，主张未来软件交付由"人 + Agent + 基础设施"三方共同操作同一组 self-service action [[22]](https://www.port.io/blog/port-agentic-engineering-platform)。

公开 acceptance rate 区间：GitHub Copilot 约 **30–38%**，Cursor / Supermaven inline autocomplete 报告值可达 **42–72%** [[29]](https://www.secondtalent.com/resources/github-copilot-statistics/)。这些数字进入 IDP scorecard 后，会取代"开发者满意度 8.2 分"成为平台工程团队的新 KPI——但只在 fidelity 公式四个因子达标的组织里有意义。⚠ 解读：在 catalog 烂、docs 旧、MCP 没接的组织里，高 acceptance rate 反而是危险信号——Agent 接受得很爽，merge 进去的代码却基于错误上下文。

## 6. 本质判断

第一，**L12 的本质是 docs / catalog 从 page 变成 tool**——这是比 L01"读者切换"更深的一层转换，资产形态本身在变，不只是流量方向在变。

第二，**agent-consumable context fidelity 四因子任一接近 0，整条 Coding Agent 流水线被掐死**——这是为什么 $300/月 的 Mintlify Pro 卖得动、为什么 Postman 砸钱收购 Fern、为什么 Backstage 要发明 `AIContext` 实体。

第三，**MCP slot 的分发位决定渠道格局**：per-product (Mintlify) 与 per-org (Backstage / Cortex) 共存，Stoplight 这种没下注的厂商会被结构性边缘化。

第四，**scorecard 从"考核服务健康"升级为"考核服务对 Agent 友好程度"**，DevEx 度量从主观问卷过渡到 Agent telemetry。但在底层数据 fidelity 不达标的组织里，telemetry 高分反而是误导。

第五，**`llms.txt` 与 docs MCP 是冗余共存**——前者是工具说明书，后者是工具本体；必须押一边时 MCP 的赢面更大，因为它是 stateful、可执行、被注册到 Agent 工具栏的那一项。

## 参考文献

[1] O. Rosenbaum, "Sync don't sink: why we built Swimm for dev teams," *Swimm Blog*, 2021. (Swimm 立项动机：让 docs 与代码同步。) [Online]. Available: <https://swimm.io/blog/sync-dont-sink-why-we-built-swimm-for-dev-teams>

[2] Backstage, "Descriptor Format of Catalog Entities," *backstage.io docs*, 2026. [Online]. Available: <https://backstage.io/docs/features/software-catalog/descriptor-format/>

[3] H. Wang, "Documentation is your AI interface," *Mintlify Blog*, 2026. [Online]. Available: <https://www.mintlify.com/blog/docs-as-ai-interface>

[4] Faros AI, "DORA Report 2025 Key Takeaways: AI Impact on Dev Metrics," 2025. (中位 PR review 时间同比 +441%，31% PR 无人 review merge；AI 用户日均接触 +67.4% PR 上下文。) [Online]. Available: <https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025>

[5] J. Howard, "The /llms.txt file," *llmstxt.org*, Sep. 2024. [Online]. Available: <https://llmstxt.org/>

[6] B. Schwartz, "Meet llms.txt, a proposed standard for AI website content crawling," *Search Engine Land*, 2025. (Anthropic 站点 `llms.txt` 约 8.4K tokens，`llms-full.txt` 约 481K tokens。) [Online]. Available: <https://searchengineland.com/llms-txt-proposed-standard-453676>

[7] K. Spriestersbach, "The llms.txt is dead. More precisely: a dud," *Medium*, 2025. [Online]. Available: <https://medium.com/@kaispriestersbach/the-llms-txt-is-dead-more-precisely-a-dud-ab7bee4f469c>

[8] Mintlify, "Introducing the next step towards self-updating docs," 2026. [Online]. Available: <https://www.mintlify.com/blog/autopilot>

[9] Ferndesk, "Mintlify Pricing 2026," 2026. (Autopilot 仅 Pro $300/月起开放。) [Online]. Available: <https://ferndesk.com/blog/mintlify-pricing>

[10] Mintlify, "llms.txt — Mintlify Docs," 2026. [Online]. Available: <https://www.mintlify.com/docs/ai/llmstxt>

[11] Mintlify, "Model Context Protocol (MCP)," 2026. [Online]. Available: <https://www.mintlify.com/docs/ai/model-context-protocol>

[12] Ferndesk, "Mintlify Review 2026: Features, AI Agent, and Is It Worth $300/Month?" 2026. [Online]. Available: <https://ferndesk.com/blog/mintlify-review>

[13] Swimm, "Meet /ask Swimm: Your team's contextual AI coding assistant," 2026. [Online]. Available: <https://swimm.io/blog/meetask-swimm-your-teams-contextual-ai-coding-assistant>

[14] Fern, "llms.txt and llms-full.txt," *Fern Documentation*, 2026. [Online]. Available: <https://buildwithfern.com/learn/docs/ai-features/llms-txt>

[15] P. Krill, "Postman snaps up Fern to reduce developer friction around API documentation and SDKs," *InfoWorld*, Jan. 2026. [Online]. Available: <https://www.infoworld.com/article/4115502/postman-snaps-up-fern-to-reduce-developer-friction-around-api-documentation-and-sdks.html>

[16] Spotify, "MCP — Spotify Plugins for Backstage Developer Documentation," 2026. [Online]. Available: <https://backstage.spotify.com/docs/portal/core-features-and-plugins/mcp/>

[17] Backstage maintainers, "RFC: Introduce a new `AIContext` `kind` in the Software Catalog," GitHub Issue #33575, 2026. [Online]. Available: <https://github.com/backstage/backstage/issues/33575>

[18] Roadie, "MCP Servers for Roadie, AI Search enters beta...", 2025. [Online]. Available: <https://roadie.io/blog/ai-cometh/>

[19] Z. Einy, "Backstage is dead," *Port Blog / Autonomous Engineering Newsletter*, 2026. [Online]. Available: <https://www.port.io/blog/backstage-is-dead>

[20] Cortex, "The Business Case for Internal Developer Portals in 2026," 2026. (Cortex 重新定位为 EngOps 平台。) [Online]. Available: <https://www.cortex.io/post/the-business-case-for-internal-developer-portals-in-2026>

[21] OpsLevel, "OpsLevel's new MCP Server powers your AI Assistant with real-time context," 2025. [Online]. Available: <https://www.opslevel.com/resources/opslevels-new-mcp-server-powers-your-ai-assistant-with-real-time-context>

[22] Port, "Agentic engineering platform: The evolution of internal developer portals," *Port Blog*, 2026. [Online]. Available: <https://www.port.io/blog/port-agentic-engineering-platform>

[23] Humanitec, "Platform Orchestrator," 2026. [Online]. Available: <https://humanitec.com/products/platform-orchestrator>

[24] GetDX, "DORA metrics tools in 2026: What to measure, and what's missing," 2026. [Online]. Available: <https://getdx.com/blog/dora-metrics-tools/>

[25] InfoQ, "New DORA Report Claims Strong Engineering Foundations Drive AI Return on Investment," May 2026. [Online]. Available: <https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/>

[26] Spotify, "AI Gateway — Spotify Plugins for Backstage," 2026. [Online]. Available: <https://backstage.spotify.com/docs/portal/core-features-and-plugins/ai-gateway/>

[27] R. Miller, "Swimm nabs $27.6M Series A to include up-to-date documentation throughout coding process," *TechCrunch*, Nov. 2021. (Swimm 创立于 2019 年，定位 code-coupled docs。) [Online]. Available: <https://techcrunch.com/2021/11/08/swimm-nabs-27-6m-series-a-to-include-up-to-date-documentation-in-every-release/>

[28] DORA, "DORA's software delivery metrics: the four keys," *dora.dev*, 2024. (部署频率、变更前置时间、变更失败率、服务恢复时间。) [Online]. Available: <https://dora.dev/guides/dora-metrics-four-keys/>

[29] Second Talent, "GitHub Copilot Statistics & Adoption Trends [2026]," 2026. (Copilot acceptance rate 约 30–38%；Cursor/Supermaven inline autocomplete 报告值 42–72%。) [Online]. Available: <https://www.secondtalent.com/resources/github-copilot-statistics/>
