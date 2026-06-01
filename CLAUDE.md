# Controversy — 每日研究笔记

用户每天往这个仓库里沉淀想法的库。**条目类型不固定**，可能是：

- **新闻研究**：当天的 AI / 科技热点，需要搜英文一手信源、交叉核对
- **想法 / 观点**：用户分享的 idea、立场、半成品论证，让我帮忙整理或扩写
- **素材整理**：用户扔过来的链接、代码片段、对话稿，让我归档或加工
- **混合体**：以上几种叠加

每次 session 一开始要先判断**这次是哪一类**，再选模板。不要默认所有条目都按"新闻"格式来。

## 目录结构

- `chat/` — 用户从 claude.ai 导出的对话稿、其他来源的素材，文件名通常含 `(YYYY-MM-DD)`
- `news/` — 每天一篇或多篇笔记，命名 `YYYY-MM-DD-slug.md`。slug 用主体关键词的小写英文短横线形式。
  - 名字虽然叫 news，但容纳所有类型的条目（暂不拆分目录，太碎）
- `README.md` — 索引表，按日期倒序追加。表格的"主题"列要一眼看出是新闻、想法还是其他

## 通用工作流

1. **先弄清楚用户给的是什么**：
   - 指明的 `chat/` 文件？读它，但要分清这是背景资料、用户原话、还是素材
   - 链接 / 代码片段？当作素材保留原貌，不要擅自重写
   - 让我写一段文字？先确认我已经理解他的立场，不要自由发挥
2. **判断条目类型**：新闻、想法、素材，还是混合
3. **如果包含事实声明**（人名、日期、数字、产品发布）：必须验证或问用户。不编造。
4. **写到 `news/YYYY-MM-DD-slug.md`**，用对应模板（见下）
5. **更新 `README.md` 索引表**：在表格顶部加一行，主题列里点明类型

## 网络搜索语言

默认用**英文**关键词搜索——英文一手信源覆盖面广、噪声少。

**例外**：搜索对象是**中国本土实体**（公司 / 产品 / 人名 / 政策 / 平台 / 微信公众号等）时用中文，因为这些实体的一手语境在中文。双语都有的情况（华为 Ascend / DeepSeek / Qwen / 智谱 / 字节…）：先英文，再补中文交叉核对。

## 模板：新闻研究

适用于"今天 X 发生了 Y"类条目。

- `# YYYY-MM-DD：一句话标题`（带钩子）
- 第一段：核心事实 + 关键数字 + 历史对比
- `## 当事人各自的主张`：每方一条 bullet
- `## 这条新闻的意义`：3–4 点编号列表
- `## 相关资料`：链向 `chat/` 下相关对话稿
- `## 信源`：英文标题 + URL，官方源在前

## 模板：想法 / 观点

适用于"用户分享了一个 idea，让我整理 / 扩写"。

- `# YYYY-MM-DD：一句话点题`
- `## 用户的核心立场`：用户原话或忠实复述，**不要替他下结论**
- `## 展开`：按用户希望的方向扩写——论证、反例、引申、对照。结构由内容决定，不强求章节
- `## 相关链接 / 素材`：用户提供的链接、代码片段、引文，原样保留
- 写完后**回到用户确认**：这个表达是否符合他的意图，再考虑是否补充

## 模板：素材归档

适用于"用户扔了一堆东西，让我存下来 + 简单加工"。

- 标题点明素材性质
- 一段话说明素材来源、用户备注、为什么收藏
- 素材原文（链接 / 代码 / 引文），加最小化的注解
- 不要"总结"成另一种东西——归档就是归档

## 方法：IBIS 论证图

用户要求"用 IBIS 方法画图""把论证结构画出来"时用这套。IBIS（Issue-Based Information System）把一篇文章／一场争论拆成**议题 — 立场 — 论据**三类节点，用 Mermaid 图呈现。适用于给观点稠密的文章做结构化重构，或并入用户的反方质疑做多空对照。它是**对原文论证的重构**，不是原文自身的章节划分——图前要加一句 `⚠ 说明：IBIS 拆解是本人对原文论证结构的重构方式，并非原文章节`。

### 三类节点 + 极性在边上（核心原则）

- **IS{n}·议题 Issue**（蓝色六边形 `{{...}}`）：待回答的问题。
- **PO{n}·立场 Position**（橙色圆角框 `(...)`）：对某议题的回答／主张。一个议题下可挂多个**竞争立场**（并列候选答案）。
- **AR{n}·论据 Argument**（灰色矩形 `[...]`）：**内容中立的事实陈述，本身不含立场**。
- **关键：支持／反对是边的属性，不是节点的属性。** 同一条论据可以对一个立场是支持、对另一个立场是反对——这种"一身二任"的论据必须建成**一个 AR 节点 + 两条不同极性的边**，不要拆成两个重复节点。（典型：Solow 悖论/统计滞后先例，既支持"价值隐形"又反对"确实没产出"。）

### 边的类型（遵循 IBIS／gIBIS 语法，关系写在边标签上）

只允许以下关系，**别自创**：

- `PO -- 回应 --> IS`：立场**回应**议题（Position responds-to Issue）。同一议题下的并列候选答案都用它指回该议题——不要用无标签 `IS --> PO`。
- `AR -- 支持 --> PO` / `AR -- 反对 --> PO`：论据**支持／反对**立场（Argument supports／objects-to Position）。
- `IS -. 源自 .-> PO`：议题**由某立场引出**（Issue is-suggested-by Position／Issue／Argument）。
- `IS -. 质疑 .-> PO`：议题**质疑**某立场／论据（Issue questions）。
- `IS == specializes ==> IS`：议题间 generalize／specialize／replace。

**两条硬约束（来自 IBIS 语法，常踩的坑）**：

1. **Position 与 Issue 之间只有 `responds-to` 一种关系**——不存在「立场派生议题」。子议题要用 `IS -. 源自 .-> PO`（议题 is-suggested-by 立场），方向是议题指向立场，不是反过来。
2. **论据只连立场**（支持／反对），**不直接连另一条论据**。要表达「论据 A 削弱论据 B」，改写成 A 对 B 所支撑的那个立场的「反对」边（并在正文注明它专门针对 B），或另立一个 `质疑` 该论据的议题。

仍然成立的核心原则：**支持／反对是边的属性，不是节点的属性**。同一条论据可对一个立场支持、对另一个立场反对——必须建成**一个 AR 节点 + 两条不同极性的边**，不要拆成两个重复节点。（典型：Solow 悖论/统计滞后先例，既支持"价值隐形"又反对"确实没产出"。）

### ID 与图文对照

- ID 用类型前缀 + **全图唯一、按出现顺序递增**的序号（IS1、PO1、AR1…）。删节点后要重排，保证序号连续无空缺。
- **图内每个节点标签以自己的 ID 开头**（如 `AR9 历史先例：Solow 悖论…`），渲染出来即可对号。
- **图外正文每条详解前加 `【ID】`**；论据条目还要标出它在图中连出的极性边，格式 `【AR9｜支持 PO1·反对 PO15】`。正文里交叉引用也用 ID（"AR22 专门针对 AR16 的推断""见 PO15 一节"）。
- 次要的、不进图的旁证显式标注"（图中从略）"，不硬塞 ID，保持图文 1:1。

### Mermaid 骨架

```mermaid
---
config:
  layout: elk
---
graph TD
    classDef issue fill:#e7f0fb,stroke:#1565c0,stroke-width:2px,color:#0d3c78;
    classDef position fill:#fff6e0,stroke:#e08e0b,stroke-width:2px,color:#6b4a08;
    classDef argument fill:#f0f0f0,stroke:#777,stroke-width:1px,color:#333;
```

节点定义后跟 `:::issue` / `:::position` / `:::argument` 指定类型。`layout: elk` 用 ELK 引擎排版——节点多、交叉边多（论据一身二任时尤甚）时布局更清晰。

### 收尾必做

- **每次改完图都用 mermaid-cli 渲染校验语法**：`npx -y @mermaid-js/mermaid-cli@latest -i <file> -o /tmp/x.svg`，确认输出 `✅` 后删掉临时 svg（含工作目录里生成的 `x-1.svg`）。
- 多张图能合并就合并成一张（竞争立场挂同一个议题，比单独建"反向议题"更准）。
- 用脚本核对节点计数与序号连续性，并 grep 确认无旧 ID 残留。

## 风格规范（所有模板通用）

- 中文正文，专有名词保留原文（METR / Time Horizons / Project Glasswing 等）
- 不用 emoji
- 不写"总结"或"结语"段
- 数字要精确（"16 小时（95% CI 8.5–55h）"，不写"大约十几个小时"）
- 区分**事实**（带信源）和**解读**（自己或用户的分析）
- 用户原话优先保留，**不要美化或软化他的语气**——这个库的名字叫 Controversy，不是 Balanced View
- 代码片段保留原始格式，不要为了美观重排

### md 正文只保留结果，不保留修改过程

md 文件应当作为**最终成品**呈现给读者，**修改史不留正文**。下列内容应在 Claude Code 对话里反馈给用户，**不要写进 md**：

- 日期版本标记："（5/14 修订）"、"（5/14 补）"、"二轮重写"、"补充层"、"已扩充"、"已升级"
- 修改史叙事："本篇按 X 重写"、"原版用 X 框架，现在改为 Y"、"系列说明：namespace.so 是 CI/CD 层的样本... 本篇..."
- 拒绝替代方案的辩护：如"为什么不是流量框架"、"为什么不是单独一层"——读者不需要知道作者考虑过什么并拒绝，直接呈现结论即可
- 第一人称作者叙事："我们重写"、"我重新组织"、"作者预设的 lens 是..."
- 跨文件历史引用："5/14 补充的 X 已合并入此文"、"参考诊断 subagent 的建议"

**应当保留**：分析框架本身（lens 是什么、为什么这个 lens 准确，但**不引用前版本或外部 lens 作对比**）、所有数据点、所有引用、章节结构、本质判断、⚠ 估算 / 解读标注。

判断方法：**想象一个第一次看这份文件的读者**——他需要看到结论 + 论证 + 数据；不需要知道作者经过了几轮修改、考虑过哪些备选 lens、引用过哪个 subagent 的建议。元叙事统统压到 Claude Code 对话窗口里告诉我。

### 引用规范（IEEE 风格）

- 行内：`[N]` 数字方括号；并列 `[N], [M]`。
- **正文中的 `[N]` 一律渲染为指向出处 URL 的超链接**，格式 `[[N]](URL)`；URL 取自参考文献条目里 `Available: <URL>` 的部分。无 URL 的条目（书籍、纸刊未上网者）正文里保留纯 `[N]`。
- **一个段落多个论点时，每个论点至少配一条引用**，不要堆一行 `[N]` 在末尾。
- 每个markdown文件引用编号**独立从 `[1]` 开始**，严格递增。
- 找不到直接证据时：用相邻领域类比并显式声明：

  > ⚠ **声明**：本节判断是从 X 类比推断，仍需面向 Y 做实证评估。

- 条目格式：
  ```
  [N] Authors, "Title," *Venue*, vol., no., pp., Month Year. [Online]. Available: <URL>
  ```
- arXiv：
  ```
  [N] X. Y et al., "Title," *arXiv preprint*, arXiv:NNNN.NNNNN, MMM YEAR. [Online]. Available: <https://arxiv.org/abs/NNNN.NNNNN>
  ```
- 当引用支撑了**具体数字**，把数字写进条目末尾的括号注释（方便读者抽查）：
  ```
  [18] Xia et al., "...", IEEE TSE 2018. (7 projects, 79 devs, 3244 hours; ~58% time on comprehension.) [Online]. Available: <...>
  ```
- **经典文献引用原文**（Brooks, Conway, Lehman, Parnas, Gray, Mitnick, Miller, Cowan, Hofstadter…），不要引二手综述。
- **当代论点配近 1–2 年 arXiv / 顶会 / 顶级博客**（Karpathy, Mollick, Chollet, Anthropic / OpenAI 官方等）。
- **数据来源** 以行业垂直网站、主流财经平台为主。

## Reddit 数据处理方法论（`data/reddit/`）

从 Reddit 帖子/评论中提取结构化信息的通用方法。价格和退市只是已实现的两个例子，
同一套流程适用于任何信息提取任务。

### 数据来源

https://arctic-shift.photon-reddit.com/download-tool 下载频道 JSONL：
- `r_*_posts.jsonl`：帖子，字段 title / selftext / created_utc / score / permalink
- `r_*_comments.jsonl`：评论，用 body 替代 selftext，无 title，link_id 关联父帖

新频道文件放入 `data/reddit/` 后脚本直接重跑，无需改代码。

### 两级抽取流程：按信号噪声比选择方法

**判断依据**：目标信息在帖子文本中的**信噪比**。

#### Level 1：纯正则（信号明确、噪声低）

适用于：帖子里有**结构化字面量**的信息——金额、费率、配额数字等。
正则抽得出、误命中少，不需要 LLM。

- 脚本：`scripts/analyze_reddit_prices.py --mode <name>`
- 统一处理 posts + comments（comments 用 body 替代 selftext）
- 廉价预过滤（小写子串判断），只对可能命中的帖跑正则，避免百万行回溯
- 输出 CSV 含抽取值 + 帖子元数据（date / score / permalink / snippet）

已实现例：`--mode price`（美元金额 / token 费率 / 用量上限 / premium request）

#### Level 2：正则粗筛 + LLM 精分类 + LLM 结构化抽取（信号模糊、噪声高）

适用于：关键词命中多但语义歧义大——"removed" 可能是模型退市、版主删帖、功能下架、
rate limit 变更……正则无法区分。

三步流程：

**第 1 步：正则粗筛**（同 Level 1 的脚本）
- 用宽松正则捞出所有*可能*相关的帖（宁多勿漏）
- 输出候选 CSV，每行一个帖

**第 2 步：Haiku 快速分类**（大批量、低成本、过滤噪声）
- 从候选 CSV 筛 score>=5 且有实体名的帖（~2000 条量级）
- 分批（每批 30–40 条）通过 Workflow pipeline 发给 Haiku subagent
- Haiku 只做**分类**（是/否/哪一类），不抽取细节
- 结果写回 CSV 的 `llm_verdict` + `llm_confidence` 列
- 这步的目的是**把 70–80% 的噪声廉价地过滤掉**

**第 3 步：Sonnet 结构化抽取**（少量、高质量、抽取细节）
- 只对 Haiku 判为目标类别的帖（~300–400 条）发给 Sonnet
- Sonnet 同时做两件事：**校验 Haiku 判定**（推翻约 20–30% 假阳性）+
  **从帖子内容抽取结构化字段**
- 用 JSON Schema 强制输出结构（structured output），每条帖返回一个 events 数组
- 结果写回 CSV 的 `llm_events` JSON 列

**调用 LLM 一律用 Claude Code subagent**（Workflow + `Agent({model: 'haiku'/'sonnet', schema: ...})`），
不要 `pip install anthropic` 走 API。

### 退市事件抽取（已实现的 Level 2 例子）

第 1 步正则：`--mode deprecation`，关键词 deprecat/sunset/retired/removed 等
第 2 步 Haiku 分类为：`model_retirement` / `model_replacement` / `feature_change` /
  `rate_limit_change` / `price_change` / `general_discussion` / `other`
第 3 步 Sonnet 对每条帖抽取 `events[]`，每个 event 含：
  - `model`：精确模型名（如 gpt-3.5-turbo-0301，不是 GPT-3.5）
  - `provider`：OpenAI / Anthropic / Google / DeepSeek / ...
  - `timing`：
    - `immediate`：帖子日期 = 退市生效日
    - `announced_future`：官方预告，退市日在未来（看 effective_date）
    - `already_happened`：追溯讨论，帖子日期晚于退市日
    - `speculative`：推测/担忧/传闻，不可作为证据
  - `effective_date`：帖子里明确提到的退市生效日（YYYY-MM-DD），无则空

### 通用 schema 设计原则

设计 LLM 抽取的 schema 时注意：
- **帖子日期（created_utc）≠ 事件生效日期**：Reddit 帖可能在预告、追溯、推测。
  必须让 LLM 区分 timing，不能直接拿帖子日期当事件日期
- **模型/实体名要精确**：让 LLM 抽出具体版本号（gpt-4-0314 而非 GPT-4），
  模糊名会导致下游匹配到错误实体
- **events 是数组**：一条帖子可能讨论多个事件，schema 设计为数组
- **Haiku 用平面分类（enum）,Sonnet 用嵌套结构（object array）**：
  Haiku 抽不好复杂嵌套，只让它做 verdict；结构化抽取留给 Sonnet

### 结果回填其他数据文件的规范

- 从 Reddit 发现的新数据点先在对话中**跟现有数据交叉比对**,无冲突才加入
- 加入时在 notes 列追加 `confirmed/corroborated YYYY-MM-DD (Reddit r/SubName)`
- 在 source 列追加 ` | https://reddit.com/comments/XXXXX`（` | ` 分隔多源）
- Reddit 帖的 `created_utc` 是"在野"证据日期,不等于事件生效日期——两者分别标注

## 关键陷阱（来自此前的失败）

- 模型/产品的**发布日期 ≠ 评测公布日期 ≠ 新闻报道日期**，三者要分别核对（曾把 4 月发布的 Mythos Preview 误写成"今天同步发布"）
- `chat/` 下的对话**不等于今天的新闻事实**，里面可能完全不包含当天关键事实；要搜或问，不要默默编造
- 用户给的不一定是新闻——**先判断条目类型，再选模板**，不要把每件事都套成"信源 + 主张 + 意义"
- 用户让我"整理 idea"≠ 让我"自由发挥"。**不要替他想结论**，先把他给的东西忠实组织好，再问要不要扩
