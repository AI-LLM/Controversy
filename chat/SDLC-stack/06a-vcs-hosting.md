# 2026-05-14：SDLC 栈 / 代码托管 (D6) 层深度研究

本篇是「Pre-Coding-Agent vs Post-Coding-Agent 软件开发栈」系列拆分后的 D6（代码托管）层。**只写托管平台本身**——GitHub / GitLab / Bitbucket / Gitea / Codeberg / Sourcehut / Azure DevOps Repos——在 Agent 时代的形态变化与战略重排。AI 评审（D5'）单独成文于 06b。

与上游 CI / 推理层不同，**代码托管不按 PR / commit 计费**——Marketplace 收的是订阅 + 抽佣，不是按调用次数。所以本文的分析框架不是「流量 → 计费 → 估值」三段式，而是**分发渠道护城河 + 协议先发护城河**的双层结构。流量数字在本文里只作为「分发渠道厚度」的指示器，不作为收入推算的基础。

---

## 一、Agent 时代代码托管的协议重写——为什么 L06a 的本质不是流量

L06a 与 L05（推理 / CI 算力）的根本差异在于**计费维度**：CI 按 build minute 计、推理按 token 计，所以流量爆炸直接传导到收入；代码托管按 seat / Enterprise / Marketplace 分成计，**Agent 推 10 个 commit 还是 100 个 commit 对 GitHub 自身的边际收入接近 0**。真正决定 L06a 格局的不是流量，而是 Agent 时代被重写的四条底层协议——谁先把这四条协议写成事实标准，谁就握住了 Devin / Cursor / Codex 等外部 Agent 的「商用准入证」。

四条协议：

1. **Agent identity 一等公民**：bot 账号要有自己的 OIDC 身份、独立的 commit author / committer 字段、可被 audit log 单独抽出来。GitHub 已把 Copilot Coding Agent 的 PR author / commit author 显式标记为 Copilot 账户，并在 commit trailer 写 `Co-authored-by: Copilot <copilot@github.com>` [[1]](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent), [[2]](https://github.com/orgs/community/discussions/179983)。
2. **Commit signing for agents**：「Require signed commits」原本几乎与 Agent 互斥——bot 不会签名。2026-04 GitHub Copilot Cloud Agent 上线**自动 GPG 签名**，让 Agent 能进受保护分支 [[3]](https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/)。这一变化把「签名」从「人的身份证明」语义重写为「身份 + 来源证明」。
3. **Build provenance / SLSA artifact attestation**：托管平台需要把「这段代码由哪个 workflow、哪个 Agent、哪个 OIDC token 在哪个 commit SHA 产出」写成 SLSA provenance。GitHub 用 Sigstore 短期证书 + `actions/attest-build-provenance` 把 attestation 上传到 attestations API，公仓走 public-good Sigstore，私仓走 GitHub 私有 Sigstore 实例 [[4]](https://docs.github.com/en/actions/concepts/security/artifact-attestations), [[5]](https://github.com/actions/attest-build-provenance)。
4. **By-actor ruleset**：必须能在 ruleset 里写「Agent 开的 PR 强制要求 2 个人类 reviewer + 必须等待 build attestation 通过」。GitHub Rulesets 已支持 by-actor 条件 + 按 actor 区分 required reviewer + required signed commits [[6]](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)。

这四条不是锦上添花，是 Agent 时代代码托管的最小合规集。Devin、Cursor Background Agent、OpenAI Codex Cloud 想在受监管企业里跑「自动开 PR、自动 merge」的工作流，**必须先适配这四条协议**——也就是必须先在 GitHub 上跑通，再考虑 GitLab。

⚠ **解读**：这是 L06a 与 L05 最根本的不同——L05 是「谁先把价格降下来」，L06a 是「谁先把协议写出来」。协议先发权一旦确立，迁移成本会被锁进 ruleset、audit log schema、attestation API endpoint，沉淀成不可逆资产。GitLab Duo Agent Platform 在 2026-04 也补齐了 automated security remediation / pipeline setup / model selection 等条目 [[7]](https://about.gitlab.com/gitlab-duo-agent-platform/)，但**绝大多数能力上是 fast-follower**——它在做的事情是「确保 GitLab 客户不必跳船」，不是「定义协议」。

作为旁证：Octoverse 2025（覆盖 2024-09 至 2025-08）数据显示，年化 **986M commits / +25.1%、43.2M merged PR / 月 / +23%** [[8]](https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/)；2025-05 至 2025-09 五个月内 **Coding Agent 开出 1M+ PR**，集中在高 star 仓库 [[8]](https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/)。commit comment 数量同比 −27%、PR 数量 +20% [[8]](https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/)——人对每个 commit 的「精细看」在退化，把注意力前移到 PR 层。这些数字本身不带来收入，但它们指示**协议必须落在哪里**——落在 PR 页、落在 ruleset、落在 attestation。

## 二、GitHub：分发渠道 + 协议先发的双护城河

GitHub 的护城河是两层叠加，不是「聚合解构」单层。

**第一层——分发渠道护城河**：180M dev 默认目录 + Marketplace 过路费经济。Octoverse 2025 给出的分发面：新开发者注册速度约 **1 人 / 秒**，年内新增 36M+，总数 **180M+**；新建仓库 121M（创历史峰值），230+ 仓库 / 分钟；总活跃仓库 **630M** [[9]](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)。CodeRabbit / Greptile / Graphite / Sentry / Snyk 等第三方越火，GitHub Marketplace 越值钱——**它收的是租金 + 分成，不是产品力**。Coding Agent 一个月开 20 万 PR 不是因为 Copilot 比 Devin 强，而是因为它默认开在 180M dev 的 PR 页旁边。

**第二层——协议先发护城河**：§1 列的四条协议（identity / signed commits / SLSA provenance / by-actor ruleset）GitHub 一直是首发者 [[3]](https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/), [[4]](https://docs.github.com/en/actions/concepts/security/artifact-attestations), [[6]](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)。每一条协议落地都对应一个「外部 Agent 必须先适配 GitHub」的强制点——Devin 想进银行客户，必须先支持 GitHub by-actor ruleset；Cursor Background Agent 想合规商用，必须接 Sigstore attestation。

**两层为什么能复合**：分发渠道决定外部 Agent 必须来 GitHub 找用户（180M dev 在这里），协议先发决定它们来了之后必须按 GitHub 的接口跑（identity / signing / provenance）。任意一层被 best-of-breed 拆掉，另一层仍在锁定——Cursor 抢走编辑器？VS Code 仍然是默认 IDE 且 commit author 仍走 GitHub identity；Linear 抢走 issue？GitHub Issues 仍在 PR 旁边显示且 PR 仍是 ruleset + attestation 的强制落点。

**工作流锁定的具体面**：PR 页同时是 Issue 联动点（GitHub Issues / Projects）、CI 入口（Actions）、Agent 入口（Copilot Coding Agent / Marketplace Agent）、合规入口（Rulesets + Attestations）、Marketplace 触达点。把仓库迁到 GitLab，意味着同时迁这五条线索——而每条线索都有独立的外部依赖（Marketplace 集成、Actions workflow、Sigstore endpoint、Copilot 配额）。迁移成本不是「git push 改一个 URL」，是**重写五张协议表**。

⚠ **解读**：这就是「为什么不是聚合解构」——纯解构论只解释 GitLab 输（一站式叙事破产），不解释 GitHub 凭什么不被同样解构。答案是**协议先发把 Agent 时代的新接口锁回了 GitHub**，外部 best-of-breed 越多，GitHub 作为协议中枢越强。

## 三、GitLab：一站式叙事降级为现金牛

2025 自然年股价 **−33%、52 周高点 $53.43 下挫 62.8%**，市场叙事一度认为 GitLab 已被 AI 拆 [[10]](https://www.fool.com/investing/2026/01/20/why-gitlab-stock-lost-33-in-2025/), [[11]](https://www.benzinga.com/trading-ideas/movers/26/05/52491665/gitlab-stock-tumbles-amid-ai-linked-restructuring)。但 FY2026（截至 2026-01）年报扭转：

- **全年营收 $955M / +26%**，ARR 突破 $1B [[12]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)。
- **Adjusted FCF $220M / +83%**；non-GAAP operating margin 17%（+680 bp）[[12]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)。
- **$100K+ ARR 客户 1,456（+18% YoY）；$1M+ ARR 客户 155（+26% YoY）；DBNR 118%** [[12]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)。
- 但 **FY2027 营收指引 $1.099–1.118B（+15%–17%）**，从 +26% 降到 +16%——增长曲线明显趄陡 [[12]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)。

董事会批了 **$400M 回购** [[12]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx)，是对「叙事悲观、现金强劲」最直接的表态。

⚠ **解读**：GitLab 没死、但「一站式 DevSecOps」从增长故事降级为现金牛。**护城河收窄到"监管客群"这一条**——银行、政府、国防、自建 IDC、本地化合规（GDPR / 信创 / 数据驻留），这些客户偏好单一应用，因为多供应商带来的审计成本远高于功能差距。Act 2 重组 [[11]](https://www.benzinga.com/trading-ideas/movers/26/05/52491665/gitlab-stock-tumbles-amid-ai-linked-restructuring) 是收缩战线、聚焦监管客群的财务表态。

从协议视角看，GitLab Duo Agent Platform [[7]](https://about.gitlab.com/gitlab-duo-agent-platform/) 在功能层做了齐全的对齐（Planner / Security Analyst / Data Analyst / CI Pipeline Agent / 模型选择 GA），但**在协议层始终落后 6–12 个月**——Sigstore attestation 对应物、by-actor ruleset 对应物、Agent signed commit 对应物，几乎都是 GitHub 先发后 GitLab 跟。这种「永远 fast-follower」的位置意味着：外部 Agent 厂商（Devin / Cursor / Codex）做集成时永远 GitHub-first，GitLab 是次要 SKU。

## 四、Bitbucket / Atlassian：被母船既保护又限制的长尾

Atlassian 不单独披露 Bitbucket 营收，FY2025 全年 $5.215B（+19.66% YoY）；Cloud Q1 FY2026 $998M / +26% YoY [[13]](https://www.businesswire.com/news/home/20251030385606/en/Atlassian-Announces-First-Quarter-Fiscal-Year-2026-Results), [[14]](https://www.macrotrends.net/stocks/charts/TEAM/atlassian/revenue)。Atlassian 股票 TEAM 一度从高点 **−56%**，反映市场对 Jira / Confluence 被 Notion + Linear + Coding Agent 三向夹击的悲观。可观测的代码托管基线：**15M 开发者用 Bitbucket，Pipelines 月跑 10 亿+ build 分钟** [[15]](https://www.atlassian.com/blog/bitbucket/the-2025-year-in-review-and-whats-coming-soon)。

⚠ **估算**：业界一般认为 Bitbucket 占 Atlassian 营收 5%–10%，没有官方拆分。这种「包内边缘化」是结构性的——Jira 才是 Atlassian 的主力，Bitbucket 长期被当作附赠。

Rovo Dev 是 Atlassian 的翻盘动作：基于 Claude 3.5 Sonnet 的代码 Agent，**2025-10 GA**，跨 Jira / Confluence / Bitbucket / Compass [[16]](https://siliconangle.com/2025/10/08/atlassian-gives-rovo-ai-major-upgrade-developers-new-tools/), [[17]](https://www.atlassian.com/software/rovo-dev)。Atlassian 内部基准：**PR cycle time −30.8%，人写评论数 −35.6%** [[18]](https://www.atlassian.com/blog/artificial-intelligence/developer-productivity-improved-with-rovo-dev)。战略口径是「AI-native SDLC + 整合工具 + 企业信任」三条 [[15]](https://www.atlassian.com/blog/bitbucket/the-2025-year-in-review-and-whats-coming-soon)。

⚠ **解读**：母船 Atlassian 既保护又限制 Bitbucket——保护体现在 Jira 重客户天然会用 Bitbucket，Rovo Dev 的「Jira → Bitbucket」高保真上下文链是真实差异化；限制体现在两层：

1. **分发渠道层**：Bitbucket 开发者基数 15M 跟 GitHub 180M [[9]](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/) 差 12 倍，外部 Marketplace 生态不足以养出独立飞轮。
2. **协议层**：Atlassian 没有可比的 Sigstore / SLSA / by-actor ruleset 公开承诺——Rovo Dev 是产品级 Agent，不是协议级标准。

结果是 Bitbucket 在 Agent 时代仍只能服务「Jira 用户的代码托管」，不会成为「Coder 的代码托管」。

## 五、Azure Repos & Self-host 复兴：长尾与数据主权利基

**Azure DevOps Repos**：Microsoft 不再披露 Azure DevOps Repos 用户数。⚠ **估算**：从 GitHub Enterprise 在 Azure 上的整合演进与 Azure Repos 官方页强调「unlimited free private Git repos」却几乎不更新功能这两个信号判断，Microsoft 战略上把 Azure DevOps 客群导向 GitHub Enterprise + Azure。Azure Repos 仍服务**已经买了 Azure DevOps Server 自建客户 + 政府 / 国防合规客户**两个长尾。这一判断与微软公开战略一致但缺少单一一手来源支撑。Microsoft 的「四占战略」（GitHub + Copilot + VS Code + Azure）意味着 Azure Repos 在内部就被定位为「迁出口」，不是「主线产品」。

**Self-hosted 复兴**：GitHub 高度集中（630M repo 在一个供应商上）带来**单点失败焦虑** + **数据被拿去训练**的双重担忧，两条具体数字：

- **Codeberg**：2025-11 已托管 30 万+ 仓库、注册账号 20 万+，是 Forgejo 最大公共实例 [[19]](https://en.wikipedia.org/wiki/Codeberg)。
- **Forgejo**：从 2024 年从 Gitea fork 出来（治理原因），过去三年 1,930+ 贡献者；2025-04 NLnet 给 €50,000 grant [[20]](https://forgejo.org/2025-10-monthly-report/)。

定位差异：

- **Gitea**：「我只是想自己装一个 GitHub」——Docker 一拉、Actions 兼容、indie hacker 标配 [[21]](https://www.serverspan.com/en/blog/the-2026-guide-to-self-hosted-git-gitea-forgejo-and-the-future-of-code-hosting)。
- **Forgejo**：community-governed 反 Gitea 公司治理的分叉版本 [[21]](https://www.serverspan.com/en/blog/the-2026-guide-to-self-hosted-git-gitea-forgejo-and-the-future-of-code-hosting)。
- **Sourcehut**：极简 + git send-email 邮件列表工作流，UI 在 Lynx 可用——面向开源原教旨主义维护者，市场份额排到 20 位之外 [[21]](https://www.serverspan.com/en/blog/the-2026-guide-to-self-hosted-git-gitea-forgejo-and-the-future-of-code-hosting)。

⚠ **解读**：Self-hosted 复兴的**驱动力不是性能也不是价格，而是数据主权**——欧盟 / APAC 政府客户、开源基金会、对 Copilot 训练数据合规有疑虑的研究机构、中国信创自主可控客户。Codeberg 30 万仓 vs GitHub 6.3 亿仓相差约 **2,000 倍**，规模上不会超过 GitHub 的 1%，但在「Agent 必须看到全仓 + 不能让数据外流」这一具体 Agent 场景里，self-hosted + 私有 LLM + 私有 attestation 链是唯一解。增长但不替代。

## 六、几条本质判断

**(1) L06a 的本质不是流量，是协议**。代码托管不按 PR / commit 计费，所以 986M commit / 43.2M PR / 1M Agent PR [[8]](https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/) 是**分发渠道厚度的指示器**而不是收入推算的基础。真正决定格局的是 Agent 时代被重写的四条协议——identity / signed commits / SLSA provenance / by-actor ruleset [[1]](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent), [[3]](https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/), [[4]](https://docs.github.com/en/actions/concepts/security/artifact-attestations), [[6]](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)。

**(2) GitHub 的护城河是双层而非单层**。分发渠道护城河（180M dev 默认目录 + Marketplace 过路费）解释为什么外部 Agent 必须来 GitHub 找用户；协议先发护城河解释来了之后必须按 GitHub 的接口跑。CodeRabbit / Greptile / Graphite 越成功，Marketplace 越值钱；Devin / Cursor / Codex 越成功，GitHub 协议层越被强化为事实标准。

**(3) GitLab 的「一站式」叙事破产但公司没破产**。FY2026 营收 +26%、ARR 过 $1B、自由现金流 +83% [[12]](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx) 证明监管严的客群仍然要单一应用。但增长降速到 +16%、协议层永远 fast-follower [[7]](https://about.gitlab.com/gitlab-duo-agent-platform/)，把 GitLab 重新定位成「监管客群现金牛」而不是「成长股」。

**(4) Bitbucket 被 Jira 既保护又限制**。Rovo Dev 在 Jira 重客户里能扳一局（PR cycle −30.8% 不是小数 [[18]](https://www.atlassian.com/blog/artificial-intelligence/developer-productivity-improved-with-rovo-dev)），但 15M / 180M 的基数差 [[9]](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/) + Atlassian 没拿出 Sigstore / by-actor ruleset 级的协议级承诺，让它永远是「Jira 用户的代码托管」。

**(5) Self-hosted 是数据主权利基不是革命**。Codeberg 30 万仓 vs GitHub 6.3 亿仓 [[9]](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/), [[19]](https://en.wikipedia.org/wiki/Codeberg) 相差 2,000 倍，但「Agent 训练数据主权 + 私有 LLM 全仓索引」两个 Agent 时代具体场景为 self-hosted 拓出真实付费缺口——欧盟数据主权与中国信创两个监管区是主战场。

---

## 参考文献

[1] GitHub Docs, "About GitHub Copilot coding agent," 2026. (Coding Agent opens PRs and pushes commits under its own bot identity; PR author / commit author surfaces Copilot.) [Online]. Available: <https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent>

[2] GitHub Community Discussion #179983, "How to prevent Copilot Coding Agent from being the main author of commits in master," 2025. (Co-authored-by: Copilot trailer on merged PRs.) [Online]. Available: <https://github.com/orgs/community/discussions/179983>

[3] GitHub Changelog, "Copilot cloud agent signs its commits," Apr. 3 2026. (Coding agent now works in repos with Require signed commits ruleset.) [Online]. Available: <https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/>

[4] GitHub Docs, "Artifact attestations," 2026. (Sigstore short-lived signing cert; public-good Sigstore for public repos / private Sigstore for private repos; SLSA build provenance.) [Online]. Available: <https://docs.github.com/en/actions/concepts/security/artifact-attestations>

[5] GitHub, "actions/attest-build-provenance," 2025. (Action generating build provenance attestations for workflow artifacts.) [Online]. Available: <https://github.com/actions/attest-build-provenance>

[6] GitHub Docs, "Available rules for rulesets," 2026. (Rulesets support by-actor conditions, required signed commits, required reviewers per actor.) [Online]. Available: <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets>

[7] GitLab, "GitLab Duo Agent Platform," 2026. (Planner / Security Analyst / Data Analyst / CI Pipeline Agent; model selection GA in 18.4.) [Online]. Available: <https://about.gitlab.com/gitlab-duo-agent-platform/>

[8] GitHub Blog, "What 986 million code pushes say about the developer workflow in 2025," 2025. (986M commits/yr +25.1% YoY; 43.2M merged PR/mo +23%; commit comments −27%; 1M+ Coding Agent PRs May–Sep 2025.) [Online]. Available: <https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/>

[9] GitHub Blog, "Octoverse: A new developer joins GitHub every second as AI leads TypeScript to #1," 2025. (180M+ devs, +36M/yr; 630M total repos, +121M in 2025; 230+ repos/min; 11.5B Actions minutes free.) [Online]. Available: <https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/>

[10] Motley Fool, "Why GitLab Stock Lost 33% in 2025," Jan. 2026. (FY2025 −33%; net new customer additions at four-year low; NRR decline.) [Online]. Available: <https://www.fool.com/investing/2026/01/20/why-gitlab-stock-lost-33-in-2025/>

[11] Benzinga, "GitLab Stock Tumbles Amid AI-Linked Restructuring," May 2026. (62.8% below 52-week high of $53.43; Act 2 restructuring.) [Online]. Available: <https://www.benzinga.com/trading-ideas/movers/26/05/52491665/gitlab-stock-tumbles-amid-ai-linked-restructuring>

[12] GitLab IR, "GitLab Reports Fourth Quarter and Full Year Fiscal Year 2026 Financial Results; Board of Directors Authorizes $400 million for Share Repurchase Program," Mar. 2026. (Revenue $955M +26%; ARR > $1B; Adj. FCF $220M +83%; non-GAAP op margin 17%; $100K+ ARR customers 1,456 +18%; $1M+ ARR customers 155 +26%; DBNR 118%; FY27 guide $1.099–1.118B +15–17%.) [Online]. Available: <https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx>

[13] BusinessWire, "Atlassian Announces First Quarter Fiscal Year 2026 Results," Oct. 2025. (Cloud Q1 FY26 revenue $998M +26% YoY.) [Online]. Available: <https://www.businesswire.com/news/home/20251030385606/en/Atlassian-Announces-First-Quarter-Fiscal-Year-2026-Results>

[14] MacroTrends, "Atlassian Revenue 2014-2025 | TEAM," 2025. (FY2025 revenue $5.215B +19.66% YoY; TEAM stock once −56% from peak.) [Online]. Available: <https://www.macrotrends.net/stocks/charts/TEAM/atlassian/revenue>

[15] Atlassian Work Life, "The 2025 Year in Review (and what's coming soon)," 2025. (15M developers on Bitbucket; Bitbucket Pipelines 1B+ build minutes/mo; three 2026 missions: AI-native SDLC / tool consolidation / enterprise trust.) [Online]. Available: <https://www.atlassian.com/blog/bitbucket/the-2025-year-in-review-and-whats-coming-soon>

[16] SiliconANGLE, "Atlassian gives Rovo AI a major upgrade and developers new tools," Oct. 8 2025. (Rovo Dev GA Oct 2025; cross Jira / Confluence / Bitbucket / Compass.) [Online]. Available: <https://siliconangle.com/2025/10/08/atlassian-gives-rovo-ai-major-upgrade-developers-new-tools/>

[17] Atlassian, "Rovo Dev | Agentic AI for software teams," 2026. [Online]. Available: <https://www.atlassian.com/software/rovo-dev>

[18] Atlassian Work Life, "30.8% Faster PRs: How AI-Driven Rovo Dev Code Reviewer Improved Developer Productivity at Atlassian," 2025. (PR cycle time −30.8%; human-written comments −35.6%.) [Online]. Available: <https://www.atlassian.com/blog/artificial-intelligence/developer-productivity-improved-with-rovo-dev>

[19] Wikipedia, "Codeberg," 2025. (As of Nov 2025: 300K+ repos, 200K+ registered accounts; largest Forgejo public instance.) [Online]. Available: <https://en.wikipedia.org/wiki/Codeberg>

[20] Forgejo, "Forgejo monthly report - October 2025," Oct. 2025. (1,930+ contributors over 3 yrs; NLnet €50,000 grant Apr 2025.) [Online]. Available: <https://forgejo.org/2025-10-monthly-report/>

[21] ServerSpan, "The 2026 Guide to Self-Hosted Git: Gitea, Forgejo, and the Future of Code Hosting," 2026. (Gitea rank #2 in self-hosted; Sourcehut rank #20; Forgejo fork from Gitea late 2024 over governance.) [Online]. Available: <https://www.serverspan.com/en/blog/the-2026-guide-to-self-hosted-git-gitea-forgejo-and-the-future-of-code-hosting>

[22] minware, "Average PRs Merged Per Developer," 2024. (Elite teams: 5+ PR/dev/week; Google median: 3 changes/week, 80th pct 7; Lyst median: 3 PR/week.) [Online]. Available: <https://www.minware.com/guide/metrics/average-prs-merged-per-developer>
