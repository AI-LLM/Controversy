# 2026-06-06: How Small Models Challenge the Closed Frontier — From "Beating" on Benchmarks to "Replacing" in Real Workflows

The US stock market just had its "Black Friday" last Friday (June 5, 2026)[[1]](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-june-05-2026). The "AI bubble" is no longer a question of whether, only of when. Anthropic, OpenAI and SpaceX — the three AI-concept stocks — are all sprinting toward IPO[[2]](https://www.npr.org/2026/06/01/nx-s1-5843199/anthropic-ipo-filing-ai-large), [[3]](https://www.cnbc.com/2026/05/31/my-guide-to-the-ipos-of-spacex-openai-and-anthropic-including-the-one-i-really-want-to-buy.html), and as the dot-com-bubble alarms grow louder, Google is raising $85B in cash[[4]](https://www.cnbc.com/2026/06/05/alphabet-ai-data-center-financing.html) — for AI capex, or to buy the dip? For instance, it signed a contract with SpaceX to pay about $920M per month from October 2026 through June 2029, renting roughly 110,000 NVIDIA GPUs and related infrastructure[[5]](https://www.cnbc.com/2026/06/05/google-to-pay-spacex-920-million-a-month-for-xai-compute-capacity.html). The community questions whether the deal has a circular-investment flavor. HN user harmmonica calculates: "At a $1.5T valuation, Google's (diluted) SpaceX stake is roughly $80–100B (when it invested in 2015 the valuation was below $10B). This contract sends about $12B/year back to SpaceX, ~12% of the stake's market value."[[6]](https://news.ycombinator.com/item?id=48417490) In other words, Google is both a long-term SpaceX shareholder and one of its largest compute customers — a dual role that blurs the line between "real demand" and "strategic investment."

The biggest difference from the dot-com bubble so far is that the three giants' IPOs are about to drain market liquidity. But can a top-3 winner-take-all emerge? There's no social-media user network effect, no Google-Search data lock-in, and not even a technical moat in model training — Anthropic proved OpenAI has none, so it falls back on so-called "safety" to scare governments and public opinion, indirectly keeping others from catching up[[7]](https://www.darioamodei.com/post/on-deepseek-and-export-controls)[[8]](https://www.anthropic.com/news/anthropic-is-endorsing-sb-53)[[9]](https://officechai.com/ai/anthropic-has-a-pattern-of-using-fear-to-market-its-products-us-ai-czar-david-sacks/).

How to corroborate that LLMs have no technical moat? Each vendor's evaluations have become a joke, not to be trusted[[10]](https://arxiv.org/abs/2405.00332)[[11]](https://arxiv.org/abs/2504.20879)[[12]](https://arxiv.org/abs/2605.19999)[[13]](https://www.digitalapplied.com/blog/llm-benchmark-methodology-2026-contamination-leaderboard-guide)[[14]](https://arxiv.org/abs/2605.28966)[[15]](https://www.mindstudio.ai/blog/benchmark-gaming-ai-inflated-scores-explained). So I tried to find the trend from the number of empirical case-reports shared in online communities.

This piece tells the story of "small models challenging the closed frontier" inside three years of r/LocalLLaMA corpus (2023-03 → 2026-06-06, 118,391 posts + 1,787,788 comments), along **two complementary lines**:

1. **Beating on the boards** — the community claims a smaller model matches or surpasses a closed flagship (ChatGPT/GPT, Claude, Gemini, Grok) on benchmarks/hands-on tests. Out of 3,275 "punching-up" events I filter the **1,395 (43%)** that specifically target closed models, and look at who gets challenged, how many parameters it takes, and how solid the claims are (data source `capability_events.csv`).
2. **Replacing in real work** — whether people actually use small models to get real jobs done, even to the point of **canceling paid cloud**. This is a separate search yielding **981 real-task events** (data source `realtask_events.csv`), of which **22% explicitly replaced a cloud/paid model**.

Together: small models challenge the closed frontier not just as "I'm stronger" on the leaderboard, but as "good enough, and I'm in control" in real workflows — the former seeks to win and draws skepticism (31% pushed back on), the latter seeks sufficiency and the community barely argues (3.6% questioned).

The data is community **claims/self-reports**, not ground truth; the shares and counts are facts about the corpus, the conclusions are interpretations of those claims (and of community reception). The LLM extraction's second-pass review overturned ~9%/5% across the two lines; treat as "in-the-wild" evidence. Full method, the four-angle overview, and each line's limitations are in the Related Material at the end.

## By challenged vendor

| Challenged vendor | Events | Share | Most-named models |
|---|---|---|---|
| OpenAI (GPT / o* / ChatGPT) | 866 | 62% | GPT-4 (199), GPT-4o (118), GPT-3.5 (116) |
| Anthropic (Claude / Opus / Sonnet) | 258 | 18% | Claude 3.5 Sonnet (40), Claude Opus (25) |
| Generic "frontier / closed / cloud" | 143 | 10% | frontier, cloud models |
| Google Gemini | 116 | 8% | Gemini 2.5 Pro (16) |
| xAI Grok | 12 | 1% | — |

(GPT-OSS is excluded — it's OpenAI's open-weight model, not closed.) OpenAI is challenged far more than the other three combined, and more than half of those still target GPT-4 / GPT-4o / GPT-3.5, the "household-name" targets.

## Counterintuitive: the parameter budget is stuck at ~25–30B, but the opponent got several generations stronger

Year by year, the median parameter count of dense models that successfully challenged closed models in "core domains (general/coding/reasoning/agentic/math), community-not-skeptical":

| Year | Events | Median size | That year's opponent |
|---|---|---|---|
| 2023 | 121 | **13B** | GPT-3.5 |
| 2024 | 245 | 32B | GPT-4 / GPT-4o |
| 2025 | 211 | 22B | GPT-4o / o3-mini / Gemini 2.5 |
| 2026 | 109 | **27B** | GPT-5 / Claude Sonnet 4.6 / Gemini 3 Pro |

The parameter budget barely moved (always pinned in the 20–32B band); what changed is the opponent — from GPT-3.5 all the way up to GPT-5 / Gemini 3 Pro. **The gain in capability density shows up not as "fewer parameters" but as "the same ~25–30B now challenges a closed flagship several generations stronger."** MoE is a separate thread: things like Qwen3-30B-A3B (3B active) are already being put up against Gemini 2.5 Flash.

## The hardest subset: endorsed + hands-on "beat-the-closed" records (all 19)

Of the 1,395:

- Evidence: pure benchmark/lmarena 55% (762), hands-on 38% (533)
- Marketing tone: 16%
- Community reaction: **skeptical 429 (31%)**, mixed 212, clearly endorsed only 80 (6%), the rest without enough reply signal

The families issuing the challenges, by count: Qwen 374 (the dominant one), Llama 214, Gemma 79, Mistral 50, DeepSeek 41, GLM 31. Landmark high-score posts: Gemma 4 31B "destroyed every model" (challenging both Claude Sonnet 4.6 and Gemini 3 Pro, 1607 upvotes, endorsed)[[16]](https://reddit.com/r/LocalLLaMA/comments/1sdcotc/); Jan-nano (Qwen3-4B finetune) > Claude 3.7 Sonnet (890 upvotes, endorsed)[[17]](https://reddit.com/r/LocalLLaMA/comments/1ljyo2p/); GLM-4-32B > Gemini 2.5 Flash (577 upvotes, endorsed)[[18]](https://reddit.com/r/LocalLLaMA/comments/1k4god7/).

Cut the 1,395 twice more — **community clearly endorsed AND evidence is first-hand hands-on use (personal_use/anecdote, not benchmark scores)** — and only 19 posts remain (21 events deduped), listed in full by time (title links to the original post):

| Date | Small model | Challenged closed model | Domain | Upvotes | Original title |
|---|---|---|---|---|---|
| 2023-12-12 | Mixtral-8x7B (47B/13B active) | GPT-3.5 | general | 234 | [LLM Comparison/Test: Mixtral-8x7B, Mistral, DeciLM, Synthia-MoE](https://reddit.com/r/LocalLLaMA/comments/18gz54r/) |
| 2024-07-07 | Gemma 2 27B | ChatGPT-3.5 | creative | 29 | [Any worthy Gemma 2 27B finetunes for writing/RP?](https://reddit.com/r/LocalLLaMA/comments/1dxpc4r/) |
| 2024-11-01 | Qwen2.5-14B | GPT-4o | agentic | 173 | [IMO the best model for agents: Qwen2.5 14b](https://reddit.com/r/LocalLLaMA/comments/1gheq9t/) |
| 2024-11-14 | Qwen2.5-Coder-32B | GPT-4o | coding | 291 | [Qwen 32B Coder-Ins vs 72B-Ins on the latest Leetcode problems](https://reddit.com/r/LocalLLaMA/comments/1gr35xp/) |
| 2024-11-28 | QwQ-32B (4bit quant) | o1-preview / o1-mini | reasoning | 208 | [I ran my misguided attention eval locally on QwQ-32B 4bit quantized and it beats o1-preview and o1-mini](https://reddit.com/r/LocalLLaMA/comments/1h1u7r9/) |
| 2025-03-06 | QwQ-32B | o3-mini (med/high) | math | 168 | [new QwQ is beating any distil deepseek model in math … level o3 mini med/high](https://reddit.com/r/LocalLLaMA/comments/1j4x8sq/) |
| 2025-03-21 | Mistral Small 3.1 (24B) | GPT-4o Mini | vision | 60 | [Mistral-small 3.1 Vision for PDF RAG tested](https://reddit.com/r/LocalLLaMA/comments/1jg5sbj/) |
| 2025-04-17 | Gemma 3 27B | ChatGPT (GPT-3.5 Turbo) | general | 335 | [Medium sized local models already beating vanilla ChatGPT - Mind blown](https://reddit.com/r/LocalLLaMA/comments/1k1av1x/) |
| 2025-04-21 | GLM-4-32B | Gemini 2.5 Flash | coding | 577 | [GLM-4 32B is mind blowing](https://reddit.com/r/LocalLLaMA/comments/1k4god7/) |
| 2025-07-30 | Qwen3-30B-A3B-thinking (3B active) | Gemini 2.5 Flash | general | 463 | [Qwen3-30b-a3b-thinking-2507 This is insane performance](https://reddit.com/r/LocalLLaMA/comments/1md8slx/) |
| 2025-08-08 | Granite 3 8B | GPT-5 mini/nano | agentic | 203 | [Granite 3 8B is seriously underrated - still outperforming newer models](https://reddit.com/r/LocalLLaMA/comments/1mkp0am/) |
| 2025-12-19 | Qwen 8B | cloud models | agentic | 29 | [I've been experimenting with SLM's a lot recently … prove even SLMs can be accurate](https://reddit.com/r/LocalLLaMA/comments/1pqd7sy/) |
| 2026-01-21 | distilled Text2SQL 0.6B | GPT-class models | coding | 162 | [Knowledge distillation with Claude as the interface: trained a 0.6B model to match GPT-class performance on Text2SQL](https://reddit.com/r/LocalLLaMA/comments/1qiu6jo/) |
| 2026-03-30 | Qwen 3.5-27B | frontier (agentic text-to-SQL) | coding | 196 | [I tested as many of the small local and OpenRouter models I could with my own agentic text-to-SQL benchmark. Surprises ensured…](https://reddit.com/r/LocalLLaMA/comments/1s7r9wu/) |
| 2026-04-06 | Gemma 4 26B | Gemini 3 Flash | agentic | 136 | [Gemma4:26b's reasoning capabilities are crazy](https://reddit.com/r/LocalLLaMA/comments/1sdz71b/) |
| 2026-04-09 | Gemma 4 31B (UD IQ3 XXS quant) | Claude Opus 4.6 | general | 847 | [It's insane how lobotomized Opus 4.6 is right now. Even Gemma 4 31B UD IQ3 XXS beat it on the carwash test on my 5070 TI](https://reddit.com/r/LocalLLaMA/comments/1sgd7fp/) |
| 2026-04-24 | Qwen 3.6 27B | Claude Sonnet 4.6 | coding | 133 | [Opinion: Qwen 3.6 27b Beats Sonnet 4.6 on Feature Planning](https://reddit.com/r/LocalLLaMA/comments/1supft2/) |
| 2026-05-05 | Qwen 3.6 27B | cloud models | coding | 635 | [DeepSeek V4 being 17x cheaper got me to actually measure what I send to cloud vs what I could run locally](https://reddit.com/r/LocalLLaMA/comments/1t4s6g2/) |
| 2026-05-11 | Qwen 3.6 35B-A3B (3B active) | frontier | coding | 419 | [The Qwen 3.6 35B A3B hype is real!!!](https://reddit.com/r/LocalLLaMA/comments/1t9whrt/) |

Read these 19 with two discounts: (1) they're **hands-on impressions** — mostly single-person, single-task, custom evals, not systematic evaluation — "good enough for my job" ≠ "comprehensively superior"; (2) many titles carry emotion ("mind blowing", "insane", "lobotomized Opus"), strong on social proof but weak on reproducibility. Even so, the commonality is solid: **the domains nearly all fall in coding/agentic/reasoning — the work local users actually do every day — sizes cluster at 24–32B (plus two MoE with 3B active and one 0.6B distilled task-specific model), and the opponent climbs from 2023's GPT-3.5 to 2026's Claude Opus 4.6 / Sonnet 4.6 / Gemini 3** — corroborating the "parameters stuck at ~25–30B while the opponent got several generations stronger" conclusion.

⚠ Interpretation: the 2026 entries (Gemma 4, Qwen 3.5/3.6, opponents in the GPT-5 series / Claude 4.6 / Gemini 3) are beyond independent verification; **the primary source is the r/LocalLLaMA discussion itself at the time** (see the in-table permalinks), and this piece does not vouch for their external benchmark truth.

The next two sections come from the companion "small models getting real tasks done" search (another line on the same corpus, 913 posts / 981 real-task events) — **challenging the closed frontier happens not only on benchmarks but in real workflows**: people actually use small models to do work, even canceling paid cloud. The counts below (event counts, the 22%, etc.) are all based on those 981 real-task events; full method and limitations are in the Related Material.

## What kinds of work small models do

By task domain (success + partial combined):

| Domain | 23 | 24 | 25 | 26* | Total | Typical uses |
|---|---|---|---|---|---|---|
| coding | 16 | 44 | 83 | 71 | 214 | code completion, coding agents, debugging, full-stack vibe coding |
| general | 21 | 60 | 57 | 43 | 181 | everyday Q&A, rewriting, email, odd-job assistant |
| agentic | 15 | 22 | 48 | 58 | 143 | multi-agent orchestration, tool calls, memory layer, scheduled tasks |
| rag | 16 | 35 | 25 | 6 | 82 | local document Q&A, knowledge-base retrieval |
| data-extraction | 4 | 22 | 22 | 13 | 61 | structuring transcripts/files, extracting JSON, classification |
| writing | 11 | 21 | 18 | 9 | 59 | copy polishing, de-"AI-ifying", long-form writing |
| roleplay | 13 | 18 | 18 | 7 | 56 | role-play, interactive storytelling |
| summarization | 5 | 19 | 10 | 5 | 39 | meeting / medical / document summaries |
| voice | 1 | 6 | 15 | 14 | 36 | local voice assistant |
| vision-ocr | 1 | 7 | 14 | 14 | 36 | OCR, image understanding, video analysis |
| research | 1 | 11 | 6 | 6 | 24 | automated search & scraping, cited research reports |
| home-automation | 0 | 4 | 9 | 7 | 20 | Home Assistant smart home |
| translation | 0 | 6 | 6 | 1 | 13 | domain-specific translation |

The time trend is clear: **coding (16→44→83→71) and agentic (15→22→48→58) surge year over year**, the main battlegrounds of 2025–2026; **rag (peaked at 35 in 2024 → only 6 in 2026), roleplay, and general decline in share**; voice / vision-ocr rise steadily from nothing. The center of gravity shifts visibly from "chat/retrieval" to **coding + agentic**, the "dirty work people actually have to do every day." Over half the events (**529, 54%**) are users who **built an app/agent/tool/pipeline around** the small model — the model is embedded as a **component** in a system, not used as a chat toy (\* 2026 is Jan–Jun only).

By year, each domain's curve (one line per domain, the number in the legend parentheses is that domain's total events; **2026 has only Jan–Jun data, annualized ×2.36 assuming a uniform full-year rate**, so the 2025→2026 segment is dashed to mark it as an estimate; 2023 starts in March and is itself low, not annualized):

![Yearly event counts by task domain](realtask_domain_yearly%20(2026-06-06).png)

The trend is obvious at a glance: **coding annualizes to ~167 (83 in 2025, nearly double), agentic to ~137 (48 in 2025)**, the two lines spiking sharply in 2026 and pulling away from the rest; general annualizes to ~101, growth slowing after a 2024 peak; rag declines year over year after peaking (35) in 2024. ⚠ Annualization assumes a uniform full-year rate, but H1 2026 happens to coincide with coding/agentic monthly highs, so the real full-year figures may not extrapolate linearly this high — treat as estimates.

High-score examples of success per domain (title links to the original post):

| Date | Domain | Model | Task | Upvotes | Post |
|---|---|---|---|---|---|
| 2024-11-20 | research | Phi 3.8B/14B | automated search & scraping + cited research report | 1286 | [I Created an AI Research Assistant that actually DOES research](https://reddit.com/r/LocalLLaMA/comments/1gvlzug/) |
| 2026-05-18 | coding | Gemma 4 4B (4B active) | coding agent (SmallCode), 87% on benchmark | 754 | [I built a coding agent that gets 87% on benchmarks with a 4B parameter model](https://reddit.com/r/LocalLLaMA/comments/1tgecrq/) |
| 2026-03-05 | agentic | Qwen 3.5 9B | a real agent on M1 Pro 16GB (not a demo) | 887 | [Ran Qwen 3.5 9B on M1 Pro (16GB) as an actual agent, not just a chat demo](https://reddit.com/r/LocalLLaMA/comments/1rll349/) |
| 2024-05-10 | summarization | Phi-3 3B (finetuned) | SOAP summaries from medical dialogue for clinicians | 332 | [3B Model Beating GPT4 on Medical Summarisation](https://reddit.com/r/LocalLLaMA/comments/1cp2h1v/) |
| 2025-09-01 | data-extraction | Llama 3.2 3B (finetuned) | transcript analysis into structured JSON | 231 | [I fine-tuned Llama 3.2 3B for transcript analysis](https://reddit.com/r/LocalLLaMA/comments/1n5w9yy/) |
| 2025-01-09 | vision-ocr | Moondream 2B | gaze detection on arbitrary video | 238 | [Moondream 2B's new gaze detection](https://reddit.com/r/LocalLLaMA/comments/1hxm0ep/) |
| 2025-09-13 | roleplay | GPT-OSS 20B | multi-agent role-play terminal game | 380 | [I made a game using LLMs (gpt-oss:20b) — Among LLMs](https://reddit.com/r/LocalLLaMA/comments/1nfrzbv/) |
| 2024-09-22 | general | Gemma 2B | local file auto-organizer | 324 | [I built an AI file organizer that reads and sorts your files, running 100% on your device](https://reddit.com/r/LocalLLaMA/comments/1fn3aee/) |

## 22% "canceled the cloud": local small models replacing paid subscriptions

215 events (**22%**) explicitly report **replacing a cloud/paid model with a local small model** for the job. Most-replaced: ChatGPT (22), Claude (7), GPT-4 API (6), GPT-4 (6), GPT-4o-mini (4), Claude Code (4), GitHub Copilot (3).

By year, the **cloud-replacement share rises steadily**:

| | 2023 | 2024 | 2025 | 2026* | Total |
|---|---|---|---|---|---|
| Replaced cloud | 18 | 56 | 75 | 66 | 215 |
| Local-native | 88 | 226 | 262 | 190 | 766 |
| Replacement share | 17% | 20% | 22% | 26% | 22% |

(\* 2026 is Jan–Jun only.) From 17% in 2023 to 26% in 2026 — the later it gets, the more people are not "just running something locally on the side" but **actively canceling a paid subscription to switch to a local small model**.

By the cloud being replaced, the yearly curves (one line per replaced target, 2026 also annualized ×2.36, dashed final segment = estimate):

![Yearly curves of cloud-replacement events by replaced vendor](realtask_replaced_cloud_yearly%20(2026-06-06).png)

The replacement target itself is **changing hands**: **ChatGPT/OpenAI (blue) peaked (35) in 2024 then fell back** to ~26 annualized in 2026; while **Claude/Anthropic (green) went 1→5→16→61 annualized, and generic cloud (orange) 1→9→27→61 annualized**, both overtaking ChatGPT in 2026 as the top replacement target. This matches the timing of agent tools like Claude Code catching fire — first popular and widely adopted, then treated by local small models as "the subscription to cut." GitHub Copilot and Gemini stay small throughout. ⚠ Also an annualized estimate — read the trend, not exact values. High-score examples:

| Model | Replaced | Task | Upvotes | Post |
|---|---|---|---|---|
| Qwen 3.5 9B | Claude Code | memory/tool calls in a personal automation agent | 887 | [Ran Qwen 3.5 9B on M1 Pro as an actual agent](https://reddit.com/r/LocalLLaMA/comments/1rll349/) |
| DeepSeek-R1 distill 8B | ChatGPT Plus / o1 | everyday reasoning tasks | 652 | [Just canceled my ChatGPT Plus subscription](https://reddit.com/r/LocalLLaMA/comments/1if5q97/) |
| Qwen 3.6 27B | cloud subscription | PySpark/Python data-transform debugging + tool calls | 599 | [Qwen 3.6 27B is a BEAST](https://reddit.com/r/LocalLLaMA/comments/1steip4/) |
| DeepSeek-R1 14B | OpenAI Plus | everyday tasks (incl. privacy-sensitive personal finance) | 505 | [(same discussion thread)](https://reddit.com/r/LocalLLaMA/comments/1if5q97/) |
| Phi-3 3B (finetuned) | GPT-4 | medical SOAP summaries | 332 | [3B Model Beating GPT4 on Medical Summarisation](https://reddit.com/r/LocalLLaMA/comments/1cp2h1v/) |
| Gemma 2B | Groq API | local file auto-organizer | 324 | [I built an AI file organizer … 100% on your device](https://reddit.com/r/LocalLLaMA/comments/1fn3aee/) |
| Qwen3.6-27B Q8 | GitHub Copilot | everyday coding help in VSCode | 251 | [(Qwen 3.6 27B thread)](https://reddit.com/r/LocalLLaMA/comments/1steip4/) |

The recurring reason for replacement is not "stronger" but **cost, privacy, control, offline** — privacy-sensitive scenarios (personal finance, medical, local files) especially favor local. This is a completely different motive from the punching-up claims: punching up seeks "to win," replacing cloud seeks "good enough, and I call the shots."

## Related material

- Companion search (the full versions of the "what work small models do" + "22% canceled the cloud" sections + quality/size/hardware stats + limitations + Haiku/Sonnet prompts): [小模型干成真实任务 (2026-06-06).md](小模型干成真实任务%20(2026-06-06).md) — the data in the two sections above all comes from that piece's Level-2 extraction `realtask_events.csv` (981 real-task events).
- The parent piece (four-angle overview + full extraction pipeline + Haiku/Sonnet prompts): [LocalLLaMA能力密度挖掘 (2026-06-06).md](LocalLLaMA能力密度挖掘%20(2026-06-06).md) — this piece's vendor distribution, yearly median size, quality stats, and the 19-record hard subset all come from that piece's Level-2 extraction `capability_events.csv`.

## References

[1] TheStreet, "Stock Market Today (June 5, 2026): Nasdaq falls 4% as semiconductor slide wipes $1T from markets," Jun 2026. (S&P -2.6%, Nasdaq -4.2%, worst since October, chip stocks led the drop.) [Online]. Available: <https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-june-05-2026>

[2] NPR, "AI giant Anthropic prepares to sell stock to the public; files preliminary IPO paperwork," Jun 1, 2026. (Anthropic filed a draft S-1, valuation ~$965B.) [Online]. Available: <https://www.npr.org/2026/06/01/nx-s1-5843199/anthropic-ipo-filing-ai-large>

[3] CNBC, "My guide to the IPOs of SpaceX, OpenAI and Anthropic," May 31, 2026. (SpaceX S-1 public, pricing ~6/12; OpenAI confidential filing; the three may draw $200B+ combined.) [Online]. Available: <https://www.cnbc.com/2026/05/31/my-guide-to-the-ipos-of-spacex-openai-and-anthropic-including-the-one-i-really-want-to-buy.html>

[4] CNBC, "Alphabet seeking $85 billion with stock facing 4-week losing streak," Jun 5, 2026. (Alphabet priced ~$84.75B equity raise on 6/2 for AI compute; 2026 capex projected $180–190B.) [Online]. Available: <https://www.cnbc.com/2026/06/05/alphabet-ai-data-center-financing.html>

[5] CNBC, "Google to pay SpaceX $920 million a month for compute capacity at xAI data centers," Jun 5, 2026. (Oct 2026 – Jun 2029, $920M/month, ~110,000 NVIDIA GPUs; ~$11B/year, ~$30B total over the term; disclosed one week before the IPO.) [Online]. Available: <https://www.cnbc.com/2026/06/05/google-to-pay-spacex-920-million-a-month-for-xai-compute-capacity.html>

[6] Hacker News, "Google to pay SpaceX $920M a month for compute capacity at xAI data centers" (comment by harmmonica), Jun 2026. (Google invested in SpaceX in 2015; at a $1.5T valuation its diluted stake is ~$80–100B, the contract sends ~$12B/year back, ~12% of the stake.) [Online]. Available: <https://news.ycombinator.com/item?id=48417490>

[7] D. Amodei, "On DeepSeek and Export Controls," *darioamodei.com*, Jan 2025. (Argues for stronger chip export controls on China, claiming this lets the US and allies build a "long-lasting lead" and keeps competitors from catching up.) [Online]. Available: <https://www.darioamodei.com/post/on-deepseek-and-export-controls>

[8] Anthropic, "Anthropic is endorsing SB 53," *anthropic.com*, 2025. (Endorses California frontier-AI safety legislation requiring frontier developers to adopt mandatory safety standards.) [Online]. Available: <https://www.anthropic.com/news/anthropic-is-endorsing-sb-53>

[9] D. Sacks (US AI czar), "Anthropic Has A Pattern Of Using Fear To Market Its Products," *OfficeChai*, Apr 11, 2026. (Says Anthropic "has a pattern of using fear" to market products, and previously called it a "regulatory capture strategy based on fear-mongering," timing alarmist safety studies to coincide with new model releases.) [Online]. Available: <https://officechai.com/ai/anthropic-has-a-pattern-of-using-fear-to-market-its-products-us-ai-czar-david-sacks/>

[10] H. Zhang et al., "A Careful Examination of Large Language Model Performance on Grade School Arithmetic," *arXiv preprint*, arXiv:2405.00332, May 2024. (Built a fresh GSM1k set; leading models drop up to 13% accuracy; Phi/Mistral and others systematically overfit GSM8k.) [Online]. Available: <https://arxiv.org/abs/2405.00332>

[11] S. Singh et al., "The Leaderboard Illusion," *arXiv preprint*, arXiv:2504.20879, Apr 2025. (Analyzes 2M Chatbot Arena battles; private testing, selective disclosure, and data-access imbalance — Meta tested 27 private variants before Llama-4.) [Online]. Available: <https://arxiv.org/abs/2504.20879>

[12] Anon., "LLM Benchmark Datasets Should Be Contamination-Resistant," *arXiv preprint*, arXiv:2605.19999, May 2026. (Recent studies measure up to 45% contamination on common benchmarks.) [Online]. Available: <https://arxiv.org/abs/2605.19999>

[13] Digital Applied, "LLM Benchmark Methodology 2026: Reading Leaderboards," Jun 2026. (Every widely-cited static benchmark is contaminated to some degree; MMLU etc. saturated above 88% with near-noise score gaps; identical weights score 10–20 points apart across eval harnesses.) [Online]. Available: <https://www.digitalapplied.com/blog/llm-benchmark-methodology-2026-contamination-leaderboard-guide>

[14] "The Trust Paradox: How CS Researchers Engage LLM Leaderboards," *arXiv preprint*, arXiv:2605.28966, May 2026. (CS researchers keep using leaderboards in practice despite knowing their reliability and robustness are limited.) [Online]. Available: <https://arxiv.org/abs/2605.28966>

[15] MindStudio, "What Is Benchmark Gaming in AI? Why Self-Reported Scores Are Often Inflated," Apr 7, 2026. (Kimi K2 self-reported 50% on Humanity's Last Exam vs 29.4% on independent re-testing, a 20-point gap.) [Online]. Available: <https://www.mindstudio.ai/blog/benchmark-gaming-ai-inflated-scores-explained>

[16] r/LocalLLaMA, "Gemma 4 just casually destroyed every model on our leaderboard," Apr 2026. (1607 upvotes; challenges both Claude Sonnet 4.6 and Gemini 3 Pro.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1sdcotc/>

[17] r/LocalLLaMA, "Jan-nano-128k: A 4B Model … Still Outperforms 671B," Jun 2025. (890 upvotes; Qwen3-4B finetune > Claude 3.7 Sonnet.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1ljyo2p/>

[18] r/LocalLLaMA, "GLM-4 32B is mind blowing," Apr 2025. (577 upvotes; > Gemini 2.5 Flash.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1k4god7/>
