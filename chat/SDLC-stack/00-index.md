# 2026-05-14：SDLC 工具栈 — Coding Agent 接入前后的逐层深度研究（索引）

## 起源

这一系列是 `chat/美股软件股近期重挫 (2026-05-13).md` 附录 III 的展开。该附录给出了软件开发栈的 22 层 Pre-Agent / Post-Agent 对比框架，但每一层只能放一行。**用户要求把每一层用 subagent 并行深度研究，挖到流量/任务量模式突变 → 新需求 → 解决方案 → 案例代码 这一层的本质**。范本是 namespace.so（CI/CD 那一层）。

12 个 subagent 并行后台执行，每个一篇独立报告。本索引把它们串起来。

## 文件列表（按 SDLC 先后顺序）

| # | 层 | 文件 | 字数 | 关键代表公司 |
|---|---|---|---|---|
| L01 | 规划 / 工单 | [01-planning-tickets.md](01-planning-tickets.md) | ~3300 | Linear、Atlassian Jira |
| L02 | 设计 / 架构 + Vibe coding | [02-design-vibe-coding.md](02-design-vibe-coding.md) | ~3400 | Lovable、Bolt.new、v0、Replit Agent |
| L03 | 知识 / 答疑 | [03-knowledge-qa.md](03-knowledge-qa.md) | ~3500 | Stack Overflow（衰败）、Context7、llms.txt |
| L04 | IDE + AI 编辑器 | [04-ide-ai-editor.md](04-ide-ai-editor.md) | ~3000 | Cursor、Copilot、Windsurf、Zed、JetBrains |
| L05 | 终端 / 自治 Coding Agent | [05-coding-agent-cli.md](05-coding-agent-cli.md) | ~3000 | Claude Code、Devin、Codex CLI、Aider |
| L06 | 版本控制 + AI 评审 | [06-vcs-review.md](06-vcs-review.md) | ~3100 | GitHub、GitLab、CodeRabbit、Greptile、Graphite |
| L07 | CI/CD + 构建 | [07-ci-build.md](07-ci-build.md) | ~3300 | namespace.so、Depot、Blacksmith、Buildkite、Dagger |
| L08 | 测试 Agent | [08-test-agents.md](08-test-agents.md) | ~4500 | Meticulous、Qodo、Diffblue、Browserbase |
| L09 | 安全 / 漏洞 | [09-security-vuln.md](09-security-vuln.md) | ~2800 | Socket、Snyk、Semgrep、Endor Labs、GitGuardian |
| L10 | 代码索引 + Dev MCP | [10-code-index-mcp.md](10-code-index-mcp.md) | ~3200 | Sourcegraph、Augment、9 400+ MCP server |
| L11 | 可观测 + 事故响应 | [11-observability-incident.md](11-observability-incident.md) | ~3100 | Datadog Bits AI、Sentry Seer、Honeycomb、Resolve.ai |
| L12 | 文档 + IDP | [12-docs-idp.md](12-docs-idp.md) | ~3000 | Mintlify、Backstage、Cortex、Port |

合计正文约 **4 万字**，~240 条 IEEE 引用，全部用 WebSearch / WebFetch 拉的 2025–2026 一手数据。

## 12 层一句话本质

| 层 | 一句话本质 |
|---|---|
| **L01 工单** | 工单系统的目标函数从"让 ticket 不丢"换成"让 agent 不跑偏"；产品主索引从 UI 转向 API/schema |
| **L02 Vibe coding** | 不切 Cursor / Copilot 的盘子，而是把"以前请不起工程师的人"变成新用户；$4.7B → $12.3B 全是增量市场 |
| **L03 知识答疑** | 用户行为整体跳过的第一案例（不是被替代，是动作消失）——Zendesk / Intercom / Confluence / Notion 命运预演 |
| **L04 IDE** | VS Code 是宿主级护城河；Cursor 的 $50B 押的是企业 control plane 而非补全；IDE 这一层正被 agent 从上方釜底抽薪 |
| **L05 终端 Agent** | CLI agent = "unix 进程化的开发者"——可 headless、可 SSH/CI/cron 才是真正的护城河；Copilot 在这一层失去全部飞轮 |
| **L06 VCS + 评审** | PR 抽象语义在迁移、人退到策略层；GitHub 护城河是分发不是产品；GitLab 输给"可拼装组合" |
| **L07 CI/CD** | 流量模式重写——PR 合并 +98%、单工程师日 build 5→30-80、夜间 build 占比 10%→35%；价值向上游 merge queue + 下游 ephemeral compute 外溢 |
| **L08 测试** | 单测层会被 Coding Agent 吃掉；护城河 = 拥有与代码作者独立的 oracle（用户流量、形式化规格、业务知识基线） |
| **L09 安全** | D3 是 SaaSpocalypse 中**结构性增长板块**；安全从年度审计变 per-PR 必经；behavioral integrity 是下一个未解问题 |
| **L10 代码索引 + MCP** | MCP 把"集成"从一个昂贵环节变成商品；这是 dev 工具栈所有传统 SaaS 的真实失血传导链；gateway/registry/aggregator 三层是协议级机会 |
| **L11 可观测** | Coding Agent 时代少数显著扩张的中间层；下一代 monitoring 四元组 = metrics/logs/traces/**agent traces** |
| **L12 文档 + IDP** | 文档主要读者从人变成 Agent；买家从 tech writer 转向 platform engineering；Confluence/Notion 搜索价值被 LLM 内置搜索清零 |

## 跨层主线

12 篇报告读下来，可以归纳出 6 条贯穿所有层的现象：

### 1. 流量/任务量模式突变是源头，不是"AI 写代码更快"

每一层都先看流量模式怎么变。这是用户给的 namespace.so 范式的核心。具体数字：
- **PR 合并量**：高 AI 采用团队 +98%（Faros 2026-04，见 L07）
- **单工程师日 build 量**：5 → 30-80（Cursor 2.0 8 并行 + Devin 2.0 multi-instance，见 L07）
- **夜间 build 占比**：<10% → ~35%（agent 不睡，见 L07）
- **每个 PR build 次数**：3 → 8-15（agent 自修复迭代，见 L07）
- **Devin PR merge 率**：34% → 67%（见 L01 / L06）
- **Cursor 自主 PR**：35% PR 由 agent 自主产生（见 L01）
- **Stack Overflow 新问题量**：峰值 200K/月 → 2026 近零（−77%，见 L03）
- **on-call alert 量**：60 天后 −70~95%（见 L11）
- **AI 代码漏洞密度**：+36%（见 L09）
- **AI-service secret 泄漏**：+81%（GitGuardian，见 L09）

### 2. 真正受益的是"基础设施 + 中间件 + 安全 + 可观测"，被吃掉的是"流程 SaaS"

把 12 层映射回 5/13 主文件 decliner / winner 榜：

| 主文件 winner | 对应 SDLC 层 |
|---|---|
| Datadog DDOG +30% 单日 | L11 可观测 |
| Cloudflare NET YTD +30% | L01 边缘云 + L07 CI ephemeral compute（部分） |
| AppLovin APP TTM +89% | 不在 dev 栈 |
| DigitalOcean DOCN +40% | L01 / L07 周边 |
| Okta OKTA YTD +35% | L09 安全（身份）|
| Snyk / Socket / GitGuardian（未上市） | L09 |

| 主文件 decliner | 对应 SDLC 层 |
|---|---|
| GitLab GTLB −33% (2025) | L06 全平台 SaaS（best-of-breed 解构）|
| Atlassian TEAM YTD 一度 −56% | L01 Jira + L12 Confluence + L06 Bitbucket |
| ServiceNow / Workday / Salesforce 等 | 不在 dev 栈（应用 SaaS L8）|

**结论**：在 dev 栈内部，输赢比应用 SaaS 那边的"集中失血"更分散，但**底层 / 中间件 / 安全 / 可观测显著扩张**这一规律高度一致。

### 3. 协议级机会比产品级机会更稀缺

L10 给了最清晰的视角：**MCP（2024-11 由 Anthropic 发布，2025-12 捐给 Linux Foundation）已经事实上把"集成"商品化**。9 400+ MCP server，原生支持的厂商包括 Anthropic / OpenAI / Google / Microsoft / AWS。

这条协议带来的"gateway / registry / aggregator"三层是未来 3 年最重要的机会（参见 L10）。SAP Joule MCP Gateway（主文件 SAP 章节）是企业应用栈的对应物。

### 4. "新增层"比"被吃掉的层"出现得更快

12 层里 **9 层都有新增子层**：
- L02 Vibe coding（全新象限）
- L04 AI 编辑器（Cursor 等）
- L05 终端 Coding Agent（CLI / 自治）
- L06 AI 评审（CodeRabbit / Greptile）
- L08 自治测试（Meticulous / Qodo）
- L09 AI 漏洞 / supply chain（Socket）
- L10 RAG-for-code + MCP server
- L11 AI 事故响应（Resolve.ai / Cleric）
- L12 docs-as-MCP

被掏空的层（L03 Stack Overflow / L06 GitLab 一站式叙事 / L04 老 IDE 补全）数量远少于新增层。dev 工具栈是**增量市场**，与应用 SaaS 那边的"零和重新分配"相反。

### 5. 合规 / 审计 / 数据新鲜度是 agent 时代的隐形护城河

- L06：SOC 2 CC6.1 / CC8.1 锁死"人不能完全退出"代码评审合规底线
- L09：SLSA 1.2、AI BOM、behavioral integrity
- L10：OAuth 2.1 + RFC 8707 + audit log 为 MCP server 提供企业合规栈
- L12：service catalog 真护城河是"数据新鲜度"而非可视化

这些都是 agent 时代的**新成本支出项**，对应也是新的付费产品类目。

### 6. 同一笔钱被重新切给不同链条

主文件 附录 III F 节的判断在这里得到分层验证：**SaaSpocalypse 本质是分配规则突变，不是市场缩水**。Gartner 2026 全球软件支出 +10.8% YoY，dev 栈这边 Cursor 18 个月 $0 → $2B ARR、Anthropic Claude $2.5B annualized run rate 都是**开发者自掏增量预算**，不是从 JetBrains / Atlassian / Stack Overflow 抢的存量。

## 几个值得后续追踪的开放问题

1. **MCP gateway 这一层会不会快速出现一家"AWS for AI Agent integrations"的霸主**？（参考 L10：mcp-gateway-registry、Composio Tool Router、SAP Joule Gateway 三种范式）
2. **VS Code 的宿主优势在 Zed / Cursor / Antigravity 各自做了 fork 之后能维持多久**？（L04）
3. **测试层的 oracle 问题能否被解决到让单测层完全被 Coding Agent 吸收**？（L08）
4. **PR / commit 这两个 Git 抽象本身会不会被 agent 时代的新协议替代**？（L06：stacked PR、agent commit、incremental merge queue）
5. **Datadog Bits AI / Sentry Seer 等 incumbent 的"AI 入口"叙事 vs Resolve / Cleric / Parity 的"AI native"叙事，3 年后谁赢**？（L11）
6. **Atlassian 的 Jira 业务面没塌（cloud +26%）vs 估值面塌掉（TEAM −56%）的 gap 会怎么收敛**？（L01）

## 与 5/13 主文件的衔接

主文件 `chat/美股软件股近期重挫 (2026-05-13).md` 已经在末尾追加附录 IV，链回本子目录。两份文件互为正反——主文件是"市场/股价/估值"视角，子目录是"工具栈/技术架构"视角。同一组现象（SaaSpocalypse、AI Agent 重组、卖席位的输 / 卖铲子的赢）从两边互相验证。
