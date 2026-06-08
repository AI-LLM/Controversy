# 在 Gitea / Forgejo 上实现"代理化工作流"——非 GitHub 的 ACMM L5/L6 落地计划

## 这份计划要解决什么

[hive-acmm-level-mapping.md](hive-acmm-level-mapping.md) 里分析的"代理化工作流（agentic workflows，系统自己提议并执行）"，整套实现绑死在 GitHub 专有栈上：gh-aw 编译器、GitHub Copilot 编码 agent、GitHub Actions、`pull_request_target`、Copilot 指派。**自托管 Gitea / Forgejo 用户拿不到这套。** 本计划把这套能力移植到 Gitea / Forgejo，做到"系统在自己的 forge 上提议并执行工作"。

参考实现：`data/opencode-review-gitea`（[ccsert/opencode-review-gitea](https://github.com/ccsert/opencode-review-gitea)，MIT）。它已经在 Gitea 上跑通了**一条** agentic workflow（PR 自动评审）。本计划把它**泛化成完整的 agentic-workflow 套件**（triage → implement → review → stuck-recovery → 自我提议），并补上 GitHub 版独有、Gitea 版缺失的环节。

事实（参考库已实现的）与设计（本计划提出的）会分别标注。

---

## 一、为什么 opencode + Gitea 是对的底座

gh-aw 那套 L6 的关键不是"AI 多强"，而是**护栏拓扑**：agent 零权限、只能往一个受限的"安全输出"通道写提议、由下游用最小权限施加白名单内的动作（见 [hive-acmm-level-mapping.md](hive-acmm-level-mapping.md) L5 那节的 safe-outputs 分析）。参考库用 opencode 在 Gitea 上复刻了**同构的护栏**：

| gh-aw（GitHub） | opencode + Gitea 等价物 | 出处 |
|---|---|---|
| `.md` frontmatter `on:` 触发器 | `.gitea/workflows/*.yaml` 的 `on:`（Gitea Actions，GitHub 语法子集） | `data/opencode-review-gitea/.gitea/workflows/opencode-review.yaml` |
| `gh aw compile` → `.lock.yml` | **不需要**——opencode 运行时解释 `agent.md`（无编译步骤 = 无"改了不算"的漂移问题） | — |
| body = agent prompt | `opencode run --agent X "<prompt>"` + `agents/X.md` 正文 | `.opencode-review/agents/code-review.md` |
| `safe-outputs:`（add-labels / add-comment / assign-to-agent） | agent frontmatter 的 `tools:` 白名单 + 自定义工具是 agent 碰外界的**唯一**接口 | `agents/code-review.md` 的 `tools: {"*": false, "gitea-review": true, ...}` |
| `permissions: {}`（agent token 零权限） | `opencode.json` 的 `permission: {edit: deny, bash: deny, read: deny}` + 作用域受限的 `GITEA_TOKEN` | `.opencode-review/opencode.json` |
| 安全输出通道（outputs.jsonl，只施加白名单类型） | `tools/*.ts`（每个工具就是一种被允许的副作用，封装一次 Gitea API 调用） | `.opencode-review/tools/gitea-review.ts` |
| github-mcp-server 提供工具 | opencode 自定义工具（`@opencode-ai/plugin`）/ 亦可接 MCP | `tools/gitea-review.ts` 用 `tool()` 定义 |
| 防火墙容器（squid egress 收口） | **缺口**——需补（见 §五风险 1） | — |
| Copilot 编码 agent（`assign-to-agent` 写 PR） | **缺口**——Gitea 无此物，须由 opencode 自己写码开 PR（见 §三 workflow C） | — |
| `config.yml`（provider / protected-paths / retry / stuck 阈值） | `opencode.json` + 环境变量 + 新增 `agentic.yml` | `.opencode-review/opencode.json` |
| 计划任务 stuck-detection（cron） | Gitea Actions `on: schedule:`（需确认 runner 版本支持） | 设计 |

**核心判断**：参考库证明了 safe-outputs 护栏可在 Gitea 上以"opencode permission-deny + per-agent 工具白名单"实现，且因为没有编译步骤，反而消除了 gh-aw 的"源 `.md` 与产物 `.lock.yml` 漂移"那个失效模式。剩下的工作是**把单一 review 工作流扩成完整套件 + 补两个缺口（egress 防火墙、编码执行）**。

---

## 二、目标架构

```
Gitea 事件 (comment / PR / issue label / schedule)
        │
        ▼
.gitea/workflows/ai-*.yaml          ← 触发层（Gitea Actions，等价 gh-aw 的 on:）
        │  起容器、注入 scoped GITEA_TOKEN + LLM key + 上下文 env
        ▼
opencode run --agent <role>         ← 执行层（容器内 opencode CLI）
        │  读 agents/<role>.md（tools 白名单）+ opencode.json（permission deny）
        ▼
自定义工具 tools/*.ts               ← 安全输出层（agent 碰 forge 的唯一接口）
        │  每个工具 = 一种被允许的副作用，封装一次 Gitea API
        ▼
Gitea REST API (/api/v1/...)        ← 副作用真正落地（打标签 / 评论 / 开 PR / 建 issue）
```

护栏在三处叠加，与 gh-aw 同构：
1. **触发层**：workflow 的 `if:` 门（命令前缀 `/ai`、标签、作者白名单）。
2. **执行层**：`opencode.json` 全局 deny + `agents/<role>.md` 的 `tools:` 白名单——agent **默认什么都不能做**，只开放它这个角色该有的工具。
3. **安全输出层**：工具本身是窄接口（`gitea-review` 只能提交评审、`gitea-label` 只能加白名单内标签），且服务端 token 作用域受限。

---

## 三、要实现的 agentic workflows（对齐 gh-aw 三件套 + 扩展）

每条 = 一个 `.gitea/workflows/ai-X.yaml`（触发）+ 一个 `agents/X.md`（角色+工具白名单）+ 若干 `tools/*.ts`（安全输出）。

### Workflow A — 自动评审（auto-review）｜对应 gh-aw 之外、参考库已有
- **触发**：`pull_request: [opened, synchronize]` 或评论 `/ai review`。
- **状态**：参考库**已实现**，直接采用 `data/opencode-review-gitea` 整套（agent `code-review.md` + 工具 `gitea-pr-diff` / `gitea-incremental-diff` / `gitea-review`）。
- **安全输出**：仅 `gitea-review`（提交 COMMENT/APPROVE/REQUEST_CHANGES + 行级评论）。

### Workflow B — 自动分诊（auto-triage）｜对应 gh-aw `auto-triage.md`
- **触发**：`issues: [opened]`，或评论触发；对齐 gh-aw 的"issue 进来即分类"。
- **agent `triage.md`**：读 issue 标题/正文，判类型（bug / enhancement / docs / question）、估复杂度、决定是否 `ai-fix-requested`。
- **安全输出（新建工具）**：`gitea-label`（只能加预定义标签集，等价 gh-aw `add-labels: max 3`）、可选 `gitea-comment`（max 1）。**禁止**改代码、关 issue。
- **enforcement**：`agents/triage.md` 的 `tools: {"*": false, "gitea-label": true}`。

### Workflow C — 自动实现（implement-fix）｜对应 gh-aw `implement-fix.md`（最大缺口）
- **gh-aw 做法**：`assign-to-agent` 把 issue 甩给 Copilot 编码 agent。**Gitea 没有 Copilot agent**，所以这一步必须由 opencode **自己写码**。
- **触发**：issue 被打上 `ai-fix-requested`（`issues: [labeled]`，需确认 Gitea 支持该事件，否则用 `/ai fix` 评论触发）。
- **agent `implement.md`**：这是**唯一需要放开 `edit` + `bash` 权限**的 agent——但限制在一次性 worktree 容器里：
  1. clone + 建 worktree（绝不直接提交 main）
  2. 读 issue + 相关代码，改之
  3. 跑 `build` / `lint` / `test`（项目命令，写进 agent 指令）
  4. 通过失败则按 `agentic.yml` 的 retry 退避重试（上限 N 次→标 `ai-needs-human`）
  5. 通过则 commit（带 DCO `-s`）、push 分支、用新工具 `gitea-create-pr` 开 PR
- **安全输出（新建工具）**：`gitea-create-pr`（开 PR，标题强制 `[AI]` 前缀、自动加 `ai-generated` 标签）、`gitea-comment`。
- **关键护栏**：(a) `edit`/`bash` 仅对此 agent 开、仅在隔离容器；(b) `protected-paths`（见 §四）禁止它改 `.gitea/workflows/`、`*.md`、lockfile；(c) push 目标永远是 `ai/fix-<issue>` 分支，main 由分支保护挡。

### Workflow D — 卡死恢复（stuck-recovery）｜对应 gh-aw `stuck-detection.md`
- **触发**：`on: schedule: cron`（如每 30 分钟；**须确认 Gitea/Forgejo Actions 的 schedule 支持**，否则用外部 cron 调 `workflow_dispatch` 或 hive 式 systemd timer，见 §五风险 2）。
- **agent `stuck.md`**：用工具列出超时项（处理中 issue > 2h、草稿 PR 无活动 > 1h——阈值来自 `agentic.yml`），评论催办 / 重新触发 / 升级。
- **安全输出**：`gitea-list-stale`（只读列举）+ `gitea-comment` + `gitea-label`。

### Workflow E — 自我提议（self-proposal / automated issue generation）｜对应 gh-aw L6"系统提议自己的下一个任务"
- **触发**：`on: schedule`（每日）。
- **agent `scanner.md`**：扫 TODO/FIXME、失败的 CI、覆盖率缺口、陈旧依赖，**开 issue 让 triage→implement 流水线接手**——这就是"系统自己提议工作"的闭环起点。
- **安全输出（新建工具）**：`gitea-create-issue`（开 issue，自动加 `ai-proposed`）。
- **去重**：开前先 `gitea-search-issues` 查重，避免重复提案。

---

## 四、治理与护栏（对应 gh-aw config.yml + 论文 L4 anti-pattern"无护栏的自动化"）

新增 `.opencode-agents/agentic.yml`（opencode.json 之外的策略集中地，等价 `data/opencode-review-gitea` 没有、但 gh-aw `config.yml` 有的那层）：

- **protected-paths**：AI agent 禁改 `.gitea/workflows/*.yaml`、`*.md`、`*.lock` / `go.sum`——由 implement agent 在 push 前自检 + CI 侧 `paths` 守卫双保险。（对应 gh-aw `config.yml:43-47`。）
- **retry / backoff**：指数退避，max-attempts=3，对应论文"error recovery with exponential backoff"。
- **stuck 阈值**：processing-timeout / pr-inactivity-timeout，喂给 Workflow D。
- **author / 触发白名单**：只有 bot 账号或维护者评论 `/ai` 才触发，挡住任意人触发烧 token。
- **作用域 token**：给 bot 账号建**仓库级、最小 scope** 的 access token（issue+PR 写，**不给 admin / workflow 写**），存进 Gitea repo/org secrets（参考库用 `secrets.OPENCODE_GIT_TOKEN`）。

**真·强制层（不靠 agent 自觉，对应 merge-policy 的"一等机制兜底"）**：
- **Gitea 分支保护**：main 禁直推、PR 必过 required status checks（build/lint）、可要求人审——等价 gh-aw 的 `no-direct-main` + `ci-gate`，且这是 Gitea **设置项**（真拦），不是声明文件。
- **DCO**：Gitea 内置 DCO 检查或 CI 工作流强制 `Signed-off-by`。
- **CI 门禁**：项目自己的 `.gitea/workflows/ci.yaml`（build/test/coverage）作为 PR 合并的 required check。

---

## 五、关键缺口与风险（务必正视，别假装 Gitea = GitHub）

1. **egress 防火墙缺失**。gh-aw 用 squid 把 agent 容器的出网收口（防 prompt 注入后外联），参考库**没有**这层。设计：给 Gitea runner 的 agent 容器加网络策略——只允许 Gitea API + LLM provider 端点（docker network + iptables 白名单，或 runner 级 egress 代理）。这是把"评审型只读 agent"升级成"会写码的 implement agent"后**必须补**的，否则放开 `bash` 的容器是攻击面。

2. **schedule / 事件支持是 Gitea/Forgejo 版本相关的**。参考库只用了 `issue_comment` / `pull_request` / `pull_request_review_comment`（确认可用）。`on: schedule`（Workflow D/E 依赖）和 `issues: [labeled]`（Workflow C 依赖）**须在目标 Gitea/Forgejo + act_runner 版本上实测**。回退方案：用 hive 式外部调度（systemd timer / cron 调 Gitea API 触发 `workflow_dispatch`），把"调度可靠性移出 forge"——正好呼应论文 §5 hive 的设计哲学。

3. **没有 Copilot 编码 agent = implement-fix 全靠 opencode 自己写**。这是工作量与质量的最大不确定点。建议：implement agent 用强模型（Claude Sonnet/Opus 或 DeepSeek），且**先只对低风险类别**（docs、lint、测试补全）放开自动实现，复杂改动仍走"提议+人批"（即先停在 L5，验证稳了再放到 L6 自动合并）。

4. **opencode 工具即信任边界**。agent 的全部副作用都过 `tools/*.ts`，所以工具实现必须把 Gitea API 调用写窄（如 `gitea-label` 校验标签在白名单内、`gitea-create-pr` 强制分支前缀与标题前缀）。工具有多严，护栏就有多严。

---

## 六、分阶段落地（按 ACMM 级别递进，可验证）

- **Phase 0 — 地基**：建 bot 账号 + 作用域 token + secrets；起 act_runner；放最小 `opencode.json`（全 deny）。
- **Phase 1 — L2 指令层**：写 `CLAUDE.md` / 项目约定 + 各 `agents/*.md`（角色 + 工具白名单）。
- **Phase 2 — 安全输出工具层**：实现 `tools/`：`gitea-pr-diff`、`gitea-review`（采参考库）+ 新建 `gitea-label`、`gitea-comment`、`gitea-create-pr`、`gitea-create-issue`、`gitea-list-stale`、`gitea-search-issues`。每个配单测（参考库 `tests/*.test.ts` 模式）。
- **Phase 3 — 评审（Workflow A）**：直接移植参考库，跑通 `/ai review`。验证护栏（agent 只能评审、动不了代码）。
- **Phase 4 — 分诊+提议（B、E）**：只读/打标签/开 issue 的低风险 agent 先上，形成"系统提议工作"的入口。**此时已达 L4-L5**。
- **Phase 5 — 自动实现（C）**：放开 implement agent（隔离容器 + egress 防火墙 + protected-paths），先限低风险类别，PR 仍人批 = **稳态 L5**。
- **Phase 6 — 闭环+调度（D + 自动合并）**：补 schedule/外部调度跑 stuck-recovery；对高接受率类别开自动合并（merge-eligible 由 CI required-checks 判定）= **L6**。每升一级前用 `agentic.yml` 的开关灰度。

---

## 七、最终交付物清单（目标 Gitea 仓库里新增的文件）

```
.gitea/workflows/
  ai-review.yaml          # Workflow A（采参考库 opencode-review.yaml）
  ai-triage.yaml          # Workflow B
  ai-implement.yaml       # Workflow C（隔离容器 + 放开 edit/bash）
  ai-stuck.yaml           # Workflow D（schedule 或外部调度）
  ai-scan.yaml            # Workflow E（schedule）
  ci.yaml                 # required checks（build/lint/test/coverage）— 合并门禁

.opencode-agents/         # 改名自参考库 .opencode-review/，避免与用户 .opencode/ 冲突
  opencode.json           # permission 全 deny（采参考库）
  agentic.yml             # 新增：protected-paths / retry / stuck 阈值 / 白名单
  agents/
    code-review.md        # 采参考库
    triage.md  implement.md  stuck.md  scanner.md   # 新建
  tools/
    gitea-pr-diff.ts  gitea-incremental-diff.ts  gitea-review.ts   # 采参考库
    gitea-label.ts  gitea-comment.ts  gitea-create-pr.ts          # 新建
    gitea-create-issue.ts  gitea-list-stale.ts  gitea-search-issues.ts
  tests/                  # 每个工具配单测（参考库模式）

# Gitea 设置项（非文件，但属交付）：main 分支保护 + required checks + DCO + bot token scope
```

## 信源 / 参考

- 参考实现：`data/opencode-review-gitea`（[ccsert/opencode-review-gitea](https://github.com/ccsert/opencode-review-gitea)，MIT）——已跑通的 Gitea PR 评审 agent
- gh-aw 原型分析：[hive-acmm-level-mapping.md](hive-acmm-level-mapping.md) 的 Level 5 "代理化工作流"deep-dive（safe-outputs / 编译链 / config.yml 护栏）
- opencode 自定义工具与权限：`data/opencode-review-gitea/.opencode-review/opencode.json`、`agents/code-review.md`、`tools/gitea-review.ts`
- ACMM 模型：<https://arxiv.org/abs/2604.09388>
