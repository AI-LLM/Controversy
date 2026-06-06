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

3,275 条越级事件里，**1,395 条（43%）的被比对象是闭源／前沿模型**（target_size 为空的闭源旗舰，已剔除 GPT-OSS 等开放权重）。按厂商：

| 被叫板的厂商 | 事件数 | 占比 | 被点名最多的型号 |
|---|---|---|---|
| OpenAI（GPT / o* / ChatGPT） | 866 | 62% | GPT-4 (199)、GPT-4o (118)、GPT-3.5 (116) |
| Anthropic（Claude / Opus / Sonnet） | 258 | 18% | Claude 3.5 Sonnet (40)、Claude Opus (25) |
| 泛指"前沿 / 闭源 / cloud" | 143 | 10% | frontier、cloud models |
| Google Gemini | 116 | 8% | Gemini 2.5 Pro (16) |
| xAI Grok | 12 | 1% | — |

一个反直觉的结构：**挑战闭源所需的参数量没有一路下降，而是卡在 ~25–30B 不动——但被它叫板的对手强了好几代**。逐年看"核心域、社区非质疑、稠密模型"成功叫板闭源的中位参数量：

| 年份 | 事件数 | 中位尺寸 | 那年的对手 |
|---|---|---|---|
| 2023 | 121 | **13B** | GPT-3.5 |
| 2024 | 245 | 32B | GPT-4 / GPT-4o |
| 2025 | 211 | 22B | GPT-4o / o3-mini / Gemini 2.5 |
| 2026 | 109 | **27B** | GPT-5 / Claude Sonnet 4.6 / Gemini 3 Pro |

参数预算几乎没变（始终压在 20–32B 这一档），变的是对手——从 GPT-3.5 一路升到 GPT-5 / Gemini 3 Pro。**能力密度的提升不体现在"参数变小"，而体现在"同样 ~25–30B，今天叫板的是强好几代的闭源旗舰"**。MoE 是另一条线：Qwen3-30B-A3B（3B 活跃）这类已能拿来跟 Gemini 2.5 Flash 比。

成色上，打闭源的声明 benchmaxx 折扣最厚：证据为纯 benchmark/lmarena 的占 55%（762 条）、有实测的 38%（533 条）；社区反应里**质疑 429 条（31%）**、分歧 212、明确认同仅 80 条（6%），其余无足够回复信号。**叫板闭源比叫板开源更招怀疑**——近三分之一此类帖评论区在打假，明确买账的只有 6%。

发起挑战的家族：Qwen 374（绝对主力）、Llama 214、Gemma 79、Mistral 50、DeepSeek 41、GLM 31。标志性高分帖：Gemma 4 31B "destroyed every model"（同时叫板 Claude Sonnet 4.6 与 Gemini 3 Pro，1607 赞，认同）[[11]](https://reddit.com/r/LocalLLaMA/comments/1sdcotc/)；Jan-nano（Qwen3-4B 微调）> Claude 3.7 Sonnet（890 赞，认同）[[12]](https://reddit.com/r/LocalLLaMA/comments/1ljyo2p/)；GLM-4-32B > Gemini 2.5 Flash（577 赞，认同）[[13]](https://reddit.com/r/LocalLLaMA/comments/1k4god7/)。

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

### 含金量最高的一档：社区明确认同 + 有实测证据的全部记录（62 帖）

把"社区明确认同（endorsed）"与"证据为实测（personal_use / anecdote，非跑分）"两个条件同时满足的事件全部列出——这是整份语料里**最不打折**的越级记录：既不是 benchmaxx，也不是营销，而是有人真用过、且评论区认账。共 78 条事件、去重后 62 个帖：

| 日期 | 赞 | 小模型 | 被比下去 | 域 | 标题 | 链接 |
|---|---|---|---|---|---|---|
| 2023-09-27 | 170 | Mistral-7B-Instruct-v0.1 | Llama 13B models | general | LLM Chat/RP Comparison/Test: Mistral 7B Base + Instruct | [链接](https://reddit.com/r/LocalLLaMA/comments/16twtfn/) |
| 2023-10-22 | 138 | LLaMA2-13B-Tiefighter | OpenHermes 2 Mistral 7B | general | My current favorite new LLMs: SynthIA v1.5 and Tiefighter! | [链接](https://reddit.com/r/LocalLLaMA/comments/17e446l/) |
| 2023-12-06 | 8 | xwin-mlewd-13b-v0.2 | 7B-13B models (50+ competitors) | creative | I tested over 50 different language models in the past two weeks | [链接](https://reddit.com/r/LocalLLaMA/comments/18c2cs4/kc8qrou/#kc8qrou) |
| 2023-12-12 | 234 | Mixtral-8x7B-Instruct-v0.1 | Llama 2 70B / GPT-3.5 | general | LLM Comparison/Test: Mixtral-8x7B, Mistral, DeciLM, Synthia-MoE | [链接](https://reddit.com/r/LocalLLaMA/comments/18gz54r/) |
| 2023-12-22 | 74 | Mixtral 8x7B | Llama 2 70B | general | Mixtral MoE ELI5: How are the responses a higher quality than a 7b? | [链接](https://reddit.com/r/LocalLLaMA/comments/18osgzt/) |
| 2023-12-24 | 5 | Starling-LM-7B | PuddleJumper-13B-v2 | general | Starling 7B — basically the best 7B I have tried so far | [链接](https://reddit.com/r/LocalLLaMA/comments/18pgfuy/keovmjd/#keovmjd) |
| 2023-12-27 | 76 | flan-T5-3B / lamini-flan-t5-783m | mini orca 3B / TinyLlama-1.1B | general | Why is no-one fine-tuning something like t5? | [链接](https://reddit.com/r/LocalLLaMA/comments/18rryf1/) |
| 2024-02-27 | 38 | Phi-2 | Gemma-2B 和 Qwen1.5-4B 微调 | coding | no other model perform above PHI-2 (below 5B) | [链接](https://reddit.com/r/LocalLLaMA/comments/1b1eohd/) |
| 2024-04-19 | 25 | Mixtral 8x22B Q2K | Mixtral 8x7B | reasoning | I was wrong about 2-bit quants | [链接](https://reddit.com/r/LocalLLaMA/comments/1c81oxo/) |
| 2024-04-20 | 258 | Llama 3 8B | Mistral 7B v0.2 | general | Thanks Zuck/Meta for these great Llama 3 models! ...BUT... | [链接](https://reddit.com/r/LocalLLaMA/comments/1c8u0n5/) |
| 2024-04-25 | 155 | Llama 3 8B fp16 | Llama 3 70B Q4 | coding | Quantizing Llama 3 8B seems more harmful compared to other models | [链接](https://reddit.com/r/LocalLLaMA/comments/1cci5w6/) |
| 2024-05-23 | 146 | SFR-Iterative-DPO-LLaMA-3-8B-R | larger open source models | reasoning | The Salesforce finetune of Llama 3 … is fantastic for reasoning | [链接](https://reddit.com/r/LocalLLaMA/comments/1cyxh1d/) |
| 2024-06-28 | 136 | Gemma 2 9B / Gemma 2 27B | Llama 3 8B / Llama 3 70B | general | What are your thoughts on Gemma2 27B and 9B? | [链接](https://reddit.com/r/LocalLLaMA/comments/1dqlis5/) |
| 2024-06-30 | 112 | Codestral 22B | DeepSeek Coder v1 34B | coding | My experience with using Codestral 22b for developing my first android app | [链接](https://reddit.com/r/LocalLLaMA/comments/1ds9ogn/) |
| 2024-07-07 | 29 | Gemma 2 27B | Goliath-120B / ChatGPT-3.5 | creative | Any worthy Gemma 2 27B finetunes for writing/RP? | [链接](https://reddit.com/r/LocalLLaMA/comments/1dxpc4r/) |
| 2024-07-26 | 43 | mini-magnum-12b-v1.1 (NeMo 12B 微调) | Llama 3 8B | creative | Nemo 12b, rp/erp/storytelling | [链接](https://reddit.com/r/LocalLLaMA/comments/1ecekpv/) |
| 2024-09-17 | 166 | Mistral-Small-Instruct-2409 | Gemma 27B | general | Mistral-Small-Instruct-2409 is actually really impressive | [链接](https://reddit.com/r/LocalLLaMA/comments/1fjb4i5/) |
| 2024-09-19 | 146 | Qwen2.5-32B | Llama 3.1 70B / Gemma 2 27B | general | Just replaced Llama 3.1 70B @ iQ2S for Qwen 2.5 32B @ Q4KM | [链接](https://reddit.com/r/LocalLLaMA/comments/1fkbumy/) |
| 2024-09-20 | 206 | Qwen2.5-32B-Instruct | Gemma 27B | general | Qwen2.5-32B-Instruct may be the best model for 3090s right now | [链接](https://reddit.com/r/LocalLLaMA/comments/1flfh0p/) |
| 2024-11-01 | 173 | Qwen2.5-14B | GPT-4o | agentic | IMO the best model for agents: Qwen2.5 14b | [链接](https://reddit.com/r/LocalLLaMA/comments/1gheq9t/) |
| 2024-11-14 | 291 | Qwen2.5-Coder-32B-Instruct | Qwen2.5-72B / GPT-4o | coding | Qwen 32B Coder-Ins vs 72B-Ins on the latest Leetcode problems | [链接](https://reddit.com/r/LocalLLaMA/comments/1gr35xp/) |
| 2024-11-28 | 208 | QwQ-32B | o1-preview / o1-mini | reasoning | I ran my misguided attention eval locally on QwQ-32B 4bit — beats o1-preview | [链接](https://reddit.com/r/LocalLLaMA/comments/1h1u7r9/) |
| 2025-01-25 | 43 | Qwen2.5-Coder-32B-Instruct | Llama-3.3-70B | coding | So what is now the best local AI for coding? | [链接](https://reddit.com/r/LocalLLaMA/comments/1ia0j9o/) |
| 2025-02-26 | 60 | Gemma 2 2B | Llama 3 400B | multilingual | Gemma 2 2B: Small in Size, Giant in Multilingual Performance | [链接](https://reddit.com/r/LocalLLaMA/comments/1iywf6n/) |
| 2025-03-06 | 232 | QwQ-32B | DeepSeek-R1 Distill 32B | coding | A few hours with QwQ and Aider - and my thoughts | [链接](https://reddit.com/r/LocalLLaMA/comments/1j4p3xw/) |
| 2025-03-06 | 168 | QwQ-32B | DeepSeek-R1 671B / o3-mini | math | new QwQ is beating any distil deepseek model in math, even better than full 670b | [链接](https://reddit.com/r/LocalLLaMA/comments/1j4x8sq/) |
| 2025-03-21 | 60 | Mistral Small 3.1 | GPT-4o Mini | vision | Mistral-small 3.1 Vision for PDF RAG tested | [链接](https://reddit.com/r/LocalLLaMA/comments/1jg5sbj/) |
| 2025-04-17 | 335 | Gemma 3 27B | ChatGPT (GPT-3.5 Turbo) | general | Medium sized local models already beating vanilla ChatGPT - Mind blown | [链接](https://reddit.com/r/LocalLLaMA/comments/1k1av1x/) |
| 2025-04-21 | 577 | GLM-4-32B | Gemini 2.5 Flash / Llama 70B | coding / general | GLM-4 32B is mind blowing | [链接](https://reddit.com/r/LocalLLaMA/comments/1k4god7/) |
| 2025-05-05 | 89 | Qwen3-235B-A22B | DeepSeek-R1 / DeepSeek-V3-0324 | general | Quick-and-dirty test of 5 models on a Mac Studio M3 Ultra 512GB | [链接](https://reddit.com/r/LocalLLaMA/comments/1kfi8xh/) |
| 2025-05-06 | 67 | Qwen3-4B | Gemma 3 12B | general | Qwen 3 Small Models: 0.6B, 1.7B & 4B compared with Gemma 3 | [链接](https://reddit.com/r/LocalLLaMA/comments/1kfrcul/) |
| 2025-05-30 | 171 | DeepSeek-R1-0528-Qwen3-8B | DeepSeek-R1 (原 8B distill) | agentic | Deepseek-r1-0528-qwen3-8b is much better than expected | [链接](https://reddit.com/r/LocalLLaMA/comments/1kyt71a/) |
| 2025-07-22 | 361 | Qwen3-Coder-408B-A35B-Instruct | Kimi-K2-Instruct | coding | Qwen3-Coder Web Development | [链接](https://reddit.com/r/LocalLLaMA/comments/1m6ny2q/) |
| 2025-07-30 | 463 | Qwen3-30B-A3B-thinking-2507 | Gemini 2.5 Flash | general | Qwen3-30b-a3b-thinking-2507 This is insane performance | [链接](https://reddit.com/r/LocalLLaMA/comments/1md8slx/) |
| 2025-07-30 | 205 | GLM-4.5-Air | Qwen2.5-32B | agentic | glm-4.5-Air appreciation post — give this model a try | [链接](https://reddit.com/r/LocalLLaMA/comments/1mdhfhs/) |
| 2025-08-08 | 203 | Granite 3 8B | GPT-5 mini/nano | agentic | Granite 3 8B is seriously underrated - still outperforming newer models | [链接](https://reddit.com/r/LocalLLaMA/comments/1mkp0am/) |
| 2025-08-20 | 43 | NVIDIA-Nemotron-Nano-9B-v2 | Qwen3-Coder-30B | coding | NVIDIA-Nemotron-Nano-9B-v2 vs Qwen3-Coder-30B | [链接](https://reddit.com/r/LocalLLaMA/comments/1mv6cjq/) |
| 2025-09-12 | 109 | parakeet-tdt-0.6b-v3 | Whisper large | other | 30 Days Testing Parakeet v3 vs Whisper | [链接](https://reddit.com/r/LocalLLaMA/comments/1nf10ye/) |
| 2025-11-27 | 57 | TongyiMaizi-Image-Turbo 6B | FLUX.2 | vision | r/StableDiffusion everyone over there is going NUTS over this model | [链接](https://reddit.com/r/LocalLLaMA/comments/1p7i9qh/nqyz5rn/#nqyz5rn) |
| 2025-11-29 | 126 | gpt-oss-120b | Qwen3-Next-80B-A3B | agentic | Qwen3-Next-80B-A3B vs gpt-oss-120b | [链接](https://reddit.com/r/LocalLLaMA/comments/1p9nckz/) |
| 2025-12-19 | 29 | Qwen 8B | cloud models | agentic | I've been experimenting with SLM's a lot recently … even SLMs can be accurate | [链接](https://reddit.com/r/LocalLLaMA/comments/1pqd7sy/) |
| 2026-01-15 | 101 | LFM 2.5 (~1B) | models 3x larger (~3B class) | general | LFM 2.5 is insanely good | [链接](https://reddit.com/r/LocalLLaMA/comments/1qdax6z/) |
| 2026-01-21 | 162 | distilled Text2SQL 0.6B | GPT-class models | coding | Knowledge distillation with Claude: trained a 0.6B model to match GPT-class | [链接](https://reddit.com/r/LocalLLaMA/comments/1qiu6jo/) |
| 2026-02-06 | 26 | Nanbeige4-3B-Thinking-2511 | Qwen3-14B | agentic | Nanbeige4-3B-Thinking-2511 is honestly impressive | [链接](https://reddit.com/r/LocalLLaMA/comments/1qxxhi4/) |
| 2026-02-07 | 160 | Qwen2.5 1.5B | Qwen2.5 3B | agentic | I tested 11 small LLMs on tool-calling judgment — on CPU, no GPU | [链接](https://reddit.com/r/LocalLLaMA/comments/1qyg10z/) |
| 2026-02-20 | 81 | Qwen3-Coder-Next-30B Q2 | 30B models (Qwen 30B, Devstral) | coding | Qwen3 coder next oddly usable at aggressive quantization | [链接](https://reddit.com/r/LocalLLaMA/comments/1rabg6o/) |
| 2026-02-21 | 41 | Nanbeige 4.1 | Qwen 4B | general | Nanbeige 4.1 is the best small LLM, it crush qwen 4b | [链接](https://reddit.com/r/LocalLLaMA/comments/1rb61og/) |
| 2026-02-24 | 41 | Qwen-3.5-35B-A3B | GLM 4.7 Flash | agentic | Qwen-3.5-35B-A3B is impressive | [链接](https://reddit.com/r/LocalLLaMA/comments/1rdru9p/) |
| 2026-02-24 | 16 | LocoOperator-4B | 7B models | agentic | A small 4B sub-agent for local codebase navigation, 100% tool-calling validity | [链接](https://reddit.com/r/LocalLLaMA/comments/1rdfu5e/) |
| 2026-03-05 | 8 | Qwen3.5-9B | GPT-OSS 120B | general | Are we at a tipping point for local AI? Qwen3.5 might just be | [链接](https://reddit.com/r/LocalLLaMA/comments/1rln0dv/) |
| 2026-03-10 | 190 | Qwen 3.5 0.8B (LoRA 微调) | larger models (baseline) | coding | 0.8B model teaching itself on a MacBook Air with 6GB RAM | [链接](https://reddit.com/r/LocalLLaMA/comments/1rq3bix/) |
| 2026-03-13 | 42 | Qwen 3.5 2B (微调) | Qwen 3.5 4B / 9B / 27B / 35B | other | Fine-tuned Qwen 3.5 2B to beat same-quant 4B, 9B, 27B, 35B on dictation cleanup | [链接](https://reddit.com/r/LocalLLaMA/comments/1rstcy3/) |
| 2026-03-23 | 131 | Qwen3.5-27B | Qwen3.5-122B | coding | Another appreciation post for qwen3.5 27b model | [链接](https://reddit.com/r/LocalLLaMA/comments/1s1p2jo/) |
| 2026-03-30 | 196 | Qwen 3.5-27B / Nemotron-Cascade-2-30B-A3B | frontier / Qwen 3.5-35B-A3B | coding | I tested as many small local and OpenRouter models … agentic text-to-SQL | [链接](https://reddit.com/r/LocalLLaMA/comments/1s7r9wu/) |
| 2026-04-06 | 136 | Gemma 4 26B | Gemini 3 Flash | agentic | Gemma4:26b's reasoning capabilities are crazy | [链接](https://reddit.com/r/LocalLLaMA/comments/1sdz71b/) |
| 2026-04-09 | 847 | Gemma 4 31B UD IQ3 XXS | Claude Opus 4.6 | general | It's insane how lobotomized Opus 4.6 is right now. Even Gemma 4 31B beat it | [链接](https://reddit.com/r/LocalLLaMA/comments/1sgd7fp/) |
| 2026-04-12 | 7 | Qwen3.5-9B BF16 | Qwen 3.5 UD Q8_K_XL | reasoning | A Reasoning (Local) Model Comparison … complex long-range reasoning | [链接](https://reddit.com/r/LocalLLaMA/comments/1sj07pe/) |
| 2026-04-18 | 288 | Qwen3.6-35B-A3B | Qwen3.5-27B / Qwen3.5-122B | coding | Qwen3.6-35B-A3B solved coding problems Qwen3.5-27B couldn't | [链接](https://reddit.com/r/LocalLLaMA/comments/1soxyfi/) |
| 2026-04-24 | 133 | Qwen 3.6 27B | Claude Sonnet 4.6 | coding | Opinion: Qwen 3.6 27b Beats Sonnet 4.6 on Feature Planning | [链接](https://reddit.com/r/LocalLLaMA/comments/1supft2/) |
| 2026-05-05 | 635 | Qwen 3.6 27B | cloud models | coding | DeepSeek V4 17x cheaper got me to measure cloud vs local | [链接](https://reddit.com/r/LocalLLaMA/comments/1t4s6g2/) |
| 2026-05-11 | 419 | Qwen 3.6 35B A3B / Gemma 4 26B A4B | frontier | coding | The Qwen 3.6 35B A3B hype is real!!! | [链接](https://reddit.com/r/LocalLLaMA/comments/1t9whrt/) |
| 2026-06-04 | 288 | Qwen3.6-35B-A3B IQ4NXL | Qwen3.5-27B Q5_K_XL | coding | You guys were right - Qwen 3.6 35B IS good … and KV Cache DOES matter | [链接](https://reddit.com/r/LocalLLaMA/comments/1twyoqe/) |

读这张表的两个观察：(1) **被认账的实测越级，主体是 20-34B 与 7-15B 稠密模型**——Qwen2.5/3.x-32B、Gemma 2/3/4-27B、QwQ-32B、GLM-4-32B 反复出现，正是甜点档；(2) 标题大量是"appreciation post""mind blowing""insane performance"这类**用户自发安利**，而非厂商通告——与第四节"20-34B 营销占比最低、实测最高"的统计互为印证。⚠ 这 62 帖仍是社区**判断**，证据为发帖人自述实测 + 评论区认同，未经独立复现。

## 方法与数据

- **语料**：r/LocalLLaMA 全量，118,391 帖 + 1,787,788 评论，2023-03-10 → 2026-06-06（增量 dump 经去重合并入主文件，`scripts/merge_reddit_dumps.py`）。
- **Level-1（正则）**：`analyze_reddit_prices.py --mode capability` 抽参数量（含 MoE 的 N×M 与 active 记法）、模型家族、硬件／量化共现、跨尺寸比较旗标，命中 220,287 条，产出 `capability_mentions.csv` 与四角度聚合 `capability_aggregates.json`。尺寸正则用负向后顾排除 `24GB`／`$7B`／`4bit` 等误命中。
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

[11] r/LocalLLaMA, "Gemma 4 just casually destroyed every model on our leaderboard," Apr 2026. (1607 赞；同时叫板 Claude Sonnet 4.6 与 Gemini 3 Pro.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1sdcotc/>

[12] r/LocalLLaMA, "Jan-nano-128k: A 4B Model … Still Outperforms 671B," Jun 2025. (890 赞；Qwen3-4B 微调 > Claude 3.7 Sonnet.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1ljyo2p/>

[13] r/LocalLLaMA, "GLM-4 32B is mind blowing," Apr 2025. (577 赞；> Gemini 2.5 Flash.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1k4god7/>

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
