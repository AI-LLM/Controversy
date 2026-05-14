# 2026-05-14：SDLC 栈 / 规划与工单 层深度研究

> 系列说明：namespace.so 是 CI/CD 层的样本，把"任务流量"作分析角度——因为 CI 的核心变量是 throughput。其他层有更自然的角度。**本篇的角度是"消费者切换 (consumer switch)"**——工单产品的读者从人脑切换为 LLM。由此推论意图保真度成为新瓶颈、代理拓扑被重画、seat 经济学反转。"工单流量爆炸"是上述变化的下游症状，不是本质。

## 1. 视角：为什么 L01 的本质不是流量

CI/CD 的核心变量是 throughput——build 数量、并行度、cache 命中。工单层的核心变量不是这个：

- 工单总数虽然涨（agent 切碎了原本的大 ticket），但这不是工单产品价值的主导变量。Pre-Agent 时代，Jira 卷的也不是"能存多少条"，而是**如何把意图喂进人脑**。
- 真正的变量是**工单的消费者**：Pre-Agent 是人类工程师；Post-Agent 越来越多是 AI Agent——Devin、Claude Code、GitHub Copilot coding agent、Cursor agent。
- 一旦消费者变了，工单的 UI、字段、schema、approval、定价**全部假设**都得重审。

Linear CEO Karri Saarinen 2026-03 说 "issue tracking is dead" [[11]](https://buttondown.com/verified/archive/the-death-of-the-ticket-why-linear-is-pivoting/) [[12]](https://www.tbpndigest.com/story/2026-03-26/linear-ceo-karri-saarinen-declares-issue-tracking-is-dead-and-reveals-linears-ai-era-pivot)——不是说没人开 ticket 了，而是说"为人类阅读设计的工单"这个产品形态死了。

## 2. Pre-Agent 工单：为人脑设计

Pre-Agent 时代工单系统的**隐性功能**是把意图喂进人脑。所有产品决策都围绕这个：

- **理解成本是主要矛盾**。Xia 等 IEEE TSE 2018 研究显示开发者约 **58% 时间花在代码理解、读 ticket、对齐意图**上 [[3]](https://ieeexplore.ieee.org/document/8048025)。工单 UI（评论流、@提及、字段、附件）都是为了**降低人脑加载意图的摩擦**。
- **写读不对称**。PM 写 ticket 的成本 ≪ 工程师读 ticket 的成本。所以历史上 ticket 写得越粗越好——剩下细节靠人拉会议补齐。**Jira "自定义字段地狱"的根因**：每个团队都试图用模板把意图固化下来，但模板永远跟不上业务。
- **生命周期为人类节奏服务**。典型业务 ticket 的完整生命：PM 起草 → triage → backlog → refinement → sprint planning → 开发 → review → QA → release，跨度通常 **2–8 周**（⚠ 行业经验值，作者综合估算；依据：Atlassian 推荐 sprint 2 周、backlog refinement 每 sprint 一次、多数业务 ticket 跨 1–3 个 sprint [[31]](https://www.atlassian.com/agile/tutorials/sprints) [[32]](https://www.atlassian.com/agile/project-management/backlog-refinement-meeting)）。
- **Cycle time 基线**。典型工程团队 cycle time 中位 **3.4 天**，前 25% 为 1.8 天，后 25% 为 6.2 天（Accelerate State of DevOps 系列）；~3000 个团队样本中位 cycle time 约 7 天，**PR review 独占 4 天** [[1]](https://linearb.io/blog/cycle-time) [[2]](https://linearb.io/blog/lead-time-vs-cycle-time)。Review 4 天的瓶颈是人脑加载意图的等待时间，不是 throughput。

总结：Pre-Agent 工单是**意图 anchor**——它说大概是什么，剩下靠人脑、靠会议、靠 face-to-face 把意图补全。工单不需要自包含。

## 3. Post-Agent 工单：为 LLM 设计

消费者切换为 LLM 之后，Pre-Agent 假设几乎全部翻转：

### 3.1 意图必须自包含

Agent 不能主动拉 PM 进会议澄清。它能做的最多是"在 promptContext 里说'信息不足'"，然后人 review 时看到 agent 卡住。这对 ticket 的**意图保真度**提了硬约束：

- 必须有可执行级 acceptance criteria：不是"做一个登录页面"，而是"在 LoginForm 加一个 forgot-password 链接，文案 X，导向 /reset 路由"
- 必须显式列出 affected files / repos / 相关 PR / 相关 doc 链接
- 隐性约束（数据库 schema、auth flow、错误处理标准）必须显式 link 或挂在 CLAUDE.md / agent context 里

Linear 这步走在前面：`promptContext` 用**结构化 XML 而非 Markdown 评论** [[10]](https://linear.app/developers/agents)——这本身就承认了"agent 不会自动阅读理解评论流"。

### 3.2 颗粒度细化（不是想，是必须）

Devin 一个 ACU ≈ 15 分钟有效执行 [[33]](https://cognition.ai/blog/how-cognition-uses-devin-to-build-devin)；Cognition 自报安全漏洞修复 ~1.5 分钟/张、ETL 单文件迁移 3–4 小时 [[33]](https://cognition.ai/blog/how-cognition-uses-devin-to-build-devin)。**Cursor / Devin 30 分钟内消费完一个 well-scoped ticket 已是常态**（⚠ 解读；依据：上述 Cognition 数据 + Cursor agent 用户 1 年增 15× 与 35% PR 由 agent 自主开 [[5]](https://devgraphiq.com/cursor-statistics/)）。

这逼着 PM 写更细：原本的"大 ticket"被切成 **3–10 个 agent-sized 任务**（⚠ 行业经验值，作者综合估算；依据：Linear Agent 自报 3 个月 agent-driven 工作量 5× [[11]](https://buttondown.com/verified/archive/the-death-of-the-ticket-why-linear-is-pivoting/) + Devin/Cursor 公开的 ACU/PR 单位推算）。这是**结构性 by-product**，不是产品想做就能不做。

### 3.3 Schema > Markdown

Pre-Agent 工单的"自由文本评论流"是 feature——人脑擅长从对话里抽 context。Post-Agent，自由文本变 anti-feature——LLM 读不出隐含承诺、说话者权重、未说的部分。新需求：

- **Ticket schema 可被 MCP 调用**：`list_issues / create_issue / update_status / comment / attach_pr`，带权限、审计、可撤销
- **工单 ↔ PR 双向绑定**：状态变化要回写 agent session（让 agent 知道自己被打断 / 恢复）[[10]](https://linear.app/developers/agents)
- **Agent 执行 timeline 嵌入 ticket**：进度、思考、调用的工具、卡点——Linear AgentSession 即此 [[10]](https://linear.app/developers/agents)
- **Skills / 可复用 prompt**：高频 workflow（"周报"、"draft spec from meeting note"）沉淀为 Skill，可被 slash command 触发或 agent 在条件满足时自动调用 [[11]](https://buttondown.com/verified/archive/the-death-of-the-ticket-why-linear-is-pivoting/)

## 4. 代理与责任拓扑（agency topology）

消费者切换之后第二个被重画的是**谁负责**。当 agent 能 10 秒开 100 个 PR，老的"工程师对 PR 负责"假设崩了。两个产品决策框架的对照：

### 4.1 Linear："agent 即同事，但责任在被委托的人类身上"

Linear Agents API 的关键设计 [[10]](https://linear.app/developers/agents)：人把 issue assign 给 agent（或在评论 @agent），Linear 向 agent 端 webhook 推一个 `AgentSessionEvent`（header `Linear-Event: AgentSessionEvent`，payload 用 `payload.agentSession` 而非 `payload.data`），其中包含 `promptContext`（结构化 XML，不是纯文本）、关联 issue、comment、上下文 [[16]](https://linear.app/developers/webhooks)。委托后 agent 接管执行，但**责任仍在被委托的人类身上**——这是关键的"agent 即同事"产品决策。

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

已上架的 agent 集成包括 Devin（issue → tested PR）、Charlie（TypeScript PR plan + implement + review）、GitHub Copilot coding agent、Cyrus（Claude Code 驱动）、Huginn 等 [[17]](https://linear.app/integrations/agents)。

### 4.2 GitHub Copilot：用沙箱 + 分支约定划界

GitHub Copilot coding agent 走另一条 [[6]](https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/) [[7]](https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent)：被 assign 到 Issue 后自动开 `copilot/*` 分支、写代码、跑测试、自查失败、迭代，直到测试绿才 @ 人 review。**显式限制：agent 只能写 `copilot/*` 分支，不能 push 到 main/protected**。

这是不同的产品哲学：**用沙箱隔离 + 分支约定**代替"agent 即同事"。Agent 像"自动化的实习生"，责任完全在 reviewer 身上。Linear 把 agent 当人组织 workflow，GitHub 把 agent 当流水线组织。

### 4.3 Approval workflow 是新护城河

两种哲学的共通点：approval workflow 成为新付费层。当 agent 能 10 秒开 100 个 PR，"谁能 merge / 哪些路径需要 human-in-the-loop"的策略引擎价值反超工单本身。

- Linear 用 issue assignment + agent session 状态机做轻量护栏
- Atlassian 用 Forge audit log + Rovo Studio 做企业级合规 [[22]](https://www.atlassian.com/software/jira/ai) [[23]](https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/) [[24]](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/)
- GitHub 用 branch protection rules + Actions sandbox 做隔离 [[7]](https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent)

三条路都把"谁有权让 agent 合并代码"做成产品差异点。

## 5. Seat 经济学反转

消费者切换之后第三个被重画的是定价。Pre-Agent: **一个 seat = 一个 productive unit**。Post-Agent: **seat 是入口、agent 是产能**——同一个 seat 上的人可以挂 8 个并行 agent 跑活（Cursor 2.0 8 并行的同源逻辑）。seat 单价的天然上限被压制了。

### 5.1 Linear：agent 不收 seat 费

Linear 把 AI agent 功能内置在 Free / Basic ($10/seat/月) / Business ($16/seat/月) / Enterprise 四档里**不另收 agent seat 费**，但"高用量 Automations / Code Intelligence" 预留 usage-based 升级口 [[18]](https://www.vendr.com/marketplace/linear) [[19]](https://linear.app/pricing)。

这是清晰的产品决策：让 agent 的边际成本接近零，换更深的 workflow 锁定。**赌赢家在 schema / context / approval 那一层，而不是 seat 数量**。

规模佐证：Linear 2025-06 完成 8200 万美元 C 轮，估值 12.5 亿；2026 年宣布服务 25 000+ 组织（OpenAI 3000 席位、Ramp 从 5 人扩到 1000+ 人都长期使用）；revenue 接近 1 亿 ARR 量级 [[20]](https://sacra.com/c/linear/) [[21]](https://getlatka.com/companies/linear.app)。

### 5.2 Atlassian：Rovo 走 credit 包销售

Atlassian 把 Rovo 折成单独 credit 包：

- **Rovo Agents** 2026 GA：在 Jira 里能被分派 work item，所有动作有审计日志；Rovo Studio 允许非工程师"造 agent" [[22]](https://www.atlassian.com/software/jira/ai) [[23]](https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/)
- **Teamwork Graph**：声称 150B+ 条 connection，新开 CLI 和 MCP server（open beta）[[23]](https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/)
- **Forge `rovo:agent` 模块**：开发者用 manifest YAML 声明 agent，本质是把 agent 当成 Forge app 的一类模块 [[24]](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/)
- **采纳**：>90% 企业云客户在用 Rovo，agentic automation 6 个月 7× [[23]](https://siliconangle.com/2026/05/06/atlassian-opens-teamwork-graph-pushes-rovo-agentic-execution-team-26/)
- **业务面**：Q2 FY26 收入 15.86 亿、cloud +26% 首破 10 亿/季 [[28]](https://seekingalpha.com/article/4886583-atlassian-stock-collapsed-business-did-not-rating-downgrade)——没塌

### 5.3 市场用 TEAM −56% 给 seat compression 定价

业务面没塌，估值面塌了。**TEAM 股价 2026 年 2 月单月跌 36%，YTD 一度 −56%，过去 12 个月跌约 70%**；Guggenheim、Barclays、BTIG 连环下调目标价至 $100–$115 区间 [[25]](https://www.tikr.com/blog/atlassian-stock-is-down-57-in-2026-heres-why-analysts-see-47-upside-to-98) [[26]](https://www.techi.com/atlassian-team-stock-crash-february-2026-analysis/) [[27]](https://247wallst.com/investing/2026/04/28/btig-lowers-atlassian-price-target-to-110-is-the-cloud-transition-story-losing-steam/)。

核心担忧叫 **"seat compression"**：AI 让单个开发者抵 N 个，Jira Standard ~$7.91、Premium ~$15.25 / user / month（年付，2026 公开报价区间）的 seat 收入会被吃掉 [[34]](https://www.atlassian.com/software/jira/pricing) [[35]](https://tech.co/project-management-software/jira-pricing)。

> **解读**：市场不是说 Jira 没人用了，而是说"在 agent-native 时代，Jira 这种为 human seat 设计的工具，单位 seat 价值会缩水"。Linear 已经在产品层用"agent 不占 seat 费"对冲——愿意让 agent 边际成本接近零，换 workflow 锁定。Atlassian Rovo 走 usage credit 路线，方向相反。两条路 2-3 年内会有清晰胜负。

## 6. 流量症状：消费者切换已经发生的旁证

虽然流量不是 L01 的核心 lens，但症状本身值得记下来——它们证实"消费者切换"已经发生：

- **Devin（Cognition）一年内 PR merge 率 34% → 67%，问题解决速度 4×，资源消耗 1/2**，累计 merge "数十万张" [[4]](https://cognition.ai/blog/devin-annual-performance-review-2025)
- **Cursor agent 用户 1 年增 15×，2026 年初已是 Tab 用户的 2 倍；Cursor 自身 35% merged PR 由 agent 在云 VM 中自主开出** [[5]](https://devgraphiq.com/cursor-statistics/)
- **GitHub Copilot coding agent** 显式接 GitHub Issues / Azure Boards / Jira / Linear / Raycast 多个工单来源 [[6]](https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/) [[7]](https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent)
- **AI 用于测试生成 + bug fix 后 PR cycle time 缩短 30–40%，生产环境工单 resolution time 下降 30–50%** [[8]](https://www.faros.ai/blog/claude-code-vs-devin-comparison)
- **Linear 自报 75% 企业 workspace 已装至少一个 coding agent，3 个月 agent-driven 工作量增长 5×** [[11]](https://buttondown.com/verified/archive/the-death-of-the-ticket-why-linear-is-pivoting/)
- **Linear AI 功能拉动 25 000+ 组织规模**：OpenAI 3000 seats、Ramp 5→1000+ [[20]](https://sacra.com/c/linear/) [[21]](https://getlatka.com/companies/linear.app)

这些数据指向同一件事：**工单消费方已经从"主要是人类"变成"人 + agent 混合"，agent 比例还在快速上升**。但**消费者切换是因，流量变化只是果**——所以前 5 节才是 L01 的本体，本节只是症状记录。

## 7. 几条本质判断

1. **当工单的消费者从人变成 agent，工单产品的"主索引"从 UI 变成 API**。以前 Jira 靠界面 + 自定义字段卷，现在卷的是 MCP schema 是否清晰、webhook payload 是否带够 context、agent session 是否能 resume。
2. **意图保真度是新瓶颈**。Pre-Agent，"工单写得粗、人脑补足"是 feature；Post-Agent，"工单写得粗、agent 跑偏"是 bug。这反过来给 PM 工具创造新场景：**自动把 raw idea 扩成 agent-readable 规格**——Linear 用 Skills 走在前面，Notion AI / Granola 这类记录工具会从外围切入。
3. **代理拓扑决定责任边界，责任边界决定合规底线**。Linear "agent 即同事但责任在人" + GitHub "agent 沙箱化" 两条路都有市场，但都把 approval workflow 推上付费层。这是企业版的主要差异化点；可被 EU AI Act 推上强制合规层。
4. **Seat 经济学反转：Linear 0 收 agent vs Atlassian credit 包销，市场已经用 TEAM −56% 投票**。Linear 押 workflow 锁定不靠 seat；Atlassian 想保 seat ARPU 但被 AI 挤压。3 年内见分晓——若 Linear 押对，整个 PM 工具分类的定价结构会被重写。
5. **GitHub Issues + Copilot coding agent 是第三极**——"代码即工单、issue 由 git 流水线驱动"。Linear / Jira 都被压扁的风险是 **ticket 这个抽象本身被 issue tracker 之外的工具吸收**。Height / Plane / Shortcut / Asana AI 在这场战争里更多是快速跟随者，未见结构性差异化 [[29]](https://www.usepylon.com/blog/best-ai-ticketing-systems-for-customer-support-2026) [[30]](https://getathenic.com/blog/linear-vs-height-vs-plane-project-management)。
6. **"issue tracking is dead" 是营销话术但底层在动**。Saarinen 真正想表达的：传统 ticket 的 UI / 字段 / 审批假设的是"稀缺 + 慢"的人类执行单元；agent 时代执行单元是"廉价 + 快"的并行流，**工单系统的目标函数从'让 ticket 不丢' 变成 '让 agent 不跑偏'**。这是产品范式的换轴，整章可压缩为这一句。

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

[31] Atlassian, "How to create and use sprints in Jira," *Atlassian Agile Coach*, 2026. (Recommended sprint length: 2 weeks; typical range 1–4 weeks.) [Online]. Available: <https://www.atlassian.com/agile/tutorials/sprints>

[32] Atlassian, "How to master backlog refinement meetings," *Atlassian Agile Coach*, 2026. (Backlog refinement cadence: at least once per sprint, 2–3 days before sprint end for two-week sprints.) [Online]. Available: <https://www.atlassian.com/agile/project-management/backlog-refinement-meeting>

[33] Cognition, "How Cognition Uses Devin to Build Devin," *Cognition Blog*, 2025. (Security vuln fixes ~1.5 min vs human 30 min; ETL single-file migration 3–4 h; 1 ACU ≈ 15 min Devin active work.) [Online]. Available: <https://cognition.ai/blog/how-cognition-uses-devin-to-build-devin>

[34] Atlassian, "Jira pricing — Free, Standard, Premium, Enterprise," *Atlassian Official*, 2026. (Standard ~$7.91 / user / month, Premium ~$15.25 / user / month, annual billing.) [Online]. Available: <https://www.atlassian.com/software/jira/pricing>

[35] Tech.co, "Jira Pricing Guide 2026: Plans, Hidden Fees, and More," 2026. (Cross-verifies Standard $7.91 / Premium $15.25 user/month annual; monthly billing higher.) [Online]. Available: <https://tech.co/project-management-software/jira-pricing>
