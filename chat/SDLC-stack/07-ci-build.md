# 2026-05-14：SDLC 栈 / CI-CD 与构建 层深度研究

附录 III 把 D4（构建 / CI）和 C5（部署 / CD）压成一行表格，结论只写了 "GitHub Actions、Buildkite + AI 受益；CircleCI 被挤压"。但这一层在 2025–2026 发生的事远比 "加个 AI 排查失败原因" 剧烈——**流量模式本身被 Coding Agent 改写了**：PR 的产生方不再是人，build 的触发频率与并发度不再服从办公时间分布，cache 的命中策略也不再是 "同一开发者多次 push"。这一节单独深挖。

## 一、Pre-Agent 时代的 CI 流量模式（2010–2023）

**典型负载剖面**（中型 SaaS，~200 工程师）：

- **PR/天**：每工程师 ~1.5，团队 ~300 PR/天高峰；夜间归零
- **build/PR**：~3 次（push、rebase、merge），合计 ~900 build/天
- **build runtime**：JS monorepo 中位 8–12 分钟，Java/Bazel 大库 20–40 分钟
- **cache hit rate**：GitHub Actions 默认 cache 上限 10 GB，传输 ~145 MiB/s，命中 60–75% 是好成绩 [[1]](https://runs-on.com/benchmarks/github-actions-cache-performance/)
- **并发上限**：免费 GHA 默认 20 个 concurrent job，企业版 1000；CircleCI 按合同并发数计费
- **触发时间分布**：UTC 工作时段集中，周末/夜晚 < 10%

钱的逻辑是 **per-minute 计 build runtime**——GitHub Actions Linux x64 标准价 $0.008/min，Windows 1.6×，macOS 8×，2025 年 GitHub 全平台跑掉 **115 亿分钟** [[2]](https://github.com/resources/insights/2026-pricing-changes-for-github-actions)。

CI 平台的护城河是 **生态（marketplace action）+ 与 SCM 的集成**，性能差异不大，因为 build runtime 的瓶颈在用户自己的脚本（`npm install`、`docker build`、`pytest`），不在调度。这是 Jenkins / CircleCI / GitHub Actions 多年共存的原因。

## 二、Post-Agent 流量模式：四个本质变化

### 2.1 PR 数量爆炸

Faros AI 在 2026-04 发布的 *AI Productivity Paradox* 研究：**高 AI 采用率团队完成任务多 21%，合并 PR 多 98%**，但 PR review time 也涨 91% [[3]](https://www.faros.ai/blog/ai-software-engineering)。Cursor 2026-02 ARR $2B 时已有 1M+ 日活、5 万企业客户 [[4]](https://www.getpanto.ai/blog/cursor-ai-statistics)；Cursor 2.0（2025-10）支持单开发者 **同时跑 8 个并行 agent**，每个 agent 占独立 workspace clone [[5]](https://medium.com/@chaos.architect25/the-best-ai-coding-tools-of-may-2026-cf2db2804a0f)。Devin 2.0 同样支持 **multi-instance parallel**，一名工程师把当天 4 个任务各分配一个 Devin 实例 [[6]](https://www.deployhq.com/guides/devin)。

后果：**一名工程师每日触发的 build 数从 ~5（3 次/PR × 1.5 PR）跳到 ~30–80**——8 个 agent 各自跑 lint/test 的 push 频率远高于人。

### 2.2 触发分布扁平化

Agent 不睡觉。Cursor 的 background agent 跑在 AWS 隔离 VM 上，"machine that kicked it off goes offline" 之后 agent 继续运行 [[7]](https://docs.cursor.com/en/background-agent)。Devin 接受 issue → 异步排队、跑通 CI、贴回 PR；夜里 02:00 触发的 build 比例从 < 10% 涨到 ~35%（基于 Faros 数据外推，**解读**）。

CI 的容量规划假设——"工作日 9–18 点峰值，按峰值买 runner"——被破坏。**弹性需求从 5× 倍峰谷比变成几乎无峰谷**，预付固定 self-hosted 容量的模型立刻变得低效。

### 2.3 build 失败被 agent 主动消费

传统 CI 失败 → 等人看 → 修。Agent 的 loop 是 build 失败 → agent 读日志 → 再 push → 再 build。Devin 的官方描述："picking up review feedback and CI results to get each PR approved and merged" [[6]](https://www.deployhq.com/guides/devin)。**每个 PR 的 build 次数从 ~3 上升到 ~8–15**（agent 多轮自修复直到绿）。

这把 CI 从"验证关卡"变成了 "agent 的反馈传感器"——CI 必须**毫秒级返回结构化失败信号**（不是 30 分钟后给一段日志）。GitLab Duo 的 Root Cause Analysis（GA since GitLab 17.3）已开始把 CI 日志解析成结构化失败原因供 agent 消费 [[8]](https://www.buildmvpfast.com/alternatives/buildkite)。

### 2.4 每个 agent 需要一个隔离环境

Cursor background agent、Devin、Replit Agent 都要求**独立 sandbox**：不能共享主机，否则 npm install 互相污染、端口冲突、密钥泄漏。Cursor 一次"easy PR" 的成本实测 $4.63 [[9]](https://www.morphllm.com/cursor-background-agents)，里面环境启动占非平凡比例。

新需求一句话总结：**亚秒级冷启动 + 单租户隔离 + 整盘共享 cache + 按秒计费**。这套需求传统 CI runner（Jenkins agent / GitHub Actions runner pool）的架构完全做不到——它们假设 runner 长期复用、cache 走网络、隔离靠 Docker 容器。

## 三、namespace.so：把 CI runner 重新当作"compute platform"建

Namespace Labs 创始人 Hugo Santos（前 Google，参与 Search/Photos/Assistant 微服务平台基础设施），2020 年成立公司，2026-03 完成 Series A 共 $23M 融资 [[10]](https://www.crunchbase.com/organization/namespace-labs)。核心产品三件套：

1. **Ephemeral Clusters**——按需启动的 k3s Kubernetes 集群，**秒级**就绪 [[11]](https://namespace.so/)
2. **CI Runners（GHA / GitLab）**——GitHub Actions 和 GitLab CI 的 drop-in 替换
3. **Devbox / Agent Sandbox**——为 Coding Agent 提供独立云环境，"agent 在 Devbox 里干活，不阻塞本地机器" [[11]](https://namespace.so/)

### 关键架构创新

**自有机柜，不租公有云**：Namespace 自建多数据中心机柜，"full-stack solutions encompassing compute, network, and storage" [[12]](https://betterstack.com/community/comparisons/namespace-alternatives/)。第三方基准里 Namespace **x64 单线程跑分领先所有第三方 GHA runner 提供商，arm64 也领先** [[13]](https://runs-on.com/benchmarks/github-actions-cpu-performance/)。

**本地高性能存储 + 内置 cache**：Bazel、Turborepo 等工具的 cache 后端直接打通到 runner 本地 NVMe，cache 命中不走公网。对比 GitHub 内置 cache 的 145 MiB/s，Depot 实测 1,000 MiB/s（~7×）[[14]](https://depot.dev/blog/comparing-github-actions-and-depot-runners-for-2x-faster-builds)。Namespace 走同一思路但绑定自己的存储层。

**nsc CLI——把"开 sandbox"做成一行命令**：

```bash
# 起一台 2 vCPU / 8GB ARM64 Linux 实例（秒级）
nsc create --shape linux/arm64/2x8

# 在 ephemeral 环境里直接跑容器
nsc run --image ghcr.io/myorg/agent:latest --port 8080

# 把 Docker 上下文指向 ephemeral 环境（本地 docker build 实则跑在远端）
nsc docker attach-context

# Kubernetes 服务暴露公网 ingress
nsc expose kubernetes --service my-service
```

四个命令覆盖：**实例创建（D4）→ 运行容器（C4）→ 远端 Docker（D4）→ K8s 暴露（C5）**——D4 和 C5 两层的边界被一根 CLI 抹掉。这是和老一代（Jenkins YAML / CircleCI YAML / GHA workflow）最本质的不同：**老 CI 假设 build 跑在"作业槽"里，namespace 假设 build 跑在"一次性云"里**。

### 定价模型

Namespace 公开价格 [[15]](https://namespace.so/pricing)：

| 形态 | 价格 |
|---|---|
| x64 standard 2 vCPU / 8 GB | **$0.0008/min** |
| x64 standard 30 vCPU | $0.0120/min |
| x64 premium | 2× standard |
| arm64 standard | 同 x64 standard |
| Linux-on-Apple-Silicon | $0.012/min |

对比 GitHub Actions 2 vCPU Linux 标准价 $0.008/min（2026-01 后），namespace 2 vCPU 同档 **便宜 10×**；GHA 30 vCPU 不存在等价档位，需买 64 vCPU 的 $0.256/min，namespace 30 vCPU $0.012/min **便宜 ~20×**。用户实测"pipeline execution time 3× 提升的同时更便宜" [[12]](https://betterstack.com/community/comparisons/namespace-alternatives/)。

### 和老一代的对比

| 维度 | Jenkins / CircleCI / GHA 原生 | namespace.so |
|---|---|---|
| 启动时延 | 30–90s（拉镜像、装依赖） | 秒级（预热 + 本地存储） |
| 隔离粒度 | 容器 / job 级 | 一次性 micro-VM / 集群级 |
| Cache 带宽 | 公网 145 MiB/s（GHA） | 本地 NVMe ~GB/s 级 |
| 弹性曲线 | 预购并发数 / 排队 | 按秒计费、瞬时扩容 |
| Agent 友好度 | 不假设 agent 触发 | 一等公民（Devbox） |
| 定价单位 | per-minute（最小 1 分钟） | per-minute 但秒级冷启动让短任务可行 |

## 四、同层其他玩家：各自切哪个角度

| 玩家 | 切入角度 | 关键数字 / 特征 |
|---|---|---|
| **Depot** | "GitHub Actions 替代 runner + 远程 Docker build cache" | 比 GHA 快 2–3×，cache 上传/下载 ~1,000 MiB/s vs GHA 145 MiB/s；同场 build 含 cache 成本 $0.012 vs GHA $0.04（−70%） [[14]](https://depot.dev/blog/comparing-github-actions-and-depot-runners-for-2x-faster-builds) |
| **Blacksmith** | "Hetzner 裸金属上跑 GHA runner，便宜 50%/快 2×" | 跑在 Hetzner 物理机；$0.004/min（2 vCPU）；3000 min/月免费额度；Docker layer cache 加价 ~$0.50/GB/月 [[15]](https://www.blacksmith.sh/blog/actions-pricing) |
| **Buildkite** | "你自己出 runner，我负责 orchestration + AI" | 2026 推出 LLM Proxy：流水线直接调 Anthropic Claude（Sonnet / Opus / Haiku），统一密钥/计费；定位是 "AI-powered CI 的底座" [[8]](https://www.buildmvpfast.com/alternatives/buildkite) |
| **Dagger** | "用 Go/Python/TS 写流水线，DAG 在容器里跑，跨 CI 可移植" | 由 Docker 创始人 Solomon Hykes 创立；Apache 2.0 开源 engine；2025-07 接管已停服的 Earthly 用户，Dagger Cloud Team 免费 1 年 + migration workshop [[16]](https://dagger.io/blog/earthly-to-dagger-migration) |
| **Earthly** | （已退场） | 2025-07-16 关闭 Earthly Cloud 与 Earthfile 主动维护，CEO 公开承认 "inability to monetize compute as a commodity" [[17]](https://earthly.dev/blog/shutting-down-earthfiles-cloud/) |
| **Garnix** | "Nix flakes 原生 CI + 全网 binary cache" | 用 Nix flake 保证 reproducible；比 GHA 上的 Nix-CI 快 **2–10×**；intermediate build 结果上传 cache，"CI 永不重建同一物件" [[18]](https://garnix.io/) |
| **CircleCI** | （老叙事被分走）维持企业大客户 | 仍是托管型，没有自有 agent 故事；2026 多份对比报告把它列为 "可被 Buildkite/GHA+Depot 替代" 的代表 [[19]](https://spacelift.io/blog/circleci-alternatives) |
| **Mergify / Aviator** | C5 上游的 **merge queue**——PR 数量爆炸后真正的瓶颈 | Aviator MergeQueue 用于 1000+ 工程师团队 monorepo；Mergify Max plan $21/seat/月；2026-05 Mergify 用 `auto_merge_conditions` 替代旧 `autoqueue`，并自动开 migration PR [[20]](https://www.aviator.co/aviator-mergequeue-mergify) [[21]](https://docs.mergify.com/changelog/2026-05-06-automatic-migration-from-autoqueue-to-auto-merge-conditions/) |

**解读**：把这些玩家排队，能看出 D4 这一层被切成三个子赛道——

- **底层 compute**：namespace、Depot、Blacksmith、Garnix。竞争维度是 "秒级冷启动 + 本地 cache 带宽 + 单价"
- **流水线编程模型**：Dagger（活下来的）、Earthly（死了）。竞争维度是 "用真编程语言写 pipeline"
- **PR/merge 治理**：Mergify、Aviator、GitHub 原生 merge queue。竞争维度是 "PR 爆炸后如何不让 main 一直挂"

GitHub Actions 自己也在调整——2026-01 hosted runner 降价最多 39%，但 2026-03 起 self-hosted runner 加收 $0.002/min 的 "Actions cloud platform fee"，把 Blacksmith、namespace、Depot 这些第三方 runner 收编为 "ecosystem partners rather than workarounds" [[2]](https://github.com/resources/insights/2026-pricing-changes-for-github-actions)。**GitHub 不打算赢底层 compute，但要确保所有 build 流量都过它的控制平面**。

## 五、典型客户路径与计费实例

一家 60 人的 AI 原生 SaaS 公司，2025 年还在 GHA 上跑：

- 每月 build 分钟 ~120,000（60 人 × 22 工作日 × 90 min/天）
- GHA Linux 标准 $0.008/min × 120,000 = **$960/月**

2026 年接入 Cursor + Claude Code，每位工程师每天 ~6 个 background agent，agent 触发的 build 占比涨到 65%：

- build 分钟 ~360,000/月（3× 增长，主要来自夜里和并行）
- 仍跑 GHA：$0.008 × 360,000 = **$2,880/月**
- 切 namespace standard 2 vCPU：$0.0008 × 360,000 = **$288/月**

**绝对节省 ~$2,600/月**，但更重要的不是节省，而是**没有切 namespace 会跑到 GHA 的并发上限**（企业版 1000）——8 个 agent × 60 人 = 480 并发 token 已经接近上限，再加 retry / matrix 就溢出排队，把 agent 的迭代延迟从秒级拉到小时级，agent 的价值就垮了。

这就是 namespace 那段 "ephemeral compute platform optimized for developer use-cases with high I/O requirements" 文案的真实含义——**它在卖的不是便宜的 CI 分钟，是 agent 时代必需的瞬时扩容能力**。

## 六、3 年视角的几条本质判断

1. **D4 这一层的 commodity 化已经发生**。Earthly 关掉 Earthfile Cloud 时 CEO 写的那句 "compute is a commodity" 是这一层的墓志铭——纯 build 编排 SaaS 没有定价权了，价值会向两端外溢：**上游（Mergify/Aviator 的 merge queue 治理）和下游（namespace/Depot 的 compute substrate）**。

2. **CI 流量模式从"人 push 触发"变成"agent 触发 + 长尾分布"**，预付固定 runner 容量的商业模式（Jenkins 自营、CircleCI 套餐）在结构上劣于按秒计费 + 秒级冷启动。CircleCI 5 年内被边缘化的概率，**解读**：高。

3. **Cache 带宽差几个数量级是赢家的关键**：GHA 145 MiB/s vs Depot/namespace ~1 GB/s。当 agent 每天触发几十次 build，cache miss 的 30 秒乘几十次 = 一名 agent 一天浪费十几分钟。Cache 不再是优化项，是**功能正确性的一部分**。

4. **CI 与 dev-environment 边界在消失**。namespace 的 nsc CLI、Cursor 的 background agent VM、Devin 的 sandbox、Replit 的 Workspace——本质都是 "一次性、隔离、带 cache 的云 Linux"。未来的赢家会是**同时托管 CI build 和 agent 运行环境的统一平台**，而不是单纯做 CI runner。namespace.so 正卡在这个位置。

5. **GitHub 的控制平面策略 = 抽税**。2026-03 起对 self-hosted runner 收 $0.002/min 平台费，是把 D4 底层 compute 让给第三方、把控制平面权力集中到自己手里的明确信号。这意味着 namespace / Depot / Blacksmith 越成功，GitHub 越赚钱——他们和微软在结构上是共生的，不是对抗。

6. **Earthly 的死值得二次复盘**：技术（Earthfile DSL）漂亮，融资充足，但败给了"无法把 commodity compute 卖出溢价"。Dagger 之所以还活着，是因为它选择**不卖 compute、卖编程模型**——pipeline 用真语言写，跑在用户自己的任何 CI 上。这条边界对所有想进入这一层的创业公司是关键警示。

---

## 信源

[1] RunsOn, "Fastest GitHub Actions Runners: Cache," 2026. (GHA 内置 cache 上限 10 GB，传输带宽 ~145 MiB/s) [Online]. Available: <https://runs-on.com/benchmarks/github-actions-cache-performance/>

[2] GitHub, "Pricing changes for GitHub Actions," 2026. (2025 年全 GHA 跑 115 亿分钟；2026-01 hosted runner 最多降价 39%；2026-03 起 self-hosted 加收 $0.002/min cloud platform fee；4% 用户受影响) [Online]. Available: <https://github.com/resources/insights/2026-pricing-changes-for-github-actions>

[3] Faros AI, "The AI Productivity Paradox Research Report," Apr 2026. (高 AI 采用率团队完成任务多 21%，合并 PR 多 98%，但 PR review time 涨 91%) [Online]. Available: <https://www.faros.ai/blog/ai-software-engineering>

[4] Panto AI, "Cursor AI Statistics 2026: Users, Revenue and Adoption," 2026. (Cursor 2026-02 ARR $2B；1M+ 日活；50,000 企业客户) [Online]. Available: <https://www.getpanto.ai/blog/cursor-ai-statistics>

[5] R. Pires, "The Best AI Coding Tools of May 2026: A Scorecard," *Medium*, May 2026. (Cursor 2.0 支持 8 个并行 agent，每个独立 workspace clone；2026-02 各家同时上 multi-agent parallel coding) [Online]. Available: <https://medium.com/@chaos.architect25/the-best-ai-coding-tools-of-may-2026-cf2db2804a0f>

[6] DeployHQ, "Devin AI Guide: Autonomous Coding Agent & Deployment," 2026. (Devin 2.0 支持 parallel multi-instance；agent 主动消费 CI 失败并迭代 PR) [Online]. Available: <https://www.deployhq.com/guides/devin>

[7] Cursor, "Background Agents — Documentation," 2026. (Cursor background agent 跑在 AWS 隔离 VM，触发机器下线后 agent 继续运行；2026-03 起强制 GitHub) [Online]. Available: <https://docs.cursor.com/en/background-agent>

[8] BuildMVPFast, "Best Buildkite Alternatives (2026): Pricing Compared," 2026. (Buildkite 2026 LLM Proxy：流水线直调 Claude；GitLab Duo Root Cause Analysis 自 17.3 GA，把 CI 日志解析成结构化失败) [Online]. Available: <https://www.buildmvpfast.com/alternatives/buildkite>

[9] MorphLLM, "Cursor Background Agents: Complete Guide (2026)," 2026. (一次 easy PR 实测成本 $4.63；usage-based pricing 最低 $10/月) [Online]. Available: <https://www.morphllm.com/cursor-background-agents>

[10] Crunchbase, "Namespace Labs — Company Profile & Funding," 2026. (创始人 Hugo Santos 前 Google；2026-03-23 完成 Series A；累计 $23M / 2 轮 / 6 投资人) [Online]. Available: <https://www.crunchbase.com/organization/namespace-labs>

[11] Namespace, "Accelerate your developer workflow," 2026. (Ephemeral Cluster 秒级启动 k3s；Devbox 给 agent 提供独立云环境) [Online]. Available: <https://namespace.so/>

[12] Better Stack, "12 Best Namespace Alternatives for GitHub Actions Runners," 2026. (Namespace 自建多数据中心机柜；用户 pipeline 提速 3× 同时更便宜) [Online]. Available: <https://betterstack.com/community/comparisons/namespace-alternatives/>

[13] RunsOn, "Fastest GitHub Actions Runners: CPU Speed," 2026. (Namespace x64 单线程跑分领先所有第三方 GHA runner 提供商，arm64 也领先) [Online]. Available: <https://runs-on.com/benchmarks/github-actions-cpu-performance/>

[14] Depot, "Comparing GitHub Actions and Depot runners for 2x faster builds," 2026. (Depot cache 上传/下载 ~1,000 MiB/s vs GHA 145 MiB/s；含 cache build 比 GHA 快 57%；同场 build 成本 $0.012 vs GHA $0.04，−70%；GHA 10 GB cache 上限被打破) [Online]. Available: <https://depot.dev/blog/comparing-github-actions-and-depot-runners-for-2x-faster-builds>

[15] Blacksmith, "The GitHub Actions control plane is no longer free," 2026. (Blacksmith 跑在 Hetzner；$0.004/min 2 vCPU 起；3000 min/月免费；Docker layer cache ~$0.50/GB/月) [Online]. Available: <https://www.blacksmith.sh/blog/actions-pricing>

[16] Dagger, "A Soft Landing for Earthly Users," 2025. (Dagger 接管 Earthly 用户，Dagger Cloud Team 免费 1 年 + 工程师 migration workshop) [Online]. Available: <https://dagger.io/blog/earthly-to-dagger-migration>

[17] Earthly, "A message about Earthly," Jul 2025. (Earthly Cloud 2025-07-16 关闭，Earthfile 主动维护终止；CEO 归因 "inability to monetize compute as a commodity") [Online]. Available: <https://earthly.dev/blog/shutting-down-earthfiles-cloud/>

[18] Garnix, "the nix CI," 2026. (Nix flake 原生 CI；intermediate build 全部上 cache 永不重建；比 GHA 上 Nix-CI 快 2–10×) [Online]. Available: <https://garnix.io/>

[19] Spacelift, "12 Most Popular CircleCI Alternatives to Consider in 2026," 2026. (CircleCI 多份对比报告列为可被 GHA + 第三方 runner 替代) [Online]. Available: <https://spacelift.io/blog/circleci-alternatives>

[20] Aviator, "Aviator MergeQueue vs. Mergify: A Comparison," 2026. (Aviator MergeQueue 用于 1000+ 工程师 monorepo 团队；Mergify Max plan $21/seat/月) [Online]. Available: <https://www.aviator.co/aviator-mergequeue-mergify>

[21] Mergify, "Automatic migration from autoqueue to auto_merge_conditions," May 2026. (2026-05-06 deprecation；Mergify 自动开 migration PR 重写配置) [Online]. Available: <https://docs.mergify.com/changelog/2026-05-06-automatic-migration-from-autoqueue-to-auto-merge-conditions/>
