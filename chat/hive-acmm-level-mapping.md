# hive 代码库与 ACMM 六个 Level 的逐项对照

把论文 *The AI Codebase Maturity Model: From Assisted Coding to Fully Autonomous Systems*（Andy Anderson, IBM Research）里定义的六级成熟度模型，逐 Level 落到 `data/hive` 这个示例代码库的**具体文件和具体内容**上。

## 阅读前必须先分清的两层

论文里 hive 是 **Level 6 的参考实现**（reference implementation），不是 Level 1–5 的案例。Level 1–5 的案例是另一个仓库 **KubeStellar Console**（论文 §4）。但 `data/hive` 这个仓库里**同时沉淀了两类东西**，对照时不要混：

- **hive 本体**（`bin/`、`config/`、`systemd/`、`dashboard/`、`docs/`）—— 多智能体编排引擎本身。它直接对应 **Level 4–6** 的"基础设施级"产物（治理、合并队列、健康自愈、可观测性）。
- **`examples/kubestellar/`** —— 把 KubeStellar Console 项目里的实际配置抽成模板放进来。它是 **Level 1–5** 产物（指令文件、策略、技能、状态库 schema）的可复制样本。

所以下面每个 Level，"对应文件"既可能在 hive 本体里，也可能在 `examples/kubestellar/` 里。事实陈述（文件确实存在、内容确实如此）我都给了 `路径:行号`；判断性的对应关系标注为解读。

---

## Level 1 — Assisted（提示与审查）

**论文描述**：人发起每一次交互，AI 是高级自动补全，会话之间无持久上下文。**关键产物：除代码本身外没有任何产物**——所有偏好、模式、架构决策都只在开发者脑子里。

**对应文件**：按定义，**Level 1 在代码库里留不下任何专属文件**。这一级的"证据"恰恰是它的缺席——没有 `CLAUDE.md`、没有策略文件、没有测试门禁。

hive 仓库里能间接看到 L1 痛点被反复点名的地方，是策略文件里"不要依赖上下文记忆"的硬规定：

- `examples/scanner-policy.md:13-25`（Step 0 pre-flight re-read）：`**Do NOT rely on in-context memory from previous iterations.**` —— 这正是论文说 L1 "会话间无持久上下文"的反制措施，把它从"脑子里"逼进文件。

**判断（解读）**：在成熟的 hive 体系里 L1 已经被完全消化。它在仓库里不是一个文件，而是被 L2 的指令文件取代掉的一个**空位**。

---

## Level 2 — Instructed（编码化的偏好）

**论文描述**：偏好、约定、架构决策被写进文件，AI 每次会话开始时读取。典型实践：`CLAUDE.md`、`.github/copilot-instructions.md`、PR 模板、卡片/组件开发指南。**关键产物：指令文件、风格指南**。

**对应文件**：

- **每个 agent 的 CLAUDE.md（核心指令文件）**：
  - `examples/kubestellar/agents/scanner-CLAUDE.md`、`reviewer-CLAUDE.md`、`architect-CLAUDE.md`、`outreach-CLAUDE.md`、`supervisor-CLAUDE.md`、`analyst-CLAUDE.md`、`tester-CLAUDE.md`、`guardian-CLAUDE.md`、`sec-check-CLAUDE.md`、`strategist-CLAUDE.md`、`ci-maintainer-CLAUDE.md`
  - 内容就是论文说的"把拒绝 PR 的理由编码成规则"。例如 `scanner-CLAUDE.md:3-9` 的 `⛔ HOLD LABEL — ABSOLUTE HARD STOP`、`:17` 的 `⛔ ADOPTERS.md PRs — DO NOT TOUCH`、`:25` 的 `⛔ NO @copilot/@claude DISPATCH`——每一条都对应论文里那句"a single card development guide encoded approximately 90% of the reasons I had been rejecting AI-generated PRs"，即把人工拒绝理由沉淀成硬规则。
  - `scanner-CLAUDE.md:39` 的 `Output Rules — Terse Mode`：把风格约定（去冠词、去客套、片段化）编码进指令，正是论文说的"codified style guides"。

- **agent 行为策略文件（policy / 即论文 L6 的"agent policy files"，但其内容主体是 L2 指令）**：
  - `examples/scanner-policy.md`、`examples/reviewer-policy.md`、`examples/architect-policy.md`、`examples/outreach-policy.md`
  - 这些是"agent 每次 firing 都重读"的 markdown 规则书。论文在 L6 把它叫 *Agent policy files*，但其**内容**是 L2 性质的指令编码。

- **技能文件（skills，把可复用工作流编码）**：
  - `examples/kubestellar/agents/reviewer-skills/coverage.md`、`health-checks.md`、`goodnight.md`、`ga4-watch.md`
  - `examples/kubestellar/agents/architect-skills/ideation.md`、`beads-status.md`
  - `examples/kubestellar/agents/outreach-skills/awesome-lists.md`、`acmm-outreach.md`

**判断（解读）**：hive 把 L2 推到了极致——指令不是一个 `CLAUDE.md`，而是**按角色分文件**的指令矩阵（11 个 CLAUDE.md + 4 个 policy + 10+ skills）。论文 §6.2 "Ask Questions, Not Commands" 描述的"questions produce instructions as a side effect"，物化结果就是这一堆持续增长的指令文件。

---

## Level 3 — Measured（反馈变得可见）

**论文描述**：系统产出关于 AI 表现的**量化信号**——接受率、覆盖率、错误率、用户反馈被系统化追踪。典型实践：按类别追踪 PR 接受率、每个 PR 上的覆盖率门禁、夜间测试套件、GA4 错误监控、NPS。**关键产物：接受率日志（如 `auto-qa-tuning.json`）、覆盖率报告、监控面板、错误分类系统**。

**对应文件**：

- **错误监控（GA4）—— 把生产错误变成可见信号**：
  - `bin/ga4-anomaly-detector.sh:1-8`：`Compares recent error counts against 7-day baseline. Writes /var/run/hive-metrics/ga4-anomalies.json` —— 这就是论文说的"GA4 or equivalent error monitoring"，把 7 天基线对比预计算成 JSON 给 reviewer agent 用。
  - `examples/kubestellar/agents/reviewer-skills/ga4-watch.md`：reviewer 消费 GA4 异常信号的技能。

- **覆盖率度量与门禁**：
  - `bin/fetch-coverage.sh`：抓取覆盖率。
  - `examples/kubestellar/agents/reviewer-skills/coverage.md:5-9`：`maintain ≥91% — FIX MANDATORY`，明确 91% 阈值——对应论文 Table 3 的 "Code coverage 91% across 12 shards (L3)"。

- **健康检查（把 CI/夜间/部署状态量化成 1/0/-1）**：
  - `examples/kubestellar/agents/reviewer-skills/health-checks.md:13`：health-check.sh 返回 `ci/brew/helm/nightly/.../hourly` 的 `1=ok, 0=fail, -1=unknown` JSON——错误分类系统的雏形。
  - `dashboard/health-check.sh`：生成该 JSON。

- **接受率追踪 / 错误分类**：
  - `bin/issue-classifier.sh:1-6`：`Enriches actionable.json with: complexity_tier, model_recommendation, is_tracker, cluster_key, lane, needs_architecture_review` —— 确定性的 issue 分类系统。
  - 论文点名的 `auto-qa-tuning.json` **不在 hive 本体里**（它属于 KubeStellar Console 仓库）。hive 里对应的痕迹是 `auto-qa-tuning-report` 标签（`bin/kick-governor.sh:79` 把它列入 governor 的豁免标签），以及 `examples/kubestellar/auto-qa-skill.md` 描述的 auto-qa issue 处理流程。

- **监控面板（度量的呈现层）**：
  - `dashboard/server.js`、`dashboard/index.html`、`dashboard/agent-metrics.sh`、`dashboard/token-collector.sh`、`bin/token-usage.py`、`bin/token-collector.sh`：token 消耗、agent 活跃度等度量采集与展示。

**判断（解读）**：论文强调 L3 的突破是"Testing"。在 hive 里，"测试可信度"这件事的载体不是测试代码本身（那在 Console 仓库），而是 **reviewer 的强制修复义务**——coverage.md 和 health-checks.md 都写着 "Do NOT just report... FIX MANDATORY"，即把"度量"直接绑死到"必须行动"，这其实已经在向 L4 过渡。

---

## Level 4 — Adaptive（反馈环自我闭合）

**论文描述**：系统对自己的度量采取行动，阈值触发自动响应，人的监督从执行转向治理。典型实践：基于 PR 接受率自调权重、自动 issue triage 环（每 15 分钟跨多仓）、隔夜自动修 bug、worktree 并发会话。**关键产物：自修改配置文件（如 `auto-qa-tuning.json`，接受率低于 20% 的类别自动屏蔽）、闭环 CI/CD 流水线**。

**对应文件**：

- **自动 triage 环 + 闭环流水线（L4 的核心机制）**：
  - `bin/run-pipeline.sh:11-13`：`enumerator → classifier → gate → monitor`，确定性的预-kick 流水线，在任何 LLM 看到工作前先跑过滤、分类、合并门禁、监控。
  - `bin/enumerate-actionable.sh`：枚举可执行的 issue/PR backlog，写 `actionable.json`。
  - `bin/kick-agents.sh`、`bin/supervisor-kick.sh`：每个周期把 agent kick 起来——对应论文"automated issue triage loops (every 15 minutes across multiple repos)"。

- **阈值触发的自动响应 / 治理（governor）**：
  - `bin/kick-governor.sh:11-32`：SURGE/BUSY/QUIET/IDLE 四档，按 backlog 深度切换每个 agent 的 cadence。这是论文 L4 "thresholds trigger automated responses, human oversight shifts from execution to governance" 的直接实现——阈值在文件里（`SURGE_THRESHOLD_ISSUES:-20` 等，`:82-85`），人调阈值不调单次行为。
  - （注意：论文把 governor 主要算作 L6 的"adaptive workload governance"。它横跨 L4/L6——L4 是"阈值触发自动响应"的思想，L6 是"多 agent 自适应治理"的完整形态。同一个文件，两级都指向它。）

- **worktree 并发会话**：
  - `examples/scanner-policy.md:32`：`Fix what you can using git worktrees (never commit directly to main)` —— 对应论文 Table 3 "Concurrent AI sessions: Multiple via git worktrees (L4)"。

- **自修改配置**：
  - 论文的标志性产物 `auto-qa-tuning.json`（"categories with acceptance rates below 20% are automatically blocked"）**实体在 Console 仓库**。hive 里的等价机制是 governor 的 `EXEMPT_LABEL_REGEX`（`bin/kick-governor.sh:79`）和 cost weight（`:138-141`、`:392-402`）——这些值都"sourced from an env file on every tick"（`/etc/hive/governor.env`），改文件即改行为、无需重启，符合论文 L4 "self-tuning rotation weights" 的运行模型。

**判断（解读）**：hive 把 L4 的"自修改配置"做成了**配置外置 + 每 tick 重读**的模式（governor.env、policy md 每次 firing 重读），而不是程序写回 JSON。两者等价：都让"代码即策略"，人不再做实时决策。论文 anti-pattern "autonomous action without sufficient guardrails" 的护栏，就是 L3 的度量（覆盖率门禁、merge-gate）。

---

## Level 5 — Semi-Automated（系统提议，人批准）

**论文描述**：系统检测问题并提议修复，无需人发起；但人仍然批准——系统提议，不自主合并。典型实践：社区驱动的 issue→实现流水线（bug 30 分钟内修，feature 60 分钟内实现）、多 agent 跨仓编排、自改进环（系统分析自己合并的 PR 并更新指南）。**关键产物：整个代码库即 AI 的操作手册**——每个测试是信任约束，每个 workflow 是策略，每个度量阈值是优先级决策。

**对应文件**：

- **"代码库即操作手册" 的物化**：
  - `examples/scanner-policy.md` 整篇就是论文这句话的样本——它把 SLA（`:50` "30 min from issue-filed to PR-merged"）、"NEVER idle"（`:46`）、queue-debt auto-dispatch（`:54`）等写成 agent 每次重读的手册。
  - `examples/kubestellar/fix-loop-skill.md`：issue→fix 的自动化流水线技能（含 `:44` SKIP、`:114` backoff 规则）。

- **多 agent 跨仓编排（L5 提议形态）**：
  - `bin/supervisor.sh`、`bin/supervisor-kick.sh`：supervisor 协调多个 agent。
  - `examples/kubestellar/hive-project.yaml`、`config/hive-project.yaml.example`：`repos:` 列出跨仓范围（`:13-15`），多仓 backlog 统一治理。

- **自改进环**：
  - `bin/kick-outcome-tracker.sh`：追踪 kick 的产出（系统观察自己的行为）。
  - `examples/kubestellar/agents/architect-skills/ideation.md`：architect 在空闲周期产出改进提案——对应论文"self-improvement cycles"。

**判断（解读）**：L5 与 L6 的唯一区别论文说得很死："at L5, the system proposes; at L6, it acts"。在 hive 里，这条线就是 **merge-gate + 是否自动合并**。L5 = agent 开 PR 但等人批；L6 = `merge-gate.sh` 标记 eligible 后 agent 自动合并。所以同一套 hive 既能跑 L5（人批准）也能跑 L6（自动合并），切换点是"是否允许 agent 合并 merge-eligible.json 里的 PR"。

---

## Level 6 — Fully Autonomous（系统自我运行）

**论文描述**：系统对发现的问题直接行动——生成 issue、派发 agent、合并 PR、回滚失败。多 agent 作为协调的舰队在自适应治理下运行，人事后审计。**反馈环：带外部编排的多环；supervisor 协调 executor；workload governor 按实时 backlog 调节节奏；工作通过 Beads（分布式工作账本）认领以防冲突；push 通知升级需人判断的决策。**

**关键产物**逐条对照：

### 1. Agent policy files（每次 firing 重读策略，改行为不需重启）
- `examples/scanner-policy.md:13-25`（Step 0 pre-flight re-read）：明文规定每次迭代用 Read 工具重读策略文件本身——对应论文"each agent reads a markdown policy file on every firing (no restart needed to change behavior)"。
- `examples/reviewer-policy.md`、`architect-policy.md`、`outreach-policy.md` 同理。

### 2. Beads work ledger（防重复工作 + agent 记忆连续性）
- `examples/sqlite-state.md`：论文用 Beads（`bd` CLI），hive 同时提供 SQLite 备选后端。schema 在 `:30-45`，含 `fix_attempts INTEGER DEFAULT 0`（`:37`）——正是论文 §5.5 强调的 backoff 计数器。
- `examples/sqlite-state.md:5` 解释 Beads vs SQLite 选型；`:83-84` "Items that failed 3+ fix attempts (backoff candidates)" 对应论文 "3 failed attempts → status='skip'"。
- `examples/kubestellar/worker.sh:61`：worker 里同样的 `fix_attempts` schema。
- 用途对应论文两点：(a) `bd add --actor <name>` 认领工作防两 agent 撞车；(b) "agent memory continuity"——记忆活在账本里而非对话历史里，所以 compaction/重启/换 CLI/限流都不丢状态。

### 3. Governor configuration（实时调节节奏，env 文件每 tick 取）
- `bin/kick-governor.sh`：完整的自适应 workload governor。`:11-32` 四档模式表，`:82-85` 阈值，`:138-141` 成本权重。
- 配置外置：`/etc/hive/governor.env`（`:51-54` 读取）、`config/agent.env.example`、`config/backends.conf`——对应论文 "cadence rules that adapt in real time, sourced from an env file on every tick"。

### 4. Push notification infrastructure（ntfy / Slack / Discord 升级人判断）
- `bin/notify.sh:1-13`：`notify "<title>" "<body>" [priority]`，支持 `NTFY_TOPIC`、`SLACK_WEBHOOK`、`DISCORD_WEBHOOK`——精确对应论文 "ntfy, Slack, Discord for human escalation"。
- `discord/`（`discord/lib/`、`discord/package.json`）：Discord 集成实现。

### 5. Observability runbook（人如何 debug 自主行为）
- `docs/troubleshooting.md`：整篇就是论文说的 "Observability runbook — how humans debug autonomous behavior"。含 `/loop` 不触发、permission prompt 阻塞、`systemctl restart` 不重生会话（`:27` 的 footgun）、ntfy 不到等真实故障的诊断步骤。
- `docs/architecture.md`：架构说明，配合 runbook 让 strategist 理解系统。
- `dashboard/`（web 仪表盘，端口 3001）：论文称之为 "the L6 observability artifact"——`dashboard/server.js`（SSE 实时推送）、`dashboard/index.html`、`dashboard/ubersicht/hive-status.widget.jsx`（macOS Übersicht 桌面小组件）、`dashboard/agent-activity.py`（sparkline 历史）。

### 6. Merge queue / auto-merge（验证过的 PR 无人工合并）
- `bin/merge-gate.sh:5-13`：判定哪些 PR merge-eligible，写 `merge-eligible.json`；`:13` 明文 "Agents should ONLY merge PRs that appear in this file"。这是论文 "Merge queue with automated merge (verified PRs merge without manual intervention)" 的实现。
- `.github/workflows/copilot-automation.yml`、`ai-fix.yml`：CI 侧的 PR 自动化与 AI 修复触发。

### 7. Risk assessment config（高风险路径强制人审，与 AI 置信度无关）
- `examples/architect-policy.md:105` `## Blast radius (mandatory)`、`:159-168`：每个提案必须带 blast-radius 段落，"A proposal without a blast-radius section is incomplete"——对应论文 "Risk assessment configuration (high-risk paths require human review regardless of AI confidence)" 和 L6 criteria 的 "Blast radius awareness"。
- `examples/outreach-policy.md:252-298`：outreach 的 blast-radius 规则（公开内容更需要）。
- `config/restrictions/README.md`：限制配置目录。

### 8. Automated issue generation（cron 扫 TODO / 陈旧依赖 / 失败测试 / 覆盖缺口）
- `bin/ga4-anomaly-detector.sh`（生产错误→issue）、`examples/kubestellar/auto-qa-skill.md`（auto-qa 自动产 issue）、`examples/kubestellar/agents/reviewer-skills/coverage.md`（覆盖缺口→PR）。
- `bin/architecture-detector.sh`：检测架构问题。

### 9. Multi-agent orchestration with role specialization
- `README.md:Agents 表`：scanner / reviewer / architect / outreach / supervisor 五角色及各自 cadence。
- `systemd/hive@.service`（每 agent 一个 systemd 单元）、`systemd/hive.service`、`bin/agent-launch.sh`、`bin/hive.sh`（`hive supervisor` 一键启动）。

### 10. Health monitoring & self-healing（四层韧性）
- `bin/agent-healthcheck.sh:7,20,75-93`：`AGENT_MAX_RESPAWNS:-3`，连续 3 次重生失败后停止自动重生并 page 人——对应论文 §5.3 "After MAX_RESPAWNS failed attempts... 'manual intervention needed'"。
- `bin/supervisor.sh`：supervisor 每 10 秒轮询 agent 进程崩溃 / tmux 会话死亡。
- `systemd/*.timer`：定时器层。`gh-zombie-reaper.timer`（每 2 分钟清僵尸 gh 进程）、`hive-deploy.timer`（每分钟拉取部署）、`hive-snapshot.timer`（每 15 分钟发快照）。
- `bin/gh-zombie-reaper.sh`、`bin/gh-rate-check.sh`、`bin/conflict-sweeper.sh`。

### 11. Rollback drill（回滚自主变更的成文流程）
- `bin/conflict-sweeper.sh:1-12`：对 CONFLICTING 的 AI PR 自动 rebase，rebase 失败则关 PR + 重开原 issue——这是"撤销失败自主变更"的一种自动化。
- `examples/scanner-policy.md:247`：`**Revert**: remove the Step 0.5 section...` 给出关闭某能力的回滚说明。
- `examples/reviewer-policy.md:204`：定位 blame PR 后 "suggest revert or fix"。
- （成文的"rollback drill"在 hive 里偏分散，主要靠 conflict-sweeper 自动回滚 + policy 里的 revert 说明，没有单独一个 `rollback-drill.md`。这是相对论文 criteria 表里较弱的一项——**解读**。）

### 12. CLI-backend agnostic（论文强调 L6 不绑定具体 AI 工具）
- `config/backends.conf`：claude / gemini / copilot / goose 后端配置。
- `bin/hive.sh` 的 `hive switch <agent> <backend>`、`hive model <agent> <model>`：运行时切后端/模型。
- 印证论文 §6.1 "The intelligence is in the system, not the model"——模型可换，周边基础设施不可换。

### 13. Two scheduling models（论文 §5.2）
- **Model A 自调度** 与 **Model B EXECUTOR（supervisor 驱动）**：`bin/supervisor.sh` + `bin/kick-agents.sh` 用 `tmux send-keys` 发工作令实现 Model B；`launchd/com.hive.scanner.plist.example`（macOS）和 systemd timer 体现 Model A 的 cron 自调度。生产部署用 Model B（agent 在 prompt 等命令，调度可靠性移出 agent 进 OS）。

---

## 总览对照表

| Level | 论文关键产物 | hive 里的对应文件（代表） | 所在层 |
|---|---|---|---|
| 1 Assisted | 无产物（知识在脑中） | （刻意的空位；反制见 scanner-policy Step 0） | — |
| 2 Instructed | 指令文件、风格指南 | `examples/kubestellar/agents/*-CLAUDE.md`、`examples/*-policy.md`、`reviewer-skills/*.md` | examples |
| 3 Measured | 接受率日志、覆盖率、错误分类、监控面板 | `bin/ga4-anomaly-detector.sh`、`bin/fetch-coverage.sh`、`bin/issue-classifier.sh`、`reviewer-skills/coverage.md` `health-checks.md`、`dashboard/` | hive + examples |
| 4 Adaptive | 自修改配置、闭环 CI/CD、自动 triage 环 | `bin/run-pipeline.sh`、`bin/enumerate-actionable.sh`、`bin/kick-agents.sh`、`bin/kick-governor.sh`（阈值）、worktree（scanner-policy） | hive |
| 5 Semi-Automated | 代码库即操作手册、多 agent 编排、自改进环 | `examples/scanner-policy.md`、`fix-loop-skill.md`、`bin/supervisor.sh`、`bin/kick-outcome-tracker.sh`、`hive-project.yaml`（多仓） | hive + examples |
| 6 Fully Autonomous | policy 文件 + Beads 账本 + governor + push 通知 + 可观测 runbook + 合并队列 + 风险配置 | `examples/sqlite-state.md`、`bin/kick-governor.sh`、`bin/notify.sh`、`bin/merge-gate.sh`、`bin/conflict-sweeper.sh`、`bin/agent-healthcheck.sh`、`docs/troubleshooting.md`、`dashboard/`、`examples/architect-policy.md`（blast radius）、`config/backends.conf` | hive |

## 三个需要注意的边界（解读）

1. **论文点名的 `auto-qa-tuning.json` 不在 hive 仓库里**。它是 KubeStellar Console（L1–L5 案例仓库）的产物。hive 是 L6 编排引擎，里面的等价机制是 governor 的外置 env + 标签豁免（`kick-governor.sh:79`），运行模型相同（每 tick 重读、低价值类别自动屏蔽）但实现位置不同。

2. **同一个文件常常横跨多级**。`bin/kick-governor.sh` 既是 L4 的"阈值触发自动响应"，又是 L6 的"自适应 workload governance"；`examples/*-policy.md` 内容是 L2 指令但论文按 L6 "agent policy files" 归类。Level 是反馈环拓扑的属性，不是文件的属性——一个文件可以同时承担多级的环。

3. **rollback drill 是相对弱的一项**。论文 criteria 表要求"成文的回滚流程"，hive 里靠 `conflict-sweeper.sh` 自动回滚 + 各 policy 里零散的 revert 说明拼出来，没有集中的 `rollback-drill.md`。这是对照中唯一明显"论文要求 > 仓库现状"的缺口。

## 信源

- 论文：`/Users/luwei/Documents/AI/LLM/Coding/The AI Codebase Maturity Model- From Assisted Coding to Self-Sustaining Systems.pdf`（Andy Anderson, IBM Research，v2，含 Level 6 与 Hive）
- 代码库：`data/hive`（github.com/AI-LLM/hive 镜像；上游 github.com/kubestellar/hive，Apache 2.0）
