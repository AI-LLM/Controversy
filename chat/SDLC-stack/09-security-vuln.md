# 2026-05-14：SDLC 栈 / 安全与漏洞 (D3) 层深度研究

D3 层（漏洞 / 供应链 / 密钥）的市场盘子不取决于 PR 数量，而取决于两件事：攻击面的形态如何被 Coding Agent 重塑，信任结构如何在人类 reviewer、AI reviewer、工具调用沙盒、运行时行为证明之间迁移。本报告用两个分析视角串起 Snyk、Socket、GitGuardian、Semgrep、Endor Labs、Aikido、Veracode、Anthropic Claude Code Security、CodeQL/GitHub 的现状：一是**攻击面双扩张**（内生漏洞密度 + 外源供应链），二是**信任移交四级阶梯**。

## 1. 这一层的核心是信噪比 + MTTR

D3 层的价值由两个轴定义：**信噪比**——一次扫描里有多少是真阳性、值得人类 triage；**MTTR**——从发现到修复的时间。两者共同决定"扫描行为是否产生业务价值"，与 PR 数量无关。

**信噪比轴**：默认配置下的 SAST 误报极高——NIST 测过 Java SAST 工具误报率高达 78% [[1]](https://www.mobb.ai/blog/sast-tools-false-positive-comparison)；2024 年 Tolly 报告显示 Checkmarx 在基准应用上误报 36.3% [[1]](https://www.mobb.ai/blog/sast-tools-false-positive-comparison)；SonarQube 在 Java/TypeScript 默认配置下 40–60% 的发现被判定为非问题（⚠ 作者综合估算：SonarQube 官方自报"已审阅 issue"误报率 3.2%，与一线团队普遍体感存在落差；此处 40–60% 取行业从业者经验，非官方披露）；行业经验是"未调优 60–90%，调优后 10–20%" [[1]](https://www.mobb.ai/blog/sast-tools-false-positive-comparison)。**MTTR 轴**：Dark Reading 引用的数据是平均 MTTR 270 天 [[2]](https://www.darkreading.com/cyberattacks-data-breaches/mttr-most-important-security-metric)；Edgescan 给出 Critical 级 MTTR 约 65 天 [[3]](https://info.edgescan.com/vulnerability-statistics-li23)。CISA BOD 22-01 把 KEV 修复时限压到 14 天 [[34]](https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities)，是事实上的"上限红线"，多数私营公司远达不到。

⚠ 解读：40–78% 误报的工具即使运行 10× 频次也只产出 10× 噪声；270 天 MTTR 对 14 天 KEV 红线意味着扫得到也修不掉。这两个轴决定了 D3 厂商的 ARR 与 PR 流量本质上解耦——增长由**攻击面形态的变化**与**信任结构的迁移**驱动，per-PR 扫描位次是这两件事的结果，不是原因。后续两节分别展开这两个驱动。

## 2. 攻击面双扩张：内生 + 外源两条曲线

### 2.1 攻击面 a 段：AI 代码内生漏洞密度上涨

Snyk 2024 的研究显示，AI 生成的代码比人写的代码平均多 36% 安全问题，集中在 CWE-20 输入校验、CWE-79 输出编码 [[4]](https://devclass.com/2023/12/05/ai-assistants-write-insecure-code-that-humans-trust-too-much-snyk-survey-finds/)。Stanford 早在 2022 就发现接入 Codex 的参与者写出更不安全的解 [[5]](https://techcrunch.com/2022/12/28/code-generating-ai-can-introduce-security-vulnerabilities-study-finds/)。2025 年 arXiv 大规模分析 [[6]](https://arxiv.org/abs/2510.26103) 进一步指出 AI 代码"漏洞密度"系统性高于人写代码。复合效果：单位时间漏洞产出可能上涨 5–10×（⚠ 作者综合估算：以 AI 提速代码产出 3–5× × 漏洞密度 +36% 的乘数推得，无单一信源直接支撑该区间）。

a 段还有一个被低估的子项：**AI 误用包 / 误调 API**。GitGuardian State of Secrets Sprawl 2026 显示，2025 全年公开 GitHub 上新增 29,000,000 个硬编码 secrets，同比 +34%；其中 AI 服务 secret 涨 81% 到 1,275,105；**Claude Code 辅助 commit 的泄漏率 3.2%，是全 GitHub 基线 1.5% 的 2 倍多**；2022 年泄漏的 valid secrets 中 64% 到 2026 还没吊销 [[14]](https://blog.gitguardian.com/the-state-of-secrets-sprawl-2026/)。⚠ 解读：a 段的本质不是"Agent 写错代码"，而是"Agent 把外部世界（环境变量、SDK key、Stripe webhook）误以为是自己上下文的一部分写进了 repo"——这是一种新的语义漏洞，传统 SAST 规则集匹配不到。

### 2.2 攻击面 b 段：外源供应链 + prompt injection

b 段是攻击者侧的红利。**Slopsquatting**：USENIX Security 2025 一项 576,000 代码样本、16 个 LLM 的研究显示，AI 推荐的包名 19.7% 是不存在的——五分之一 [[7]](https://socket.dev/blog/slopsquatting-how-ai-hallucinations-are-fueling-a-new-class-of-supply-chain-attacks)。攻击者只需注册这些幻觉名字、塞入恶意 payload，等 Coding Agent 把它写进 `package.json`。Socket 2026 报告披露 2025 全年 npm 上发布了 454,648 个恶意包 [[7]](https://socket.dev/blog/slopsquatting-how-ai-hallucinations-are-fueling-a-new-class-of-supply-chain-attacks)。

**Shai-Hulud npm 蠕虫**：2025-09 起，"Shai-Hulud"劫持 `@ctrl/tinycolor` 等 500+ npm 包，利用 TruffleHog 抓取 AWS/GCP/Azure 凭证、用偷到的 npm token 自动感染同维护者的其他包 [[11]](https://www.stepsecurity.io/blog/ctrl-tinycolor-and-40-npm-packages-compromised)；11 月 Shai-Hulud 2.0 影响 25,000+ 恶意仓库、350+ 用户 [[12]](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/)；CISA 出官方告警 [[13]](https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem)。这是历史上最大规模的自传播 npm 攻击，且攻击模式天然契合 AI Agent 的"一键 `npm install`"工作流。

**Prompt injection 升级为 RCE**：2026 年 SecurityWeek 报道，Claude Code Security Review、Gemini CLI Action、GitHub Copilot Agent 三家主流"AI 评审员"都中招——攻击者构造一个含恶意指令的 PR 标题或评论，就能让评审 Agent 执行任意命令、把凭证当作"安全发现"上报 [[8]](https://www.securityweek.com/claude-code-gemini-cli-github-copilot-agents-vulnerable-to-prompt-injection-via-comments/)。Microsoft 同月披露 Semantic Kernel 里的 prompt injection 可升级为宿主级 RCE，一条 prompt 触发 calc.exe [[9]](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/)；Copilot Studio 的 CVE-2026-21520 是首批 indirect prompt injection CVE 之一 [[10]](https://venturebeat.com/security/microsoft-salesforce-copilot-agentforce-prompt-injection-cve-agent-remediation-playbook)。

⚠ 解读：b 段最致命的地方在于"攻击者只要操纵一个上游 npm 包 / 一个 PR 评论 / 一段 README"，就能拿到下游每一个 Coding Agent 的执行权限——传统 L09 的对手是"开发者粗心"，新的对手是**直接把 Agent 当成可编程的肉鸡**。a 段把漏洞引入"内部 = 自己 repo"，b 段把漏洞引入"外部 = 依赖 + 评审 + MCP 工具"，二者叠加才是 D3 总盘扩张的真正动力。

## 3. 信任移交：从人类 reviewer 到 behavioral integrity 的四级阶梯

L09 市场格局由**信任移交阶梯**决定。每升一级，旧台阶上的厂商就失去定价权，红利向新台阶迁移。

**台阶 1：人类 reviewer。**Pre-Agent 时代的默认假设——开发者写代码，另一个开发者 review，安全是"季度审计 + 偶尔的 SAST 扫"。在 PR 速度可控（人写）的世界里，这套是 working 的。但当 Agent 一晚上能开几十个 PR，人类 reviewer 直接饱和；这一层的厂商（纯规则 SAST 卖给安全部门做合规打勾）失去对开发流程的实际控制权。

**台阶 2：AI reviewer——LLM 作 triage 与生成。**核心命题是"让 AI 来 review AI 写的代码"。两条路线：

- **生成路线（Snyk / GitHub Autofix）**：扫到漏洞→LLM 生成补丁→PR 上 review→合并。Snyk Agent Fix 自称 80% 准确率、MTTR 下降 84%（开启 autofix 时）[[19]](https://snyk.io/blog/find-auto-fix-prioritize-intelligently-snyks-ai-powered-code/)；技术核心 CodeReduce 把上下文压缩后喂给 LLM，使开源 LLM 的修复表现超过 GPT-4 [[20]](https://snyk.io/blog/deepcode-ai-vulnerability-autofixing/)；2026-02 Snyk 宣布 AI Security Fabric 覆盖代码 / 模型 / Agent 三层 [[35]](https://snyk.io/news/snyk-ai-security-fabric/)。GitHub Copilot Autofix 绑定 CodeQL 规则集，覆盖 9 种主流语言 [[27]](https://docs.github.com/en/code-security/concepts/code-scanning/copilot-autofix-for-code-scanning)，自报有 fix 建议的漏洞修复速度 3× 普通，XSS 7×，SQL injection 12× [[28]](https://github.blog/news-insights/product-news/found-means-fixed-introducing-code-scanning-autofix-powered-by-github-copilot-and-codeql/)；2025-02 扩了 29% 的 alert 类型，autofix 数量整体 +8%、新类组 +270% [[29]](https://github.blog/changelog/2025-02-20-copilot-autofix-is-available-for-more-code-scanning-alerts/)。Anthropic Claude Code Security 2026-02 发布，"读代码像人类研究员"的语义分析，多阶段 self-verification 过滤误报，声称用 Opus 4.6 在开源代码库里发掘 500+ 历史漏洞 [[30]](https://www.anthropic.com/news/claude-code-security)。
- **triage 路线（Semgrep / Aikido）**：把 LLM 当成规则的"上下文层"而非生成器。Semgrep Autotriage 用 RAG + LLM 对 rule 元数据、过去的 triage 决定、findings 数据流上下文（几十行附近代码）做综合判断 [[21]](https://semgrep.dev/blog/2025/building-an-appsec-ai-that-security-researchers-agree-with-96-of-the-time/)；自报与安全研究员"真阳性"一致率 96%、误报识别准确率 >95% [[21]](https://semgrep.dev/blog/2025/building-an-appsec-ai-that-security-researchers-agree-with-96-of-the-time/)；triage 工作量首周降 20%、一周后降 40% [[22]](https://semgrep.dev/blog/2025/announcing-ai-noise-filtering-and-triage-memories/)。Aikido AutoTriage 自称降噪 95%（去重 + reachability + 上下文关联）[[36]](https://www.aikido.dev/blog/autotriage-and-the-swiss-cheese-model-of-security-noise-reduction)，Pro $600/月 / 10 用户 [[31]](https://www.aikido.dev/pricing)。Endor Labs 走的是 function-level call graph 路线——跨 40+ 语言，<9.5% 的漏洞真正可达，砍 90%+ 噪声 [[23]](https://www.endorlabs.com/use-cases/reachability-sca)，2026 推出 JavaScript phantom dependency 检测 [[24]](https://www.endorlabs.com/learn/javascript-typescript-nodejs-reachability-phantom-dependency-detection)。

**台阶 3：工具调用沙盒——ingress + blast-radius 控制。**台阶 2 解决"漏洞发现 / 修复"，但解决不了"Agent 主动作恶或被 prompt injection 劫持后干坏事"。台阶 3 的核心命题：信任不放在 Agent 输出上，而放在**Agent 能调到哪些工具、能访问什么网络出口、能改哪些文件**。Socket Firewall（2025-09 上线）在开发者机器本地 block 已确认的恶意包，AI 标记但未人工复核的只警告不阻断 [[17]](https://www.theregister.com/2025/09/30/socket_will_block_it_with/)；其行为分析覆盖每一个发布到 npm 的包的 install script、混淆代码、隐藏 payload、特权 API 调用，识别 70+ 风险信号，从发布到检出常常以分钟计 [[15]](https://docs.socket.dev/docs/socket-firewall-free)；phantom dependencies（在 `node_modules` 里被 `require()` 但没在 `package.json` 声明的包）会被单独打标 [[16]](https://docs.socket.dev/docs/phantom-dependencies)；Socket for GitHub 在 PR 维度监听 `package.json`/`yarn.lock` 变化，新依赖即触发评论 [[18]](https://docs.socket.dev/docs/socket-for-github)。GitGuardian 的 ggshield AI hook（2026-04 推出）专门 hook 进 Cursor / Copilot / Claude Code 的写盘瞬间，阻止 secret 被 commit 进 AI 生成的代码 [[26]](https://www.helpnetsecurity.com/2026/04/15/product-showcase-gitguardian-ggshield-ai-hook/)；其 ML 引擎用 Secret Enricher 模型对 generic secrets 做上下文分类 [[25]](https://docs.gitguardian.com/secrets-detection/secrets-detection-engine/machine_learning)。Claude Code 的产品设计本身——strict read-only by default、显式审批 [[33]](https://code.claude.com/docs/en/security)——就是把信任放在沙盒边界上的样本。主流共识是"没有银弹，只有 layered defense + blast-radius 缩小" [[8]](https://www.securityweek.com/claude-code-gemini-cli-github-copilot-agents-vulnerable-to-prompt-injection-via-comments/)。

**台阶 4：behavioral integrity——运行时证明 Agent / 制品没作恶。**SLSA/SBOM 解决 provenance，AI BOM 解决 origin tag，但"这段代码 / 这个 MCP tool 实际跑起来会不会偷东西"——目前没有标准。2025-11 Linux Foundation 发布 SLSA 1.2，分 build track 与 source track，原生支持 AI 增加的吞吐 [[32]](https://www.darkreading.com/application-security/sboms-in-2026-some-love-some-hate-much-ambivalence)。但有一道根本天花板：一个工具可以代码签名干净、provenance 完整、SBOM 准确，**所有制品完整性检查都通过，行为本身仍然可能恶意**——SLSA 不解决 behavioral integrity [[32]](https://www.darkreading.com/application-security/sboms-in-2026-some-love-some-hate-much-ambivalence)。这是 L09 下一个 12–24 个月才会成熟的台阶。

⚠ 解读：阶梯不是替代关系而是叠加关系——台阶 2 不替代台阶 1（仍然需要人最后签字），台阶 3 不替代台阶 2（仍然要扫漏洞）。但**每一层新台阶建立时，旧台阶上的"唯一价值"叙事破产**：纯 SAST 厂商一旦失去"我是 PR 安全的最后一道关"，价格就被压缩到合规线。

## 4. 厂商分层：四类卡位

把厂商按信任移交阶梯卡位排序：

- **语义层赢家（台阶 2，生成 / triage）**：Semgrep（96% AI triage 一致率）、Snyk（Agent Fix 80% 准确率 + AI Security Fabric）、GitHub Autofix（Copilot Autofix XSS 7×、SQLi 12×）、Claude Code Security（500+ 历史漏洞）。这一层吃的红利是 a 段（内生漏洞密度）+ AI reviewer 替代人类 reviewer。
- **triage / reachability 层赢家（台阶 2，专注降噪）**：Endor Labs（reachability 砍 90%+ 噪声）、Aikido（AutoTriage 降噪 95%）。卖点是"PR 流量涨 10× 时，让告警量不要也涨 10×"。
- **ingress 层赢家（台阶 3，工具调用沙盒）**：Socket（Firewall + 70+ 风险信号 + phantom dep）、GitGuardian（ggshield AI hook + AI service secret +81% 增量、3.2% Claude Code 泄漏率）、Snyk Broker。这一层吃的红利是 b 段（外源供应链 + prompt injection），与台阶 2 不冲突，常作为台阶 2 厂商的补足。
- **合规打勾出局者（台阶 1 残留）**：部分 legacy Veracode/Checkmarx SKU。仍有 SOC2/ISO 27001 审计需要的"出报告"用途，但不再决定 PR 流程，定价被压。

⚠ 解读：分层不一定是终局——Snyk 同时跨台阶 2（Agent Fix）+ 台阶 3（Broker），Socket 同时跨台阶 3（Firewall）+ 部分台阶 2（行为分析侧的"triage"），GitGuardian 同时跨 secrets 检测（台阶 2）+ AI hook 阻断（台阶 3）。最终格局更可能是 3–4 个全栈玩家 + 一批垂直专精玩家（Endor 守 reachability、Aikido 守 SMB 整合），而非"每个台阶一个赢家"。

## 5. 本质判断

**判断一：D3 增长来自双扩张，不来自 PR 流量。**a 段（内生漏洞密度 +36%、AI 服务 secret +81%、Claude Code commit 泄漏率 2× 基线）与 b 段（slopsquatting 19.7% 幻觉率、Shai-Hulud 500+ npm 包、prompt injection CVE 化）是两条同向放大的曲线。"per-PR 必经"是这两个扩张作用在 PR 工作流上的**结果**——D3 厂商真正卖的，是"在攻击面新扩出的两块上提供检测 / 修复 / 阻断"。

**判断二：赢家归属由信任移交阶梯卡位决定，不由扫描频次决定。**信任结构从"人类 reviewer"经"AI reviewer + 工具调用沙盒"逐级让渡到"behavioral integrity"。卡到正确台阶的厂商吃整条增长，卡错台阶的（仍然把自己定义为"给安全部门出报告的扫描器"）被压缩为合规打勾。Semgrep / Snyk / GitHub Autofix 卡台阶 2，Socket / GitGuardian / Snyk Broker 卡台阶 3，台阶 4 还在等候新进入者。

**判断三：供应链是新的零日。**Shai-Hulud、slopsquatting、phantom dependencies 三件套表明攻击者已经把"AI 推荐 + 自动 install"当成主入侵向量。npm/PyPI 的"open by default"模型与 Coding Agent 的"trust by default"行为正面冲突。未来 12 个月会看到更多"firewall 式"产品（Socket Firewall、Snyk Broker、GitGuardian MCP），即在 Agent 工具调用层做 ingress 控制，而非事后扫描——这是台阶 3 的红利继续兑现。

**判断四：Behavioral integrity 是下一个未被解决的问题。**SLSA/SBOM 解决 provenance，AI BOM 解决 origin tag，但"这段代码 / 这个 MCP tool 实际跑起来会不会偷东西"目前没有标准。这会催生一个全新子类：runtime attestation 与 agent sandbox（候选玩家：Edera、Chainguard、StackHawk + 新创公司）。⚠ 解读：台阶 4 一旦成熟，台阶 2 的"AI reviewer"地位会被进一步弱化——既然能在运行时证明无害，那么静态发现漏洞的优先级会下降，台阶 3 + 台阶 4 的"边界控制 + 行为证明"组合会成为新的事实标准。

## 参考文献

[1] Mobb, "Top SAST Tools Compared by False Positive Rate," 2025. (NIST Java 78%; Checkmarx 36.3% Tolly 2024; SonarQube 40–60% default.) [Online]. Available: <https://www.mobb.ai/blog/sast-tools-false-positive-comparison>

[2] E. Chickowski, "MTTR: The Most Important Security Metric," *Dark Reading*. (Average MTTR ~270 days.) [Online]. Available: <https://www.darkreading.com/cyberattacks-data-breaches/mttr-most-important-security-metric>

[3] Edgescan, "Vulnerability Statistics Report." (Critical MTTR 65 days.) [Online]. Available: <https://info.edgescan.com/vulnerability-statistics-li23>

[4] T. Claburn, "Snyk survey: AI Assistants write insecure code that humans trust too much," *DEVCLASS*, Dec. 2023. (AI 代码安全问题 +36%.) [Online]. Available: <https://devclass.com/2023/12/05/ai-assistants-write-insecure-code-that-humans-trust-too-much-snyk-survey-finds/>

[5] K. Wiggers, "Code-generating AI can introduce security vulnerabilities, study finds," *TechCrunch*, Dec. 2022. [Online]. Available: <https://techcrunch.com/2022/12/28/code-generating-ai-can-introduce-security-vulnerabilities-study-finds/>

[6] Authors, "Security Vulnerabilities in AI-Generated Code: A Large-Scale Analysis of Public GitHub Repositories," *arXiv preprint*, arXiv:2510.26103, Oct. 2025. [Online]. Available: <https://arxiv.org/abs/2510.26103>

[7] Socket, "The Rise of Slopsquatting: How AI Hallucinations Are Fueling a New Class of Supply Chain Attacks." (USENIX Security 2025: 576k samples, 16 LLMs, 19.7% hallucinated packages; 454,648 malicious npm packages 2025.) [Online]. Available: <https://socket.dev/blog/slopsquatting-how-ai-hallucinations-are-fueling-a-new-class-of-supply-chain-attacks>

[8] R. Lakshmanan, "Claude Code, Gemini CLI, GitHub Copilot Agents Vulnerable to Prompt Injection via Comments," *SecurityWeek*, 2026. [Online]. Available: <https://www.securityweek.com/claude-code-gemini-cli-github-copilot-agents-vulnerable-to-prompt-injection-via-comments/>

[9] Microsoft Security, "When prompts become shells: RCE vulnerabilities in AI agent frameworks," May 7, 2026. [Online]. Available: <https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/>

[10] L. Columbus, "Microsoft patched a Copilot Studio prompt injection. The data exfiltrated anyway," *VentureBeat*. (CVE-2026-21520, CVSS 7.5.) [Online]. Available: <https://venturebeat.com/security/microsoft-salesforce-copilot-agentforce-prompt-injection-cve-agent-remediation-playbook>

[11] StepSecurity, "Shai-Hulud: Self-Replicating Worm Compromises 500+ NPM Packages." (始于 @ctrl/tinycolor, 2025-09-14.) [Online]. Available: <https://www.stepsecurity.io/blog/ctrl-tinycolor-and-40-npm-packages-compromised>

[12] Palo Alto Unit 42, "'Shai-Hulud' Worm Compromises npm Ecosystem in Supply Chain Attack (Updated November 26)." (Shai-Hulud 2.0: 25,000+ repos, 350+ users.) [Online]. Available: <https://unit42.paloaltonetworks.com/npm-supply-chain-attack/>

[13] CISA, "Widespread Supply Chain Compromise Impacting npm Ecosystem," Sep. 23, 2025. [Online]. Available: <https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem>

[14] GitGuardian, "The State of Secrets Sprawl 2026." (29M new secrets 2025, +34% YoY; AI-service secrets +81% to 1,275,105; Claude Code commit 泄漏率 3.2% vs 1.5%; 64% 2022 valid secrets 未吊销.) [Online]. Available: <https://blog.gitguardian.com/the-state-of-secrets-sprawl-2026/>

[15] Socket, "Socket Firewall Free." [Online]. Available: <https://docs.socket.dev/docs/socket-firewall-free>

[16] Socket, "Phantom Dependencies." [Online]. Available: <https://docs.socket.dev/docs/phantom-dependencies>

[17] T. Claburn, "Socket will block malicious packages with free firewall," *The Register*, Sep. 30, 2025. [Online]. Available: <https://www.theregister.com/2025/09/30/socket_will_block_it_with/>

[18] Socket, "Guide to Socket for GitHub." [Online]. Available: <https://docs.socket.dev/docs/socket-for-github>

[19] Snyk, "Find, auto-fix, and prioritize intelligently, with Snyk's AI-powered code security tools." (Agent Fix 80% accuracy; MTTR -84%.) [Online]. Available: <https://snyk.io/blog/find-auto-fix-prioritize-intelligently-snyks-ai-powered-code/>

[20] Snyk, "More accurate than GPT-4: How Snyk's CodeReduce improved the performance of other LLMs." [Online]. Available: <https://snyk.io/blog/deepcode-ai-vulnerability-autofixing/>

[21] Semgrep, "How we built an AppSec AI that security researchers agree with 96% of the time," 2025. [Online]. Available: <https://semgrep.dev/blog/2025/building-an-appsec-ai-that-security-researchers-agree-with-96-of-the-time/>

[22] Semgrep, "Announcing an AI AppSec engineer that users agree with 95% of the time," 2025. (Triage 工作量 -20%/-40%.) [Online]. Available: <https://semgrep.dev/blog/2025/announcing-ai-noise-filtering-and-triage-memories/>

[23] Endor Labs, "SCA with Reachability." (<9.5% 漏洞可达，>90% 噪声降幅.) [Online]. Available: <https://www.endorlabs.com/use-cases/reachability-sca>

[24] Endor Labs, "Introducing JavaScript Reachability and Phantom Dependency Detection." [Online]. Available: <https://www.endorlabs.com/learn/javascript-typescript-nodejs-reachability-phantom-dependency-detection>

[25] GitGuardian, "Machine learning – GitGuardian documentation." [Online]. Available: <https://docs.gitguardian.com/secrets-detection/secrets-detection-engine/machine_learning>

[26] Help Net Security, "Stop secrets from leaking through AI coding tools with GitGuardian," Apr. 15, 2026. [Online]. Available: <https://www.helpnetsecurity.com/2026/04/15/product-showcase-gitguardian-ggshield-ai-hook/>

[27] GitHub, "About Copilot Autofix for code scanning." [Online]. Available: <https://docs.github.com/en/code-security/concepts/code-scanning/copilot-autofix-for-code-scanning>

[28] GitHub, "Found means fixed: Introducing code scanning autofix, powered by GitHub Copilot and CodeQL." (3× / XSS 7× / SQLi 12×.) [Online]. Available: <https://github.blog/news-insights/product-news/found-means-fixed-introducing-code-scanning-autofix-powered-by-github-copilot-and-codeql/>

[29] GitHub Changelog, "Copilot Autofix is available for more code scanning alerts," Feb. 20, 2025. (覆盖 +29% alert 类型，autofix +270% on new group.) [Online]. Available: <https://github.blog/changelog/2025-02-20-copilot-autofix-is-available-for-more-code-scanning-alerts/>

[30] Anthropic, "Making frontier cybersecurity capabilities available to defenders," 2026. (Opus 4.6 在开源代码中发现 500+ 历史漏洞.) [Online]. Available: <https://www.anthropic.com/news/claude-code-security>

[31] Aikido Security, "Pricing." [Online]. Available: <https://www.aikido.dev/pricing>

[32] R. Lemos, "SBOMs in 2026: Some Love, Some Hate, Much Ambivalence," *Dark Reading*. (SLSA 1.2 build/source track; AI BOM 概念；behavioral integrity 未解.) [Online]. Available: <https://www.darkreading.com/application-security/sboms-in-2026-some-love-some-hate-much-ambivalence>

[33] Anthropic, "Security – Claude Code Docs." (Strict read-only by default, explicit permission.) [Online]. Available: <https://code.claude.com/docs/en/security>

[34] CISA, "BOD 22-01: Reducing the Significant Risk of Known Exploited Vulnerabilities," Nov. 2021. (KEV 列入后默认 14 天修复时限，部分早期条目最长 6 个月.) [Online]. Available: <https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities>

[35] Snyk, "Snyk Unveils the AI Security Fabric: An Adaptive System to Unleash AI Innovators Securely," Feb. 3, 2026. (AI Security Fabric 覆盖代码 / 模型 / Agent.) [Online]. Available: <https://snyk.io/news/snyk-ai-security-fabric/>

[36] Aikido Security, "AutoTriage and the Swiss Cheese Model of Security Noise Reduction." (AutoTriage 降噪 95%：去重 + reachability + 上下文关联.) [Online]. Available: <https://www.aikido.dev/blog/autotriage-and-the-swiss-cheese-model-of-security-noise-reduction>
