# 2026-05-14：SDLC 栈 / IDE 与 AI 编辑器 层深度研究

本篇覆盖 D8（IDE）与 D7'（AI 编辑器）两层。问题不是"AI 把补全做得更准了"，也不是"谁的 MAU 最高"——把 L04 当流量层来看会错过这一年真正发生的事。**这一层在做三段位移**：(1) **宿主权**：fork 派全部跑在微软的渲染器上，扩展点设计成了真护城河；(2) **控制台化**：Cursor 2.0 把叙事从"更好的编辑器"切到"管理多 agent 的控制台"；(3) **agent 上移**：Claude Code / Codex CLI / Devin 从终端和 web 釜底抽薪，把"IDE"这个壳本身的并购估值打塌。Cursor 三年从 0 做到 20 亿美元 ARR [[1]](https://thenextweb.com/news/cursor-anysphere-2-billion-funding-50-billion-valuation-ai-coding) 是结果，但这层的真正问题是：**形态在重写**，而 fork、控制台、CLI 是这场重写的三个时间切片。

## 一、宿主权悖论：fork 派全部跑在微软的渲染器上

L04 的本质不是流量。微软自己公布 Visual Studio + VS Code 合计 5000 万 MAU、VS Code 单独约 1400 万 MAU [[2]](https://www.thurrott.com/dev/321070/visual-studio-and-visual-studio-code-have-50-million-maus)；JetBrains 2024 年底披露全家桶 1140 万 recurring active users，财富全球 100 强中 88 家是客户 [[3]](https://finance.yahoo.com/news/jetbrains-presents-2024-annual-highlights-170000221.html)，第三方对其 ARR 的估算在 ~2.52 亿美元（保守口径）到 ~5.9 亿美元（含永久许可）之间 [[4]](https://getlatka.com/companies/jetbrains.com)。这些数字告诉你的是市场规模，**告诉不了你的是为什么 Cursor 三年走到 $50B 估值**——后者跟流量基本无关。

真正的悖论在于：所有挑战者都 fork 自微软。Cursor、Windsurf 都是从 VS Code OSS 完整 fork，**不是 extension**——这一点决定了它们能做、Copilot 做不到的事（见 §2）。结果是：微软真正的资产不是 Copilot，而是"几乎所有 AI 编辑器都跑在我开源的渲染器上"。一个 fork 派每多卖一份 license，VS Code 内核的中心地位就被加固一分。这就是 L04 第一阶段的护城河——**不是流量的护城河，是扩展点设计的护城河**。

但要注意它的脆性。VS Code 的扩展宿主是为"插件 + 单光标"设计的，AI 编辑器需要"多 agent + 后台 VM + 并行 diff overlay"——一旦 fork 派把内核改到与上游差异巨大（Cursor 已经改了渲染管线、文件系统拦截、扩展宿主），它们对微软的依赖也会逐步减弱。Zed 走更极端的赌注：完全脱离 VS Code，用 Rust 重写、GPU 渲染、120 fps、零 Electron，2026 年 4 月 29 日发 1.0 [[23]](https://www.theregister.com/2026/04/30/zed_team_releases_version_10/)。这是宿主权阶段的终局信号。

⚠ 解读：把上一代补全工具的死法也放在这里看更清楚。Kite 自述 Python 场景"提升 18% 生产力"（2019 营销口径，未独立复核），2022 年 11 月关闭并开源——500k 用户没人愿意付费 [[26]](https://devclass.com/2022/11/21/kite-ai-coding-pulled-down-to-earth-because-our-500k-developers-would-not-pay-to-use-it-now-open-source/)；Codota 2019 年 12 月收购 Tabnine、2021 年 5 月公司更名为 Tabnine [[27]](https://en.wikipedia.org/wiki/Tabnine)。这一代基于规则 / 浅层 ML、单 token 预测的工具，**不是输给 LLM 本身，是输给 LLM 让"重画编辑器形态"成为可能**——它们没有抢宿主权，只做了浅层叠加。

## 二、形态自由度：Cursor 能做、Copilot 不能做的四件事

GitHub Copilot 在 2025 年 7 月跨过 2000 万总用户线，2026 年 1 月微软 FY26 Q2 财报披露**付费订阅 470 万**（vs FY24 的 180 万）[[5]](https://techcrunch.com/2025/07/30/github-copilot-crosses-20-million-all-time-users/)。企业部署研究测得**建议接受率 27-33%、行级接受率约 20%**，96% 的开发者每天至少接受一条 [[6]](https://arxiv.org/html/2501.13282v1)。这是 extension 派能达到的密度天花板。

Cursor 在 2026 年 4 月披露**日活破百万、付费用户超百万、ARR 突破 20 亿美元**，从 2025 年 1 月的 1 亿 ARR 起步，14 个月走完 [[7]](https://research.contrary.com/company/cursor)。问 Microsoft 为何拥有 GitHub、Azure OpenAI、最便宜的 Copilot（$10/月起）仍然只能跟随——答案不是节奏，是**形态自由度**。fork 让 Cursor 能做四件事而 extension 派做不到 [[11]](https://medium.com/data-science-collective/how-cursor-actually-works-c0702d5d91a9)：

1. **改写渲染管线**：diff overlay 直接叠在源文件上、不进侧栏，光标体验不被切断。
2. **拦截文件系统**：让 background agent 在云端 VM 里写文件而不冲击 unsaved buffer——extension API 没有这个钩子。
3. **重写扩展宿主**：允许 multi-agent 共享同一项目状态、同一 token 池。
4. **绑自研补全模型与 speculative edits**：Cursor Tab 训练在数十亿条编辑序列上，预测"下一跳"（jump）而不是只预测 token；配合 Fireworks 的 speculative decoding，把 apply 速率推到 **~1000 token/s** [[12]](https://fireworks.ai/blog/cursor)。这种端到端栈对接，extension 派受制于 VS Code 公开 API。

`.cursorrules`（legacy）和 `.cursor/rules/*.mdc`（新结构）是注入 system prompt 的机制。最小 MDC 文件：

```
---
description: RPC service boilerplate
globs:
  - "src/rpc/**/*.ts"
alwaysApply: false
---
- Use our internal RPC pattern when defining services
- Always use snake_case for service names
```

`alwaysApply: true` 无条件附加每个 turn；`globs` 决定按文件路径自动激活；嵌套目录下的 `.cursor/rules` 在相关文件被引用时自动追加 [[15]](https://cursor.com/docs/context/rules)。这是 Cursor 把"团队规范"嵌入提示词的工程接口——版本化、目录化、glob 触发——是 Copilot Custom Instructions 的对位物，但工程深度高一个量级。

价格上 Cursor 并不便宜：Hobby $0 / Pro $20 / Pro+ $60 / Ultra $200 / Teams $40 per seat / Enterprise 定价。2025 年 6 月 Cursor 完成关键定价转折：从"固定 fast request 配额"换成"按模型实际 API 成本计费的 usage-based credit"——成本压力传给重度用户、轻度用户体验保住 [[16]](https://www.vantage.sh/blog/cursor-pricing-explained)。这套定价能跑通，**前提是 fork 派形态自由度撑得起 $20-200/月的差异化体验**。

## 三、控制台化：从补全器到 agent orchestration

L04 的第二段位移发生在 2025 年下半年。Cursor 2.0（2025-10-29）的发布博客把核心叙事从"更好的编辑器"切到"**管理多 agent 的控制台**"[[13]](https://cursor.com/blog/2-0)。这不是营销话术，是产品形态的根本切换——四个组件构成新的"控制台"：

1. **Cursor Tab**：专有补全模型，预测下一跳；speculative edits ~1000 token/s [[12]](https://fireworks.ai/blog/cursor)。这是控制台里的"快编辑"通道。
2. **Composer Agent**：2025-10-29 自研 Composer 模型，MoE + RL + MXFP8 量化，号称同等智力下比通用模型快 4×，大部分回合 < 30 秒 [[13]](https://cursor.com/blog/2-0)。这是控制台里的"中等任务"通道。
3. **Background Agent / 多 agent 接口**：允许同时跑最多 **8 个 agent**，各自占一个 git worktree 或远端 VM、分别开 PR；2.4 之后引入 subagent，可树状递归（自定义 subagent 继承父 agent 的 Task tool 即可继续派生）[[28]](https://cursor.com/changelog)。⚠ 解读："树状递归"系作者从官方 changelog + 论坛讨论综合推断，官方未明确使用该措辞。这是控制台里的"长任务"通道。
4. **Context Engine**：Tree-sitter 按函数 / 类边界切片，向量索引整库；客户端将相关切片**加密**后发到 backend，backend 在 enclave 内解密喂模型。Privacy Mode 下 zero data retention（与 OpenAI / Anthropic 等供应商签 ZDR 合同）[[14]](https://cursor.com/security)。这是控制台的"共享上下文"层。

控制台化不止 Cursor 在做。JetBrains 走另一路：**AI Assistant**（嵌入式补全 / 聊天，覆盖 IntelliJ 全家桶 + Android Studio + VS Code 扩展，$10-30/月）+ **Junie**（自主 agent，2025-07 GA）[[21]](https://www.jetbrains.com/junie/)。Junie 2025 年底引入 MCP 支持、GitHub 异步集成（无需开 IDE 即可派单），2025 年 12 月把 Junie UI 并入 AI Chat [[22]](https://blog.jetbrains.com/ai/2025/12/junie-now-integrated-into-the-ai-chat/)。Zed 1.0 的 Threads 侧栏更彻底：并行 agent，支持 Anthropic Claude Agent、OpenAI Codex、OpenCode、Cursor agent，通过新提出的 **Agent Client Protocol (ACP)** 统一接入 [[23]](https://www.theregister.com/2026/04/30/zed_team_releases_version_10/)。

⚠ 解读：控制台化对 L04 的真正含义是——"编辑器"这个名字开始不准确。Cursor 2.0、Junie、Zed Threads 都把视觉中心从"光标 + 文件"移到"任务卡片 + agent 状态 + diff 队列"，光标变成了 agent 失败时的兜底操作面。这同时回答了为什么补全接受率（27-33%）不再是关键指标：**控制台时代的指标是"task throughput × 一次性通过率"**，不是 token 命中率。

## 四、上移威胁：CLI agent 釜底抽薪 IDE 本体

控制台化看起来是 IDE 的胜利，但同一时间发生了第三段位移：**agent 跑出 IDE，到 CLI / Web / GitHub PR 入口**。Claude Code、Codex CLI、Gemini Code、Devin 不需要编辑器壳——它们在终端、PR comment、Slack 里就能完成"任务输入 → diff 输出"的回路。当 agent 占主导、编辑器退化为 agent 的可视化界面，那 VS Code fork 的形态自由度优势就被绕过：**反正你最后看的是 PR diff，IDE 的 overlay 是不是更精致没人关心**。

Windsurf 的并购故事是这条逻辑的早期信号。Codeium（2021 年由 Varun Mohan、Douglas Chen 创立，前名 Exafunction，做 GPU 虚拟化）在 2022 年转向 AI 代码补全，2024 年 11 月发布 Windsurf Editor——VS Code fork，主打 Cascade（深度代码理解）+ Flows（在 copilot 与 agent 模式间流动）[[18]](https://research.contrary.com/company/windsurf)。2025 年 7 月 72 小时连续剧：

1. OpenAI 提出 **30 亿美元**收购，最终散场
2. **Google 用 24 亿美元做"反向 acqui-hire"**：以技术许可形式给 Windsurf 投资人 12 亿美元，另 12 亿打包成约 40 名核心员工（含两位创始人）加入 Google DeepMind 的薪酬包；**不收股权**
3. 剩下的公司壳 + 全员 + IP 被 Cognition（Devin 的母公司）以**约 2.5 亿美元**接走 [[19]](https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/)

两个月后 Cognition 估值跳到 102 亿美元 [[20]](https://www.cnbc.com/2025/09/08/cognition-valued-at-10point2-billion-two-months-after-windsurf-.html)。这三段切割揭示的不是"反垄断绕道"那么简单——揭示的是 **IDE 本体的并购价值在塌陷**：$3B → $2.4B 人 → $250M 壳。创始团队 + 模型团队被估到 IDE editor 产品线的约 10×。中间层（VS Code fork + agent UI）在头部模型公司眼里**可被绕过**，因为他们自己的 CLI agent 就足以承担入口。

这对 L04 玩家的策略含义是分裂的。Cursor 的回应是**自研 Composer + 企业 control plane**（见 §5），把"控制台"做成 agent 不可绕过的中枢；Zed 的回应是 **ACP**，让任何 agent 接进来、降低对单一 CLI 的依赖；JetBrains 的回应是 **Junie + 语言深度**，赌 CLI agent 在静态分析精度上仍差一档。

⚠ 解读：AI 贡献代码占比的产业大数（Google 75% [[8]](https://www.breitbart.com/tech/2026/04/24/google-says-75-percent-of-fresh-code-now-generated-by-ai/)、Microsoft 内部 20-30% 升至 50% [[9]](https://techcrunch.com/2025/04/29/microsoft-ceo-says-up-to-30-of-the-companys-code-was-written-by-ai/)、行业头部 25-30% [[10]](https://medium.com/@sohail_saifi/ai-writes-30-of-microsofts-code-and-25-of-google-s-6909f6e0b406)）混淆"AI 起草并被接受"与"AI 起草后被人改写"，本身是营销修辞，不要直接推算"工程师产能翻 N 倍"。但这些数字间接支持上移趋势：当 75% 的新代码经 AI 起草，**起草入口在哪里**就成了关键，而 CLI / PR comment 入口正在和 IDE 抢这个位置。

## 五、谁守得住：三条不同的赌注

L04 的下一段已经在分流。三条赌注、三个押法：

**Cursor 押"企业 control plane"**。$50B 估值押的不是补全，是企业 control plane。2026 年披露已渗透 **64% 财富 500 / 近 70% 财富 1000**，客户含 NVIDIA、Uber、Adobe、Salesforce、PwC [[17]](https://cursor.com/enterprise)。Privacy Mode + ZDR + SOC 2 Type II + pooled usage 这套组合直接对位企业采购清单。Copilot 同样有 Enterprise SKU，但企业更倾向"和 GitHub 数据访问解耦"——这点上 Cursor 反而把劣势变优势。Pro 个人订阅 + usage credit 撑不到 $6B ARR，必然靠 Teams / Enterprise SKU 的 seat × pooled usage——这意味着 Cursor 下一阶段会越来越像 Datadog，卖给 CIO + Security，不是开发者本人。控制台化在企业语境里的价值远比在个人语境里高：CIO 要的是"一个面板看所有 agent 的活动 + 合规审计"，正好是控制台叙事。

**JetBrains 押"语言深度"**。优势是深度语言索引（IntelliJ 的静态分析比 tree-sitter 强出一个量级），劣势是 JetBrains 不 fork 自己——AI 是叠加层，无法重画编辑器形态。如果 LLM 把语义分析做到与 IntelliJ 静态分析同等精度，JetBrains 的二十年护城河被填平；目前 LLM 还差 1-2 代，但这是确定性的时间问题。Junie 把"agent + 本地深度索引"绑在一起，赌的是 CLI agent 在跨函数 / 跨包重构上仍需借助 IDE 的静态分析。

**Zed 押"新形态 + 协议"**。Rust + GPU 渲染解决性能门槛，ACP 解决 agent 异构问题。团队来自 GitHub Atom + Tree-sitter，押"agentic 时代需要新形态编辑器，而不是给老编辑器装外挂"。即使 1.0 已发，市场份额仍远不及 fork 派；脱离 VS Code 需要的不仅是更快的渲染器，还要重建几千个 LSP / DAP / 主题 / 调试器扩展生态——5-10 年量级的迁移。

开源 / 小众阵营在三条赌注之外：**Cline**（VS Code 扩展，不 fork，Apache 2.0，58k stars）、**Continue.dev**（31k stars）、**Cody**（靠 Sourcegraph 代码图谱做检索增强）、**Aider**（CLI 形态，41k stars，位置上接近 D6.5 CLI agent 而非严格 IDE）[[24]](https://www.opensourcealternatives.to/blog/best-open-source-ai-coding-assistants)。它们是分布式赌注：Cline 押"extension 也能跑 agent"，Aider 直接押"CLI 上移"——后者其实就是 §4 上移威胁的开源版本。

横跨三条赌注的共同基础设施：**MCP**。Cursor / Junie / Zed 都把 MCP 当一等公民，2026 年 3 月生态 5000+ 社区 server [[25]](https://cursor.com/docs/mcp)。MCP 是 L04 与 L05（agent layer）的解耦协议——它在事实上承认了"agent 可以跨编辑器"，进而支撑了 ACP 的出现。

⚠ 解读：三段位移的时间排序值得记下来——宿主权（2022-2024）→ 控制台化（2025）→ 上移（2025-2026）。每一段都没有杀死上一段，而是把上一段的护城河重新定价。L04 在 2026 年的真正问题不是"哪个编辑器赢"，而是"editor 这一层值多少钱"。Windsurf 三段切割已经给了一个数：壳 $250M、人 $2.4B、未实现的整合期望值 $3B。**editor 本体在向下挤压、agent 入口在向上吸纳**，控制台是中间的暂态。这层在 5 年后是不是还叫"IDE"都不一定。

## 参考文献

[1] N. Nelson, "Cursor in talks to raise $2B at $50B valuation after hitting $2B ARR in three years," *The Next Web*, Apr. 2026. [Online]. Available: <https://thenextweb.com/news/cursor-anysphere-2-billion-funding-50-billion-valuation-ai-coding>

[2] P. Thurrott, "Visual Studio and Visual Studio Code Have 50 Million MAUs," *Thurrott.com*, May 2025. (Combined VS + VS Code 50M MAU; VS Code 单独约 14M MAU.) [Online]. Available: <https://www.thurrott.com/dev/321070/visual-studio-and-visual-studio-code-have-50-million-maus>

[3] JetBrains, "JetBrains Presents 2024 Annual Highlights — 11.4M Developers Globally," Yahoo Finance press release, Dec. 2024. [Online]. Available: <https://finance.yahoo.com/news/jetbrains-presents-2024-annual-highlights-170000221.html>

[4] Latka, "JetBrains Revenue 2024: $252M ARR Estimate," *getlatka.com*. [Online]. Available: <https://getlatka.com/companies/jetbrains.com>

[5] R. Wiggers, "GitHub Copilot crosses 20M all-time users," *TechCrunch*, Jul. 30, 2025. (FY26 Q2 微软披露付费 4.7M.) [Online]. Available: <https://techcrunch.com/2025/07/30/github-copilot-crosses-20-million-all-time-users/>

[6] V. Murali et al., "Experience with GitHub Copilot for Developer Productivity at Zoominfo," *arXiv*, arXiv:2501.13282, Jan. 2025. (建议接受率 27-33%，行级 ~20%；96% 开发者每日接受 ≥1.) [Online]. Available: <https://arxiv.org/html/2501.13282v1>

[7] Contrary Research, "Cursor Business Breakdown & Founding Story," 2026. (1M DAU、20 亿 ARR、9900% YoY.) [Online]. Available: <https://research.contrary.com/company/cursor>

[8] L. Nolan, "Google Says 75% of Fresh Code Now Generated by AI," *Breitbart Tech*, Apr. 24, 2026. [Online]. Available: <https://www.breitbart.com/tech/2026/04/24/google-says-75-percent-of-fresh-code-now-generated-by-ai/>

[9] J. Bommasani, "Microsoft CEO says up to 30% of the company's code was written by AI," *TechCrunch*, Apr. 29, 2025. [Online]. Available: <https://techcrunch.com/2025/04/29/microsoft-ceo-says-up-to-30-of-the-companys-code-was-written-by-ai/>

[10] S. Saifi, "AI Writes 30% of Microsoft's Code and 25% of Google's. So, Why Are Their Engineer Headcounts Not Dropping?," *Medium*, 2026. [Online]. Available: <https://medium.com/@sohail_saifi/ai-writes-30-of-microsofts-code-and-25-of-google-s-6909f6e0b406>

[11] Data Science Collective, "How Cursor Actually Works: Architecture and Engineering," *Medium*, 2026. (Priompt、Tree-sitter、Background Agent VM 等架构细节.) [Online]. Available: <https://medium.com/data-science-collective/how-cursor-actually-works-c0702d5d91a9>

[12] Fireworks AI, "How Cursor built Fast Apply using the Speculative Decoding API." (~1000 token/s apply 速率.) [Online]. Available: <https://fireworks.ai/blog/cursor>

[13] Cursor (Anysphere), "Introducing Cursor 2.0 and Composer," *Cursor Blog*, Oct. 29, 2025. (Composer MoE + RL + MXFP8；4× 同等智力速度；最多 8 个并行 agent.) [Online]. Available: <https://cursor.com/blog/2-0>

[14] Cursor, "Security." (Privacy Mode、ZDR、SOC 2 Type II.) [Online]. Available: <https://cursor.com/security>

[15] Cursor Docs, "Rules — MDC 格式." [Online]. Available: <https://cursor.com/docs/context/rules>

[16] Vantage, "Cursor Pricing Explained 2026." (2025-06 切换 usage-based credit；五档价目.) [Online]. Available: <https://www.vantage.sh/blog/cursor-pricing-explained>

[17] Cursor, "Cursor for Enterprise — Trusted by 64% of Fortune 500 companies." (~70% Fortune 1000；NVIDIA/Uber/Adobe/Salesforce/PwC.) [Online]. Available: <https://cursor.com/enterprise>

[18] Contrary Research, "Windsurf Business Breakdown & Founding Story." (2021 创立 Exafunction → 2022 转 AI 代码 → 2024-11 发布 Windsurf Editor.) [Online]. Available: <https://research.contrary.com/company/windsurf>

[19] R. Wiggers, "Cognition, maker of the AI coding agent Devin, acquires Windsurf," *TechCrunch*, Jul. 14, 2025. (Cognition ~$250M 收 Windsurf 残余；Google $2.4B 反向 acqui-hire ~40 人.) [Online]. Available: <https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/>

[20] J. Novet, "Cognition valued at $10.2 billion two months after Windsurf purchase," *CNBC*, Sep. 8, 2025. [Online]. Available: <https://www.cnbc.com/2025/09/08/cognition-valued-at-10point2-billion-two-months-after-windsurf-.html>

[21] JetBrains, "Junie, the AI coding agent by JetBrains." [Online]. Available: <https://www.jetbrains.com/junie/>

[22] JetBrains, "Junie Now Integrated Into the AI Chat," *JetBrains AI Blog*, Dec. 2025. [Online]. Available: <https://blog.jetbrains.com/ai/2025/12/junie-now-integrated-into-the-ai-chat/>

[23] T. Anderson, "Zed team releases version 1.0 of Rust-built editor," *The Register*, Apr. 30, 2026. (Rust + GPU 渲染 + 120fps；Threads + Agent Client Protocol.) [Online]. Available: <https://www.theregister.com/2026/04/30/zed_team_releases_version_10/>

[24] Open Source Alternatives, "9 Best Open Source AI Coding Assistants in 2026." (OpenHands 68k★, Cline 58k★, Aider 41k★, Tabby 33k★, Continue 31k★.) [Online]. Available: <https://www.opensourcealternatives.to/blog/best-open-source-ai-coding-assistants>

[25] Cursor Docs, "Model Context Protocol (MCP)." (~5000+ 社区 MCP server.) [Online]. Available: <https://cursor.com/docs/mcp>

[26] T. Anderson, "Kite AI coding pulled down to earth because 'our 500k developers would not pay to use it,' now open source," *DevClass*, Nov. 21, 2022. (Kite 2022-11 关闭并开源；500k 用户未付费.) [Online]. Available: <https://devclass.com/2022/11/21/kite-ai-coding-pulled-down-to-earth-because-our-500k-developers-would-not-pay-to-use-it-now-open-source/>

[27] Wikipedia, "Tabnine." (Codota 于 2019-12 收购 Tabnine；2021-05 公司更名为 Tabnine.) [Online]. Available: <https://en.wikipedia.org/wiki/Tabnine>

[28] Cursor, "What's New in Cursor — Latest Updates & Release Notes." (Cursor 2.4 Subagents，2026-01；自定义 subagent 可继承 Task tool 继续派生.) [Online]. Available: <https://cursor.com/changelog>
