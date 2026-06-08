# ACMM 六个 Level 与示例代码库的逐项对照（console + hive）

把论文 *The AI Codebase Maturity Model: From Assisted Coding to Fully Autonomous Systems*（Andy Anderson, IBM Research, v2）定义的六级成熟度模型，逐 Level 落到两个示例代码库的**具体文件和具体内容**上。文件名与行号均链接到 GitHub（`hive` → `AI-LLM/hive`，`console` → `AI-LLM/console`）。

## 两个仓库的分工（先分清，否则全乱）

论文用了**两个**示例代码库，它们是被管理者与管理者的关系：

- **console = KubeStellar Console**（论文 §4 的纵向案例）——一个真实的 Kubernetes 多集群管理面板（Go 后端 + React/TS 前端）。它是 **Level 1→5 的成长样本**，也是**被 hive 托管的那个代码库**。论文里 L1–L5 的全部量化指标都来自它。
- **hive = Hive**（论文 §5 的参考实现）——多智能体编排引擎。它是 **Level 6 的参考实现**，负责"运行" console 这样的项目。

所以一个 Level 的产物可能同时出现在两处：被管理项目里（console，偏 L1–L5）和编排引擎里（hive，偏 L4–L6）。下面每个 Level 我都先给 console 的实证，再给 hive 的实证。事实陈述给文件+行号链接，判断性对应标注为解读。

一个关键自指事实：console 仓库里有 [.github/workflows/acmm-level-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/acmm-level-monitor.yml)，**这个代码库每天自动检测自己的 ACMM level**（默认要求 ≥ L5，[:11](https://github.com/AI-LLM/console/blob/main/.github/workflows/acmm-level-monitor.yml#L11)），低于阈值就开 issue。论文的模型被它的案例代码库当成了 CI 门禁。

---

## Level 1 — Assisted（提示与审查）

**论文描述**：人发起每次交互，AI 是高级自动补全，会话间无持久上下文。**关键产物：除代码本身外没有任何产物**——偏好/模式/架构决策都只在开发者脑中。

**对应文件**：按定义 **L1 在代码库里留不下专属文件**——它的证据是缺席。在 console 的 git 早期历史里能看到这个阶段，但成熟后的仓库里它已被 L2 的指令文件完全取代。hive 侧把"不要靠上下文记忆"写成硬规则（[examples/scanner-policy.md:13-25](https://github.com/AI-LLM/hive/blob/main/examples/scanner-policy.md#L13-L25)），正是对 L1 缺陷的反制。

**判断（解读）**：L1 不是一个文件，是一个被填补掉的空位。

---

## Level 2 — Instructed（编码化的偏好）

**论文描述**：偏好、约定、架构决策写进文件，AI 每次会话开始时读取。典型实践：`CLAUDE.md`、`.github/copilot-instructions.md`、PR 模板、卡片/组件开发指南。**关键产物：指令文件、风格指南、卡片/组件开发指南**——论文原话："a single card development guide encoded approximately 90% of the reasons I had been rejecting AI-generated PRs"。

**console 的对应文件（L2 主场，且能逐句对上论文）**：

- **[.github/CARD_DEVELOPMENT_GUIDE.md](https://github.com/AI-LLM/console/blob/main/.github/CARD_DEVELOPMENT_GUIDE.md)** —— 这就是论文点名的那份"card development guide"。文件 [:4](https://github.com/AI-LLM/console/blob/main/.github/CARD_DEVELOPMENT_GUIDE.md#L4) 原话：`Following this guide will prevent 90% of the review feedback we give on card PRs`，与论文的 "90%" 数字**逐字吻合**。[:11-27](https://github.com/AI-LLM/console/blob/main/.github/CARD_DEVELOPMENT_GUIDE.md#L11-L27) 的 "Common Rejection Reasons" 表把每条人工拒绝理由（demo data、magic numbers、hardcoded strings、scope creep、nil slices、缺测试、PR 标题缺 emoji…）编码成规则——L2 的标准定义。
- **[CLAUDE.md](https://github.com/AI-LLM/console/blob/main/CLAUDE.md)**（26 KB，17 个章节，[:1](https://github.com/AI-LLM/console/blob/main/CLAUDE.md#L1) "KubeStellar Console — Agent Guide"）：主指令文件。含 [:49](https://github.com/AI-LLM/console/blob/main/CLAUDE.md#L49) MANDATORY Testing Requirements、[:153](https://github.com/AI-LLM/console/blob/main/CLAUDE.md#L153) Card Development Rules、[:214](https://github.com/AI-LLM/console/blob/main/CLAUDE.md#L214) Critical Rules、[:480](https://github.com/AI-LLM/console/blob/main/CLAUDE.md#L480) Go Backend Patterns、[:598](https://github.com/AI-LLM/console/blob/main/CLAUDE.md#L598) i18n——把架构决策固化成 AI 每次读取的规则。
- **[.github/copilot-instructions.md](https://github.com/AI-LLM/console/blob/main/.github/copilot-instructions.md)** —— 论文点名的另一份。[:3-18](https://github.com/AI-LLM/console/blob/main/.github/copilot-instructions.md#L3-L18) 把"每次 commit 前必须 build + lint，失败就修"写成不可协商的硬规则。
- **[AGENTS.md](https://github.com/AI-LLM/console/blob/main/AGENTS.md)**、**[.github/pull_request_template.md](https://github.com/AI-LLM/console/blob/main/.github/pull_request_template.md)**：补充指令与 AI-可读的 PR 模板。
- **[.github/agents/](https://github.com/AI-LLM/console/tree/main/.github/agents)**（12 个角色定义 `*.agent.md`）：[issue-scanner.agent.md](https://github.com/AI-LLM/console/blob/main/.github/agents/issue-scanner.agent.md)、[tdd.agent.md](https://github.com/AI-LLM/console/blob/main/.github/agents/tdd.agent.md)、[rca.agent.md](https://github.com/AI-LLM/console/blob/main/.github/agents/rca.agent.md)、[perf-test.agent.md](https://github.com/AI-LLM/console/blob/main/.github/agents/perf-test.agent.md)、[ui-compliance-test.agent.md](https://github.com/AI-LLM/console/blob/main/.github/agents/ui-compliance-test.agent.md) 等，每个是一个 agent 的 frontmatter + 指令（如 [issue-scanner.agent.md:2](https://github.com/AI-LLM/console/blob/main/.github/agents/issue-scanner.agent.md#L2) 描述"监控 4 仓、每 15 分钟"）。

**hive 的对应文件**：按角色分文件的指令矩阵——[examples/kubestellar/agents/](https://github.com/AI-LLM/hive/tree/main/examples/kubestellar/agents)（11 个 `*-CLAUDE.md`）、[examples/](https://github.com/AI-LLM/hive/tree/main/examples)（4 个 `*-policy.md`）、[examples/kubestellar/agents/reviewer-skills/](https://github.com/AI-LLM/hive/tree/main/examples/kubestellar/agents/reviewer-skills) 等。

**判断（解读）**：论文 §6.2 "questions produce instructions as a side effect" 的物化结果，在 console 就是 CARD_DEVELOPMENT_GUIDE + CLAUDE.md，在 hive 就是那堆 policy/CLAUDE 文件。

---

## Level 3 — Measured（反馈变得可见）

**论文描述**：系统产出关于 AI 表现的**量化信号**——接受率、覆盖率、错误率、用户反馈被系统化追踪。典型实践：按类别追踪 PR 接受率、每个 PR 上的覆盖率门禁、夜间测试套件、GA4 错误监控、NPS。**关键产物：接受率日志（如 `auto-qa-tuning.json`）、覆盖率报告、监控面板、错误分类系统**。"Testing 是整个旅程里最重要的单项投资。"

**console 的对应文件（这里能找到论文点名的全部实物）**：

- **[.github/auto-qa-tuning.json](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json)** —— 论文反复点名的那个文件，真身在此。[:5](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json#L5) `rolling_window_days: 30`；`categories` 段按 8 个类别（performance/security/a11y/operator/sre/features/resilience/consistency）记 `merged`/`closed`/`acceptance_rate`/`status`（[:6-62](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json#L6-L62)）。这就是"接受率日志"。

- **测试体量（论文称为第一投资）**：前端测试 **1904** 个 `*.test.ts(x)` 文件、Go 测试 **357** 个 `*_test.go`、Playwright E2E **123** 个 `*.spec.ts`。这是论文"the sheer volume of test cases"的实测落地。

- **覆盖率门禁与报告**：
  - [.github/workflows/coverage-gate.yml:26](https://github.com/AI-LLM/console/blob/main/.github/workflows/coverage-gate.yml#L26) `COVERAGE_THRESHOLD: 91` —— 与论文 Table 3 "Code coverage 91%" **吻合**。每个 PR 上跑（[:8-12](https://github.com/AI-LLM/console/blob/main/.github/workflows/coverage-gate.yml#L8-L12)，限 `web/src/**`）。
  - [.github/workflows/coverage-hourly.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/coverage-hourly.yml)（全量小时级）、[.github/workflows/coverage-weekly-review.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/coverage-weekly-review.yml)（周复盘）、[.github/workflows/test-coverage-check.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/test-coverage-check.yml)。
  - [scripts/check-test-coverage.sh](https://github.com/AI-LLM/console/blob/main/scripts/check-test-coverage.sh)、[scripts/check-go-coverage-ratchet.sh](https://github.com/AI-LLM/console/blob/main/scripts/check-go-coverage-ratchet.sh)。

- **错误监控（GA4，对应论文 §6.4 "telemetry as the nervous system"）**：
  - [.github/workflows/ga4-error-monitor.yml:2-3](https://github.com/AI-LLM/console/blob/main/.github/workflows/ga4-error-monitor.yml#L2-L3)：`Queries GA4 for recent ksc_error events and creates GitHub issues`——论文 §6.4 点名的 `ksc_error` 自定义事件就在这里。每小时跑（[:13](https://github.com/AI-LLM/console/blob/main/.github/workflows/ga4-error-monitor.yml#L13)），错误数超阈值就开 issue 让 Copilot 修。
  - [.github/workflows/ga4-error-regression.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/ga4-error-regression.yml)、[.github/workflows/ga4-mobile-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/ga4-mobile-monitor.yml)、[.github/workflows/netlify-error-reporter.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/netlify-error-reporter.yml)。

- **夜间测试套件（论文 Table 3 "32 nightly test suites"）**：[.github/workflows/nightly-test-suite.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/nightly-test-suite.yml)、[card-standard-nightly.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/card-standard-nightly.yml)、[nightly-compliance.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/nightly-compliance.yml)、[nightly-dashboard-health.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/nightly-dashboard-health.yml)、[nightly-dast.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/nightly-dast.yml)、[nightly-ux-journeys.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/nightly-ux-journeys.yml)、[playwright-nightly.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/playwright-nightly.yml) 等——合规/性能/安全/可访问性各一套，正是论文"compliance, performance, security, accessibility"的分层。

- **错误分类 / 防回归基线（把"什么算退步"量化成数字）**：[.github/go-coverage-ratchet.txt](https://github.com/AI-LLM/console/blob/main/.github/go-coverage-ratchet.txt)（内容 `52.0`，Go 覆盖率棘轮下限）、[.github/ai-magic-numbers-baseline.txt](https://github.com/AI-LLM/console/blob/main/.github/ai-magic-numbers-baseline.txt)（`7`）、[.github/ai-non-localized-baseline.txt](https://github.com/AI-LLM/console/blob/main/.github/ai-non-localized-baseline.txt)（`272`）、[.github/ai-noop-assertions-baseline.txt](https://github.com/AI-LLM/console/blob/main/.github/ai-noop-assertions-baseline.txt)、[.github/ai-hardcoded-routes-baseline.txt](https://github.com/AI-LLM/console/blob/main/.github/ai-hardcoded-routes-baseline.txt)、[.github/array-safety-baseline.txt](https://github.com/AI-LLM/console/blob/main/.github/array-safety-baseline.txt)、[.github/nilaway-baseline.json](https://github.com/AI-LLM/console/blob/main/.github/nilaway-baseline.json)、[.github/kb-nightly-validation-baseline.json](https://github.com/AI-LLM/console/blob/main/.github/kb-nightly-validation-baseline.json)——每个是一类 AI 易犯错误的当前计数，CI 不许超过它。

- **DORA 式度量**：[.github/workflows/mttr-badge.yml:5](https://github.com/AI-LLM/console/blob/main/.github/workflows/mttr-badge.yml#L5)（每小时算 MTTR 徽章）——对应论文 §2.1 引用的 DORA "mean time to restore"。

**hive 的对应文件**：[bin/ga4-anomaly-detector.sh](https://github.com/AI-LLM/hive/blob/main/bin/ga4-anomaly-detector.sh)（7 天基线对比）、[bin/fetch-coverage.sh](https://github.com/AI-LLM/hive/blob/main/bin/fetch-coverage.sh)、[bin/issue-classifier.sh](https://github.com/AI-LLM/hive/blob/main/bin/issue-classifier.sh)、[dashboard/](https://github.com/AI-LLM/hive/tree/main/dashboard)。

**判断（解读）**：论文说 L3 突破在 Testing 的"volume + coverage + determinism"。console 用 1904+357+123 个测试给了 volume，用 coverage-gate 的 91% 给了 coverage，用一堆 `*-baseline.txt` 棘轮给了 determinism（防 flaky / 防回归）。

---

## Level 4 — Adaptive（反馈环自我闭合）

**论文描述**：系统对自己的度量采取行动，阈值触发自动响应，人的监督从执行转向治理。典型实践：基于 PR 接受率自调权重、自动 issue triage 环、隔夜自动修 bug、worktree 并发。**关键产物：自修改配置文件（如 `auto-qa-tuning.json`，接受率低于 20% 的类别自动屏蔽）、闭环 CI/CD 流水线**。

**console 的对应文件（论文 §4.4 Case E 的实证在这里）**：

- **[.github/workflows/auto-qa-tuner.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-qa-tuner.yml)** —— 写回 auto-qa-tuning.json 的那只手，把它变成"自修改配置"。三条反馈环（[:4-7](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-qa-tuner.yml#L4-L7)）：daily-feedback / weekly-analysis / cncf-intelligence。关键阈值 [:30-32](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-qa-tuner.yml#L30-L32)：`BLOCKED_THRESHOLD: 20`、`BOOSTED_THRESHOLD: 80`、`MIN_SAMPLES: 10`——**`BLOCKED_THRESHOLD: 20` 与论文 "acceptance rates below 20% are automatically blocked" 逐字吻合**。

- **论文 §4.4 Case E 的历史证据**（"operator 类别 129 closed vs 11 merged，8% 接受率，系统自动把权重设 0"）：
  - 翻 [.github/auto-qa-tuning.json](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json) 的 `history[]`：`2026-04-05` 到 `2026-05-09` 连续多天 `categories_blocked: ["operator", "sre"]`（如 [:131-145](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json#L131-L145)），`2026-05-20` 起恢复为空。**这就是 Case E 描述的自动屏蔽事件留在配置文件里的痕迹**。
  - 当前 `rotation_weights`（文件末尾）：security 0.78、resilience 0.77 偏低，sre 1.08、a11y 1.01 偏高——系统按接受率动态调过的权重，正是论文 L4 "self-tuning rotation weights"。

- **隔夜自动修 / 自动测试生成**：[.github/workflows/auto-qa.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-qa.yml)（自动产 QA issue）、[.github/workflows/auto-test-gen.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-test-gen.yml)（自动生成测试）、[.github/workflows/ai-fix.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/ai-fix.yml)（标签触发 AI 修复）。

- **闭环 CI/CD 与 86 个 workflow**：[.github/workflows/](https://github.com/AI-LLM/console/tree/main/.github/workflows) 下 **86 个 `.yml`**（论文 v1 时记 74 个，含 22 个 AI 专用；现已增长）。[build-deploy.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/build-deploy.yml)、[post-merge-verify.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/post-merge-verify.yml)、[pr-closed-verification.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/pr-closed-verification.yml) 构成"合并→部署→验证"闭环。

**hive 的对应文件**：[bin/run-pipeline.sh](https://github.com/AI-LLM/hive/blob/main/bin/run-pipeline.sh)（enumerator→classifier→gate→monitor 闭环）、[bin/kick-governor.sh](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh)（SURGE/BUSY/QUIET/IDLE 阈值触发自动响应）、worktree 并发（[examples/scanner-policy.md:32](https://github.com/AI-LLM/hive/blob/main/examples/scanner-policy.md#L32)）。

**判断（解读）**：L4 的标志性产物 `auto-qa-tuning.json` 在 console（被写回），其调速器在 hive（governor）。两边是同一思想的两种实现：把"人实时调权重"换成"代码按阈值自动调"。

---

## Level 5 — Semi-Automated（系统提议，人批准）

**论文描述**：系统检测问题并提议修复，无需人发起；但人仍批准——系统提议，不自主合并。典型实践：社区驱动的 issue→实现流水线（bug 30 分钟、feature 60 分钟）、多 agent 跨仓编排、自改进环。**关键产物：整个代码库即 AI 的操作手册**——每个测试是信任约束，每个 workflow 是策略，每个度量阈值是优先级决策。

**console 的对应文件**：

- **机器可执行的策略（"每个 workflow 是策略"的物化）**：
  - [.github/policies/merge-policy.yaml](https://github.com/AI-LLM/console/blob/main/.github/policies/merge-policy.yaml)：把 PR 接受规则写成 machine-enforceable rules——`dco-required`（[:3-6](https://github.com/AI-LLM/console/blob/main/.github/policies/merge-policy.yaml#L3-L6)）、`adopters-human-approval`（`auto_merge: false`，[:8-12](https://github.com/AI-LLM/console/blob/main/.github/policies/merge-policy.yaml#L8-L12)）、`no-direct-main`（branch_protection，[:14-17](https://github.com/AI-LLM/console/blob/main/.github/policies/merge-policy.yaml#L14-L17)）、`ci-gate`（required_checks build+lint，[:19-23](https://github.com/AI-LLM/console/blob/main/.github/policies/merge-policy.yaml#L19-L23)）。
    - **它与下面的 ai-boundaries.yaml 同病**：全仓**无人 parse 它**（grep 规则名 `dco-required` / `ci-gate` / `required_checks` / `no-direct-main` 除自身外均 0 命中），也只经那份孤儿 README 被提及，CLAUDE.md 不指向它。（注：早先把它当成"被 ACMM scanner 引用"是误判——那几处 `merge-policy` 命中其实是无关的检测 id `fullsend:auto-merge-policy`，它找的是 `.github/auto-merge.yml` / `tide.yaml`，不是本文件。）
    - **但有一处关键差别**：merge-policy 声明的规则**条条都被真执行**，只是执行者是各自独立的一等机制、都不读这份 yaml——`dco-required` 由 [copilot-dco.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/copilot-dco.yml) 挡，`ci-gate` 由 [go-test.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/go-test.yml) / [build-deploy.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/build-deploy.yml) / [coverage-gate.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/coverage-gate.yml) + GitHub required-checks 挡，`no-direct-main` 由 GitHub 分支保护（仓库设置，不在代码里）挡，`adopters-human-approval` 由合并自动化排除 ADOPTERS + scanner 的 CLAUDE.md hard-stop 挡。所以它是"对别处真实强制的一份**镜像声明**"，不是强制本身；而 ai-boundaries 的部分参数（如 `max_files: 10`）连真执行点都没有，更偏 aspirational。
  - [.github/policies/ai-boundaries.yaml](https://github.com/AI-LLM/console/blob/main/.github/policies/ai-boundaries.yaml)：`deny_write`（deploy/、migrations/、workflows、.env）、`require_review`（后端 API surface）、`auto_merge_eligible`（作者白名单 + max_files 10 + 排除 ADOPTERS）——这是"每个度量阈值是优先级决策"的配置形态。

    **这份文件具体怎么被"执行"？——基本不被任何程序执行。** 它是一份"给 AI / 人读的声明式护栏"，真正的强制由别处独立的硬编码机制兜底。三层拆开看：

    1. **它在引用图里几乎是孤岛——agent 的入口指令文件根本不指向它**。把"谁指向谁"摊开（每条可点开核对）：
       - **[CLAUDE.md](https://github.com/AI-LLM/console/blob/main/CLAUDE.md)（agent 每轮必读的入口）→ ✗ 零次**：全文 grep `policies` / `boundaries` / `governance` 命中数为 **0**。agent 的主指令文件**完全没提** policies。
       - **[.github/policies/README.md:10-11](https://github.com/AI-LLM/console/blob/main/.github/policies/README.md#L10-L11) → ai-boundaries.yaml**：全仓**唯一**一处文本引用，且只是散文里的反引号文件名（"See `merge-policy.yaml` ... and `ai-boundaries.yaml` for AI agent guardrails"），不是可点链接。
       - **谁指向这个 README？→ ✗ 无人**：grep `policies/README` 零命中，它本身是无人引用的孤儿文档。
       - **唯一"看见" policies/ 的代码是 ACMM 自评分器**，且只匹配**目录是否存在**、不读内容：[criteria.ts:77](https://github.com/AI-LLM/console/blob/main/web/netlify/functions/acmm-scan/criteria.ts#L77)、[acmm.ts:714](https://github.com/AI-LLM/console/blob/main/web/src/lib/acmm/sources/acmm.ts#L714)、[acmm_scan.go:185](https://github.com/AI-LLM/console/blob/main/pkg/api/handlers/acmm_scan.go#L185) 的 `policy-as-code` 检测 pattern 里列着 `".github/policies/"`。

       结论：所谓"CLAUDE.md → README → ai-boundaries.yaml"的引用链**不存在**——CLAUDE.md 不在链上，README 又无人引用。`ai-boundaries.yaml` **没有任何程序性引用链通向它**，agent 只能靠列目录撞见。而它声明的 `deny_write` / `require_review` / `auto_merge_eligible` 三个 key，全仓 grep 除 yaml 自身外**零命中**——没有 OPA / Kyverno / conftest 解释器（Console UI 里的 kyverno 卡片是产品功能，不是作用于本仓的策略机）。

    2. **真正的"执行者"是 AI agent 自身——靠"读到即遵守"**。这正是 L5"代码库即操作手册"的运行模型：agent 每轮重读仓库（CLAUDE.md / policy / 这份 yaml）后自我设限。boundary 的强制 = agent 的自觉 + 一圈**各自独立重写**的 CI 兜底，没有任何环节以这份 yaml 为输入：
       - `deny_write`（workflows / deploy / .env）→ 实际由 GitHub 分支保护 + [submodule-guard.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/submodule-guard.yml)、[update-guard.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/update-guard.yml) 等 path 守卫各自挡；
       - `require_review`（后端 API surface）→ 仓库**没有 CODEOWNERS** 文件，实际由 [privileged-client-lint.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/privileged-client-lint.yml)、[api-contract.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/api-contract.yml) 这类专项 lint 扫；
       - `auto_merge_eligible`（作者白名单 / max_files 10 / 排除 ADOPTERS）→ 作者门禁硬编码在合并自动化（[copilot-automation.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/copilot-automation.yml) + hive 的 [merge-gate.sh](https://github.com/AI-LLM/hive/blob/main/bin/merge-gate.sh)）和 scanner 的 CLAUDE.md hard-stop 里；其中 `max_files: 10` 这个具体数字**没有任何 workflow 真的去读**。
       即：yaml 里声明的每条规则，别处都有一个**独立重新实现**的强制点，但谁都不把这份 yaml 当输入。

    3. **而 ACMM 自评分器只检查它"存在"、不检查它"生效"**。自评分逻辑 [criteria.ts:77](https://github.com/AI-LLM/console/blob/main/web/netlify/functions/acmm-scan/criteria.ts#L77) / [acmm_scan.go:185](https://github.com/AI-LLM/console/blob/main/pkg/api/handlers/acmm_scan.go#L185) 的 `acmm:policy-as-code` 检测项，pattern 就是匹配 `policies/` 或 `.github/policies/` **路径是否存在**——有这个目录就给一分 L5 治理分，与是否真被强制无关。

    > ⚠ **解读**：这里有一道"声明 vs 执行"的缝。ai-boundaries.yaml 是真实有用的（agent 和人确实读它、据它行事），但它**不是确定性的策略引擎**，其参数（如 `max_files: 10`）也无人当输入；而成熟度扫描器无法区分"写了策略文件"与"策略真被执行"。这是 L4 anti-pattern（"metrics collected but never acted upon"）在 L5 的变体：**policy-as-code 的"code"若没有解释器，就退化回 policy-as-document**。

- **代理化工作流（agentic workflows，系统自己提议并执行）**：
  - [.github/aw/](https://github.com/AI-LLM/console/tree/main/.github/aw)（[github-agentic-workflows.md](https://github.com/AI-LLM/console/blob/main/.github/aw/github-agentic-workflows.md)、[config.yml](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml)、[actions-lock.json](https://github.com/AI-LLM/console/blob/main/.github/aw/actions-lock.json)、[schemas/](https://github.com/AI-LLM/console/tree/main/.github/aw/schemas)）：gh-aw 框架。
  - [.github/workflows/auto-triage.md](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.md)（Copilot 被指派即自动加 `triage/accepted` 标签）、[.github/workflows/implement-fix.md](https://github.com/AI-LLM/console/blob/main/.github/workflows/implement-fix.md)（triage 后把 issue 派给 Copilot 实现，[:1-2](https://github.com/AI-LLM/console/blob/main/.github/workflows/implement-fix.md#L1-L2)）、[.github/workflows/stuck-detection.md](https://github.com/AI-LLM/console/blob/main/.github/workflows/stuck-detection.md)（每 30 分钟检测卡住的工作流并尝试自动恢复，[:3-4](https://github.com/AI-LLM/console/blob/main/.github/workflows/stuck-detection.md#L3-L4)）——issue→triage→实现的提议流水线，对应论文 "community-driven issue-to-implementation pipelines"。

    **这些 `.md` 具体怎么被"执行"？——与上面两份 policy yaml 相反，它们有一条真实、确定性的执行链。** 这些不是声明式文档，而是 gh-aw（GitHub Agentic Workflows）框架的**源文件**，会被编译成可运行的 GitHub Actions workflow：

    1. **源 → 编译 → 运行**。`auto-triage.md` 等是源（frontmatter 声明触发器 `on:` + 护栏 `safe-outputs:` + 正文是给 AI agent 的自然语言 prompt）。`gh aw compile` 把每个 `.md` 转译成 [auto-triage.lock.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml)（文件头标 "DO NOT EDIT"，由 gh-aw v0.77.5 生成，并带源文件的 `frontmatter_hash`/`body_hash`——源与产物绑死、漂移可检测）。GitHub Actions 真正跑的是这个 **active 的 `.lock.yml`**；同目录的 `.md` 与 `.disabled` 副本是惰性的（GitHub 只执行 `.yml`）。编译后还要跑 [.github/aw/patch-lock-files.sh](https://github.com/AI-LLM/console/blob/main/.github/aw/patch-lock-files.sh) 注入 Copilot 指派所需的 GraphQL header（[config.yml:4-7](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L4-L7)）。

    2. **触发器逐字对齐**。`.md` 的 `on: issues: types:[assigned]` 编译进 [auto-triage.lock.yml:50-52](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L50-L52) 成为真触发器。runtime 在防火墙容器里跑 AI agent（provider `copilot`，[config.yml:10](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L10)；egress 经 squid 代理收口，[config.yml:12-17](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L12-L17) `firewall: true`），用固定 SHA 的 actions + github-mcp-server 提供工具。

    3. **safe-outputs 是硬强制点（与 policy yaml 最大的不同：它真被读、真生效）**。agent 不能任意行动——顶层 [permissions: {}](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L55) 让 agent 自身的 token 零权限，它只能往一个 `outputs.jsonl` 写"提议"，再由下游 job 用受限 token **只施加白名单内的输出类型**。auto-triage 的 agent 实际只拿到工具 `add_labels(max:3)`（[auto-triage.lock.yml:210](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L210)），config 写死 `{"add_labels":{"max":3},...}`（[:458](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L458)）+ 约束串 "Maximum 3 label(s)"（[:465](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L465)）——它连评论都发不了。**每个 workflow 的"权能"由各自 frontmatter 的 safe-outputs 决定**：auto-triage = 仅打标签；[implement-fix.md:12-19](https://github.com/AI-LLM/console/blob/main/.github/workflows/implement-fix.md#L12-L19) = `assign-to-agent` + add-comment(max 2)，即它本身不写代码，而是**把 issue 指派给 Copilot 编码 agent** 去写 PR（"实现"那一步是转派）。

    4. **仓库级护栏在 [config.yml](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml) 里、且确实生效**：`protected-paths`（[:43-47](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L43-L47)）禁止 AI 改 `.github/workflows/*.yml`、`*.md`、lockfile——这与 ai-boundaries.yaml 的 `deny_write` **意图相同，但这里是真被 gh-aw runtime 读取强制的**（ai-boundaries 那份没人读）。另有 `threat-detection`（[:48-51](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L48-L51)）、指数退避 `retry`（[:53-58](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L53-L58)，对应论文 "error recovery with exponential backoff"）、stuck 超时阈值（[:100-111](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L100-L111)）、升级通知 team（[:113-118](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L113-L118)）、production 环境覆盖（[:120-127](https://github.com/AI-LLM/console/blob/main/.github/aw/config.yml#L120-L127)）。

    > ⚠ **解读**：这与 policy yaml 是**镜像对照**。policy yaml 是"真实文件、零执行"；agentic workflow 是"真实执行、但跑的是编译产物"。它的信任边界在**编译步骤**：执行的是 `.lock.yml` 而非 `.md`，若有人改了 `.md` 却没重跑 `gh aw compile`，运行行为不变（hash 让漂移可检测，但 compile 不会自动发生）。也就是说——policy yaml 的失效模式是"写了不算"，agentic workflow 的潜在失效模式是"改了不算（直到重新编译）"。但就"系统是否真的自己提议并执行"而言，答案在这里是**确定的 yes**，且护栏（safe-outputs + 零权限 token + 防火墙 + protected-paths）正是论文 L4 anti-pattern（"autonomous action without sufficient guardrails"）所要求的那种。

- **自指的成熟度反馈环（system analyzes itself）**：[.github/workflows/acmm-level-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/acmm-level-monitor.yml)（每天检测自身 ACMM level）+ [.github/workflows/accm-history-update.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/accm-history-update.yml)（更新历史）——代码库分析自己的成熟度并据此开 issue，是"self-improvement cycles" 的极端形态。

**L5 三类产物"声明 vs 执行"对照**：上面三块（两份 policy yaml + 一套 agentic workflow）都被论文当作 L5 治理产物展示，但它们"是否真被执行"截然不同——这是判断一个 L5 代码库成色的关键切面：

| 产物 | 文件是否真实 | 是否真被执行 | 执行机制 | 失效模式 |
|---|---|---|---|---|
| [ai-boundaries.yaml](https://github.com/AI-LLM/console/blob/main/.github/policies/ai-boundaries.yaml) | ✓ | ✗ 零运行时消费者 | 无（部分参数如 `max_files:10` 全仓无人读） | **"写了不算"**——纯声明 |
| [merge-policy.yaml](https://github.com/AI-LLM/console/blob/main/.github/policies/merge-policy.yaml) | ✓ | ✗ yaml 本身没人 parse | 规则**另由**一等机制兜底（[copilot-dco.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/copilot-dco.yml)、CI required-checks、分支保护、CLAUDE.md hard-stop） | "写了不算"，但规则别处**真拦**——是对真实强制的**镜像声明** |
| **agentic `.md`**（[auto-triage](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.md) / [implement-fix](https://github.com/AI-LLM/console/blob/main/.github/workflows/implement-fix.md) / [stuck-detection](https://github.com/AI-LLM/console/blob/main/.github/workflows/stuck-detection.md)） | ✓ | **✓ 编译成 [.lock.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml) 真跑** | gh-aw：`gh aw compile` → GitHub Actions 在防火墙容器跑 agent，safe-outputs + 零权限 token 硬性收口 | **"改了不算"**——跑的是编译产物 `.lock.yml`，改 `.md` 不重编译则行为不变 |

三者共同点：都凭 `.github/policies/` 或对应路径**存在**就被 ACMM 自评分器给 L5 分（[criteria.ts:77](https://github.com/AI-LLM/console/blob/main/web/netlify/functions/acmm-scan/criteria.ts#L77) / [acmm_scan.go:185](https://github.com/AI-LLM/console/blob/main/pkg/api/handlers/acmm_scan.go#L185)），而扫描器**区分不出"声明"与"执行"**。差异点：policy yaml 的失效是"写了不算"，agentic workflow 的失效是"改了不算（直到重新编译）"——前者根本没有执行路径，后者有完整执行路径、只是源与产物可能漂移。

**hive 的对应文件**：[examples/scanner-policy.md](https://github.com/AI-LLM/hive/blob/main/examples/scanner-policy.md)（整篇即"代码库操作手册"）、[examples/kubestellar/fix-loop-skill.md](https://github.com/AI-LLM/hive/blob/main/examples/kubestellar/fix-loop-skill.md)、[bin/supervisor.sh](https://github.com/AI-LLM/hive/blob/main/bin/supervisor.sh)、[bin/kick-outcome-tracker.sh](https://github.com/AI-LLM/hive/blob/main/bin/kick-outcome-tracker.sh)、多仓配置 [examples/kubestellar/hive-project.yaml](https://github.com/AI-LLM/hive/blob/main/examples/kubestellar/hive-project.yaml)。

**判断（解读）**：L5↔L6 的唯一分界是"提议 vs 自动合并"。在 console 里这条线就写在 ai-boundaries.yaml 的 `auto_merge_eligible` 和 merge-policy.yaml 的 `auto_merge: false`——谁能自动合、谁必须人批，是配置项。console 自身停在 L5（人批关键合并），由 hive 把它推到 L6（自动合并 merge-eligible 的 PR）。

---

## Level 6 — Fully Autonomous（系统自我运行）

**论文描述**：系统对发现的问题直接行动——生成 issue、派发 agent、合并 PR、回滚失败。多 agent 作为协调舰队在自适应治理下运行，人事后审计。反馈环：带外部编排的多环；supervisor 协调 executor；workload governor 按实时 backlog 调节；工作经 Beads 账本认领防冲突；push 通知升级需人判断的决策。

L6 的产物**主体在 hive**（参考实现）。console 侧只留两个把自己接到 hive 的接口：[.github/workflows/hive-interactive.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/hive-interactive.yml)、[.github/workflows/hive-trust-gate.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/hive-trust-gate.yml)。以下逐条对照 hive：

### 1. Agent policy files（每次 firing 重读，改行为不重启）
- [examples/scanner-policy.md:13-25](https://github.com/AI-LLM/hive/blob/main/examples/scanner-policy.md#L13-L25)（Step 0 强制重读策略文件），[examples/reviewer-policy.md](https://github.com/AI-LLM/hive/blob/main/examples/reviewer-policy.md)、[examples/architect-policy.md](https://github.com/AI-LLM/hive/blob/main/examples/architect-policy.md)、[examples/outreach-policy.md](https://github.com/AI-LLM/hive/blob/main/examples/outreach-policy.md) 同理。

### 2. Beads work ledger（防重复 + agent 记忆连续性）
- [examples/sqlite-state.md](https://github.com/AI-LLM/hive/blob/main/examples/sqlite-state.md)：Beads（`bd` CLI）与 SQLite 双后端。schema [:30-45](https://github.com/AI-LLM/hive/blob/main/examples/sqlite-state.md#L30-L45) 含 `fix_attempts INTEGER DEFAULT 0`（[:37](https://github.com/AI-LLM/hive/blob/main/examples/sqlite-state.md#L37)，论文 §5.5 的 backoff 计数器）；[:83-84](https://github.com/AI-LLM/hive/blob/main/examples/sqlite-state.md#L83-L84) "failed 3+ attempts → backoff"。[examples/kubestellar/worker.sh:61](https://github.com/AI-LLM/hive/blob/main/examples/kubestellar/worker.sh#L61) 同 schema。

### 3. Governor configuration（实时调速，env 每 tick 取）
- [bin/kick-governor.sh](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh)：四档模式表 [:11-32](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh#L11-L32)、阈值 [:82-85](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh#L82-L85)、成本权重 [:138-141](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh#L138-L141)，全部从 `/etc/hive/governor.env` 每 tick 读取（[:51-54](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh#L51-L54)）。

### 4. Push notification infrastructure（ntfy/Slack/Discord 升级）
- [bin/notify.sh:1-13](https://github.com/AI-LLM/hive/blob/main/bin/notify.sh#L1-L13)（三通道）、[discord/](https://github.com/AI-LLM/hive/tree/main/discord)。

### 5. Observability runbook（人如何 debug 自主行为）
- [docs/troubleshooting.md](https://github.com/AI-LLM/hive/blob/main/docs/troubleshooting.md)（整篇 = 论文的 observability runbook，含 [:27](https://github.com/AI-LLM/hive/blob/main/docs/troubleshooting.md#L27) 的 `systemctl restart` 不重生会话 footgun）、[docs/architecture.md](https://github.com/AI-LLM/hive/blob/main/docs/architecture.md)。
- [dashboard/](https://github.com/AI-LLM/hive/tree/main/dashboard)（论文称之为 "L6 observability artifact"）：[server.js](https://github.com/AI-LLM/hive/blob/main/dashboard/server.js)（SSE 实时）、[ubersicht/hive-status.widget.jsx](https://github.com/AI-LLM/hive/blob/main/dashboard/ubersicht/hive-status.widget.jsx)（macOS 桌面组件）、[agent-activity.py](https://github.com/AI-LLM/hive/blob/main/dashboard/agent-activity.py)（sparkline）。

### 6. Merge queue / auto-merge（验证过的 PR 无人合并）
- [bin/merge-gate.sh:5-13](https://github.com/AI-LLM/hive/blob/main/bin/merge-gate.sh#L5-L13)：判定 merge-eligible 写 JSON，[:13](https://github.com/AI-LLM/hive/blob/main/bin/merge-gate.sh#L13) "Agents should ONLY merge PRs that appear in this file"。
- console 侧：[.github/workflows/copilot-automation.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/copilot-automation.yml)、[.github/workflows/ai-fix.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/ai-fix.yml)。

### 7. Risk assessment config（高风险路径强制人审，与 AI 置信度无关）
- console：[.github/policies/ai-boundaries.yaml](https://github.com/AI-LLM/console/blob/main/.github/policies/ai-boundaries.yaml) 的 `deny_write` / `require_review`（最精确的"风险配置"实物）。
- hive：[examples/architect-policy.md:105](https://github.com/AI-LLM/hive/blob/main/examples/architect-policy.md#L105) 与 [:159-168](https://github.com/AI-LLM/hive/blob/main/examples/architect-policy.md#L159-L168) 强制每个提案带 blast-radius 段落；[config/restrictions/](https://github.com/AI-LLM/hive/tree/main/config/restrictions)。

### 8. Automated issue generation（cron 扫 TODO/陈旧依赖/失败测试/覆盖缺口）
- console：[.github/workflows/ga4-error-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/ga4-error-monitor.yml)、[.github/workflows/auto-qa.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-qa.yml)、[.github/workflows/auto-test-gen.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-test-gen.yml)、[.github/workflows/acmm-level-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/acmm-level-monitor.yml) 都会自动开 issue。
- hive：[bin/ga4-anomaly-detector.sh](https://github.com/AI-LLM/hive/blob/main/bin/ga4-anomaly-detector.sh)、[bin/architecture-detector.sh](https://github.com/AI-LLM/hive/blob/main/bin/architecture-detector.sh)。

### 9. Multi-agent orchestration with role specialization
- hive：[README.md](https://github.com/AI-LLM/hive/blob/main/README.md) 的 5 角色表（scanner/reviewer/architect/outreach/supervisor）、[systemd/hive@.service](https://github.com/AI-LLM/hive/blob/main/systemd/hive@.service)（每 agent 一个单元）、[bin/agent-launch.sh](https://github.com/AI-LLM/hive/blob/main/bin/agent-launch.sh)、[bin/hive.sh](https://github.com/AI-LLM/hive/blob/main/bin/hive.sh)。

### 10. Health monitoring & self-healing（四层韧性）
- [bin/agent-healthcheck.sh:20](https://github.com/AI-LLM/hive/blob/main/bin/agent-healthcheck.sh#L20) 与 [:75-93](https://github.com/AI-LLM/hive/blob/main/bin/agent-healthcheck.sh#L75-L93)：`AGENT_MAX_RESPAWNS:-3`，3 次重生失败即停并 page 人（论文 §5.3）。
- [bin/supervisor.sh](https://github.com/AI-LLM/hive/blob/main/bin/supervisor.sh)（10 秒轮询）、[systemd/](https://github.com/AI-LLM/hive/tree/main/systemd)（gh-zombie-reaper 每 2 分钟等）、[bin/conflict-sweeper.sh](https://github.com/AI-LLM/hive/blob/main/bin/conflict-sweeper.sh)。

### 11. Rollback drill（回滚自主变更的成文流程）
- hive：[bin/conflict-sweeper.sh:1-12](https://github.com/AI-LLM/hive/blob/main/bin/conflict-sweeper.sh#L1-L12)（CONFLICTING PR 自动 rebase，失败则关 PR + 重开 issue）、[examples/scanner-policy.md:247](https://github.com/AI-LLM/hive/blob/main/examples/scanner-policy.md#L247) revert 说明、[examples/reviewer-policy.md:204](https://github.com/AI-LLM/hive/blob/main/examples/reviewer-policy.md#L204) "suggest revert"。
- console：[.github/workflows/post-merge-verify.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/post-merge-verify.yml) / [.github/workflows/pr-closed-verification.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/pr-closed-verification.yml)（合并后验证，失败可触发回滚）。

### 12. CLI-backend agnostic（不绑定具体 AI 工具）
- [config/backends.conf](https://github.com/AI-LLM/hive/blob/main/config/backends.conf)（claude/gemini/copilot/goose）、[bin/hive.sh](https://github.com/AI-LLM/hive/blob/main/bin/hive.sh) 的 `hive switch`/`hive model` 运行时切换。印证论文 §6.1 "intelligence is in the system, not the model"。

### 13. Two scheduling models（Model A 自调度 / Model B EXECUTOR）
- [bin/supervisor.sh](https://github.com/AI-LLM/hive/blob/main/bin/supervisor.sh) + [bin/kick-agents.sh](https://github.com/AI-LLM/hive/blob/main/bin/kick-agents.sh)（tmux send-keys 发工作令 = Model B）；[launchd/com.hive.scanner.plist.example](https://github.com/AI-LLM/hive/blob/main/launchd/com.hive.scanner.plist.example) + [systemd/](https://github.com/AI-LLM/hive/tree/main/systemd) timer（Model A）。生产用 Model B。

---

## 总览对照表

| Level | 论文关键产物 | console（被管理项目，L1–L5 主场） | hive（编排引擎，L4–L6 主场） |
|---|---|---|---|
| 1 Assisted | 无产物 | 刻意的空位（早期 git 史） | [scanner-policy.md](https://github.com/AI-LLM/hive/blob/main/examples/scanner-policy.md#L13-L25) Step 0 反制 |
| 2 Instructed | 指令文件、卡片开发指南 | [CLAUDE.md](https://github.com/AI-LLM/console/blob/main/CLAUDE.md)、[CARD_DEVELOPMENT_GUIDE.md](https://github.com/AI-LLM/console/blob/main/.github/CARD_DEVELOPMENT_GUIDE.md)（"90%" 原话）、[copilot-instructions.md](https://github.com/AI-LLM/console/blob/main/.github/copilot-instructions.md)、[.github/agents/](https://github.com/AI-LLM/console/tree/main/.github/agents) | [examples/.../​*-CLAUDE.md](https://github.com/AI-LLM/hive/tree/main/examples/kubestellar/agents)、[examples/*-policy.md](https://github.com/AI-LLM/hive/tree/main/examples) |
| 3 Measured | 接受率日志、覆盖率、GA4、错误分类、夜间测试 | [auto-qa-tuning.json](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json)、[coverage-gate.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/coverage-gate.yml#L26)(91%)、[ga4-error-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/ga4-error-monitor.yml)(ksc_error)、[nightly-test-suite.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/nightly-test-suite.yml)、[go-coverage-ratchet.txt](https://github.com/AI-LLM/console/blob/main/.github/go-coverage-ratchet.txt) 棘轮、1904+357+123 个测试、[mttr-badge.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/mttr-badge.yml) | [ga4-anomaly-detector.sh](https://github.com/AI-LLM/hive/blob/main/bin/ga4-anomaly-detector.sh)、[fetch-coverage.sh](https://github.com/AI-LLM/hive/blob/main/bin/fetch-coverage.sh)、[issue-classifier.sh](https://github.com/AI-LLM/hive/blob/main/bin/issue-classifier.sh)、[dashboard/](https://github.com/AI-LLM/hive/tree/main/dashboard) |
| 4 Adaptive | 自修改配置(<20% 屏蔽)、闭环 CI/CD | [auto-qa-tuner.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-qa-tuner.yml#L30-L32)(BLOCKED_THRESHOLD:20)、[auto-qa-tuning.json](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json#L131-L145) 的 `history` 里 operator/sre 实际被屏蔽、`rotation_weights`、86 个 [workflow](https://github.com/AI-LLM/console/tree/main/.github/workflows) | [run-pipeline.sh](https://github.com/AI-LLM/hive/blob/main/bin/run-pipeline.sh)、[kick-governor.sh](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh)、worktree |
| 5 Semi-Automated | 代码库即操作手册、多 agent 编排、机器可执行策略 | [merge-policy.yaml](https://github.com/AI-LLM/console/blob/main/.github/policies/merge-policy.yaml)、[ai-boundaries.yaml](https://github.com/AI-LLM/console/blob/main/.github/policies/ai-boundaries.yaml)、[.github/aw/](https://github.com/AI-LLM/console/tree/main/.github/aw)、[auto-triage.md](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.md)/[implement-fix.md](https://github.com/AI-LLM/console/blob/main/.github/workflows/implement-fix.md)/[stuck-detection.md](https://github.com/AI-LLM/console/blob/main/.github/workflows/stuck-detection.md)、[acmm-level-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/acmm-level-monitor.yml) | [scanner-policy.md](https://github.com/AI-LLM/hive/blob/main/examples/scanner-policy.md)、[supervisor.sh](https://github.com/AI-LLM/hive/blob/main/bin/supervisor.sh)、[kick-outcome-tracker.sh](https://github.com/AI-LLM/hive/blob/main/bin/kick-outcome-tracker.sh) |
| 6 Fully Autonomous | policy + Beads + governor + push + runbook + 合并队列 + 风险配置 | [hive-interactive.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/hive-interactive.yml)、[hive-trust-gate.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/hive-trust-gate.yml)（接入 hive） | [sqlite-state.md](https://github.com/AI-LLM/hive/blob/main/examples/sqlite-state.md)、[kick-governor.sh](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh)、[notify.sh](https://github.com/AI-LLM/hive/blob/main/bin/notify.sh)、[merge-gate.sh](https://github.com/AI-LLM/hive/blob/main/bin/merge-gate.sh)、[conflict-sweeper.sh](https://github.com/AI-LLM/hive/blob/main/bin/conflict-sweeper.sh)、[agent-healthcheck.sh](https://github.com/AI-LLM/hive/blob/main/bin/agent-healthcheck.sh)、[docs/troubleshooting.md](https://github.com/AI-LLM/hive/blob/main/docs/troubleshooting.md)、[dashboard/](https://github.com/AI-LLM/hive/tree/main/dashboard)、[architect-policy.md](https://github.com/AI-LLM/hive/blob/main/examples/architect-policy.md#L105) blast radius、[backends.conf](https://github.com/AI-LLM/hive/blob/main/config/backends.conf) |

## 几条需要注意的边界（解读）

1. **两个仓库是被管理者 / 管理者关系**，不是两个独立案例。console = L1→L5 一路成长起来的真实项目，hive = 把它（和另外几个仓库）推到 L6 的引擎。论文的 L1–L5 量化数据全来自 console，L6 参考实现是 hive。

2. **论文点名的 `auto-qa-tuning.json` 实物在 console，不在 hive**。第一版分析里这是个悬而未决的缺口，现已坐实：文件在 [.github/auto-qa-tuning.json](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json)，其写回手是 [auto-qa-tuner.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-qa-tuner.yml)（`BLOCKED_THRESHOLD: 20`），其 `history[]` 里 2026-04-05 起 operator/sre 被自动屏蔽的记录，正是论文 §4.4 Case E 的原始证据。

3. **同一文件常横跨多级**。`auto-qa-tuning.json` 是 L3（接受率日志）也是 L4（被自动写回的自修改配置）；`kick-governor.sh` 是 L4（阈值响应）也是 L6（自适应治理）。Level 是反馈环拓扑的属性，不是文件的属性。

4. **代码库给模型当了 CI 门禁**。[acmm-level-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/acmm-level-monitor.yml) 让 console 每天检测自己的 ACMM level 并要求 ≥ L5——论文的成熟度模型被它的案例代码库内化成了自动化质量门。

## git 历史还原的 level 演进时间线

两个仓库的 commit 历史把 level 上升过程逐月记录了下来——把每个 level 标志性产物**第一次进 commit** 的日期排出来，就是一条成熟度爬升曲线。

### console（L1→L5 的成长轨迹）

仓库初始化 `2026-01-16`，到 2026-06 共 8804 个 commit。每月提交量本身就是论文"吞吐量随 level 加速"论点的实证：

| 月份 | commits | 对应 level（论文 Table 4） |
|---|---|---|
| 2026-01 | 701 | L1→L2 |
| 2026-02 | 899 | L3 |
| 2026-03 | 1409 | L4 |
| 2026-04 | 2939（暴涨） | L5→L6 |
| 2026-05 | 2529 | — |
| 2026-06 | 327（未满月） | — |

标志性产物的首次出现：

| 日期 | 文件首次 commit（链向上游 commit） | 标记的 level |
|---|---|---|
| 2026-01-16 | 初始化（[`63331c4`](https://github.com/kubestellar/console/commit/63331c4234de26b9be786f5aa51b96fbf584f600)）；最早几个 commit 全是 `Fix TypeScript compilation errors` 之类——纯写代码、无任何指令文件 | **L1**（prompt & review） |
| 2026-01-27 | [CLAUDE.md](https://github.com/AI-LLM/console/blob/main/CLAUDE.md) ([`ff0053a`](https://github.com/kubestellar/console/commit/ff0053a189795954eb097e731bf8753bd60d070d)) + [.github/copilot-instructions.md](https://github.com/AI-LLM/console/blob/main/.github/copilot-instructions.md) ([`d4d2fcf`](https://github.com/kubestellar/console/commit/d4d2fcffd8642e085e24109d23db201ae4d015a7)) | **L2** 起点 |
| 2026-02-06 / 02-10 | 第一个前端测试（[`9757be7`](https://github.com/kubestellar/console/commit/9757be7770910d13585f6266109234e82b5f3c3a)） / 第一个 Go 测试（[`6e7c19a`](https://github.com/kubestellar/console/commit/6e7c19a2f8a33ba2666a60101a5e34ae389dbf70)） | **L3** 测试基建开始 |
| 2026-02-17 | [.github/auto-qa-tuning.json](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json) + [.github/workflows/auto-qa-tuner.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-qa-tuner.yml)（同一 commit [`54b0f0a`](https://github.com/kubestellar/console/commit/54b0f0a4d33bf98d6023f27e73ffa1a28e92a37d)） | **L3 接受率日志 + L4 自调权重** |
| 2026-03-07 / 03-13 | [nightly-test-suite.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/nightly-test-suite.yml) ([`2a56039`](https://github.com/kubestellar/console/commit/2a56039d805460fad73c93bf8a218e0ed000532b))、[ga4-error-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/ga4-error-monitor.yml) ([`60101e3`](https://github.com/kubestellar/console/commit/60101e312e97a7312ee3f02e34fd387d768976a4))、[CARD_DEVELOPMENT_GUIDE.md](https://github.com/AI-LLM/console/blob/main/.github/CARD_DEVELOPMENT_GUIDE.md) ([`568a8a2`](https://github.com/kubestellar/console/commit/568a8a29cc82a11f498479fb3f8a7c570095a230)) | L3 加深 |
| 2026-03-31 | [coverage-gate.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/coverage-gate.yml) ([`71a7c5c`](https://github.com/kubestellar/console/commit/71a7c5c5afa2653106e966e6efdeeb0796f169a2))（91% 门禁） | L3/L4 门禁闭环 |
| 2026-04-21 | [.github/policies/ai-boundaries.yaml](https://github.com/AI-LLM/console/blob/main/.github/policies/ai-boundaries.yaml) ([`61a5db6`](https://github.com/kubestellar/console/commit/61a5db609dd4314281dcb7fcac36d79c7a1baf98)) | **L5** 机器可执行策略 |
| 2026-04-25 | [acmm-level-monitor.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/acmm-level-monitor.yml) ([`4352673`](https://github.com/kubestellar/console/commit/4352673ec33d8098e748fcfc6b1dbccb60afa57d))（自测成熟度） | **L5** 自指反馈环 |
| 2026-05-15 | [hive-interactive.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/hive-interactive.yml) ([`ac75a38`](https://github.com/kubestellar/console/commit/ac75a381c60cbc59dc852514c454e037e28a087f))（接入 hive） | **L6** 交接给编排引擎 |

补一个有力细节：[.github/auto-qa-tuning.json](https://github.com/AI-LLM/console/blob/main/.github/auto-qa-tuning.json) 这个文件**被改了 105 次**——它确实是论文说的"自修改配置"，在被持续重写。

### hive（L6 引擎，出生即成熟）

初始化 `2026-04-17`，commit message 即 `initial commit: supervised-agent runtime`。它建得晚得多（仅 713 个 commit、两个月），且几乎所有 L6 产物都挤在 2 周内落地：

- 2026-04-17（第一天，init commit [`eba8935`](https://github.com/kubestellar/hive/commit/eba89356fdf8d6575af3976b6466bc6ee9ac8880)，同时引入）：[bin/agent-healthcheck.sh](https://github.com/AI-LLM/hive/blob/main/bin/agent-healthcheck.sh)、[docs/troubleshooting.md](https://github.com/AI-LLM/hive/blob/main/docs/troubleshooting.md)
- 2026-04-23/24：[examples/sqlite-state.md](https://github.com/AI-LLM/hive/blob/main/examples/sqlite-state.md) ([`48ee157`](https://github.com/kubestellar/hive/commit/48ee157f01463662e182588b05743527381cad5e))、[bin/kick-governor.sh](https://github.com/AI-LLM/hive/blob/main/bin/kick-governor.sh) ([`26bf8b5`](https://github.com/kubestellar/hive/commit/26bf8b5aba401c8cd9187a55d55d7764366caa4a))、[bin/notify.sh](https://github.com/AI-LLM/hive/blob/main/bin/notify.sh) ([`6832716`](https://github.com/kubestellar/hive/commit/683271684a8f276feeebf706506213b557e1cfb9))、[dashboard/server.js](https://github.com/AI-LLM/hive/blob/main/dashboard/server.js) ([`ade2110`](https://github.com/kubestellar/hive/commit/ade2110eaac1af5cfdafaf5a24a637311328bdd8))
- 2026-04-27/29：[config/backends.conf](https://github.com/AI-LLM/hive/blob/main/config/backends.conf) ([`57f262f`](https://github.com/kubestellar/hive/commit/57f262f798b7b53ee71209d39b9d82b79b0e00f2))、[bin/merge-gate.sh](https://github.com/AI-LLM/hive/blob/main/bin/merge-gate.sh) ([`f363157`](https://github.com/kubestellar/hive/commit/f3631578152698da7afc1ff7be74d021d6a91c3f))
- 2026-05-01：[bin/conflict-sweeper.sh](https://github.com/AI-LLM/hive/blob/main/bin/conflict-sweeper.sh) ([`f92be2e`](https://github.com/kubestellar/hive/commit/f92be2e362aa0a4deb19c458b24b4f0f79a2ae9d))
- 2026-05-20：[v2/Dockerfile](https://github.com/AI-LLM/hive/blob/main/v2/Dockerfile) ([`def0d73`](https://github.com/kubestellar/hive/commit/def0d73d95abbaa53d3e4c309d1de4fff1425225))（容器化）

这印证论文 §5.1：Level 6 是 v1 发表三周后才补的，Hive "built in the week preceding this revision"。

### git 历史揭穿的一处理想化（解读）

论文把演进讲成干净的"L1→L2→L3 逐月递进、每级完全先于下一级"。git 历史显示真实过程是**交错叠加**的：

1. **L4 的自调权重（auto-qa-tuner.yml）与 L3 的接受率日志（auto-qa-tuning.json）是同一天（02-17）进来的**——测量和自适应几乎一起建，不是"先有完整 L3 才进 L4"。
2. **论文重点强调的 L2 产物 CARD_DEVELOPMENT_GUIDE.md 直到 03-13 才出现**——那时 L3 测试基建早已铺开。指令文件是边跑边补的，不是 L2 阶段一次写完。
3. **日期对不齐论文的"82 天到 L5、93 天到 L6"**：console 公开初始化是 01-16，但论文称开发始于 2025 年 12 月中（私有期）。以哪个为"零点"都凑不出 82/93 这两个数——论文的天数是约数，公开 git 史只能从 01-16 起算。

结论：**git 历史能清楚还原 level 上升的顺序与加速度，但它呈现的是"基础设施持续叠加"的连续过程，而非论文那种台阶式的离散跃迁**。后者是事后为讲清模型而做的整理。

### AI 署名的可追溯性：连"谁/什么模型写的"都被编码进 commit

console 的 8804 个 commit 里能直接数出**用了哪些模型、哪个 agent**——因为有 [.github/workflows/ai-attribution.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/ai-attribution.yml) 在 CI 侧强制给每个 commit 打 `Co-Authored-By` / `Signed-off-by` 署名。这不是事后估算，是**机器强制的元数据**——本身又是 ACMM 核心论点（"把判断编码进 system artifacts"）的一个例子：连作者归属都沉淀成可查询的 commit trailer。

**模型署名（按 commit 计，含首末日期）**：

| 模型 | commits | 活跃期 |
|---|---|---|
| **Copilot**（执行层，默认底模 Claude Sonnet 4.6，见下） | 3452 | 2026-01-23 → 06-06（贯穿全程） |
| **Claude Opus 4.5** | 1032 | 2026-01-16 → 03-06 |
| **Claude Opus 4.6** | 399 | 2026-02-06 → 03-29 |
| Claude Sonnet 4.6 | 21 | 2026-03-20 → 05-14 |
| Claude Haiku 4.5 | 9 | 2026-05-11 → 05-19 |
| Gemini / gpt-4.1 / DeepSeek-R1 | ~30 / 2 / 1 | 零星 |

**"Copilot"署名背后是什么模型？** 要分两个：

1. **代理化工作流里的 Copilot CLI（auto-triage/implement-fix/stuck-detection）默认钉死 Claude Sonnet 4.6**。编译产物里写死 `COPILOT_MODEL: ... || 'claude-sonnet-4.6'`（[auto-triage.lock.yml:738](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L738)、[:1212](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L1212)、[implement-fix.lock.yml:115](https://github.com/AI-LLM/console/blob/main/.github/workflows/implement-fix.lock.yml#L115)），可被仓库变量覆盖。Copilot 在这里是执行 harness，底层路由到 Sonnet 4.6。AWF 防火墙的模型偏好序也印证（[auto-triage.lock.yml:714](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L714) 内嵌 JSON）：`agent: ["sonnet-6x"(=sonnet-4-5/4-6), "gpt-5.4", "gpt-5.3", "gemini-pro", ...]`——Sonnet 排第一。
2. **托管的 `copilot-swe-agent[bot]`（那 3452 个 commit 的主力，`assign-to-agent` 写 PR 的那个）模型不在仓库内钉**——由 GitHub Copilot 后台设置决定，是托管服务；仓库只能通过上面那个 AWF 允许集间接约束（偏好同样是 Sonnet 4.5/4.6 → GPT-5.x → Gemini Pro）。

所以"Copilot 路由到 GPT/Claude/Gemini"精确说是：**默认 Claude Sonnet 4.6，允许集含 GPT-5.x / Gemini-3.x**。

**但不要据此推成"console 主要功能由 Sonnet 4.6 实现"——时间线否定这点**：`claude-sonnet-4.6` 这个钉法 **2026-04-28 才进仓**（随一次 gh-aw 升级），且只管那三个代理化维护工作流。拆开看分工：

- **1–3 月（L1–L4）核心功能建设期**——架构、卡片、后端、CI 基建——主力是 **Claude Opus 4.5/4.6**（reasoning，~1400 commits 集中于此）+ 托管 `copilot-swe-agent[bot]`（**模型仓库未钉**）+ 人类 Andy（人在环驱动）。
- **4 月底–6 月（L5–L6）自主维护洪峰**——triage / auto-QA 修复 / stuck 恢复——才是 **Sonnet 4.6** 经 Copilot CLI 跑出来的（Copilot 署名 commit 5 月单月 2020 个，但内容偏 QA/小修，非主体功能）。

直接以 `Co-Authored-By: Claude Sonnet 4.6` 署名的只有 21 个 commit。Sonnet 4.6 的体量几乎全在后期维护层；**核心功能的建设主力是 Claude Opus 4.5/4.6**。

**hive 舰队各角色 agent 署名**（signed-off/co-authored）：hive bot 总 1266、reviewer 444、scanner 151、tester 112、architect 61、supervisor 3。（outreach/guardian/analyst/strategist 在本仓未留 commit 署名——未启用或主要在他仓活动。）

**提交者**（谁把 commit 推上去）：Andy Anderson（人类维护者）~5232、**kubestellar-hive[bot]（L6 全自主舰队）2146**、Copilot ~382、github-actions[bot] ~356、dependabot 182。

两个能与 level 演进对上的读法：

1. **推理模型集中在前半程（建设期），执行器贯穿后半程（自主期）**。Claude Opus 4.5/4.6 的署名几乎全在 2026-01～03（L1–L4 的人驱动建设期）；进入 4 月后 Claude 署名骤减，**Copilot（到 6 月、3452 commits）接管后半程**——与 hive 的 `engine: copilot` 执行模型一致（reasoning 在前期密集，autonomous 期是 Copilot CLI 做执行器）。Opus 4.5→4.6 的接棒发生在 2 月中～3 月。
2. **作者维度区分了"人在环"与"全自主"**：Andy 作者的 ~5232 commit 大多带 AI co-author（L1–L5 的人驱动 agent），而 `kubestellar-hive[bot]` 作为作者的 2146 commit 是**人不在键盘上的 L6 自主提交**——这条线把 L5（人批）与 L6（自主合并）在 commit 元数据里也划了出来。

## 需求 → 规格 → 驱动 agent → 代码 / 测试 / 约束的对应链（console 上游）

前面各节看的是"产物落在哪个 level"。这一节看**上游**：console 怎么把"要做什么"一路传导到"agent 生成什么、被什么卡住"。它是一条分层、且**约束端机器强制**的链——不是航天级可追溯矩阵，但对应关系明确。

### ① 需求 / 规格层（WHAT）

- [ROADMAP.md](https://github.com/AI-LLM/console/blob/main/ROADMAP.md)：里程碑需求（按版本/季度，含 Non-Goals）。
- [INVENTORY.md](https://github.com/AI-LLM/console/blob/main/INVENTORY.md)：组件清单（现有 surface 的规格目录）。
- [docs/ai-mission-proposals.md](https://github.com/AI-LLM/console/blob/main/docs/ai-mission-proposals.md)：**AI 生成的需求提案**（18 类 mission + gap analysis）。
- [docs/plans/](https://github.com/AI-LLM/console/tree/main/docs/plans)：RFC（GitOps / Plugin 架构提案）。
- [docs/components/TEMPLATE.md](https://github.com/AI-LLM/console/blob/main/docs/components/TEMPLATE.md)：**单组件规格模板**（Purpose / Data Sources / Props / UI States / Logic / AI Integration）。
- GitHub Issues + ISSUE_TEMPLATE：社区驱动的需求入口（论文的"community is the roadmap"）。

### ② 架构 / 设计规范层（HOW it's shaped）

- [docs/ARCHITECTURE.md](https://github.com/AI-LLM/console/blob/main/docs/ARCHITECTURE.md)、[docs/TEST-COVERAGE-ARCHITECTURE.md](https://github.com/AI-LLM/console/blob/main/docs/TEST-COVERAGE-ARCHITECTURE.md)。
- [docs/components/component-criteria.md](https://github.com/AI-LLM/console/blob/main/docs/components/component-criteria.md)：**设计系统 + 验收标准**（5 种卡片范式、design token、hook 选择、**Definition of Done**）。
- [CLAUDE.md](https://github.com/AI-LLM/console/blob/main/CLAUDE.md) 的 Architecture Decisions 节。

### ③ 驱动 agent 层（spec → agent 的桥）

- [AGENTS.md](https://github.com/AI-LLM/console/blob/main/AGENTS.md)：工具中立入口，指向 CLAUDE.md 为 source of truth。
- [CLAUDE.md](https://github.com/AI-LLM/console/blob/main/CLAUDE.md)：规范总纲（约定 / critical rules / MANDATORY testing）。
- [.github/CARD_DEVELOPMENT_GUIDE.md](https://github.com/AI-LLM/console/blob/main/.github/CARD_DEVELOPMENT_GUIDE.md)：卡片"规格→代码"驱动器（防 90% 拒绝）。
- [.github/agents/*.agent.md](https://github.com/AI-LLM/console/tree/main/.github/agents)：各角色 agent 定义。
- [docs/qa/AI-UX-ISSUE-AGENT-BRIEF.md](https://github.com/AI-LLM/console/blob/main/docs/qa/AI-UX-ISSUE-AGENT-BRIEF.md)：UX agent 的 operating brief（输入/目标/约束）。

### ④⑤ 代码 + 测试

- 代码 `web/src/...`（卡片/hooks）、`pkg/...`（Go）——形状由 TEMPLATE + component-criteria 定，agent 填。
- 测试：CLAUDE.md 的 MANDATORY Testing Requirements + [auto-test-gen.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-test-gen.yml) 自动生成；落地 1904 前端 + 357 Go 测试。

### ⑥ 约束层——关键：写在指南里的约束 ↔ 机器强制的 ratchet ↔ lint，一一对应

这是整条链最硬的地方。CARD guide 的每条"拒绝理由"都有一个棘轮基线 + lint 工作流兜底：

| 指南里的约束（规格） | 机器强制（ratchet/baseline） | lint 工作流 |
|---|---|---|
| 禁 magic numbers | [ai-magic-numbers-baseline.txt](https://github.com/AI-LLM/console/blob/main/.github/ai-magic-numbers-baseline.txt)（`7`） | QA 棘轮 |
| 禁硬编码英文串（用 `t()`） | [ai-non-localized-baseline.txt](https://github.com/AI-LLM/console/blob/main/.github/ai-non-localized-baseline.txt)（`272`） | i18n check |
| 数组操作前必须 guard | [array-safety-baseline.txt](https://github.com/AI-LLM/console/blob/main/.github/array-safety-baseline.txt) | array-safety |
| Go nil slice → `make([]T,0)` | [nilaway-baseline.json](https://github.com/AI-LLM/console/blob/main/.github/nilaway-baseline.json) | [nil-safety.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/nil-safety.yml) |
| 覆盖率 ≥91% | [go-coverage-ratchet.txt](https://github.com/AI-LLM/console/blob/main/.github/go-coverage-ratchet.txt)（`52.0`） | [coverage-gate.yml](https://github.com/AI-LLM/console/blob/main/.github/workflows/coverage-gate.yml) |

再加 [tier-classifier-rules.yml](https://github.com/AI-LLM/console/blob/main/.github/tier-classifier-rules.yml)（按改动路径把 PR 分 tier 0/1/2/3 → 决定要几个人审）与 [docs/AI-QUALITY-ASSURANCE.md](https://github.com/AI-LLM/console/blob/main/docs/AI-QUALITY-ASSURANCE.md) 的 5 个反馈环统管。

**判断（解读）**：整条链是完整的，且约束端机器强制——**"人写下的规格约束"与"CI 强制的基线"一一对应**，这正是 ACMM 核心（把人的判断编码进 system artifacts）：连"卡片该怎么写"都从散文规格压成了可机器卡的数字基线。

> ⚠ **caveat**：这不是正式的需求可追溯矩阵——没有 req-ID → 具体 test 的映射；顶层需求主要是**社区 issue + AI 提案 + ROADMAP**，是 community-steered 而非冻结的 SRS。所以是"分层文档 + 强制约束"，不是航天级 traceability。

## 信源

- 论文：<https://arxiv.org/abs/2604.09388>（Andy Anderson, IBM Research，v2，含 Level 6 与 Hive）
- 被管理项目：console（github.com/AI-LLM/console；上游 github.com/kubestellar/console）
- 编排引擎：hive（github.com/AI-LLM/hive；上游 github.com/kubestellar/hive，Apache 2.0）
