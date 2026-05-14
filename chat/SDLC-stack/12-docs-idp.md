# 2026-05-14：SDLC 栈 / 文档与 IDP 层深度研究

软件开发栈在 Coding Agent 普及之后发生的最隐蔽却最具结构性的迁移，发生在两个看似最不性感的层：**文档（M1）** 与 **内部开发者平台（M3，IDP）**。在 2024 年以前，两者都被归类为"开发者体验"的卫星问题——文档归技术写作者管，IDP 归平台工程小队管，预算来自"DevEx 满意度"。到 2026 年中，这两层都被重新定义为 **Agent 上下文供给基础设施（context plane for agents）**：文档变成 LLM 在生成代码前查询的事实库，service catalog 变成 Agent 调度的知识图谱。买家、衡量指标、产品形态全部位移。

本报告解剖 M1/M3 在 Pre-Coding-Agent 与 Post-Coding-Agent 两个时代的差别，并以 namespace.so 式的"挖本质"视角追问：**文档与 IDP 这两件事的根本读者到底变成了谁？**

## 1. Pre-Agent 时代：文档与 IDP 的四个老痛点

第一个痛点是**文档总是滞后于代码**。手写 Markdown 与代码同处一个仓库时，PR 作者绝大多数不会同步更新 docs（⚠ 解读：估算值，缺乏公开 benchmark；依据是 Swimm 等厂商把"docs lag code"列为产品立项的核心痛点 [[1]](https://swimm.io/blog/sync-dont-sink-why-we-built-swimm-for-dev-teams)）；docs 站点（Confluence / Notion / GitBook）甚至和代码不在一个 repo，更新成本接近写一篇新文。Swimm 自 2019 年成立起即以"code-coupled docs"切入这个痛点的核心定义：文档应当与具体代码 snippet 强绑定，snippet 一旦漂移，文档自动失效 [[1]](https://swimm.io/blog/sync-dont-sink-why-we-built-swimm-for-dev-teams), [[27]](https://techcrunch.com/2021/11/08/swimm-nabs-27-6m-series-a-to-include-up-to-date-documentation-in-every-release/)。

第二个痛点是 **no one reads it**。文档站点的内部搜索体验普遍糟糕（Confluence 的全文搜索曾被开发者公开调侃），开发者宁可问同事或跑去读源码，也不愿打开 Wiki。这是 2010 年代后期 Mintlify、Fern、ReadMe 共同押注"漂亮的开发者门户 + better search"的市场前提。

第三个痛点是 **service catalog 维护成本**。Backstage 自 2020 年开源后席卷大厂，但其 `catalog-info.yaml` 元数据必须由人工或脚本维护，owner 字段过时、依赖关系腐烂是常态 [[2]](https://backstage.io/docs/features/software-catalog/descriptor-format/)。Cortex、OpsLevel、Roadie 等托管 IDP 出现的商业理由，部分就是替企业承担"让 catalog 不烂"的运营负担。

第四个痛点是 **DevEx 难量化**。"开发者体验"长期靠每年一次的 SPACE / DevEx 问卷估算，缺乏在产品里的连续信号。DORA 四指标（部署频率、变更前置时间、变更失败率、恢复时间）[[28]](https://dora.dev/guides/dora-metrics-four-keys/) 解决了交付效能的量化，但对"工具是否真的被用"几乎沉默（⚠ 解读）。

## 2. Post-Agent 时代的根本变化：文档的主要读者不再是人

Coding Agent（Cursor、Claude Code、Windsurf、Copilot Workspace、Devin 等）在 2025 年下半年完成了一件关键事：在每次生成代码之前，它们会**先检索文档**，把命中片段塞进 prompt 上下文。Mintlify 在年度复盘里把这一现实总结为一句话：*Documentation is your AI interface* [[3]](https://www.mintlify.com/blog/docs-as-ai-interface)。这意味着 docs 必须满足四个新硬性约束：

- **MCP-accessible**：Agent 可以通过 Model Context Protocol 直接 query；
- **Machine-readable**：除 HTML 渲染外，提供干净 Markdown（content negotiation 返回 `.md`）；
- **与代码强同步**：Agent 拿到的不能是六个月前的旧示例；
- **包含可复制的 example**：Agent 倾向于 copy 而不是 reason，提供 working snippet 命中率显著高于纯散文。

DORA 2025 报告也在数据上印证：使用 AI 的开发者每天接触的 PR 上下文增加 67.4%，任务上下文增加 17.7%，但 PR 评审中位时间却暴涨 441%、31% 的 PR 在无人 review 的情况下被 merge [[4]](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025)。Agent 成为新的"重度读者"，传统给人看的文档形态与速率都跟不上。

## 3. llms.txt / llms-full.txt 规范的兴起

Jeremy Howard（Answer.AI）于 2024 年 9 月提出 [`llms.txt` 规范](https://llmstxt.org/)：一份放在站点根目录的 Markdown 索引文件，给 LLM 一份"网站精华地图"[[5]](https://llmstxt.org/)。骨架很简单：

```
# Project Name
> 一句话项目摘要

## Docs
- [Quick Start](https://...): 入门指南
- [API Reference](https://...): 完整 API

## Optional
- [Changelog](https://...): 可选，上下文紧时可跳过
```

配套的 `llms-full.txt` 把全站正文直接拼成一个长 Markdown，方便整段塞进上下文窗口。Anthropic 自家 docs 站点同时提供 `llms.txt`（约 8.4K tokens）与 `llms-full.txt`（约 48 万 tokens），覆盖整个 API 文档 [[6]](https://searchengineland.com/llms-txt-proposed-standard-453676)。BuiltWith 截至 2025 年 10 月统计已有 84.4 万站点部署 `llms.txt`，但同样有批评认为"没有一家主流 LLM 厂商公开声明会读这个文件"，更多是 SEO 心理安慰 [[7]](https://medium.com/@kaispriestersbach/the-llms-txt-is-dead-more-precisely-a-dud-ab7bee4f469c)。真正决定它命运的不是 spec 本身，而是 **MCP server 是否成为标配**——只要每家 SaaS 都暴露一个 docs MCP，Agent 不需要爬 `llms.txt` 也能查到。两个机制并行，互为冗余。

## 4. Mintlify 怎么吃这一波

Mintlify 是当下"AI-native docs"叙事的最大赢家。它在 2025–2026 把产品形态彻底重写为四件套：

1. **Autopilot Agent**：监听 codebase，每次 ship 自动起 PR 更新 docs，并从 merge 进来的 PR 草拟 changelog [[8]](https://www.mintlify.com/blog/autopilot)。Autopilot 仅在 $300/月起的 Pro 与企业版开放 [[9]](https://ferndesk.com/blog/mintlify-pricing)。
2. **自动生成 llms.txt / llms-full.txt / skill.md**：每个 Mintlify 站点开箱自带，零维护 [[10]](https://www.mintlify.com/docs/ai/llmstxt)。
3. **Content negotiation 输出干净 Markdown**：同一 URL 加 `Accept: text/markdown` 返回去样式的 Markdown，给 Agent 解析远比 HTML 稳。
4. **自动托管 MCP server**：每个 docs 站点自动开 MCP 端点，Claude / Cursor / Windsurf / ChatGPT 可以一键 add server，在任务期间 query 实时文档 [[11]](https://www.mintlify.com/docs/ai/model-context-protocol)。

这是把 docs 站点从"网页"重新定义为"**Agent API**"。买家也随之位移：技术写作者只是文档编辑者，真正决定要不要付 $300/月的是**平台工程团队**——他们需要的是 Agent 能否在生成代码时拿到正确的 SDK 示例。Mintlify 自己把这套定位明确为"AI interface"，市场反馈把 Mintlify Review 2026 列为 buyer persona 由 tech writer 转向 platform / AI ops 的标志案例 [[12]](https://ferndesk.com/blog/mintlify-review)。

## 5. Swimm、Fern、ReadMe、Stoplight 的差异化

**Swimm** 的护城河仍是 *code-coupled doc*：文档块通过 snippet ID 绑定到具体函数，重构改名时 doc 自动标记 stale，CI 卡 PR。2026 年它把 `/ask Swimm` 上线为"contextual AI coding assistant"，索引 codebase 后生成"Generate Documents"，描述跨文件流程，再用 auto-sync 维护新鲜度 [[13]](https://swimm.io/blog/meetask-swimm-your-teams-contextual-ai-coding-assistant)。Swimm 的取舍是放弃漂亮的公开门户、专吃**内部代码库文档**这一块——这是 Mintlify 的弱区。

**Fern** 走 API spec → SDK + docs + `llms.txt` 一体化生成路线，machine-readable artifact 是默认输出 [[14]](https://buildwithfern.com/learn/docs/ai-features/llms-txt)。Postman 在 2026 年 1 月收购 Fern，标志着 API 平台正式把"AI 可消费的 docs"纳入护城河 [[15]](https://www.infoworld.com/article/4115502/postman-snaps-up-fern-to-reduce-developer-friction-around-api-documentation-and-sdks.html)。

**ReadMe** 推出 Agent Owlbert：风格 lint、文档审计、Ask AI 搜索，并支持 `llms.txt` 与 MCP server 生成。**Stoplight** 几乎缺席这一轮 AI 化，目前没有公开的 Agent 或 MCP 能力——这是它从竞争对照中掉队的直接原因。

## 6. Backstage 在 Agent 时代的二次发明

Backstage 的核心资产 Software Catalog 是 YAML 维护的"组织级软件实体图"——components、systems、APIs、owners、dependencies 都是节点 [[2]](https://backstage.io/docs/features/software-catalog/descriptor-format/)。2025 年以前，它的消费者是人类开发者打开 Backstage 网页"找服务"。2026 年的关键转向是：**Catalog 的主要消费者变成 Agent**。

具体表现：

- Spotify 在官方 Portal 上线 **MCP Actions Backend**，把每个 Backstage 插件的能力注册到 Actions Registry 并聚合成一个 MCP server endpoint。AiKA（Spotify 自家 AI 助手）、Claude Code、Cursor、VS Code Copilot 都通过同一组 MCP tool 访问 catalog [[16]](https://backstage.spotify.com/docs/portal/core-features-and-plugins/mcp/)。
- Backstage 仓库出现 RFC #33575：**新增 `AIContext` 实体类型**到 Software Catalog，专门描述"AI 编码工具消费的上下文"，第一批 scope 是 rules 与 skills [[17]](https://github.com/backstage/backstage/issues/33575)。这是 Catalog 模型自身在为 Agent 重新设计 schema。
- Roadie 在 2025 末上线 6 个 MCP servers 覆盖 Backstage catalog、scaffolder、tech docs，并可让 Decorator 通过 LLM 反向修改 Catalog entity [[18]](https://roadie.io/blog/ai-cometh/)。

底层语义变化是：service catalog 不再是"门户网站"，而是 **Agent 的 knowledge graph**——"这个服务的 owner 是谁、跑在哪、健康分多少、调用规范是什么"，这些问题以前由 SRE 在 Slack 回答，现在由 MCP 工具直接喂给 Agent。Port 的标题更激进："Backstage is dead"，主张未来的 IDP 必须是 **Agentic Engineering Platform**——人、Agent、基础设施共享同一控制面 [[19]](https://www.port.io/blog/backstage-is-dead)。

## 7. Cortex / Roadie / OpsLevel：scorecards 变成 Agent 入口

托管 IDP 阵营的 AI 化路径出奇一致：

- **Cortex** 把 Catalog、Scorecards、组织知识全部通过 MCP 暴露，开发者可在 ChatGPT 或任何 MCP client 问"这个服务的 owner、依赖、production-readiness 分"；自家 AI 引擎 Magellan 负责自动 catalog import、ownership 发现、discovery audit。2026 年初 Cortex 发布"Engineering Operations Manifesto"，把自己从 IDP 重塑为 **EngOps 平台**，覆盖 platform engineering、SRE、DevEx、security [[20]](https://www.cortex.io/post/the-business-case-for-internal-developer-portals-in-2026)。Scorecard 的新一类指标是 "AI readiness"——服务是否具备 MCP 接入、文档是否 machine-readable、是否暴露 OpenAPI。
- **OpsLevel** 推出 MCP Server，让 Copilot、Cursor、Claude 直接查 catalog；并明确指出 "AI assistant 的效果上限就是 IDP 数据质量" [[21]](https://www.opslevel.com/resources/opslevels-new-mcp-server-powers-your-ai-assistant-with-real-time-context)。
- **Roadie** 把 MCP + AI Search 列为 2026 主线，beta 中允许 Decorator 通过 LLM 修改 Catalog [[18]](https://roadie.io/blog/ai-cometh/)。
- **Port** 自称从 IDP 进化为 *Agentic Engineering Platform*，主张未来软件交付由"人 + Agent + 基础设施"三方共同操作同一组 self-service action [[22]](https://www.port.io/blog/port-agentic-engineering-platform)。
- **Humanitec** 的 Platform Orchestrator 把核心问题重新表述为："当 Agent 在你的基础设施上操作，会发生什么？"——即 guardrail、policy、回滚要先于 Agent 行动 [[23]](https://humanitec.com/products/platform-orchestrator)。

scorecard 从"考核服务健康"变成"考核服务对 Agent 友好程度"，这是 IDP 这一代的 SKU 转折。

## 8. 新的 DevEx 指标：Agent 使用频次与接受率

DORA 2025 报告引入显式的"AI measurement layer"，建议跟踪 *AI-assisted / AI-generated 在 merged code 中的占比* [[4]](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025)。DX、GetDX、Faros 等 DevEx 度量厂商把"Agent 接受率（acceptance rate）"、"Agent 启动到 merge 的中位时长"、"被 Agent 触发的 PR 比例"列为新指标 [[24]](https://getdx.com/blog/dora-metrics-tools/)。InfoQ 援引 DORA 2026 报告："AI 是放大器，回报来自组织系统而非工具本身"，没有底层（catalog、文档、guardrail）的团队会出现"AI 局部高产出 + 下游混乱"的悖论 [[25]](https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/)。

对应的产品形态变化：IDP 自身必须有 **Agent UI**——开发者在 Cursor 或 Claude Code 里直接调起 self-service action，而不是去 IDP 网页点按钮；Backstage AI Gateway、Cortex Magellan、Roadie AI Search 都在这个方向走 [[26]](https://backstage.spotify.com/docs/portal/core-features-and-plugins/ai-gateway/)。

## 9. 本质判断

第一，**文档的根本读者从人变成 Agent**，docs 工具的买家从 tech writer 转向 platform engineering / AI ops。$300/月 的 Mintlify Pro 之所以卖得动，是因为决策者重新变成了平台团队 leader，不是写作者。

第二，**Confluence / Notion 的内部搜索体验被 LLM 内置搜索绕过**。Agent 不在意 docs 站点的搜索好不好用——它要的是结构化的 Markdown + MCP endpoint。这等同于把 Confluence 这一代工具的"信息架构 + UI"价值清零，剩下的价值只在"内容本身和 access control"。

第三，**Service catalog 的真正护城河是数据新鲜度而非可视化**。Backstage 网页再漂亮，YAML 腐烂照样让 Agent 给出错误答案。Roadie / Cortex / OpsLevel 三家未来 18 个月的角力焦点就是"谁能让 catalog 自动保鲜"——AI 发现 ownership、AI 修复 broken dependency、AI 自动 onboard 新服务。

第四，**DevEx 度量从主观问卷过渡到 Agent telemetry**。这一波的 DORA 升级会重新定义平台工程团队的 KPI——不再是"开发者满意度 8.2 分"，而是"AI 接受率 41%、Agent 触发 PR 占 23%"。问卷不死，但权重会被信号替代。

第五，**llms.txt 与 docs MCP server 是冗余共存而非二选一**。前者面向通用爬虫式消费，后者面向有 session 的 Agent 任务；二者覆盖不同的 Agent 工作流，预计未来 2 年都不会消失。但若必须押一边，MCP 的赢面更大——因为它是 stateful 的、可执行的，而不仅是只读 index。

## 参考文献

[1] Swimm.io, "Swimm — Code-Coupled Documentation," 2026. [Online]. Available: <https://swimm.io/>

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
