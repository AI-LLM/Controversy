# 2026-05-14：SDLC 栈 / 终端与自治 Coding Agent 层深度研究

软件开发栈 Pre-Coding-Agent vs Post-Coding-Agent 系列，第 5 篇，对应 D6.4 + D6.5。

## 1. lens：CLI agent = 可被 cron / CI / SSH / 另一个 agent 拉起的 unix 进程

这一层与上一层（IDE 内 Copilot / Cursor）的根本分野，不是"模型更强"也不是"能力更大"，而是**形态**：CLI agent 是一个**普通的 unix 可执行文件**。

它服从 unix 进程的三条约束、也享受 unix 进程的三条自由：

- **有 stdin / stdout / 退出码** → 可被 shell 管道、cron job、systemd unit、GitHub Actions step、另一个 agent 的 tool 调用拉起；
- **有自己的进程地址空间和文件系统视图** → 可以塞进 Docker / Bubblewrap / Firecracker / 一次性 VM 做强 sandbox，每个任务一个隔离环境；
- **没有 GUI session 依赖** → headless、可 SSH、可批量、可并行 N 份同时跑。

Copilot / Cursor 把 agent 绑在 IDE 进程的生命周期里，agent 只能在"有人坐在编辑器前"时活着。CLI agent 把这条绑定砍断，agent 因此第一次成为可被**任何 unix 主体**拉起的工作单元。**"agent-as-unix-process" 是机制；"执行环境自由度（cron / CI / SSH / 远端 VM / 另一个 agent）"是结果**。本文以下所有讨论——形态光谱、任务量爆炸、Copilot 失位、Anthropic 的护城河——都是这条 lens 的下游推论。

第一次满足这条形态的产品是 Anthropic 2024 年 10 月发布的 Claude Code beta [[1]](https://www.anthropic.com/news/claude-3-5-sonnet)，2025 年 4 月 OpenAI Codex CLI 跟进 [[2]](https://github.com/openai/codex)。到 2026 年 5 月，它已成为高级工程师的默认工作面。

## 2. Pre-Agent 时代为什么三条胶水都缺"进程化"

要看清"agent-as-unix-process"是真正的新东西，得先看 2024 年以前**已经"近似"过这件事**的三条胶水各自**缺什么**。

1. **IDE + Copilot 补全**：Copilot 是 VS Code 插件，是 IDE 进程内部的一个 in-process 服务，**不是独立 unix 进程**。它没有自己的 stdin / stdout、没有退出码、不能 `cd`、不能 `npm test`、不能读 `git log`。Copilot 缺的不是"智能"，是**进程身份**——你无法把它放进 cron。
2. **shell script + cron**：shell 脚本是**完美的 unix 进程**，但**缺语义层**。`sed -i 's/React.FC/FunctionComponent/g'` 跑得动，"读自然语言 ticket → 决定改哪几个文件" 跑不动。cron 调得动 bash，调不动"理解"。
3. **codemod / jscodeshift / OpenRewrite**：AST 级批量改造工具是 unix 进程、能进 CI、能批量，**但每条迁移规则要单独写 AST visitor**。Airbnb 2017 把 React class component 迁到 hooks 走的就是这条路 [[3]](https://github.com/reactjs/react-codemod)。codemod 缺的是**通用性**——一规则一脚本，不能"读 ticket 然后判断怎么改"。

把这三条横着对齐，缺的恰好是同一件东西的不同侧面：**一个既具备语义理解、又具备 unix 进程身份的工作单元**。Copilot 有语义没进程身份；shell + codemod 有进程身份没通用语义。**CLI agent 是这两条第一次合流的产物**。这就是为什么"agent-as-unix-process" 是机制而不是修辞——它字面上指明了缺口在哪儿。

## 3. 形态光谱：按"进程化深度"排序

市面上 6 款主流终端 / 自治 agent 都自称"在 terminal 里跑"，但它们在**进程化深度**（headless 程度、sandbox 强度、可被调用程度）上落差很大。按 lens 的三条约束打分如下（⚠ 解读；维度是作者综合 lens 推出，不是行业标准评测）：

**进程化最深：Devin / Factory Droids（"agent 是独立服务"）**
- Devin 的每个任务直接在 Cognition 托管的一次性 VM 里跑，从 Linear / Jira / Slack webhook 触发，agent 全程**完全脱离任何人类 session**——它本质上是 SaaS 后端的一个 worker，CLI 只是入口之一。ACU（Agent Compute Unit，1 ACU ≈ 15 分钟 VM + 推理 + 网络）作为计费单位本身就预设"agent 是按时长跑的进程" [[4]](https://venturebeat.com/programming-development/devin-2-0-is-here-cognition-slashes-price-of-ai-software-engineer-to-20-per-month-from-500)。
- Factory.ai Droids 同构：从 ticket 拉起、droid 隔离沙盒执行、多模型路由（Claude 4.5 规划 / DeepSeek 高产出 / 小模型写测试），2026-04 拿 \$150M C 轮、\$1.5B 估值（Khosla 领投）[[5]](https://tech-insider.org/factory-ai-150-million-series-c-khosla-coding-droids-2026/)。
- 这类形态把"agent 是 unix 进程"推到极致：它不仅是进程，还是**远端托管进程**，连本机都不需要。

**进程化较深：Claude Code / Codex CLI / OpenHands / Goose**
- 本机可执行，`claude -p "fix all uses of deprecated React.FC"` 或 `codex exec` 直接 headless、可进 CI、可进 cron。
- 自带 OS 级 sandbox（`--permission-mode`）+ MCP 协议把外部能力当 tool 调用 [[6]](https://code.claude.com/docs/en/mcp)。
- OpenHands / All Hands AI 是开源旗舰，CodeAct 2.1 是首个 SWE-bench >50% 的开源 agent，SDK 在 SWE-bench Verified 用 Claude Sonnet 4.5 达 72% [[7]](https://www.openhands.dev/)。
- Goose (Block) 2025 年 1 月开源、CLI + 桌面双形态、最早一批 MCP 深度集成者、70+ extensions、2025-12 捐给 Linux Foundation Agentic AI Foundation [[8]](https://block.xyz/inside/block-open-source-introduces-codename-goose)。
- Codex CLI 2025-04-16 Rust 开源重生（与 2021 同名 API 模型无技术关系，仅复用品牌）。2026-04 累计 75K+ GitHub stars、1453 万 npm 月下载、300 万周活跃（Sam Altman 2026-04-08 披露）[[9]](https://www.gradually.ai/en/codex-statistics/)。

**进程化较浅但 git 集成最深：Aider**
- 同样是 unix 进程，但故意保持轻——BYOK + 任意模型 + 重 git 集成。每次成功编辑自动 `git commit`，message 自动写。
- 关键差异是 **search/replace diff edit format**：不让模型重写整文件，而是输出 diff block，显著降低 token 消耗与"误删无关代码"的概率 [[10]](https://github.com/Aider-AI/aider-swe-bench)。
- Aider Polyglot benchmark（225 道 Exercism 最难题、覆盖 C++/Go/Java/JavaScript/Python/Rust 共 6 语言）是社区里被广泛引用的多语言尺子 [[11]](https://aider.chat/2024/12/21/polyglot.html)，2026-05 榜首由 Claude Opus 4.5 / 4.6 占据（Opus 4.5 ~89.4%，Opus 4.6 进一步领先）[[12]](https://aider.chat/docs/leaderboards/)。

**进程化最浅（agent-first IDE）：Google Antigravity**
- 2025-11-18 公开预览、Gemini 3 同步发布、"agent-first IDE"。Mission Control 视图能并行调度 5 个 agent；支持 Gemini 3.1 Pro / Flash、Claude Sonnet/Opus 4.6、GPT-OSS-120B。深度浏览器集成（agent 自己开 Chromium 跑 e2e）[[13]](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)。
- 形态上是 IDE 包 agent，所以 agent 的可被调用性弱于纯 CLI——它仍然假设有 IDE session 存在。这正好印证 lens：**离 unix 进程越远，越退回 Copilot 的窠臼**。

光谱两头的差距由此清楚：进程化越深，越往 SaaS worker 演化；越浅，越退化为"带 agent 的 IDE"。**这条排序的标尺不是哪个产品分数高，而是 lens 本身。**

## 4. "进程化"的下游压力：任务形状变了

把 agent 升格为可被任意 unix 主体拉起的进程，最直接的后果是**任务的形状**变了：

- Pre-Agent：工程师驻守 IDE 1 小时写 100 行 → 1 个 PR / 半天。
- Post-Agent：让 agent 跑一晚生成 10 000 行 → 100 个 PR / 早晨醒来。

这不是"agent 写得更快"——是**调用模型从同步变成异步**。同步模式要求"人在场"，异步模式只要求"进程能跑"。而异步是 unix 进程的天然形态。

这给下游基础设施带来三道连锁压力：

1. **CI 计算量爆炸**：一个工程师过去一天触发 3–5 次 CI，现在 agent 在后台触发 50–100 次（⚠ 作者综合估算；依据是 agent 异步触发模式 + 一线团队反馈，非官方计量）。GitHub Actions 账单变成 OpenAI tokens 之外另一个新支出大头。
2. **Code review 瓶颈**：人审 PR 速度没变，但 PR 量 10x（⚠ 作者综合估算）。一线团队的应对是"agent 写 agent 审"——专门跑一个 reviewer subagent 先过一遍，把噪音 PR 卡住。
3. **Observability 压力**：100 个 agent 并行在 100 个分支上写代码，谁动了什么必须可追溯。Honeycomb、Datadog 都在加 agent run 维度。

由此第一次成立的几类用例**全部依赖"进程化"**：

- **跨百仓批量改造**：把同一段 prompt 在 300 个 microservice repo 上分发执行（⚠ 作者综合估算；Stripe / Shopify / Block 等组织已公开使用 Claude Code 做迁移与批量改造，但"300 个 repo"是数量级示意，非官方数字；Shopify 2026-04-09 开源 Shopify AI Toolkit 含 Claude Code plugin，可印证规模化使用 [[14]](https://weaverse.io/blogs/shopify-ai-toolkit-dev-mcp-hydrogen-2026)）。这件事只可能在 agent 是 unix 进程时成立——你要并发 300 份 sandbox 跑同一段语义改造，必须既有 sandbox 又有可批量调用。
- **依赖升级 PR 工厂**：Renovate webhook → agent 读 changelog → 改调用点 → 跑测试 → 提 PR。
- **incident-driven 修复**：PagerDuty webhook → 启动 agent → 读日志 → 定位 → 提 hotfix PR。Factory.ai 的 incident droid 就是这条线 [[15]](https://factory.ai/)。
- **codebase migration**：Python 2→3、React class→hooks、CommonJS→ESM 类大型迁移可以让 agent 一仓一仓跑。

这四类用例都共享一条结构：**触发器是另一个 unix 主体（webhook / cron / queue）而非人**。这是 lens 的字面验证。

## 5. Claude Code：把 unix 进程做成可扩展执行环境

Claude Code 是这一层架构最完整的样本，它把"agent 是 unix 进程"这条原则**具象化为五个 primitive**，每一个都对应"如何让进程更可被组合"。

**(a) CLAUDE.md**：仓库根部的 markdown，每次 session 启动自动注入到上下文。把"项目规范 + 命令 + 注意陷阱"塞进进程启动协议，等价于 `.bashrc` 之于 shell。本仓库的 `CLAUDE.md` 即一例。

**(b) Subagents**：`.claude/agents/*.md`，YAML frontmatter 定义元数据，body 是 system prompt。每个 subagent 有独立 context 与 tool 白名单，主 agent 通过 Task tool 派发 [[16]](https://code.claude.com/docs/en/sub-agents)：

```yaml
---
name: code-reviewer
description: "Expert code review specialist. Use PROACTIVELY after code changes to check security, style, and maintainability."
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer. When invoked:
1. Read the diff via `git diff main...HEAD`
2. Flag security issues, unidiomatic patterns, missing tests
3. Output a checklist; do NOT modify files.
```

形态上对应"主进程 fork 出多个子进程，每个子进程有独立地址空间"。

**(c) Skills**：`.claude/skills/*` 目录，每个 skill 是 markdown + 可选脚本的包。比 subagent 轻——按需加载，不消耗常驻 context。2026 年和 slash command 合并 [[17]](https://blakecrosley.com/guides/claude-code)。

**(d) Hooks**：`.claude/settings.json` 里声明的生命周期钩子。十二种事件，最常用的是 PreToolUse / PostToolUse / Stop / SubagentStop。它们是**确定性**的——返回 deny 就阻断 [[18]](https://code.claude.com/docs/en/hooks)。Hooks 本质是**让 agent 进程对外暴露 unix 风格的事件接口**，外部脚本可以拦截、改写、阻断：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command",
            "command": "node ~/.claude/hooks/block-dangerous-commands.js" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command",
            "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\"" }
        ]
      }
    ]
  }
}
```

**(e) MCP server**：用 `claude mcp add` 注册外部能力，agent 把它们当 tool 调用 [[6]](https://code.claude.com/docs/en/mcp)。MCP 是把"另一个 unix 进程"显式纳入 agent 工具集的协议：

```bash
claude mcp add --transport stdio --env AIRTABLE_API_KEY=$KEY \
  airtable -- npx -y airtable-mcp-server

claude mcp add --transport http github \
  https://api.githubcopilot.com/mcp --header "Authorization: Bearer $GH"
```

**并行调度**：主 agent 用 Task tool 并发派发到 N 个 subagent，每个子任务跑在隔离的 context；主 agent 只看摘要回包。对大型 refactor 至关重要——主 context 不被 1 万行 grep 输出污染。

这五个 primitive 都不在"让模型更聪明"上花力气，全部花在"让进程更可被组合"上——CLAUDE.md 是启动协议，subagents 是 fork，hooks 是事件接口，MCP 是 IPC，skills 是 dynamic linking。**Claude Code 看似是个 CLI 工具，本质是一个 unix-style 的 agent 运行时**。

## 6. Lens 反证：GitHub Copilot 为何在这一层失位

Copilot 的失位是 lens 最有力的反证案例。Copilot 不缺资源、不缺模型、不缺渠道、不缺先发——它在 IDE 补全形态里有多年飞轮。但当形态从"在编辑器里"变成"在 terminal headless"，Copilot 内部的飞轮**一个也不能直接平移**：

- **分发渠道错配**：IDE 插件 marketplace 在 CLI 无用。CLI agent 走 npm / Homebrew / brew tap，根本不经过 VS Code Extension Marketplace。
- **漏斗错配**：Copilot 的商业漏斗是"免费补全 → 付费 enterprise"，依赖"按 Tab 的那一瞬"。agent 形态里这一瞬不存在——agent 在凌晨 3 点跑，没有 Tab、没有"接受补全"的微动作。计费必须改成 token / ACU / VM 时长，整个销售剧本要重写。
- **耦合错配**：与 VS Code 的深度耦合反而是负资产——agent 用户不在 VS Code 里，他们在 tmux / iTerm / SSH session 里。Copilot 越是与 VS Code 紧绑定，越难做成"可被 cron 拉起的 unix 进程"。
- **DNA 错配**：Copilot 的组织、产品、UI、定价、销售全部围绕"在编辑器里按 Tab"。当形态从同步交互（< 30 秒、人在场）变为异步任务（> 5 分钟、人不在场），这套 DNA 全部需要重写。

GitHub 2025 才急着推 Copilot Workspace + coding agent，被 Claude Code 抢先一年。9 个月内 Claude Code 在 senior agent 使用者里拿到 46% 偏好，对手是有多年先发的 Copilot [[19]](https://tianpan.co/forum/t/claude-code-became-market-leader-in-9-months-github-copilot-had-a-multi-year-head-start-what-changed/2840)。

这条反证的结论不是"Copilot 不努力"，而是**形态决定结构**——当 agent 必须是 unix 进程时，IDE 厂家的全部积累都成了枷锁。这也是为什么 lens 必须立在第一节而不是结尾：所有后续判断都建立在"形态是因，能力 / 市场 / 飞轮是果"之上。

## 7. 几条本质判断

**(a) CLI agent vs IDE agent 的长期格局**：两者不是替代关系，是**异步 vs 同步**的分工。IDE agent（Cursor、Copilot inline）覆盖 < 30 秒的同步交互；CLI agent 覆盖 > 5 分钟的异步任务（⚠ 解读；时间阈值是作者对两种形态典型 latency 的概括，非测量值）。senior 工程师从 IDE 主战场迁到 terminal + Mission Control，初级工程师还在 IDE。这条裂痕 2025–2026 已经非常清晰。

**(b) Anthropic 的结构性优势**：Claude Code 让 Anthropic 在 dev 工具栈拿到**协议层（MCP）+ 客户端形态（Claude Code）+ 模型本身**三件一起出。这是"卖铲子的同时也下场挖矿"。结构性优势的根源仍是 lens——MCP 协议本身就是为"agent 进程之间互相调用"设计的，Claude Code 是这套协议第一个完整 reference implementation。

**(c) "可被其它系统调用"是这一层的真正护城河**：CLI agent 真正的杀手锏不是 UI，是它**作为 unix 进程的可组合性**——能被 cron 拉起、能被 GitHub Actions 调用、能被另一个 agent 当 tool。这把 coding agent 从"开发者的工具"变成"系统的一部分"。IDE agent 永远做不到，因为它绑死在 GUI。

## 附录 A：市场验证数字

下列数字本身不构成判断，只用于印证"agent-as-unix-process" 这条形态在 2025–2026 已被市场验证：

- **Claude Code run-rate revenue 2026-02 超 \$2.5B**（外部估算，含 API 使用 + 订阅 + 企业合同；非审计数字）[[20]](https://www.mindstudio.ai/blog/claude-code-2-5-billion-annualized-revenue-terminal-tool)。
- **JetBrains 2026-04 调研**：Claude Code 占 agentic dev 工作量 71%；senior 工程师"最爱"占 46%，远超 Cursor (19%) 和 GitHub Copilot (9%) [[21]](https://blog.jetbrains.com/research/2026/04/which-ai-coding-tools-do-developers-actually-use-at-work/)。
- **Codex CLI 2025-04-16 重生**后，至 2026-04 累计 75K+ GitHub stars、1453 万 npm 月下载（2026-03）、300 万周活跃（Sam Altman 2026-04-08 披露）[[9]](https://www.gradually.ai/en/codex-statistics/)。
- **Devin merge rate 34% → 67%**（Devin 1 早期到 2.0 自我报告区间，⚠ 解读；端到端任务定义随版本调整，跨版本严格可比性有限）；Devin 2.0 把入门价从 \$500/月砍到 \$20/月 [[4]](https://venturebeat.com/programming-development/devin-2-0-is-here-cognition-slashes-price-of-ai-software-engineer-to-20-per-month-from-500)。Devin 首发 SWE-bench 13.86%（当时 SOTA 7×），之后两年无官方更新 [[22]](https://ucstrategies.com/news/devin-1-specs-benchmarks-why-its-obsolete-2026/)。
- **Terminal-Bench 2.0**（2026）：Codex CLI 77.3%，Claude Code 65.4%，调校过的 Claude Mythos harness 92.1% [[23]](https://www.tbench.ai/leaderboard/terminal-bench/2.0)。
- **SWE-bench Verified**：Opus 4.6 80.8%、Sonnet 4.6 79.6%、Opus 4.7 87.6% [[24]](https://www.swebench.com/)。
- **Aider vs Copilot**：Aider 在内部 SWE-bench 类评测下 edit format 成功率 99%、Copilot 65%（⚠ 数字来自 Aider 自家 benchmark，定义为"模型输出 diff 能被无歧义 apply"；不等同于"任务整体完成率"，与 SWE-bench 不可直接比较）[[10]](https://github.com/Aider-AI/aider-swe-bench)。
- **Antigravity 2025-11-18** 公开预览，Mission Control 并行 5 agent [[13]](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)。

## 参考文献

[1] Anthropic, "Introducing Claude 3.5 Sonnet and Claude Code (beta)," *Anthropic Blog*, Oct. 2024. [Online]. Available: <https://www.anthropic.com/news/claude-3-5-sonnet>

[2] OpenAI, "openai/codex: Lightweight coding agent that runs in your terminal," *GitHub*, 2025. [Online]. Available: <https://github.com/openai/codex>

[3] React team, "react-codemod: codemod scripts for React," *GitHub*. [Online]. Available: <https://github.com/reactjs/react-codemod>

[4] C. Franzen, "Devin 2.0 is here: Cognition slashes price of AI software engineer to \$20/month from \$500," *VentureBeat*, Apr. 2025. (Devin 2.0 内部基准：单 ACU 比 1.x 多完成 83% junior 任务；1 ACU ≈ 15 min；Core \$2.25/ACU、Team \$2.00/ACU。) [Online]. Available: <https://venturebeat.com/programming-development/devin-2-0-is-here-cognition-slashes-price-of-ai-software-engineer-to-20-per-month-from-500>

[5] Tech-Insider, "Factory AI \$150M Series C: \$1.5B Khosla Bet," Apr. 2026. [Online]. Available: <https://tech-insider.org/factory-ai-150-million-series-c-khosla-coding-droids-2026/>

[6] Anthropic, "Connect Claude Code to tools via MCP," *Claude Code Docs*, 2026. [Online]. Available: <https://code.claude.com/docs/en/mcp>

[7] All Hands AI, "OpenHands — The Open Platform for Cloud Coding Agents," 2026. (CodeAct 2.1 首个 SWE-bench >50% 开源 agent；SDK 在 SWE-bench Verified 用 Claude Sonnet 4.5 达 72%。) [Online]. Available: <https://www.openhands.dev/>

[8] Block, "Block Open Source Introduces 'codename goose' — an Open Framework for AI Agents," Jan. 2025. (70+ MCP extensions；2025-12 捐给 Linux Foundation Agentic AI Foundation。) [Online]. Available: <https://block.xyz/inside/block-open-source-introduces-codename-goose>

[9] Gradually.ai, "OpenAI Codex Statistics 2026: Key Numbers, Data & Facts," 2026. (75K+ GitHub stars；npm 月下载 1453 万（2026-03）；3M weekly active users，Sam Altman 2026-04-08 披露。) [Online]. Available: <https://www.gradually.ai/en/codex-statistics/>

[10] Aider-AI, "aider-swe-bench: Harness used to benchmark aider against SWE Bench," *GitHub*. [Online]. Available: <https://github.com/Aider-AI/aider-swe-bench>

[11] P. Gauthier, "o1 tops aider's new polyglot leaderboard," *aider.chat*, Dec. 2024. (225 道 Exercism 最难题，覆盖 C++/Go/Java/JavaScript/Python/Rust 6 语言。) [Online]. Available: <https://aider.chat/2024/12/21/polyglot.html>

[12] Aider, "Aider LLM Leaderboards," 2026. (2026 年 5 月 Opus 4.5 ~89.4%；Opus 4.6 进一步领先。) [Online]. Available: <https://aider.chat/docs/leaderboards/>

[13] Google Developers Blog, "Build with Google Antigravity, our new agentic development platform," Nov. 2025. [Online]. Available: <https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/>

[14] Weaverse, "Shopify AI Toolkit Explained: Dev MCP, Cursor, Claude Code, Skill Packages (2026)," 2026. (Shopify 2026-04-09 开源 Shopify AI Toolkit，含 Claude Code plugin。) [Online]. Available: <https://weaverse.io/blogs/shopify-ai-toolkit-dev-mcp-hydrogen-2026>

[15] Factory, "Factory — Agent-Native Software Development," 2026. [Online]. Available: <https://factory.ai/>

[16] Anthropic, "Create custom subagents," *Claude Code Docs*, 2026. [Online]. Available: <https://code.claude.com/docs/en/sub-agents>

[17] B. Crosley, "Claude Code CLI: The Complete Guide — Hooks, MCP, Skills," 2026. [Online]. Available: <https://blakecrosley.com/guides/claude-code>

[18] Anthropic, "Hooks reference," *Claude Code Docs*, 2026. [Online]. Available: <https://code.claude.com/docs/en/hooks>

[19] T. Pan, "Claude Code Became Market Leader in 9 Months. GitHub Copilot Had a Multi-Year Head Start. What Changed?," *10x.pub Forum*, 2026. [Online]. Available: <https://tianpan.co/forum/t/claude-code-became-market-leader-in-9-months-github-copilot-had-a-multi-year-head-start-what-changed/2840>

[20] MindStudio, "Claude Code Is Doing \$2.5B in Annualized Revenue — Just from the Terminal Tool," 2026. (2026-02 Claude Code run-rate revenue 超 \$2.5B，含 API + 订阅 + 企业合同；外部估算。) [Online]. Available: <https://www.mindstudio.ai/blog/claude-code-2-5-billion-annualized-revenue-terminal-tool>

[21] JetBrains Research Blog, "Which AI Coding Tools Do Developers Actually Use at Work?," Apr. 2026. (Claude Code: senior 工程师 46% "most loved"; 71% of agent-using devs use Claude Code.) [Online]. Available: <https://blog.jetbrains.com/research/2026/04/which-ai-coding-tools-do-developers-actually-use-at-work/>

[22] UCStrategies, "Devin 1: Specs, Benchmarks & Why It's Obsolete," 2026. (Devin 首发 SWE-bench 13.86%；之后两年无官方更新。) [Online]. Available: <https://ucstrategies.com/news/devin-1-specs-benchmarks-why-its-obsolete-2026/>

[23] Terminal-Bench team, "Terminal-Bench 2.0 leaderboard," 2026. (Codex CLI 77.3% vs Claude Code 65.4%；Claude Mythos harness 92.1%。) [Online]. Available: <https://www.tbench.ai/leaderboard/terminal-bench/2.0>

[24] SWE-bench team, "SWE-bench Leaderboards," 2026. (Opus 4.6: 80.8%；Sonnet 4.6: 79.6%；Opus 4.7: 87.6%。) [Online]. Available: <https://www.swebench.com/>

[25] OpenAI Developers, "CLI – Codex," 2025. [Online]. Available: <https://developers.openai.com/codex/cli>
