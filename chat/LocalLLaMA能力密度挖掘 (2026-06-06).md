# 2026-06-06：r/LocalLLaMA 三年语料里的"能力密度"曲线——小模型怎样一路打平大模型

把 r/LocalLLaMA 从 2023-03 到 2026-06-06 的全部 118,391 个帖子 + 1,787,788 条评论拉出来，按参数量级做结构化抽取，能看到一条比任何榜单都贴近"实际能用"体感的曲线：**同样的能力，所需的参数量在三年里持续下降**。2023 年要 30–70B 才敢叫板 GPT-3.5／GPT-4；到 2026 年，社区把 27–31B 摆上桌跟 GPT-5 级别的闭源模型比，而 MoE 又把"活跃参数"压到个位数 B。

下面四节分别是：越级声明的时间线（能力密度）、社区注意力的尺寸迁移、模型家族×尺寸的铺位、以及最关键的一条——**营销标题党与实测口碑怎么随尺寸分化**。

数据是社区的**声明**，不是客观真值。本文的份额、计数是关于语料的事实；"能力密度上升"是对这些声明（及社区自己的接受度数据）的解读。LLM 抽取的 3,275 条事件里，二次校验推翻了约 9%（见方法节），阅读时按"在野证据"对待。

## 一、能力密度曲线：越级"小打大"的时间线

从语料里抽出 3,275 条"较小模型打平／超越更大或前沿模型"的事件，取通用／推理／编码／agentic 域、社区非一致质疑、且帖子日期即事件日期的高关注度条目，逐季度的标志性里程碑如下：

| 季度 | 小模型 | 被比下去的对象 | 域 | 点赞数 | 社区反应 |
|---|---|---|---|---|---|
| 2023Q2 | phi-1 **1.3B** | GPT-3.5 | coding | 433 | 认同 |
| 2023Q2 | WizardLM-30B | GPT-4 | reasoning | 123 | 分歧 |
| 2023Q3 | Mistral-7B-v0.1 | 13B | general | 170 | 认同 |
| 2023Q4 | Mixtral-8x7B（**47B/12.9B 活跃**） | Llama 2 70B | general | 234 | 认同 |
| 2024Q1 | Mistral-7B（ReAct 微调） | Gemini Pro | agentic | 253 | 分歧 |
| 2024Q4 | Llama **3B** + 测试时搜索 | Llama 70B | reasoning/math | 773 | 认同 |
| 2025Q1 | OLMo 2 **32B** | GPT-4o mini / GPT-3.5 | general | 1551 | 认同 |
| 2025Q2 | Qwen3-**4B** | 72B | general | 1768 | 认同 |
| 2025Q2 | Qwen3-30B-**A3B** | 32B（稠密） | general | 1768 | 认同 |
| 2025Q3 | Qwen3-30B-A3B-thinking | 235B | reasoning | 463 | 认同 |
| 2026Q1 | Qwen2.5-Coder-32B（PewDiePie 微调） | ChatGPT-4o | coding | 743 | 分歧 |
| 2026Q2 | Gemma 4 **31B** | GPT-5.2 / Gemini 3 Pro | agentic | 1607 | 认同 |

两列来源不同，不要混看：**点赞数**是该帖在 Reddit 上的原始 score（客观计数）；**社区反应**是 Sonnet 读取该帖通过 `link_id` 关联到的高赞回复（top_replies）再结合赞数，判断社区是否买账——分 endorsed（多数回复认同，本表记"认同"）／mixed（回复有赞有弹，记"分歧"）／skeptical（多数回复质疑、打假）／none（回复信号不足）四档。它是 **LLM 对真实评论内容的判读，不是由赞数机械换算**——高赞帖也可能是"分歧"（如 Qwen2.5-Coder-32B 那条 743 赞，但回复区对"是否训练集污染／刷榜"争论不一）。本里程碑表已滤掉 skeptical 档（社区一致质疑的不计入里程碑）。

四个有据可查的历史锚点：

- **phi-1（1.3B）**：用 GPT-3.5 合成的"教科书质量"数据训练，HumanEval pass@1 达 50.6%，越过同期 GPT-3.5 的编码水平 [[1]](https://arxiv.org/abs/2306.11644)。这是"数据质量换参数量"的第一个出圈样本。
- **Mixtral-8x7B**：稀疏 MoE，总 46.7B、每 token 仅激活 12.9B，官方与社区评测都认为它打平 Llama 2 70B 与 GPT-3.5 [[2]](https://mistral.ai/news/mixtral-of-experts)。MoE 第一次让"看起来像 7B、聪明像 70B"成为现实。
- **Llama 3B + 测试时计算**：Hugging Face 用步骤级奖励模型 + DVTS 树搜索，让 3B 在 MATH-500 上追平 70B [[3]](https://huggingface.co/posts/lewtun/679536201490974)。能力可以从"参数"转嫁到"推理时算力"。
- **QwQ-32B**：用 RL 把 32B 的推理拉到与 DeepSeek-R1（671B、37B 活跃）同级，AIME24 79.5% vs R1 79.8% [[4]](https://qwenlm.github.io/blog/qwq-32b/)。一个能塞进单张 24GB 卡的模型，叫板一个要整机柜的 671B。

这条曲线有两层独立的下降叠加：其一是**稠密模型的能力密度**本身在升（13B→7B→4B 逐代追上前代大哥）；其二是 **MoE 把"活跃参数"从总参数里解耦**——Qwen3-30B-A3B 总 30B、每 token 只激活 3B，却被社区拿来跟 235B 比。到 2026 年，"几 B 打几百 B"的句式从夸张标题变成了日常表达。

⚠ 解读：2026 年的条目（Gemma 4 31B、Qwen 3.5/3.6 27B、对手 GPT-5.2/Gemini 3 Pro）超出可独立核验的范围，**一手源是 r/LocalLLaMA 当时的讨论本身**（见信源 permalink），本文不对其外部 benchmark 真值背书；社区对这批声明的接受度见第四节。

### 专打闭源前沿：1,395 条叫板 ChatGPT / Claude / Gemini 的事件

3,275 条越级事件里，**1,395 条（43%）的被比对象是闭源／前沿旗舰**（OpenAI 866、Anthropic 258、Gemini 116、Grok 12，另有 143 条泛指"前沿/cloud"；已剔除 GPT-OSS 等开放权重）。一个反直觉的结构：**挑战闭源所需的参数量没有一路下降，而是卡在 ~25–30B 不动——但被它叫板的对手从 GPT-3.5 一路升到 GPT-5 / Gemini 3 Pro**。再把口径砍到"社区明确认同 + 亲自实测（非跑分）"，整份语料只剩 19 帖硬核样本。

这一支线已独立成篇，含厂商分布、逐年中位尺寸、benchmaxx 成色、以及全 19 条实测记录（带原帖链接）：[小模型叫板闭源前沿 (2026-06-06).md](小模型叫板闭源前沿%20(2026-06-06).md)。

## 二、甜点区迁移：13B/70B 退场，20-34B 与 100B+ MoE 上位

按月统计带参数量的帖子，再算"当月各尺寸桶占尺寸提及总数的份额"（自归一化，同时抵消总帖量和尺寸标注率两个混淆）。季度份额（%）：

| 季度 | <1B | 1-3B | 4-6B | 7-9B | 11-15B | 20-34B | 40-49B | 65-72B | 100B+ |
|---|---|---|---|---|---|---|---|---|---|
| 2023Q2 | 0 | 3 | 1 | 20 | 28 | 27 | 2 | 16 | 3 |
| 2023Q4 | 0 | 5 | 1 | **33** | 17 | 16 | 1 | 20 | 7 |
| 2024Q2 | 0 | 5 | 2 | **37** | 7 | 14 | 1 | **26** | 8 |
| 2024Q4 | 2 | 14 | 1 | 20 | 11 | 20 | 1 | 22 | 10 |
| 2025Q2 | 2 | 8 | 6 | 14 | 12 | **35** | 1 | 10 | 12 |
| 2025Q3 | 2 | 7 | 8 | 10 | 8 | 33 | 2 | 7 | **24** |
| 2026Q1 | 2 | 9 | 7 | 15 | 5 | 33 | 1 | 5 | 23 |
| 2026Q2 | 1 | 6 | 5 | 10 | 4 | **55** | 1 | 3 | 16 |

三个清晰的趋势：

- **"70B 为王"档（65-72B）崩塌**：2024Q2 占 26%，到 2026Q2 只剩 3%。Llama 2/3 的 70B 曾是本地高端的代名词，如今几乎没人再提。
- **"13B 时代"（11-15B）消亡**：从 2023 年的 28% 一路跌到 4%。这个曾经的消费级甜点被 7-9B（更省）和 20-34B（更强）两头夹死。
- **20-34B 成为新王**：从个位数份额涨到 2026Q2 的 55%。Qwen 32B、Gemma 27/31B、QwQ-32B 这一档，正好卡在"单张 24–32GB 卡能跑 + 能力够顶"的位置。
- **100B+ MoE 崛起**：从近乎 0 涨到 2025Q3 起稳定 23–25%。DeepSeek、GLM、Kimi、Qwen 的大 MoE 把"百 B 级"重新拉回本地玩家的视野。

为什么迁移？硬件共现给了驱动证据。把帖子里的显卡／内存提及按季度统计，2025Q3 起 **128GB／64GB 的提及显著上行**（与 100B+ MoE 同步），而 **24GB（3090／4090）始终是主力工作台**——3090 三年来一直在每季 Top 3。叠加 GGUF／量化的普及（量化提及里 Q4_K_M、IQ3、GGUF 长期高频），大模型被"压"进消费级显存，这才让 100B+ MoE 和 20-34B 稠密模型同时进入本地可跑区间。

## 三、家族 × 尺寸 × 时间：各家占的是哪一格

把 17 个模型家族按尺寸桶聚合（n=家族总提及，主力档=占比 ≥10% 的桶）：

| 家族 | 提及量 | 活跃区间 | 主力尺寸档 |
|---|---|---|---|
| Qwen | 84,682 | 2023-08～至今 | **20-34B (41%)**、7-9B、100B+ |
| Llama | 70,576 | 2023-03～至今 | 7-9B (25%)、**65-72B (21%)**、20-34B |
| Gemma | 27,105 | 2024-02～至今 | **20-34B (42%)**、7-9B、11-15B |
| Mistral | 26,487 | 2023-09～至今 | 7-9B (33%)、20-34B、11-15B |
| DeepSeek | 15,224 | 2023-11～至今 | 20-34B、**100B+ (22%)**、65-72B |
| Mixtral | 7,829 | 2023-12～2026-05 | **7-9B (44%, 即 8x7B)**、20-34B |
| GLM | 4,746 | 2023-04～至今 | 20-34B、**100B+ (32%)** |
| Phi | 4,563 | 2023-06～至今 | 1-3B、7-9B、11-15B（**小模型专精**） |
| Kimi | 3,081 | 2023-12～至今 | 20-34B、**100B+ (37%)** |

读出来的格局：**Qwen 是 20-34B 甜点区的王**（单家 8.4 万提及，41% 压在这一档），也是这轮迁移的最大受益者；**Llama 是 70B 老王**，重心还压在正在退场的 65-72B；**Mixtral 把 8x7B 这一记法推火又随之淡出**（末次提及 2026-05）；**DeepSeek／GLM／Kimi 扎堆 100B+ MoE**，是大 MoE 复兴的主力；**Phi 始终守在 1-7B 的小模型专精位**，是"小而精"路线的代表。

## 四、营销标题党 vs 实测口碑：越小的模型越靠跑分

这是四个角度里信息量最大的一条。把每条越级事件按小模型尺寸分档，统计证据类型和社区反应：

| 小模型档 | 事件数 | 营销口吻 | 仅 benchmark | 有实测证据 | 社区质疑 |
|---|---|---|---|---|---|
| <7B | 544 | **29%** | **63%** | 26% | 27% |
| 7-15B | 991 | 15% | 56% | 36% | 30% |
| 20-34B | 963 | **7%** | 46% | **50%** | **21%** |
| 40-72B | 333 | 15% | 56% | 38% | 27% |
| 100B+ | 240 | 10% | 48% | 46% | 25% |

规律很干净：**模型越小，越级声明越靠 benchmark 和营销撑场**。<7B 档里 29% 是营销通告口吻、63% 只有跑分、仅 26% 有真实使用佐证；而 **20-34B 甜点档恰恰相反**——营销口吻只占 7%、半数有实测证据、社区质疑率全场最低（21%）。换句话说，小模型的"越级"很多是 benchmaxx 标题党，而 20-34B 这一档是社区**真的在用、真的认账**的。

社区对 benchmaxx 的免疫力也写在语料里。高分帖里反复出现打假：

- "Stop asking what model to run. There are literally only two." [2340 赞] [[5]](https://reddit.com/r/LocalLLaMA/comments/1tu82wi/stop_asking_what_model_to_run_there_are_literally/)——对满屏越级帖的反讽。
- "I am sorry but the technical report screams 'training on test'" [605 赞] [[6]](https://reddit.com/r/LocalLLaMA/comments/1mfitwb/skywork_mindlink_32b72b/)——对 32B/72B 刷榜的直接质疑。
- "No it is not R1 equivalent" [605 赞] [[7]](https://reddit.com/r/LocalLLaMA/comments/1ikgsl6/germany_we_released_model_equivalent_to_r1_back/)——对"我们早就做出 R1 级模型"的打脸。
- 反向的也有：gemma 3 27b "underrated af, #11 at lmarena, matches o1" [555 赞] [[8]](https://reddit.com/r/LocalLLaMA/comments/1k2kl84/gemma_3_27b_is_underrated_af_its_at_11_at_lmarena/)——社区给实测过硬的小模型背书。

全局看，3,275 条事件里证据类型为纯 benchmark/lmarena 的占一半（1,735 条），有实测（personal_use/anecdote）的约 41%（1,342 条）；社区反应明确质疑的 863 条、明确认同仅 206 条。**"小打大"是真趋势，但每一条具体声明都要扣掉一层 benchmaxx 折扣**——而这层折扣，小模型档最厚。

## 方法与数据

- **语料**：r/LocalLLaMA 全量，118,391 帖 + 1,787,788 评论，2023-03-10 → 2026-06-06（增量 dump 经去重合并入主文件，`scripts/merge_reddit_dumps.py`）。
- **Level-1（正则）**：`analyze_reddit.py --mode capability` 抽参数量（含 MoE 的 N×M 与 active 记法）、模型家族、硬件／量化共现、跨尺寸比较旗标，命中 220,287 条，产出 `capability_mentions.csv` 与四角度聚合 `capability_aggregates.json`。尺寸正则用负向后顾排除 `24GB`／`$7B`／`4bit` 等误命中。
- **Level-2（LLM）**：对 7,875 条候选（跨尺寸比较 + 有尺寸 + score≥5）做两段式抽取——Haiku 分类过滤（verified_underdog 1,493、benchmark_only 951、refuted 793 等），Sonnet 对正例抽结构化 `events[]`（小模型／尺寸／被超对象／域／证据类型／timing／营销／社区反应）。共 3,275 条事件。LLM 一律走 Claude Code subagent（Workflow），非 API。
- **已知局限**：(1) 事件是社区**声明**，Sonnet 二次校验推翻约 9%（286/3,275），benchmaxx 声明仍可能漏网；(2) 社区反应基于帖子高赞回复 + 赞数代理，非完整评论树情感分析；(3) 2026 年模型超出可独立核验范围，以 Reddit 讨论为一手源；(4) "帖子日期 ≠ 事件生效日期"已在抽取时用 timing 字段区分，本文只取 immediate 类入里程碑。

## 信源

[1] S. Gunasekar et al., "Textbooks Are All You Need," *arXiv preprint*, arXiv:2306.11644, Jun 2023. (phi-1 1.3B, HumanEval pass@1 50.6%.) [Online]. Available: <https://arxiv.org/abs/2306.11644>

[2] Mistral AI, "Mixtral of experts," *Mistral AI News*, Dec 2023. (8x7B, 46.7B 总/12.9B 活跃，持平 Llama 2 70B 与 GPT-3.5.) [Online]. Available: <https://mistral.ai/news/mixtral-of-experts>

[3] L. Tunstall, E. Beeching, et al., "Scaling Test-Time Compute," *Hugging Face*, Dec 2024. (Llama 3B 在 MATH-500 追平 70B，DVTS 树搜索.) [Online]. Available: <https://huggingface.co/posts/lewtun/679536201490974>

[4] Qwen Team, "QwQ-32B: Embracing the Power of Reinforcement Learning," *Qwen Blog*, Mar 2025. (32B 持平 DeepSeek-R1 671B/37B 活跃；AIME24 79.5 vs 79.8.) [Online]. Available: <https://qwenlm.github.io/blog/qwq-32b/>

[5] r/LocalLLaMA, "Stop asking what model to run. There are literally only two," Jun 2026. (2340 赞.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1tu82wi/>

[6] r/LocalLLaMA, "Skywork MindLink 32B/72B — 'training on test'," Aug 2025. (605 赞质疑回复.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1mfitwb/>

[7] r/LocalLLaMA, "Germany: we released model equivalent to R1 — 'No it is not R1 equivalent'," Feb 2025. (605 赞质疑回复.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1ikgsl6/>

[8] r/LocalLLaMA, "gemma 3 27b is underrated af, #11 at lmarena, matches o1," Apr 2025. (555 赞.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1k2kl84/>

[9] r/LocalLLaMA, "HuggingFace researchers got 3b Llama to outperform 70b using search," Dec 2024. (773 赞.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1hgybhg/>

[10] r/LocalLLaMA, "AI2 releases OLMo 2 32B," Mar 2025. (1551 赞.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1jaj6gc/>

## 附录：Level-2 所用 LLM prompt

两段式抽取的 prompt 原文，供复现。每个 agent 读一个输入批文件（`b_NNN.json` / `s_NNN.json`，40 条/15 条一批），把结果写回对应输出批文件。

### Haiku 分类 prompt

```
你在给 r/LocalLLaMA 关于"不同参数量级模型能力比较"的帖子/评论做分类。

用 Read 工具读取 JSON 数组：<输入批路径>
每条含 id, kind, title, snippet, sizes_b（提到的参数量）, model_families, frontier_targets（被比较的前沿模型）, score。

给每条分配恰好一个 verdict：
- verified_underdog：声称一个【更小】的模型确实打平/超越【更大或前沿】模型，且作者当作真事呈现（自己实测或给了 benchmark）。
- benchmark_only：跨尺寸超越声明，但【仅】基于 benchmark 跑分（benchmaxx 味），没有实际使用佐证。
- refuted：文本【否定】小模型真能打平大/前沿（打假、"并没有"、"名不副实"、"R1 蒸馏版不是真 R1"）。
- marketing_hype：发布/推广通告，宣传口吻地声称更强，未经证实。
- sentiment_only：对某尺寸档的体感/观点，但【没有】具体的跨尺寸比较。
- off_topic：跟"按尺寸比能力"无关（纯硬件、玩笑、跑题）。

再给 confidence：high / medium / low。

判断要点：
- 关键是【小 vs 大】的方向。若只是同级比较或大模型更强，多半 sentiment_only 或 off_topic。
- 标题是营销通告口吻（"X released!"、"introducing"、"我们发布了"）且自夸 → marketing_hype。
- snippet 里有"actually not"、"falls short"、"not really"、"overhyped" → 倾向 refuted。

用 Write 工具把结果写成 JSON 数组到：<输出批路径>
格式：[{"id":"...","verdict":"...","confidence":"..."}, ...]，每条输入一个对应条目，id 必须一致。
文件里【只】写合法 JSON，不要 markdown 代码块、不要解释。
最终消息只回一句："b_NNN: <条数> classified"。
```

### Sonnet 抽取 prompt

```
你在从 r/LocalLLaMA 的帖子/评论里抽取"小模型越级打平/超越大模型或前沿模型"的结构化事件。

用 Read 工具读取 JSON 数组：<输入批路径>
每条含：id, kind(post/comment), date(帖子日期), score, title, body(正文/评论全文), top_replies(高赞回复，社区真实反应), sizes_b, active_params_b, model_families, frontier_targets, haiku_verdict(初判：verified_underdog/benchmark_only/refuted)。

对每条做两件事：
1) verdict_check：校验初判对不对，回 confirmed / overturned（你认为初判错）/ unclear。
2) 抽取 events 数组。一条帖可能含 0、1 或多个越级事件。每个 event：
   - small_model：被夸的【较小】模型精确名（如 "Qwen3-32B"、"Gemma 3 27B"、"QwQ-32B"；尽量带版本/尺寸，别只写 "Qwen"）
   - small_size_b：该模型参数量(数字, B)；无法确定填 null
   - active_size_b：若是 MoE 的活跃参数(数字)；否则 null
   - beaten_target：被比下去的【更大/前沿】对象名（如 "DeepSeek-R1"、"GPT-4o"、"Claude 3.5 Sonnet"、"Llama-3 70B"；泛指就写 "frontier" 或 "cloud models"）
   - target_size_b：被比对象参数量(数字)；前沿闭源/未知填 null
   - task_domain：coding / math / reasoning / general / agentic / multilingual / vision / creative / other
   - claim_strength：surpasses（超越） / on_par（持平） / approaches（接近但不及）
   - evidence_type：benchmark / lmarena / personal_use / anecdote / announcement / none
   - timing：immediate（帖子日=事件日） / announced（预告未来） / retrospective（回溯旧事） / speculative（推测传闻）
   - effective_date：文本明确提到的事件生效日 YYYY-MM-DD；无则 null（注意：帖子日期≠事件日期）
   - is_marketing：true/false（是否营销通告口吻而非中立/实测）
   - community_reaction：看 top_replies 和 score 判断社区是否买账 —— endorsed（多数认同） / skeptical（多数质疑、打假） / mixed / none（无足够回复信号）

抽取要点：
- 只抽【小→大】方向的越级。同级或大胜小不是 event。
- refuted 类：仍抽出它所【否定】的那个声明（small_model 是被质疑能越级的小模型，claim_strength 填原声称的强度），并让 community_reaction=skeptical、verdict_check=confirmed。
- small_size 必须真的【小于】target_size 才算越级（前沿闭源 target_size=null 时，看常识：32B 打 GPT-4o 算越级）。
- 拿不准 small_model 精确名时用 title/body 里出现的最具体写法。

用 Write 工具把结果写成 JSON 数组到：<输出批路径>
格式：[{"id":"...","haiku_verdict":"...","verdict_check":"...","events":[{...}, ...]}, ...]，每条输入对应一个条目，id 一致，events 可为 []。
文件里【只】写合法 JSON，无 markdown 代码块、无解释。
最终消息只回一句："s_NNN: <事件数> events"。
```
