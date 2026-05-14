# 2026-05-14：SDLC 栈 / 可观测与监控 (O5) 层深度研究

**O5 层的护城河结构是"四元组重组下的协议位次 + 数据广度"** —— metrics / logs / traces / agent traces 是新货架，OTel GenAI Semantic Conventions + MCP 是新协议；谁占住货架、谁把货架开放给 coding agent，谁赢。Datadog 占的是**数据广度**，Honeycomb 占的是**协议位次**（BubbleUp 等高基数能力直接 tool 化），Grafana / Langfuse 开源派站在**第四元组的开放采集侧**。

Coding Agent 把代码产出量推高一个数量级以上（⚠ 解读：取自本系列姐妹篇的量纲假设，行业公开测量目前多在 ~30–55% 任务提速、46% 代码由 Copilot 生成区间 [[1]](https://www.getpanto.ai/blog/github-copilot-statistics)，"10–100x" 是上限叠加多 agent 并发的外推）之后，2026 Q1 财报季在 SaaS 中间层显著跑赢的是可观测：DDOG 在 2026-05-07 公布 Q1 营收 $1,006M、同比 +32%、ARR 越过 $40 亿，盘后跳涨约 31%——自 2019 上市以来最大单日涨幅 [[2]](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results), [[3]](https://www.tikr.com/blog/datadog-stock-jumps-31-after-q1-revenue-crosses-1-billion-for-the-first-time)。**这个 +30% 单日的结构是 (a) 按量计费的体量放大叠加 (b) 协议位次的红利**。Honeycomb 同期同步跑赢、Grafana Labs 估值 2026 早期被报抬到 $9B、Langfuse 2026-01 被 ClickHouse 收购，都落在同一条护城河上。本篇只谈 metrics / logs / traces / agent traces 监控平台；错误追踪（O4 Sentry）与事故响应（O1' Resolve / Cleric / PagerDuty SRE Agent）分别在 11b 与 11c。

## 一、第四元组的成立：agent traces 作为新货架

Logs / metrics / traces 在 Charity Majors 时代被确立为可观测的三根支柱 [[10]](https://www.elastic.co/blog/3-pillars-of-observability)，OpenTelemetry 在 2023 之后逐渐成为采集层事实标准 [[11]](https://opentelemetry.io/docs/concepts/observability-primer/)。2023–2024 的底色是"三元组成型 + cardinality 爆炸"两条曲线并存：IDC 估到 2025 年全球数据体量 180 ZB [[6]](https://clickhouse.com/resources/engineering/what-is-observability)；成本由 volume × cardinality × retention 三轴驱动 [[7]](https://clickhouse.com/resources/engineering/observability-tco-cost-reduction)；Kubernetes 容器化把 cardinality 推到指数线，每个 pod 自己一套 label，单 deployment 扩缩容就能让 series 数翻倍 [[8]](https://www.observeinc.com/blog/understanding-high-cardinality-in-observability), [[9]](https://www.sawmills.ai/blog/best-practices-for-high-cardinality-metrics-in-datadog)。DORA 2024 把"恢复时长"拆成 Failed Deployment Recovery Time，Elite < 1h、High < 1day、Low > 1month 是经典阶梯；SRE 圈把 MTTA < 45s 作为"不让检测延迟吃掉修复时钟"的下限 [[4]](https://www.atlassian.com/incident-management/kpis/common-metrics), [[5]](https://www.harness.io/blog/what-is-mttr-dora-metric)。

进入 Agent 时代，多出来的不是"事件量"而是**一种新的数据形态**：agent plan → tool call → observation → next step 的序列。它和 trace 同形（都是 span 树），但语义在更高一层——不是 service A 调 service B，而是 agent 在思考、调工具、读返回、决定下一步。这条数据线在 LLMOps 小圈子里早就有，但 2025–2026 关键的变化是：

1. **三大 APM 同时下注**。Datadog DASH 2025 推出 execution flow chart，可视化 agent 决策路径、agent 间交互、工具使用、retrieval 步骤 [[12]](https://www.augmentcode.com/tools/best-ai-agent-observability-tools)；Honeycomb 2026-03 Agent Timeline 把"每一次 LLM 调用 / agent 交接 / tool 调用"连成单视图 [[13]](https://siliconangle.com/2026/05/12/honeycomb-introduces-agent-observability-features-keep-eye-production/)；New Relic 2026 Advance 把 AI Agent Monitoring 正式塞进 APM context [[14]](https://newrelic.com/blog/news/scaling-ai-agents-ai-observability), [[15]](https://newrelic.com/blog/news/new-relic-advance-2026)。三家在同一年同时把这条数据当作一等公民开列产品发布会标题位（⚠ 解读：作者整合三家 2026 Q1 产品发布的归纳）。
2. **协议层固化**。OTel GenAI Semantic Conventions 在 2025–2026 期间快速扩展，覆盖 `create_agent` / `invoke_agent` 等 agent 操作 spans、GenAI events、GenAI metrics [[37]](https://opentelemetry.io/docs/specs/semconv/gen-ai/), [[38]](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)。截至 2026-03 大部分仍是 experimental 状态，但 Datadog 自 v1.37+ 原生支持，使其在事实层面落地 [[24]](https://www.datadoghq.com/blog/llm-otel-semantic-convention/)。Anthropic 在 Claude Code / Claude Agent SDK 层把 OTel 接成一等公民——CLI 自带 traces / metrics / logs 三个独立 OTel 信号开关；Agent SDK 可导出到任意 OTLP 后端 [[39]](https://code.claude.com/docs/en/agent-sdk/observability), [[40]](https://support.claude.com/en/articles/14477985-monitor-claude-cowork-activity-with-opentelemetry)；Langfuse 已专门为 Claude Agent SDK 写好集成 [[41]](https://langfuse.com/integrations/frameworks/claude-agent-sdk)。
3. **携带不可降维的新需求**。**agent identity & audit**（哪个 agent、什么权限、在什么 commit 上跑、改了哪些文件）、**token / cost 归因**（按 agent / user / 任务）、**LLM eval**（faithful / relevant / safe）、**模型回归检测**（同一 prompt 在新模型版本下质量飘移）——这些 APM 量不出来、传统 logging 也量不出来 [[18]](https://www.confident-ai.com/knowledge-base/compare/10-llm-observability-tools-to-evaluate-and-monitor-ai-2026)。

"第四元组"这个术语本身在业内尚未统一（候选项还有 profiling、context、config data [[16]](https://www.mezmo.com/learn-observability/a-fourth-pillar-of-observability), [[17]](https://www.cloudquery.io/blog/fourth-lost-pillar-of-observability-config-data-monitoring)），但 agent traces 是 2026 唯一被三大 APM 同时下注、又被 OTel 在 spec 层固化的候选。货架本身从三格扩成四格，所有占住新格的玩家都得到红利——这是 Datadog、Honeycomb、Grafana、Langfuse 在 2026 Q1 同步走强的共同结构。

## 二、按量计费 × 超线性 telemetry：DDOG Q1 +32% 的结构解释

把 DDOG Q1 2026 拆开看：营收 $1,006M、同比 +32% [[2]](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results)；盘后跳涨 31%（2019 IPO 以来最大单日涨幅）；同时上调 2026 全年指引到 $4.30B–$4.34B，上调幅度在大型 SaaS 里罕见 [[3]](https://www.tikr.com/blog/datadog-stock-jumps-31-after-q1-revenue-crosses-1-billion-for-the-first-time)。这条上调要解释，靠"Bits AI 卖得好"不够——Bits AI 大部分仍在 GA 早期，Q1 的真正发动机是**按量计费乘以代码爆炸**。

机制：

- **代码量 10–100x → 服务数 / 依赖数 / 金丝雀阶段数线性甚至超线性膨胀**。Coding Agent 不只是让 PR 变多，而是让微服务拆分、临时 endpoint、A/B 实验同步膨胀；每一个新 endpoint 自带一组 high-cardinality label。
- **错误类型分布偏移**。Pre-Agent 事故偏典型（逻辑越界、SQL 慢、容量超限），Post-Agent 多出一类**幻觉诱发型 bug**：变量名拼错但通过 lint、API 参数顺序颠倒、对 deprecated 接口的自信调用。这类 bug 单点小、面儿广、跨服务、低 reproducibility——**人类读 log 不容易抓，机器读全栈 trace 才抓得到**。这把 trace 的相对价值往上拉，metric / log 的相对价值往下压；按量计费的 trace 后端因此结构性受益。
- **事故密度未必同比，但 alert 数量随之上行**。客户在 2026 第一季度对"自动分诊"的需求增速远超对"采集更多数据"的需求增速（⚠ 解读：作者从 Datadog / New Relic / Honeycomb 2026 Q1 产品发布会的相对权重归纳，无单一数字信源）。

对照 Pre-Agent 时代的 AIOps 基线：PagerDuty 等老牌 AIOps 厂商以"事件相关性 / 噪声削减"为卖点，公开口径是 AIOps 可削减约 91% 的告警噪声 [[43]](https://www.pagerduty.com/platform/aiops/)。这个数字在 Pre-Agent 是核心 KPI，进入 2026 反而退化成必要不充分条件——**降噪不创造收入弹性，按量计费的体量放大才创造**。AWS 在 re:Invent 2024 公开的 DevOps Agent 数据是另一头的对照：在内部使用中把 MTTR 削减约 77% [[44]](https://aws.amazon.com/blogs/devops/) (⚠ 解读：AWS 官方博客口径，未经第三方独立复算)。这类"降低 MTTR"的指标在 2026 已成为新一代 agent 产品的入场券，而非差异化卖点。

DDOG Q1 +32% 的结构解释因此是：**(a) 按量计费的 telemetry 体量被 coding agent 超线性放大，(b) 按 fix 收费 / 自动分诊带来的产品组合升级在估值倍数上叠加**。前者给收入，后者给倍数。两条线都不需要"自然语言入口"来解释。

## 三、双护城河样本：Datadog 数据广度 vs Honeycomb trace 深度 + tool 化

Bits AI 是 Datadog 把"全平台数据"作为护城河的具象化。它至少有三个 sub-agent：**Bits AI SRE**（事故）、**Bits AI Dev**（提 PR）、**Bits AI Security**（Q1 2026 GA）[[2]](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results)。

- **架构**：Bits AI SRE 设计成"像一支 SRE 团队那样思考"——读 monitor message、抓 Confluence runbook、查同一 monitor 的历史调查、跑 exploratory query；把假设拆成 sub-hypothesis，逐一用 live telemetry 验证 [[19]](https://www.datadoghq.com/blog/building-bits-ai-sre/)。
- **数据触角**：2026 升级后接入 metrics / logs / traces / dashboards / changes / source code / events / RUM / Database Monitoring / Network Path / Continuous Profiler——基本是 Datadog 平台数据**总和** [[20]](https://www.datadoghq.com/blog/bits-ai-sre-deeper-reasoning/)。这是别家 APM 复制不了的护城河——LLM 同质化，数据广度不同质化。
- **Bits AI Dev 工作流**：与 GitHub 集成，开 draft PR、用 CI log 迭代、checks 通过后转 ready for review；auto-push 能自动为高影响错误（500、crash）开 PR；还能为 flaky test 生成 PR、为 Code Security 漏洞生成修复 PR [[21]](https://www.datadoghq.com/blog/bits-ai-dev-agent/), [[22]](https://www.datadoghq.com/blog/bitsai-dev-agent-code-security/), [[23]](https://www.datadoghq.com/blog/bits-ai-test-optimization/)。
- **MCP Server Q1 2026 GA**：把 Datadog 数据暴露给 Cursor / Claude Code，等于让 coding agent 在写代码阶段就消费 Datadog 数据——反向把 SDLC 上游也吸进来 [[2]](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results)。
- **官方效果口径**：TTR 下降高达 95%；新一代 Bits AI SRE "approximately twice as fast" [[20]](https://www.datadoghq.com/blog/bits-ai-sre-deeper-reasoning/), [[25]](https://www.datadoghq.com/product/ai/bits-ai-sre/)。

Honeycomb 走的不是"广"而是"深 + 协议位次"。MCP server 2025 开源，2026-03 扩展到 Claude Code / Cursor / AWS DevOps Agent，并发布 Honeycomb Metrics GA 与 Agent Timeline / Canvas Agent / Canvas Skills [[26]](https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development), [[13]](https://siliconangle.com/2026/05/12/honeycomb-introduces-agent-observability-features-keep-eye-production/)。配置直接一行：

```
claude mcp add honeycomb --transport http https://mcp.honeycomb.io/mcp
```

[[27]](https://docs.honeycomb.io/integrations/mcp/concepts)。暴露的 tool 包括 `run_query`（跑遥测查询）、`run_bubbleup`（在已有 query 上找异常 cohort）、`find_columns`（用自然语言找字段）、`get_trace`（拉完整 trace）[[27]](https://docs.honeycomb.io/integrations/mcp/concepts), [[28]](https://github.com/honeycombio/honeycomb-mcp)。Honeycomb 自己也用这套 MCP 评估 Claude Code 的 ROI 与采纳率 [[29]](https://www.honeycomb.io/blog/measuring-claude-code-roi-adoption-honeycomb)。

本质：**Honeycomb 把 BubbleUp 这种"高基数下找异常 cohort"的核心能力做成 LLM tool**——这恰好是 LLM 自己干不了、但人类 SRE 又最依赖的步骤。Datadog 是平台数据广度赢，Honeycomb 是 trace 深度 + tool 化赢；二者在 2026 表现出明显的差异化共存而非正面替代。如果 lens 是"入口转移"，这俩应当此消彼长；事实上是两条护城河——广度护城河给 Datadog 留 enterprise 横向心智，深度 / 协议护城河给 Honeycomb 留 trace-heavy 团队的工具调用心智。

## 四、协议位次：OTel GenAI + MCP 把消费侧外包给 IDE

四元组货架立起来后，决定谁吃到红利的是**协议位次**。这条线分两段：

**采集侧**：OTel GenAI Semantic Conventions 把 agent 操作 spans / events / metrics 的字段名固化下来 [[37]](https://opentelemetry.io/docs/specs/semconv/gen-ai/), [[38]](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)。Datadog 自 v1.37 起原生支持 [[24]](https://www.datadoghq.com/blog/llm-otel-semantic-convention/)，第三方 agent 框架的 trace 不需要二次桥接就能进 Datadog。Anthropic 把 OTel 接成 Claude Code / Claude Agent SDK 的一等公民，traces / metrics / logs 三个独立信号开关，OTLP 后端任选 [[39]](https://code.claude.com/docs/en/agent-sdk/observability), [[40]](https://support.claude.com/en/articles/14477985-monitor-claude-cowork-activity-with-opentelemetry)。Langfuse 已专门为 Claude Agent SDK 写好集成 [[41]](https://langfuse.com/integrations/frameworks/claude-agent-sdk)。

**消费侧**：MCP 把"看 dashboard"这件事外包给 IDE / 编辑器侧的 coding agent。`claude mcp add honeycomb` 一行接入就能让 Claude Code 直接对 Honeycomb 提问、跑 BubbleUp、抓 trace [[27]](https://docs.honeycomb.io/integrations/mcp/concepts)。Datadog MCP Server Q1 2026 GA 在 Cursor / Claude Code 侧暴露 Datadog 数据 [[2]](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results)。

这两段叠起来的含义：**O5 平台不再是 dashboard 终点站，而是 coding agent 的工具调用对象**。壁垒从"UI 谁更好看"重新回到"数据 + 协议"。这条变化对开源派（Grafana / Elastic / Langfuse）尤其友好：

- **Grafana Labs** 进入 2026 时 ARR > $400M，估值约 $6B（早前数据），2026 早期一轮估值据报 $9B；LGTM 栈（Loki logs / Grafana metrics / Tempo traces / Mimir / Pyroscope profiling）继续作为开源派的事实标准 [[33]](https://sacra.com/c/grafana-labs/), [[34]](https://grafana.com/docs/pyroscope/latest/)。一个潜在 IPO 窗口（2027）将重设开源观测的估值基准。
- **Langfuse** 开源自托管 + 框架无关，2026-01 被 ClickHouse 收购 [[36]](https://medium.com/@kanerika/llmops-observability-langsmith-vs-arize-vs-langfuse-vs-w-b-f1baeabd1bbf)——这条交易是"OLAP 引擎 + 开源 LLM observability"的纵向整合，押的不是 LLM 谁聪明，是"OTel GenAI conventions 之上谁有最便宜的写入路径"。
- **AI-native 第三派格局**：到 2026 Q2，行业共识收敛成六平台格局：LangSmith / Langfuse / Arize Phoenix / Helicone / Datadog LLM Observability / Honeycomb LLM Observability [[35]](https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026), [[36]](https://medium.com/@kanerika/llmops-observability-langsmith-vs-arize-vs-langfuse-vs-w-b-f1baeabd1bbf)。选型大致是：LangGraph → LangSmith；框架无关 + 自托管 → Langfuse；eval 严苛 → Arize Phoenix [[35]](https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026)。AI gateway（Helicone / Portkey）夹在 app 与 LLM provider 之间做 routing / caching / 成本归因 [[42]](https://www.augmentcode.com/tools/best-ai-agent-observability-tools)，是这条管道里相对新的一段。

其余 APM 阵营各自在四元组里找位次：**New Relic** 2026-02 发布 AI Agent Monitoring 与 New Relic Agentic Platform，把 SRE Agent / Knowledge / Agent Monitoring 串起来，强调"full-stack from infra to agent decision logic" [[30]](https://techcrunch.com/2026/02/24/new-relic-launches-new-ai-agent-platform-and-opentelemetry-tools/), [[14]](https://newrelic.com/blog/news/scaling-ai-agents-ai-observability), [[31]](https://www.helpnetsecurity.com/2026/05/06/new-relic-knowledge-capability/)。**Splunk (Cisco)** 2024 完成收购后正以 Splunk 数据 fabric 串 ThousandEyes + AppDynamics + Nexus One，定位"NetOps + SecOps 单一 telemetry pipeline"；可观测在 Cisco 内部从独立 SaaS 转为网络栈附带能力 [[32]](https://www.heygotrade.com/en/blog/datadog-ddog-vs-splunk-cisco-observability-war/)。**Dynatrace** 2026 财年指引 $2.005–$2.010B、EPS 增速 ~23%，定位大型受监管企业的 AI-first APM [[32]](https://www.heygotrade.com/en/blog/datadog-ddog-vs-splunk-cisco-observability-war/)。**Elastic Observability** 仍以"search + open-core"打开发者心智，预算紧时尤其受益 [[32]](https://www.heygotrade.com/en/blog/datadog-ddog-vs-splunk-cisco-observability-war/)。

## 五、不赢的画像

把上面四节倒过来看，能写出三类"在 2026 跑不出来"的产品画像：

1. **只押 LLM 聪明的**。LLM 同质化的速度比 SaaS 行业预期更快——Datadog 自己的 Bits AI 也并未押单一模型。任何只讲"我们家 LLM 更懂 SRE"的可观测产品，没有数据广度（DDOG）/ trace 深度（Honeycomb）/ 协议位次（OTel + MCP）做底，在 2026 都不能讲通故事。
2. **只押 dashboard UI 的**。MCP 把消费侧外包给 IDE 之后，"做一个更好看的故障墙"不再是护城河。dashboard 仍有价值（人类排障的兜底界面），但**它不再是用户与平台之间的唯一接口**。重押 UI 而轻视 tool / MCP 接入的厂商，会发现自己的产品被 coding agent"绕过"——agent 走 MCP 直接读底层数据，把 dashboard 跳过。
3. **只押降噪的**。Pre-Agent 的 AIOps 把"91% 噪声削减"当核心 KPI [[43]](https://www.pagerduty.com/platform/aiops/)；进入 Agent 时代，降噪只是入场券。真正的弹性来自"自动分诊 + 自动修复 + 写回 PR"的闭环——MTTR -77%、TTR -95% 这类口径已经是新一代产品的及格线 [[44]](https://aws.amazon.com/blogs/devops/), [[25]](https://www.datadoghq.com/product/ai/bits-ai-sre/)。卡在只降噪的产品，被两侧挤压：一边是按量计费平台用全栈数据吃掉相关性聚类，另一边是 fix-loop 产品用 GitHub PR 吃掉操作面。

收尾的本质判断：**O5 层的护城河不是 LLM 本身，而是 (a) 已有客户的数据广度（DDOG）/ (b) trace 深度 + 工具语义化（Honeycomb）/ (c) 协议位次（OTel + MCP）三选一或叠加**。Q1 2026 +30% 单日是市场对这条三选一的定价，不是周期，也不是"入口转移"的单点叙事——后者只能解释 Bits AI，无法解释 Honeycomb 同步跑赢、Grafana / Langfuse 估值上行。

## 信源

[1] Panto AI, "GitHub Copilot Statistics 2026 — Users, Revenue & Adoption," 2026. (Copilot 用户 ~55% 任务提速、46% 代码由 Copilot 生成；本文用作 "10–100x" 上限推断的底线信源。) [Online]. Available: <https://www.getpanto.ai/blog/github-copilot-statistics>

[2] Datadog, "Datadog Announces First Quarter 2026 Financial Results," 2026-05-07. (Q1 营收 $1.006B, +32% YoY, ARR > $4B; Bits AI Security Agent / MCP Server / GPU Monitoring / Experiments GA.) [Online]. Available: <https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results>

[3] TIKR, "Datadog Stock Jumps 31% After Q1 Revenue Crosses $1 Billion for the First Time," May 2026. (盘后跳涨 31%，2019 IPO 以来最大单日；上调 2026 全年指引到 $4.30–$4.34B.) [Online]. Available: <https://www.tikr.com/blog/datadog-stock-jumps-31-after-q1-revenue-crosses-1-billion-for-the-first-time>

[4] Atlassian, "MTBF, MTTR, MTTA, and MTTF," Atlassian Incident Management. [Online]. Available: <https://www.atlassian.com/incident-management/kpis/common-metrics>

[5] Harness, "What Is MTTR?: The DORA Metric You Need To Know." (DORA Elite < 1h / High < 1day / Low > 1month; MTTA < 45s.) [Online]. Available: <https://www.harness.io/blog/what-is-mttr-dora-metric>

[6] ClickHouse, "What is observability in 2026?" (IDC: 2025 全球数据 180 ZB.) [Online]. Available: <https://clickhouse.com/resources/engineering/what-is-observability>

[7] ClickHouse, "A practical guide to observability TCO and cost reduction." (成本 = volume × cardinality × retention.) [Online]. Available: <https://clickhouse.com/resources/engineering/observability-tco-cost-reduction>

[8] Observe Inc., "Understanding High Cardinality in Observability." [Online]. Available: <https://www.observeinc.com/blog/understanding-high-cardinality-in-observability>

[9] Sawmills, "Best Practices for High-Cardinality Metrics in Datadog." [Online]. Available: <https://www.sawmills.ai/blog/best-practices-for-high-cardinality-metrics-in-datadog>

[10] Elastic, "The 3 pillars of observability: Unified logs, metrics, and traces." [Online]. Available: <https://www.elastic.co/blog/3-pillars-of-observability>

[11] OpenTelemetry, "Observability primer." [Online]. Available: <https://opentelemetry.io/docs/concepts/observability-primer/>

[12] Augment Code, "7 Best AI Agent Observability Tools for Coding Teams in 2026." (Datadog DASH 2025 execution flow chart; APM / AI-native / AI gateway 三分格局.) [Online]. Available: <https://www.augmentcode.com/tools/best-ai-agent-observability-tools>

[13] SiliconANGLE, "Honeycomb introduces agent observability features to keep an eye on production," 2026-05-12. (Agent Timeline / Canvas Agent / Canvas Skills.) [Online]. Available: <https://siliconangle.com/2026/05/12/honeycomb-introduces-agent-observability-features-keep-eye-production/>

[14] New Relic, "Scaling AI Agents With AI Observability." (AI Agent Monitoring 嵌入 APM context.) [Online]. Available: <https://newrelic.com/blog/news/scaling-ai-agents-ai-observability>

[15] New Relic, "New Relic Advance 2026: Operating Beyond Human Scale." [Online]. Available: <https://newrelic.com/blog/news/new-relic-advance-2026>

[16] Mezmo, "A Fourth Pillar of Observability." (候选：profiling / context / config.) [Online]. Available: <https://www.mezmo.com/learn-observability/a-fourth-pillar-of-observability>

[17] CloudQuery, "The Lost Fourth Pillar of Observability — Config Data Monitoring." [Online]. Available: <https://www.cloudquery.io/blog/fourth-lost-pillar-of-observability-config-data-monitoring>

[18] Confident AI, "10 LLM Observability Tools to Evaluate & Monitor AI in 2026." [Online]. Available: <https://www.confident-ai.com/knowledge-base/compare/10-llm-observability-tools-to-evaluate-and-monitor-ai-2026>

[19] Datadog, "How we built an AI SRE agent that investigates like a team of engineers," 2026. (多 agent 假设拆分 + Bits AI Dev hand-off 闭环.) [Online]. Available: <https://www.datadoghq.com/blog/building-bits-ai-sre/>

[20] Datadog, "Meet the new Bits AI SRE: Deeper reasoning, twice as fast," 2026. (接入 source code / RUM / Database Monitoring / Network Path / Profiler；速度 ~2x.) [Online]. Available: <https://www.datadoghq.com/blog/bits-ai-sre-deeper-reasoning/>

[21] Datadog, "Automatically identify issues and generate fixes with Bits AI Dev." (draft PR + CI 迭代 + auto-push.) [Online]. Available: <https://www.datadoghq.com/blog/bits-ai-dev-agent/>

[22] Datadog, "Introducing Bits AI Dev Agent for Code Security." (为漏洞自动生成 PR.) [Online]. Available: <https://www.datadoghq.com/blog/bitsai-dev-agent-code-security/>

[23] Datadog, "Automate flaky test fixes with the Bits AI Dev Agent and Test Optimization." [Online]. Available: <https://www.datadoghq.com/blog/bits-ai-test-optimization/>

[24] Datadog, "Datadog LLM Observability natively supports OpenTelemetry GenAI Semantic Conventions." (v1.37+.) [Online]. Available: <https://www.datadoghq.com/blog/llm-otel-semantic-convention/>

[25] Datadog, "Bits AI SRE Product Page." (TTR 削减高达 95%.) [Online]. Available: <https://www.datadoghq.com/product/ai/bits-ai-sre/>

[26] Honeycomb, "Honeycomb Advances Observability for AI-Powered Software Development," Mar 2026. (Metrics GA; MCP 扩展到 Claude Code / Cursor / AWS DevOps Agent.) [Online]. Available: <https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development>

[27] Honeycomb Docs, "Core Concepts of Honeycomb MCP." (tool: run_query / run_bubbleup / find_columns / get_trace; `claude mcp add honeycomb --transport http https://mcp.honeycomb.io/mcp`.) [Online]. Available: <https://docs.honeycomb.io/integrations/mcp/concepts>

[28] honeycombio/honeycomb-mcp, GitHub repository. [Online]. Available: <https://github.com/honeycombio/honeycomb-mcp>

[29] Honeycomb, "Measuring Claude Code ROI and Adoption in Honeycomb." [Online]. Available: <https://www.honeycomb.io/blog/measuring-claude-code-roi-adoption-honeycomb>

[30] TechCrunch, "New Relic launches new AI agent platform and OpenTelemetry tools," 2026-02-24. [Online]. Available: <https://techcrunch.com/2026/02/24/new-relic-launches-new-ai-agent-platform-and-opentelemetry-tools/>

[31] Help Net Security, "New Relic advances AI observability with new intelligence layer," 2026-05-06. (New Relic Knowledge.) [Online]. Available: <https://www.helpnetsecurity.com/2026/05/06/new-relic-knowledge-capability/>

[32] HeyGoTrade, "Datadog (DDOG) vs Splunk (Cisco): Observability War 2026." (Splunk 在 Cisco 内的整合定位；Dynatrace FY26 指引 $2.005–2.010B；Elastic 开源核心.) [Online]. Available: <https://www.heygotrade.com/en/blog/datadog-ddog-vs-splunk-cisco-observability-war/>

[33] Sacra, "Grafana Labs revenue, valuation & funding." (ARR > $400M, 估值约 $6B；LGTM 栈构成；2026 早期一轮估值据报 $9B.) [Online]. Available: <https://sacra.com/c/grafana-labs/>

[34] Grafana, "Grafana Pyroscope documentation." (Continuous profiling 作为 LGTM 一支.) [Online]. Available: <https://grafana.com/docs/pyroscope/latest/>

[35] Digital Applied, "Agent Observability: LangSmith, Langfuse, Arize 2026." (六平台格局；LangGraph → LangSmith / 框架无关 → Langfuse / eval 重 → Arize.) [Online]. Available: <https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026>

[36] Kanerika, "LLMOps Observability: LangSmith vs Arize vs Langfuse vs W&B," May 2026. (Langfuse 2026-01 被 ClickHouse 收购.) [Online]. Available: <https://medium.com/@kanerika/llmops-observability-langsmith-vs-arize-vs-langfuse-vs-w-b-f1baeabd1bbf>

[37] OpenTelemetry, "Semantic conventions for generative AI systems." [Online]. Available: <https://opentelemetry.io/docs/specs/semconv/gen-ai/>

[38] OpenTelemetry, "Semantic Conventions for GenAI agent and framework spans." (`create_agent` / `invoke_agent`.) [Online]. Available: <https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/>

[39] Anthropic, "Observability with OpenTelemetry — Claude Agent SDK." (三个独立 OTel 信号开关；OTLP 后端任选.) [Online]. Available: <https://code.claude.com/docs/en/agent-sdk/observability>

[40] Anthropic, "Monitor Claude Cowork activity with OpenTelemetry." [Online]. Available: <https://support.claude.com/en/articles/14477985-monitor-claude-cowork-activity-with-opentelemetry>

[41] Langfuse, "Observability for Claude Agent SDK with Langfuse." [Online]. Available: <https://langfuse.com/integrations/frameworks/claude-agent-sdk>

[42] Augment Code, "7 Best AI Agent Observability Tools for Coding Teams in 2026." (AI gateway: Helicone / Portkey.) [Online]. Available: <https://www.augmentcode.com/tools/best-ai-agent-observability-tools>

[43] PagerDuty, "AIOps Platform." (AIOps 可削减约 91% 告警噪声，作为 Pre-Agent 时代降噪 KPI 的代表口径.) [Online]. Available: <https://www.pagerduty.com/platform/aiops/>

[44] AWS, "DevOps Blog — AWS DevOps Agent / Operational Investigation case studies." (内部使用中 MTTR 削减约 77%；⚠ AWS 官方口径，未经第三方独立复算.) [Online]. Available: <https://aws.amazon.com/blogs/devops/>
