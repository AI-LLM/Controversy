# 2026-06-06: The "Capability-Density" Curve in Three Years of r/LocalLLaMA — How Small Models Kept Catching Up to the Big Ones

Pulling all 118,391 posts + 1,787,788 comments of r/LocalLLaMA from 2023-03 to 2026-06-06 and doing structured extraction by parameter scale reveals a curve closer to the "what actually works" feel than any leaderboard: **for the same capability, the parameter count needed keeps dropping over three years**. In 2023 it took 30–70B to dare challenge GPT-3.5/GPT-4; by 2026 the community puts 27–31B on the table against GPT-5-class closed models, and MoE has pushed "active parameters" down to single-digit B.

The four sections below are: the timeline of punching-up claims (capability density), the migration of community attention across sizes, the family×size layout, and — the most important one — **how marketing clickbait and hands-on reputation diverge by size**.

The data is community **claims**, not ground truth. The shares and counts in this piece are facts about the corpus; "capability density is rising" is an interpretation of those claims (and of the community's own reception data). Of the 3,275 LLM-extracted events, the second pass overturned ~9% (see the method section); read as "in-the-wild" evidence.

## I. The capability-density curve: the timeline of "small beats big"

From the corpus I extracted 3,275 "a smaller model matches/surpasses a bigger or frontier model" events; taking general/reasoning/coding/agentic domains, community-not-uniformly-skeptical, with post date = event date, the high-attention landmark milestones by quarter:

| Quarter | Small model | Model beaten | Domain | Upvotes | Community reaction |
|---|---|---|---|---|---|
| 2023Q2 | phi-1 **1.3B** | GPT-3.5 | coding | 433 | endorsed |
| 2023Q2 | WizardLM-30B | GPT-4 | reasoning | 123 | mixed |
| 2023Q3 | Mistral-7B-v0.1 | 13B | general | 170 | endorsed |
| 2023Q4 | Mixtral-8x7B (**47B/12.9B active**) | Llama 2 70B | general | 234 | endorsed |
| 2024Q1 | Mistral-7B (ReAct finetune) | Gemini Pro | agentic | 253 | mixed |
| 2024Q4 | Llama **3B** + test-time search | Llama 70B | reasoning/math | 773 | endorsed |
| 2025Q1 | OLMo 2 **32B** | GPT-4o mini / GPT-3.5 | general | 1551 | endorsed |
| 2025Q2 | Qwen3-**4B** | 72B | general | 1768 | endorsed |
| 2025Q2 | Qwen3-30B-**A3B** | 32B (dense) | general | 1768 | endorsed |
| 2025Q3 | Qwen3-30B-A3B-thinking | 235B | reasoning | 463 | endorsed |
| 2026Q1 | Qwen2.5-Coder-32B (PewDiePie finetune) | ChatGPT-4o | coding | 743 | mixed |
| 2026Q2 | Gemma 4 **31B** | GPT-5.2 / Gemini 3 Pro | agentic | 1607 | endorsed |

The two columns come from different places, don't conflate them: **Upvotes** is the post's raw Reddit score (an objective count); **Community reaction** is Sonnet's read of the post's high-upvote replies (top_replies, linked via `link_id`) combined with the score, judging whether the community bought it — across four levels: endorsed (most replies agree, marked "endorsed" here) / mixed (replies split) / skeptical (most replies doubt/debunk) / none (not enough reply signal). It is the **LLM's read of actual comment content, not a mechanical conversion from upvotes** — a high-upvote post can still be "mixed" (e.g., the Qwen2.5-Coder-32B one with 743 upvotes, where the comments argued over "training-set contamination / benchmark gaming"). This milestone table has filtered out the skeptical tier (community-uniformly-questioned items don't count as milestones).

Four verifiable historical anchors:

- **phi-1 (1.3B)**: trained on GPT-3.5-synthesized "textbook-quality" data, HumanEval pass@1 50.6%, surpassing the contemporaneous GPT-3.5's coding level [[1]](https://arxiv.org/abs/2306.11644). The first breakout sample of "data quality for parameter count."
- **Mixtral-8x7B**: sparse MoE, 46.7B total but only 12.9B activated per token; both official and community evals see it matching Llama 2 70B and GPT-3.5 [[2]](https://mistral.ai/news/mixtral-of-experts). The first time "looks like a 7B, smart like a 70B" became real.
- **Llama 3B + test-time compute**: Hugging Face used step-level reward models + DVTS tree search to let 3B match 70B on MATH-500 [[3]](https://huggingface.co/posts/lewtun/679536201490974). Capability can shift from "parameters" to "inference-time compute."
- **QwQ-32B**: RL pushed a 32B's reasoning to the level of DeepSeek-R1 (671B, 37B active), AIME24 79.5% vs R1 79.8% [[4]](https://qwenlm.github.io/blog/qwq-32b/). A model that fits on a single 24GB card challenges one that needs a whole rack.

This curve has two independent declines stacked: one is the **capability density of dense models** itself rising (13B→7B→4B each catching up to the prior generation's big brother); the other is **MoE decoupling "active parameters" from total** — Qwen3-30B-A3B is 30B total but activates only 3B per token, yet gets put up against 235B. By 2026, "a few B beating a few hundred B" has gone from a hyperbolic headline to everyday phrasing.

⚠ Interpretation: the 2026 entries (Gemma 4 31B, Qwen 3.5/3.6 27B, opponents GPT-5.2/Gemini 3 Pro) are beyond independent verification; **the primary source is the r/LocalLLaMA discussion itself at the time** (see the reference permalinks), and this piece does not vouch for their external benchmark truth; community reception of these claims is in section IV.

### Targeting the closed frontier: 1,395 events challenging ChatGPT / Claude / Gemini

Of the 3,275 punching-up events, **1,395 (43%) target a closed/frontier flagship** (OpenAI 866, Anthropic 258, Gemini 116, Grok 12, plus 143 generic "frontier/cloud"; GPT-OSS and other open weights excluded). A counterintuitive structure: **the parameters needed to challenge closed models did not keep dropping — they're stuck at ~25–30B — but the opponent climbed from GPT-3.5 all the way to GPT-5 / Gemini 3 Pro**. Cut further to "community clearly endorsed + first-hand hands-on (not benchmark scores)" and the whole corpus leaves only 19 hard records.

That thread is its own piece, with vendor distribution, yearly median size, benchmaxx quality, and all 19 hands-on records (with original-post links): [small-models-vs-closed-frontier (2026-06-06).md](small-models-vs-closed-frontier%20(2026-06-06).md).

## II. Sweet-spot migration: 13B/70B exit, 20-34B and 100B+ MoE rise

Counting posts with a parameter size by month, then computing "each month's share of each size bucket out of total size mentions" (self-normalizing, canceling both total-volume and size-labeling-rate confounds). Quarterly shares (%):

| Quarter | <1B | 1-3B | 4-6B | 7-9B | 11-15B | 20-34B | 40-49B | 65-72B | 100B+ |
|---|---|---|---|---|---|---|---|---|---|
| 2023Q2 | 0 | 3 | 1 | 20 | 28 | 27 | 2 | 16 | 3 |
| 2023Q4 | 0 | 5 | 1 | **33** | 17 | 16 | 1 | 20 | 7 |
| 2024Q2 | 0 | 5 | 2 | **37** | 7 | 14 | 1 | **26** | 8 |
| 2024Q4 | 2 | 14 | 1 | 20 | 11 | 20 | 1 | 22 | 10 |
| 2025Q2 | 2 | 8 | 6 | 14 | 12 | **35** | 1 | 10 | 12 |
| 2025Q3 | 2 | 7 | 8 | 10 | 8 | 33 | 2 | 7 | **24** |
| 2026Q1 | 2 | 9 | 7 | 15 | 5 | 33 | 1 | 5 | 23 |
| 2026Q2 | 1 | 6 | 5 | 10 | 4 | **55** | 1 | 3 | 16 |

Three clear trends:

- **The "70B is king" tier (65-72B) collapses**: 26% in 2024Q2, down to 3% by 2026Q2. Llama 2/3's 70B was once the byword for local high-end; now almost no one mentions it.
- **The "13B era" (11-15B) dies out**: from 28% in 2023 down to 4%. This once consumer sweet-spot got squeezed from both sides — by 7-9B (cheaper) and 20-34B (stronger).
- **20-34B becomes the new king**: from single-digit share to 55% in 2026Q2. Qwen 32B, Gemma 27/31B, QwQ-32B — this tier sits right at "runs on a single 24–32GB card + capability good enough to top out."
- **100B+ MoE rises**: from near 0 to a steady 23–25% since 2025Q3. The big MoE from DeepSeek, GLM, Kimi, Qwen pulled the "hundred-B class" back into local players' view.

Why the migration? Hardware co-mentions give driving evidence. Counting GPU/memory mentions by quarter, since 2025Q3 **128GB/64GB mentions rise markedly** (in sync with 100B+ MoE), while **24GB (3090/4090) is always the main workbench** — the 3090 has been in the quarterly Top 3 for three years. Add the spread of GGUF/quantization (Q4_K_M, IQ3, GGUF stay high-frequency among quant mentions), and big models get "squeezed" into consumer VRAM, which is what brought 100B+ MoE and 20-34B dense models into the locally-runnable range at the same time.

## III. Family × size × time: which cell each vendor occupies

Aggregating 17 model families by size bucket (n = family total mentions, primary tiers = buckets with ≥10% share):

| Family | Mentions | Active span | Primary size tiers |
|---|---|---|---|
| Qwen | 84,682 | 2023-08 ~ now | **20-34B (41%)**, 7-9B, 100B+ |
| Llama | 70,576 | 2023-03 ~ now | 7-9B (25%), **65-72B (21%)**, 20-34B |
| Gemma | 27,105 | 2024-02 ~ now | **20-34B (42%)**, 7-9B, 11-15B |
| Mistral | 26,487 | 2023-09 ~ now | 7-9B (33%), 20-34B, 11-15B |
| DeepSeek | 15,224 | 2023-11 ~ now | 20-34B, **100B+ (22%)**, 65-72B |
| Mixtral | 7,829 | 2023-12 ~ 2026-05 | **7-9B (44%, i.e. 8x7B)**, 20-34B |
| GLM | 4,746 | 2023-04 ~ now | 20-34B, **100B+ (32%)** |
| Phi | 4,563 | 2023-06 ~ now | 1-3B, 7-9B, 11-15B (**small-model specialist**) |
| Kimi | 3,081 | 2023-12 ~ now | 20-34B, **100B+ (37%)** |

The landscape that reads out: **Qwen is the king of the 20-34B sweet spot** (84k mentions for one family, 41% pinned in this tier), and the biggest beneficiary of this migration; **Llama is the old 70B king**, its center of gravity still on the exiting 65-72B; **Mixtral popularized the 8x7B notation then faded with it** (last mention 2026-05); **DeepSeek/GLM/Kimi cluster in 100B+ MoE**, the mainstays of the big-MoE revival; **Phi holds the 1-7B small-model-specialist spot**, the representative of the "small but sharp" route.

## IV. Marketing clickbait vs hands-on reputation: the smaller the model, the more it leans on benchmarks

This is the most information-dense of the four angles. Bucketing each punching-up event by small-model size and tallying evidence type and community reaction:

| Small-model tier | Events | Marketing tone | Benchmark-only | Has hands-on evidence | Community skeptical |
|---|---|---|---|---|---|
| <7B | 544 | **29%** | **63%** | 26% | 27% |
| 7-15B | 991 | 15% | 56% | 36% | 30% |
| 20-34B | 963 | **7%** | 46% | **50%** | **21%** |
| 40-72B | 333 | 15% | 56% | 38% | 27% |
| 100B+ | 240 | 10% | 48% | 46% | 25% |

The pattern is clean: **the smaller the model, the more the punching-up claim rests on benchmarks and marketing**. In the <7B tier, 29% are marketing-announcement tone, 63% have only benchmark scores, and only 26% have real-use corroboration; while the **20-34B sweet spot is exactly the opposite** — only 7% marketing tone, half with hands-on evidence, the lowest community-skepticism rate of all (21%). In other words, small models' "punching up" is often benchmaxx clickbait, while the 20-34B tier is what the community **actually uses and actually endorses**.

The community's immunity to benchmaxx is also written into the corpus. Debunking recurs in high-score posts:

- "Stop asking what model to run. There are literally only two." [2340 upvotes] [[5]](https://reddit.com/r/LocalLLaMA/comments/1tu82wi/stop_asking_what_model_to_run_there_are_literally/) — a jab at the wall-to-wall punching-up posts.
- "I am sorry but the technical report screams 'training on test'" [605 upvotes] [[6]](https://reddit.com/r/LocalLLaMA/comments/1mfitwb/skywork_mindlink_32b72b/) — direct skepticism at 32B/72B benchmark gaming.
- "No it is not R1 equivalent" [605 upvotes] [[7]](https://reddit.com/r/LocalLLaMA/comments/1ikgsl6/germany_we_released_model_equivalent_to_r1_back/) — slapping down "we already made an R1-class model."
- The reverse also exists: gemma 3 27b "underrated af, #11 at lmarena, matches o1" [555 upvotes] [[8]](https://reddit.com/r/LocalLLaMA/comments/1k2kl84/gemma_3_27b_is_underrated_af_its_at_11_at_lmarena/) — the community endorsing a small model with solid hands-on results.

Overall, of the 3,275 events, half (1,735) have evidence type of pure benchmark/lmarena, ~41% (1,342) have hands-on (personal_use/anecdote); community reaction is clearly skeptical for 863, clearly endorsed for only 206. **"Small beats big" is a real trend, but every specific claim needs a benchmaxx discount subtracted** — and that discount is thickest in the small-model tier.

## Method & data

- **Corpus**: full r/LocalLLaMA, 118,391 posts + 1,787,788 comments, 2023-03-10 → 2026-06-06 (incremental dumps deduped and merged into the main files, `scripts/merge_reddit_dumps.py`).
- **Level-1 (regex)**: `analyze_reddit.py --mode capability` extracts parameter sizes (including MoE N×M and active notation), model families, hardware/quant co-mentions, and cross-size comparison flags; 220,287 hits, producing `capability_mentions.csv` and the four-angle aggregate `capability_aggregates.json`. The size regex uses negative lookbehind to exclude false hits like `24GB`/`$7B`/`4bit`.
- **Level-2 (LLM)**: two-stage extraction over 7,875 candidates (cross-size comparison + has size + score≥5) — Haiku classification filter (verified_underdog 1,493, benchmark_only 951, refuted 793, etc.), Sonnet extracting structured `events[]` for positives (small model / size / beaten target / domain / evidence type / timing / marketing / community reaction). 3,275 events total. LLM calls always go through Claude Code subagents (Workflow), not the API.
- **Known limitations**: (1) events are community **claims**; Sonnet's second pass overturned ~9% (286/3,275), and benchmaxx claims may still slip through; (2) community reaction is based on a post's high-upvote replies + upvote-count proxy, not full comment-tree sentiment analysis; (3) 2026 models are beyond independent verification, with Reddit discussion as the primary source; (4) "post date ≠ event effective date" is distinguished by the timing field at extraction time, and only immediate-type entries are taken into milestones.

## References

[1] S. Gunasekar et al., "Textbooks Are All You Need," *arXiv preprint*, arXiv:2306.11644, Jun 2023. (phi-1 1.3B, HumanEval pass@1 50.6%.) [Online]. Available: <https://arxiv.org/abs/2306.11644>

[2] Mistral AI, "Mixtral of experts," *Mistral AI News*, Dec 2023. (8x7B, 46.7B total / 12.9B active, matching Llama 2 70B and GPT-3.5.) [Online]. Available: <https://mistral.ai/news/mixtral-of-experts>

[3] L. Tunstall, E. Beeching, et al., "Scaling Test-Time Compute," *Hugging Face*, Dec 2024. (Llama 3B matching 70B on MATH-500 via DVTS tree search.) [Online]. Available: <https://huggingface.co/posts/lewtun/679536201490974>

[4] Qwen Team, "QwQ-32B: Embracing the Power of Reinforcement Learning," *Qwen Blog*, Mar 2025. (32B matching DeepSeek-R1 671B/37B active; AIME24 79.5 vs 79.8.) [Online]. Available: <https://qwenlm.github.io/blog/qwq-32b/>

[5] r/LocalLLaMA, "Stop asking what model to run. There are literally only two," Jun 2026. (2340 upvotes.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1tu82wi/>

[6] r/LocalLLaMA, "Skywork MindLink 32B/72B — 'training on test'," Aug 2025. (605-upvote skeptical reply.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1mfitwb/>

[7] r/LocalLLaMA, "Germany: we released model equivalent to R1 — 'No it is not R1 equivalent'," Feb 2025. (605-upvote skeptical reply.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1ikgsl6/>

[8] r/LocalLLaMA, "gemma 3 27b is underrated af, #11 at lmarena, matches o1," Apr 2025. (555 upvotes.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1k2kl84/>

[9] r/LocalLLaMA, "HuggingFace researchers got 3b Llama to outperform 70b using search," Dec 2024. (773 upvotes.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1hgybhg/>

[10] r/LocalLLaMA, "AI2 releases OLMo 2 32B," Mar 2025. (1551 upvotes.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1jaj6gc/>

## Appendix: LLM prompts used

The two-stage extraction prompts (originally run in Chinese; translated here for readability). Each agent reads one input batch file (`b_NNN.json` / `s_NNN.json`, 40/15 items per batch) and writes results back to the corresponding output batch file.

### Haiku classification prompt

```
You are classifying r/LocalLLaMA posts/comments about "capability comparisons across model parameter scales."

Use the Read tool to read the JSON array: <input batch path>
Each item has id, kind, title, snippet, sizes_b (mentioned parameter counts), model_families, frontier_targets (frontier models compared against), score.

Assign exactly one verdict per item:
- verified_underdog: claims a [smaller] model genuinely matches/surpasses a [bigger or frontier] model, presented by the author as real (own hands-on test or a benchmark given).
- benchmark_only: a cross-size superiority claim resting [only] on benchmark scores (benchmaxx flavor), no real-use corroboration.
- refuted: the text [denies] that a small model really matches a bigger/frontier one (debunking, "not really", "name doesn't match reality", "the R1 distill isn't real R1").
- marketing_hype: a release/promo announcement claiming superiority in promotional tone, unverified.
- sentiment_only: an impression/opinion about a size tier, but [no] concrete cross-size comparison.
- off_topic: unrelated to "comparing capability by size" (pure hardware, jokes, off-topic).

Also give confidence: high / medium / low.

Judgment points:
- The key is the [small vs big] direction. If it's only a same-tier comparison or the bigger model is stronger, it's mostly sentiment_only or off_topic.
- Title in marketing-announcement tone ("X released!", "introducing", "we released") and self-praising → marketing_hype.
- snippet has "actually not", "falls short", "not really", "overhyped" → lean refuted.

Use the Write tool to write the result as a JSON array to: <output batch path>
Format: [{"id":"...","verdict":"...","confidence":"..."}, ...], one entry per input, ids must match.
Write [only] valid JSON in the file, no markdown code blocks, no explanation.
Final message: just "b_NNN: <count> classified".
```

### Sonnet extraction prompt

```
You are extracting structured events of "a small model punching up to match/surpass a bigger or frontier model" from r/LocalLLaMA posts/comments.

Use the Read tool to read the JSON array: <input batch path>
Each item has: id, kind(post/comment), date(post date), score, title, body(full post/comment text), top_replies(high-upvote replies, real community reaction), sizes_b, active_params_b, model_families, frontier_targets, haiku_verdict(initial: verified_underdog/benchmark_only/refuted).

For each item do two things:
1) verdict_check: validate the initial verdict, return confirmed / overturned (you think the initial is wrong) / unclear.
2) Extract an events array. A post may contain 0, 1 or more punching-up events. Each event:
   - small_model: exact name of the [smaller] model praised (e.g. "Qwen3-32B", "Gemma 3 27B", "QwQ-32B"; include version/size, don't write just "Qwen")
   - small_size_b: that model's parameter count (number, B); null if undeterminable
   - active_size_b: MoE active params (number) if applicable; else null
   - beaten_target: name of the [bigger/frontier] target beaten (e.g. "DeepSeek-R1", "GPT-4o", "Claude 3.5 Sonnet", "Llama-3 70B"; for generic, write "frontier" or "cloud models")
   - target_size_b: the target's parameter count (number); null for frontier-closed/unknown
   - task_domain: coding / math / reasoning / general / agentic / multilingual / vision / creative / other
   - claim_strength: surpasses / on_par / approaches
   - evidence_type: benchmark / lmarena / personal_use / anecdote / announcement / none
   - timing: immediate (post date = event date) / announced (forecasting the future) / retrospective (recalling the past) / speculative (guess/rumor)
   - effective_date: the event effective date explicitly mentioned in text, YYYY-MM-DD; null if none (note: post date ≠ event date)
   - is_marketing: true/false (marketing-announcement tone vs neutral/hands-on)
   - community_reaction: from top_replies and score, judge whether the community bought it — endorsed (mostly agree) / skeptical (mostly doubt/debunk) / mixed / none (insufficient reply signal)

Extraction points:
- Only extract the [small→big] direction. Same-tier or big-beats-small is not an event.
- refuted class: still extract the claim it [denies] (small_model is the small model questioned for punching up, claim_strength filled with the originally-claimed strength), and set community_reaction=skeptical, verdict_check=confirmed.
- small_size must really be [smaller] than target_size to count as punching up (when frontier-closed target_size=null, use common sense: 32B beating GPT-4o counts).
- When unsure of the exact small_model name, use the most specific spelling appearing in title/body.

Use the Write tool to write the result as a JSON array to: <output batch path>
Format: [{"id":"...","haiku_verdict":"...","verdict_check":"...","events":[{...}, ...]}, ...], one entry per input, ids consistent, events may be [].
Write [only] valid JSON in the file, no markdown code blocks, no explanation.
Final message: just "s_NNN: <event count> events".
```
