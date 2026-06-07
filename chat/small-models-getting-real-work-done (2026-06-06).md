# 2026-06-06: Small Models Getting the Job Done — 913 r/LocalLLaMA posts of "using a local small model to complete a real task"

This is a line complementary to "punching up at bigger models": instead of whether a small model beat someone on a benchmark, it looks only at **whether a user actually used it to get a real job done**. From three years of r/LocalLLaMA corpus I filtered 2,509 posts that "mention a small model (≤34B tier) + first-person real use / building / cloud-replacement," then ran Haiku classification (filtering out 52% hardware posts / model-recommendation requests / vague impressions) and Sonnet structured extraction, yielding **913 unique posts, 981 real-task events**.

The data is community **self-reports**, mostly single-person single-scenario, not systematic evaluation; the counts are facts about the corpus, and "small models are good enough" is a generalization over those self-reports. Sonnet's second pass overturned ~5% (33/981).

## Core: lots succeed, very few get questioned

| Outcome | 2023 | 2024 | 2025 | 2026* | Total | Share |
|---|---|---|---|---|---|---|
| success (done / in use) | 74 | 212 | 241 | 204 | 731 | 75% |
| partial (usable with caveats) | 28 | 61 | 85 | 47 | 221 | 23% |
| failed (didn't work / fell back to cloud) | 4 | 9 | 11 | 5 | 29 | 3% |
| Year total | 106 | 282 | 337 | 256 | 981 | — |

\* 2026 covers only Jan–Jun, already near the full-2025 volume — real-task reports are accelerating. The success share holds steady at 70–80% year over year (80% in 2026).

The most notable thing is the community reaction: **clear skepticism is only 35 (3.6%)**, endorsed 156, mixed 153, the rest without enough reply signal. Compared with the 31% skepticism rate of the "beat-the-closed" set — **"I used a 7B to get my job done" is far harder to dispute than "my 7B beats GPT-4."** The former is a reproducible personal fact, the latter a strong claim that has to withstand leaderboard and reproducibility pressure. This line is therefore much "cleaner" than the punching-up claims: the benchmaxx discount is thin, failed is only 3%, and the community barely argues. (⚠ Interpretation: low failed also has survivorship bias — people who didn't succeed post about it less.)

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

## How small is enough: 3–14B is the real workhorse, 20–34B caps the top

Size distribution of the small models in the events:

| Tier | 23 | 24 | 25 | 26* | Total |
|---|---|---|---|---|---|
| <3B | 1 | 18 | 42 | 28 | 89 |
| 3-7B | 63 | 91 | 75 | 34 | 263 |
| 8-14B | 27 | 93 | 76 | 26 | 222 |
| 20-34B | 11 | 48 | 116 | 154 | 329 |
| >34B | 4 | 22 | 13 | 8 | 47 |

(\* 2026 is Jan–Jun only; 950 events have a clear size, 31 are unlabeled.) Over time it's a **fork**, not a simple downward shift: in 2023 it relied on **3-7B** (use whatever runs, 63 events pinned here); by 2025–2026, on one end **20-34B surges into the top tier for general work** (11→48→116→154), and on the other **<3B grows from 1 to 42** specializing in narrow tasks. On narrow, well-defined jobs (structured extraction, summarization, OCR, file organizing, voice), **2–3B small models repeatedly succeed** — medical SOAP summaries with Phi-3 3B, file organizing with Gemma 2B, gaze detection with Moondream 2B, transcript analysis with Llama 3.2 3B. The narrower the task and the more finetunable, the fewer parameters needed; more general work converges toward 20–34B. Unlike "beat-the-closed," which clusters at 24–32B, the real-task line stretches the usable size range at both ends.

What hardware it runs on (355 events mention hardware): 3090 (55) most, Apple M-series ~114 combined (Mac/M1/M2/M3/M4), 4090 (16), 3060 (14), CPU only 18, even phones 7. **Consumer single cards and Macs are the main stage for real tasks**, no server rack needed.

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

## Known limitations

1. Events are **user self-reports**, mostly single-person, single-task, custom scenarios, weak on reproducibility; high success has survivorship bias (people who failed post less).
2. Candidates come from regex filtering (small-model size + use/build language), missing posts where the task is only stated in the body and the title is bland.
3. Model/size follows the community's wording; a few "3B models" may actually be MoE or finetuned, recorded per the original post.
4. Community reaction is based on top replies + upvote-count as a proxy, not full comment-tree sentiment analysis.
5. The "replacement" in cloud-replacement is a user claim, not necessarily sustained long-term; it only reflects the choice at posting time.

## Related material

- Companion search (the "beat-the-closed-frontier" line: which closed flagship gets challenged, how many parameters it takes, benchmaxx quality, the 19 hardest records): [small-models-vs-closed-frontier (2026-06-06).md](small-models-vs-closed-frontier%20(2026-06-06).md) — same corpus, `capability_events.csv`.
- The parent piece (four-angle overview + full extraction pipeline + Haiku/Sonnet prompts): [localllama-capability-density (2026-06-06).md](localllama-capability-density%20(2026-06-06).md).

## References

[1] r/LocalLLaMA, "I Created an AI Research Assistant that actually DOES research," Nov 2024. (1286 upvotes; Phi 3.8B/14B automated search + cited research report.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1gvlzug/>

[2] r/LocalLLaMA, "Ran Qwen 3.5 9B on M1 Pro (16GB) as an actual agent, not just a chat demo," 2026. (887 upvotes; agent replacing Claude Code.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1rll349/>

[3] r/LocalLLaMA, "I built a coding agent that gets 87% on benchmarks with a 4B parameter model," 2026. (754 upvotes; Gemma 4 4B + SmallCode agent.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1tgecrq/>

[4] r/LocalLLaMA, "Just canceled my ChatGPT Plus subscription," Feb 2025. (652 upvotes; DeepSeek-R1 distill 8B replacing ChatGPT Plus/o1.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1if5q97/>

[5] r/LocalLLaMA, "Qwen 3.6 27B is a BEAST," 2026. (599 upvotes; replacing a cloud subscription for data-transform debugging.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1steip4/>

[6] r/LocalLLaMA, "3B Model Beating GPT4 on Medical Summarisation," May 2024. (332 upvotes; Phi-3 3B finetuned for medical SOAP summaries.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1cp2h1v/>

[7] r/LocalLLaMA, "I built an AI file organizer that reads and sorts your files, running 100% on your device," Sep 2024. (324 upvotes; Gemma 2B replacing Groq API.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1fn3aee/>

[8] r/LocalLLaMA, "I fine-tuned Llama 3.2 3B for transcript analysis," 2025. (231 upvotes; transcript structured extraction.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1n5w9yy/>

[9] r/LocalLLaMA, "I made a game using LLMs (gpt-oss:20b) — Among LLMs," Sep 2025. (380 upvotes; 20B driving a multi-agent role-play game.) [Online]. Available: <https://reddit.com/r/LocalLLaMA/comments/1nfrzbv/>

## Appendix: LLM prompts used

The two-stage extraction prompts (originally run in Chinese; translated here for readability — see `scripts/prep_realtask.py` and the Chinese companion for the verbatim originals). Candidate criteria: has a small-model size (≤34B tier) + score≥5 + first-person use/build/cloud-replacement language (regex-filtered). Each agent reads one input batch file (`b_NNN.json` / `s_NNN.json`) and writes results back to the corresponding output batch file.

### Haiku classification prompt

```
You are classifying r/LocalLLaMA posts/comments, judging whether each is a record of "a user reporting that they used a [small model] to get a real task/job done" (no comparison with other models required).

Use the Read tool to read the JSON array: <input batch path>
Each item has id, kind, title, snippet, sizes_b, model_families, hardware, score.

Assign exactly one verdict per item:
- task_done: the author reports [successfully] completing a real task with some local small model, or building a usable app/agent/workflow/product with it (e.g. "I built a customer-service bot with Qwen 7B, it's live", "a local 14B runs my RAG nicely").
- task_partial: usable with clear caveats ("good enough but limited", "fine for small tasks, not complex ones", "needs a lot of tuning").
- task_failed: tried but [did not get] the real task done ("didn't work in practice", "doesn't meet the bar", "still had to use cloud").
- not_task: not a real-task-completion report — pure hardware/VRAM posts, "which model should I pick" questions, tutorials, benchmark scores, release announcements, vague impressions.

Also give confidence: high / medium / low.

Judgment points:
- The core is [a real task/actual use + a specific small model used]. Merely saying "this model is nice" with no concrete task → not_task.
- Pure discussion of what size the hardware can run, recommendation requests, pure quantization tests → not_task.
- "I canceled my ChatGPT subscription and switched to a local X for Y" → task_done (and Sonnet will later record replaced_cloud).

Use the Write tool to write the result as a JSON array to: <output batch path>
Format: [{"id":"...","verdict":"...","confidence":"..."}, ...], one per input, ids consistent.
Write only valid JSON in the file, no markdown code blocks, no explanation.
Final message: just "b_NNN: <count> done".
```

### Sonnet extraction prompt

```
You are extracting structured events of "a user using a [local small model] to complete a real task" from r/LocalLLaMA posts/comments.

Use the Read tool to read the JSON array: <input batch path>
Each item has: id, kind(post/comment), date, score, title, body(full text), top_replies(high-upvote replies = real community reaction), sizes_b, active_params_b, model_families, hardware, haiku_verdict(initial: task_done/task_partial/task_failed).

For each item do two things:
1) verdict_check: validate the initial verdict, return confirmed / overturned / unclear.
2) Extract an events array (usually 1 per post, possibly 0 or more). Each event:
   - model: the exact name of the small model used (e.g. "Qwen2.5-7B", "Gemma 3 12B", "Llama 3.1 8B"; include version/size where possible)
   - size_b: parameter count (number, B); null if uncertain
   - active_size_b: MoE active params (number); else null
   - task: one sentence describing the [real task/use] (e.g. "summarize legal PDFs", "home voice assistant", "code completion in the editor", "customer-service chatbot", "bulk data cleaning/classification")
   - task_domain: coding / agentic / writing / roleplay / rag / translation / data-extraction / vision-ocr / voice / home-automation / research / summarization / general / other
   - outcome: success (done/in use) / partial (usable with caveats) / failed (didn't work, fell back to cloud)
   - replaced_cloud: true/false — whether it explicitly [replaced a cloud/paid model] for this task
   - replaced_what: the replaced cloud model/service name (e.g. "ChatGPT Plus", "GPT-4 API", "Claude"); null if none
   - hardware: what it runs on (e.g. "RTX 3060 12GB", "M2 Max", "CPU only"); null if unmentioned
   - is_self_built: true/false — whether they [built] an app/agent/tool/pipeline around it
   - community_reaction: from top_replies + score — endorsed (mostly agree/also using) / skeptical (mostly doubt) / mixed / none

Extraction points:
- Extract only [real tasks/actual use]. Pure impressions, pure benchmarks, recommendation requests, hardware discussion → leave events empty [].
- model must be the small model [used to do the work], not a comparison target mentioned in passing.
- "Canceled ChatGPT, local X does Y" → replaced_cloud=true, replaced_what="ChatGPT", outcome=success.

Use the Write tool to write the result as a JSON array to: <output batch path>
Format: [{"id":"...","haiku_verdict":"...","verdict_check":"...","events":[{...}]}, ...], one per input, ids consistent, events may be [].
Write only valid JSON in the file, no markdown code blocks, no explanation.
Final message: just "s_NNN: <event count> events".
```
