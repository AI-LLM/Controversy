# 2026-05-14：SDLC 栈 / 代码索引与 RAG-for-code (D8.5) 层深度研究

> 系列子报告：软件开发栈 Pre-Coding-Agent vs Post-Coding-Agent。本篇仅覆盖 D8.5（代码索引 / RAG-for-code）。MCP（D6.6）单独成文，见 `10b-mcp.md`。范本：namespace.so 范式——挖本质，不堆现象。

这一层在 Pre-Agent 时代**不存在**。Pre-Agent 时代的"代码上下文获取"是开发者大脑里完成的：grep 一遍、按 F12 跳定义、Sourcegraph 搜一个符号、ctags 跳几下，**结果留在人的工作记忆里**。LLM 进场之后，工作记忆从人脑迁移到 context window 里，而 context window 容量有限、调用成本线性，于是必须有一个**"专门负责把对的代码片段在对的时刻喂给模型"的中间层**——这一层是 2023–2026 期间新增的。Sourcegraph 把它叫 RAG-for-code、Augment 叫 Context Engine、Greptile 叫 codebase graph、Cursor 内部就叫 codebase indexing。

## 1. Pre-Agent 时代的"代码上下文获取"长什么样

Pre-Agent 栈里，开发者获取"和我现在改的代码相关的其它代码"靠四件武器：

- **grep / ripgrep**：字面量、正则。准、但召回低、不懂语义（找 `getUser` 找不到 `fetchUser`）。
- **IDE find references / go-to-definition**：靠语言服务（LSP / SCIP），精确但只对**已建过索引的语言**有效，跨仓库瓶颈明显。
- **Sourcegraph 早期 code search**（2013 年由 Quinn Slack / Beyang Liu 创立 [[1]](https://en.wikipedia.org/wiki/Sourcegraph)）：本质是把 grep 和 LSP-类符号图扩到**组织级跨仓库**的产品 [[2]](https://sourcegraph.com/blog/anatomy-of-a-coding-assistant)。
- **ctags / cscope**：90 年代留下的符号索引，至今仍在 Linux 内核开发圈广泛使用。

这套体系的设定是"**人是检索者，工具是过滤器**"。人脑判断"哪个搜索结果相关"，工具只负责快。所有这一层的成功度量是"开发者每天 grep 几次"，没人会问"grep 把 token 分配得好不好"——因为没有 token。

## 2. Coding Agent 出现后，为什么必须长出 RAG-for-code

把 LLM 当编辑器副驾驶起，三个硬约束同时被踩到：

1. **Context window 装不下整个 codebase**。即使 Claude / GPT 类模型今天能上 200K–1M token（Claude Opus 4.6 / Sonnet 4.6 于 2026-03-13 起 1M GA [[3]](https://platform.claude.com/docs/en/build-with-claude/context-windows)，GPT-5.5 于 2026-04-23 起 API 1M [[4]](https://openai.com/index/introducing-gpt-5-5/)），一个真实的中型企业代码库（Augment 给出的口径是 400,000+ 文件 [[5]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)）也是 10⁸–10⁹ token 量级（⚠ 作者估算：400k 文件 × 平均 250 行 × 4 token/行 ≈ 4×10⁸ token）。线性塞不进去，强行长上下文也会"context rot"——模型注意力在长尾衰减 [[6]](https://www.sitepoint.com/long-context-vs-rag-1m-token-windows/)。
2. **Agent 不能每次都全文 grep**。Agent 比人慢：每个工具调用一次往返、一次推理。开放 `bash + ripgrep` 给 agent 是可行兜底（Claude Code / Cline 即走这条路 [[7]](https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing)），但任何能预先 narrow 的检索都能省下数量级的 token 和 latency。
3. **行为可控性需要"知道相关代码"**。让 agent 改一个函数前，**得让它先看到所有 call site**，否则改 API 就是制造 regression。这是工程纪律，不是性能优化。

结论：必须有一层"**在 prompt 之前**完成 codebase → 相关代码片段"映射的服务。

## 3. 新需求：实时索引 / 增量更新 / 多 repo / 隐私模式

Pre-Agent 时代的索引（ctags、Sourcegraph 早期 zoekt）只需要"每晚跑一次 cron"。Agent 时代把更新频率推到了**编辑保存级别**：

- **实时 / 增量索引**：文件保存后秒级生效，否则 agent 拿到的就是旧符号。Cursor 用 Merkle tree 做增量哈希——文件改变只重传变更分支，未变 chunk 复用 AWS 缓存 [[8]](https://towardsdatascience.com/how-cursor-actually-indexes-your-codebase/)。Augment 自报 180k 行 TS monorepo 首次索引 ≈ 4 分钟、增量更新 ≈ 40 秒 [[5]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)；400k+ 文件首次索引约 25 分钟 [[9]](https://www.augmentcode.com/context-engine)。
- **多 repo 联合检索**：Sourcegraph Cody 支持单次 query 跨最多 10 个 repo [[10]](https://sourcegraph.com/docs/cody)；Greptile 把整个组织级 repo 集合建一个统一的 code graph [[11]](https://www.greptile.com/blog/semantic-codebase-search)。Cursor 与 Augment 默认仍以单 workspace 为粒度。
- **隐私 / 数据驻留**：Cursor 仅把 embedding + 路径混淆后的元数据上传 Turbopuffer，源代码不离开开发机 [[12]](https://cursor.com/blog/secure-codebase-indexing)。Tabby、Continue.dev 走**全本地**路线，embedding 模型（如 `bge-large-en-v1.5`）跑在 Ollama 上、向量库本地 [[13]](https://docs.continue.dev/customize/custom-providers) [[14]](https://github.com/TabbyML/tabby)。监管行业（医疗、金融、国防）只接这条路线。
- **RBAC / 行级权限**：企业内不是所有开发者都该看到所有代码（M&A 隔离区、合规分区）。这件事 IDE 厂商不愿做，是 Sourcegraph / Augment 企业版的护城河。

## 4. 代表公司技术架构

代码索引架构基本可拆成三件套：**embedding（语义模糊匹配）+ AST / 符号图（精确定位）+ rerank（top-k 过滤）**。不同家在三件套上的配比不同。

### Sourcegraph Cody → Amp：经典 IR + 符号图

底层是 Sourcegraph 十年积累的 zoekt 代码搜索 + SCIP 代码图 + 向量 embedding 三结合 [[2]](https://sourcegraph.com/blog/anatomy-of-a-coding-assistant)。Cody 三段检索：embeddings search → code graph lookup（精确 find-refs / find-defs）→ rerank top-k [[10]](https://sourcegraph.com/docs/cody)。路线偏"**经典 IR 工程**"：相信稀疏检索 + 符号精确链接比纯向量更稳定。

**2025-07 战略转向**：Sourcegraph 在 2025-06-25 停止 Cody Free / Pro 新注册，2025-07-23 关闭 Free / Pro / Enterprise Starter 的 Cody 访问，全力推 Amp（原 Cody 升级为 agentic 工具，承诺 1M token+ 上下文）[[15]](https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans) [[16]](https://ampcode.com/)。**Cody Enterprise 保留并持续投资** [[15]](https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans)。这是典型的"放弃个人市场、All-in 企业 + agentic"的姿态——个人开发者已被 Cursor / Claude Code 端到端吞掉，Sourcegraph 的差异化只剩"组织级代码图"。

### Augment Code：大上下文 + 实时 Context Engine

累计融资 252M（Sutter Hill / Index / Lightspeed 领投 [[17]](https://www.augmentcode.com/blog/augment-inc-raises-227-million)）。Context Engine 不是单纯向量 RAG，而是 AST 解析 + 数据流分析 + 控制流图 + 语义 embedding + graph neural network 五件套并行 [[9]](https://www.augmentcode.com/context-engine)。它**给整个 codebase 建一个"语义依赖图"**，每次 query 从图上挑相关子集进 200K context window——关键是"**只塞需要的片段进去**"，不是"塞更多" [[18]](https://www.augmentcode.com/guides/mastering-ai-context-and-why-it-matters-more-than-token-count)。

2026-04，Augment 的 Auggie CLI 在 SWE-bench Pro 上拿到 51.80%，同一 Opus 4.5 模型下比 Cursor 多解 15 题、比 Claude Code 多解 17 题（共 731 题）[[19]](https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro)。这条数据是"上下文工程 > 模型本体"的当代最佳实证（⚠ 解读：同模型对比，Δ 只能归因于 context pipeline 与 agent 策略；Augment 自己即 frame 为前者贡献）。定价：Indie $20/mo、Standard $60/mo/dev、Max $200/mo/dev、Enterprise custom [[20]](https://checkthat.ai/brands/augment-code/pricing)。

### Greptile：docstring-of-AST + 代码图

Greptile 路线最有意思。它先**解析 AST，对每个节点递归生成 docstring（自然语言摘要），再对 docstring 做 embedding** [[11]](https://www.greptile.com/blog/semantic-codebase-search)。理由：query 是自然语言，code 是代码语法；query↔code 的相似度低于 query↔description 约 12 个百分点，所以把代码先翻译成自然语言再做向量检索召回率更高 [[11]](https://www.greptile.com/blog/semantic-codebase-search)。在 docstring embedding 之上叠一层**整 repo 的文件 / 函数 / 依赖图**，由 agent 集群在图上遍历相关性 [[21]](https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context)。2025-09 拿 Benchmark 领投的 $25M Series A，估值 180M [[22]](https://www.greptile.com/blog/series-a)。主战场是 PR 自动评审。

### Cursor：客户端 AST chunk + Merkle 同步 + Turbopuffer 向量库

Cursor 内建索引把文件按 AST 切 chunk（保证语法完整）、本地 embed、Merkle 哈希后只同步变更分支到 Turbopuffer 向量库 [[8]](https://towardsdatascience.com/how-cursor-actually-indexes-your-codebase/) [[12]](https://cursor.com/blog/secure-codebase-indexing)。文件路径走客户端混淆（每段路径用密钥 + nonce 掩码），云端只见 embedding + 混淆路径，不见源码 [[12]](https://cursor.com/blog/secure-codebase-indexing)。Embedding 按 chunk hash 缓存在 AWS，未变内容跨用户复用——这是 Cursor 把"几千万开发者机器的索引开销"摊薄的关键工程 trick。

### Continue.dev：开源 + 全本地嵌入 → 转向 agentic 探索

Continue.dev 早期主打 `@codebase` 上下文 provider：本地 embedding（Ollama + `bge-large-en-v1.5`），`nRetrieve` 控制召回数量、`nFinal` 控制传给模型的最终 chunk 数 [[13]](https://docs.continue.dev/customize/custom-providers)。**2026 起 `@Codebase` 上下文 provider 已 deprecated**，转向 agent 模式用内置 grep / glob / file-read 工具按需探索 [[23]](https://docs.continue.dev/guides/codebase-documentation-awareness)。Continue 是"open-source、self-hosted、air-gapped"的代表 [[24]](https://github.com/continuedev/continue)。

### Aider：tree-sitter + PageRank 符号图（无向量）

Aider 走**反主流**路线。不做 embedding：用 tree-sitter（130+ 语言）从源文件抽取定义和引用 tag，构造"符号定义 / 引用图"，然后跑 PageRank 选 token 预算内最相关的符号 [[25]](https://aider.chat/2023/10/22/repomap.html) [[26]](https://aider.chat/docs/repomap.html)。边权按提及的 identifier ×10、命名优良 identifier ×10、chat files ×50 加权。本质是"被 10 个函数调用的 public API 比只调一次的私有 helper 更值得放进上下文"——纯图论解 [[26]](https://aider.chat/docs/repomap.html)。

### Cline：故意不索引（agentic search）

Cline 旗帜鲜明地不做 RAG / embedding / 向量库 [[7]](https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing)。理由两条：(a) chunk 切代码会撕碎逻辑边界；(b) 持续维护 fresh index 在快速变动的 codebase 上是工程债。Cline 选择**运行时 agentic search**：agent 用 grep / glob / file-read 顺着 import 链按需读，一步推一步，类似人脑 [[7]](https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing)。Claude Code 走同一路线。这条路线随长上下文模型扩张性价比上升。

### Tabby：完全开源 + 本地 repository index

Apache 2.0、Rust 编写、本地 repository 索引 + FIM 补全 + chat + SSO，**所有能力包含在自托管免费版里**（无 paid feature gate）[[14]](https://github.com/TabbyML/tabby)。v0.30 起支持 GitLab MR 作为上下文 [[14]](https://github.com/TabbyML/tabby)。32K+ GitHub star，是隐私敏感场景"开源底盘"代表。

## 5. 路线分界线：什么时候哪条路赢

⚠ 以下三档分界线为作者综合估算，依据：Augment 自报 400k+ 文件为其设计上限 [[5]](https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai)、Sourcegraph 文档跨仓库 ≤10 repo 的硬限制 [[10]](https://sourcegraph.com/docs/cody)、"长上下文 vs RAG"经验法则——单仓库 ≤数万文件可直接长上下文兜底 [[6]](https://www.sitepoint.com/long-context-vs-rag-1m-token-windows/)；公开基准未给出精确门槛。

- **<50k 文件、单仓库**：agentic search（Cline / Claude Code）与传统 RAG（Cursor / Continue）差不多——任何方案都能在几秒内召回，差异不显著。1M 上下文模型让"全塞进去"成为可行兜底。
- **50k–400k 文件、多仓库 / monorepo**：Sourcegraph 的代码图 + 增量索引架构有十年优势；Augment 的 delta ingestion + GNN 也能跑，但调优深度还在追赶。这一档是 IDE 内建索引（Cursor）能开始吃力的地方。
- **>400k 文件、组织级、跨语言**：纯向量必然碎；纯符号图也会因为缺乏语义模糊匹配（"找到所有'鉴权相关'函数"）而召回不足。**事实上的赢家是"两边都做"**——Augment 在做符号图、Sourcegraph 在做更深的 embedding；殊途同归。

## 6. 几条本质判断

**判断 1：长上下文模型把"必须 RAG"的门槛推高了，但没有消灭 RAG**（⚠ 解读）**。** 1M token 让 ≤数万文件单仓库可以"全塞兜底"，但任何 10 年以上 SaaS / Google / Meta 级别的 codebase 都在分界线之上。代码索引层是结构性新增、不是过渡品。同时 Cline / Claude Code "agentic search 不索引"路线证明**长上下文 + 工具调用**确实可以**部分替代**预建索引——两条路线会长期并存，分界线随模型上下文成本下降逐年右移。

**判断 2：代码索引的真正护城河不是算法，是"接客户内网 + 不外泄代码 + 实时增量 + RBAC"四件脏活**（⚠ 解读，依据：Sourcegraph 砍 Cody Free/Pro 转推 Amp + 保留 Cody Enterprise [[15]](https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans)；Augment 拿 ISO/IEC 42001 认证 [[27]](https://www.augmentcode.com/tools/enterprise-multi-file-refactoring-why-ai-breaks-at-scale)；Tabby 全部能力开源自托管 [[14]](https://github.com/TabbyML/tabby)——三家在算法层差异有限，差异化集中在合规与部署形态）**。** 个人开发者用 Cursor / Claude Code 内建索引就够了；企业（>50k 文件、合规 + 数据驻留 + SSO）会继续买 Sourcegraph / Augment 这种专门产品。Sourcegraph 2025-07 砍 Cody Free / Pro 转推 Amp 即承认了这点：个人市场不打了，企业市场加倍下注。

**判断 3："上下文工程 > 模型本体"在 2026 已被 Augment 数据实证**（⚠ 解读，依据：[[19]](https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro) 同 Opus 4.5 模型下 Δ15–17 题）**。** 同一模型，不同的检索 / 排序 / 注入策略，下游解题率差 2–3 个百分点。这意味着代码索引层会从"成本中心"变成"性能护城河"——Augment 的 GNN + 数据流 + 控制流多层 fusion，与 Greptile 的"docstring-of-AST"是同一思路的两种实现：**让 embedding 看到的不是原始 code token，而是经过结构化抽取后的语义骨架**。

**判断 4：开源路线（Continue.dev / Tabby / Aider）短期不会被商业版吞掉**（⚠ 解读，依据：Continue 转向 agentic 工具 + Tabby 全功能开源 + Aider PageRank repo map 仍在迭代 [[23]](https://docs.continue.dev/guides/codebase-documentation-awareness) [[14]](https://github.com/TabbyML/tabby) [[26]](https://aider.chat/docs/repomap.html)）**。** 监管行业（医疗、金融、政府）的"代码不离开内网"硬要求 + 长尾自部署需求，给开源底盘留下了稳定生态位。但开源不会通向"赢家通吃"——三家加起来日活也远不及单家 Cursor（⚠ 估算，公开数据未披露开源工具的精确日活）。

## 信源

[1] Wikipedia contributors, "Sourcegraph," *Wikipedia*. (创立于 2013 年，创始人 Quinn Slack 与 Beyang Liu。) [Online]. Available: <https://en.wikipedia.org/wiki/Sourcegraph>

[2] Sourcegraph, "The anatomy of an AI coding assistant," *Sourcegraph Blog*, 2025. [Online]. Available: <https://sourcegraph.com/blog/anatomy-of-a-coding-assistant>

[3] Anthropic, "Context windows," *Claude API Docs*. (Opus 4.6/Sonnet 4.6 自 2026-03-13 起 1M 上下文 GA；默认 200K。) [Online]. Available: <https://platform.claude.com/docs/en/build-with-claude/context-windows>

[4] OpenAI, "Introducing GPT-5.5," *OpenAI Blog*, Apr. 2026. (API 1M 上下文，Codex 400K，发布于 2026-04-23。) [Online]. Available: <https://openai.com/index/introducing-gpt-5-5/>

[5] Augment Code, "Why 400k+ File Codebases Break Traditional AI," *Augment Code Guides*, 2026. (180k 行 TS monorepo：首次索引 ≈ 4 min，增量 ≈ 40 s。) [Online]. Available: <https://www.augmentcode.com/guides/why-400k-file-codebases-break-traditional-ai>

[6] C. Wood, "Long Context vs RAG: When 1M Token Windows Replace RAG," *SitePoint*, 2026. (长上下文 context rot 与 RAG 适用边界讨论。) [Online]. Available: <https://www.sitepoint.com/long-context-vs-rag-1m-token-windows/>

[7] Cline, "Why Cline Doesn't Index Your Codebase (And Why That's a Good Thing)," *Cline Blog*, 2026. (no RAG / no embeddings / no vector DB；agentic search 路线声明。) [Online]. Available: <https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing>

[8] Towards Data Science, "How Cursor Actually Indexes Your Codebase," 2026. (Merkle tree + Turbopuffer + AWS chunk hash 缓存。) [Online]. Available: <https://towardsdatascience.com/how-cursor-actually-indexes-your-codebase/>

[9] Augment Code, "Context Engine," *Augment Code Product*. (AST + 数据流 + 控制流 + 语义 embedding + GNN 五层融合；400k+ 文件首次索引约 25 分钟。) [Online]. Available: <https://www.augmentcode.com/context-engine>

[10] Sourcegraph, "Cody Documentation," *Sourcegraph Docs*. (embeddings + code graph + rerank 三段检索；跨仓库 ≤10 repo。) [Online]. Available: <https://sourcegraph.com/docs/cody>

[11] Greptile, "Codebases are uniquely hard to search semantically," *Greptile Blog*. (docstring-of-AST 路线；query↔description 比 query↔code 相似度高约 12pp。) [Online]. Available: <https://www.greptile.com/blog/semantic-codebase-search>

[12] Sourcegraph 误植 → Cursor, "Securely indexing large codebases," *Cursor Blog*. (路径混淆 + Turbopuffer + 源码不上云。) [Online]. Available: <https://cursor.com/blog/secure-codebase-indexing>

[13] Continue.dev, "Context Providers," *Continue Docs*. (`bge-large-en-v1.5` + Ollama；nRetrieve / nFinal 控制召回与最终注入数。) [Online]. Available: <https://docs.continue.dev/customize/custom-providers>

[14] TabbyML, "tabby," *GitHub*. (Apache 2.0；Rust；本地 repository index + FIM + SSO；v0.30 起支持 GitLab MR 作为上下文；无 paid tier。) [Online]. Available: <https://github.com/TabbyML/tabby>

[15] Sourcegraph, "Changes to Cody Free, Pro, and Enterprise Starter plans," *Sourcegraph Blog*, 2025. (2025-06-25 停止新注册；2025-07-23 关闭 Free / Pro / Enterprise Starter 的 Cody 访问；Cody Enterprise 保留。) [Online]. Available: <https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans>

[16] Sourcegraph, "Amp — an AI coding agent built by Sourcegraph," *ampcode.com*, 2026. (1M+ token 上下文；free tier 含 $10/day 用量。) [Online]. Available: <https://ampcode.com/>

[17] Augment Code, "Augment Inc. raises $227 Million," *Augment Code Blog*, 2024. (累计 252M 融资，Sutter Hill / Index / Lightspeed / Innovation Endeavors / Meritech。) [Online]. Available: <https://www.augmentcode.com/blog/augment-inc-raises-227-million>

[18] Augment Code, "Mastering AI Context — and why it matters more than token count," *Augment Code Guides*, 2026. [Online]. Available: <https://www.augmentcode.com/guides/mastering-ai-context-and-why-it-matters-more-than-token-count>

[19] Augment Code, "Auggie tops SWE-Bench Pro," *Augment Code Blog*, Apr. 2026. (Opus 4.5 同模型：Auggie 51.80%、Cursor 50.21%、Claude Code 49.75%、Codex 46.47%；731 题样本，Auggie 比 Cursor 多解 15 题、比 Claude Code 多解 17 题。) [Online]. Available: <https://www.augmentcode.com/blog/auggie-tops-swe-bench-pro>

[20] CheckThat.ai, "Augment Code Pricing 2026: Plans, Costs & TCO," 2026. (Indie $20、Standard $60/dev、Max $200/dev、Enterprise custom。) [Online]. Available: <https://checkthat.ai/brands/augment-code/pricing>

[21] Greptile, "Graph-based Codebase Context," *Greptile Docs*. (file / function / dependency 三层图 + agent swarm 遍历。) [Online]. Available: <https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context>

[22] Greptile, "Series A and Greptile v3," *Greptile Blog*, Sep. 2025. ($25M Series A by Benchmark；估值 180M。) [Online]. Available: <https://www.greptile.com/blog/series-a>

[23] Continue.dev, "How to Make Agent mode Aware of Codebases and Documentation," *Continue Docs*, 2026. (`@Codebase` provider deprecated；转向 agent 内置 grep / glob / file-read。) [Online]. Available: <https://docs.continue.dev/guides/codebase-documentation-awareness>

[24] continuedev, "continue," *GitHub*. (开源；VS Code / JetBrains；self-hosted / air-gapped。) [Online]. Available: <https://github.com/continuedev/continue>

[25] P. Gauthier, "Building a better repository map with tree sitter," *aider.chat*, Oct. 2023. (从 ctags 迁移到 tree-sitter；定义 + 引用 tag 抽取。) [Online]. Available: <https://aider.chat/2023/10/22/repomap.html>

[26] P. Gauthier, "Repository map," *aider docs*. (PageRank 选符号；130+ 语言；提及 identifier ×10、命名良好 ×10、chat files ×50 加权。) [Online]. Available: <https://aider.chat/docs/repomap.html>

[27] Augment Code, "Enterprise Multi-File Refactoring: Why AI Breaks at Scale," *Augment Code Tools*, 2026. (89% 多文件重构准确率；首家 ISO/IEC 42001 认证 AI 编码助手。) [Online]. Available: <https://www.augmentcode.com/tools/enterprise-multi-file-refactoring-why-ai-breaks-at-scale>
