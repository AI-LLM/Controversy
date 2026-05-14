# 2026-05-14：SDLC 栈 / 事故响应与 AI SRE (O1') 层深度研究

事故响应（O1'）是 SDLC 栈里被 Coding Agent 时代倒逼最猛的一层，但它不能用"流量"这个 lens 来读。监控（O5）按 volume 计费、错误追踪（O4）按 issue 计费，那两层确实是流量层；O1' 不是——alert 多寡、降噪比、人均寻呼数都只是**输入参数**，真正决定这一层市场结构的是两根正交主轴：

- **Tier 1 自治闭环（处置侧）**：无人介入即可关单的事故占比，乘以"不引入新事故"的安全边界。这一根轴解释了为什么计费单位从席位重构成 per-fix / per-incident，也解释了为什么 PagerDuty 把 AIOps 与 SRE Agent 拆成两层产品。
- **runbook 即资产（沉淀侧）**：runbook / skill bundle 沉淀深度构成的切换成本。这一根轴解释了为什么 Resolve、Cleric、Honeycomb Canvas、Anthropic Skills 都在卷"团队默会知识可消费化"——护城河不在 LLM、不在集成数，而在客户私有 runbook 资产的厚度。

"角色重分配"——on-call 从夜班变白日 review——是这两根轴交叉后的**结果**，不是 lens 本身。本篇按 namespace.so 范式拆这一层。

## 一、Pre-Agent 基线：寻呼带宽、降噪上限、人是瓶颈

L11c 的本质不是流量。要看清这一点，先把 2024 这条 baseline 摆出来：

- **人均寻呼数**：incident.io 2024 对 500+ on-call 工程师调研，**人均每周中位 42 次寻呼** [[1]](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works)。
- **疲劳与离职**：Catchpoint 2024 SRE 调研显示 **70% 团队**把"告警疲劳"列入前三大运维痛点；**41% 工程师**因 on-call 压力考虑离职 [[1]](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works)。Catchpoint 2025 SRE Report 进一步把**操作 toil 占比从 25% 推到 30%**，五年来首次回升 [[2]](https://www.catchpoint.com/learn/sre-report-2025)——工具增量并未抵消负载增量。
- **MTTR / MTTA 阶梯**：DORA Elite 团队故障恢复 < 1 小时、High < 1 天、Low > 1 个月 [[3]](https://www.atlassian.com/incident-management/kpis/common-metrics)；SRE 行业内卷 MTTA < 45 秒以免"检测延迟吃掉修复预算" [[4]](https://www.harness.io/blog/what-is-mttr-dora-metric)。
- **降噪的旧上限**：PagerDuty AIOps 在 LLM 之前能做到的极限是 87–91% 告警噪声削减 [[5]](https://www.pagerduty.com/platform/aiops/)。这一代 AIOps 解决的是"事件聚类、相关性、抑制"，**不解决"自己上手修"**——降噪的下游仍然是人。

把这四条放在一起看：42 pages/wk 是流量、降噪率是流量的衰减系数、MTTR 是人作业速度的天花板、离职率是人作业意愿的天花板。**Pre-Agent 时代 L11c 的瓶颈是"人均带宽 × 留任率"，流量只是把人压到这两条天花板的施力**。改流量（再降噪）边际收益已经趋零——PagerDuty AIOps 把 87% 噪声砍掉之后剩下的告警每一条都重要，**降噪不再是 lens**。

⚠ **解读**：把 §1 写成"流量基线"是错的诊断角度。这一节的功能是说明"为什么单靠继续降噪解决不了 L11c"，从而引出双主轴。incident.io 的 42 pages/wk、Catchpoint 的 41% 离职率，是用来证伪"流量 lens"的反面证据，不是 L11c 估值的锚。

## 二、双主轴突变：Tier 1 闭环率上探 + runbook 从 wiki 变 skill 资产

2025 下半年到 2026 上半年发生的关键变化，是两根主轴同时位移。

**主轴一：Tier 1 自治闭环率上探**。Pre-Agent 工作流是 "alert → 人接 → 人查 → 人修 → 人复盘"，闭环率以人为单位计；Post-Agent 是 "alert → agent 接 → agent 查 → agent 提 PR → 人 review/merge → agent 写 retro 草稿"，**闭环率以"无人介入即关单"为单位计**。AWS DevOps Agent GA 文档援引早期客户口径："**up to 75% lower MTTR、80% faster investigations、94% root cause accuracy**，支撑 3–5x 事故解决加速" [[6]](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)；WGU 案例把一次 service disruption 从估计 2 小时压到 28 分钟（**77% MTTR 改进**）[[6]](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)。Resolve 客户口径：**Coinbase 73% 更快定位根因**（"median first response 秒级、critical incident 分钟级到 likely root cause"）[[7]](https://resolve.ai/customers/coinbase)；**DoorDash 调查快 87%** [[8]](https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976)。这些百分比的共同特征：**它们度量的是 agent 在"自治关单 + 高 confidence"区间内的覆盖面**，不是降噪率，也不是人作业速度。

错误类型偏移加速了这一上探。Agent 写出的 bug 偏向"幻觉诱发型"——变量名错、参数顺序乱、对 deprecated API 的自信调用——单点小、面儿广、跨服务、低 reproducibility；人类 SRE 翻 log 不容易抓住，但跨全栈 trace 的 agent 反而合适：一次 investigation 里读 100 个 service 的 deploy diff，人类做不到（⚠ **解读**：这是从 Sentry Seer 自己修自己事故的范式 [[9]](https://blog.sentry.io/seer-fixes-seer-debugging-agent/) 引申，普适性待更多公开案例证实）。

**主轴二：runbook 从 wiki 变 skill 资产**。Pre-Agent 时代 runbook 是给人读的 markdown，价值在"写下来"；Post-Agent 时代 runbook 是给 agent 消费的可调用结构，价值在"被调用次数 × 沉淀深度"。Anthropic Claude Managed Agents 把 SRE on-call 做成参考 cookbook：agent 收 PagerDuty payload → 挂载 runbook **skill bundle** → triage 到 root cause → 起最小可安全部署的 fix；progressive disclosure 让 agent 只读相关 runbook 段落而非整本 [[10]](https://platform.claude.com/cookbook/managed-agents-sre-incident-responder)。Honeycomb **Canvas Skills** 把同一思路做成产品形态：工程师把最佳实践 debug 知识"教"给 agent，下次类似事故 agent 直接调用 [[11]](https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development)。Cleric 把每次事故沉淀一份"运营记忆"，与 confidence score 一起给出 [[12]](https://cleric.ai/)——这也是 runbook 资产化的一种形态：每次事故都在让客户私有资产增厚。

**两根主轴是耦合的**：闭环率上探需要 runbook 资产做底（没有私有 runbook，agent 就只能干通用 K8s/AWS 那一段）；runbook 资产化又只在闭环率上探后才有商业意义（agent 不接管 Tier 1，runbook 就没人写）。**这就是 O1' 这一层 2026 年集中爆量的结构性原因**。

## 三、闭环率的工程化：confidence、证据链、human-in-loop gate、false-fix 风控

把"无人介入关单"做成可承诺的产品，工程上必须解决四件事：

1. **confidence 分必须显式可读**。Cleric 的 Slack 出口在每条事故旁挂 confidence 分与证据链 [[12]](https://cleric.ai/)；Resolve 给出"带 citation 的结构化解释"，客户能看到推理过程、相关 query、引入 bug 的具体 PR [[13]](https://resolve.ai/product/ai-sre)。没有显式 confidence，闭环率无法定价。
2. **证据链必须可回放**。AIOps 时代"投票哪几个 alert 是同一原因"够用；Agent 时代要"亲自去取新证据"——alert 到来后 agent 直接 shell 进 sandboxed pod 跑 `kubectl describe`、查 cloud API、读 CI/CD pipeline、再 re-plan，最后把"高 confidence + 证据链"或"low confidence + 升级人"两种结果之一交给 Slack [[14]](https://stackgen.com/blog/pagerduty-vs.-ai-sre-why-traditional-incident-response-cant-keep-up)。证据链是 Tier 1 自治闭环的合法性来源。
3. **human-in-loop gate 必须强制**。Anthropic Claude Managed Agents 给 SRE agent 的自定义工具就三个：`open_pull_request`、`request_approval`、`merge_pull_request` [[10]](https://platform.claude.com/cookbook/managed-agents-sre-incident-responder)——**写 PR 是 agent 的，合 PR 是人的**。这条 gate 是 Tier 1 闭环承诺与 false-fix 风险之间的安全阀。
4. **false-fix 风险必须可对冲**。⚠ **解读**：这是 Resolve / Cleric / AWS DevOps Agent 当前都在公开数字上避开的失败模式——94% root cause accuracy [[6]](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/) 听起来高，但落在"每周 42 寻呼"基数下，剩 6% 若是 silent false-fix 仍是灾难。公开 confidence 分、强制 human gate、把 retry/rollback 内置成 agent 一等动作——这是当前一线产品对冲 false-fix 风险的主要手段。

把四件事打包做完，Tier 1 闭环率才能从"演示数字"变成"可计费数字"。这也直接解释了 **计费单位重构**：传统 PagerDuty 按席位卖（人越多越贵），Resolve / Cleric 在打按事故、按 Tier 1 处置量计费——**计费基底从"被叫醒的人数"切到"自治关单的事故数"**，与 O5（按 volume）、O4（按 issue）的计费基底都不同。计费单位变了，市场天花板被重画。

## 四、玩家分型：四条切入路径，没有自然垄断者

**Vendor-neutral 路线（Resolve / Cleric / Parity）**——赌"客户不愿被任何一家可观测厂或云厂绑定 SRE agent"。**Resolve.ai** 由前 Splunk 高管 Spiros Xanthos（OpenTelemetry co-creator）与 Mayank Agarwal 创立，**2026-02 Series A $125M @ $1B 估值**（Lightspeed 领投，Greylock / Unusual / Artisanal / A* 加注，Fei-Fei Li 与 Jeff Dean 站台）[[15]](https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/), [[16]](https://resolve.ai/blog/series-a-funding)；**2026-04 Series A Extension $40M @ $1.5B**（DST Global / Salesforce Ventures）[[17]](https://resolve.ai/news/Series-A-extension-and-Resolve-AI-Labs)——14 个月内估值 $1B → $1.5B。三 agent 架构（根因 + 修复、成本优化、把 production context 喂回 feature 开发），调查时**并行追多 hypothesis、每条用 evidence 验证** [[13]](https://resolve.ai/product/ai-sre)。集成跨 Datadog / Splunk / New Relic / Grafana / AWS / GCP / Azure / K8s / GitHub / GitLab / Jenkins / Slack / PagerDuty / Jira [[8]](https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976)；客户名单 Coinbase / DoorDash / Salesforce / MongoDB / Zscaler / Toast / Pinecone [[8]](https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976)。**Cleric** 以 Slack 为出口，Gartner 2025 Cool Vendor (AI for SRE & Observability)，公开 20–30% 工程容量释放 [[12]](https://cleric.ai/)。**Parity**（YC 项目，三创始人来自 Crusoe 的 on-call rotation）首家把"AI SRE for Kubernetes on-call engineers"做成单点切入，包含 **runbook 自动执行** [[18]](https://www.ycombinator.com/companies/parity)——直接对应主轴二。

**云厂闭环路线（AWS / Azure）**——赌"我家数据 + 我家 LLM 闭环就够"。**AWS DevOps Agent** **2026-03-31 GA**，六区域覆盖，企业级安全、CMK、合规 [[19]](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-devops-agent-generally-available/)；预览期客户口径 MTTR -75% / investigation -80% / RCA 94% / 3–5x 加速 [[6]](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)；AWS 把它定位为"frontier agent"——与 AWS Security Agent 同批发布，**Agentic Ops 进了 AWS 战略 SKU**。

**入口卡位路线（PagerDuty / incident.io / FireHydrant）**——赌"escalation policy / Slack 入口本身就是壁垒"。**PagerDuty AIOps + SRE Agent**：**Spring 2026 release 把 agent 直接挂到 escalation policy 上** [[14]](https://stackgen.com/blog/pagerduty-vs.-ai-sre-why-traditional-incident-response-cant-keep-up)，逻辑分工是 AIOps 先把告警量砍掉 87% [[5]](https://www.pagerduty.com/platform/aiops/)，剩下高价值告警交给 SRE Agent 去取新证据 + re-plan——**AIOps 减体积、Agent 做深度**。**Incident.io** 从 on-call 工具厂转型 AI SRE 平台，做 autonomous investigation、**Scribe**（自动 transcribe incident call 填进 timeline）、自动起草 post-mortem [[20]](https://incident.io/blog/5-best-ai-powered-incident-management-platforms-2026)。**FireHydrant** 不押 root cause 而押事故协作：incident summary、Zoom 会议 insight、AI retrospective、状态页更新、AI 辅助 Five Whys [[21]](https://docs.firehydrant.com/docs/ai-powered-incident-management)——"事故周边写作工作"自动化，这块成本被低估。

**知识层路线（Honeycomb Canvas / Anthropic Skills / Robusta HolmesGPT）**——赌"runbook 资产化本身就是层"。**Anthropic Claude Managed Agents** 把 SRE on-call 做成参考实现，agent session workspace 包含近期 logs、infra repo、team runbook [[10]](https://platform.claude.com/cookbook/managed-agents-sre-incident-responder)；Anthropic 自家 SRE 公开"从 1 月起遇事先 reach for Claude 而非传统监控面板" [[22]](https://www.theregister.com/2026/03/19/anthropic_claude_sre)。**Honeycomb Automated Investigations + Canvas Skills**：alert 触发或 SLO burn 时 agent 自动调查、推荐解；Canvas Skills 让团队把内部 debug 知识沉淀成可复用 playbook [[11]](https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development)。**Robusta / HolmesGPT** 开源路线，**CNCF Sandbox 2025-10 收录** [[23]](https://github.com/robusta-dev/holmesgpt)，iterative ReAct loop 覆盖 K8s / VM / 云厂 / 数据库 / SaaS——SRE agent 赛道的**开源参考实现**。

四条路径同台，**没有自然垄断者**——这是这一层估值多点开花的结构原因。

## 五、本质判断：计费、护城河、岗位

把双主轴的位移翻译成结构性结论，三句话：

1. **计费单位从席位切到处置量**。Pre-Agent 时代 PagerDuty 按人头卖，逻辑是"人是稀缺的接警工"；Post-Agent 时代 Resolve / Cleric 按事故 / Tier 1 处置量卖，逻辑是"agent 是稀缺的关单工"。计费单位的迁移是 Tier 1 闭环率上探的**直接结果**——只有当"无人介入关单"成为可承诺的产品形态，per-fix 才有合同基础。这与 O5（按 volume 计）、O4（按 issue 计）的计费基底都不同，**O1' 的市场天花板因此被重画**。
2. **护城河从集成数切到私有 runbook 资产**。早期 AI SRE 比拼"接了多少家可观测厂、多少家云、多少家 CI/CD"，集成数是显性变量；当多数玩家都接了 14+ 家之后，**真正的切换成本变成"客户在你这里沉淀了多少私有 runbook / skill bundle / 运营记忆"**。Anthropic Skills、Honeycomb Canvas、Cleric 的 operational memory——三家做同一件事：把客户默会知识固化在 agent 可消费的结构里，让客户搬家时不得不重新教一遍。**谁掌握客户 runbook，谁就掌握下一代 on-call 入口**。Resolve.ai 14 个月估值 $1B → $1.5B 押的不是 LLM，是 vendor-neutral 通道里沉淀的客户 workflow 与 runbook——这条假设如果成立，Resolve 会成为新一代 PagerDuty；不成立，会被大厂吃掉。**贵的不是模型，是私有 runbook 沉淀深度**。
3. **岗位从夜班切到白日 review**。⚠ **解读**：on-call 工程师工作的"夜间属性"将在 24 个月内基本消失（窗口为外推，基础是 Resolve / Bits AI / AWS DevOps Agent 当前部署节奏 + Anthropic 自家 SRE 已"先 reach for Claude" [[22]](https://www.theregister.com/2026/03/19/anthropic_claude_sre)）。Tier 1 由 agent 在分钟内闭环、人在白天 review；只有 Sev-0 / 架构问题保留人值守。**41% 工程师考虑因 on-call 离职**这一基线 [[1]](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works) 将被结构性消解——但前提是 false-fix 率足够低。岗位重分配是双主轴的**结果**而非 lens：自治闭环率上探把人从 Tier 1 顶出来、runbook 资产化把人的角色固化在"教 agent + review agent"上。**SRE 不会消失，但夜班会**。

补一句配套观察：**AIOps 与 SRE Agent 是两件事**。AIOps 解决"alert 太多"，SRE Agent 解决"alert 接下来怎么办"——PagerDuty 自己把它们拆成两层产品就是承认这一点。incident.io 等老 IM 厂的 AI SRE，必须先解决降噪、再叠 agent，不能跳步。把降噪 lens 与处置 lens 混在一起谈，是 §1 容易掉进的旧惯性，本篇明确把它分开。

## 信源

[1] incident.io, "Alert fatigue solutions for DevOps teams in 2025: What works," 2025. (incident.io 2024 调研 500+ on-call 工程师，人均周中位 42 次寻呼；Catchpoint 2024 SRE 调研 70% 团队列入前三痛点、41% 考虑离职。) [Online]. Available: <https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works>

[2] Catchpoint, "SRE Report 2025." (操作 toil 占比从 25% 升至 30%，五年来首次回升；n=301。) [Online]. Available: <https://www.catchpoint.com/learn/sre-report-2025>

[3] Atlassian, "MTBF, MTTR, MTTA, and MTTF," Atlassian Incident Management. (DORA Elite < 1h / High < 1day / Low > 1month.) [Online]. Available: <https://www.atlassian.com/incident-management/kpis/common-metrics>

[4] Harness, "What Is MTTR?: The DORA Metric You Need To Know." (MTTA < 45s 内卷.) [Online]. Available: <https://www.harness.io/blog/what-is-mttr-dora-metric>

[5] PagerDuty, "PagerDuty AIOps Platform." (告警噪声削减 87–91%, MTTR -70%.) [Online]. Available: <https://www.pagerduty.com/platform/aiops/>

[6] AWS, "Announcing General Availability of AWS DevOps Agent," *AWS Cloud Operations Blog*, Mar 2026. (预览客户口径 MTTR -75% / investigation -80% / RCA 94% / 3-5x 加速；WGU 案例 2h → 28min, 77% MTTR 改进.) [Online]. Available: <https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/>

[7] Resolve AI, "Coinbase — Making the Global Crypto Backbone More Resilient." (73% 更快定位根因；median first response 秒级、critical incident 分钟到 likely RC.) [Online]. Available: <https://resolve.ai/customers/coinbase>

[8] Skywork, "Resolve.ai: The Agentic AI SRE Changing the Future of On-Call." (DoorDash 87%；客户名单 Coinbase / Salesforce / MongoDB / Zscaler / Toast / Pinecone；集成清单.) [Online]. Available: <https://skywork.ai/skypage/en/Resolve.ai-The-Agentic-AI-SRE-Changing-the-Future-of-On-Call/1976483370459262976>

[9] Sentry Engineering, "Seer fixes Seer: How Seer pointed us toward a bug and helped fix an outage," 2026. (幻觉型 bug 范式 + agent 自我修复案例.) [Online]. Available: <https://blog.sentry.io/seer-fixes-seer-debugging-agent/>

[10] Anthropic, "Build an SRE incident response agent with Claude Managed Agents," *Claude Cookbook*, 2026. (PagerDuty payload + runbook skill bundle + progressive disclosure；open_pull_request / request_approval / merge_pull_request 自定义工具.) [Online]. Available: <https://platform.claude.com/cookbook/managed-agents-sre-incident-responder>

[11] Honeycomb, "Honeycomb Advances Observability for AI-Powered Software Development," Mar 2026. (Automated Investigations + Canvas Skills；alert/SLO burn 触发 agent 自调查；可复用 debug playbook.) [Online]. Available: <https://www.honeycomb.io/blog/honeycomb-advances-observability-for-ai-powered-software-development>

[12] Cleric, "Operational Memory for Engineering Teams." (Gartner 2025 Cool Vendor; 20–30% 工程容量释放；Slack-native + confidence + 证据链.) [Online]. Available: <https://cleric.ai/>

[13] Resolve AI, "AI SRE Product Page," 2026. (三 agent 架构、并行多 hypothesis、带 citation 的 RCA 解释、生成 PR / kubectl / scripts.) [Online]. Available: <https://resolve.ai/product/ai-sre>

[14] StackGen, "PagerDuty vs. AI SRE: Why Traditional Incident Response Can't Keep Up," 2026. (Spring 2026 PagerDuty SRE Agent 挂到 escalation policy；agent shell 进 pod / kubectl describe / re-plan.) [Online]. Available: <https://stackgen.com/blog/pagerduty-vs.-ai-sre-why-traditional-incident-response-cant-keep-up>

[15] M. Wiggers, "AI SRE Resolve AI confirms $125M raise, unicorn valuation," *TechCrunch*, Feb 2026. [Online]. Available: <https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/>

[16] Resolve AI, "Resolve AI raises $125M Series A to scale AI for prod," 2026-02. [Online]. Available: <https://resolve.ai/blog/series-a-funding>

[17] Resolve AI, "Series A Extension at $1.5B and Resolve AI Labs," 2026-04. ($40M Series A Extension @ $1.5B; DST Global / Salesforce Ventures.) [Online]. Available: <https://resolve.ai/news/Series-A-extension-and-Resolve-AI-Labs>

[18] Y Combinator, "Parity: The AI SRE for Incident Response." (K8s on-call agent；自动跑 runbook；创始团队来自 Crusoe.) [Online]. Available: <https://www.ycombinator.com/companies/parity>

[19] AWS, "AWS DevOps Agent is now generally available," Mar 2026. (2026-03-31 GA；六区域；CMK / 合规.) [Online]. Available: <https://aws.amazon.com/about-aws/whats-new/2026/03/aws-devops-agent-generally-available/>

[20] incident.io, "5 best AI-powered incident management platforms 2026." (Incident.io AI SRE Slack-native + autonomous investigation + Scribe + post-mortem 草稿.) [Online]. Available: <https://incident.io/blog/5-best-ai-powered-incident-management-platforms-2026>

[21] FireHydrant, "AI-Powered Incident Management." (incident summary / Zoom insight / AI retrospective / status update / Five Whys.) [Online]. Available: <https://docs.firehydrant.com/docs/ai-powered-incident-management>

[22] T. Claburn, "Fixing Claude with Claude: Anthropic reports on AI SRE," *The Register*, Mar 2026. (Anthropic 自家 SRE 公开"先 reach for Claude 而非传统监控".) [Online]. Available: <https://www.theregister.com/2026/03/19/anthropic_claude_sre>

[23] robusta-dev/holmesgpt, GitHub repository. (CNCF Sandbox 2025-10；iterative ReAct loop；K8s / VM / 云 / DB / SaaS.) [Online]. Available: <https://github.com/robusta-dev/holmesgpt>

[24] Panto AI, "GitHub Copilot Statistics 2026 — Users, Revenue & Adoption," 2026. (Copilot ~55% 任务提速、46% 代码由 Copilot 生成；用作上游 Coding Agent 产出规模的参考底线，本篇不再以此外推 L11c 流量。) [Online]. Available: <https://www.getpanto.ai/blog/github-copilot-statistics>
