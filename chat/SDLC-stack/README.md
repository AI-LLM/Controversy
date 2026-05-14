# 2026-05-14：SDLC 工具栈 — Coding Agent 接入前后的逐层深度研究（索引）

## 起源

这一系列是 [`chat/美股软件股近期重挫 (2026-05-13).md`](../美股软件股近期重挫%20(2026-05-13).md) 附录 III 的展开。该附录的 C 节给出了 SDLC 栈 **18 行**的 Pre-Agent / Post-Agent 对比框架，每行只能放一句结论。**用户要求把每一层用 subagent 并行深度研究，挖到流量/任务量模式突变 → 新需求 → 解决方案 → 案例代码 这一层的本质**。范本是 namespace.so（CI/CD 那一层）。

17 个 subagent 并行后台执行（16 个原始层 + 1 个 2026-05-14 补充层 L13），每个一篇独立报告，按 namespace.so 范式作答：
1. Pre-Agent 流量/任务量模式
2. Agent 时代如何突变
3. 由此产生的新需求
4. 代表公司技术架构（含配置示例、benchmark）
5. 几条本质判断

## 与主文件附录 III C 表的层级对应

主文件 C 表 **18 行 → 本目录 17 个文件**。两处保持有意合并（**L04** 和 **L05** 的产品本身跨界，强行拆开 70% 内容重复）；其余 3 处合并（原 L06/L10/L11）已按用户要求拆开。**L13 是 5/14 补充层**，C 表写作时漏了"产品供给侧改造"这条方向。

| 主文件 C 表行 | 本目录文件 | 备注 |
|---|---|---|
| D11 工单 | [`01-planning-tickets.md`](01-planning-tickets.md) | 1:1 |
| D10 设计 | [`02-design-vibe-coding.md`](02-design-vibe-coding.md) | 含 Vibe coding 子层（C 表未单列） |
| D9 知识 / 答疑 | [`03-knowledge-qa.md`](03-knowledge-qa.md) | 1:1 |
| **D8 IDE** + **D7' AI 编辑器** | [`04-ide-ai-editor.md`](04-ide-ai-editor.md) | **有意合并**：Cursor 既是 IDE fork 又是 AI 编辑器，拆开重复 70% |
| **D6.5 终端 Agent** + **D6.4 自治 Agent** | [`05-coding-agent-cli.md`](05-coding-agent-cli.md) | **有意合并**：Claude Code 跨终端 / Devin 跨自治，边界模糊 |
| D6 代码托管 | [`06a-vcs-hosting.md`](06a-vcs-hosting.md) | 已从原 L06 拆出 |
| D5' AI 评审 | [`06b-ai-review.md`](06b-ai-review.md) | 已从原 L06 拆出 |
| D4 CI/CD（含 C5 部署） | [`07-ci-build.md`](07-ci-build.md) | 含 C5（C 表未列） |
| D3 安全扫描 | [`09-security-vuln.md`](09-security-vuln.md) | 1:1 |
| D2 测试 | [`08-test-agents.md`](08-test-agents.md) | 1:1 |
| D8.5 代码索引 / 上下文 | [`10a-code-index.md`](10a-code-index.md) | 已从原 L10 拆出 |
| D6.6 Dev MCP servers | [`10b-mcp-servers.md`](10b-mcp-servers.md) | 已从原 L10 拆出 |
| O5 可观测 | [`11a-observability.md`](11a-observability.md) | 已从原 L11 拆出 |
| O4 错误追踪 | [`11b-error-tracking.md`](11b-error-tracking.md) | 已从原 L11 拆出 |
| O1' 事故响应 | [`11c-incident-response.md`](11c-incident-response.md) | 已从原 L11 拆出 |
| M1 文档 | [`12-docs-idp.md`](12-docs-idp.md) | 含 M3 IDP（C 表未单列） |
| **（新增）** L13 GUI → Agent 化（供给侧） | [`13-agent-interfaces.md`](13-agent-interfaces.md) | **5/14 补充**：C 表写作时漏了"产品方如何被迫给 Agent 长脸"这条主线 |

**总文件数 17 = 18 行 C 表 − 2 处有意合并 + 1 处补充层**。

## 文件统计

合计正文约 **6.3 万字**，~400 条 IEEE 引用，全部用 WebSearch / WebFetch 拉的 2025–2026 一手数据。所有引用经独立审计 round 修正：能找到出处的全部带 `[[N]](URL)`，找不到出处的所有数字 / 命名声明均显式标注 `⚠ 估算 / 解读` 并写明依据。

| # | 层 | 文件 | 字数 | 关键代表公司 |
|---|---|---|---|---|
| L01 | 规划 / 工单 | [01-planning-tickets.md](01-planning-tickets.md) | ~3300 | Linear、Atlassian Jira |
| L02 | 设计 + Vibe coding | [02-design-vibe-coding.md](02-design-vibe-coding.md) | ~3400 | Lovable、Bolt.new、v0、Replit Agent |
| L03 | 知识 / 答疑 | [03-knowledge-qa.md](03-knowledge-qa.md) | ~3500 | Stack Overflow、Context7、llms.txt |
| L04 | IDE + AI 编辑器 | [04-ide-ai-editor.md](04-ide-ai-editor.md) | ~3000 | Cursor、Copilot、Windsurf、Zed、JetBrains |
| L05 | 终端 / 自治 Coding Agent | [05-coding-agent-cli.md](05-coding-agent-cli.md) | ~3000 | Claude Code、Devin、Codex CLI、Aider |
| L06a | 代码托管 | [06a-vcs-hosting.md](06a-vcs-hosting.md) | ~2800 | GitHub、GitLab、Bitbucket、Forgejo、Codeberg |
| L06b | AI 代码评审 | [06b-ai-review.md](06b-ai-review.md) | ~2700 | CodeRabbit、Greptile、Graphite、Qodo、Pixee |
| L07 | CI/CD + 构建 | [07-ci-build.md](07-ci-build.md) | ~3300 | namespace.so、Depot、Blacksmith、Buildkite、Dagger |
| L08 | 测试 Agent | [08-test-agents.md](08-test-agents.md) | ~4500 | Meticulous、Qodo、Diffblue、Browserbase |
| L09 | 安全 / 漏洞 | [09-security-vuln.md](09-security-vuln.md) | ~2800 | Socket、Snyk、Semgrep、Endor Labs、GitGuardian |
| L10a | 代码索引 / RAG-for-code | [10a-code-index.md](10a-code-index.md) | ~2600 | Sourcegraph、Augment、Greptile、Continue、Aider |
| L10b | Dev MCP server / Agent 集成协议 | [10b-mcp-servers.md](10b-mcp-servers.md) | ~3100 | Anthropic MCP、Composio、Cloudflare AI Gateway |
| L11a | 可观测 / 监控 | [11a-observability.md](11a-observability.md) | ~2800 | Datadog Bits AI、Honeycomb、New Relic、Splunk、Langfuse |
| L11b | 错误追踪 / AI Debugging | [11b-error-tracking.md](11b-error-tracking.md) | ~2400 | Sentry Seer、Rollbar、Bugsnag、Datadog Error Tracking |
| L11c | 事故响应 / AI SRE | [11c-incident-response.md](11c-incident-response.md) | ~2700 | Resolve.ai、Cleric、Parity、Robusta、Incident.io |
| L12 | 文档 + IDP | [12-docs-idp.md](12-docs-idp.md) | ~3000 | Mintlify、Backstage、Cortex、Port |
| **L13** | **GUI → Agent 化（产品供给侧）** | [13-agent-interfaces.md](13-agent-interfaces.md) | ~3800 | Stripe Agent Toolkit、Cloudflare MCP、Computer Use、Operator、Browserbase、Manus AI、Skyvern、browser-use、**OpenCLI、CLI-Anything、Vercel agent-browser** |

## 17 层一句话本质

| 层 | 一句话本质 |
|---|---|
| **L01 工单** | 工单系统的目标函数从"让 ticket 不丢"换成"让 agent 不跑偏"；产品主索引从 UI 转向 API/schema |
| **L02 Vibe coding** | 不切 Cursor / Copilot 的盘子，把"以前请不起工程师的人"变成新用户；$4.7B → $12.3B 全是增量市场 |
| **L03 知识答疑** | 用户行为整体跳过的第一案例（不是被替代，是动作消失）——Zendesk / Intercom / Confluence / Notion 命运预演 |
| **L04 IDE + AI 编辑器** | VS Code 是宿主级护城河；Cursor 的 $50B 押的是企业 control plane 而非补全；IDE 正被 agent 从上方釜底抽薪 |
| **L05 终端 / 自治 Agent** | CLI agent = "unix 进程化的开发者"——可 headless、可 SSH/CI/cron 才是真正护城河；Copilot 在这层失去全部飞轮 |
| **L06a 代码托管** | GitHub 四占（仓库 + Copilot + VS Code + Azure）反脆弱；GitLab 一站式叙事被 best-of-breed 解构（GTLB −33%）|
| **L06b AI 评审** | "PR" 抽象语义正在迁移；人退到策略层；trust score / AI-PR 标记将被 EU AI Act 推上合规层 |
| **L07 CI/CD** | 流量模式重写——PR 合并 +98%、单工程师日 build 5→30-80、夜间 build 占比 10%→35%；价值向 merge queue + ephemeral compute 外溢 |
| **L08 测试** | 单测层会被 Coding Agent 吃掉；护城河 = 拥有与代码作者独立的 oracle（用户流量、形式化规格、业务知识基线）|
| **L09 安全** | D3 是 SaaSpocalypse 中**结构性增长板块**；安全从年度审计变 per-PR 必经；behavioral integrity 是下一个未解问题 |
| **L10a 代码索引** | 大上下文 (Augment) vs 经典 IR+embedding (Sourcegraph) 双路线，分界线 50k / 400k 文件；Sourcegraph 2025-07 砍 Cody Free/Pro 转推 Amp 是行业转向信号 |
| **L10b MCP** | MCP 把"集成"商品化；这是 dev 工具栈所有传统 SaaS 的真实失血传导链；gateway/registry/aggregator 是协议级机会 |
| **L11a 可观测** | Coding Agent 时代少数显著扩张的中间层；下一代 monitoring 四元组 = metrics/logs/traces/**agent traces** |
| **L11b 错误追踪** | Sentry Seer 是 "error → root cause → fix PR" 闭环范本；error tracking 工具变成 agent 的修复入口 |
| **L11c 事故响应** | on-call Tier 1 由 agent 接管；alert fatigue 42 pages/wk 中位数推动 AI SRE 赛道（Resolve $1.5B 估值）|
| **L12 文档 + IDP** | 文档主要读者从人变成 Agent；买家从 tech writer 转向 platform engineering；Confluence/Notion 搜索价值被 LLM 内置搜索清零 |
| **L13 GUI → Agent 化** | 2025 自动化流量首次过半（Imperva 51%、Cloudflare bot 30%、HUMAN agentic AI +7851% YoY），SaaS 必须三选一：CLI / MCP / 浏览器 Agent；Cloudflare HTTP 402 把反 Bot 从成本中心变成收入中心；OpenCLI（CLI 的 OpenAPI）+ CLI-Anything（21K stars，第三方把 GUI 应用强制 CLI 化）让 CLI 路径绕开"产品方做不做"的决策权 |

## 跨层主线（6 条贯穿整个 dev 栈的规律）

### 1. 流量/任务量模式突变是源头，不是"AI 写代码更快"

每一层都先看流量模式怎么变。这是用户给的 namespace.so 范式的核心。关键数字：
- **PR 合并量**：高 AI 采用团队 +98%（Faros 2026-04，L07）
- **单工程师日 build 量**：5 → 30-80（Cursor 2.0 8 并行 + Devin 2.0 multi-instance，L07）
- **夜间 build 占比**：<10% → ~35%（agent 不睡，L07）
- **每个 PR build 次数**：3 → 8-15（agent 自修复迭代，L07）
- **Devin PR merge 率**：34% → 67%（L01 / L06b）
- **Cursor 自主 PR**：35% PR 由 agent 自主产生（L01）
- **Stack Overflow 新问题量**：峰值 200K/月 → 2026 近零（−77%，L03）
- **on-call alert 量**：60 天后 −70~95%（L11c）
- **AI 代码漏洞密度**：+36%（L09）
- **AI-service secret 泄漏**：+81%（GitGuardian，L09）
- **自动化流量首次过半**：Imperva 51%、Cloudflare bot 30%、HUMAN agentic AI 同比 **+7 851%**（L13）—— SaaS "GUI-first" 默认假设被打穿

### 2. 真正受益的是"基础设施 + 中间件 + 安全 + 可观测"，被吃掉的是"流程 SaaS"

主文件 5/13 decliner / winner 榜可以一一映射回本目录的层：

| 主文件 winner | 本目录对应层 |
|---|---|
| Datadog DDOG +30% 单日 | L11a 可观测 |
| Cloudflare NET YTD +30% | L07 CI ephemeral compute / L10b MCP gateway |
| Okta OKTA YTD +35% | L09 安全（身份）|
| Snyk / Socket / GitGuardian（未上市） | L09 |

| 主文件 decliner | 本目录对应层 |
|---|---|
| GitLab GTLB −33%（2025）| L06a 一站式 SaaS（best-of-breed 解构）|
| Atlassian TEAM YTD 一度 −56% | L01 Jira + L12 Confluence + L06a Bitbucket |

### 3. 协议级机会比产品级机会更稀缺（L10b）

**MCP（2024-11 由 Anthropic 发布，2025-12 捐给 Linux Foundation）已经事实上把"集成"商品化**。9 400+ MCP server，原生支持的厂商包括 Anthropic / OpenAI / Google / Microsoft / AWS。

这条协议带来的"gateway / registry / aggregator"三层是未来 3 年最重要的机会。SAP Joule MCP Gateway（主文件 SAP 章节）是企业应用栈的对应物。

### 4. "新增层"比"被吃掉的层"出现得更快

C 表 18 行里 **8 行是 2024 之后全新的层**（D7' / D6.5 / D6.4 / D5' / D8.5 / D6.6 / O1' / Vibe coding 子层）；被掏空的层（D9 Stack Overflow / D6 GitLab 一站式叙事 / D8 老 IDE 补全）数量远少于新增层。dev 工具栈是**增量市场**，与应用 SaaS 那边的"零和重新分配"相反。

### 5. 合规 / 审计 / 数据新鲜度是 agent 时代的隐形护城河

- L06b：SOC 2 CC6.1 / CC8.1 锁死"人不能完全退出"代码评审合规底线；EU AI Act 第 113 条将于 2026 年推动 AI-PR 强制标记
- L09：SLSA 1.2、AI BOM、behavioral integrity
- L10b：OAuth 2.1 + RFC 8707 + audit log 为 MCP server 提供企业合规栈
- L12：service catalog 真护城河是"数据新鲜度"而非可视化

### 6. 同一笔钱被重新切给不同链条

主文件附录 III F 节判断在这里得到分层验证：**SaaSpocalypse 本质是分配规则突变，不是市场缩水**。Gartner 2026 全球软件支出 +10.8% YoY，dev 栈这边 Cursor 18 个月 $0 → $2B ARR、Anthropic Claude $2.5B annualized run rate 都是**开发者自掏增量预算**，不是从 JetBrains / Atlassian / Stack Overflow 抢的存量。

## 几个值得后续追踪的开放问题

1. **MCP gateway 这一层会不会快速出现一家"AWS for AI Agent integrations"的霸主**？（L10b：mcp-gateway-registry、Composio Tool Router、SAP Joule Gateway、Cloudflare AI Gateway 四种范式）
2. **VS Code 的宿主优势在 Zed / Cursor / Antigravity 各自做了 fork 之后能维持多久**？（L04）
3. **测试层的 oracle 问题能否被解决到让单测层完全被 Coding Agent 吸收**？（L08）
4. **PR / commit 这两个 Git 抽象本身会不会被 agent 时代的新协议替代**？（L06a/b：stacked PR、agent commit、incremental merge queue）
5. **Datadog Bits AI / Sentry Seer 等 incumbent 的"AI 入口"叙事 vs Resolve / Cleric / Parity 的"AI native"叙事，3 年后谁赢**？（L11a/b/c）
6. **Atlassian 的 Jira 业务面没塌（cloud +26%）vs 估值面塌掉（TEAM −56%）的 gap 会怎么收敛**？（L01）
7. **第四元组 (metrics/logs/traces/agent traces) 的术语会被哪家定义**？Mezmo、CloudQuery、Anthropic、Datadog 都在抢（L11a）

## 与 5/13 主文件的衔接

主文件 [`chat/美股软件股近期重挫 (2026-05-13).md`](../美股软件股近期重挫%20(2026-05-13).md) 附录 III 的 C 表是本目录的索引母表，本目录是 C 表的展开。两份文件互为正反——主文件是"市场 / 股价 / 估值"视角，本目录是"工具栈 / 技术架构"视角。同一组现象（SaaSpocalypse、AI Agent 重组、卖席位的输 / 卖铲子的赢）从两边互相验证。
