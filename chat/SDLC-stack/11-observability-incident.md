# 2026-05-14：SDLC 栈 / 可观测与事故响应 层深度研究

Coding Agent 把代码产出量推高 10–100x（⚠ 解读：取自本系列姐妹篇的量纲假设，行业公开测量目前多在 ~30–55% 任务提速、46% 代码由 Copilot 生成区间 [[33]](https://www.getpanto.ai/blog/github-copilot-statistics)，"10–100x" 是上限叠加多 agent 并发的外推）之后，唯一在金融市场上跑赢"AI 焦虑"的中间层就是可观测性。DDOG 在 2026-05-07 公布 Q1 营收破 10 亿、同比 +32%，当日盘后跳涨约 31% [[1]](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results), [[2]](https://www.benzinga.com/Opinion/26/05/52461478/datadog-becomes-harder-to-ignore-after-solid-q1-earnings)。这不是某个 SaaS 周期性反弹，而是一条结构性结论的市场定价：**Coding Agent 既制造垃圾、也制造昂贵的垃圾，垃圾产生在生产环境，所以"观察 + 处置"层是 Agent 时代唯一显著扩张的中间层。** 本篇按 namespace.so 范式拆 O5（可观测平台）/ O4（事故响应）/ O1'（AI Agent 自身可观测）三层，挖底层结构变化。

## 一、Pre-Agent 时代的基线流量

在 2023–2024 这条 baseline 上：

- **MTTR / MTTA**：DORA 2024 把"恢复时长" 拆成 Failed Deployment Recovery Time，Elite < 1h、High < 1day、Low > 1month 是经典阶梯 [[3]](https://www.atlassian.com/incident-management/kpis/common-metrics)。SRE 圈追求 MTTA < 45s 不让"修复时钟"被检测延迟吃掉 [[4]](https://www.harness.io/blog/what-is-mttr-dora-metric)。
- **on-call 压力**：PagerDuty AIOps 公布的工业基线是它能砍 91% 的告警噪声 [[5]](https://www.pagerduty.com/platform/aiops/)；这个 91% 与基线相互校验：incident.io 2024 年对 500+ on-call 工程师的调研显示**人均每周中位 42 次寻呼** [[34]](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works)，Catchpoint 2024 SRE 调研里 70% 团队把"告警疲劳"列入前三大运维痛点、41% 工程师考虑因之离职 [[34]](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works)——"告警疲劳"成为 2024 年 on-call 工程岗位被引用最多的离职动因（⚠ 解读：从上述两条调研合成的小结，"最被引用"是定性归纳而非排名结果）。
- **log/metric 爆炸**：IDC 估到 2025 年全球数据体量 180 ZB [[6]](https://clickhouse.com/resources/engineering/what-is-observability)；可观测成本由 volume × cardinality × retention 三轴驱动 [[7]](https://clickhouse.com/resources/engineering/observability-tco-cost-reduction)。Kubernetes 容器化把 cardinality 推到指数线——每个 pod 自己一套 label，单一 deployment 的扩缩容就能让 series 数翻倍 [[8]](https://www.observeinc.com/blog/understanding-high-cardinality-in-observability)。"Cardinality explosion is the silent budget killer" 在 2024 年成为业内口头禅 [[9]](https://www.sawmills.ai/blog/best-practices-for-high-cardinality-metrics-in-datadog)。

底色：**人均 on-call 容量被两条曲线挤压**——告警维度（cardinality）指数增长，人脑带宽线性。AIOps 在 2024 之前的故事是降噪、是相关性聚类，**还没敢说"自己修"**。

## 二、Coding Agent 带来的流量本质变化

Coding Agent 时代代码量按 10–100x 放大（⚠ 解读：同上节假设，引自本系列姐妹篇 [[33]](https://www.getpanto.ai/blog/github-copilot-statistics)），对 O5/O4 的冲击不止"bug 多了"：

1. **错误类型分布偏移**。Pre-Agent 的事故偏典型——逻辑越界、SQL 慢、容量超限；Post-Agent 多出一类**幻觉诱发型 bug**：变量名拼错但通过 lint、API 调用参数顺序颠倒、对一个 deprecated 接口的自信调用。Sentry Seer 自己的内部事故就是一例：`LlmNoRegionsToRunError` 阻断了 ~42 000 issue summary、~1 600 spam-detection、~850 autofix 调用，根因只有 6 行代码——"我们 provision 了 GCP 容量"与"代码知道我们 provision 了"之间的认知差 [[10]](https://blog.sentry.io/seer-fixes-seer-debugging-agent/)。这种 bug 的特征：单点小、面儿广、跨服务、低 reproducibility——**人类读 log 不容易抓，机器读全栈 trace 才抓得到**。
2. **on-call 压力曲线非线性爆炸**。代码量乘 10–100x、事故密度未必同比，但**告警面积线性膨胀**：更多服务、更多依赖、更多金丝雀阶段。PagerDuty 2026 Spring 把 SRE agent 直接挂在 escalation policy 上，AWS DevOps Agent 案例宣称 77% MTTR 削减 [[11]](https://medium.com/devops-ai-decoded/the-ai-sre-agent-revolution-why-2026-is-the-year-of-autonomous-incident-resolution-073807b2209d)。一线 SRE 反馈：**60 天后整体 alert 量 70–95% 下降、Sev-2 MTTR 20–40% 改进** [[11]](https://medium.com/devops-ai-decoded/the-ai-sre-agent-revolution-why-2026-is-the-year-of-autonomous-incident-resolution-073807b2209d)。
3. **闭环正在形成**：Agent 写代码 → 生产报错 → Agent 读 trace → Agent 提交 fix PR。这是本层最深刻的变化——**事故响应从"人在回路"退化为"人在审计"**。

## 三、Datadog Bits AI 架构：为什么 DDOG 跑赢

Bits AI 是 Datadog 把全平台数据作为护城河的具象化。它至少有三个 sub-agent：**Bits AI SRE**（事故）、**Bits AI Dev**（提 PR）、**Bits AI Security**（Q1 2026 GA）[[1]](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results)。

- **架构**：Bits AI SRE 设计成"像一支 SRE 团队那样思考"——读 monitor message、抓 Confluence runbook、查同一 monitor 的历史调查、跑 exploratory query；然后把假设拆成 sub-hypothesis，逐一用 live telemetry 验证 [[12]](https://www.datadoghq.com/blog/building-bits-ai-sre/)。
- **数据触角**：2026 升级后接入 metrics / logs / traces / dashboards / changes / source code / events / RUM / Database Monitoring / Network Path / Continuous Profiler—基本是 Datadog 平台数据**总和** [[13]](https://www.datadoghq.com/blog/bits-ai-sre-deeper-reasoning/)。
- **闭环交接**：Bits AI SRE 定位代码型根因 → 把 root cause 结构化交给 Bits AI Dev Agent → 由后者起 PR，工程师只做 review/merge [[12]](https://www.datadoghq.com/blog/building-bits-ai-sre/)。
- **效果**：DDG 官方口径"TTR 下降高达 95%" [[14]](https://www.datadoghq.com/product/ai/bits-ai-sre/)；新一代 Bits AI SRE "approximately twice as fast" [[13]](https://www.datadoghq.com/blog/bits-ai-sre-deeper-reasoning/)。

**Q1 2026 +30% 单日的逻辑**：投资人在重新定价"哪个 SaaS 层是 Agent 净受益方"。Datadog 同时拿到 (a) 代码爆炸 → telemetry 体量爆炸 → 按量计费上行；(b) Bits AI 作为顶层入口把"用 Datadog"从"用 dashboard"变成"对 Datadog 提一个问题，让它跑"——AI agent 入口本身锁定 platform lock-in。MCP Server 也在 Q1 2026 GA [[1]](https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results)，把 Datadog 数据暴露给 Cursor / Claude Code，等于让 coding agent 在写代码阶段就消费 Datadog 数据——**反向把 SDLC 上游也吸进来**。

## 四、Sentry Seer：autonomous debugging 的标准范式

Seer 在 2025 年 GA，是 Sentry 把"看 stack trace"升级到"读代码定位 + 改代码提 PR"的一次产品再造 [[15]](https://blog.sentry.io/seer-sentrys-ai-debugger-is-generally-available/)。

**Issue Autofix 三段流水线** [[16]](https://docs.sentry.io/product/ai-in-sentry/seer/autofix/)：

1. **Root Cause Analysis**——以 issue + breadcrumbs + 关联 commit + 关联代码作为 context，推断根因；
2. **Solution Identification**——给出修复方案、需要改的文件与函数；
3. **Code Generation**——直接生成补丁，**可以选择交给外部 coding agent**（Claude Code 或 Cursor Cloud Agents）继续执行 [[16]](https://docs.sentry.io/product/ai-in-sentry/seer/autofix/)。

GitHub 是当前唯一支持的 SCM；Seer 会读取 Cursor / Windsurf / Cline / Claude Code 各自的 rules 文件——也就是说，它**继承同一个 repo 的 agent 规范**，输出与人类工程师写的代码风格一致 [[16]](https://docs.sentry.io/product/ai-in-sentry/seer/autofix/)。Seer 还把 root cause + solution 作为结构化 prompt 直接 hand-off 给 Claude Code 在终端或 CI 中执行 [[17]](https://docs.sentry.io/integrations/coding-agents/claude/)。配合 sentry-mcp，Cursor / Claude Code 可以在写代码阶段就 query Sentry [[18]](https://github.com/getsentry/sentry-mcp)。**这是"Agent 写 → Agent 修"闭环的最干净样本**。

## 五、Honeycomb AI / MCP：让 Claude Code 直查 trace

Honeycomb 的差异化是把高基数 trace 直接做成 LLM 可消费的形态。MCP server 2025 开源、2026 年 3 月 Honeycomb 把 MCP 集成扩展到 Claude Code / Cursor / AWS DevOps Agent [[19]](https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development)。配置直接一行：

```
claude mcp add honeycomb --transport http https://mcp.honeycomb.io/mcp
```

[[20]](https://docs.honeycomb.io/integrations/mcp/concepts)。暴露的 tool 包括 `run_query`（跑遥测查询）、`run_bubbleup`（在已有 query 上找异常 cohort）、`find_columns`（用自然语言找字段）、`get_trace`（拉完整 trace）[[20]](https://docs.honeycomb.io/integrations/mcp/concepts), [[21]](https://github.com/honeycombio/honeycomb-mcp)。Honeycomb 自己也用这套 MCP 评估 Claude Code 的 ROI 与采纳率 [[22]](https://www.honeycomb.io/blog/measuring-claude-code-roi-adoption-honeycomb)。

本质：**Honeycomb 把 BubbleUp 这种"高基数下找异常 cohort"的核心能力做成 LLM tool**——这恰好是 LLM 自己干不了、但人类 SRE 又最依赖的步骤。Datadog 是平台数据广度赢，Honeycomb 是 trace 深度赢。

## 六、纯 AI SRE 公司：Resolve.ai / Cleric / Parity

**Resolve.ai**：2024 年由前 Splunk 高管 Spiros Xanthos（OpenTelemetry co-creator）和 Mayank Agarwal 创立；2026-02 宣布 Series A $125M @ $1B 估值（Lightspeed 领投，Greylock / Unusual / Artisanal / A* 加注、Fei-Fei Li 与 Jeff Dean 站台）[[23]](https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/), [[24]](https://resolve.ai/blog/series-a-funding)；2026-04 Series A Extension $40M @ $1.5B 估值（DST Global / Salesforce Ventures）[[25]](https://resolve.ai/news/Series-A-extension-and-Resolve-AI-Labs)。客户包括 Coinbase（root cause 快 73%）、DoorDash（调查快 87%）、Salesforce、MongoDB、Zscaler、Toast、Pinecone [[26]](https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976)。集成 Datadog / Splunk / New Relic / Grafana / AWS / GCP / Azure / Kubernetes / GitHub / GitLab / Jenkins / Slack / PagerDuty / Jira [[26]](https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976)。

**Cleric**：自我定位"the AI SRE that learns"——以 Slack 为出口，每次事故都建一份"运营记忆"，给出 confidence 分数与证据链路。Gartner 2025 Cool Vendor (AI for SRE & Observability)，早期客户报告释放 20–30% 工程容量 [[27]](https://cleric.ai/)。

**Parity**：聚焦 Kubernetes 与云基础设施可靠性 [[11]](https://medium.com/devops-ai-decoded/the-ai-sre-agent-revolution-why-2026-is-the-year-of-autonomous-incident-resolution-073807b2209d)。

切入角度对比：Resolve = **跨可观测平台的 SRE 中枢**（看到所有家厂的数据）；Cleric = **on-call 知识沉淀 + 信号降噪**；Parity = **K8s 特定栈纵深**。

## 七、O1'：AI Agent 自身的可观测

代码爆炸的同时还出现一层全新负载——agent 自己的 runtime。需要 4 类新数据：

- **agent 行为日志**：plan → tool call → observation → next step 序列；
- **token 消耗**：按 agent、按 user、按任务的成本归因；
- **tool call trace**：每次 MCP / function-call 的参数、延迟、错误；
- **LLM eval**：响应质量是否"faithful / relevant / safe"——APM 工具量不出来，传统 logging 也量不出来 [[28]](https://www.confident-ai.com/knowledge-base/compare/10-llm-observability-tools-to-evaluate-and-monitor-ai-2026)。

格局已三分 [[29]](https://www.augmentcode.com/tools/best-ai-agent-observability-tools)：（a）APM 大厂——Datadog LLM Observability 提供 inputs/outputs/latency/token/errors 端到端 trace [[30]](https://www.datadoghq.com/product/ai/llm-observability/)；New Relic、Honeycomb Agent Timeline 渲染多 agent 多 trace 的对话视图 [[31]](https://www.honeycomb.io/platform/agent-timeline)。（b）AI-native——Langfuse / LangSmith / Arize 抓 trace 更深但停在"记录发生了什么" [[32]](https://www.langchain.com/articles/llm-observability-tools)。（c）AI gateway——Helicone / Portkey 夹在 app 与 LLM provider 之间做 routing / caching / 成本归因 [[29]](https://www.augmentcode.com/tools/best-ai-agent-observability-tools)。

**Datadog DASH 2025 已推出 "execution flow chart" 可视化 agent 执行 + 决策路径、agent 间交互、工具使用、retrieval 步骤** [[29]](https://www.augmentcode.com/tools/best-ai-agent-observability-tools)。这意味着大厂 APM 正在把 LLM 流量当作和 HTTP 一样的一等公民——而不是 niche feature。

附带产生的新需求：**agent identity & audit**——哪个 agent、什么权限、在什么 commit 上跑、改了哪些文件——这条线 incident.io / PagerDuty 都在 2026 Spring 的发布会上点了名 [[11]](https://medium.com/devops-ai-decoded/the-ai-sre-agent-revolution-why-2026-is-the-year-of-autonomous-incident-resolution-073807b2209d)。

## 八、几条本质判断

1. **可观测层是 Coding Agent 时代少数显著扩张的中间层**。Coding Agent 把代码量推高 10–100x（⚠ 解读：同前节假设 [[33]](https://www.getpanto.ai/blog/github-copilot-statistics)），下游 telemetry 体量被线性甚至超线性放大；同时高基数 + 幻觉 bug 让"无 LLM 协助则不可解"的事故占比上升。两条曲线叠加，让按量计费 SaaS（DDOG、Splunk、Honeycomb）和按 fix 收费 SaaS（Resolve、Cleric）同时受益。
2. **DDOG 跑赢是平台数据广度 × LLM 入口的双杀**——别人只有部分数据，Bits AI 拿全栈；别人 LLM 工具是 add-on，Datadog 用 Bits AI 把 dashboard 替换成自然语言入口，**锁定下一代用户的肌肉记忆**。Q1 +30% 是市场对这个论点的定价，不是周期。
3. **下一代 monitoring = metrics / logs / traces / agent traces 四元组**。前三元组是 Charity Majors 时代的口号，第四元组让"什么人/什么 agent 做了什么"变成可审计、可计费、可治理的一级对象。三大厂（Datadog / New Relic / Splunk）+ AI-native（Langfuse / Arize）+ AI gateway（Helicone / Portkey）正在抢这个第四元组的标准位。
4. **闭环已经成型**：Sentry Seer → Claude Code → GitHub PR；Datadog Bits AI SRE → Bits AI Dev → PR。**fix PR 从"工程师写"变成"agent 写、agent 审、人 merge"**。on-call 这个职位将在 24 个月内重新定义——从"夜里被叫醒去查 log"变成"早上来 review 一堆 agent 已经修好的 PR"。
5. **真正的护城河不是 LLM，是数据 + 工具 + workflow 的整合**。Resolve.ai 拿 OTel 之父做 founder、押的是"跨平台数据整合 + Agent 决策" ——它赌的是垂直 SRE 公司能在大厂 LLM 同质化之前把客户挂在自己的 workflow 上。

## 信源

[1] Datadog, "Datadog Announces First Quarter 2026 Financial Results," 2026-05-07. (Q1 营收 $1.006B, +32% YoY; Bits AI Security Agent、MCP Server、GPU Monitoring、Experiments GA.) [Online]. Available: <https://investors.datadoghq.com/news-releases/news-release-details/datadog-announces-first-quarter-2026-financial-results>

[2] Benzinga, "Datadog Becomes Harder To Ignore After Solid Q1 Earnings," May 2026. (财报后 DDOG 跳涨约 31%.) [Online]. Available: <https://www.benzinga.com/Opinion/26/05/52461478/datadog-becomes-harder-to-ignore-after-solid-q1-earnings>

[3] Atlassian, "MTBF, MTTR, MTTA, and MTTF," Atlassian Incident Management. [Online]. Available: <https://www.atlassian.com/incident-management/kpis/common-metrics>

[4] Harness, "What Is MTTR?: The DORA Metric You Need To Know." (DORA Elite < 1h / High < 1day / Low > 1month; MTTA < 45s.) [Online]. Available: <https://www.harness.io/blog/what-is-mttr-dora-metric>

[5] PagerDuty, "PagerDuty AIOps Platform." (告警噪声削减 91%, MTTR -70%.) [Online]. Available: <https://www.pagerduty.com/platform/aiops/>

[6] ClickHouse, "What is observability in 2026?" (IDC: 2025 全球数据 180 ZB.) [Online]. Available: <https://clickhouse.com/resources/engineering/what-is-observability>

[7] ClickHouse, "A practical guide to observability TCO and cost reduction." (成本 = volume × cardinality × retention.) [Online]. Available: <https://clickhouse.com/resources/engineering/observability-tco-cost-reduction>

[8] Observe Inc., "Understanding High Cardinality in Observability." [Online]. Available: <https://www.observeinc.com/blog/understanding-high-cardinality-in-observability>

[9] Sawmills, "Best Practices for High-Cardinality Metrics in Datadog." [Online]. Available: <https://www.sawmills.ai/blog/best-practices-for-high-cardinality-metrics-in-datadog>

[10] Sentry Engineering, "Seer fixes Seer: How Seer pointed us toward a bug and helped fix an outage," 2026. (LlmNoRegionsToRunError 阻断 ~42 000 issue summary / ~1 600 spam / ~850 autofix; 6 行代码修复.) [Online]. Available: <https://blog.sentry.io/seer-fixes-seer-debugging-agent/>

[11] N. Shah, "The AI SRE Agent Revolution: Why 2026 Is the Year of Autonomous Incident Resolution," *Devops & AI Hub*, Apr 2026. (60 天后 alert 量降 70–95%, Sev-2 MTTR 改进 20–40%; AWS DevOps Agent 77% MTTR.) [Online]. Available: <https://medium.com/devops-ai-decoded/the-ai-sre-agent-revolution-why-2026-is-the-year-of-autonomous-incident-resolution-073807b2209d>

[12] Datadog, "How we built an AI SRE agent that investigates like a team of engineers," 2026. (多 agent 假设拆分 + Bits AI Dev Agent 提 PR 闭环.) [Online]. Available: <https://www.datadoghq.com/blog/building-bits-ai-sre/>

[13] Datadog, "Meet the new Bits AI SRE: Deeper reasoning, twice as fast," 2026. (Bits AI SRE 接入 source code / RUM / Database Monitoring / Network Path / Profiler.) [Online]. Available: <https://www.datadoghq.com/blog/bits-ai-sre-deeper-reasoning/>

[14] Datadog, "Bits AI SRE Product Page." (TTR 削减高达 95%.) [Online]. Available: <https://www.datadoghq.com/product/ai/bits-ai-sre/>

[15] Sentry, "Seer, Sentry's AI Debugger, is Generally Available," 2025. [Online]. Available: <https://blog.sentry.io/seer-sentrys-ai-debugger-is-generally-available/>

[16] Sentry Docs, "Issue Autofix." (Root Cause → Solution → Code Gen 三段流水线; hand-off Claude Code / Cursor Cloud Agents.) [Online]. Available: <https://docs.sentry.io/product/ai-in-sentry/seer/autofix/>

[17] Sentry Docs, "Coding Agents — Claude." [Online]. Available: <https://docs.sentry.io/integrations/coding-agents/claude/>

[18] getsentry/sentry-mcp, GitHub repository. [Online]. Available: <https://github.com/getsentry/sentry-mcp>

[19] Honeycomb, "Honeycomb Advances Observability for AI-Powered Software Development," Mar 2026. (Honeycomb Metrics GA; MCP 集成扩展到 Claude Code / Cursor / AWS DevOps Agent.) [Online]. Available: <https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development>

[20] Honeycomb Docs, "Core Concepts of Honeycomb MCP." (tool: run_query / run_bubbleup / find_columns / get_trace; `claude mcp add honeycomb --transport http https://mcp.honeycomb.io/mcp`.) [Online]. Available: <https://docs.honeycomb.io/integrations/mcp/concepts>

[21] honeycombio/honeycomb-mcp, GitHub repository. [Online]. Available: <https://github.com/honeycombio/honeycomb-mcp>

[22] Honeycomb, "Measuring Claude Code ROI and Adoption in Honeycomb." [Online]. Available: <https://www.honeycomb.io/blog/measuring-claude-code-roi-adoption-honeycomb>

[23] M. Wiggers, "AI SRE Resolve AI confirms $125M raise, unicorn valuation," *TechCrunch*, Feb 2026. [Online]. Available: <https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/>

[24] Resolve AI, "Resolve AI raises $125M Series A to scale AI for prod," 2026-02. [Online]. Available: <https://resolve.ai/blog/series-a-funding>

[25] Resolve AI, "Series A Extension at $1.5B and Resolve AI Labs," 2026-04. ($40M Series A Extension @ $1.5B; DST Global / Salesforce Ventures.) [Online]. Available: <https://resolve.ai/news/Series-A-extension-and-Resolve-AI-Labs>

[26] Skywork, "Resolve.ai: The Agentic AI SRE Changing the Future of On-Call." (Coinbase 73% / DoorDash 87% 提速; 客户名单与集成列表.) [Online]. Available: <https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976>

[27] Cleric, "Operational Memory for Engineering Teams." (Gartner 2025 Cool Vendor; 20–30% 工程容量释放.) [Online]. Available: <https://cleric.ai/>

[28] Confident AI, "10 LLM Observability Tools to Evaluate & Monitor AI in 2026." [Online]. Available: <https://www.confident-ai.com/knowledge-base/compare/10-llm-observability-tools-to-evaluate-and-monitor-ai-2026>

[29] Augment Code, "7 Best AI Agent Observability Tools for Coding Teams in 2026." (三分格局：APM / AI-native / AI gateway; Datadog DASH 2025 execution flow chart.) [Online]. Available: <https://www.augmentcode.com/tools/best-ai-agent-observability-tools>

[30] Datadog, "LLM Observability." [Online]. Available: <https://www.datadoghq.com/product/ai/llm-observability/>

[31] Honeycomb, "Agent Timeline — AI Agent Observability." [Online]. Available: <https://www.honeycomb.io/platform/agent-timeline>

[32] LangChain, "8 LLM Observability Tools to Monitor & Evaluate AI Agents." [Online]. Available: <https://www.langchain.com/articles/llm-observability-tools>
