# 2026-05-14：SDLC 栈 / 终端与自治 Coding Agent 层深度研究

软件开发栈 Pre-Coding-Agent vs Post-Coding-Agent 系列，第 5 篇，对应 D6.4 + D6.5。

本层是整张栈图里**完全新增**的一层——2022 年以前不存在 CLI 形态的 coding agent；Copilot 是 IDE 插件，Codex（旧）是 API，Replit 是 web IDE。**"在终端里跑、可 headless、可被 CI 拉起、可在沙盒里自由读写文件、可调用 MCP、可挂 hooks"** 这一组形态，2024 年 10 月 Anthropic 发布 Claude Code beta 才第一次成立 [[1]](https://www.anthropic.com/news/claude-3-5-sonnet)，2025 年 4 月 OpenAI Codex CLI 跟进 [[2]](https://github.com/openai/codex)，到 2026 年 5 月已成为高级工程师的默认工作面。

## 1. Pre-Agent 时代的"自治"近似物

CLI agent 出现之前，"无人值守"开发工作流靠三条胶水：

1. **IDE 内手动**：VS Code + Copilot 必须有人按 Tab、有人切文件、有人粘 stack trace。Copilot 不会 `cd`、不会 `npm test`、不会读 `git log`，因此所谓"自治"基本不存在。
2. **shell script + cron**：批量 lint、跑测试、用 `sed` 改全仓的事用 Bash / Python 脚本完成；但脚本写死了语法，不能"读 ticket 然后判断怎么改"。任何**语义层**改造都得人坐在前面。
3. **codemod / jscodeshift / OpenRewrite**：AST 级批量改造工具。能力强但门槛高——每条迁移规则要单独写 AST visitor。Airbnb 2017 把 React class component 迁到 hooks 用的就是这条路 [[3]](https://github.com/reactjs/react-codemod)。

这三条加起来，仍然解决不了"读自然语言 issue → 决定改哪几个文件 → 写改动 → 跑测试 → 写 PR 描述"这个**端到端循环**。Pre-Agent 时代的工程师**就是这个循环本身**。

## 2. 终端 / 自治 Agent 解锁的新工作流

CLI agent 把"agent 本体"从 GUI 进程里拆出来变成普通的可执行文件，由此带来的变化是**形态级**而非功能级的：

- **headless**：`claude -p "fix all uses of deprecated React.FC"` 或 `codex exec` 不再需要桌面会话。
- **SSH / CI / cron 可托管**：可以放进 GitHub Actions、放进 Kubernetes Job、放进 Jenkins，跟其它命令行工具拼装。
- **sandbox**：每个 agent 跑在自己的容器 / VM / Bubblewrap 里，写文件不污染宿主。Devin 默认每个任务一个一次性 VM；Claude Code 提供 `--permission-mode` 和 OS 级沙盒。
- **可被其他系统调用**：通过 stdin/stdout、通过 MCP 协议，agent 变成上游 orchestrator 的一个 tool。

由此第一次成立的用例：

- **跨百仓批量改造**：把同一段 prompt 在 300 个 microservice repo 上分发执行（⚠ 作者综合估算；Stripe / Shopify / Block 等大型组织已公开使用 Claude Code 做迁移与批量改造，但"300 个 repo"是数量级示意，非官方数字；Shopify 2026-04-09 开源 Shopify AI Toolkit，含 Claude Code plugin，可印证规模化使用 [[21]](https://weaverse.io/blogs/shopify-ai-toolkit-dev-mcp-hydrogen-2026)），传统 codemod 写不出来。
- **依赖升级 PR 工厂**：Renovate + agent。检测到 lockfile 漂移，agent 自己读 changelog、改调用点、跑测试、提 PR。
- **incident-driven 修复**：PagerDuty webhook → 启动 agent → 读日志 → 定位 → 提 hotfix PR。Factory.ai 的 incident droid 就是这条线 [[4]](https://factory.ai/)。
- **codebase migration**：Python 2→3、React class→hooks、CommonJS→ESM 类大型迁移可以让 agent 一仓一仓跑。

## 3. 任务量模式变化

这一层最容易被低估的不是"agent 写代码更快"，而是**任务的形状变了**：

Pre-Agent：工程师驻守 IDE 1 小时写 100 行 → 1 个 PR / 半天。
Post-Agent：让 agent 跑一晚生成 10 000 行 → 100 个 PR / 早晨醒来。

这给下游基础设施带来三道连锁压力：

1. **CI 计算量爆炸**：一个工程师过去一天触发 3–5 次 CI，现在 agent 在后台触发 50–100 次（⚠ 作者综合估算；依据是 agent 异步触发模式 + 一线团队反馈，非官方计量）。GitHub Actions 账单变成 OpenAI tokens 之外另一个新支出大头。
2. **Code review 瓶颈**：人审 PR 速度没变，但 PR 量 10x（⚠ 作者综合估算）。一线团队的应对是"agent 写 agent 审"——专门跑一个 reviewer subagent 先过一遍，把噪音 PR 卡住。
3. **Observability 压力**：100 个 agent 并行在 100 个分支上写代码，谁动了什么必须可追溯。Honeycomb、Datadog 都在加 agent run 维度。

数据上：Claude Code 用户群 2026 年 71% 的 agentic dev 工作量来自这个工具，"senior 工程师最爱"占比 46%，远超 Cursor (19%) 和 GitHub Copilot (9%) [[5]](https://blog.jetbrains.com/research/2026/04/which-ai-coding-tools-do-developers-actually-use-at-work/)。

## 4. Claude Code 的技术架构

Claude Code 是这一层架构最完整的样本。五个 primitive：

**(a) CLAUDE.md**：仓库根部的 markdown，每次 session 启动自动注入到上下文。用来沉淀项目规范、命令、注意陷阱。本仓库的 `CLAUDE.md` 就是一例。

**(b) Subagents**：`.claude/agents/*.md` 文件，YAML frontmatter 定义元数据，body 是 system prompt。每个 subagent 有自己的上下文窗口、自己的工具白名单，主 agent 通过 Task tool 调用 [[6]](https://code.claude.com/docs/en/sub-agents)：

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

**(c) Skills**：`.claude/skills/*` 目录，每个 skill 是一个 markdown + 可选脚本的包。比 subagent 轻——按需加载，不消耗常驻 context。2026 年和 slash command 合并 [[7]](https://blakecrosley.com/guides/claude-code)。

**(d) Hooks**：`.claude/settings.json` 里声明的生命周期钩子。十二种事件，最常用的是 PreToolUse / PostToolUse / Stop / SubagentStop。它们是**确定性**的——返回 deny 就阻断 [[8]](https://code.claude.com/docs/en/hooks)：

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

**(e) MCP server**：用 `claude mcp add` 注册外部能力，agent 把它们当 tool 调用 [[9]](https://code.claude.com/docs/en/mcp)：

```bash
claude mcp add --transport stdio --env AIRTABLE_API_KEY=$KEY \
  airtable -- npx -y airtable-mcp-server

claude mcp add --transport http github \
  https://api.githubcopilot.com/mcp --header "Authorization: Bearer $GH"
```

**并行调度**：主 agent 用 Task tool 并发派发到 N 个 subagent，每个子任务跑在隔离的 context；主 agent 只看摘要回包。这一点对大型 refactor 至关重要——主 context 不被 1 万行 grep 输出污染。

## 5. Devin 的差异化：autonomous end-to-end

Cognition Devin 与 Claude Code 走的不是一条路。Claude Code 是**让工程师在 terminal 用 agent**，Devin 是**派 agent 直接当工程师**——它从 Linear/Jira/Slack 拉 ticket，自己规划 plan，自己拉分支，自己写代码，自己跑 CI，自己回应 review。

**ACU (Agent Compute Unit) 定价**：1 ACU ≈ 15 分钟 Devin 的自治工作（VM 时间 + 模型推理 + 网络）。2025 年 4 月 Devin 2.0 把入门价从 \$500/月砍到 \$20/月（Core plan，ACU \$2.25 计费），Team plan \$500/月含 250 ACU（\$2.00/ACU）[[10]](https://venturebeat.com/programming-development/devin-2-0-is-here-cognition-slashes-price-of-ai-software-engineer-to-20-per-month-from-500)。

**Success rate 演进**：2024 年初发布时官方 SWE-bench 13.86%（首次端到端通过率，是当时 SOTA 7×）；之后 Cognition 不再公布新版 SWE-bench 分数。2026 年自我报告"约 75% 任务完成、25% 需人介入"，但**官方 benchmark 沉默两年**导致外界对真实成绩存疑 [[11]](https://ucstrategies.com/news/devin-1-specs-benchmarks-why-its-obsolete-2026/)。Devin 2.0 内部基准称单 ACU 比 1.x 多完成 83% junior 级任务。

## 6. OpenAI Codex CLI、Aider 的差异

**OpenAI Codex CLI**（2025-04-16 发布，**不是** 2021 那个 Codex 模型；同名复用）：Rust 写的开源终端 agent，npm/Homebrew 分发。绑 ChatGPT 订阅（Plus / Pro / Business / Enterprise）即用，跑 o3 / o4-mini 后端 [[12]](https://developers.openai.com/codex/cli)。2026 年 4 月：75K+ GitHub stars、1453 万 npm 月下载（2026-03）、300 万周活跃（Sam Altman 2026-04-08 披露）[[22]](https://www.gradually.ai/en/codex-statistics/)。在 Terminal-Bench 2.0 上以 **77.3%** 领先 Claude Code 的 **65.4%**（但调校过的 "Claude Mythos" harness 能打到 92.1%）[[13]](https://www.tbench.ai/leaderboard/terminal-bench/2.0)。

**Aider**：开源 CLI agent，**最重要的差异**是 git-aware diff 模式——不让模型重写整文件，而是要求模型输出 search/replace diff block；这种 edit format 显著降低 token 消耗，也降低"误删无关代码"的概率 [[14]](https://github.com/Aider-AI/aider-swe-bench)。每次成功编辑自动 `git commit`，message 自动写。Aider Polyglot benchmark（225 道 Exercism 难题，覆盖 C++/Go/Java/JavaScript/Python/Rust 共 6 语言）是社区里被广泛引用的多语言尺子 [[23]](https://aider.chat/2024/12/21/polyglot.html)，2026 年 5 月榜首区由 Claude Opus 4.5/4.6 占据（Aider 官方榜显示 Opus 4.5 ~89.4%，Opus 4.6 进一步领先）[[24]](https://aider.chat/docs/leaderboards/)。Aider 的定位：**BYOK + 任意模型 + 重 git 集成**，对成本敏感、模型不锁定的团队是首选。

其他重要玩家：

- **Google Antigravity**（2025-11-18 公开预览）：Gemini 3 同步发布，"agent-first IDE"，Mission Control 视图能并行调度 5 个 agent；支持 Gemini 3.1 Pro / Flash、Claude Sonnet/Opus 4.6、GPT-OSS-120B。深度浏览器集成是亮点（agent 自己开 Chromium 跑 e2e）[[15]](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)。
- **OpenHands / All Hands AI**：开源旗舰，CodeAct 2.1 是首个 SWE-bench >50% 的开源 agent；SDK 在 SWE-bench Verified 用 Claude Sonnet 4.5 拿到 72% [[16]](https://www.openhands.dev/)。
- **Goose (Block)**：2025 年 1 月开源，CLI + 桌面双形态，最早一批 MCP 深度集成者，70+ extensions；2025-12 捐给 Linux Foundation Agentic AI Foundation [[17]](https://block.xyz/inside/block-open-source-introduces-codename-goose)。
- **Factory.ai Droids**：2026-04 拿 \$150M C 轮 \$1.5B 估值（Khosla 领投）；不是 IDE 也不是脚手架，是 **delivery pipeline**——从 Linear/Jira 拉任务、droid 隔离沙盒执行、多模型路由（Claude 4.5 规划、DeepSeek 高产出、小模型写测试）[[18]](https://tech-insider.org/factory-ai-150-million-series-c-khosla-coding-droids-2026/)。

## 7. 几条本质判断

**(a) CLI agent vs IDE agent 的长期格局**：两者不是替代关系，是**异步 vs 同步**的分工。IDE agent（Cursor、Copilot inline）覆盖 < 30 秒的同步交互；CLI agent 覆盖 > 5 分钟的异步任务（⚠ 解读；时间阈值是作者对两种形态典型 latency 的概括，非测量值）。**senior 工程师从 IDE 主战场迁到 terminal + Mission Control，初级工程师还在 IDE。**这条裂痕 2025–2026 已经非常清晰。

**(b) Anthropic 的位置**：Claude Code 让 Anthropic 在 dev 工具栈拿到了一个**结构性优势**——不只是模型 API，还有**协议层（MCP）+ 客户端形态（Claude Code）+ 模型本身**三件一起出。Claude Code run-rate revenue 在 2026-02 已超 \$2.5B（投资分析报告综合估算，含 API 使用 + 订阅 + 企业合同；非审计数字）[[25]](https://www.mindstudio.ai/blog/claude-code-2-5-billion-annualized-revenue-terminal-tool)。SWE-bench Verified Opus 4.6 80.8% / Sonnet 4.6 79.6%（更新到 Opus 4.7 87.6%）[[19]](https://www.swebench.com/)。Anthropic 实际上在 coding agent 这一层做了"卖铲子的同时也下场挖矿"。

**(c) 为什么 GitHub Copilot 在这一层没拿到优势**：Copilot 的 DNA 是"IDE 补全"，组织、产品、UI、定价、销售全部围绕"在编辑器里按 Tab"。当形态从"在编辑器里"变成"在 terminal headless"，Copilot 内部所有积累的飞轮都不能直接平移：
  - IDE 插件分发渠道在 CLI 无用；
  - "免费补全 → 付费 enterprise" 的漏斗在 agent 形态里不存在；
  - 与 VS Code 的耦合反而是负资产——agent 用户不在 VS Code 里。
  
GitHub 2025 才急着推 Copilot Workspace + coding agent，但被 Claude Code 抢先一年——9 个月 Claude Code 在 senior agent 使用者里拿到 46% 偏好，对手是有多年先发的 Copilot [[20]](https://tianpan.co/forum/t/claude-code-became-market-leader-in-9-months-github-copilot-had-a-multi-year-head-start-what-changed/2840)。

**(d) "可被其它系统调用"是这一层的真正护城河**：CLI agent 真正的杀手锏不是 UI，是它**作为 unix 进程的可组合性**——能被 cron 拉起、能被 GitHub Actions 调用、能被另一个 agent 当 tool。这把 coding agent 从"开发者的工具"变成"系统的一部分"。这一点 IDE agent 永远做不到，因为它绑死在 GUI。

## 参考文献

[1] Anthropic, "Introducing Claude 3.5 Sonnet and Claude Code (beta)," *Anthropic Blog*, Oct. 2024. [Online]. Available: <https://www.anthropic.com/news/claude-3-5-sonnet>

[2] OpenAI, "openai/codex: Lightweight coding agent that runs in your terminal," *GitHub*, 2025. [Online]. Available: <https://github.com/openai/codex>

[3] React team, "react-codemod: codemod scripts for React," *GitHub*. [Online]. Available: <https://github.com/reactjs/react-codemod>

[4] Factory, "Factory — Agent-Native Software Development," 2026. [Online]. Available: <https://factory.ai/>

[5] JetBrains Research Blog, "Which AI Coding Tools Do Developers Actually Use at Work?," Apr. 2026. (Claude Code: senior 工程师 46% "most loved"; 71% of agent-using devs use Claude Code.) [Online]. Available: <https://blog.jetbrains.com/research/2026/04/which-ai-coding-tools-do-developers-actually-use-at-work/>

[6] Anthropic, "Create custom subagents," *Claude Code Docs*, 2026. [Online]. Available: <https://code.claude.com/docs/en/sub-agents>

[7] B. Crosley, "Claude Code CLI: The Complete Guide — Hooks, MCP, Skills," 2026. [Online]. Available: <https://blakecrosley.com/guides/claude-code>

[8] Anthropic, "Hooks reference," *Claude Code Docs*, 2026. [Online]. Available: <https://code.claude.com/docs/en/hooks>

[9] Anthropic, "Connect Claude Code to tools via MCP," *Claude Code Docs*, 2026. [Online]. Available: <https://code.claude.com/docs/en/mcp>

[10] C. Franzen, "Devin 2.0 is here: Cognition slashes price of AI software engineer to \$20/month from \$500," *VentureBeat*, Apr. 2025. (Devin 2.0 内部基准：单 ACU 比 1.x 多完成 83% junior 任务；1 ACU ≈ 15 min；Core \$2.25/ACU、Team \$2.00/ACU。) [Online]. Available: <https://venturebeat.com/programming-development/devin-2-0-is-here-cognition-slashes-price-of-ai-software-engineer-to-20-per-month-from-500>

[11] UCStrategies, "Devin 1: Specs, Benchmarks & Why It's Obsolete," 2026. (Devin 首发 SWE-bench 13.86%；之后两年无官方更新。) [Online]. Available: <https://ucstrategies.com/news/devin-1-specs-benchmarks-why-its-obsolete-2026/>

[12] OpenAI Developers, "CLI – Codex," 2025. [Online]. Available: <https://developers.openai.com/codex/cli>

[13] Terminal-Bench team, "Terminal-Bench 2.0 leaderboard," 2026. (Codex CLI 77.3% vs Claude Code 65.4%；Claude Mythos harness 92.1%。) [Online]. Available: <https://www.tbench.ai/leaderboard/terminal-bench/2.0>

[14] Aider-AI, "aider-swe-bench: Harness used to benchmark aider against SWE Bench," *GitHub*. [Online]. Available: <https://github.com/Aider-AI/aider-swe-bench>

[15] Google Developers Blog, "Build with Google Antigravity, our new agentic development platform," Nov. 2025. [Online]. Available: <https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/>

[16] All Hands AI, "OpenHands — The Open Platform for Cloud Coding Agents," 2026. (CodeAct 2.1 首个 SWE-bench >50% 开源 agent；SDK 在 SWE-bench Verified 用 Claude Sonnet 4.5 达 72%。) [Online]. Available: <https://www.openhands.dev/>

[17] Block, "Block Open Source Introduces 'codename goose' — an Open Framework for AI Agents," Jan. 2025. (70+ MCP extensions；2025-12 捐给 Linux Foundation Agentic AI Foundation。) [Online]. Available: <https://block.xyz/inside/block-open-source-introduces-codename-goose>

[18] Tech-Insider, "Factory AI \$150M Series C: \$1.5B Khosla Bet," Apr. 2026. [Online]. Available: <https://tech-insider.org/factory-ai-150-million-series-c-khosla-coding-droids-2026/>

[19] SWE-bench team, "SWE-bench Leaderboards," 2026. (Opus 4.6: 80.8%；Sonnet 4.6: 79.6%；Opus 4.7: 87.6%。) [Online]. Available: <https://www.swebench.com/>

[20] T. Pan, "Claude Code Became Market Leader in 9 Months. GitHub Copilot Had a Multi-Year Head Start. What Changed?," *10x.pub Forum*, 2026. [Online]. Available: <https://tianpan.co/forum/t/claude-code-became-market-leader-in-9-months-github-copilot-had-a-multi-year-head-start-what-changed/2840>

[21] Weaverse, "Shopify AI Toolkit Explained: Dev MCP, Cursor, Claude Code, Skill Packages (2026)," 2026. (Shopify 2026-04-09 开源 Shopify AI Toolkit，含 Claude Code plugin。) [Online]. Available: <https://weaverse.io/blogs/shopify-ai-toolkit-dev-mcp-hydrogen-2026>

[22] Gradually.ai, "OpenAI Codex Statistics 2026: Key Numbers, Data & Facts," 2026. (75K+ GitHub stars；npm 月下载 1453 万（2026-03）；3M weekly active users，Sam Altman 2026-04-08 披露。) [Online]. Available: <https://www.gradually.ai/en/codex-statistics/>

[23] P. Gauthier, "o1 tops aider's new polyglot leaderboard," *aider.chat*, Dec. 2024. (225 道 Exercism 最难题，覆盖 C++/Go/Java/JavaScript/Python/Rust 6 语言。) [Online]. Available: <https://aider.chat/2024/12/21/polyglot.html>

[24] Aider, "Aider LLM Leaderboards," 2026. (2026 年 5 月 Opus 4.5 ~89.4%；Opus 4.6 进一步领先。) [Online]. Available: <https://aider.chat/docs/leaderboards/>

[25] MindStudio, "Claude Code Is Doing \$2.5B in Annualized Revenue — Just from the Terminal Tool," 2026. (2026-02 Claude Code run-rate revenue 超 \$2.5B，含 API + 订阅 + 企业合同；外部估算。) [Online]. Available: <https://www.mindstudio.ai/blog/claude-code-2-5-billion-annualized-revenue-terminal-tool>
