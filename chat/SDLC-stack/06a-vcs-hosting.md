# 2026-05-14：SDLC 栈 / 代码托管 (D6) 层深度研究

本篇是「Pre-Coding-Agent vs Post-Coding-Agent 软件开发栈」系列拆分后的 D6（代码托管）层。**只写托管平台本身**——GitHub / GitLab / Bitbucket / Gitea / Codeberg / Sourcehut / Azure DevOps Repos——在 Agent 时代的形态变化与战略重排。AI 评审（D5'）单独成文于 06b。

范本沿用 namespace.so 范式：先看 Pre-Agent 流量模式，再看 Agent 时代流量怎么突变，再看新需求与代表玩家的技术架构，最后给本质判断。

---

## 一、Pre-Agent 时代：代码托管是「人推送的稀疏事件流」

在 Coding Agent 普及前，托管平台承担的吞吐基本由人的工程师小时决定。GitHub 2024 财年（Octoverse 报告区间 2023-09 至 2024-08）数据可作为基线：

- 月 push 数量级在「亿级」，年化 push ≈ 7.9 亿次；月 merged PR 数量级在「3,500 万」上下（推算自 [[1]](https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/) 的同比基数）。
- 单个工程师典型流量：精英团队人均每周 5 PR 以上，Google 内部中位作者每周 3 changes，80 分位 7 changes/周 [[2]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer)。
- 单个仓库典型流量：活跃 SaaS 仓库 1–10 PR/天、5–30 push/天。⚠ 估算：综合 [[2]](https://www.minware.com/guide/metrics/average-prs-merged-per-developer) 中位团队规模 8–15 人 × 中位人均 3 PR/周推算，未对应单一一手来源。

在这个数量级下，托管平台的设计假设是：**push 是稀疏离散事件、PR 是同步会议、commit author 一定对应一个有 GitHub / GitLab 账号的真人**。Branch protection、required reviewer、CODEOWNERS 都是对人的协议——「至少 1 人 review、绿勾 CI、squash merge」。

GitLab 2021–2024 的「Single Application for the entire DevSecOps lifecycle」叙事就是建立在这个假设上：因为流量稀疏、流程串行，所以「一个工具覆盖 plan→code→build→test→secure→deploy」可以装得下。

## 二、Post-Agent 流量突变：托管平台被 Agent 提交流冲击

GitHub Octoverse 2025（覆盖 2024-09 至 2025-08）的同比数字直接量化了突变：

- **986M commits / 年，同比 +25.1%** [[1]](https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/)。
- **43.2M merged PR / 月，同比 +23%**；新建仓库 121M（创历史峰值），230+ 仓库 / 分钟；总活跃仓库 630M [[3]](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)。
- **新开发者注册速度：约 1 人 / 秒，年内新增 36M+，总数 180M+** [[3]](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)。
- **明确归属 Coding Agent 的 PR**：2025-05 至 2025-09 五个月内，Coding Agent 开出 1M+ PR，集中在高 star 仓库 [[1]](https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/)。

值得注意的不止增量，还有「形状」：commit comment 数量同比 −27%，而 PR 数量 +20% [[1]](https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/)——人对每个 commit 的「精细看」在退化，把注意力前移到 PR 层。

⚠ **本质变化**：托管平台从「人推送的稀疏事件流」变成「Agent + 人混合推送的密集流」。其中 Agent 推送在结构上有三个特征——(a) 24×7 不停（不受人工作时间限制）；(b) 来源可识别（bot 账号 / OIDC token）；(c) 同一 PR 往往对应一个外部任务 ID（Jira / Linear issue），不再是个人意图。这三点共同打破了「commit author = 真人 + 人类节奏」的旧假设。

## 三、新需求：流量爆发后托管层长出的护栏

旧 branch protection 只能拦人，对 Agent 推送既挡不住也分不开。Agent 时代托管平台必须长出的能力：

1. **Agent identity 一等公民**：bot 账号要有自己的 OIDC 身份、独立的 commit author / committer 字段、可被 audit log 单独抽出来。GitHub 已把 Copilot Coding Agent 的 PR author / commit author 显式标记为 Copilot 账户，并在 commit trailer 写 `Co-authored-by: Copilot <copilot@github.com>` [[4]](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent), [[5]](https://github.com/orgs/community/discussions/179983)。
2. **Commit signing for agents**：「Require signed commits」原本几乎与 Agent 互斥——bot 不会签名。2026-04 GitHub Copilot Cloud Agent 上线**自动 GPG 签名**，让 Agent 能进受保护分支 [[6]](https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/)。这一变化把「签名」从「人的身份证明」语义重写为「身份+来源证明」。
3. **Build provenance / artifact attestation**：托管平台需要把「这段代码由哪个 workflow、哪个 Agent、哪个 OIDC token 在哪个 commit SHA 产出」写成 SLSA provenance。GitHub 用 Sigstore 短期证书 + `actions/attest-build-provenance` 把 attestation 上传到 attestations API，公仓走 public-good Sigstore，私仓走 GitHub 私有 Sigstore 实例 [[7]](https://docs.github.com/en/actions/concepts/security/artifact-attestations), [[8]](https://github.com/actions/attest-build-provenance)。
4. **针对 bot 的差异化 ruleset**：必须能在 ruleset 里写「Agent 开的 PR 强制要求 2 个人类 reviewer + 必须等待 build attestation 通过」，否则风险敞口会被 Agent 的高速推送撑爆。GitHub Rulesets 已支持 by-actor 条件 [[9]](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)。

这四条不是锦上添花，是 Agent 时代代码托管的最小合规集。GitLab Duo Agent Platform 在 2026-04 也补齐了 automated security remediation / pipeline setup 等条目 [[10]](https://about.gitlab.com/gitlab-duo-agent-platform/)。

## 四、四家代表：战略与财务

### GitHub：四占战略的反脆弱

Microsoft 同时占四个层：**GitHub（仓库）+ Copilot（IDE/Chat/Coding Agent）+ VS Code（编辑器）+ Azure（推理底座）**。Octoverse 2025 的 630M repo / 986M commit / 180M dev 都跑在这个组合上 [[3]](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)。其反脆弱体现在：

- **任意一层被 best-of-breed 拆掉，其它三层仍在分发流量**。Cursor 抢走编辑器？VS Code 仍然是默认 IDE；Linear 抢走 issue？GitHub Issues 仍在 PR 旁边显示。
- **Agent 时代特定能力（attestation / signed commits / ruleset by actor）GitHub 一直是协议先发者** [[6]](https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/), [[7]](https://docs.github.com/en/actions/concepts/security/artifact-attestations)；GitLab 在大多数对应能力上是 fast-follower。
- **CodeRabbit / Greptile / Graphite 等第三方越火，GitHub Marketplace 越值钱**——它收的是租金，不是产品力。

### GitLab：一站式叙事被解构，但财务复活

2025 自然年股价 −33%、52 周高点 $53.43 下挫 62.8%，市场叙事一度认为 GitLab 已被 AI 拆 [[11]](https://www.fool.com/investing/2026/01/20/why-gitlab-stock-lost-33-in-2025/), [[12]](https://www.benzinga.com/trading-ideas/movers/26/05/52491665/gitlab-stock-tumbles-amid-ai-linked-restructuring)。但 FY2026（截至 2026-01）年报扭转：

- **全年营收 $955M / +26%**，ARR 突破 $1B [[13]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)。
- **Adjusted FCF $220M / +83%**；non-GAAP operating margin 17%（+680 bp）[[13]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)。
- **$100K+ ARR 客户 1,456（+18% YoY）；$1M+ ARR 客户 155（+26% YoY）；DBNR 118%** [[13]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)。
- 但 **FY2027 营收指引 $1.099–1.118B（+15%–17%）**，从 +26% 降到 +16%——增长曲线明显趄陡 [[13]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)。

董事会批了 **$400M 回购** [[13]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)，是对「叙事悲观、现金强劲」的最直接表态。⚠ **解读**：GitLab 没死、但「一站式 DevSecOps」从增长故事降级为现金牛——监管严格的银行 / 政府 / 自建 IDC 客户仍偏好单一应用，是它的护城河；公司层重组（Act 2）是收缩战线 [[12]](https://www.benzinga.com/trading-ideas/movers/26/05/52491665/gitlab-stock-tumbles-amid-ai-linked-restructuring)。

### Bitbucket / Atlassian：包内边缘化 + Rovo Dev 翻盘尝试

Atlassian 不单独披露 Bitbucket 营收，FY2025 全年 $5.215B（+19.66% YoY）；Cloud Q1 FY2026 $998M / +26% YoY [[14]](https://www.businesswire.com/news/home/20251030385606/en/Atlassian-Announces-First-Quarter-Fiscal-Year-2026-Results), [[15]](https://www.macrotrends.net/stocks/charts/TEAM/atlassian/revenue)。可观测的代码托管基线：**15M 开发者用 Bitbucket，Pipelines 月跑 10 亿+ build 分钟** [[16]](https://www.atlassian.com/blog/bitbucket/the-2025-year-in-review-and-whats-coming-soon)。

⚠ **估算**：业界一般认为 Bitbucket 占 Atlassian 营收 5%–10%，没有官方拆分。这种「包内边缘化」是结构性的——Jira 才是 Atlassian 的主力，Bitbucket 长期被当作附赠。

Rovo Dev 是 Atlassian 的翻盘动作：基于 Claude 3.5 Sonnet 的代码 Agent，**2025-10 GA**，跨 Jira / Confluence / Bitbucket / Compass [[17]](https://siliconangle.com/2025/10/08/atlassian-gives-rovo-ai-major-upgrade-developers-new-tools/), [[18]](https://www.atlassian.com/software/rovo-dev)。Atlassian 内部基准：**PR cycle time −30.8%，人写评论数 −35.6%** [[19]](https://www.atlassian.com/blog/artificial-intelligence/developer-productivity-improved-with-rovo-dev)。战略口径是「AI-native SDLC + 整合工具 + 企业信任」三条 [[16]](https://www.atlassian.com/blog/bitbucket/the-2025-year-in-review-and-whats-coming-soon)。

但 Bitbucket 的天花板很硬：它的开发者基数 15M 跟 GitHub 180M [[3]](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/) 差 12 倍；Rovo Dev 唯一能扳的是「Jira → Bitbucket 链路」的高保真上下文，而这条链对 Jira 重客户才有粘性。

### Azure DevOps Repos：被自家 GitHub 慢性蚕食

Microsoft 不再披露 Azure DevOps Repos 用户数。⚠ **估算**：从 GitHub Enterprise 在 Azure 上的整合演进与 Azure Repos 官方页强调「unlimited free private Git repos」却几乎不更新功能这两个信号判断，Microsoft 战略上把 Azure DevOps 客群导向 GitHub Enterprise + Azure。Azure Repos 仍服务**已经买了 Azure DevOps Server 自建客户 + 政府 / 国防合规客户**两个长尾。这一判断与微软公开战略一致但缺少单一一手来源支撑。

## 五、Self-hosted 复兴：Codeberg / Forgejo / Gitea / Sourcehut

GitHub Octoverse 2025 也间接催热 self-hosted——630M repo 高度集中带来**单点失败焦虑** + **AI 模型训练数据被拿去训练**的担忧。两条具体数字：

- **Codeberg**：2025-11 已托管 30 万+ 仓库、注册账号 20 万+，是 Forgejo 最大公共实例 [[20]](https://en.wikipedia.org/wiki/Codeberg)。
- **Forgejo**：从 2024 年从 Gitea fork 出来（治理原因），过去三年 1,930+ 贡献者；2025-04 NLnet 给 €50,000 grant [[21]](https://forgejo.org/2025-10-monthly-report/)。

定位差异：

- **Gitea**：「我只是想自己装一个 GitHub」——Docker 一拉、Actions 兼容、indie hacker 标配 [[22]](https://www.serverspan.com/en/blog/the-2026-guide-to-self-hosted-git-gitea-forgejo-and-the-future-of-code-hosting)。
- **Forgejo**：community-governed 反 Gitea 公司治理的分叉版本 [[22]](https://www.serverspan.com/en/blog/the-2026-guide-to-self-hosted-git-gitea-forgejo-and-the-future-of-code-hosting)。
- **Sourcehut**：极简 + git send-email 邮件列表工作流，UI 在 Lynx 可用——面向开源原教旨主义维护者，市场份额排到 20 位之外 [[22]](https://www.serverspan.com/en/blog/the-2026-guide-to-self-hosted-git-gitea-forgejo-and-the-future-of-code-hosting)。

⚠ **解读**：Self-hosted 复兴的**驱动力不是性能也不是价格，而是数据主权**——欧盟 / APAC 政府客户、开源基金会、对 Copilot 训练数据合规有疑虑的研究机构。规模不会超过 GitHub 的 1%（粗略数量级），但在「Agent 必须看到全仓 + 不能让数据外流」这一具体 Agent 场景里，self-hosted + 私有 LLM 是唯一解。

## 六、几条本质判断

**(1) 代码托管层的核心抽象正在重写**：从「commit author = 一个真人」迁到「commit author = 一个 OIDC 身份（人或 Agent）+ 一份 build provenance」。GitHub 在 ruleset / Sigstore / Copilot signed commits 三个点同时推这条迁移 [[6]](https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/), [[7]](https://docs.github.com/en/actions/concepts/security/artifact-attestations), [[9]](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)。

**(2) GitHub 的护城河是分发不是产品**。Coding Agent 一个月开 20 万 PR 不是因为 Copilot 比 Devin 强，而是因为它默认开在 180M dev 的 PR 页旁边。同理 CodeRabbit / Greptile / Graphite 越成功，GitHub Marketplace 越值钱——GitHub 收的是过路费。

**(3) GitLab 的「一站式」叙事破产但公司没破产**。FY2026 营收 +26%、ARR 过 $1B、自由现金流 +83% [[13]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx) 证明监管严的客群（银行、政府、自建 IDC）仍然要单一应用。增长降速到 +16% 把 GitLab 重新定位成现金牛，而不是高成长股——这是 Best-of-breed 复辟下「一站式」厂商的典型归宿。

**(4) Bitbucket 被 Jira 既保护又限制**。Rovo Dev 在 Jira 重客户里能扳一局（PR cycle −30.8% 不是小数 [[19]](https://www.atlassian.com/blog/artificial-intelligence/developer-productivity-improved-with-rovo-dev)），但 15M / 180M 的基数差让它永远是「Jira 用户的代码托管」而不是「Coder 的代码托管」。

**(5) Self-hosted 是利基不是革命**。Codeberg 30 万仓 vs GitHub 6.3 亿仓相差 2,000 倍，但「Agent 训练数据主权 + 私有 LLM 全仓索引」这两个 Agent 时代具体场景为 self-hosted 拓出了真实付费缺口——尤其欧盟数据主权与中国信创自主可控两个监管区。增长但不替代。

---

## 参考文献

[1] GitHub Blog, "What 986 million code pushes say about the developer workflow in 2025," 2025. (986M commits/yr +25.1% YoY; 43.2M merged PR/mo +23%; commit comments −27%; 1M+ Coding Agent PRs May–Sep 2025.) [Online]. Available: <https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/>

[2] minware, "Average PRs Merged Per Developer," 2024. (Elite teams: 5+ PR/dev/week; Google median: 3 changes/week, 80th pct 7; Lyst median: 3 PR/week.) [Online]. Available: <https://www.minware.com/guide/metrics/average-prs-merged-per-developer>

[3] GitHub Blog, "Octoverse: A new developer joins GitHub every second as AI leads TypeScript to #1," 2025. (180M+ devs, +36M/yr; 630M total repos, +121M in 2025; 230+ repos/min; 11.5B Actions minutes free.) [Online]. Available: <https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/>

[4] GitHub Docs, "About GitHub Copilot coding agent," 2026. (Coding Agent opens PRs and pushes commits under its own bot identity; PR author / commit author surfaces Copilot.) [Online]. Available: <https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent>

[5] GitHub Community Discussion #179983, "How to prevent Copilot Coding Agent from being the main author of commits in master," 2025. (Co-authored-by: Copilot trailer on merged PRs.) [Online]. Available: <https://github.com/orgs/community/discussions/179983>

[6] GitHub Changelog, "Copilot cloud agent signs its commits," Apr. 3 2026. (Coding agent now works in repos with Require signed commits ruleset.) [Online]. Available: <https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/>

[7] GitHub Docs, "Artifact attestations," 2026. (Sigstore short-lived signing cert; public-good Sigstore for public repos / private Sigstore for private repos; SLSA build provenance.) [Online]. Available: <https://docs.github.com/en/actions/concepts/security/artifact-attestations>

[8] GitHub, "actions/attest-build-provenance," 2025. (Action generating build provenance attestations for workflow artifacts.) [Online]. Available: <https://github.com/actions/attest-build-provenance>

[9] GitHub Docs, "Available rules for rulesets," 2026. (Rulesets support by-actor conditions, required signed commits, required reviewers per actor.) [Online]. Available: <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets>

[10] GitLab, "GitLab Duo Agent Platform," 2026. (Planner / Security Analyst / Data Analyst / CI Pipeline Agent; model selection GA in 18.4.) [Online]. Available: <https://about.gitlab.com/gitlab-duo-agent-platform/>

[11] Motley Fool, "Why GitLab Stock Lost 33% in 2025," Jan. 2026. (FY2025 −33%; net new customer additions at four-year low; NRR decline.) [Online]. Available: <https://www.fool.com/investing/2026/01/20/why-gitlab-stock-lost-33-in-2025/>

[12] Benzinga, "GitLab Stock Tumbles Amid AI-Linked Restructuring," May 2026. (62.8% below 52-week high of $53.43; Act 2 restructuring.) [Online]. Available: <https://www.benzinga.com/trading-ideas/movers/26/05/52491665/gitlab-stock-tumbles-amid-ai-linked-restructuring>

[13] GitLab IR, "GitLab Reports Fourth Quarter and Full Year Fiscal Year 2026 Financial Results; Board of Directors Authorizes $400 million for Share Repurchase Program," Mar. 2026. (Revenue $955M +26%; ARR > $1B; Adj. FCF $220M +83%; non-GAAP op margin 17%; $100K+ ARR customers 1,456 +18%; $1M+ ARR customers 155 +26%; DBNR 118%; FY27 guide $1.099–1.118B +15–17%.) [Online]. Available: <https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx>

[14] BusinessWire, "Atlassian Announces First Quarter Fiscal Year 2026 Results," Oct. 2025. (Cloud Q1 FY26 revenue $998M +26% YoY.) [Online]. Available: <https://www.businesswire.com/news/home/20251030385606/en/Atlassian-Announces-First-Quarter-Fiscal-Year-2026-Results>

[15] MacroTrends, "Atlassian Revenue 2014-2025 | TEAM," 2025. (FY2025 revenue $5.215B +19.66% YoY.) [Online]. Available: <https://www.macrotrends.net/stocks/charts/TEAM/atlassian/revenue>

[16] Atlassian Work Life, "The 2025 Year in Review (and what's coming soon)," 2025. (15M developers on Bitbucket; Bitbucket Pipelines 1B+ build minutes/mo; three 2026 missions: AI-native SDLC / tool consolidation / enterprise trust.) [Online]. Available: <https://www.atlassian.com/blog/bitbucket/the-2025-year-in-review-and-whats-coming-soon>

[17] SiliconANGLE, "Atlassian gives Rovo AI a major upgrade and developers new tools," Oct. 8 2025. (Rovo Dev GA Oct 2025; cross Jira / Confluence / Bitbucket / Compass.) [Online]. Available: <https://siliconangle.com/2025/10/08/atlassian-gives-rovo-ai-major-upgrade-developers-new-tools/>

[18] Atlassian, "Rovo Dev | Agentic AI for software teams," 2026. [Online]. Available: <https://www.atlassian.com/software/rovo-dev>

[19] Atlassian Work Life, "30.8% Faster PRs: How AI-Driven Rovo Dev Code Reviewer Improved Developer Productivity at Atlassian," 2025. (PR cycle time −30.8%; human-written comments −35.6%.) [Online]. Available: <https://www.atlassian.com/blog/artificial-intelligence/developer-productivity-improved-with-rovo-dev>

[20] Wikipedia, "Codeberg," 2025. (As of Nov 2025: 300K+ repos, 200K+ registered accounts; largest Forgejo public instance.) [Online]. Available: <https://en.wikipedia.org/wiki/Codeberg>

[21] Forgejo, "Forgejo monthly report - October 2025," Oct. 2025. (1,930+ contributors over 3 yrs; NLnet €50,000 grant Apr 2025.) [Online]. Available: <https://forgejo.org/2025-10-monthly-report/>

[22] ServerSpan, "The 2026 Guide to Self-Hosted Git: Gitea, Forgejo, and the Future of Code Hosting," 2026. (Gitea rank #2 in self-hosted; Sourcehut rank #20; Forgejo fork from Gitea late 2024 over governance.) [Online]. Available: <https://www.serverspan.com/en/blog/the-2026-guide-to-self-hosted-git-gitea-forgejo-and-the-future-of-code-hosting>
