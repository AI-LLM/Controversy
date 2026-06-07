# ACMM 六个 Level 与示例代码库的逐项对照（console + hive）

把论文 *The AI Codebase Maturity Model: From Assisted Coding to Fully Autonomous Systems*（Andy Anderson, IBM Research, v2）定义的六级成熟度模型，逐 Level 落到两个示例代码库的**具体文件和具体内容**上。

## 两个仓库的分工（先分清，否则全乱）

论文用了**两个**示例代码库，它们是被管理者与管理者的关系：

- **`data/console` = KubeStellar Console**（论文 §4 的纵向案例）——一个真实的 Kubernetes 多集群管理面板（Go 后端 + React/TS 前端）。它是 **Level 1→5 的成长样本**，也是**被 hive 托管的那个代码库**。论文里 L1–L5 的全部量化指标都来自它。
- **`data/hive` = Hive**（论文 §5 的参考实现）——多智能体编排引擎。它是 **Level 6 的参考实现**，负责"运行" console 这样的项目。

所以一个 Level 的产物可能同时出现在两处：被管理项目里（console，偏 L1–L5）和编排引擎里（hive，偏 L4–L6）。下面每个 Level 我都先给 console 的实证，再给 hive 的实证。事实陈述给 `路径:行号`，判断性对应标注为解读。

一个关键自指事实：console 仓库里有 `.github/workflows/acmm-level-monitor.yml`，**这个代码库每天自动检测自己的 ACMM level**（默认要求 ≥ L5，`acmm-level-monitor.yml:11`），低于阈值就开 issue。论文的模型被它的案例代码库当成了 CI 门禁。

---

## Level 1 — Assisted（提示与审查）

**论文描述**：人发起每次交互，AI 是高级自动补全，会话间无持久上下文。**关键产物：除代码本身外没有任何产物**——偏好/模式/架构决策都只在开发者脑中。

**对应文件**：按定义 **L1 在代码库里留不下专属文件**——它的证据是缺席。在 console 的 git 早期历史里能看到这个阶段，但成熟后的仓库里它已被 L2 的指令文件完全取代。hive 侧把"不要靠上下文记忆"写成硬规则（`data/hive/examples/scanner-policy.md:13-25`），正是对 L1 缺陷的反制。

**判断（解读）**：L1 不是一个文件，是一个被填补掉的空位。

---

## Level 2 — Instructed（编码化的偏好）

**论文描述**：偏好、约定、架构决策写进文件，AI 每次会话开始时读取。典型实践：`CLAUDE.md`、`.github/copilot-instructions.md`、PR 模板、卡片/组件开发指南。**关键产物：指令文件、风格指南、卡片/组件开发指南**——论文原话："a single card development guide encoded approximately 90% of the reasons I had been rejecting AI-generated PRs"。

**console 的对应文件（L2 主场，且能逐句对上论文）**：

- **`data/console/.github/CARD_DEVELOPMENT_GUIDE.md`** —— 这就是论文点名的那份"card development guide"。文件第 4 行原话：`Following this guide will prevent 90% of the review feedback we give on card PRs`，与论文的 "90%" 数字**逐字吻合**。`:11-27` 的 "Common Rejection Reasons" 表把每条人工拒绝理由（demo data、magic numbers、hardcoded strings、scope creep、nil slices、缺测试、PR 标题缺 emoji…）编码成规则——L2 的标准定义。
- **`data/console/CLAUDE.md`**（26 KB，17 个章节，`:1` "KubeStellar Console — Agent Guide"）：主指令文件。含 `:49` MANDATORY Testing Requirements、`:153` Card Development Rules、`:214` Critical Rules、`:480` Go Backend Patterns、`:598` i18n——把架构决策固化成 AI 每次读取的规则。
- **`data/console/.github/copilot-instructions.md`** —— 论文点名的另一份。`:3-18` 把"每次 commit 前必须 build + lint，失败就修"写成不可协商的硬规则。
- **`data/console/AGENTS.md`**、**`data/console/.github/pull_request_template.md`**：补充指令与 AI-可读的 PR 模板。
- **`data/console/.github/agents/*.agent.md`**（12 个角色定义）：`issue-scanner.agent.md`、`tdd.agent.md`、`rca.agent.md`、`perf-test.agent.md`、`ui-compliance-test.agent.md` 等，每个是一个 agent 的 frontmatter + 指令（如 `issue-scanner.agent.md:2` 描述"监控 4 仓、每 15 分钟"）。

**hive 的对应文件**：按角色分文件的指令矩阵——`data/hive/examples/kubestellar/agents/*-CLAUDE.md`（11 个）、`data/hive/examples/*-policy.md`（4 个）、`reviewer-skills/*.md` 等。

**判断（解读）**：论文 §6.2 "questions produce instructions as a side effect" 的物化结果，在 console 就是 CARD_DEVELOPMENT_GUIDE + CLAUDE.md，在 hive 就是那堆 policy/CLAUDE 文件。

---

## Level 3 — Measured（反馈变得可见）

**论文描述**：系统产出关于 AI 表现的**量化信号**——接受率、覆盖率、错误率、用户反馈被系统化追踪。典型实践：按类别追踪 PR 接受率、每个 PR 上的覆盖率门禁、夜间测试套件、GA4 错误监控、NPS。**关键产物：接受率日志（如 `auto-qa-tuning.json`）、覆盖率报告、监控面板、错误分类系统**。"Testing 是整个旅程里最重要的单项投资。"

**console 的对应文件（这里能找到论文点名的全部实物）**：

- **`data/console/.github/auto-qa-tuning.json`** —— 论文反复点名的那个文件，真身在此。`:5` `rolling_window_days: 30`；`categories` 段按 8 个类别（performance/security/a11y/operator/sre/features/resilience/consistency）记 `merged`/`closed`/`acceptance_rate`/`status`（`:6-62`）。这就是"接受率日志"。

- **测试体量（论文称为第一投资）**：
  - 前端测试 **1904** 个 `*.test.ts(x)` 文件、Go 测试 **357** 个 `*_test.go`、Playwright E2E **123** 个 `*.spec.ts`。这是论文"the sheer volume of test cases"的实测落地。

- **覆盖率门禁与报告**：
  - `data/console/.github/workflows/coverage-gate.yml:26` `COVERAGE_THRESHOLD: 91` —— 与论文 Table 3 "Code coverage 91%" **吻合**。每个 PR 上跑（`:8-12`，限 `web/src/**`）。
  - `coverage-hourly.yml`（全量小时级）、`coverage-weekly-review.yml`（周复盘）、`test-coverage-check.yml`。
  - `scripts/check-test-coverage.sh`、`scripts/check-go-coverage-ratchet.sh`。

- **错误监控（GA4，对应论文 §6.4 "telemetry as the nervous system"）**：
  - `data/console/.github/workflows/ga4-error-monitor.yml:2-3`：`Queries GA4 for recent ksc_error events and creates GitHub issues`——论文 §6.4 点名的 `ksc_error` 自定义事件就在这里。每小时跑（`:13`），错误数超阈值就开 issue 让 Copilot 修。
  - `ga4-error-regression.yml`、`ga4-mobile-monitor.yml`、`netlify-error-reporter.yml`。

- **夜间测试套件（论文 Table 3 "32 nightly test suites"）**：
  - `nightly-test-suite.yml`、`card-standard-nightly.yml`、`nightly-compliance.yml`、`nightly-dashboard-health.yml`、`nightly-dast.yml`、`nightly-ux-journeys.yml`、`playwright-nightly.yml` 等——合规/性能/安全/可访问性各一套，正是论文"compliance, performance, security, accessibility"的分层。

- **错误分类 / 防回归基线（把"什么算退步"量化成数字）**：
  - `data/console/.github/go-coverage-ratchet.txt`（内容 `52.0`，Go 覆盖率棘轮下限）、`ai-magic-numbers-baseline.txt`（`7`）、`ai-non-localized-baseline.txt`（`272`）、`ai-noop-assertions-baseline.txt`、`ai-hardcoded-routes-baseline.txt`、`array-safety-baseline.txt`、`nilaway-baseline.json`、`kb-nightly-validation-baseline.json`——每个是一类 AI 易犯错误的当前计数，CI 不许超过它。

- **DORA 式度量**：
  - `mttr-badge.yml`（每小时算 MTTR 徽章，`:5`）——对应论文 §2.1 引用的 DORA "mean time to restore"。

**hive 的对应文件**：`bin/ga4-anomaly-detector.sh`（7 天基线对比）、`bin/fetch-coverage.sh`、`bin/issue-classifier.sh`、`dashboard/`。

**判断（解读）**：论文说 L3 突破在 Testing 的"volume + coverage + determinism"。console 用 1904+357+123 个测试给了 volume，用 coverage-gate 的 91% 给了 coverage，用一堆 `*-baseline.txt` 棘轮给了 determinism（防 flaky / 防回归）。

---

## Level 4 — Adaptive（反馈环自我闭合）

**论文描述**：系统对自己的度量采取行动，阈值触发自动响应，人的监督从执行转向治理。典型实践：基于 PR 接受率自调权重、自动 issue triage 环、隔夜自动修 bug、worktree 并发。**关键产物：自修改配置文件（如 `auto-qa-tuning.json`，接受率低于 20% 的类别自动屏蔽）、闭环 CI/CD 流水线**。

**console 的对应文件（论文 §4.4 Case E 的实证在这里）**：

- **`data/console/.github/workflows/auto-qa-tuner.yml`** —— 写回 auto-qa-tuning.json 的那只手，把它变成"自修改配置"。三条反馈环（`:4-7`）：daily-feedback / weekly-analysis / cncf-intelligence。关键阈值 `:30-32`：`BLOCKED_THRESHOLD: 20`、`BOOSTED_THRESHOLD: 80`、`MIN_SAMPLES: 10`——**`BLOCKED_THRESHOLD: 20` 与论文 "acceptance rates below 20% are automatically blocked" 逐字吻合**。

- **论文 §4.4 Case E 的历史证据**（"operator 类别 129 closed vs 11 merged，8% 接受率，系统自动把权重设 0"）：
  - 翻 `auto-qa-tuning.json` 的 `history[]`：`2026-04-05` 到 `2026-05-09` 连续多天 `categories_blocked: ["operator", "sre"]`（如 `:131-145`），`2026-05-20` 起恢复为空。**这就是 Case E 描述的自动屏蔽事件留在配置文件里的痕迹**。
  - 当前 `rotation_weights`（文件末尾）：security 0.78、resilience 0.77 偏低，sre 1.08、a11y 1.01 偏高——系统按接受率动态调过的权重，正是论文 L4 "self-tuning rotation weights"。

- **隔夜自动修 / 自动测试生成**：
  - `auto-qa.yml`（自动产 QA issue）、`auto-test-gen.yml`（自动生成测试）、`ai-fix.yml`（标签触发 AI 修复）。

- **闭环 CI/CD 与 86 个 workflow**：
  - `data/console/.github/workflows/` 下 **86 个 `.yml`**（论文 v1 时记 74 个，含 22 个 AI 专用；现已增长）。`build-deploy.yml`、`post-merge-verify.yml`、`pr-closed-verification.yml` 构成"合并→部署→验证"闭环。

**hive 的对应文件**：`bin/run-pipeline.sh`（enumerator→classifier→gate→monitor 闭环）、`bin/kick-governor.sh`（SURGE/BUSY/QUIET/IDLE 阈值触发自动响应）、worktree 并发（`scanner-policy.md:32`）。

**判断（解读）**：L4 的标志性产物 `auto-qa-tuning.json` 在 console（被写回），其调速器在 hive（governor）。两边是同一思想的两种实现：把"人实时调权重"换成"代码按阈值自动调"。

---

## Level 5 — Semi-Automated（系统提议，人批准）

**论文描述**：系统检测问题并提议修复，无需人发起；但人仍批准——系统提议，不自主合并。典型实践：社区驱动的 issue→实现流水线（bug 30 分钟、feature 60 分钟）、多 agent 跨仓编排、自改进环。**关键产物：整个代码库即 AI 的操作手册**——每个测试是信任约束，每个 workflow 是策略，每个度量阈值是优先级决策。

**console 的对应文件**：

- **机器可执行的策略（"每个 workflow 是策略"的物化）**：
  - `data/console/.github/policies/merge-policy.yaml`：把 PR 接受规则写成 machine-enforceable rules——`dco-required`、`adopters-human-approval`（`auto_merge: false`，`:11`）、`no-direct-main`、`ci-gate`（required_checks build+lint，`:24`）。
  - `data/console/.github/policies/ai-boundaries.yaml`：`deny_write`（deploy/、migrations/、workflows、.env）、`require_review`（后端 API surface）、`auto_merge_eligible`（作者白名单 + max_files 10 + 排除 ADOPTERS）——这是"每个度量阈值是优先级决策"的配置形态。

- **代理化工作流（agentic workflows，系统自己提议并执行）**：
  - `data/console/.github/aw/`（`github-agentic-workflows.md`、`config.yml`、`actions-lock.json`、`schemas/`）：gh-aw 框架。
  - `auto-triage.md`（Copilot 被指派即自动加 `triage/accepted` 标签）、`implement-fix.md`（triage 后把 issue 派给 Copilot 实现，`:1-2`）、`stuck-detection.md`（每 30 分钟检测卡住的工作流并尝试自动恢复，`:3-4`）——issue→triage→实现的提议流水线，对应论文 "community-driven issue-to-implementation pipelines"。

- **自指的成熟度反馈环（system analyzes itself）**：
  - `acmm-level-monitor.yml`（每天检测自身 ACMM level）+ `accm-history-update.yml`（更新历史）——代码库分析自己的成熟度并据此开 issue，是"self-improvement cycles" 的极端形态。

**hive 的对应文件**：`examples/scanner-policy.md`（整篇即"代码库操作手册"）、`fix-loop-skill.md`、`bin/supervisor.sh`、`bin/kick-outcome-tracker.sh`、多仓配置 `hive-project.yaml`。

**判断（解读）**：L5↔L6 的唯一分界是"提议 vs 自动合并"。在 console 里这条线就写在 `ai-boundaries.yaml` 的 `auto_merge_eligible` 和 `merge-policy.yaml` 的 `auto_merge: false`——谁能自动合、谁必须人批，是配置项。console 自身停在 L5（人批关键合并），由 hive 把它推到 L6（自动合并 merge-eligible 的 PR）。

---

## Level 6 — Fully Autonomous（系统自我运行）

**论文描述**：系统对发现的问题直接行动——生成 issue、派发 agent、合并 PR、回滚失败。多 agent 作为协调舰队在自适应治理下运行，人事后审计。反馈环：带外部编排的多环；supervisor 协调 executor；workload governor 按实时 backlog 调节；工作经 Beads 账本认领防冲突；push 通知升级需人判断的决策。

L6 的产物**主体在 hive**（参考实现）。console 侧只留两个把自己接到 hive 的接口：`data/console/.github/workflows/hive-interactive.yml`、`hive-trust-gate.yml`。以下逐条对照 hive：

### 1. Agent policy files（每次 firing 重读，改行为不重启）
- `data/hive/examples/scanner-policy.md:13-25`（Step 0 强制重读策略文件），`reviewer/architect/outreach-policy.md` 同理。

### 2. Beads work ledger（防重复 + agent 记忆连续性）
- `data/hive/examples/sqlite-state.md`：Beads（`bd` CLI）与 SQLite 双后端。schema `:30-45` 含 `fix_attempts INTEGER DEFAULT 0`（`:37`，论文 §5.5 的 backoff 计数器）；`:83-84` "failed 3+ attempts → backoff"。`worker.sh:61` 同 schema。

### 3. Governor configuration（实时调速，env 每 tick 取）
- `data/hive/bin/kick-governor.sh`：四档模式表 `:11-32`、阈值 `:82-85`、成本权重 `:138-141`，全部从 `/etc/hive/governor.env` 每 tick 读取（`:51-54`）。

### 4. Push notification infrastructure（ntfy/Slack/Discord 升级）
- `data/hive/bin/notify.sh:1-13`（三通道）、`data/hive/discord/`。

### 5. Observability runbook（人如何 debug 自主行为）
- `data/hive/docs/troubleshooting.md`（整篇 = 论文的 observability runbook，含 `:27` 的 `systemctl restart` 不重生会话 footgun）、`docs/architecture.md`。
- `data/hive/dashboard/`（论文称之为 "L6 observability artifact"）：`server.js`（SSE 实时）、`ubersicht/hive-status.widget.jsx`（macOS 桌面组件）、`agent-activity.py`（sparkline）。

### 6. Merge queue / auto-merge（验证过的 PR 无人合并）
- `data/hive/bin/merge-gate.sh:5-13`：判定 merge-eligible 写 JSON，`:13` "Agents should ONLY merge PRs that appear in this file"。
- console 侧：`copilot-automation.yml`、`ai-fix.yml`。

### 7. Risk assessment config（高风险路径强制人审，与 AI 置信度无关）
- console：`ai-boundaries.yaml` 的 `deny_write` / `require_review`（最精确的"风险配置"实物）。
- hive：`examples/architect-policy.md:105,159-168` 强制每个提案带 blast-radius 段落；`config/restrictions/`。

### 8. Automated issue generation（cron 扫 TODO/陈旧依赖/失败测试/覆盖缺口）
- console：`ga4-error-monitor.yml`、`auto-qa.yml`、`auto-test-gen.yml`、`acmm-level-monitor.yml` 都会自动开 issue。
- hive：`bin/ga4-anomaly-detector.sh`、`bin/architecture-detector.sh`。

### 9. Multi-agent orchestration with role specialization
- hive：`README.md` 的 5 角色表（scanner/reviewer/architect/outreach/supervisor）、`systemd/hive@.service`（每 agent 一个单元）、`bin/agent-launch.sh`、`bin/hive.sh`。

### 10. Health monitoring & self-healing（四层韧性）
- `data/hive/bin/agent-healthcheck.sh:20,75-93`：`AGENT_MAX_RESPAWNS:-3`，3 次重生失败即停并 page 人（论文 §5.3）。
- `bin/supervisor.sh`（10 秒轮询）、`systemd/*.timer`（gh-zombie-reaper 每 2 分钟等）、`bin/conflict-sweeper.sh`。

### 11. Rollback drill（回滚自主变更的成文流程）
- hive：`bin/conflict-sweeper.sh:1-12`（CONFLICTING PR 自动 rebase，失败则关 PR + 重开 issue）、`scanner-policy.md:247` revert 说明、`reviewer-policy.md:204` "suggest revert"。
- console：`post-merge-verify.yml` / `pr-closed-verification.yml`（合并后验证，失败可触发回滚）。

### 12. CLI-backend agnostic（不绑定具体 AI 工具）
- `data/hive/config/backends.conf`（claude/gemini/copilot/goose）、`hive switch`/`hive model` 运行时切换。印证论文 §6.1 "intelligence is in the system, not the model"。

### 13. Two scheduling models（Model A 自调度 / Model B EXECUTOR）
- `bin/supervisor.sh` + `bin/kick-agents.sh`（tmux send-keys 发工作令 = Model B）；`launchd/com.hive.scanner.plist.example` + systemd timer（Model A）。生产用 Model B。

---

## 总览对照表

| Level | 论文关键产物 | console（被管理项目，L1–L5 主场） | hive（编排引擎，L4–L6 主场） |
|---|---|---|---|
| 1 Assisted | 无产物 | 刻意的空位（早期 git 史） | scanner-policy Step 0 反制 |
| 2 Instructed | 指令文件、卡片开发指南 | `CLAUDE.md`、`.github/CARD_DEVELOPMENT_GUIDE.md`（"90%" 原话）、`.github/copilot-instructions.md`、`.github/agents/*.agent.md` | `examples/.../​*-CLAUDE.md`、`examples/*-policy.md` |
| 3 Measured | 接受率日志、覆盖率、GA4、错误分类、夜间测试 | `.github/auto-qa-tuning.json`、`coverage-gate.yml`(91%)、`ga4-error-monitor.yml`(ksc_error)、`nightly-*.yml`、`*-baseline.txt` 棘轮、1904+357+123 个测试、`mttr-badge.yml` | `ga4-anomaly-detector.sh`、`fetch-coverage.sh`、`issue-classifier.sh`、`dashboard/` |
| 4 Adaptive | 自修改配置(<20% 屏蔽)、闭环 CI/CD | `auto-qa-tuner.yml`(BLOCKED_THRESHOLD:20)、`auto-qa-tuning.json` 的 `history` 里 operator/sre 实际被屏蔽、`rotation_weights`、86 个 workflow | `run-pipeline.sh`、`kick-governor.sh`、worktree |
| 5 Semi-Automated | 代码库即操作手册、多 agent 编排、机器可执行策略 | `.github/policies/merge-policy.yaml`、`ai-boundaries.yaml`、`.github/aw/`、`auto-triage.md`/`implement-fix.md`/`stuck-detection.md`、`acmm-level-monitor.yml` | `scanner-policy.md`、`supervisor.sh`、`kick-outcome-tracker.sh` |
| 6 Fully Autonomous | policy + Beads + governor + push + runbook + 合并队列 + 风险配置 | `hive-interactive.yml`、`hive-trust-gate.yml`（接入 hive） | `sqlite-state.md`、`kick-governor.sh`、`notify.sh`、`merge-gate.sh`、`conflict-sweeper.sh`、`agent-healthcheck.sh`、`docs/troubleshooting.md`、`dashboard/`、`architect-policy.md` blast radius、`backends.conf` |

## 几条需要注意的边界（解读）

1. **两个仓库是被管理者 / 管理者关系**，不是两个独立案例。console = L1→L5 一路成长起来的真实项目，hive = 把它（和另外几个仓库）推到 L6 的引擎。论文的 L1–L5 量化数据全来自 console，L6 参考实现是 hive。

2. **论文点名的 `auto-qa-tuning.json` 实物在 console，不在 hive**。第一版分析里这是个悬而未决的缺口，现已坐实：文件在 `data/console/.github/auto-qa-tuning.json`，其写回手是 `auto-qa-tuner.yml`（`BLOCKED_THRESHOLD: 20`），其 `history[]` 里 2026-04-05 起 operator/sre 被自动屏蔽的记录，正是论文 §4.4 Case E 的原始证据。

3. **同一文件常横跨多级**。`auto-qa-tuning.json` 是 L3（接受率日志）也是 L4（被自动写回的自修改配置）；`kick-governor.sh` 是 L4（阈值响应）也是 L6（自适应治理）。Level 是反馈环拓扑的属性，不是文件的属性。

4. **代码库给模型当了 CI 门禁**。`acmm-level-monitor.yml` 让 console 每天检测自己的 ACMM level 并要求 ≥ L5——论文的成熟度模型被它的案例代码库内化成了自动化质量门。

## 信源

- 论文：`/Users/luwei/Documents/AI/LLM/Coding/The AI Codebase Maturity Model- From Assisted Coding to Self-Sustaining Systems.pdf`（Andy Anderson, IBM Research，v2，含 Level 6 与 Hive）
- 被管理项目：`data/console`（KubeStellar Console；上游 github.com/kubestellar/console）
- 编排引擎：`data/hive`（上游 github.com/kubestellar/hive，Apache 2.0）
