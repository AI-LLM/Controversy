# 2026-05-14：SDLC 栈 / IDE 与 AI 编辑器 层深度研究

本篇覆盖 D8（IDE）与 D7'（AI 编辑器）两层。问题不是"AI 把补全做得更准了"，而是 **编辑器本身的形态在重写**：从围绕"光标 + 按键"的人类工作面，过渡到围绕"任务 + 多 agent + 后台机器"的人机协作面。Cursor 三年从 0 做到 20 亿美元 ARR [[1]](https://thenextweb.com/news/cursor-anysphere-2-billion-funding-50-billion-valuation-ai-coding)，是 SDLC 栈中商业斜率最陡的一层，但它仍然 fork 自 VS Code——这一矛盾贯穿全文。

## 一、Pre-Agent 时代的 IDE 流量底盘

VS Code 早在 2024-2025 即是事实标准。Microsoft 在 2025 年 5 月公布 Visual Studio + VS Code 合计 5000 万 MAU，其中 VS Code 单独约 1400 万 MAU [[2]](https://www.thurrott.com/dev/321070/visual-studio-and-visual-studio-code-have-50-million-maus)；JetBrains 2024 年底披露全家桶 1140 万 recurring active users，财富全球 100 强中 88 家是其客户 [[3]](https://finance.yahoo.com/news/jetbrains-presents-2024-annual-highlights-170000221.html)。JetBrains 是私有公司、不披露准确 ARR，第三方估算 2024 年 ARR 约 2.52 亿美元（保守口径）或更高的 ~5.9 亿美元（含一次性永久许可）[[4]](https://getlatka.com/companies/jetbrains.com)。

老一代补全的接受率天花板在 30% 以下。Kite 自述用户在 Python 场景下"平均提升 18% 生产力"（2019 营销口径，未独立复核）（⚠ 作者综合估算 / 解读：18% 这一数字来自 Kite 早期博客的营销宣传，未见独立学术评估）；Codota 主打 Java/Kotlin 学习式补全，从未公布严肃数据。这一代工具的共同特征：**基于规则 / 浅层 ML、单 token 预测、补全长度 1-3 个 token**。Kite 于 **2022 年 11 月**关闭并将代码开源 [[26]](https://devclass.com/2022/11/21/kite-ai-coding-pulled-down-to-earth-because-our-500k-developers-would-not-pay-to-use-it-now-open-source/)；Codota 实际上在 **2019 年 12 月**收购了 Tabnine，并于 2021 年 5 月将公司更名为 Tabnine [[27]](https://en.wikipedia.org/wiki/Tabnine)——LLM 一来，这一代直接被腰斩。

## 二、AI 编辑器普及后的使用密度变化

GitHub Copilot 在 2025 年 7 月跨过 2000 万总用户线，2026 年 1 月微软 FY26 Q2 财报披露 **付费订阅 470 万**（vs FY24 的 180 万）[[5]](https://techcrunch.com/2025/07/30/github-copilot-crosses-20-million-all-time-users/)。但更重要的是密度指标：企业部署研究测得 **建议层接受率 27-33%、行级接受率 ~20%**，96% 的开发者会在收到建议当天至少接受一条；每开发者每天面对的建议在"几十条"量级 [[6]](https://arxiv.org/html/2501.13282v1)。

Cursor 在 2026 年 4 月披露 **日活破百万、付费用户超百万、ARR 突破 20 亿美元**；这是从 2025 年 1 月的 1 亿 ARR 起步，14 个月走完的路径 [[7]](https://research.contrary.com/company/cursor)。

AI 贡献代码占比的产业大数：

- Google 2026 年 4 月公开 "**新代码 75% 由 AI 生成**"（CEO Pichai 强调仍由工程师 review）[[8]](https://www.breitbart.com/tech/2026/04/24/google-says-75-percent-of-fresh-code-now-generated-by-ai/)
- Microsoft Nadella 2025 年 4 月给出 "**某些项目 20-30%**"，2026 年披露部分内部 repo 已超过 50% [[9]](https://techcrunch.com/2025/04/29/microsoft-ceo-says-up-to-30-of-the-companys-code-was-written-by-ai/)
- 行业普遍口径：头部公司 2026 年生产代码 AI 占比 25-30%（含已被改写或拒绝的）[[10]](https://medium.com/@sohail_saifi/ai-writes-30-of-microsofts-code-and-25-of-google-s-6909f6e0b406)

口径警告：以上数字混淆"AI 起草并被接受"与"AI 起草后被人改写"，本身就是营销修辞，不要直接用来推算"工程师产能翻 N 倍"。

## 三、Cursor 的技术架构

Cursor 是 Anysphere（MIT 四人创立）从 VS Code OSS 完整 fork，**不是 extension**。这一点决定了它能做、Copilot 做不到的事：

- 改写编辑器的渲染管线，把 diff overlay 直接叠在源文件上（不是侧栏）
- 拦截文件系统调用，让 agent 在后台 VM 里写文件而不冲击 unsaved buffer
- 重写扩展宿主，允许 multi-agent 共享同一项目状态 [[11]](https://medium.com/data-science-collective/how-cursor-actually-works-c0702d5d91a9)

四个核心组件：

1. **Cursor Tab**（专有补全模型）。自研稀疏 LM，训练在数十亿条编辑序列上；不只是预测下一个 token，还预测"光标下一跳"（jump suggestion）。配合 Fireworks 的"speculative edits"（推测式编辑解码），把 apply 速率推到 ~1000 token/s [[12]](https://fireworks.ai/blog/cursor)。
2. **Composer Agent**（多文件编辑）。2025 年 10 月 29 日 Cursor 2.0 发布自研 Composer 模型——MoE + RL + MXFP8 量化，号称同等智力下比通用模型快 4×，大部分回合 < 30 秒 [[13]](https://cursor.com/blog/2-0)。
3. **Background Agent / 多 agent 接口**。允许同时跑最多 **8 个 agent**，各自占一个 git worktree 或远端 VM，分别开 PR；2.4 之后引入 subagent，可树状递归（自定义 subagent 继承父 agent 的 Task tool 即可继续派生）[[28]](https://cursor.com/changelog)（⚠ 解读："树状递归"系作者从官方 changelog + 论坛讨论综合推断，官方未明确使用该措辞）。
4. **Context Engine**。Tree-sitter 按函数/类边界切片，向量索引整库；客户端将相关切片**加密**后发到 backend，backend 在 enclave 内解密再喂模型。Privacy Mode 下保证 zero data retention（与 OpenAI / Anthropic 等供应商签的 ZDR 合同）[[14]](https://cursor.com/security)。

`.cursorrules`（项目根，legacy）和 `.cursor/rules/*.mdc`（新结构）是注入 system prompt 的机制。一个最小 MDC 文件：

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

`alwaysApply: true` 会无条件附加到每个 turn；`globs` 决定按文件路径自动激活；嵌套目录下的 `.cursor/rules` 会在相关文件被引用时自动追加 [[15]](https://cursor.com/docs/context/rules)。这是 Cursor 把"团队规范"嵌入提示词的标准接口，也是 Copilot Custom Instructions 的对位物——区别在于 Cursor 把它做成**版本化、目录化、glob 触发**的工程对象。

## 四、Cursor vs Copilot：为什么微软只能跟随

价格上 Cursor 并不便宜：

| 档位 | 月费 | 关键点 |
|---|---|---|
| Hobby | $0 | 限量 Agent、限量 Tab |
| Pro | $20 | Tab 不限量，$20 frontier 模型 credit |
| Pro+ | $60 | 3× credit |
| Ultra | $200 | 20× credit + 新功能优先权 |
| Teams | $40/seat | 加管理面 |
| Enterprise | 定价 | 池化用量、合规 |

2025 年 6 月 Cursor 完成关键定价转折：从"固定 fast request 配额"换成"按模型实际 API 成本计费的 usage-based credit"——把成本压力直接传导给重度用户，同时保住轻度用户的体验 [[16]](https://www.vantage.sh/blog/cursor-pricing-explained)。

为什么 Microsoft 拥有 GitHub、拥有 Azure OpenAI、拥有最便宜的 Copilot（$10/月起），仍然只能跟随？三点本质：

1. **形态绑定**。Copilot 是 extension，受 VS Code 扩展宿主的接口约束；它无法重画 diff overlay、无法拦截 file watcher、无法让多 agent 在同一进程内共享 token 池。Cursor fork 了宿主，所以工程上能跑得更快、更激进。
2. **节奏**。Cursor 从 Composer 1（GPT/Claude）→ 自研 Composer 模型 → multi-agent → background agent 的节奏是 6-12 周一次大版本；微软受 GitHub × Azure × Office × Windows 四条 SKU 协调约束，慢半拍。
3. **企业突破**。Cursor 在 2026 年披露已渗透 **64% 财富 500 / 近 70% 财富 1000**，客户包括 NVIDIA、Uber、Adobe、Salesforce、PwC [[17]](https://cursor.com/enterprise)。Privacy Mode + ZDR + SOC 2 Type II + Pooled usage 这一组合直接对位企业采购的合规清单。Copilot 同样有 Enterprise SKU，但企业更倾向"和 GitHub 数据访问解耦"——Cursor 在这点上反而是劣势变优势。

## 五、Windsurf 的并购故事：被肢解的独角兽

Codeium（2021 年由 Varun Mohan、Douglas Chen 创立，前名 Exafunction，做 GPU 虚拟化）在 2022 年转向 AI 代码补全，靠"免费 + 全 IDE 覆盖"扩张。2024 年 11 月发布 Windsurf Editor——同样 VS Code fork，主打 **Cascade**（深度代码理解）+ **Flows**（在 copilot 模式与 agent 模式之间流动）[[18]](https://research.contrary.com/company/windsurf)。

2025 年 7 月的 72 小时连续剧：

1. OpenAI 提出 30 亿美元收购，最终散场
2. **Google 用 24 亿美元做"反向 acqui-hire"**：以技术许可形式给 Windsurf 投资人 12 亿美元，另 12 亿打包成约 40 名核心员工（含两位创始人）加入 Google DeepMind 的薪酬包；**不收股权**
3. 剩下的公司壳 + 全员 + IP 被 Cognition（Devin 的母公司）以 **约 2.5 亿美元** 接走 [[19]](https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/)

两个月后 Cognition 估值跳到 102 亿美元 [[20]](https://www.cnbc.com/2025/09/08/cognition-valued-at-10point2-billion-two-months-after-windsurf-.html)。这个三段切割反映出 2025-2026 的市场规则：

- **大厂买"人 + IP 许可"而非"公司"**，绕开 FTC 反垄断审查路径
- **IDE 产品本体的并购估值远低于"创始人 + 模型团队"**——Windsurf editor 这条产品线被估到 ~10× 创始团队定价
- 中间层（VS Code fork + agent UI）在头部模型公司眼里**可被绕过**，因为他们自己的 CLI（Claude Code、Codex、Gemini Code）就足以承担入口

## 六、JetBrains 反击与 Zed 的全新赌注

JetBrains 的策略分两路：**AI Assistant**（嵌入式补全 / 聊天，覆盖 IntelliJ 全家桶 + Android Studio + VS Code 扩展，订阅制 $10-30/月）+ **Junie**（自主 agent，2025 年 7 月 GA）[[21]](https://www.jetbrains.com/junie/)。Junie 在 2025 年底引入 MCP 支持、GitHub 异步集成（无需开 IDE 即可派单），并在 2025 年 12 月把 Junie UI 并入 AI Chat [[22]](https://blog.jetbrains.com/ai/2025/12/junie-now-integrated-into-the-ai-chat/)。优势是**深度语言索引**（IntelliJ 的静态分析比 tree-sitter 强出一个量级），劣势是 JetBrains 不 fork 自己——AI 是叠加层，无法重画编辑器形态。

Zed 走的是相反方向。2026 年 4 月 29 日发布 1.0，**用 Rust 重写、GPU 渲染、120 fps、零 Electron**；核心卖点是 Threads 侧栏支持并行 agent，支持 Anthropic Claude Agent、OpenAI Codex、OpenCode、Cursor agent，通过新提出的 **Agent Client Protocol** 统一接入 [[23]](https://www.theregister.com/2026/04/30/zed_team_releases_version_10/)。Zed 团队来自 GitHub Atom + Tree-sitter，押的是"agentic 时代需要新形态编辑器，而不是给老编辑器装外挂"。

## 七、开源 / 小众阵营

- **Cline**：VS Code 扩展（不 fork），Apache 2.0，2026 年支持 30+ 模型提供商；GitHub 58k stars，紧追 OpenHands 的 68k
- **Continue.dev**：开源 Copilot 替代品，31k stars
- **Cody (Sourcegraph)**：靠 Sourcegraph 的代码图谱做检索增强
- **Aider**：CLI 形态，git-commit-as-you-go，41k stars——位置上接近 D6.5（CLI agent），不在严格 IDE 这一层 [[24]](https://www.opensourcealternatives.to/blog/best-open-source-ai-coding-assistants)

## 八、新需求 / 关键技术清单

- **Multi-file edit**：Composer / Cascade / Junie 的共同基线；diff preview + atomic apply
- **Background agent**：跑在云端 VM，长任务（>10 分钟）异步执行，产出 PR + 视频/截图证据
- **本地检索 vs 云端检索**：JetBrains 在本地建索引，Cursor / Windsurf 把切片加密后送云。本地索引在隐私合规上占优，云端索引在跨仓库语义检索上占优——这条分歧到 2026 年仍未收敛
- **MCP in-IDE**：Cursor / Junie / Zed 都把 MCP 当一等公民，2026 年 3 月 MCP 生态 5000+ 社区 server [[25]](https://cursor.com/docs/mcp)
- **Agent Client Protocol (ACP)**：Zed 1.0 推动，目标是让一个 agent 跨编辑器跑

## 九、几条本质判断

1. **VS Code 是"宿主级"护城河，不是编辑器**。Cursor、Windsurf 都 fork 自它，证明这一层的扩展点设计比 UI 更值钱；微软真正的资产不是 Copilot，而是"几乎所有 AI 编辑器都跑在我开源的渲染器上"。
2. **下一代 IDE 会脱离 VS Code，但缓慢**。Zed 是第一个严肃赌注，但即使它 2026 年发 1.0，市场份额仍远不及 fork 派；脱离 VS Code 需要的不仅是更快的渲染器，还要重建几千个 LSP / DAP / 主题 / 调试器扩展生态——这是 5-10 年量级的迁移。
3. **IDE 这一层的护城河正在被"agent"上移**。Cursor 2.0 的核心叙事从"更好的编辑器"切到"管理多 agent 的控制台"——一旦 agent 占主导，编辑器退化为 agent 的可视化界面，那 VS Code fork 的优势就被 Claude Code、Codex、Devin 这些 CLI/Web agent 釜底抽薪。Windsurf 被肢解就是这条逻辑的早期信号。
4. **Cursor 的 $50B 估值押的不是补全，是企业 control plane**。Pro 个人订阅 + Usage credit 撑不到 $6B ARR，必然靠 Teams / Enterprise SKU 的 seat × pooled usage。这意味着 Cursor 下一阶段会越来越像 Datadog——卖给买家不再是开发者本人，而是 CIO + Security。
5. **JetBrains 的命悬"语言深度"**。如果 LLM 把语义分析做到与 IntelliJ 静态分析同等精度，JetBrains 的二十年护城河会被填平；目前看 LLM 还差 1-2 代，但这是确定性的时间问题。

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
