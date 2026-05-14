# 2026-05-14：SDLC 栈 / 事故响应与 AI SRE (O1') 层深度研究

事故响应（O1'）是 SDLC 栈里被 Coding Agent 时代倒逼最猛的一层。监控（O5）和错误追踪（O4）依然是"看见问题"，O1' 则是"接管问题"——把过去由 on-call 工程师在夜里执行的 Tier 1 工作流，整段移交给 agent。这一层的特殊性在于：**它不在产生 alert，它在消化 alert**。所以 Coding Agent 爆炸产生的 10–100x 代码（⚠ 解读：上限外推，行业可测的提速基线约 30–55% 任务、46% Copilot 代码占比 [[1]](https://www.getpanto.ai/blog/github-copilot-statistics)）通过 O5/O4 转化为告警洪流后，最终撞在 O1' 这块板上——而这块板的承载量，过去 10 年没怎么动过。

本篇按 namespace.so 范式拆这一层。

## 一、Pre-Agent 时代的 on-call 流量基线

2024 这条 baseline 上，on-call 工程师的工作画像有几条硬数据可锚：

- **人均寻呼数**：incident.io 2024 对 500+ on-call 工程师调研，**人均每周中位 42 次寻呼** [[2]](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works)。
- **疲劳与离职**：Catchpoint 2024 SRE 调研显示 **70% 团队**把"告警疲劳"列入前三大运维痛点；**41% 工程师**因 on-call 压力考虑离职 [[2]](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works)。Catchpoint 2025 SRE Report 进一步把**操作 toil 占比从 25% 推到 30%**，五年来首次回升 [[3]](https://www.catchpoint.com/learn/sre-report-2025)——说明工具增量并未抵消负载增量。
- **MTTR / MTTA 阶梯**：DORA Elite 团队故障恢复 < 1 小时、High < 1 天、Low > 1 个月 [[4]](https://www.atlassian.com/incident-management/kpis/common-metrics)；SRE 行业内卷 MTTA < 45 秒以免"检测延迟吃掉修复预算" [[5]](https://www.harness.io/blog/what-is-mttr-dora-metric)。
- **降噪的旧上限**：PagerDuty AIOps 在 LLM 之前能做到的极限是 87–91% 告警噪声削减 [[6]](https://www.pagerduty.com/platform/aiops/)。这一代 AIOps 解决的是"事件聚类、相关性、抑制"，**不解决"自己上手修"**——降噪的下游仍然是人。

底色：人均寻呼带宽线性、cardinality 指数膨胀，**离职率成为可靠性新的 root cause**。

## 二、Coding Agent 时代如何让 O1' 突变

Coding Agent 改变 O1' 不是因为"agent 又写出新 bug"，而是因为**告警面积的几何放大 + 错误类型的分布偏移 + 修复闭环的人位移**。

1. **告警面积线性甚至超线性膨胀**。代码量乘 10–100x（⚠ 解读：上限外推 [[1]](https://www.getpanto.ai/blog/github-copilot-statistics)），更多服务、更多依赖、更多金丝雀、更多 deploy。AWS DevOps Agent GA 文档援引早期客户口径："**up to 75% lower MTTR, 80% faster investigations, 94% root cause accuracy**，支撑 3–5x 事故解决加速" [[7]](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)——这些数字反向反映了**未上 agent 时基线之失控**。
2. **错误类型偏移**。Agent 写出的 bug 偏向"幻觉诱发型"——变量名、参数顺序、对 deprecated API 的自信调用——单点小、面儿广、跨服务、低 reproducibility。这类 bug 人类 SRE 翻 log 不容易抓住，但跨全栈 trace 的 agent 反而合适：它能在一次 investigation 里读 100 个 service 的 deploy diff，人类做不到（⚠ 解读：这是从 Sentry Seer 自己修自己事故的范式 [[8]](https://blog.sentry.io/seer-fixes-seer-debugging-agent/) 引申，普适性需要更多公开案例证实）。
3. **闭环位移**。Pre-Agent 的工作流是 "alert → 人接 → 人查 → 人修 → 人复盘"；Post-Agent 是 "alert → agent 接 → agent 查 → agent 提 PR → 人 review/merge → agent 写 retro 草稿"。**人从 Tier 1 退到 Tier 2/3**——具体表现为：on-call 这个岗位将在 24 个月内从"夜里被叫起来查 log"重新定义为"早上来 review 一堆 agent 已经修好的 PR"（⚠ 解读：24 个月窗口基于 Resolve / Bits AI / AWS DevOps Agent 当前部署节奏外推，无单一信源支撑）。

## 三、Agent 时代的 O1' 新需求

四条需求被 2026 Spring 的几家发布会同步点了名：

- **自治 Tier 1**：alert 到来后 agent 直接 shell 进 sandboxed pod 跑 `kubectl describe`、查 cloud API、读 CI/CD pipeline、再 re-plan，最后把"高 confidence + 证据链"或"low confidence + 升级人"两种结果之一交给 Slack [[9]](https://stackgen.com/blog/pagerduty-vs.-ai-sre-why-traditional-incident-response-cant-keep-up)。这与 AIOps 时代的"聚类排序"差异本质："投票哪几个 alert 是同一原因"vs"亲自去取新证据"。
- **runbook 即代码**：runbook 不再是 wiki 上给人读的 markdown，而是 agent 可消费的 skill bundle。Anthropic Claude Managed Agents 把 SRE on-call 做成参考 cookbook，agent 收 PagerDuty payload → 挂载 runbook skill bundle → triage 到 root cause → 起最小可安全部署的 fix；progressive disclosure 让 agent 只读相关 runbook 段落而非整本 [[10]](https://platform.claude.com/cookbook/managed-agents-sre-incident-responder)。Honeycomb 的 **Canvas Skills** 把同一思路做成产品形态：工程师把最佳实践 debug 知识"教"给 agent，下次类似事故 agent 直接调用 [[11]](https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development)。
- **根因定位 + 自动回滚**：Resolve 把"surface 根因 + 给出可执行 PR / kubectl / 脚本"做成一等输出 [[12]](https://resolve.ai/product/ai-sre)；AWS DevOps Agent 在 WGU 案例里把一次 service disruption 从估计 2 小时压到 28 分钟（**77% MTTR 改进**），并把动作链落到具体 commit 与 rollback step 上 [[7]](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)。
- **人 → Tier 2/3**：保留人在架构决策、容量规划、可靠性策略；agent 拦截 Tier 1 重复劳动。Cleric 公开口径"释放 20–30% 工程容量" [[13]](https://cleric.ai/) 是这个分工的市场化定价。

## 四、代表公司的技术架构与案例

**Resolve.ai**——AI SRE 赛道领头羊。前 Splunk 高管 Spiros Xanthos（OpenTelemetry co-creator）与 Mayank Agarwal 创立。**2026-02 Series A $125M @ $1B 估值**（Lightspeed 领投，Greylock / Unusual / Artisanal / A* 加注，Fei-Fei Li 与 Jeff Dean 站台）[[14]](https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/), [[15]](https://resolve.ai/blog/series-a-funding)；**2026-04 Series A Extension $40M @ $1.5B**（DST Global / Salesforce Ventures）[[16]](https://resolve.ai/news/Series-A-extension-and-Resolve-AI-Labs)。架构上 Resolve 给三个 agent：根因 + 修复、成本优化、把 production context 喂回 feature 开发；调查时**并行追多 hypothesis、每条用 evidence 验证、给出带 citation 的结构化解释**——客户能看到推理过程、相关 query、甚至引入 bug 的具体 PR [[12]](https://resolve.ai/product/ai-sre)。客户案例：**Coinbase 73% 更快定位根因**（"median first response 秒级、critical incident 分钟级到 likely root cause"）[[17]](https://resolve.ai/customers/coinbase)；DoorDash 调查快 87%；Salesforce / MongoDB / Zscaler / Toast / Pinecone 全部在用 [[18]](https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976)。集成跨 Datadog / Splunk / New Relic / Grafana / AWS / GCP / Azure / K8s / GitHub / GitLab / Jenkins / Slack / PagerDuty / Jira [[18]](https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976)——**vendor-neutral 是 Resolve 对 Datadog Bits AI 的核心差异**：Bits AI 只看 Datadog 自家数据，Resolve 看所有家厂数据。

**Cleric**——以 Slack 为出口，每次事故沉淀一份"运营记忆"，给出 confidence 分与证据链。Gartner 2025 Cool Vendor (AI for SRE & Observability)，公开 20–30% 工程容量释放 [[13]](https://cleric.ai/)。

**Parity**——YC 项目，三位创始人来自 Crusoe 的 on-call rotation，**首家把"AI SRE for Kubernetes on-call engineers"做成单点切入**：调查 K8s alert、找根因、给 remediation；产品里包含**runbook 自动执行**——按预定流程跑下来 [[19]](https://www.ycombinator.com/companies/parity)。这条线是赌"K8s 这一层复杂度足以单独养一家公司"。

**Robusta / HolmesGPT**——开源路线，**CNCF Sandbox 2025-10 收录** [[20]](https://github.com/robusta-dev/holmesgpt)。HolmesGPT 跑 iterative ReAct loop：alert triage、跨系统相关性、证据打包、引导式 remediation；定位是"压缩 incident response 的搜索阶段，让答案更易验证" [[20]](https://github.com/robusta-dev/holmesgpt)。它覆盖 K8s / VM / 云厂 / 数据库 / SaaS——是 SRE agent 这条赛道的**开源参考实现**。

**Incident.io**——从 on-call 工具厂转型 AI SRE 平台。AI SRE 完全 Slack-native，做 **autonomous investigation**（把 telemetry 与 code changes 串起来找根因）、**Scribe**（自动 transcribe incident call 并填进 timeline）、**自动起草 post-mortem** [[21]](https://incident.io/blog/5-best-ai-powered-incident-management-platforms-2026)。

**PagerDuty AIOps + SRE Agent**——**Spring 2026 release 把 agent 直接挂到 escalation policy 上** [[9]](https://stackgen.com/blog/pagerduty-vs.-ai-sre-why-traditional-incident-response-cant-keep-up)。逻辑分工是：AIOps 先把告警量砍掉 87% [[6]](https://www.pagerduty.com/platform/aiops/)，剩下高价值告警交给 SRE Agent 去"取新证据 + re-plan"——**AIOps 减体积、Agent 做深度**。

**FireHydrant**——AI 不在 root cause 那一侧，而在事故协作那一侧：incident summary、Zoom 会议 insight、AI 起草 retrospective、状态页更新、AI 辅助 Five Whys [[22]](https://docs.firehydrant.com/docs/ai-powered-incident-management)。它把"事故周边写作工作"自动化——这块成本被低估。

**Anthropic Claude Managed Agents**——把 SRE on-call 做成参考实现：agent 收 PagerDuty payload，session workspace 包含近期 logs、infra repo、team runbook；自定义工具 `open_pull_request` / `request_approval` / `merge_pull_request` 强制人在回路 [[10]](https://platform.claude.com/cookbook/managed-agents-sre-incident-responder)。Anthropic 自家 SRE 公开"从 1 月起遇事先 reach for Claude 而非传统监控面板" [[23]](https://www.theregister.com/2026/03/19/anthropic_claude_sre)。

**Honeycomb Automated Investigations + Canvas Skills**——alert 触发或 SLO burn 时 agent 自动调查、推荐解；Canvas Skills 让团队把内部 debug 知识沉淀成可复用 playbook [[11]](https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development)。

**AWS DevOps Agent**——**2026-03-31 GA**，六区域覆盖，企业级安全、CMK、合规 [[24]](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-devops-agent-generally-available/)。预览期客户口径：MTTR -75%、investigation -80%、根因准确率 94%、3–5x 事故解决加速；WGU 案例 2 小时 → 28 分钟（77% MTTR 改进）[[7]](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)。AWS 把它定位为"frontier agent"——和 AWS Security Agent 同批发布，**AWS 自己把 Agentic Ops 列入战略 SKU**。

## 五、几条本质判断

1. **O1' 与 O5/O4 的关系正在重构**。监控（O5）和错误追踪（O4）继续负责"看见"，但**"接管"独立成层**——并且这一层不属于任何一家可观测厂的天然延伸。Datadog Bits AI SRE 借平台数据广度切；Resolve / Cleric / Parity 借 vendor-neutral 切；PagerDuty 借 escalation policy 入口切；AWS / Azure 借云厂闭环切。**没有自然垄断者**，这是这一层估值多点开花的结构原因。
2. **AIOps 与 SRE Agent 是两件事**。AIOps 解决"alert 太多"，SRE Agent 解决"alert 接下来怎么办"。两者不互斥而互补——PagerDuty 自己也把它们拆成两层产品。这意味着 incident.io 等老 IM 厂的 AI SRE，需要先解决降噪、再叠 agent，不能跳步。
3. **Resolve.ai 在 14 个月内估值从 $1B → $1.5B，押的是 vendor-neutral 而不是 LLM**。同期 Bits AI、AWS DevOps Agent、Azure SRE Agent 都自带"我家数据 + 我家 LLM"组合——Resolve 反过来赌"客户不愿被任何一家可观测厂或云厂绑定 SRE agent"。这条假设如果成立，Resolve 会成为新一代 PagerDuty；不成立，会被大厂吃掉。**贵的不是模型，是跨平台数据集成 + workflow 沉淀**。
4. **runbook 即代码 + Skills 是新的护城河形式**。Anthropic Skills 和 Honeycomb Canvas Skills 把"团队默会知识"打包成 agent 可消费的 skill bundle——这是过去 wiki + checklist 解决不了的形态。**谁掌握客户 runbook，谁就掌握下一代 on-call 入口**。
5. **on-call 工程师工作的"夜间属性"将在 24 个月内基本消失**（⚠ 解读：24 个月窗口为外推，基础是 Resolve / Bits AI / AWS DevOps Agent 当前部署节奏 + Anthropic 自家 SRE 已"先 reach for Claude" [[23]](https://www.theregister.com/2026/03/19/anthropic_claude_sre)）。Tier 1 由 agent 在分钟内闭环、人在白天 review；只有 Sev-0 / 架构问题保留人值守。**41% 工程师考虑因 on-call 离职**这一基线 [[2]](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works) 将被结构性消解——但前提是 agent 的 false-positive fix 率足够低（这是 Resolve / Cleric 当前最害怕的失败模式，公开 confidence score 是对冲）。
6. **O1' 是 Agent 时代第一个被"按 fix 收费"取代"按席位收费"重构的中间层**。传统 PagerDuty 是按用户席位卖（人越多越贵），Resolve / Cleric 在打按事故、按 Tier 1 处置量计费——这与 O5（按 volume 计）、O4（按 issue 计）的计费基底都不同。**计费单位变了，意味着市场天花板被重画**。

## 信源

[1] Panto AI, "GitHub Copilot Statistics 2026 — Users, Revenue & Adoption," 2026. (Copilot ~55% 任务提速、46% 代码由 Copilot 生成；用作 "10–100x" 上限外推的底线信源。) [Online]. Available: <https://www.getpanto.ai/blog/github-copilot-statistics>

[2] incident.io, "Alert fatigue solutions for DevOps teams in 2025: What works," 2025. (incident.io 2024 调研 500+ on-call 工程师，人均周中位 42 次寻呼；Catchpoint 2024 SRE 调研 70% 团队列入前三痛点、41% 考虑离职。) [Online]. Available: <https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works>

[3] Catchpoint, "SRE Report 2025." (操作 toil 占比从 25% 升至 30%，五年来首次回升；n=301。) [Online]. Available: <https://www.catchpoint.com/learn/sre-report-2025>

[4] Atlassian, "MTBF, MTTR, MTTA, and MTTF," Atlassian Incident Management. (DORA Elite < 1h / High < 1day / Low > 1month.) [Online]. Available: <https://www.atlassian.com/incident-management/kpis/common-metrics>

[5] Harness, "What Is MTTR?: The DORA Metric You Need To Know." (MTTA < 45s 内卷.) [Online]. Available: <https://www.harness.io/blog/what-is-mttr-dora-metric>

[6] PagerDuty, "PagerDuty AIOps Platform." (告警噪声削减 87–91%, MTTR -70%.) [Online]. Available: <https://www.pagerduty.com/platform/aiops/>

[7] AWS, "Announcing General Availability of AWS DevOps Agent," *AWS Cloud Operations Blog*, Mar 2026. (预览客户口径 MTTR -75% / investigation -80% / RCA 94% / 3-5x 加速；WGU 案例 2h → 28min, 77% MTTR 改进.) [Online]. Available: <https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/>

[8] Sentry Engineering, "Seer fixes Seer: How Seer pointed us toward a bug and helped fix an outage," 2026. (幻觉型 bug 范式 + agent 自我修复案例.) [Online]. Available: <https://blog.sentry.io/seer-fixes-seer-debugging-agent/>

[9] StackGen, "PagerDuty vs. AI SRE: Why Traditional Incident Response Can't Keep Up," 2026. (Spring 2026 PagerDuty SRE Agent 挂到 escalation policy；agent shell 进 pod / kubectl describe / re-plan.) [Online]. Available: <https://stackgen.com/blog/pagerduty-vs.-ai-sre-why-traditional-incident-response-cant-keep-up>

[10] Anthropic, "Build an SRE incident response agent with Claude Managed Agents," *Claude Cookbook*, 2026. (PagerDuty payload + runbook skill bundle + progressive disclosure；open_pull_request / request_approval / merge_pull_request 自定义工具.) [Online]. Available: <https://platform.claude.com/cookbook/managed-agents-sre-incident-responder>

[11] Honeycomb, "Honeycomb Advances Observability for AI-Powered Software Development," Mar 2026. (Automated Investigations + Canvas Skills；alert/SLO burn 触发 agent 自调查；可复用 debug playbook.) [Online]. Available: <https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development>

[12] Resolve AI, "AI SRE Product Page," 2026. (三 agent 架构、并行多 hypothesis、带 citation 的 RCA 解释、生成 PR / kubectl / scripts.) [Online]. Available: <https://resolve.ai/product/ai-sre>

[13] Cleric, "Operational Memory for Engineering Teams." (Gartner 2025 Cool Vendor; 20–30% 工程容量释放；Slack-native + confidence + 证据链.) [Online]. Available: <https://cleric.ai/>

[14] M. Wiggers, "AI SRE Resolve AI confirms $125M raise, unicorn valuation," *TechCrunch*, Feb 2026. [Online]. Available: <https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/>

[15] Resolve AI, "Resolve AI raises $125M Series A to scale AI for prod," 2026-02. [Online]. Available: <https://resolve.ai/blog/series-a-funding>

[16] Resolve AI, "Series A Extension at $1.5B and Resolve AI Labs," 2026-04. ($40M Series A Extension @ $1.5B; DST Global / Salesforce Ventures.) [Online]. Available: <https://resolve.ai/news/Series-A-extension-and-Resolve-AI-Labs>

[17] Resolve AI, "Coinbase — Making the Global Crypto Backbone More Resilient." (73% 更快定位根因；median first response 秒级、critical incident 分钟到 likely RC.) [Online]. Available: <https://resolve.ai/customers/coinbase>

[18] Skywork, "Resolve.ai: The Agentic AI SRE Changing the Future of On-Call." (DoorDash 87%；客户名单 Coinbase / Salesforce / MongoDB / Zscaler / Toast / Pinecone；集成清单.) [Online]. Available: <https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976>

[19] Y Combinator, "Parity: The AI SRE for Incident Response." (K8s on-call agent；自动跑 runbook；创始团队来自 Crusoe.) [Online]. Available: <https://www.ycombinator.com/companies/parity>

[20] robusta-dev/holmesgpt, GitHub repository. (CNCF Sandbox 2025-10；iterative ReAct loop；K8s / VM / 云 / DB / SaaS.) [Online]. Available: <https://github.com/robusta-dev/holmesgpt>

[21] incident.io, "5 best AI-powered incident management platforms 2026." (Incident.io AI SRE Slack-native + autonomous investigation + Scribe + post-mortem 草稿.) [Online]. Available: <https://incident.io/blog/5-best-ai-powered-incident-management-platforms-2026>

[22] FireHydrant, "AI-Powered Incident Management." (incident summary / Zoom insight / AI retrospective / status update / Five Whys.) [Online]. Available: <https://docs.firehydrant.com/docs/ai-powered-incident-management>

[23] T. Claburn, "Fixing Claude with Claude: Anthropic reports on AI SRE," *The Register*, Mar 2026. (Anthropic 自家 SRE 公开"先 reach for Claude 而非传统监控".) [Online]. Available: <https://www.theregister.com/2026/03/19/anthropic_claude_sre>

[24] AWS, "AWS DevOps Agent is now generally available," Mar 2026. (2026-03-31 GA；六区域；CMK / 合规.) [Online]. Available: <https://aws.amazon.com/about-aws/whats-new/2026/03/aws-devops-agent-generally-available/>
