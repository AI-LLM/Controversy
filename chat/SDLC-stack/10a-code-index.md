# 2026-05-14：SDLC 栈 / 代码索引与 RAG-for-code (D8.5) 层深度研究

代码索引层的核心是**embedding / 注入之前先把代码翻译成什么**。当 Claude Opus 4.6 / GPT-5.5 这类模型本体已经在 API 层被任何 agent 厂商等价调用、并且 1M 上下文也都开放（Anthropic 自 2026-03-13 GA [[1]](https://platform.claude.com/docs/en/build-with-claude/context-windows)、OpenAI 自 2026-04-23 GA [[2]](https://openai.com/index/introducing-gpt-5-5/)），下游解题率的拉开来自同一份源码语料的**结构化抽取竞赛 (structured-extraction race over code corpus)**：五家给出了五种"中间表示"——AST chunk、docstring、符号图、数据流图，或者干脆不抽取——下游召回质量与同模型 Δ 直接由此决定。

## 1. Pre-Agent 时代 vs Agent 时代的语料形态变化

Pre-Agent 栈里"代码上下文获取"的语料形态是**人脑工作记忆 + 静态符号索引**。开发者四件武器：

- **grep / ripgrep**：字面量、正则。准、召回低、不懂语义（找 `getUser` 找不到 `fetchUser`）。
- **IDE find references / go-to-definition**：靠 LSP / SCIP，精确但只对已建过索引的语言有效，跨仓库瓶颈明显。
- **Sourcegraph 早期 code search**（2013 年由 Quinn Slack / Beyang Liu 创立 [[3]](https://en.wikipedia.org/wiki/Sourcegraph)）：把 grep + LSP-类符号图扩到**组织级跨仓库**产品化 [[4]](https://sourcegraph.com/blog/anatomy-of-a-coding-assistant)。
- **ctags / cscope**：90 年代留下的符号索引，至今仍在 Linux 内核开发圈广泛使用。

这套体系的设定是"**人是检索者，工具是过滤器**"——人脑判断"哪个结果相关"，工具只负责快。成功度量是"开发者每天 grep 几次"，没人问"grep 把 token 分配得好不好"，因为没有 token。

Agent 时代踩到三个硬约束，迫使"语料形态"从人脑迁移到了 prompt：

1. **Context window 装不下整个 codebase**。即使今天能上 200K–1M token，一个真实企业代码库（Augment 给出的口径是 400,000+ 文件 [[5]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)）也在 10⁸–10⁹ token 量级（⚠ 作者估算：400k 文件 × 平均 250 行 × 4 token/行 ≈ 4×10⁸ token）。线性塞不进；强行长上下文会触发 context rot——注意力在长尾衰减 [[6]](https://www.sitepoint.com/long-context-vs-rag-1m-token-windows/)。
2. **Agent 不能每次都全文 grep**。Agent 比人慢：每次工具调用一次往返、一次推理。开放 `bash + ripgrep` 给 agent 是可行兜底（Claude Code / Cline 走此路 [[7]](https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing)），但任何能预先 narrow 的检索都能省下数量级 token 与 latency。
3. **行为可控性需要"知道相关代码"**。让 agent 改一个函数前，**必须先看到所有 call site**，否则改 API 就是制造 regression。这是工程纪律，不是性能优化。

被服务对象是 agent 本身——这一层服务的是 prompt 而不是用户屏幕。Sourcegraph 2025-06-25 停止 Cody Free/Pro 新注册、2025-07-23 关闭 Free/Pro/Enterprise Starter 的 Cody 访问、All-in 推 Amp 与 Cody Enterprise [[8]](https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans) [[9]](https://ampcode.com/)：个人代码搜索市场已被 Cursor / Claude Code 端到端吞掉，护城河落在企业语料的结构化能力 + 合规位。

## 2. 结构化抽取的五条路线

代码索引架构基本可拆成三件套：**embedding（语义模糊匹配）+ AST / 符号图（精确定位）+ rerank（top-k 过滤）**。但真正决定下游召回的是"**embedding 之前先把代码翻译成什么**"——下面五条路线在这一步分叉。

### 路线 A：docstring-of-AST（Greptile）

Greptile 先**解析 AST，对每个节点递归生成 docstring（自然语言摘要），再对 docstring 做 embedding** [[10]](https://www.greptile.com/blog/semantic-codebase-search)。理由直接：query 是自然语言，code 是代码语法；query↔code 的相似度低于 query↔description 约 12 个百分点，所以把代码先翻译成自然语言再做向量检索召回率更高 [[10]](https://www.greptile.com/blog/semantic-codebase-search)。在 docstring embedding 之上叠一层**整 repo 的文件 / 函数 / 依赖图**，由 agent 集群在图上遍历相关性 [[11]](https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context)。2025-09 拿 Benchmark 领投的 $25M Series A，估值 180M [[12]](https://www.greptile.com/blog/series-a)。主战场 PR 自动评审。

⚠ 解读：这条路线赌的是"自然语言到自然语言的检索更稳"。代价是**索引时间 × LLM 调用费**——每个 AST 节点都得调一次模型生成 docstring。这把"索引成本"做成了 LLM-bound 操作而非 CPU-bound。

### 路线 B：GNN + 数据流（Augment）

Context Engine 不是单纯向量 RAG，而是 AST 解析 + 数据流分析 + 控制流图 + 语义 embedding + graph neural network 五件套并行 [[13]](https://www.augmentcode.com/context-engine)。它**给整个 codebase 建一个"语义依赖图"**，每次 query 从图上挑相关子集进 context window——关键是"**只塞需要的片段进去**"而不是"塞更多" [[14]](https://www.augmentcode.com/guides/mastering-ai-context-and-why-it-matters-more-than-token-count)。

工程指标：180k 行 TS monorepo 首次索引 ≈ 4 分钟、增量 ≈ 40 秒 [[5]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)；400k+ 文件首次索引约 25 分钟 [[13]](https://www.augmentcode.com/context-engine)；多文件重构 89% 准确率，首家拿到 ISO/IEC 42001 认证 [[15]](https://www.augmentcode.com/tools/enterprise-multi-file-refactoring-why-ai-breaks-at-scale)。累计融资 252M，Sutter Hill / Index / Lightspeed 领投 [[16]](https://www.augmentcode.com/blog/augment-inc-raises-227-million)。定价 Indie $20/mo、Standard $60/mo/dev、Max $200/mo/dev、Enterprise custom [[17]](https://checkthat.ai/brands/augment-code/pricing)。

### 路线 C：PageRank 符号图（Aider）

Aider 走**反主流**路线。不做 embedding：用 tree-sitter（130+ 语言）从源文件抽取定义和引用 tag，构造"符号定义 / 引用图"，然后跑 PageRank 选 token 预算内最相关的符号 [[18]](https://aider.chat/2023/10/22/repomap.html) [[19]](https://aider.chat/docs/repomap.html)。边权按提及的 identifier ×10、命名良好 identifier ×10、chat files ×50 加权 [[19]](https://aider.chat/docs/repomap.html)。本质是"被 10 个函数调用的 public API 比只调一次的私有 helper 更值得放进上下文"——纯图论解。

⚠ 解读：Aider 路线最便宜（不调任何模型做索引），但召回上限受限于"被引用次数 = 重要度"这个先验——对于新增 / 重构场景里"几乎没被引用但马上要改的代码"会被打分压低。

### 路线 D：AST chunk + Merkle 同步（Cursor）

Cursor 内建索引把文件按 AST 切 chunk（保证语法完整），本地 embed，Merkle 哈希后只同步变更分支到 Turbopuffer 向量库 [[20]](https://towardsdatascience.com/how-cursor-actually-indexes-your-codebase/) [[21]](https://cursor.com/blog/secure-codebase-indexing)。文件路径走客户端混淆（每段路径用密钥 + nonce 掩码），云端只见 embedding + 混淆路径，不见源码 [[21]](https://cursor.com/blog/secure-codebase-indexing)。Embedding 按 chunk hash 缓存在 AWS，未变内容跨用户复用——这是 Cursor 把"几千万开发者机器的索引开销"摊薄的关键工程 trick。

⚠ 解读：这是最"主流"也最朴素的路线——把抽取做到 AST chunk 粒度就停，剩下交给 embedding 模型。胜在简单、便宜、可扩；输于多文件重构与跨仓库语义。

### 路线 E：不抽取，纯 agentic search（Cline / Claude Code）

Cline 旗帜鲜明地不做 RAG / embedding / 向量库 [[7]](https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing)。理由两条：(a) chunk 切代码会撕碎逻辑边界；(b) 持续维护 fresh index 在快速变动的 codebase 上是工程债。Cline 选择**运行时 agentic search**：agent 用 grep / glob / file-read 顺着 import 链按需读，一步推一步，类似人脑 [[7]](https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing)。Claude Code 走同一路线。这条路线随长上下文模型扩张性价比上升——把"抽取"延后到运行时，由模型自己决定要看什么。

### 路线 F（兜底 / 经典 IR）：Sourcegraph Cody → Amp

底层是 Sourcegraph 十年积累的 zoekt 代码搜索 + SCIP 代码图 + 向量 embedding 三结合 [[4]](https://sourcegraph.com/blog/anatomy-of-a-coding-assistant)。Cody 三段检索：embeddings search → code graph lookup（精确 find-refs / find-defs）→ rerank top-k [[22]](https://sourcegraph.com/docs/cody)。路线偏"**经典 IR 工程**"：相信稀疏检索 + 符号精确链接比纯向量更稳定。2025-07 战略转向后，Cody Free / Pro / Enterprise Starter 关闭，Cody Enterprise 保留并持续投资，全力推 Amp（agentic 工具，承诺 1M token+ 上下文）[[8]](https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans) [[9]](https://ampcode.com/)。这是承认"个人市场已被吞，企业市场加倍下注"。

### 开源底盘的位置（Continue.dev / Tabby）

Continue.dev 早期主打 `@codebase` 上下文 provider：本地 embedding（Ollama + `bge-large-en-v1.5`），`nRetrieve` 控制召回数、`nFinal` 控制最终注入数 [[23]](https://docs.continue.dev/customize/custom-providers)。**2026 起 `@Codebase` provider 已 deprecated**，转向 agent 模式用内置 grep / glob / file-read 工具按需探索 [[24]](https://docs.continue.dev/guides/codebase-documentation-awareness)。Continue 是"open-source、self-hosted、air-gapped"代表 [[25]](https://github.com/continuedev/continue)。Tabby Apache 2.0、Rust 编写、本地 repository 索引 + FIM + chat + SSO，所有能力包含在自托管免费版里，v0.30 起支持 GitLab MR 作为上下文 [[26]](https://github.com/TabbyML/tabby)。Continue 的演化方向（embedding provider → agentic）实际是从"路线 D"切到"路线 E"。

## 3. 召回质量 × 新鲜度 × 合规位的三维变量

抽取策略选定后，落地到产品的差异化由三个维度联合决定。

**召回质量** = 中间表示与 query 的语义贴合度。docstring-of-AST 与 GNN + 数据流通常召回最高（中间表示已经携带语义），AST chunk 居中，PageRank 符号图在"已被使用的核心代码"场景高、在"新增 / 边缘代码"场景低，纯 agentic 无召回前置——靠模型自己 grep。

**新鲜度** = 索引滞后。Pre-Agent 时代索引（ctags、Sourcegraph 早期 zoekt）只需"每晚 cron 一次"；Agent 时代把更新频率推到**编辑保存级别**：Cursor 用 Merkle tree 做增量哈希——文件改变只重传变更分支，未变 chunk 复用 AWS 缓存 [[20]](https://towardsdatascience.com/how-cursor-actually-indexes-your-codebase/)；Augment 自报 180k 行 monorepo 增量 ≈ 40 秒 [[5]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)。docstring-of-AST 路线的新鲜度天然差——每次变更都要重调模型生成摘要。

**合规位** = 隐私 / 数据驻留 / RBAC / 多 repo 联合检索。Cursor 仅把 embedding + 路径混淆后的元数据上传 Turbopuffer，源码不离开开发机 [[21]](https://cursor.com/blog/secure-codebase-indexing)。Tabby、Continue 走**全本地**路线，embedding 模型跑在 Ollama 上、向量库本地 [[23]](https://docs.continue.dev/customize/custom-providers) [[26]](https://github.com/TabbyML/tabby)，监管行业（医疗、金融、国防）只接这条路线。Sourcegraph Cody 支持单次 query 跨最多 10 个 repo [[22]](https://sourcegraph.com/docs/cody)；Greptile 把整个组织级 repo 集合建一个统一 code graph [[10]](https://www.greptile.com/blog/semantic-codebase-search)。RBAC / 行级权限是 Sourcegraph / Augment 企业版的护城河——M&A 隔离区、合规分区这种"不是所有开发者都该看到所有代码"的需求，IDE 厂商不愿做。

⚠ 解读：三维之间存在 trade-off。docstring-of-AST 拿召回，输新鲜度；纯本地拿合规，输召回（本地嵌入模型质量天然落后于云端最优）；Cursor AST chunk 取了"性价比折中"，合规与召回都中等。

## 4. 同模型 Δ 实证：抽取策略的硬证据

2026-04，Augment Auggie CLI 在 SWE-bench Pro 上 51.80%，同一 Opus 4.5 模型下比 Cursor 多解 15 题、比 Claude Code 多解 17 题、比 Codex 多解 38 题（731 题样本）[[27]](https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro)。具体：Auggie 51.80% / Cursor 50.21% / Claude Code 49.75% / Codex 46.47% [[27]](https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro)。

⚠ 解读：同模型对比，模型本身 = 0 贡献，下游 Δ 全部归因于 agent 策略 + context pipeline。Augment 自己 frame 为前者贡献。换算：~2 个百分点 Δ ≈ 15 题，意味着**抽取策略的差异在 SWE-bench Pro 这种"多文件 / 跨函数 / 复杂依赖"的题集上稳定换算成 1.5–2% 的解题率**。这是"上下文工程 > 模型本体"在 2026 的当代最佳实证。Augment 的 GNN + 数据流 + 控制流多层 fusion，与 Greptile 的"docstring-of-AST"是同一思路的两种实现：**让 embedding 看到的不是原始 code token，而是经过结构化抽取后的语义骨架**。

为什么这个 Δ 不会被长上下文消灭：1M 上下文在题面 < 1M token 的题目上确实让"全塞兜底"成为可行兜底，但 SWE-bench Pro 这类题集刻意挑选了**跨 50+ 文件、需要找到 3–10 个真正相关函数**的题目；这种题目的难点不在窗口大小，在"能不能选对要塞的那 5 个函数"。结构化抽取的优势恰恰在选取，不在容量。

## 5. 长上下文右移分界线，但抽取层是结构性留存

⚠ 以下三档分界线为作者综合估算，依据：Augment 自报 400k+ 文件为其设计上限 [[5]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)、Sourcegraph 文档跨仓库 ≤10 repo 的硬限制 [[22]](https://sourcegraph.com/docs/cody)、"长上下文 vs RAG"经验法则——单仓库 ≤数万文件可直接长上下文兜底 [[6]](https://www.sitepoint.com/long-context-vs-rag-1m-token-windows/)；公开基准未给出精确门槛。

- **<50k 文件、单仓库**：agentic search（Cline / Claude Code）与传统 RAG（Cursor / Continue）差不多——任何方案都能在几秒内召回。1M 上下文（Claude Opus 4.6 / Sonnet 4.6 自 2026-03-13 GA [[1]](https://platform.claude.com/docs/en/build-with-claude/context-windows)、GPT-5.5 自 2026-04-23 GA [[2]](https://openai.com/index/introducing-gpt-5-5/)）让"全塞兜底"成为可行替代。
- **50k–400k 文件、多仓库 / monorepo**：Sourcegraph 的代码图 + 增量索引架构有十年优势；Augment 的 delta ingestion + GNN 也能跑。这一档是 IDE 内建索引（Cursor）开始吃力的地方。
- **>400k 文件、组织级、跨语言**：纯向量必然碎；纯符号图也会因缺乏语义模糊匹配（"找到所有'鉴权相关'函数"）而召回不足。**事实上的赢家是"两边都做"**——Augment 在做符号图、Sourcegraph 在做更深 embedding；殊途同归。

**核心判断 1：长上下文把"必须 RAG"门槛右移，但没有消灭抽取层**（⚠ 解读）。1M token 让 ≤数万文件单仓库可"全塞兜底"，但 10 年以上 SaaS / Google / Meta 级别 codebase 都在分界线之上。代码索引层是结构性新增、不是过渡品。Cline / Claude Code "agentic search 不索引"路线证明**长上下文 + 工具调用**确实能**部分替代**预建索引——两条路线长期并存，分界线随模型上下文成本下降逐年右移。

**核心判断 2：抽取策略的硬证据已落地**（⚠ 解读，依据 [[27]](https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro) 同 Opus 4.5 模型下 Δ15–17 题）。当模型本体趋同，下游 Δ 来自 context pipeline；这意味着代码索引层从"成本中心"变成"性能护城河"。GNN + 数据流（Augment）、docstring-of-AST（Greptile）、PageRank 符号图（Aider）、AST chunk（Cursor）、不抽取（Cline）——五条路线本质都在回答同一个问题，并把答案物化为产品。

**核心判断 3：真正护城河是合规位 + 实时增量 + RBAC + 数据驻留**（⚠ 解读，依据：Sourcegraph 砍 Cody Free/Pro 转推 Amp + 保留 Cody Enterprise [[8]](https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans)；Augment 拿 ISO/IEC 42001 认证 [[15]](https://www.augmentcode.com/tools/enterprise-multi-file-refactoring-why-ai-breaks-at-scale)；Tabby 全部能力开源自托管 [[26]](https://github.com/TabbyML/tabby)）。三家在抽取算法层差异有限，差异化集中在合规与部署形态。个人开发者用 Cursor / Claude Code 内建索引就够；企业（>50k 文件、合规 + 数据驻留 + SSO）会继续买 Sourcegraph / Augment 这种专门产品。

**核心判断 4：开源路线短期不会被吞掉**（⚠ 解读，依据：Continue 转向 agentic + Tabby 全功能开源 + Aider PageRank repo map 持续迭代 [[24]](https://docs.continue.dev/guides/codebase-documentation-awareness) [[26]](https://github.com/TabbyML/tabby) [[19]](https://aider.chat/docs/repomap.html)）。监管行业（医疗、金融、政府）的"代码不离开内网"硬要求 + 长尾自部署需求，给开源底盘留下稳定生态位。但开源不会通向"赢家通吃"——三家加起来日活远不及单家 Cursor（⚠ 估算，公开数据未披露开源工具的精确日活）。

## 信源

[1] Anthropic, "Context windows," *Claude API Docs*. (Opus 4.6/Sonnet 4.6 自 2026-03-13 起 1M 上下文 GA；默认 200K。) [Online]. Available: <https://platform.claude.com/docs/en/build-with-claude/context-windows>

[2] OpenAI, "Introducing GPT-5.5," *OpenAI Blog*, Apr. 2026. (API 1M 上下文，Codex 400K，发布于 2026-04-23。) [Online]. Available: <https://openai.com/index/introducing-gpt-5-5/>

[3] Wikipedia contributors, "Sourcegraph," *Wikipedia*. (创立于 2013 年，创始人 Quinn Slack 与 Beyang Liu。) [Online]. Available: <https://en.wikipedia.org/wiki/Sourcegraph>

[4] Sourcegraph, "The anatomy of an AI coding assistant," *Sourcegraph Blog*, 2025. [Online]. Available: <https://sourcegraph.com/blog/anatomy-of-a-coding-assistant>

[5] Augment Code, "Why 400k+ File Codebases Break Traditional AI," *Augment Code Guides*, 2026. (180k 行 TS monorepo：首次索引 ≈ 4 min，增量 ≈ 40 s。) [Online]. Available: <https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai>

[6] C. Wood, "Long Context vs RAG: When 1M Token Windows Replace RAG," *SitePoint*, 2026. (长上下文 context rot 与 RAG 适用边界讨论。) [Online]. Available: <https://www.sitepoint.com/long-context-vs-rag-1m-token-windows/>

[7] Cline, "Why Cline Doesn't Index Your Codebase (And Why That's a Good Thing)," *Cline Blog*, 2026. (no RAG / no embeddings / no vector DB；agentic search 路线声明。) [Online]. Available: <https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing>

[8] Sourcegraph, "Changes to Cody Free, Pro, and Enterprise Starter plans," *Sourcegraph Blog*, 2025. (2025-06-25 停止新注册；2025-07-23 关闭 Free / Pro / Enterprise Starter 的 Cody 访问；Cody Enterprise 保留。) [Online]. Available: <https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans>

[9] Sourcegraph, "Amp — an AI coding agent built by Sourcegraph," *ampcode.com*, 2026. (1M+ token 上下文；free tier 含 $10/day 用量。) [Online]. Available: <https://ampcode.com/>

[10] Greptile, "Codebases are uniquely hard to search semantically," *Greptile Blog*. (docstring-of-AST 路线；query↔description 比 query↔code 相似度高约 12pp。) [Online]. Available: <https://www.greptile.com/blog/semantic-codebase-search>

[11] Greptile, "Graph-based Codebase Context," *Greptile Docs*. (file / function / dependency 三层图 + agent swarm 遍历。) [Online]. Available: <https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context>

[12] Greptile, "Series A and Greptile v3," *Greptile Blog*, Sep. 2025. ($25M Series A by Benchmark；估值 180M。) [Online]. Available: <https://www.greptile.com/blog/series-a>

[13] Augment Code, "Context Engine," *Augment Code Product*. (AST + 数据流 + 控制流 + 语义 embedding + GNN 五层融合；400k+ 文件首次索引约 25 分钟。) [Online]. Available: <https://www.augmentcode.com/context-engine>

[14] Augment Code, "Mastering AI Context — and why it matters more than token count," *Augment Code Guides*, 2026. [Online]. Available: <https://www.augmentcode.com/guides/mastering-ai-context-and-why-it-matters-more-than-token-count>

[15] Augment Code, "Enterprise Multi-File Refactoring: Why AI Breaks at Scale," *Augment Code Tools*, 2026. (89% 多文件重构准确率；首家 ISO/IEC 42001 认证 AI 编码助手。) [Online]. Available: <https://www.augmentcode.com/tools/enterprise-multi-file-refactoring-why-ai-breaks-at-scale>

[16] Augment Code, "Augment Inc. raises $227 Million," *Augment Code Blog*, 2024. (累计 252M 融资，Sutter Hill / Index / Lightspeed / Innovation Endeavors / Meritech。) [Online]. Available: <https://www.augmentcode.com/blog/augment-inc-raises-227-million>

[17] CheckThat.ai, "Augment Code Pricing 2026: Plans, Costs & TCO," 2026. (Indie $20、Standard $60/dev、Max $200/dev、Enterprise custom。) [Online]. Available: <https://checkthat.ai/brands/augment-code/pricing>

[18] P. Gauthier, "Building a better repository map with tree sitter," *aider.chat*, Oct. 2023. (从 ctags 迁移到 tree-sitter；定义 + 引用 tag 抽取。) [Online]. Available: <https://aider.chat/2023/10/22/repomap.html>

[19] P. Gauthier, "Repository map," *aider docs*. (PageRank 选符号；130+ 语言；提及 identifier ×10、命名良好 ×10、chat files ×50 加权。) [Online]. Available: <https://aider.chat/docs/repomap.html>

[20] Towards Data Science, "How Cursor Actually Indexes Your Codebase," 2026. (Merkle tree + Turbopuffer + AWS chunk hash 缓存。) [Online]. Available: <https://towardsdatascience.com/how-cursor-actually-indexes-your-codebase/>

[21] Cursor, "Securely indexing large codebases," *Cursor Blog*. (路径混淆 + Turbopuffer + 源码不上云。) [Online]. Available: <https://cursor.com/blog/secure-codebase-indexing>

[22] Sourcegraph, "Cody Documentation," *Sourcegraph Docs*. (embeddings + code graph + rerank 三段检索；跨仓库 ≤10 repo。) [Online]. Available: <https://sourcegraph.com/docs/cody>

[23] Continue.dev, "Context Providers," *Continue Docs*. (`bge-large-en-v1.5` + Ollama；nRetrieve / nFinal 控制召回与最终注入数。) [Online]. Available: <https://docs.continue.dev/customize/custom-providers>

[24] Continue.dev, "How to Make Agent mode Aware of Codebases and Documentation," *Continue Docs*, 2026. (`@Codebase` provider deprecated；转向 agent 内置 grep / glob / file-read。) [Online]. Available: <https://docs.continue.dev/guides/codebase-documentation-awareness>

[25] continuedev, "continue," *GitHub*. (开源；VS Code / JetBrains；self-hosted / air-gapped。) [Online]. Available: <https://github.com/continuedev/continue>

[26] TabbyML, "tabby," *GitHub*. (Apache 2.0；Rust；本地 repository index + FIM + SSO；v0.30 起支持 GitLab MR 作为上下文；无 paid tier。) [Online]. Available: <https://github.com/TabbyML/tabby>

[27] Augment Code, "Auggie tops SWE-Bench Pro," *Augment Code Blog*, Apr. 2026. (Opus 4.5 同模型：Auggie 51.80%、Cursor 50.21%、Claude Code 49.75%、Codex 46.47%；731 题样本，Auggie 比 Cursor 多解 15 题、比 Claude Code 多解 17 题。) [Online]. Available: <https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro>
