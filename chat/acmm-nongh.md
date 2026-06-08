# 在 Gitea / Forgejo 上复刻 gh-aw 的"编译→锁文件→运行"链——非 GitHub 的 ACMM L5/L6 落地计划

## 这份计划要解决什么

[hive-acmm-level-mapping.md](hive-acmm-level-mapping.md) 分析的"代理化工作流"，其安全性**不在 agent 本身，而在 gh-aw 编译器生成的那套多 job 权限分离骨架**：一个声明式 `.md`（触发器 + safe-outputs + prompt）被 `gh aw compile` 展开成一个自包含的 `.lock.yml`，里面是 5–6 个 job 的流水线——只读 agent 把"提议"写进 Safe Outputs MCP，再由**另一个**带写权限的 job 施加白名单内的动作。

上一版计划里我把这条链当成"opencode 运行时解释就不需要"，**那是错的**：光跑 `opencode run` 只拿到 agent，拿不到外面那层"只读执行 + 提议收集 + 威胁检测 + 最小权限施加"的骨架。本计划的核心就是**把 compile→lock→run 这条链在 Gitea / Forgejo 上复刻出来**。

口径：本文是设计，不在本机运行、不安装任何环境、不需匹配本地版本。范围限定在 **gh-aw 文档支持 + `data/console/.github/workflows/*.md` 实际用到的功能子集**——不实现 gh-aw 全集。

事实（gh-aw 文档 / console lock 文件实测）与设计（本计划提出）分别标注。

---

## 一、先看清编译器到底生成了什么（事实，来自 console 实测）

读 `data/console/.github/workflows/auto-triage.lock.yml`（1398 行，由一个 12 行 frontmatter 的 `.md` 编译而来）。它生成的 **job 图**就是必须复刻的对象：

| 生成的 job | 权限 | 干什么（实测步骤） |
|---|---|---|
| `pre_activation` / `activation` | `contents: read`（只读） | 校验触发器、并发、skip 条件；拼 prompt（[`Create prompt with built-in context`:185](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L185)）；上传 activation artifact |
| `agent` | **`contents: read` 仅此**（[:55 `permissions: {}` 叠加只读](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L55)） | 装 AWF 防火墙二进制（[`Install AWF binary`:418](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L418)）、起 **Safe Outputs MCP HTTP Server**（[:579](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L579)）、起 MCP Gateway、跑 agent（[`Execute GitHub Copilot CLI`:702](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L702)）、**收集提议**（[`Ingest agent output`:815](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L815)）、打印防火墙日志、上传 artifact。**agent 全程无写权限，只往 MCP 写提议。** |
| `detection` | `contents: read` | 对提议做**威胁检测 / 净化**（域名白名单、@提及上限、剥离注入的仓库引用）后才放行 |
| `safe_outputs` | **`issues: write, pull-requests: write`**（[:apply job](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml)，`if: detection==success`） | 读校验过的提议，**只施加白名单类型**（auto-triage 的配置写死 `{"add_labels":{"max":3}}`，[:458](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L458)；agent 拿到的工具只有 `add_labels(max:3), missing_tool, missing_data`，[:210](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L210)） |
| `conclusion` | `issues: write, pull-requests: write` | 收尾、失败转 issue、记录 missing-tool / incomplete |

**gh-aw 官方把这套叫"separation of privilege"四层** [[safe-outputs 文档]](https://github.github.com/gh-aw/reference/safe-outputs/)：① 只读 agent ② Safe Outputs MCP 收集+校验提议 ③ 独立写权限 job 施加 ④ 威胁检测+净化。**这四层就是要在 Gitea 上 1:1 复刻的东西**，而不是"让 opencode 跑一下"。

---

## 二、参考库 `opencode-review-gitea` 有什么、缺什么（事实）

| 能力 | 参考库状态 | 与 gh-aw 骨架的差距 |
|---|---|---|
| agent 角色 + prompt | ✓ `agents/code-review.md` | 对齐 |
| 工具白名单（默认 deny） | ✓ `tools:{"*":false,...}` + `opencode.json permission deny` | 对齐 safe-outputs 的"只开放白名单工具" |
| **权限分离（只读 agent / 写权限 apply 分两个 job）** | ✗ **没有**——`tools/gitea-review.ts` 在 agent 阶段**直接调 Gitea API 写评审** | **最大缺口**：agent 自己就有写权限，没有"提议→检测→施加"的隔离 |
| **威胁检测 / 净化层** | ✗ 没有 | 缺口 |
| **egress 防火墙**（squid/AWF） | ✗ 没有 | 缺口 |
| **编译器**（声明式 .md → 多 job lock 工作流） | ✗ 没有——workflow 是手写单 job | 缺口（本计划核心） |
| **锁文件新鲜度校验**（防源/产物漂移） | ✗ 没有 | 缺口 |

结论：参考库给了**执行层（opencode + 工具白名单）**这块拼图，但**没有编译器、没有权限分离骨架**。本计划要补的正是后者。

### 二·补、能不能直接 port gh-aw？可移植性判断 + 两条路线（这决定了 §三起的设计取舍）

**gh-aw 是 MIT 开源**（Go 66% + JS 32%），配套的 **AWF 防火墙、MCP Gateway、gh-aw-actions 也都开源**，引擎支持 Copilot/Claude/Codex/Gemini [[gh-aw]](https://github.com/github/gh-aw)｜[[MIT LICENSE]](https://raw.githubusercontent.com/github/gh-aw/main/LICENSE)。所以**法律上可随便 fork/改/再分发**。但**开源 ≠ 能直接搬到 Gitea/Forgejo**——编译器**生成的产物**绑死在三样 GitHub 专有件上：

| 绑死的东西 | 为什么搬不动 | 可移植性 |
|---|---|---|
| **GitHub Actions 运行时** | Gitea/Forgejo Actions（act_runner）只是 GitHub Actions 的**兼容子集**。lock.yml 大量用 `actions/github-script`、service containers、`check_run` 事件、artifacts、schedule——在 Gitea 上**部分不支持或行为不同**，须逐个实测 | ✗ 须改 codegen |
| **GitHub REST/GraphQL API（octokit）** | safe-outputs 的 apply job 全程调 GitHub API；Gitea 是**另一套** `/api/v1`。每个施加器都得从 octokit 重写成 Gitea API | ✗ 须重写 API 层 |
| **Copilot 编码 agent**（`assign-to-agent` / `create-agent-session`） | GitHub 托管的；Gitea 没有 | ✗ 须用 opencode 自己写码替代（§六C） |
| github-mcp-server | GitHub 专属 MCP | ✗ 换 gitea-mcp（参考库的工具即是） |
| **AWF 防火墙、MCP Gateway** | 纯 egress 控制 / MCP 路由，**不绑 GitHub API** | ✓ **可直接复用** |
| **编译器架构本身**（md→多 job 权限分离） | 思路可借，codegen 的 target 要换 | ◐ fork 改 target |

**由此两条路线**：

- **路线 1 — fork gh-aw 的 Go 编译器、retarget codegen**：把代码生成的 target 从"GitHub Actions + octokit"换成"Gitea Actions + Gitea `/api/v1`"，砍掉 Copilot-only 输出类型。复用它成熟的 frontmatter 解析、job 图模板、AWF/MCP Gateway。**优点**：拿到 gh-aw 全部成熟度与 ~50 种 safe-output。**代价**：要吃透其 Go 代码，且每次上游改 codegen 都要跟着 rebase retarget 层。
- **路线 2 — 不碰 gh-aw 代码，用 opencode 重新实现 job 图拓扑**（即 §三起的 `gtaw` 方案）：只复刻"权限分离骨架"这个**架构不变量**，功能限定在 console 实际用到的子集。**优点**：实现轻、无上游耦合、与参考库 opencode 同生态。**代价**：safe-output 类型自己一种种加，成熟度从零积累。

**本计划选路线 2**，理由：(a) 目标是 console 用到的 5 种 safe-output，不需要 gh-aw 全集；(b) 执行层已有参考库的 opencode 底座，重写 codegen 比 retarget 别人的 Go 更可控；(c) 路线 2 天然规避"上游 codegen 变动→retarget 层腐烂"。

**但有一条横跨两条路线的硬建议：AWF 防火墙与 MCP Gateway 直接复用 gh-aw 的，别自己造。** 这两块是 §七风险 1（egress 防火墙）和 MCP 路由的现成开源答案，且**不绑 GitHub API**（纯 egress/路由），MIT 可直接拿。`gtaw` 生成的 agent job 应当：
- 用 **AWF**（`ghcr.io/github/gh-aw-firewall/*`，开源）做容器 egress 收口——把网络白名单（Gitea API + LLM 端点）喂给它，而不是自己写 iptables。
- 用 **MCP Gateway**（开源）路由 agent 到工具的 MCP 调用——Safe Outputs"收集器"工具挂在它后面，与 gh-aw 同构。

也就是说：**编译器/施加器/API 层走路线 2 自建，防火墙/MCP 路由走"直接复用 gh-aw 开源件"**——混合最省力。

### 二·补2、Gitea/Forgejo 实测：lock.yml 依赖逐项核实（决定 gtaw 的硬约束）

把 `auto-triage.lock.yml` 的精确依赖逐项对照 Gitea 官方文档 + go-gitea issue 跟踪器。**口径：这是文档级核实（Gitea docs + issue tracker），不是在跑着的 Gitea 实例上跑出来的——本机无 docker/act_runner/gitea，起不了运行沙盒。** 标 ◐/✗ 的项若要坐实成真实日志，需另起最小沙盒探针（见 §七风险 6）。

| lock.yml 依赖 | 用量 | Gitea/Forgejo 支持 | 破坏什么 / 对策 |
|---|---|---|---|
| **`actions/github-script`** | **24 次**（主依赖） | ✗ **不可靠**。Gitea API 非 octokit 路由兼容；`statuses/checks/deployments/id-token/security-events/pages` 等 GitHub-only scope **明确不支持** | **最致命**：github-script 里的编排 + safe-output 施加（尤其碰 checks/statuses 的）跑不通 → gtaw 施加器必须用 Gitea `/api/v1` 原生脚本重写 |
| **`if:` 表达式函数** | 大量（`!cancelled()`、`needs.X.result=='success'`） | ✗ **几乎全废**。Gitea 文档明写"**Expressions: only `always()` is supported**" | detection→apply 的 `if: detection==success` 门控会失效 → 门控逻辑落到脚本里判断 |
| **`check_run` 事件** | console `handle-complications.md` | ✗ **不支持**（Gitea 无 Checks API，用 commit status；checks scope 不支持） | 该类工作流无法以 check_run 触发 → 改 `pull_request`/`schedule` 轮询 |
| **`schedule` cron** | stuck/scan | ◐ **支持但有 bug**：仅默认分支可靠，PR 合并+自动删分支后会在已删分支上跑（[#28157](https://github.com/go-gitea/gitea/issues/28157)、[#29574](https://github.com/go-gitea/gitea/issues/29574)） | 不可靠 → hive 式外部调度（systemd timer/cron 调 API）兜底 |
| **`upload/download-artifact`** | 各 4 次 | ◐ **v4 支持但官方 action 把 Gitea 当 GHES 而中止**，须社区 fork（[gitea-upload-artifact](https://github.com/ChristopherHX/gitea-upload-artifact)）或 v3 | 换 fork，或更稳地**用 job `outputs`/文件系统传**数据、少依赖 artifact |
| **service / `container:`** | firewall、MCP gateway、node | ✓ **支持**（act_runner 用 docker backend 时） | 可用，前提 runner 配 docker backend |
| **`uses:` 钉 SHA** | checkout/setup-node 等 | ✓ 默认从 github.com 解析（或配镜像） | runner 须能访问 github.com 或配 `[actions].DEFAULT_ACTIONS_URL` 镜像 |
| `timeout-minutes` / `continue-on-error` / `environment` | safe_outputs job 用 timeout 15 | ✗ **被 Gitea 忽略** | 仅"无超时强制"，影响小 |
| `issues` / `issue_comment` / `pull_request` / `workflow_dispatch` | A/B/C | ✓ 支持 | 可用 |
| `pull_request_review` | A 评审 | ◐ 较新版本支持，须按目标版本核实 | 验证 runner/Gitea 版本 |

**这次核实直接证明"不能 port gh-aw 的 lock.yml"**——它的 github-script（24 次）、check_run、`cancelled()`/`success()` 表达式在 Gitea 上成片失效，从而**坐实了路线 2（用 opencode 重写 job 图）**。由此 gtaw 生成的 Gitea lock 必须遵守 **6 条硬约束**：

1. **零 `actions/github-script`**——施加器全用 Gitea `/api/v1` 原生脚本；
2. **门控不靠表达式函数**——`if: detection==success` 这类落到脚本里判断（只有 `always()` 可用）；
3. **不用 `check_run` 触发**——改 `pull_request`/`schedule`；
4. **artifact 换 fork 或改用文件 / job `outputs` 传数据**；
5. **`schedule` 一律配外部调度兜底**；
6. **runner 必须 docker backend**（firewall/MCP 容器要它）。

来源：[Gitea Actions 对比 GitHub](https://docs.gitea.com/usage/actions/comparison)｜[github-script 兼容性 FAQ](https://docs.gitea.com/usage/actions/faq)｜[schedule #28157](https://github.com/go-gitea/gitea/issues/28157)｜[artifact v4 #28853](https://github.com/go-gitea/gitea/issues/28853)

### 二·补3、真机实测（Gitea 1.25.5 + act_runner + docker backend，2026-06-08）

把 §二·补2 的文档级判断拿到一台真实 Gitea（`192.168.32.69:3000`，v1.25.5）上跑探针验证：建临时仓库 `LLM/gtaw-probe`，注册一个 docker-backend 的 act_runner（label `ubuntu-latest:docker://catthehacker/ubuntu:act-latest`），推 5 个探针 workflow 看真实 run 日志。**结果推翻了两条最关键的文档级判断**：

| 特性 | 文档级判断（§二·补2） | **真机实测结果** | 证据（真实 run 日志） |
|---|---|---|---|
| `actions/github-script` + octokit | ✗ 不可靠 | **✓ 对 issue/comment/label 可用** | `GHSCRIPT_RESULT {"repos_get":"OK","issues_create":"OK #5","list_labels":"OK"}`——octokit 经 github-script 真在 Gitea 上建了 issue #5。仅 GitHub-only scope（checks/statuses/deployments）不通 |
| `if:` 表达式函数 | ✗ 几乎全废 | **✓ 全部正确求值** | `needs.a.result=='success' && !cancelled()` 的 job **ran**；`failure()` 的 job **skipped**；`always()` 的 job ran。Gitea 文档"only always()"对这版 act_runner 不成立 |
| `upload/download-artifact@v4` | ◐ 须 fork | **✗ 实测确认中止** | `::error:: @actions/artifact v2.0.0+, upload-artifact@v4+ ... are not currently supported on GHES` |
| `container:` + `services:` | ✓ | **✓ 实测确认** | node:20 容器 + redis:7 service，job success |
| `uses:` 从 github.com 解析 | ✓ | **✓ 实测确认**（且 runner 有外网） | runner 日志 `☁ git clone https://github.com/actions/upload-artifact` 成功 |
| `check_run` 触发 | ✗ | ⚠ **无法实测触发**（Gitea 不产生 check_run 事件）；文件可 `workflow_dispatch`（HTTP 204） | — |
| `schedule` | ◐ 有 bug | 未实测（需等时间）；文档 bug 仍按 §二·补2 成立 | — |

**这次实测把 §二·补2 末尾的 6 条硬约束修订为 4 条**（两条最重的被现场推翻）：

- ~~1. 零 `actions/github-script`~~ → **松绑**：施加器可直接用 github-script/octokit 处理 issue/comment/label；仅 checks/statuses/deployments 等 GitHub-only scope 须改 Gitea 原生 API。
- ~~2. 门控不靠表达式函数~~ → **取消**：多 job `if:`（`needs.result` / `!cancelled()` / `failure()` / `always()`）可照搬。
- 3. **不用 `check_run` 触发**——改 `pull_request`/`schedule`（仍成立，Gitea 不发该事件）。
- 4. **artifact 换 fork（[gitea-upload-artifact](https://github.com/ChristopherHX/gitea-upload-artifact)）或 v3，或改用文件 / job `outputs`**（实测确认官方 v4 中止）。
- 5. **`schedule` 配外部调度兜底**（文档 bug 仍在）。
- 6. **runner 必须 docker backend**（实测确认 `container:`/`services:`/artifact 都靠它）。

**净效果**：路线 2 大幅去风险——lock.yml 最依赖的 github-script（24 次）与表达式门控在 Gitea 上其实能跑，连路线 1（fork gh-aw retarget）也比文档判断时更可行。真正的硬骨头收窄到：artifact（换实现）、check_run（换触发）、schedule（外部兜底）、必须 docker runner。

> ⚠ **实测口径**：以上为 Gitea **1.25.5** + 某一版 act_runner + `catthehacker/ubuntu:act-latest` 镜像的结果；不同 Gitea/Forgejo 与 runner 版本可能不同，落地目标环境仍应复跑这套探针确认。探针仓库 `LLM/gtaw-probe` 与 5 个 workflow 可复用。

---

## 三、编译器的输入：声明式源 schema（限定在 console 实际用到的子集）

定义 Gitea 版编译器 **`gtaw`**（gitea-agentic-workflows）。输入 = `.gtaw/agents/<name>.md`，frontmatter 只支持下列字段（取自 gh-aw 文档 [[frontmatter]](https://github.github.com/gh-aw/reference/frontmatter/) ∩ console `*.md` 实际用到的）：

```yaml
---
on:                      # console 用到的全部触发器：
  issues: {types: [...]}            #   assigned / labeled
  issue_comment: {types: [created]}
  pull_request: {types: [...]}      #   opened / synchronize
  pull_request_review: {types: [submitted]}
  check_run: {types: [completed]}
  schedule: [{cron: "..."}]         #   stuck/scan 用
  workflow_dispatch: {inputs: {...}}
concurrency: {group: ..., cancel-in-progress: true}   # console handle-complications 用到
engine: opencode         # 替代 gh-aw 的 engine: copilot/claude
model: deepseek/deepseek-chat
network: {allowed: [gitea-host, llm-endpoint]}        # 生成 egress 白名单
timeout-minutes: 15
permissions: {contents: read}      # agent 阶段恒只读
tools: ["gitea-pr-diff", "gitea-list-stale"]          # agent 可用的【只读】工具
safe-outputs:            # 只支持 console 用到的类型 + 必要替代：
  add-labels: {max: 3, allowed: [...]}     # console 用
  add-comment: {max: 5}                     # console 用
  create-pull-request: {title-prefix: "[AI]", protected-files: [...]}  # 替代 assign-to-agent（见 §六C）
  create-issue: {max: 3, labels: [ai-proposed]}        # scanner 用
  report-failure-as-issue: false            # console 用
  noop: true                                # 系统类型
---
<正文 = 给 opencode agent 的自然语言 prompt>
```

**关键裁剪**：gh-aw 有 ~50 种 safe-output，本计划**只实现 console 真用到的 5 种 + `create-pull-request`**（用来替代 Gitea 没有的 `assign-to-agent`）。其余不做。

---

## 四、编译器的产物：生成的 Gitea lock 工作流（多 job 权限分离）

`gtaw compile` 把上面的 `.md` 展开成 `.gitea/workflows/<name>.lock.yaml`，job 图与 gh-aw 同构：

```
pre_activation/activation (只读)
  └─ 评估 on/if、拼 prompt、上传 prompt artifact
agent (只读 token + egress 防火墙 + 容器)
  └─ opencode run --agent <name>
       工具 = 【收集器版】safe-output 工具：只把提议 append 到 $SAFE_OUTPUTS/outputs.jsonl
       （绝不调 Gitea 写 API）+ 只读工具(gitea-pr-diff 等)
       └─ 上传 outputs.jsonl artifact
detection (只读)
  └─ 净化 outputs.jsonl：域名白名单、@提及上限、剥离注入引用；不过则丢弃该条
apply / safe_outputs (scoped 写 token，独立 job)
  └─ 读净化后的 outputs.jsonl，逐条按类型施加：
       add-labels → 校验 allowed+max → 调 Gitea API
       add-comment → 校验 max → 调 API
       create-pull-request → 触发"实现"子流程（见 §六C）
conclusion
  └─ 失败转 issue（report-failure-as-issue）、记录 missing-tool
```

**与参考库最本质的改动**：safe-output 工具要**拆成两份**——
- **agent 阶段的工具是"收集器"**：`gitea-label`(collector) 只往 `outputs.jsonl` 写 `{"type":"add_labels","labels":[...]}`，**不碰 API**。这对应 gh-aw 的 Safe Outputs MCP server。opencode 侧靠 `opencode.json permission deny` + 该 agent 的 `tools` 白名单只挂收集器版工具来保证。
- **apply 阶段的工具是"施加器"**：真正的 `gitea-label`(applier) / `gitea-comment`(applier) / `gitea-create-pr`(applier) 在独立 job 里跑、用 scoped 写 token、施加前再校验一遍 `max`/`allowed`。

这样 agent 即使被 prompt 注入，也只能写出一条 jsonl 提议，下游 job 仍按白名单+上限过滤——**复刻了"agent 永远无写权限"这个 gh-aw 不变量**。

---

## 五、编译器 `gtaw` 本身（设计）

- **形态**：一个小程序（TS，用 opencode 同生态的 bun 跑；逻辑就是"读 frontmatter→按 schema 校验→模板渲染出 lock.yaml"）。它**不在用户机器跑**，而是作为仓库的一个 CI job（或 pre-commit）跑——和 gh-aw 一样，产物 `.lock.yaml` 提交进仓库、由 Gitea Actions 执行。
- **模板**：维护一套 lock 工作流的 job 模板（上面那 5 段），frontmatter 的每个字段决定模板的填充：
  - `on:` / `concurrency:` → 直接写进 lock 的顶层（Gitea Actions 语法 = GitHub 子集，须实测各触发器在目标 Gitea/act_runner 版本可用，见 §七风险 2）
  - `safe-outputs:` 的每个类型 → 决定 agent 阶段挂哪些**收集器**工具、apply 阶段生成哪些**施加器**步骤及其 `max/allowed` 校验
  - `network:` → 生成 agent job 的容器 egress 白名单（docker network + iptables / 代理）
  - `tools:` + `permissions: contents:read` → agent job 的只读约束
- **防漂移（复刻 gh-aw 的锁文件校验）**：
  - lock 文件头写入源文件的 `frontmatter_hash` / `body_hash`（gh-aw 同款，见 console lock 元数据头）。
  - CI 加一个 `lockfile-fresh` 检查：重跑 `gtaw compile` 并 `git diff`，不一致就 fail——对应 console lock 的 [`Check workflow lock file`:152](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L152) / [`Check compile-agentic version`:164](https://github.com/AI-LLM/console/blob/main/.github/workflows/auto-triage.lock.yml#L164)。这消除"改了 `.md` 没重编译则行为不变"那个失效模式。
- **版本钉**：lock 里所有 `uses:` 钉到 commit SHA（gh-aw 用 `actions-lock.json`，本计划用同样的 lock+patch 思路）。

---

## 六、五条工作流如何套这条编译链

每条 = 一个 `.gtaw/agents/<role>.md`（声明式源）→ `gtaw compile` → `.gitea/workflows/<role>.lock.yaml`。

- **A 自动评审**（参考库已有逻辑）：safe-outputs = `create-pull-request-review`（参考库的 `gitea-review` 改造成收集器+施加器两段）。这是把参考库"单 job 直接写"重构成"两段权限分离"的第一个落点。
- **B 自动分诊**（对应 console `auto-triage.md`）：trigger `issues:[opened]`；safe-outputs = `add-labels: {max:3, allowed:[bug,enhancement,...]}`。agent 只读 issue、只产标签提议。
- **C 自动实现**（对应 console `implement-fix.md` 的 `assign-to-agent`，**Gitea 无此物 → 用 `create-pull-request` 替代**）：trigger `issues:[labeled ai-fix-requested]`；safe-outputs = `create-pull-request`。**这是唯一让 apply 阶段放开写码的工作流**——施加器 `gitea-create-pr` 在独立 job 里：起隔离 worktree 容器、放开 opencode 的 `edit/bash`、按 issue 改码、跑 build/lint/test、按 retry 退避、过则 push `ai/fix-<n>` 分支 + 开 PR（标题强制 `[AI]`、自动 `ai-generated` 标签、`protected-files` 禁改 workflows/lockfile）。agent 阶段仍只读、只产"实现意图"提议；写码隔离在 apply 子 job。
- **D 卡死恢复**（对应 console `stuck-detection.md`）：trigger `schedule: cron`；safe-outputs = `add-comment{max:5}` + `add-labels{max:3}`；只读列举超时项。
- **E 自我提议**（对应论文 L6 自动开 issue）：trigger `schedule`；safe-outputs = `create-issue{labels:[ai-proposed]}`，开前去重。

---

## 七、缺口与风险（正视，别假装 Gitea = GitHub）

1. **egress 防火墙：复用 gh-aw 的 AWF，不自建**（见 §二·补）。gh-aw 的 AWF（squid+api-proxy 容器，MIT 开源、不绑 GitHub API）把 agent 出网收口；参考库没有这层。`gtaw` 生成的 agent job 直接挂 AWF，把网络白名单（只放 Gitea API + LLM 端点）喂给它，而不是自己写 iptables。放开 C 的写码容器后这是**硬要求**。
2. **触发器/schedule 是 Gitea/Forgejo + act_runner 版本相关的**。参考库只验证了 `issue_comment`/`pull_request`/`pull_request_review_comment`。`schedule`（D/E）、`issues:[labeled]`（C）、`check_run`（console handle-complications 用）须在目标版本实测；回退 = hive 式外部调度（systemd timer/cron 调 API 触发 `workflow_dispatch`），把调度可靠性移出 forge（呼应论文 §5 hive 哲学）。
3. **没有 Copilot 编码 agent**：`assign-to-agent` 在 gh-aw 是把活甩给 GitHub 托管的 Copilot；Gitea 版必须 opencode 自己写码（§六C）。质量不确定，建议先只对低风险类别（docs/lint/补测试）放开自动实现，复杂改动停在"提议+人批"（L5），稳了再到 L6。
4. **威胁检测层要自己实现**。gh-aw 的 detection job 做净化（域名白名单、@提及上限、剥离注入引用）；编译器要生成等价的 detection job，否则只读 agent + apply 分离也防不住"提议本身被注入污染"。
5. **opencode 是否支持"收集器/施加器"两段拆分要验证**。参考库的工具是直接调 API 的。把工具改成只写 jsonl、再在独立 job 施加，是本计划对 opencode 用法的关键假设；若 opencode 的 plugin 工具机制不便如此，退一步可在 agent job 内禁掉所有 Gitea 写 API（容器层 egress 只放只读端点），写操作全部留给 apply job 的纯脚本读 jsonl。
6. **~~§二·补2 的 ◐/✗ 项仍是文档级核实~~ —— 已于 2026-06-08 在真机跑过探针，见 §二·补3**。结果推翻了 github-script、表达式两条文档判断，6 条硬约束收为 4 条。仍未实测的只剩 `schedule`（需等时间窗）。落地到**目标环境**时仍建议复跑 `LLM/gtaw-probe` 那套探针，确认目标 Gitea/Forgejo + runner 版本一致。

---

## 八、分阶段落地（按 ACMM 递进，可灰度）

- **Phase 0 — 编译器骨架**：实现 `gtaw compile` 的最小版（支持 `on` + `add-labels` + 两段工具拆分 + lockfile-fresh 检查）。先只跑通"声明式 .md → 多 job lock.yaml"这条链本身。
- **Phase 1 — 权限分离落第一条（B 分诊）**：只读 agent + detection + scoped 写 apply，全套跑通一个最简单的"打标签"工作流。**验证 agent 阶段无写权限**（断网测试：拔掉 apply job，确认标签没被打上）。
- **Phase 2 — 把参考库 A 重构进编译链**：`gitea-review` 拆成收集器/施加器两段，证明现有逻辑能套这套骨架。
- **Phase 3 — egress 防火墙 + 威胁检测 job**：补 §七 缺口 1、4。此时护栏拓扑≈gh-aw。**到此达 L4-L5**。
- **Phase 4 — 自我提议（E）+ 卡死恢复（D）**：补 schedule/外部调度。系统开始自己提议工作。
- **Phase 5 — 自动实现（C）**：apply 阶段放开隔离写码容器，先限低风险类别，PR 仍人批 = **稳态 L5**。
- **Phase 6 — 自动合并**：高接受率类别 PR 过 CI required-checks 即自动合并 = **L6**。

---

## 九、交付物清单（目标 Gitea 仓库）

```
.gtaw/                              # 声明式源 + 编译器（新增，等价 .github/aw + *.md 源）
  compile.ts                        # gtaw 编译器（.md → lock.yaml）
  templates/                        # lock 工作流的 5 段 job 模板
  schema.ts                         # frontmatter 校验（限定 console 子集）
  agents/
    code-review.md  triage.md  implement.md  stuck.md  scanner.md   # 声明式源
  opencode.json                     # permission 全 deny（采参考库）
  tools/
    collectors/   gitea-label.ts gitea-comment.ts gitea-pr-intent.ts  # agent 阶段：只写 jsonl
    appliers/     gitea-label.ts gitea-comment.ts gitea-create-pr.ts  # apply 阶段：调 API
    readonly/     gitea-pr-diff.ts gitea-list-stale.ts ...            # agent 阶段只读
  tests/

.gitea/workflows/                   # 编译产物（gtaw compile 生成，提交进仓库）
  code-review.lock.yaml  triage.lock.yaml  implement.lock.yaml
  stuck.lock.yaml  scan.lock.yaml
  gtaw-lockfile-fresh.yaml          # CI：重编译并 diff，防漂移
  ci.yaml                           # required checks（合并门禁）

# Gitea 设置项（真·强制层）：main 分支保护 + required checks + DCO + bot token 最小 scope
```

---

## 十、落地总结：走路线 2 + 最省力混合，具体怎么做

实测（§二·补3）把方案大幅简化。总原则：**能复用就不造，实测能用就不绕。**

### 三条"省力"决定（全部来自真机实测）

1. **施加器直接用 `actions/github-script` + octokit，不写 Gitea-API 客户端**——实测 `issues.create / addLabels / createComment / listLabels` 在 Gitea 上都通。只有 create-pull-request（要写码）需要自定义逻辑。
2. **job 间传"提议"用 job `outputs`，不用 artifact**——实测 artifact@v4 在 Gitea 中止；提议 jsonl 很小，base64 塞进 `$GITHUB_OUTPUT` 即可，省掉换 fork。
3. **多 job 门控照搬 `needs` + `if:`**——实测 `needs.result`/`!cancelled()`/`failure()`/`always()` 都可用，不用绕。

### 复用清单（不造）

| 件 | 来源 | 怎么用 |
|---|---|---|
| opencode + `permission: deny` + agent `tools` 白名单 | 参考库 `opencode-review-gitea` | 直接拿 `opencode.json` + `agents/*.md` 范式（默认 deny，按角色开工具） |
| `gitea-pr-diff` 等只读工具 | 参考库 `tools/` | 直接用 |
| **施加器（add-labels / add-comment / create-issue）** | `actions/github-script` + octokit | 实测可用 → apply job 一个 github-script step 搞定，**省掉整层 Gitea-API 客户端** |
| **AWF 防火墙 + MCP Gateway** | gh-aw（MIT，`ghcr.io/github/gh-aw-firewall/*`、mcpg） | agent job 里挂 AWF 收 egress、MCP Gateway 路由工具 |

### 自造清单（最小）

1. **`gtaw` 编译器**：一个小 templater——读 `agents/<x>.md` frontmatter（on / safe-outputs / tools / network）→ 渲染 `.gitea/workflows/<x>.lock.yaml`。
2. **job-graph 模板**（每 agent 一份 lock，权限分离骨架）：
   ```
   job agent   (permissions: contents:read；container + AWF egress 收口)
     opencode run --agent <x>          # 工具=收集器，把提议 append 到 proposals.jsonl
     outputs.proposals = base64(proposals.jsonl)
   job apply   (needs: agent; if: needs.agent.result == 'success')
     - uses: actions/github-script     # 读 proposals，按 safe-outputs 类型 + max/allowed 施加
   ```
3. **collector 工具**：把参考库的 `gitea-*` 工具从"直接调 API"改成"append jsonl"（小改）——这是复刻 gh-aw"agent 只提议、不施加"的关键。
4. **create-pr 施加器**（唯一要写码的）：apply 阶段开一个隔离容器放开 opencode `edit/bash`，按 issue 写码 → 跑 build/lint/test → push `ai/fix-<n>` 分支 → github-script 开 PR（标题 `[AI]`、`protected-files` 禁改 workflow/lockfile）。

### 落地顺序（最短到可用，可灰度）

- **Step 1 — 证明骨架**：复用现成在线 runner，手写一条最小"`agent`(只读 opencode)→`apply`(github-script 打标签)"两 job lock，跑通。验证：拔掉 apply job → 标签打不上（证明 agent 无写权限）。
- **Step 2 — 接评审（A）**：把参考库 review agent collector 化，跑通 `/ai review`。
- **Step 3 — 挂防火墙**：给 agent job 接 AWF（复用 gh-aw 件）+ 网络白名单（Gitea API + LLM 端点）。
- **Step 4 — 上编译器**：写 `gtaw` 把 Step 1–2 的手写 lock 模板化；加 `lockfile-fresh` CI（重编译并 diff，防源/产物漂移）。
- **Step 5 — 铺工作流**：triage(B)、scanner(E)（只读+提议，低风险先上）→ 最后 create-pr(C) 的隔离写码。`schedule`(D/E) 一律配外部 cron 调 `workflow_dispatch` 兜底。
- **强制层**（贯穿）：Gitea main 分支保护 + required checks（build/lint）+ DCO + bot token 最小 scope——这层是真拦的，不靠 agent 自觉。

### 一句话

**自造的只剩三样小东西**（gtaw templater、collector 化的工具、create-pr 施加器）；**评审/打标签/开 issue 的施加全交给 github-script，egress/MCP 路由全复用 gh-aw**——这就是路线 2 + 最省力混合的全部。

---

## 信源 / 参考

- gh-aw 官方：[GitHub Agentic Workflows](https://github.com/github/gh-aw)｜[Frontmatter 参考](https://github.github.com/gh-aw/reference/frontmatter/)｜[Safe Outputs 参考](https://github.github.com/gh-aw/reference/safe-outputs/)｜[About Workflows](https://github.github.com/gh-aw/introduction/overview/)
- 编译产物实测：`data/console/.github/workflows/auto-triage.lock.yml`（job 图、Safe Outputs MCP、AWF 防火墙、锁文件校验步骤）；源 frontmatter：`data/console/.github/workflows/{auto-triage,implement-fix,stuck-detection,handle-complications.md.disabled,verify-preview.md.disabled}.md`
- 执行层参考实现：`data/opencode-review-gitea`（[ccsert/opencode-review-gitea](https://github.com/ccsert/opencode-review-gitea)，MIT）——opencode + 工具白名单 + permission deny，但无编译器/无权限分离
- gh-aw 原型分析：[hive-acmm-level-mapping.md](hive-acmm-level-mapping.md) Level 5 "代理化工作流"deep-dive
- ACMM 模型：<https://arxiv.org/abs/2604.09388>
