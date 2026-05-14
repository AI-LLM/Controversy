# 2026-05-14：SDLC 栈 / AI 代码评审 (D5') 层深度研究

本篇 lens：**signable signal generation（可签字信号生产）**——AI 代码评审层卖的不是 diff 吞吐，而是把 Agent 写出的密集 diff 流压缩成组织敢落章的离散判断单元。

---

## 一、AI 评审卖的是"可签字的信号"

PR approve 这一票之所以稀缺，不是因为读 diff 慢，而是因为它**是组织对外可签字的最小信号**：出 bug、出合规问题、出 incident 时，approve 是责任链回溯的第一个 hop。AI 评审层的产品本质——**为每个 diff 生产一个能被签字的判断**。

底层流量与延迟基线：

- **PR 流量**：精英团队人均每周 5+ PR [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)；Google 内部中位每周 3 changes、80 分位 7 [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)；Lyst 公开中位 3 PR/周 [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)。
- **Review turnaround**：2024 大公司中位工程师 merge 一个 PR 约 13 小时，绝大多数时间在等 review [[2]](https://graphite.com/guides/tracking-improving-code-review-turnaround)；行业基线 time-to-first-review 中位 7–12h、time-to-merge 中位 24–48h [[2]](https://graphite.com/guides/tracking-improving-code-review-turnaround)；Google 内部 review 平均 4h [[3]](https://www.michaelagreiler.com/code-reviews-at-google/)。
- **占工时**：Meta 内部数据显示评审是 change lead time 中**最大的延迟来源** [[4]](https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/)。

一周 5 PR、一审 7h、一改 1–2 轮，全公司能扛住的不只是流量，是**每个判断单元的颗粒度恰好匹配人的注意力 budget**（⚠ 解读，综合 [[1]][[2]] 中位数复述）。

## 二、流量突变：写端单价掉两个数量级，信号生产成为唯一瓶颈

Cursor 2025 公开的因果推断研究：把 Background Agent 设为默认工作流的公司，**周合并 PR 比对照组高 39%**（24 组实验 / 8 组对照、约 1,000 组织），未观察到 revert rate 显著上升 [[5]](https://leaddev.com/ai/cursor-claims-its-tools-are-a-massive-productivity-hack-for-devs)。Devin 2025 期间 PR merge 率从 **34% → 67%** [[6]](https://docs.devin.ai/release-notes/2026)，单实例可 24×7 不停发 PR。DORA 2024–2025：AI 把代码产出抬高约 30% 而 review 容量不变时，PR 体积变大、review 时间延长、漏检概率上升 [[7]](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025)。

把这些数字收敛成**一句论点**（作者解读，依据 [[5]][[6]][[7]]）：

> **写端的边际成本从「工程师小时」掉到「LLM tokens」——单价掉两个数量级；审端的判断仍只能由"能签字的主体"产出，单价没动。** PR 是连接两端的协议，一边指数膨胀，一边线性配额。

⚠ 这条**不是流量瓶颈**问题，而是**信号生产瓶颈**问题——单位时间能生产多少"可签字判断"，是 D5' 全部产品的真正约束。所有后续技术分叉，都是在回答"如何在 diff 单价掉两个量级后，仍然产出形状合适的信号"。

## 三、信号形状的五条分叉：召回型 / 精度型 / 颗粒型 / 窄域型 / 多维型

D5' 厂商不在同一道题上竞争。他们在生产**不同形状的信号**，每种形状服务一类下游签字者（reviewer / 安全官 / merge queue / on-call）。把代表公司按信号形状重排：

### 3.1 高精度低噪音信号 — CodeRabbit

CodeRabbit 2026 初已接入 **2M+ 仓库、处理 13M+ PR、8,000+ 付费客户**，含 Chegg、Groupon、Life360、Mercury；2025-09 Series B $60M、估值 $550M、累计 $88M [[18]](https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews)。第三方 OpenSSF CVE Benchmark：CodeRabbit 准确率 59.39% / F1 36.19%，漏检约 41% 真实漏洞 [[25]](https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests)；Greptile 自家 benchmark 中 CodeRabbit 44% catch、仅 2 false positives [[24]](https://www.greptile.com/benchmarks)。

**信号形状**：每条评论都倾向于"reviewer 看了不删"——靠**低 FP** 换取 reviewer 在 LGTM 前对该 bot 的注意力 budget。技术架构三层 [[19]](https://www.infoworld.com/article/4025088/how-coderabbit-brings-ai-to-code-reviews.html), [[20]](https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering)：static analysis（CodeQL、ast-grep）作 prompt context；Code Graph 跨文件追踪契约破坏；Context Engineering 维持 **1:1 code-to-context 比例**，diff 旁塞 Jira ticket、past PR、linter 输出、chat learning [[20]](https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering)。底层 LanceDB 毫秒级语义检索数万张 PR / 依赖表 [[21]](https://www.lancedb.com/blog/case-study-coderabbit)。

**配置示例**（`.coderabbit.yaml`）[[22]](https://docs.coderabbit.ai/guides/review-instructions) ——profile / path_instructions 是"信号刻度"的可调参数：

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

定价 [[23]](https://www.coderabbit.ai/pricing)：Lite $12 / Pro $24 / Pro+ $48 per dev/月（年付）；**仅对实际开 PR 的开发者计费**——这条 SKU 设计直接对应"按签字单价计价"的逻辑。

### 3.2 高召回宽噪音信号 — Greptile

Greptile 公开 benchmark：50 个真实 bug 测试集，**Greptile 82% catch / CodeRabbit 44% catch**，Greptile 误报 11 条、CodeRabbit 仅 2 条 [[24]](https://www.greptile.com/benchmarks)。

**信号形状**：故意拉高召回，让人 reviewer **接受"我会看到噪音"作为代价**——服务的下游不是 LGTM 而是安全官 / 合规审。先把整个 repo 索引成图再审 PR，更适合 monorepo 跨文件破坏。定价按用量计 [[26]](https://docs.greptile.com/pricing)：`POST /query` 1 unit = $0.15；`genius=true` 3 units；PR Review Bot **$0.45 / file changed**，封顶 $50/dev/月，新用户赠 150 units——**按 file changed 计价 = 按"信号生产量"计价**，与 CodeRabbit 的"按签字者计价"形成对照。部署 [[27]](https://www.greptile.com/docs/self-hosting/overview)：Docker Compose / K8s 自托管，覆盖 AWS / GCP / Azure / air-gapped；LLM provider 可换；Hosted API base URL `https://api.greptile.com/v2/`。这条 air-gapped 路线服务金融 / 政府 / 国防客户——这些客户的签字主体本来就习惯翻噪音。

### 3.3 小颗粒可审信号 — Graphite Diamond / Agent

Graphite 2025-03 推 Diamond 时明确"AI will never replace human code review"[[28]](https://www.devclass.com/ai-ml/2025/03/19/graphite-debuts-diamond-ai-code-reviewer-insists-ai-will-never-replace-human-code-review/1626959)；2025-10-08 把 Diamond 并入 **Graphite Agent**，统一 AI 评审与 stacked PR 工作流 [[29]](https://graphite.com/blog/introducing-graphite-agent-and-pricing)；Series B $52M [[30]](https://graphite.com/blog/series-b-diamond-launch)。核心论点：**大 PR 不可审，必须 stack 成小 PR**。

**信号形状**：Graphite 不是改 LLM 怎么评，而是**改信号本身的颗粒度**——把"一个无法签字的大 PR"拆成"五个能签字的小 PR"。这是把 D5' 的瓶颈在**协议层**解决，而不是在 LLM 层。2026 定价 [[29]](https://graphite.com/blog/introducing-graphite-agent-and-pricing)：Free / Starter $20 / Team $40 / Enterprise。客户证据：Shopify stacked PR 后**人均 merge PR +33%**；Asana 工程师每周省 7h、产出 +21% [[29]](https://graphite.com/blog/introducing-graphite-agent-and-pricing)（⚠ 厂商自报，未见第三方独立复核）。

### 3.4 窄域高确定性信号 — Cursor Bugbot

Cursor Bugbot 2026 早期**月处理 2M+ PR、累计 review 1M+ PR、标记 1.5M issue，70%+ flag 在 merge 前被解决** [[34]](https://cursor.com/bugbot)。

**信号形状**：故意做窄。只抓 logic bug / 安全漏洞 / race condition / null deref / 错误处理；**主动忽略**格式 / 风格 / 低优——每条 flag 自带"这不是 nit，是 bug"的语义承诺。2026-02 Bugbot Autofix：云端 VM spawn agent 修自己抓到的问题；Bugbot 还从 reviewer 反应（downvote / 回复 / 同 PR 人审评论）学习规则，累积成 active rule，负反馈过多自动退役 [[34]](https://cursor.com/bugbot)。定价 $40/user/月、按 contributor seat 计——20 人团队仅 Bugbot 一项 $800/月 [[34]](https://cursor.com/bugbot)。Cursor 在自己产品矩阵内闭环"Agent 写 → Agent 审"。

### 3.5 多维度并行信号 — Qodo

Qodo 由 CodiumAI 2024 更名而来 [[31]](https://en.wikipedia.org/wiki/Qodo)。2026-02 **Qodo 2.0** 把单次 LLM 评审拆成多 Agent 并行：一个抓 bug、一个查质量、一个做安全、一个看测试覆盖；benchmark F1 **60.1%**、recall 56.7%，在 7 厂对比中最高 [[32]](https://aicodereview.cc/blog/qodo-review/)。

**信号形状**：在同一个 PR 上**同时产出多种维度的判断**，下游签字者按维度分流（安全维度走 AppSec、覆盖率维度走 QA、bug 维度走 reviewer）。开源核心 PR-Agent 支持 GitHub / GitLab / Bitbucket / Azure DevOps / CodeCommit / Gitea，可自托管 / air-gapped / 审计 prompt [[33]](https://github.com/qodo-ai/pr-agent)；从 CodiumAI 时代继承的测试生成能力（带断言和边界用例的 unit test，不是 stub）也作为"测试维度信号"嵌入 [[31]](https://en.wikipedia.org/wiki/Qodo)。

### 3.6 自动修复信号 — Pixee（信号即 patch）

Pixee 安全侧 PR remediation：100,000+ PR 实测达到 **76% developer merge rate**，scanner-alert-to-merge 中位时间从行业平均 252 天压到 < 48h；声称消除 95%+ 误报 [[37]](https://www.pixee.ai/), [[38]](https://www.pixee.ai/blog/pixee-wins-2026-devies-award-appsecops)。

**信号形状**：信号不是评论，**是一个直接可 merge 的 patch**——把"需要 reviewer 签字的判断单元"压缩成"reviewer 只需 approve 一个一键 patch"。在五种形状里最激进：它假设下游签字者真正稀缺的不是判断，是**写补丁的工时**。

### 3.7 边缘玩家速览（信号形状未独立成型）

- **Korbit AI** [[35]](https://onlinetoolstack.com/korbit-ai)：GitHub/GitLab/Bitbucket 三端 PR review bot；Korbit Pro $24/user/月、开源免费；卖点"senior 级反馈、不拿代码训练"。
- **Aviator / Mergify** [[36]](https://www.aviator.co/aviator-mergequeue-mergify)：merge queue 起家；Aviator $12/user/月、monorepo 并行队列、`optimistic_validation_failure_depth` 容忍 flaky test；Mergify $21/user/月、merge queue + CI Insights + Merge Protections 捆绑。**这两家不是信号生产者，而是"信号消费协议层"**——后文 §4 展开。
- **GitHub Copilot Code Review** [[39]](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/)：2025-10 Public Preview，LLM + tool calling + ESLint / CodeQL 混合，建议可一键传给 Copilot Coding Agent 修；Copilot Autofix 2025 全年修复 1M+ 漏洞。
- **GitLab Duo Code Review** [[40]](https://docs.gitlab.com/user/gitlab_duo/code_review/), [[41]](https://docs.gitlab.com/user/duo_agent_platform/flows/foundational_flows/code_review/)：非 agentic 在 18.1 GA；agentic Code Review Flow 18.7 beta、**18.8 GA**（2026-01）；18.10 Free tier 开放。

## 四、信号如何被消费：合规签字、协议层吸收、人审策略化

§3 是"生产端"，本节是"消费端"。三种信号下游消费模式：

**(1) 合规签字 — 给信号盖章的法律必要性**。SOC 2 CC8.1 明确要求**所有代码变更（含 AI 生成）部署前必须有人审批**，并留 change request、approver signature、测试证据 [[14]](https://www.augmentcode.com/tools/ai-coding-tools-soc2-compliance-enterprise-security-guide), [[15]](https://www.codeant.ai/blogs/github-ai-code-review-tools-soc2-compliance)；CC6.1 把这条延伸到生产合并。这条监管事实直接锁死"全自动 Agent 直合"的天花板——人不能完全退出。CodeRabbit 2025 完成 SOC 2 Type II 第三方审计（年度续审），仓库代码在内存中 clone 完成评审后立即丢弃，可选缓存 ≤7 天或完全关闭；Enterprise（≥500 seats）可全自托管；存储同时符合 GDPR / HIPAA [[16]](https://trust.coderabbit.ai/compliance), [[17]](https://coderabbit.ai/changelog/coderabbit-is-now-soc-2-type-ii-compliant)。⚠ **合规不是 D5' 的卖点，是 D5' 信号的最终落地约束**——所有信号最终都得能塞进 SOC 2 审计的 change ticket。

**(2) 协议层吸收 — merge queue 把信号转 commit**。Aviator / Mergify 的角色不是生产信号，是**消费一束信号后产生 commit**：merge queue 把"通过 CI + 通过 CodeRabbit + 通过 Bugbot + 通过 reviewer LGTM"折叠成单一"可入主"决策 [[36]](https://www.aviator.co/aviator-mergequeue-mergify)。当 D5' 信号源数量增加，merge queue 是把它们重新串成一根决策线的必要协议层。

**(3) 人审策略化 — AI-PR 标记 + Trust Score**。reviewer 不再读 diff，而是读"这条信号信吗"。两条配套基础设施在 2026 显形：

- **AI 来源标记**：GitHub 在 PR metadata 暴露 Copilot Coding Agent 来源——PR author / commit author 显示为 Copilot bot，commit trailer 加 `Co-authored-by: Copilot <copilot@github.com>` [[8]](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent), [[9]](https://github.com/orgs/community/discussions/179983)。学术界 2026 用行为指纹做归因——XGBoost 在 33,580 个 PR 上对五大 Agent 的归属判定达到 97.2% F1 [[10]](https://arxiv.org/html/2601.17406v1)。欧盟 AI Act 第 113 条 **2026-08-02 起**所有"职业发布的 AI 生成内容"需带 C2PA 元数据（Provider Name / System Version / Creation Timestamp / Unique Identifier）[[11]](https://weventure.de/en/blog/ai-labeling)——这条法规会反向倒逼 PR 层加结构化标记。
- **Trust Score**：给 PR 叠 0–10 可信度评分，综合静态分析、测试覆盖、依赖影响、Agent 来源、过往 revert 概率。Credo AI / Fiddler 等 trust-score 框架已在通用 LLM 安全侧落地 [[12]](https://www.credo.ai/model-trust-scores-ai-evaluation), [[13]](https://docs.fiddler.ai/reference/glossary/trust-score)；PR 层等同 schema 即将出现（⚠ 截至 2026-05 尚无主流 D5' 厂商公开发布独立 "PR Trust Score" schema，作者将其列为次生市场而非现状）。

## 五、几条本质判断

**(1) PR 抽象不会消失，但语义在迁移**。Pre-Agent：PR = "人提交的工作单元"；Post-Agent：PR = "待审的 diff 包，作者可以是 Agent"。语义从"沟通载体"滑向"策略闸门"——闸门控制的不是流量，是**信号信任度的分桶**。

**(2) 召回 vs 精度不是技术问题，是信号形状问题**。Greptile（82% / 11 FP）服务"漏一个 bug 死人"的安全签字者；CodeRabbit（44% / 2 FP）服务"reviewer 注意力 budget"的工程 LGTM 签字者。两者下游是不同人。Qodo 多 Agent 路线试图在同一个 PR 上**同时产多种形状的信号**，每个 Agent 服务不同签字者；但多 Agent 意味着每 PR 多次 LLM 调用 = 单次评审成本上升（⚠ Qodo 未公开多 Agent 推理成本，作者从架构推断，无价格证据）。

**(3) Stacked PR 是迄今最务实的协议层修复**。Graphite 在做的事不是让 AI 更聪明，而是让**每个信号单元再次回到人类可签字的颗粒度**——把流量爆炸前置切成可审小块。Shopify +33% / Asana +21% 数据 [[29]](https://graphite.com/blog/introducing-graphite-agent-and-pricing) 若在第三方独立测试中复现，stacked PR 将成下一轮 D5'+D6 强制协议层。

**(4) 计价模型在重写——按"信号"还是按"签字者"**。CodeRabbit "只对实际开 PR 的开发者计费" [[23]](https://www.coderabbit.ai/pricing)；Greptile 按 file changed 计量 [[26]](https://docs.greptile.com/pricing)；Bugbot 按 contributor seat [[34]](https://cursor.com/bugbot)。背后是三种"用户"定义：CodeRabbit = "活跃签字者"，Greptile = "被处理的信号量"，Bugbot = "所有 contributor"。⚠ 作者预判：按 PR 数 / file 数 / token 数等使用量计价会胜出，因为它和 Agent 触发频率成正比，也和"信号生产量"对齐。

**(5) AI-generated PR 标记会被法规推成标配**。欧盟 AI Act 第 113 条 2026-08-02 生效 [[11]](https://weventure.de/en/blog/ai-labeling) 加上学术界指纹归因（97.2% F1）[[10]](https://arxiv.org/html/2601.17406v1)，会把"PR metadata 中标注 AI 来源"从可选最佳实践推成 enterprise 强制项。GitHub 已抢跑，CodeRabbit / Greptile / Graphite 谁先把"AI 来源 + Trust Score"做成结构化 schema，谁就拿到下一轮评审协议的话语权——**这条 schema 就是"可签字信号"的标准包装**。

---

## 参考文献

[1] minware, "Average PRs Merged Per Developer," 2024. (Elite teams: 5+ PR/dev/week; Google median: 3 changes/week, 80th pct 7; Lyst median: 3 PR/week.) [Online]. Available: <https://www.minware.com/guide/metrics/average-prs-merged-per-developer>

[2] Graphite, "Tracking and improving code review turnaround time," 2024. (Median time-to-first-review 7–12h; time-to-merge 24–48h; large-company median 13h to merge.) [Online]. Available: <https://graphite.com/guides/tracking-improving-code-review-turnaround>

[3] M. Greiler, "Code Reviews at Google are lightweight and fast," 2023. (Avg 4h, small changes <1h.) [Online]. Available: <https://www.michaelagreiler.com/code-reviews-at-google/>

[4] Meta Engineering, "Move faster, wait less: Improving code review time at Meta," Nov. 2022. [Online]. Available: <https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/>

[5] LeadDev, "New study suggests major productivity boost when using Cursor's coding agent," 2025. (Cursor agent default: +39% weekly merged PRs; 24 vs 8 orgs; ~1,000 orgs sampled.) [Online]. Available: <https://leaddev.com/ai/cursor-claims-its-tools-are-a-massive-productivity-hack-for-devs>

[6] Cognition, "Devin Release Notes 2026," 2026. (PR merge rate 34% → 67% during 2025.) [Online]. Available: <https://docs.devin.ai/release-notes/2026>

[7] Faros AI, "DORA Report 2025 Key Takeaways: AI Impact on Dev Metrics," 2025. (+30% code output with flat review capacity → longer review, more misses.) [Online]. Available: <https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025>

[8] GitHub Docs, "About GitHub Copilot coding agent," 2026. (Coding Agent opens PRs and pushes commits under its own bot identity; PR author / commit author surfaces Copilot as the source.) [Online]. Available: <https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent>

[9] GitHub Community Discussion #179983, "How to prevent Copilot Coding Agent from being the main author of commits in master," 2025. (Confirms Copilot Coding Agent appears as commit author / Co-authored-by trailer on merged PRs.) [Online]. Available: <https://github.com/orgs/community/discussions/179983>

[10] arXiv:2601.17406, "Fingerprinting AI Coding Agents on GitHub," 2026. (33,580 PRs across five major agents; XGBoost classifier achieves 97.2% F1 in agent attribution.) [Online]. Available: <https://arxiv.org/html/2601.17406v1>

[11] WeVenture, "AI labeling requirement starting in 2026: What you need to know," 2026. (EU AI Act Article 113 effective 2026-08-02; mandatory C2PA metadata: Provider Name, System Version, Creation Timestamp, Unique Identifier.) [Online]. Available: <https://weventure.de/en/blog/ai-labeling>

[12] Credo AI, "Model Trust Scores: Evaluating AI Models," 2025. [Online]. Available: <https://www.credo.ai/model-trust-scores-ai-evaluation>

[13] Fiddler, "Trust Score Reference," 2025. (Numerical assessment across safety / toxicity / faithfulness / relevance / coherence.) [Online]. Available: <https://docs.fiddler.ai/reference/glossary/trust-score>

[14] Augment Code, "AI Coding Tools SOC2 Compliance: Enterprise Security Guide," 2025. (SOC 2 change management requires AI-generated code follow same review/approval as human-written code.) [Online]. Available: <https://www.augmentcode.com/tools/ai-coding-tools-soc2-compliance-enterprise-security-guide>

[15] CodeAnt AI, "GitHub AI Code Review Tools Built for SOC 2 Audits," 2025. (CC6.1 / CC8.1 require qualified reviewer approval per change with change request + testing evidence.) [Online]. Available: <https://www.codeant.ai/blogs/github-ai-code-review-tools-soc2-compliance>

[16] CodeRabbit Trust Center, "Compliance frameworks followed by CodeRabbit Inc," 2026. (SOC 2 Type II annual renewal; GDPR / HIPAA-compliant storage; in-memory clone, discarded after review.) [Online]. Available: <https://trust.coderabbit.ai/compliance>

[17] CodeRabbit, "CodeRabbit is now SOC 2 Type II compliant," 2025. (Third-party SOC 2 Type II audit completed 2025.) [Online]. Available: <https://coderabbit.ai/changelog/coderabbit-is-now-soc-2-type-ii-compliant>

[18] CodeRabbit, "Raising our $60 million Series B: Quality gates for AI coding," Sep. 2025. (2M+ repos, 13M+ PRs, 8,000+ paying customers, $550M valuation, $88M total funding.) [Online]. Available: <https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews>

[19] InfoWorld, "How CodeRabbit brings AI to code reviews," 2025. [Online]. Available: <https://www.infoworld.com/article/4025088/how-coderabbit-brings-ai-to-code-reviews.html>

[20] CodeRabbit, "The art and science of context engineering," 2025. (1:1 code-to-context ratio in LLM prompts.) [Online]. Available: <https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering>

[21] LanceDB, "Case Study: How CodeRabbit Leverages LanceDB for AI-Powered Code Reviews," 2025. (Millisecond semantic search across tens of thousands of tables; millions of daily code interactions.) [Online]. Available: <https://www.lancedb.com/blog/case-study-coderabbit>

[22] CodeRabbit Docs, "Review Instructions," 2026. [Online]. Available: <https://docs.coderabbit.ai/guides/review-instructions>

[23] CodeRabbit, "Pricing," 2026. (Lite $12, Pro $24, Pro+ $48 per dev/month annual; billed only for devs who open PRs.) [Online]. Available: <https://www.coderabbit.ai/pricing>

[24] Greptile, "Benchmarks," 2025. (50-bug test set; Greptile 82% catch / 11 false positives; CodeRabbit 44% catch / 2 false positives; Bugbot 58%.) [Online]. Available: <https://www.greptile.com/benchmarks>

[25] CodeAnt AI, "AI Code Review Benchmark 2026: Precision, Recall, and F1 Results," 2026. (CodeRabbit 59.39% accuracy / 36.19% F1 on OpenSSF CVE Benchmark.) [Online]. Available: <https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests>

[26] Greptile Docs, "Pricing," 2026. ($0.15/unit; genius=true 3 units; PR bot $0.45/file changed capped at $50/dev/month; 150 free units.) [Online]. Available: <https://docs.greptile.com/pricing>

[27] Greptile Docs, "Self-Hosting Overview," 2026. (Docker Compose / Kubernetes; AWS / GCP / Azure / air-gapped; custom LLM provider; hosted API base URL https://api.greptile.com/v2/.) [Online]. Available: <https://www.greptile.com/docs/self-hosting/overview>

[28] DEVCLASS, "Graphite debuts Diamond AI code reviewer, insists 'AI will never replace human code review'," Mar. 2025. [Online]. Available: <https://www.devclass.com/ai-ml/2025/03/19/graphite-debuts-diamond-ai-code-reviewer-insists-ai-will-never-replace-human-code-review/1626959>

[29] Graphite, "Meet Graphite Agent: the next evolution of AI code review," Oct. 2025. (Diamond merged into Graphite Agent 2025-10-08; 2026 pricing Free / Starter $20 / Team $40 / Enterprise; Shopify +33% PR merged per dev; Asana 7h saved/week, +21% code.) [Online]. Available: <https://graphite.com/blog/introducing-graphite-agent-and-pricing>

[30] Graphite, "Series B and Diamond Launch," 2025. ($52M Series B.) [Online]. Available: <https://graphite.com/blog/series-b-diamond-launch>

[31] Wikipedia, "Qodo," 2026. (Founded as CodiumAI in 2022 by Itamar Friedman and Dedy Kredo; rebranded Qodo 2024; expanded from test generation to full quality platform.) [Online]. Available: <https://en.wikipedia.org/wiki/Qodo>

[32] AICodeReview, "Qodo AI Review 2026," 2026. (Qodo 2.0 released Feb 2026; multi-agent architecture: bug/quality/security/test-coverage agents in parallel; F1 60.1%, recall 56.7% — highest in 8-tool benchmark.) [Online]. Available: <https://aicodereview.cc/blog/qodo-review/>

[33] qodo-ai/pr-agent, "PR-Agent: Original Open-Source PR Reviewer," 2026. (Open-source core; supports GitHub / GitLab / Bitbucket / Azure DevOps / CodeCommit / Gitea; self-hostable / air-gapped.) [Online]. Available: <https://github.com/qodo-ai/pr-agent>

[34] Cursor, "Bugbot," 2026. (2M+ PRs/month; 1M+ PRs reviewed since launch; 1.5M flags; 70%+ resolved pre-merge; Autofix launched Feb 2026; learns from human reviewer signals; $40/user/month per contributor.) [Online]. Available: <https://cursor.com/bugbot>

[35] Online Tool Stack, "Korbit AI Details, Pricing, Features, and Alternatives 2026," 2026. (Pro $24/user/month, free for open source; 10 languages.) [Online]. Available: <https://onlinetoolstack.com/korbit-ai>

[36] Aviator, "MergeQueue vs. Mergify: A Comparison," 2025. (Aviator $12/user/month, Mergify $21/user/month; optimistic_validation_failure_depth for flaky tests.) [Online]. Available: <https://www.aviator.co/aviator-mergequeue-mergify>

[37] Pixee, "Agentic AppSec Platform," 2026. (76% developer merge rate across 100,000+ PRs; scanner-alert-to-merge from 252 days to <48h; 95%+ false-positive reduction.) [Online]. Available: <https://www.pixee.ai/>

[38] Pixee, "Pixee Wins 2026 DEVIES Award for AppSecOps," 2026. [Online]. Available: <https://www.pixee.ai/blog/pixee-wins-2026-devies-award-appsecops>

[39] GitHub Blog, "New public preview features in Copilot code review: AI reviews that see the full picture," Oct. 28 2025. (Autofix fixed 1M+ vulnerabilities in 2025; tool calling + ESLint + CodeQL hybrid; one-click handoff to Copilot Coding Agent.) [Online]. Available: <https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/>

[40] GitLab Docs, "GitLab Duo Code Review (non-agentic)," 2026. (Non-agentic Duo Code Review GA in 18.1; self-hosted-model variant GA in 18.4.) [Online]. Available: <https://docs.gitlab.com/user/gitlab_duo/code_review/>

[41] GitLab Docs, "Code Review Flow (agentic)," 2026. (Agentic Code Review Flow beta in 18.7, GA in 18.8 Jan 2026; Free-tier on GitLab.com with Credits in 18.10.) [Online]. Available: <https://docs.gitlab.com/user/duo_agent_platform/flows/foundational_flows/code_review/>
