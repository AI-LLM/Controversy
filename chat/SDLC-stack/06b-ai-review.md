# 2026-05-14：SDLC 栈 / AI 代码评审 (D5') 层深度研究

本篇是「Pre-Coding-Agent vs Post-Coding-Agent 软件开发栈」系列的 D5' 层——**AI 代码评审**。和 D6（代码托管平台 / VCS 本身）拆开单独成文，是因为 2025–2026 两层的产品逻辑已彻底分叉：托管在做"分发权 + 合规底座"的零和博弈，AI 评审在做"流量爆发后的新基础设施"的增量博弈。

范本沿用 namespace.so 范式：不写功能罗列，挖**流量/任务量模式突变 → 新需求 → 解决方案 → 架构 → 本质判断**。

---

## 一、Pre-Agent 时代：PR review 是"人之间的同步会议"

PR review 这个抽象的隐含假设：写代码的成本高 → PR 稀疏；reviewer 工时贵 → turnaround 是瓶颈。具体数字：

- **PR 流量**：精英团队人均每周 5+ PR [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)；Google 内部中位每周提交 3 changes、80 分位 7 changes [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)；Lyst 公开中位 3 PR/周、80 分位 ≤5 PR [[1]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)。
- **Review turnaround**：2024 大公司中位工程师 merge 一个 PR 约 13 小时，绝大多数时间在等 review [[2]](https://graphite.com/guides/tracking-improving-code-review-turnaround)；LinearB / Sleuth 行业基线 time-to-first-review 中位 7–12 小时、time-to-merge 中位 24–48 小时 [[2]](https://graphite.com/guides/tracking-improving-code-review-turnaround)；Google 内部 review 平均 4 小时 [[3]](https://www.michaelagreiler.com/code-reviews-at-google/)。
- **review 占工程师工时**：Meta 内部数据显示，评审是 change lead time 中**最大的延迟来源** [[4]](https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/)。

在这个数量级里，PR 是"写完—贴出—等人—评论—改—合并"的同步会议。一周 5 PR、一审 7 小时、一改 1–2 轮，全公司能扛得住（⚠ 解读：综合 [[1]][[2]] 中位数复述；"1–2 轮改"是作者对 Pre-Agent 时代日常的经验性描述，未对应单一来源）。

## 二、Post-Agent 流量突变：人审 bottleneck 被压成一根线

Cursor 团队 2025 公开的因果推断研究：把 Background Agent 设为默认工作流的公司，**周合并 PR 数比对照组高 39%**，覆盖 24 组实验 / 8 组对照、约 1,000 组织、数万开发者，未观察到 revert rate 显著上升 [[5]](https://leaddev.com/ai/cursor-claims-its-tools-are-a-massive-productivity-hack-for-devs)。Devin 在 2025 年期间 PR merge 率从 **34% 提升到 67%** [[6]](https://docs.devin.ai/release-notes/2026)——三分之二自治 Agent 的 PR 最终进主分支，单个 Agent 实例可 24×7 不停发 PR。

DORA 2024–2025 报告抓到了另一面：当 AI 把代码产出抬高约 30% 而 review 容量不变时，PR 体积变大、review 时间延长、问题漏检概率上升 [[7]](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025)。

⚠ **流量本质变化**（作者解读，依据 [[5]][[6]][[7]]）：

- 写端的边际成本从「工程师小时」掉到「LLM tokens」——单价掉两个数量级；
- 审端依旧是「工程师小时」——单价没动；
- PR 是连接两端的协议，一边在指数膨胀，一边在线性配额，**夹在中间的人 review 必然成为瓶颈**。

新范式必须做两件事：(a) 让 Agent 审 Agent 写的 PR；(b) 把人从"行级评论"拉到"策略级把关"。这是 D5' 层 2025–2026 所有产品的共同前提。

## 三、新需求：流量爆炸时代的次生市场

从"人发的稀疏事件"到"Agent 发的密集流"，长出几条新需求线：

1. **AI-generated PR 标记**：reviewer 需要立刻知道 diff 是 Agent 写的还是人写的，决定关注力分配。GitHub 已在 PR metadata 暴露 Copilot Coding Agent 来源：PR 作者 / commit author 直接显示为 Copilot bot，commit trailer 可加 `Co-authored-by: Copilot <copilot@github.com>` [[8]](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent), [[9]](https://github.com/orgs/community/discussions/179983)。学术界 2026 年用行为指纹做归因——XGBoost 分类器在 33,580 个 PR 上对五大 Agent 的归属判定达到 97.2% F1 [[10]](https://arxiv.org/html/2601.17406v1)；同时欧盟 AI Act 第 113 条要求 2026-08-02 起所有"职业发布的 AI 生成内容"需带 C2PA 元数据（Provider Name / System Version / Creation Timestamp / Unique Identifier）[[11]](https://weventure.de/en/blog/ai-labeling)——这条法规会反向倒逼 PR 层加结构化标记。
2. **回归风险评估 / Trust Score per PR**：给 PR 叠加 0–10 的可信度评分，综合静态分析、测试覆盖、依赖影响、Agent 来源、过往 revert 概率。Credo AI / Fiddler 等 trust-score 框架已在通用 LLM 安全侧落地 [[12]](https://www.credo.ai/model-trust-scores-ai-evaluation), [[13]](https://docs.fiddler.ai/reference/glossary/trust-score)，PR 层等同 schema 即将出现（⚠ 解读：截至 2026-05 尚无主流评审厂商公开发布"PR Trust Score"独立 schema，作者把它列为"将出现"的次生市场而非现状）。
3. **合规人最终批准**：SOC 2 CC8.1 明确要求**所有代码变更（含 AI 生成）部署前必须有人审批**，且要留 change request、approver signature、测试证据 [[14]](https://www.augmentcode.com/tools/ai-coding-tools-soc2-compliance-enterprise-security-guide), [[15]](https://www.codeant.ai/blogs/github-ai-code-review-tools-soc2-compliance)；CC6.1 把这条延伸到生产合并。这条监管事实直接锁死了"全自动 Agent 合并"的天花板——人不能完全退出。CodeRabbit 2025 完成 SOC 2 Type II 第三方审计（年度续审），数据存储同时符合 GDPR / HIPAA；仓库代码在内存中 clone 完成评审后立即丢弃，可选缓存 ≤7 天或完全关闭，Enterprise（≥500 seats）可全自托管 [[16]](https://trust.coderabbit.ai/compliance), [[17]](https://coderabbit.ai/changelog/coderabbit-is-now-soc-2-type-ii-compliant)。

## 四、代表公司技术架构

### 4.1 CodeRabbit：Astute Review + Code Graph + Context Engineering

流量证据：2026 初已接入 **2M+ 仓库、处理 13M+ PR、8,000+ 付费客户**，客户含 Chegg、Groupon、Life360、Mercury；2025-09 完成 Series B $60M，估值 $550M，累计 $88M [[18]](https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews)。

技术架构三层 [[19]](https://www.infoworld.com/article/4025088/how-coderabbit-brings-ai-to-code-reviews.html), [[20]](https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering)：

1. **Static analysis 子层**：内置数十种 linter、CodeQL、ast-grep 规则，结构化结果作为 prompt 上下文喂给 LLM。
2. **Code Graph 子层**：解析整个仓库构造依赖图，跨文件追踪函数引用——这是"astute review"的关键，让 LLM 看到 diff 在远端文件触发的 contract 破坏。
3. **Context Engineering**：自称 prompt 里维持 **1:1 的 code-to-context 比例**——diff 旁边塞 Jira ticket、past PR、code graph、linter 输出、过往 chat learning [[20]](https://www.coderabbit.ai/blog/the-art-and-science-of-context-engineering)。底层用 LanceDB 做毫秒级语义检索，索引数万张 PR / issue / 依赖表 [[21]](https://www.lancedb.com/blog/case-study-coderabbit)。

**配置示例**（`.coderabbit.yaml`）[[22]](https://docs.coderabbit.ai/guides/review-instructions)：

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

定价（2026）[[23]](https://www.coderabbit.ai/pricing)：Lite $12 / Pro $24 / Pro+ $48 per dev/月（年付）；月付分别 $30 / $60。**仅对实际开 PR 的开发者计费**——周内没开 PR 的座位不收钱，这是 Agent 时代"按实际触发"的计价创新。

### 4.2 Greptile：跨文件深审，召回优先

Greptile 的差异化是"先把整个 repo 索引成图，再审 PR"——更适合 monorepo 和跨文件破坏。公开 benchmark：50 个真实 bug 测试集，**Greptile 82% catch / CodeRabbit 44% catch**，但 Greptile 误报 11 条、CodeRabbit 仅 2 条 [[24]](https://www.greptile.com/benchmarks)。第三方 OpenSSF CVE Benchmark 复测显示 CodeRabbit 准确率 59.39% / F1 36.19%，仍漏掉约 41% 真实漏洞 [[25]](https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests)。这是一道明确的产品哲学分叉：**召回优先 vs 精度优先**。

定价采用 API 计量 [[26]](https://docs.greptile.com/pricing)：`POST /query` 1 unit = $0.15；`genius=true`（更大模型）3 units；PR Review Bot **$0.45 / file changed**，封顶 $50/dev/月，超过封顶部分免费；新用户赠 150 units。

部署形态 [[27]](https://www.greptile.com/docs/self-hosting/overview)：支持 Docker Compose / Kubernetes 自托管，覆盖 AWS / GCP / Azure / 完全 air-gapped；LLM provider 可换（OpenAI / Anthropic / 自托管模型）。Hosted API base URL `https://api.greptile.com/v2/`。这条"自托管 + air-gapped"路线针对金融 / 政府 / 国防客户。

判据：复杂代码库、跨文件破坏频发、宁可多看噪音也不愿漏 bug 的团队选 Greptile；signal-to-noise 至上的团队选 CodeRabbit。

### 4.3 Graphite Diamond / Agent：协议层修复——把 PR 拆小

Graphite 2025-03 推出 Diamond 独立产品，宣示"AI 永远不会替代人 review"[[28]](https://www.devclass.com/ai-ml/2025/03/19/graphite-debuts-diamond-ai-code-reviewer-insists-ai-will-never-replace-human-code-review/1626959)；2025-10-08 把 Diamond 并入 **Graphite Agent**，统一 AI 评审与 stacked PR 工作流 [[29]](https://graphite.com/blog/introducing-graphite-agent-and-pricing)。核心论点：**大 PR 不可审，必须 stack 成小 PR**——把"PR 体积膨胀"这个 Agent-after 顽症在**协议层**解掉，而不是靠 reviewer 加班。Series B $52M [[30]](https://graphite.com/blog/series-b-diamond-launch)。

2026 定价 [[29]](https://graphite.com/blog/introducing-graphite-agent-and-pricing)：Free（Hobby，含 CLI、VS Code 扩展、有限 Agent 配额）/ Starter $20/user/月（年付，全仓库 + insights）/ Team $40/user/月（年付，无限 Agent + 无限 AI review + merge queue）/ Enterprise 定制。

客户证据：Shopify 采用 Graphite stacked PR 后**人均 merge PR +33%**；Asana 工程师每周省 7 小时、产出 +21% [[29]](https://graphite.com/blog/introducing-graphite-agent-and-pricing)（⚠ 厂商自报数据，未见第三方独立验证）。

### 4.4 Qodo（前 CodiumAI）：多 Agent 并行 + 开源底座

Qodo 由原 CodiumAI 在 2024 年改名而来 [[31]](https://en.wikipedia.org/wiki/Qodo)。2026-02 发布 **Qodo 2.0**，把单次 LLM 评审拆成多 Agent 并行架构——一个 Agent 抓 bug、一个查代码质量、一个做安全分析、一个看测试覆盖；benchmark F1 达 **60.1%**、recall 56.7%，在 7 家厂商对比中最高 [[32]](https://aicodereview.cc/blog/qodo-review/)。差异化卖点：

- **开源核心**：评审引擎 PR-Agent 是 GitHub 开源项目，支持 GitHub / GitLab / Bitbucket / Azure DevOps / CodeCommit / Gitea，可自托管、可 air-gapped、可审计 prompt [[33]](https://github.com/qodo-ai/pr-agent)。
- **测试生成**：从 CodiumAI 时代继承，分析未测路径自动生成 unit test（不是 stub，带断言和边界用例）[[31]](https://en.wikipedia.org/wiki/Qodo)。

### 4.5 Cursor Bugbot：窄域、Autofix、行为学习

Cursor 在 2025 推出 Bugbot，2026 早期已**月处理 2M+ PR、累计 review 1M+ PR、标记 1.5M issue，70%+ flag 在 merge 前被解决** [[34]](https://cursor.com/bugbot)。差异化是**故意做窄**：只抓 logic bug、安全漏洞、race condition、空指针、错误处理——**主动忽略**格式 / 风格 / 低优问题。2026-02 发布 **Bugbot Autofix**：在云端虚拟机里 spawn agent 修 Bugbot 自己抓到的问题；Bugbot 还会**从 reviewer 反应（downvote / 回复 / 同 PR 的人审评论）学习规则**，累积信号变成 active rule，负反馈过多则退役 [[34]](https://cursor.com/bugbot)。

定价 $40/user/月，仓库**每个 contributor 都要一个 seat**，与 Cursor IDE 许可分开——20 人团队仅 Bugbot 一项就 $800/月 [[34]](https://cursor.com/bugbot)。这是 Cursor 把"Agent 写 → Agent 审"在自己产品矩阵内闭环的尝试。

### 4.6 其它玩家速览

- **Korbit AI**：GitHub/GitLab/Bitbucket 三端 PR review bot，10 种语言；Korbit Pro $24/user/月，开源免费；卖点"senior 级反馈、保证不拿你的代码训练" [[35]](https://onlinetoolstack.com/korbit-ai)。
- **Aviator / Mergify**：merge queue 起家。Aviator $12/user/月、支持 monorepo 并行队列、flaky test 容忍策略（`optimistic_validation_failure_depth`）；Mergify $21/user/月、merge queue + CI Insights + Merge Protections 全捆绑 [[36]](https://www.aviator.co/aviator-mergequeue-mergify)。它们是"PR 流量爆发后的合并层"防线。
- **Pixee**：安全侧的 PR remediation。Pixee 在 100,000+ PR 实测达到 **76% developer merge rate**，把扫描器报警到 merge 的中位时间从行业平均 252 天压到 < 48 小时；声称消除 95%+ 误报 [[37]](https://www.pixee.ai/), [[38]](https://www.pixee.ai/blog/pixee-wins-2026-devies-award-appsecops)。
- **GitHub Copilot Code Review**：2025-10 Public Preview，把 LLM 检测 + tool calling + ESLint / CodeQL 混合，建议可"一键传给 Copilot Coding Agent"自动开 PR 修 [[39]](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/)。Copilot Autofix 2025 全年修复 1M+ 漏洞 [[39]](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/)。
- **GitLab Duo Code Review**：非 agentic 版本在 GitLab 18.1 GA；自托管模型版在 18.4 GA；**agentic 版本（Code Review Flow）**18.7 beta、**18.8 GA**（2026-01）；18.10 起对 GitLab.com Free tier 开放（消耗 GitLab Credits）[[40]](https://docs.gitlab.com/user/gitlab_duo/code_review/), [[41]](https://docs.gitlab.com/user/duo_agent_platform/flows/foundational_flows/code_review/)。

## 五、几条本质判断

**(1) PR 抽象不会消失，但语义在迁移**。Pre-Agent：PR = "人提交的工作单元"；Post-Agent：PR = "待审的 diff 包，作者可以是 Agent"。语义从"沟通载体"滑向"策略闸门"。

**(2) Agent 写 → Agent 审在技术上已经成立，但在合规上不成立**。CodeRabbit 13M PR 吞吐 [[18]](https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews) 证明 LLM 评审能扛流量；Greptile 82% 召回 [[24]](https://www.greptile.com/benchmarks) 证明能抓 bug；Qodo 60.1% F1 [[32]](https://aicodereview.cc/blog/qodo-review/) 证明多 Agent 架构在精度/召回平衡上还能继续抬。但 SOC 2 / ISO 27001 / 欧盟 AI Act 第 113 条 [[11]](https://weventure.de/en/blog/ai-labeling)[[14]](https://www.augmentcode.com/tools/ai-coding-tools-soc2-compliance-enterprise-security-guide) 都把人锁定为 final approver。未来形态是 **Agent 写 → Agent 审 → 人按策略批一批**，而不是"全自动直合"。人退到"批量决策 + 异常处理"。

**(3) 召回 vs 精度是产品哲学分叉，不会有"全能赢家"**。Greptile（82% / 11 FP）与 CodeRabbit（44% / 2 FP）走的是不同 user persona——前者服务"漏一个 bug 死人"的金融/医疗/安全，后者服务"reviewer 注意力是稀缺品"的创业团队。Qodo 多 Agent 路线试图同时拉高两端，但多 Agent 意味着每 PR 多次 LLM 调用 = 单次评审成本上升（⚠ 解读：Qodo 未公开多 Agent 推理成本，作者从架构推断，无价格证据）。

**(4) Stacked PR 是协议层修复方案**。Graphite 在做的事不是"让 AI 更聪明"，而是"让 PR 更小"——把流量爆炸前置切成可审小块，符合 Pre-Agent 时代的 human-review 节奏。这是迄今最务实的桥接。Shopify +33% / Asana +21% 数据 [[29]](https://graphite.com/blog/introducing-graphite-agent-and-pricing) 若能在第三方独立测试中复现，stacked PR 将成为下一轮 D5'+D6 产品的强制协议层。

**(5) 计价模型在重写**。CodeRabbit "只对实际开 PR 的开发者计费" [[23]](https://www.coderabbit.ai/pricing)；Greptile 按 file changed 计量 [[26]](https://docs.greptile.com/pricing)；Bugbot 按 contributor seat 计费 [[34]](https://cursor.com/bugbot)。三种模式背后是同一道选择题：**Agent 时代的"用户"到底是不是开发者？**——CodeRabbit 说"活跃开发者"，Greptile 说"被处理的 diff"，Bugbot 说"所有 contributor"。这条 SKU 设计博弈到 2026 末会大幅收敛——⚠ 作者预判：按"PR 数 / file 数 / token 数"等使用量计价的模型会胜出，因为它和 Agent 触发频率成正比。

**(6) "AI-generated PR 标记" 会被法规强推成标配**。欧盟 AI Act 第 113 条 2026-08-02 生效 [[11]](https://weventure.de/en/blog/ai-labeling) 加上学术界的指纹归因方法（97.2% F1）[[10]](https://arxiv.org/html/2601.17406v1)，会把"PR metadata 中标注 AI 来源"从可选最佳实践推成 enterprise 强制项。GitHub 已抢跑，CodeRabbit / Greptile / Graphite 谁先把"AI 来源 + Trust Score"做成结构化 schema，谁就拿到下一轮评审协议的话语权。

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
