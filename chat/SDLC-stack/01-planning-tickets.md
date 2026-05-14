# 2026-05-14：SDLC 栈 / 规划与工单 层深度研究

> 系列说明：本系列把"AI Coding Agent 普及后软件开发栈的重构"按层切片。namespace.so 是 CI/CD 层的样本——它把"PR 数量翻倍 + 每个 PR 都要全套 e2e"的新流量模式当作产品出发点。本篇研究 **D11：规划 / 工单 / 任务管理** 层。本质问题：当工单的消费者从"人类工程师"切换为"AI Agent"，工单系统的产品形态会怎么变？谁在抢这个位置？

## 1. Pre-Agent 时代的工单流量模式

行业中关于"每周每位开发者新增多少 ticket"没有权威基准，因为不同公司 ticket 颗粒度差异极大。但可拼出一个粗略图景：

- **典型工程团队 cycle time 中位数 3.4 天，前 25% 为 1.8 天，后 25% 为 6.2 天**（Accelerate State of DevOps 系列研究）；近 3000 个团队样本中位 cycle time 约 7 天，其中 PR review 阶段独占 4 天 [[1]](https://linearb.io/blog/cycle-time), [[2]](https://linearb.io/blog/lead-time-vs-cycle-time)。
- 一张 Jira ticket 的"生命周期"远长于上面的"cycle time"——后者只覆盖第一次 commit 到上线。一张典型业务 ticket 的完整生命：**PM 起草 → triage → backlog → refinement → sprint planning → 开发 → review → QA → release**，跨度通常 2–8 周。
- 人力分配比例：业界引用最多的 Xia 等人 IEEE TSE 2018 研究发现开发者约 **58% 时间花在代码理解（阅读代码、读 ticket、对齐意图）** 上 [[3]](https://ieeexplore.ieee.org/document/8048025)。换句话说，Pre-Agent 时代工单系统的隐性功能是"把意图喂进人脑"——它的 UI、字段、评论流，全是为人类的注意力曲线设计的。
- 三方协作里，**PM 写 ticket 的成本 ≪ 工程师读 ticket 的成本**。所以历史上 ticket 写得越粗越好——剩下的细节靠工程师拉 PM 进会议补齐。这是 Jira"自定义字段地狱"的根因：每个团队都试图用模板把意图固化下来，但模板永远跟不上业务。

## 2. AI Coding Agent 改变了什么

2025–2026 的关键数据点：

- **Devin（Cognition）一年内 PR merge 率从 34% 升到 67%，问题解决速度 4×，资源消耗 1/2**，累计 merge PR 数量"已达数十万" [[4]](https://cognition.ai/blog/devin-annual-performance-review-2025)。
- **Cursor agent 用户数量 1 年增长 15×，2026 年初 agent 用户已是 Tab 用户的 2 倍；Cursor 自身 35% 的 merged PR 由 agent 在云 VM 中自主开出** [[5]](https://devgraphiq.com/cursor-statistics/)。
- **GitHub Copilot coding agent**：被 assign 到 GitHub Issue 后自动开 `copilot/*` 分支、写代码、跑测试、自查失败、迭代，直到测试绿才 @ 人 review；它显式接 GitHub Issues / Azure Boards / Jira / Linear / Raycast 的工单来源 [[6]](https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/), [[7]](https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent)。
- 行业内多家团队报告"AI 用于测试生成+bug fix 后 PR cycle time 缩短 30–40%"，生产环境工单 resolution time 下降 30–50% [[8]](https://www.faros.ai/blog/claude-code-vs-devin-comparison)。

事实层面的变化：

1. **单张 ticket 的实际开发耗时从"几天"压到"30 分钟–几小时"**。一个 well-scoped ticket 由 Devin 类 agent 在 30 分钟内消费完是常态。
2. **PR 频率翻倍以上**。Cursor 的"35% PR 来自 agent"是分子端的体现；分母端，人写的 PR 数量并没显著下降，所以**总 PR 流量起码翻倍**。
3. **Ticket 颗粒度被迫细化**。Agent 在 30 分钟内消费的 unit 不是"实现登录"，而是"在 LoginForm 加一个 forgot-password 链接，文案 X，导向 /reset 路由"。这逼着 PM 写更结构化的意图，否则 agent 会跑偏。
4. **User story 形态正在分裂**。一部分 story 仍由人类拆，但拆完直接 assign 给 agent；另一部分由 agent 自己拆——Linear Agent 现在能"读 backlog、合并主题、起草 spec、生成子 ticket" [[9]](https://www.eesel.ai/blog/linear-ai)。
5. **工单数量净增**。每个原本的"大 ticket"被切成 3–10 个 agent-sized 任务，加上 agent 自己生成的 follow-up（"我修了 A 但发现 B 也得修，已开新 ticket"），**工单数量不是降，是涨**。这跟 namespace.so 在 CI 层看到的"PR 数量爆炸"是同源现象。

## 3. 新需求：Agent-readable 工单系统

把"人类消费"换成"agent 消费"之后，工单产品被迫加的能力：

- **结构化意图，不再是自由文本**。Agent 需要 acceptance criteria、affected files / repos、相关 PR、相关 doc——以可被 MCP 调用的 schema 暴露，而不是埋在 Markdown 评论里。
- **Ticket API 必须是 MCP-native**。Agent 要能 `list_issues / create_issue / update_status / comment / attach_pr`，而且要带权限、审计、可撤销。
- **工单 ↔ PR 双向绑定**。Linear、GitHub Issues、Jira 现在都做到了"PR 改状态自动改 ticket"，但 agent 场景下还需要"ticket 状态变化要回写 agent session"，让 agent 知道自己被打断/恢复了。
- **Agent 执行状态可视化**。一个 ticket 上常驻一条 agent timeline：进度、思考、调用了哪些工具、卡在哪。Linear 的 AgentSession 即此 [[10]](https://linear.app/developers/agents)。
- **Approval workflow 作为护栏**。Agent 写完 PR 后，谁来 review？什么金额/什么 repo/什么文件改动需要人 sign-off？这个权限矩阵是新一类配置。GitHub Copilot 用"agent 只能写 `copilot/*` 分支、不能 push 到 main/protected" 做隔离 [[7]](https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent)。
- **Skills / 可复用 prompt**。Linear 把"周报"、"draft spec from meeting note"沉淀为 Skill，可被人 slash command 触发或 agent 在条件满足时自动调用 [[11]](https://buttondown.com/verified/archive/the-death-of-the-ticket-why-linear-is-pivoting/)。

## 4. Linear 的具体打法

Linear CEO Karri Saarinen 2026 年 3 月公开宣布"issue tracking is dead"，把 Linear 重新定位为 **"context infrastructure for agents"** [[11]](https://buttondown.com/verified/archive/the-death-of-the-ticket-why-linear-is-pivoting/), [[12]](https://www.tbpndigest.com/story/2026-03-26/linear-ceo-karri-saarinen-declares-issue-tracking-is-dead-and-reveals-linears-ai-era-pivot)。具体动作：

**(a) Linear MCP Server**：2026-02-05 上线 PM 视角的 MCP 扩展，支持 initiatives / project milestones / updates；2026-04-23 Linear Agent 本体获得"对外调用 MCP"能力，可把 Granola 会议纪要、PostHog 数据拉进 Linear 项目作为 context [[13]](https://linear.app/changelog/2026-02-05-linear-mcp-for-product-management), [[14]](https://linear.app/changelog/2026-04-23-linear-agent-mcp-support)。MCP 服务在 Claude、Cursor、Raycast 中原生可连 [[15]](https://linear.app/docs/mcp)。

**(b) Linear Agents API（Developer Preview）**：当人类把 issue assign 给 agent（或在评论 @agent），Linear 向 agent 端 webhook 推一个 `AgentSessionEvent`（header `Linear-Event: AgentSessionEvent`，payload 用 `payload.agentSession` 而非 `payload.data`），其中包含 `promptContext`（结构化 XML，不是纯文本）、关联 issue、comment、上下文 [[10]](https://linear.app/developers/agents), [[16]](https://linear.app/developers/webhooks)。委托后 agent 接管执行，但**责任仍在被委托的人类身上**——这是关键的"agent 即同事"产品决策。

```text
# 触发：用户把 LIN-123 assign 给 Cyrus（Claude Code 驱动的 agent）
POST https://my-agent.example.com/webhook
Linear-Event: AgentSessionEvent
{
  "action": "created",
  "agentSession": {
    "id": "as_…",
    "issue": { "id": "iss_…", "identifier": "LIN-123", "title": "…" },
    "promptContext": "<context><issue>…</issue><repo>…</repo></context>",
    "actor": { "type": "user", "id": "usr_…" }
  }
}
```

**(c) "Agent 即一等公民" 的工作流**。已上架的 agent 集成包括 Devin（issue → tested PR）、Charlie（TypeScript PR plan + implement + review）、GitHub Copilot coding agent、Cyrus（Claude Code 驱动）、Huginn 等 [[17]](https://linear.app/integrations/agents)。

**(d) Linear Agent 本体**：原生 AI 界面嵌进 workspace，能跨 backlog 合并主题、起草 spec、自动生成 follow-up。**Linear 自报 75% 企业 workspace 已装至少一个 coding agent，3 个月内 agent-driven 工作量增长 5×** [[11]](https://buttondown.com/verified/archive/the-death-of-the-ticket-why-linear-is-pivoting/)。

**(e) 定价**：AI agent 功能内置在 Free / Basic ($10/seat/月) / Business ($16/seat/月) / Enterprise 四档里 **不另收 agent seat 费**，但"高用量 Automations / Code Intelligence" 预留 usage-based 升级口 [[18]](https://www.vendr.com/marketplace/linear), [[19]](https://linear.app/pricing)。这是反 Atlassian 的姿态——后者倾向把 Rovo 折成单独的 credit 包销售。

**(f) 规模**：Linear 2025-06 完成 8200 万美元 C 轮，估值 12.5 亿；2026 年宣布服务 25,000+ 组织（OpenAI 3000 席位、Ramp 从 5 人扩到 1000+ 人都长期使用 Linear）；revenue 接近 1 亿 ARR 量级 [[20]](https://sacra.com/c/linear/), [[21]](https://getlatka.com/companies/linear.app)。

## 5. Jira / Atlassian 的应对：Rovo + Teamwork Graph

Atlassian 不是没动，但动得"重而慢"：

- **Rovo Agents** 2026 GA：在 Jira 里能被分派 work item，所有动作有审计日志；Rovo Studio 允许非工程师"造 agent" [[22]](https://www.atlassian.com/software/jira/ai), [[23]](https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/)。
- **Teamwork Graph**：声称 150B+ 条 connection，新开 CLI 和 MCP server（open beta），让外部 agent 接入 [[23]](https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/)。
- **Forge `rovo:agent` 模块**：开发者用 manifest YAML 声明 agent，定义 `key / name / prompt / conversationStarters / actions`，本质是把 agent 当成 Forge app 的一类模块 [[24]](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/)。
- **Rovo Service** & **Incident Command Center**：用 agent 跑 L1 客服 / 根因分析 [[23]](https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/)。
- **采纳**：>90% 企业云客户在用 Rovo，agentic automation 6 个月 7× [[23]](https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/)。

**为什么市场仍然惩罚 Atlassian**：TEAM 股价 2026 年 2 月单月跌 36%，YTD 一度 −56%，过去 12 个月跌约 70%；Guggenheim、Barclays、BTIG 连环下调目标价至 $100–$115 区间 [[25]](https://www.tikr.com/blog/atlassian-stock-is-down-57-in-2026-heres-why-analysts-see-47-upside-to-98), [[26]](https://www.techi.com/atlassian-team-stock-crash-february-2026-analysis/), [[27]](https://247wallst.com/investing/2026/04/28/btig-lowers-atlassian-price-target-to-110-is-the-cloud-transition-story-losing-steam/)。**核心担忧叫 "seat compression"**：AI 让单个开发者抵 N 个，每位 $7.95 / $16 的 seat 收入会被吃掉。即使 Q2 FY26 收入 15.86 亿、cloud 同比 +26% 首破 10 亿/季——业务面没塌，估值面却塌了 [[28]](https://seekingalpha.com/article/4886583-atlassian-stock-collapsed-business-did-not-rating-downgrade)。

> **解读**：市场不是说 Jira 没人用了，而是说"在 agent-native 时代，Jira 这种为 human seat 设计的工具，单位 seat 价值会缩水"。Linear 已经在产品层用"agent 不占 seat 费"对冲——它愿意让 agent 的边际成本接近零，换更深的工作流绑定。Atlassian 的 Rovo 走 usage credit 路线，方向相反。

## 6. 几条本质判断

1. **当工单的消费者从人变成 agent，工单产品的"主索引"从 UI 变成 API**。以前 Jira 靠界面 + 自定义字段卷，现在卷的是 MCP schema 是否清晰、webhook payload 是否带够 context、agent session 是否能 resume。
2. **Ticket 数量爆炸是必然，但每张 ticket 的"语义密度"上升**。粗放 ticket 在 agent 时代会被立即打回（agent 在 promptContext 里说"信息不足"）。这反过来给 PM 工具创造新场景：自动把 raw idea 扩成 agent-readable 规格。
3. **工单系统正在变成"agent 编排器"**。Linear 已经在做：你不再 plan "sprint by people"，你 plan "cycle of mixed human-agent execution"。Cycle 这个抽象在 agent 时代被赋予新含义——它是 agent 调度的时间窗口，而非人类心理上的节奏。
4. **Approval workflow 是新的护城河**。当 agent 能 10 秒开 100 个 PR，"谁能 merge / 哪些路径需要 human-in-the-loop" 的策略引擎价值反超工单本身。Linear 用 issue assignment + agent session 状态机做轻量护栏；Atlassian 用 Forge audit log 做企业级合规。两条路。
5. **赢家与输家的早期信号**：Linear 的"agent 不占 seat" 是清晰的 pricing 表态——它赌长期靠 workflow 锁定，不靠 seat 收 agent 钱。GitHub Issues + Copilot coding agent 是"代码即工单"的另一极——若 ticket 本身可以由 git 流水线驱动生成，Jira/Linear 都被压扁。Jira 现在被夹在中间：上面被 Linear 抢"现代化体感"，下面被 GitHub 抢"agent-native 默认值"。Height/Plane/Shortcut/Asana AI 在这场战争里更多是"快速跟随者"，未见结构性差异化 [[29]](https://www.usepylon.com/blog/best-ai-ticketing-systems-for-customer-support-2026), [[30]](https://getathenic.com/blog/linear-vs-height-vs-plane-project-management)。
6. **"issue tracking is dead" 是营销话术，但底层在动**。Saarinen 真正想表达的：传统 ticket 的 UI/字段/审批假设的是"稀缺 + 慢"的人类执行单元；agent 时代执行单元是"廉价 + 快"的并行流，**工单系统的目标函数从'让 ticket 不丢' 变成 '让 agent 不跑偏'**。这是产品范式的换轴。

## 参考文献

[1] LinearB, "What is Cycle Time in Software Development?," *LinearB Blog*, 2024. (Accelerate DevOps median 3.4 d, top quartile 1.8 d, bottom 6.2 d.) [Online]. Available: <https://linearb.io/blog/cycle-time>

[2] LinearB, "Lead Time vs Cycle Time in Software Development," *LinearB Blog*, 2024. (~3000 teams, average cycle ~7 days, 4 days in review.) [Online]. Available: <https://linearb.io/blog/lead-time-vs-cycle-time>

[3] X. Xia, L. Bao, D. Lo, Z. Xing, A. E. Hassan, S. Li, "Measuring Program Comprehension: A Large-Scale Field Study with Professionals," *IEEE Transactions on Software Engineering*, 2018. (~58% time spent on comprehension.) [Online]. Available: <https://ieeexplore.ieee.org/document/8048025>

[4] Cognition, "Devin's 2025 Performance Review: Learnings From 18 Months of Agents At Work," *Cognition Blog*, Dec. 2025. (PR merge rate 34% → 67%; 4× faster; hundreds of thousands of merged PRs.) [Online]. Available: <https://cognition.ai/blog/devin-annual-performance-review-2025>

[5] DevGraphiq, "Cursor Statistics 2025: The Complete Data Analysis Report," 2026. (35% of Cursor merged PRs by agents; agent users 15× yoy; 2:1 vs Tab.) [Online]. Available: <https://devgraphiq.com/cursor-statistics/>

[6] GitHub, "Assigning and completing issues with coding agent in GitHub Copilot," *GitHub Blog*, 2025. [Online]. Available: <https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/>

[7] GitHub, "About GitHub Copilot cloud agent," *GitHub Docs*, 2026. (Scoped to copilot/* branches, GitHub Actions sandbox.) [Online]. Available: <https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent>

[8] Faros AI, "Claude Code vs Devin — Comparison," 2025. (30–50% resolution time drop in production.) [Online]. Available: <https://www.faros.ai/blog/claude-code-vs-devin-comparison>

[9] eesel AI, "Linear AI features: What the PM tool can do (2026)," 2026. [Online]. Available: <https://www.eesel.ai/blog/linear-ai>

[10] Linear, "Getting Started — Linear Developers (Agents)," *Linear Developer Docs*, 2026. (AgentSessionEvent webhook, promptContext XML, developer preview.) [Online]. Available: <https://linear.app/developers/agents>

[11] Buttondown / Verified, "The Death of the Ticket: Why Linear is Pivoting from Issue Tracking to 'Agent Management'," Mar. 2026. (75% of enterprise workspaces have a coding agent; 5× agent volume in 3 months; Skills concept.) [Online]. Available: <https://buttondown.com/verified/archive/the-death-of-the-ticket-why-linear-is-pivoting/>

[12] TBPN Digest, "Linear CEO Karri Saarinen declares 'issue tracking is dead' and reveals Linear's AI-era pivot," 2026-03-26. [Online]. Available: <https://www.tbpndigest.com/story/2026-03-26/linear-ceo-karri-saarinen-declares-issue-tracking-is-dead-and-reveals-linears-ai-era-pivot>

[13] Linear, "Linear MCP for product management — Changelog," 2026-02-05. [Online]. Available: <https://linear.app/changelog/2026-02-05-linear-mcp-for-product-management>

[14] Linear, "Linear Agent MCP support — Changelog," 2026-04-23. [Online]. Available: <https://linear.app/changelog/2026-04-23-linear-agent-mcp-support>

[15] Linear, "MCP server — Linear Docs," 2026. [Online]. Available: <https://linear.app/docs/mcp>

[16] Linear, "Webhooks — Linear Developers," 2026. [Online]. Available: <https://linear.app/developers/webhooks>

[17] Linear, "Agents Integrations — Linear," 2026. (Devin, Charlie, Copilot, Cyrus, Huginn等.) [Online]. Available: <https://linear.app/integrations/agents>

[18] Vendr, "Linear Software Pricing & Plans 2026," 2026. (Free / $10 / $16 / Enterprise; AI included.) [Online]. Available: <https://www.vendr.com/marketplace/linear>

[19] Linear, "Pricing — Linear," 2026. [Online]. Available: <https://linear.app/pricing>

[20] Sacra, "Linear valuation, funding & news," 2026. ($82M Series C, $1.25B valuation, Jun. 2025.) [Online]. Available: <https://sacra.com/c/linear/>

[21] Latka, "Linear App Revenue 2025: $100M ARR, $1.3B Valuation," 2026. (25,000+ orgs; OpenAI 3000 seats; Ramp 5→1000+.) [Online]. Available: <https://getlatka.com/companies/linear.app>

[22] Atlassian, "Rovo in Jira: AI features," 2026. (Rovo Agents GA, audit logs.) [Online]. Available: <https://www.atlassian.com/software/jira/ai>

[23] SiliconANGLE, "Atlassian opens Teamwork Graph and pushes Rovo into agentic execution at Team '26," 2026-05-06. (>90% enterprise customers using Rovo; 7× agentic automation in 6 months; Teamwork Graph 150B+ connections; MCP server beta.) [Online]. Available: <https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/>

[24] Atlassian Developer, "Rovo Agent — Forge Manifest Reference," 2026. [Online]. Available: <https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/>

[25] TIKR, "Atlassian Stock Is Down 57% in 2026. Here's Why Analysts See 47% Upside to $98," 2026. (Guggenheim PT $115, Barclays PT $100.) [Online]. Available: <https://www.tikr.com/blog/atlassian-stock-is-down-57-in-2026-heres-why-analysts-see-47-upside-to-98>

[26] Techi, "Why Atlassian (TEAM) Stock Crashed 36% in February 2026," 2026-02. [Online]. Available: <https://www.techi.com/atlassian-team-stock-crash-february-2026-analysis/>

[27] 24/7 Wall St., "BTIG Lowers Atlassian Price Target to $110: Is the Cloud Transition Story Losing Steam?," 2026-04-28. [Online]. Available: <https://247wallst.com/investing/2026/04/28/btig-lowers-atlassian-price-target-to-110-is-the-cloud-transition-story-losing-steam/>

[28] Seeking Alpha, "Atlassian: The Stock Collapsed, But The Business Did Not," 2026. (Q2 FY26 revenue $1.586B; cloud +26% YoY first $1B quarter.) [Online]. Available: <https://seekingalpha.com/article/4886583-atlassian-stock-collapsed-business-did-not-rating-downgrade>

[29] Pylon, "Best AI Ticketing Systems for 2026: Complete Guide," 2026. [Online]. Available: <https://www.usepylon.com/blog/best-ai-ticketing-systems-for-customer-support-2026>

[30] Athenic, "Linear vs Height vs Plane: Project Management for AI Teams," 2026. [Online]. Available: <https://getathenic.com/blog/linear-vs-height-vs-plane-project-management>
