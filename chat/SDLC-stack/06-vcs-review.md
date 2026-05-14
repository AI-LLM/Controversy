# 2026-05-14：SDLC 栈 / 版本控制与 AI 评审 层深度研究

本篇是「Pre-Coding-Agent vs Post-Coding-Agent 软件开发栈」系列的 D6（版本控制）+ D5/D5'（代码评审）层。范本沿用 namespace.so 范式——不写功能罗列，挖**流量/任务量模式突变 → 新需求 → 解决方案**这条因果链。

---

## 一、Pre-Agent 时代：PR 是「人之间的协议」

PR 这个抽象的隐含假设是：写代码的成本高，所以 PR 数量稀疏；人是稀缺资源，所以 review turnaround 是瓶颈。具体数字：

- **PR 流量**：精英团队人均每周 5 PR 以上 [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)。Google 内部中位数作者每周提交约 3 changes，80 分位约 7 changes/周 [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)。Lyst 公开数据：中位开发者每周开 3 PR，80% 开发者 ≤ 5 PR/周 [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)。
- **Review turnaround**：2024 大公司中位工程师 merge 一个 PR 大约要 13 小时，其中绝大多数时间在等 review [[2]](https://graphite.com/guides/tracking-improving-code-review-turnaround)。LinearB / Sleuth 行业基线 time-to-first-review 中位数 7–12 小时，time-to-merge 中位数 24–48 小时 [[2]](https://graphite.com/guides/tracking-improving-code-review-turnaround)。Google 平均 review 4 小时 [[3]](https://www.michaelagreiler.com/code-reviews-at-google/)。
- **时间占比**：精英团队每周 review 15+ PR，merge 90%+ PR 在 24 小时内 [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)。Meta 内部数据：评审是 change lead time 中最大的延迟来源 [[4]](https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/)。

在这个数量级里，PR 是「写完—贴出—等人—评论—改—合并」的同步会议。一周 5 PR、一审 7 小时、一改 1–2 轮，全公司能扛得住。

## 二、Post-Agent 流量突变：Agent 写得快，人审不动了

Cursor 团队公开的因果推断研究：把 Background Agent 当默认工作流的公司，**周合并 PR 数比对照组高 39%** [[5]](https://leaddev.com/ai/cursor-claims-its-tools-are-a-massive-productivity-hack-for-devs)。研究覆盖 24 组实验 / 8 组对照、约 1,000 组织、数万开发者，未观察到 revert rate 显著上升 [[5]](https://leaddev.com/ai/cursor-claims-its-tools-are-a-massive-productivity-hack-for-devs)。Devin 在 2025 年的 PR merge 率从 34% 提升到 67% [[6]](https://docs.devin.ai/release-notes/2026)，意味着自治 Agent 提交的 PR 中三分之二最终进入主分支——单个 Agent 实例 24 小时不停，提 PR 速度远超任何人。

DORA 2024–2025 同一时期的报告抓到了另一面：当 AI 把代码产出抬高约 30% 而 review 容量不变时，PR 体积变大、review 时间延长、问题漏检概率上升 [[7]](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025)。

⚠ **流量本质变化**：

- 写端的边际成本从「工程师小时」掉到「LLM tokens」——单价掉两个数量级；
- 审端依旧是「工程师小时」——单价没动；
- PR 是连接两端的协议，一边在指数膨胀，一边在线性配额，**夹在中间的人 review 必然成为瓶颈**。

新范式必须做的两件事：(1) 让 Agent 审 Agent 写的 PR；(2) 把人从「行级评论」拉到「策略级把关」。

## 三、CodeRabbit：Astute Review + Code Graph 的统一抽象

CodeRabbit 是当前 Agent-on-Agent 评审的事实标准。流量证据：2026 年初已接入 **2M+ 仓库、处理 13M+ PR、8,000+ 付费客户**，客户包括 Chegg、Groupon、Life360、Mercury [[8]](https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews)。2025-09 完成 Series B $60M，估值 $550M，累计 $88M [[8]](https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews)。

技术架构有三层 [[9]](https://www.infoworld.com/article/4025088/how-coderabbit-brings-ai-to-code-reviews.html), [[10]](https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering)：

1. **Static analysis 子层**：内置数十种 linter、CodeQL、ast-grep 规则，把结构化结果当作 prompt 上下文喂给 LLM。
2. **Code Graph 子层**：解析整个仓库构造依赖图，跨文件追踪函数引用——这是「astute review」的关键，让 LLM 能看到一处 diff 在远端文件触发的 contract 破坏。
3. **Context Engineering**：CodeRabbit 自称在 prompt 里维持 **1:1 的 code-to-context 比例**——diff 旁边塞上 Jira ticket、past PR、code graph、linter 输出、过往 chat learning [[10]](https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering)。底层用 LanceDB 做毫秒级语义检索，索引数万张 PR / issue / 依赖表 [[11]](https://www.lancedb.com/blog/case-study-coderabbit)。

集成面：Jira / Linear 验证 PR 是否真的解决 issue；Slack Agent 处理 triage、事故响应、release summary、codebase Q&A [[12]](https://www.coderabbit.ai/blog/how-to-use-coderabbit-to-validate-issues-against-linear-board)。

**配置示例**（`.coderabbit.yaml`）[[13]](https://docs.coderabbit.ai/guides/review-instructions)：

```yaml
language: en-US
reviews:
  profile: chill         # or "assertive"
  request_changes_workflow: true
  high_level_summary: true
  poem: false
  auto_review:
    enabled: true
    drafts: false
  path_filters:
    - "!**/vendor/**"
    - "!**/*.generated.ts"
  path_instructions:
    - path: "src/**/*.ts"
      instructions: "Enforce Google TypeScript style; flag any use of `any`."
    - path: "tests/**/*.spec.ts"
      instructions: "Mocha tests must have descriptive test names; no skipped suites."
  tools:
    ast-grep:
      rules_dir: [".coderabbit/rules"]
      util_dirs: [".coderabbit/utils"]
      packages: ["@coderabbit/security-ts"]
chat:
  auto_reply: true
integrations:
  jira:
    project_keys: ["ENG", "PLAT"]
  linear:
    team_keys: ["CORE"]
```

定价（2026）[[14]](https://www.coderabbit.ai/pricing)：Lite $12/dev/月（年付）、Pro $24/dev/月（年付，月付 $30）、Pro+ $48/dev/月（年付，月付 $60）。仅对**实际开 PR 的开发者计费**，不开 PR 不收钱。

## 四、Greptile：跨文件深审，监控召回而非精度

Greptile 的差异化是「先把整个 repo 索引成图，再审 PR」——更适合 monorepo 和跨文件破坏。公开 benchmark：50 个真实 bug 测试集，**Greptile 82% catch / CodeRabbit 44% catch**，但 Greptile 误报 11 条、CodeRabbit 仅 2 条 [[15]](https://www.greptile.com/benchmarks)。这是一道明确的产品哲学分叉：**召回优先 vs 精度优先**。

定价采用 API 计量 [[16]](https://docs.greptile.com/pricing)：

- `POST /query` 1 unit = $0.15；`genius=true`（更大模型）3 units；
- PR Review Bot：$0.45 / file changed，封顶 $50/开发者/月，超过封顶部分免费；新用户赠 150 units。

适用判据：复杂代码库、跨文件破坏频发、宁可多看噪音也不愿漏 bug 的团队选 Greptile；signal-to-noise 至上的团队选 CodeRabbit。

## 五、Graphite Diamond / Agent：Stacked PR + 行级 reviewer

Graphite 2025-03 推出 Diamond 独立产品，宣示「AI 永远不会替代人 review」[[17]](https://www.devclass.com/ai-ml/2025/03/19/graphite-debuts-diamond-ai-code-reviewer-insists-ai-will-never-replace-human-code-review/1626959)；2025-10-08 把 Diamond 并入 **Graphite Agent**，把 AI 评审与 stacked PR 工作流统一 [[18]](https://graphite.com/blog/introducing-graphite-agent-and-pricing)。核心论点：**大 PR 不可审，必须 stack 成小 PR**——这是把「PR 体积膨胀」这个 Agent-after 顽症在协议层解掉，而不是靠 reviewer 加班。Series B $52M [[19]](https://graphite.com/blog/series-b-diamond-launch)。

## 六、其它玩家速览

- **Korbit AI**：GitHub/GitLab/Bitbucket 三端 PR review bot，10 种语言；Korbit Pro $24/user/月，开源免费；卖点是「senior 级反馈、保证不拿你的代码训练」[[20]](https://onlinetoolstack.com/korbit-ai)。
- **Aviator**：merge queue 起家，$12/user/月，支持 monorepo 并行队列、flaky test 容忍策略（`optimistic_validation_failure_depth`）[[21]](https://www.aviator.co/aviator-mergequeue-mergify)。
- **Mergify**：merge queue + CI Insights + Merge Protections 全捆绑 $21/user/月，覆盖 PR 依赖、定时合并、跨 repo 协调 [[21]](https://www.aviator.co/aviator-mergequeue-mergify)。两家是「PR 流量爆发后的合并层」防线。

## 七、GitLab 为什么输：一站式叙事被 best-of-breed 解构

GTLB 2025 全年 −33%，2026 初继续探底，距 52 周高点 $53.43 下挫 62.8% [[22]](https://www.fool.com/investing/2026/01/20/why-gitlab-stock-lost-33-in-2025/)。指责对象包括：净新增客户跌至四年低点、NRR 下行、AI 工具激增导致平台相关性受冲击 [[23]](https://www.benzinga.com/trading-ideas/movers/26/05/52491665/gitlab-stock-tumbles-amid-ai-linked-restructuring)。GitLab Duo Agent Platform 在 2025–2026 持续加码（Planner / Security Analyst / Data Analyst Agent，模型选择 GA、CI Pipeline Agent）[[24]](https://about.gitlab.com/gitlab-duo-agent-platform/), [[25]](https://www.businesswire.com/news/home/20260416605834/en/GitLab-Extends-Agentic-AI-with-New-Automated-Security-Remediation-Pipeline-Setup-and-Delivery-Analytics)，但叙事失败的本质是：**一站式 DevSecOps 单一应用**这条 2021 年的卖点，挡不住 Cursor（写）+ CodeRabbit / Greptile（审）+ Linear（issue）+ Aviator（合）的 best-of-breed 拼盘——每一层都更专、更快、定价更激进。GTLB 的 Act 2 重组（裁员 + 组织调整）被市场读作「执行风险」[[26]](https://www.quiverquant.com/news/GitLab+shares+fall+on+restructuring+plans+and+renewed+execution+worries)。

## 八、GitHub 怎么守：Microsoft 三占的反脆弱

GitHub 的位置不可替代，因为 Microsoft 同时占 **GitHub（仓库）+ Copilot（IDE/Chat/Coding Agent）+ VS Code（编辑器）+ Azure（推理）** 四个层。守势布局：

- **Copilot Autofix**：2025 修复了超过 100 万个漏洞；CodeQL 覆盖扩展后 autofix 可用 alert 增加 8%，扩展组内 autofix 数量增长 270% [[27]](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/)。
- **Copilot Code Review**：2025-10 Public Preview 把 LLM 检测 + tool calling + ESLint / CodeQL 等确定性工具混合，且能把建议「一键传给 Copilot Coding Agent」直接开新 PR 修 [[27]](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/)。
- **Copilot Workspace**：55,000+ 开发者用过、10,000+ PR 已合并；加了 build-and-repair agent、brainstorming 模式、VS Code 集成 [[28]](https://github.blog/changelog/2025-01-06-copilot-workspace-changelog-january-6-2025/)。
- **GitHub Spark**：自然语言到部署应用（Claude Sonnet 4 驱动），2025-07 起对 Copilot Pro+ 开放、2025-09 对 Copilot Enterprise 开放；可直接生成带 Actions / Dependabot 的 repo，并衔接 Copilot Coding Agent 在 codespace 继续迭代 [[29]](https://github.blog/changelog/2025-07-23-github-spark-in-public-preview-for-copilot-pro-subscribers/), [[30]](https://github.blog/changelog/2025-09-30-github-spark-in-public-preview-for-copilot-enterprise-subscribers/)。

反脆弱的关键不是单点最强，而是**任意一层被 best-of-breed 拆掉，其它三层仍在分发流量**——GitHub 是写入端，VS Code 是编辑端，Azure 是底座，Copilot 在四端拉通。CodeRabbit / Greptile 越火，GitHub Marketplace 越值钱。

## 九、新需求：流量爆炸时代的次生市场

PR 流量从「人发的稀疏事件」变成「Agent 发的密集流」之后，长出几条新需求线：

1. **AI-generated PR 标记**：reviewer 需要立刻知道 diff 是 Agent 写的还是人写的，以决定关注力分配。GitHub 已在 PR metadata 暴露 Copilot Coding Agent 来源。
2. **Trust Score per PR**：在 PR 上叠加一个 0–10 的可信度评分，综合静态分析、测试覆盖、依赖影响、Agent 来源、过往 revert 概率。Credo AI / Fiddler / Tumeryk 等 trust-score 框架已在通用 LLM 安全侧落地 [[31]](https://www.credo.ai/model-trust-scores-ai-evaluation), [[32]](https://docs.fiddler.ai/reference/glossary/trust-score)，PR 层等同 schema 即将出现。
3. **回归风险评估**：Greptile 的跨文件 graph 本质就是干这件事——「这个 diff 对远端 contract 的破坏概率」。
4. **合规审计**：SOC 2 CC8.1 明确要求**所有代码变更（含 AI 生成）部署前必须有人审批**，且要留 change request、approver signature、测试证据 [[33]](https://www.augmentcode.com/tools/ai-coding-tools-soc2-compliance-enterprise-security-guide), [[34]](https://www.codeant.ai/blogs/github-ai-code-review-tools-soc2-compliance)。CC6.1 把这个延伸到生产合并。这条监管事实直接锁死了「全自动 Agent 合并」的天花板——人不能完全退出。

## 十、几条本质判断

**(1) PR 抽象不会消失，但语义在迁移**。Pre-Agent 时代 PR = 「人提交的工作单元」；Post-Agent 时代 PR = 「待审的 diff 包，作者可以是 Agent」。语义从「沟通载体」滑向「策略闸门」。

**(2) Agent 写 → Agent 审在技术上已经成立，但在合规上不成立**。CodeRabbit 13M PR 的吞吐证明了 LLM 评审能扛流量；Greptile 82% 召回证明了能抓 bug。但 SOC 2 / ISO 27001 等强制人作为「final approver」，所以未来形态是 **Agent 写 → Agent 审 → 人按策略批一批**，而不是「全自动直合」。人退到「批量决策 + 异常处理」这一层。

**(3) Stacked PR 是协议层修复方案**。Graphite 在做的事不是「让 AI 更聪明」，而是「让 PR 更小」——把流量爆炸前置切成可审小块，符合 Pre-Agent 时代的 human-review 节奏。这是迄今最务实的桥接。

**(4) GitLab 一站式叙事破产是 best-of-breed 复辟的样本**。当每一层都有 10× 单点产品时，「单一应用」从优势变成包袱。GTLB 不是输给 GitHub，是输给了 CodeRabbit + Cursor + Linear + Aviator 这种**可拼装的组合**。

**(5) GitHub 的护城河是分发，不是产品**。Copilot Code Review 不必比 CodeRabbit / Greptile 更强——它在每个仓库默认弹出，这本身就是 60% 的胜率。CodeRabbit 在 GitHub Marketplace 上是「最多人装的 AI 应用」[[8]](https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews) 这条事实，恰恰证明 GitHub 是租金收取方。

---

## 参考文献

[1] minware, "Average PRs Merged Per Developer," 2024. (Elite teams: 5+ PR/dev/week; Google median: 3 changes/week, 80th pct 7; Lyst median: 3 PR/week.) [Online]. Available: <https://www.minware.com/guide/metrics/average-prs-merged-per-developer>

[2] Graphite, "Tracking and improving code review turnaround time," 2024. (Median time-to-first-review 7–12h; time-to-merge 24–48h; large-company median 13h to merge.) [Online]. Available: <https://graphite.com/guides/tracking-improving-code-review-turnaround>

[3] M. Greiler, "Code Reviews at Google are lightweight and fast," 2023. (Avg 4h, small changes <1h.) [Online]. Available: <https://www.michaelagreiler.com/code-reviews-at-google/>

[4] Meta Engineering, "Move faster, wait less: Improving code review time at Meta," Nov. 2022. [Online]. Available: <https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/>

[5] LeadDev, "New study suggests major productivity boost when using Cursor's coding agent," 2025. (Cursor agent default: +39% weekly merged PRs; 24 vs 8 orgs; ~1,000 orgs sampled.) [Online]. Available: <https://leaddev.com/ai/cursor-claims-its-tools-are-a-massive-productivity-hack-for-devs>

[6] Cognition, "Devin Release Notes 2026," 2026. (PR merge rate 34% → 67% during 2025.) [Online]. Available: <https://docs.devin.ai/release-notes/2026>

[7] Faros AI, "DORA Report 2025 Key Takeaways: AI Impact on Dev Metrics," 2025. (+30% code output with flat review capacity → longer review, more misses.) [Online]. Available: <https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025>

[8] CodeRabbit, "Raising our $60 million Series B: Quality gates for AI coding," Sep. 2025. (2M+ repos, 13M+ PRs, 8,000+ paying customers, $550M valuation, $88M total funding.) [Online]. Available: <https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews>

[9] InfoWorld, "How CodeRabbit brings AI to code reviews," 2025. [Online]. Available: <https://www.infoworld.com/article/4025088/how-coderabbit-brings-ai-to-code-reviews.html>

[10] CodeRabbit, "The art and science of context engineering," 2025. (1:1 code-to-context ratio in LLM prompts.) [Online]. Available: <https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering>

[11] LanceDB, "Case Study: How CodeRabbit Leverages LanceDB for AI-Powered Code Reviews," 2025. (Millisecond semantic search across tens of thousands of tables; millions of daily code interactions.) [Online]. Available: <https://www.lancedb.com/blog/case-study-coderabbit>

[12] CodeRabbit, "How to use CodeRabbit to validate issues against Linear Board," 2024. [Online]. Available: <https://www.coderabbit.ai/blog/how-to-use-coderabbit-to-validate-issues-against-linear-board>

[13] CodeRabbit Docs, "Review Instructions," 2026. [Online]. Available: <https://docs.coderabbit.ai/guides/review-instructions>

[14] CodeRabbit, "Pricing," 2026. (Lite $12, Pro $24, Pro+ $48 per dev/month annual; billed only for devs who open PRs.) [Online]. Available: <https://www.coderabbit.ai/pricing>

[15] Greptile, "Benchmarks," 2025. (50-bug test set; Greptile 82% catch / 11 false positives; CodeRabbit 44% catch / 2 false positives.) [Online]. Available: <https://www.greptile.com/benchmarks>

[16] Greptile Docs, "Pricing," 2026. ($0.15/unit; genius=true 3 units; PR bot $0.45/file changed capped at $50/dev/month; 150 free units.) [Online]. Available: <https://docs.greptile.com/pricing>

[17] DEVCLASS, "Graphite debuts Diamond AI code reviewer, insists 'AI will never replace human code review'," Mar. 2025. [Online]. Available: <https://www.devclass.com/ai-ml/2025/03/19/graphite-debuts-diamond-ai-code-reviewer-insists-ai-will-never-replace-human-code-review/1626959>

[18] Graphite, "Meet Graphite Agent: the next evolution of AI code review," Oct. 2025. (Diamond merged into Graphite Agent 2025-10-08.) [Online]. Available: <https://graphite.com/blog/introducing-graphite-agent-and-pricing>

[19] Graphite, "Series B and Diamond Launch," 2025. ($52M Series B.) [Online]. Available: <https://graphite.com/blog/series-b-diamond-launch>

[20] Online Tool Stack, "Korbit AI Details, Pricing, Features, and Alternatives 2026," 2026. (Pro $24/user/month, free for open source; 10 languages.) [Online]. Available: <https://onlinetoolstack.com/korbit-ai>

[21] Aviator, "MergeQueue vs. Mergify: A Comparison," 2025. (Aviator $12/user/month, Mergify $21/user/month; optimistic_validation_failure_depth for flaky tests.) [Online]. Available: <https://www.aviator.co/aviator-mergequeue-mergify>

[22] Motley Fool, "Why GitLab Stock Lost 33% in 2025," Jan. 2026. (FY2025 −33%; net new customer additions at four-year low; NRR decline.) [Online]. Available: <https://www.fool.com/investing/2026/01/20/why-gitlab-stock-lost-33-in-2025/>

[23] Benzinga, "GitLab Stock Tumbles Amid AI-Linked Restructuring," May 2026. (62.8% below 52-week high of $53.43.) [Online]. Available: <https://www.benzinga.com/trading-ideas/movers/26/05/52491665/gitlab-stock-tumbles-amid-ai-linked-restructuring>

[24] GitLab, "GitLab Duo Agent Platform," 2026. (Planner / Security Analyst / Data Analyst / CI Pipeline Agent; model selection GA in 18.4.) [Online]. Available: <https://about.gitlab.com/gitlab-duo-agent-platform/>

[25] BusinessWire, "GitLab Extends Agentic AI with New Automated Security Remediation, Pipeline Setup, and Delivery Analytics," Apr. 2026. [Online]. Available: <https://www.businesswire.com/news/home/20260416605834/en/GitLab-Extends-Agentic-AI-with-New-Automated-Security-Remediation-Pipeline-Setup-and-Delivery-Analytics>

[26] QuiverQuant, "GitLab shares fall on restructuring plans and renewed execution worries," 2025. [Online]. Available: <https://www.quiverquant.com/news/GitLab+shares+fall+on+restructuring+plans+and+renewed+execution+worries>

[27] GitHub Blog, "New public preview features in Copilot code review: AI reviews that see the full picture," Oct. 28 2025. (Autofix fixed 1M+ vulnerabilities in 2025; CodeQL expansion +8% autofix coverage / +270% within group; tool calling + ESLint + CodeQL hybrid.) [Online]. Available: <https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/>

[28] GitHub Blog, "Copilot Workspace Updates (January 6, 2025)," Jan. 2025. (55,000+ developers used Copilot Workspace; 10,000+ PRs merged.) [Online]. Available: <https://github.blog/changelog/2025-01-06-copilot-workspace-changelog-january-6-2025/>

[29] GitHub Blog, "GitHub Spark in public preview for Copilot Pro+ subscribers," Jul. 23 2025. (Claude Sonnet 4–powered; generates repo with Actions + Dependabot.) [Online]. Available: <https://github.blog/changelog/2025-07-23-github-spark-in-public-preview-for-copilot-pro-subscribers/>

[30] GitHub Blog, "GitHub Spark in public preview for Copilot Enterprise subscribers," Sep. 30 2025. [Online]. Available: <https://github.blog/changelog/2025-09-30-github-spark-in-public-preview-for-copilot-enterprise-subscribers/>

[31] Credo AI, "Model Trust Scores: Evaluating AI Models," 2025. [Online]. Available: <https://www.credo.ai/model-trust-scores-ai-evaluation>

[32] Fiddler, "Trust Score Reference," 2025. (Numerical assessment across safety / toxicity / faithfulness / relevance / coherence.) [Online]. Available: <https://docs.fiddler.ai/reference/glossary/trust-score>

[33] Augment Code, "AI Coding Tools SOC2 Compliance: Enterprise Security Guide," 2025. (SOC 2 change management requires AI-generated code follow same review/approval as human-written code.) [Online]. Available: <https://www.augmentcode.com/tools/ai-coding-tools-soc2-compliance-enterprise-security-guide>

[34] CodeAnt AI, "GitHub AI Code Review Tools Built for SOC 2 Audits," 2025. (CC6.1 / CC8.1 require qualified reviewer approval per change with change request + testing evidence.) [Online]. Available: <https://www.codeant.ai/blogs/github-ai-code-review-tools-soc2-compliance>
