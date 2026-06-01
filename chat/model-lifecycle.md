# AI Model Lifecycle: Release Cadence & Version Lifespan

## 数据源

- **发布日期**：`token-price.csv` 的 `effective_date`（去除降价/缓存等非新发布事件）
- **退市日期**：基线来自官方公告（DEPRECATED_BASELINE），叠加 `deprecation_events.csv`
  （Reddit 退市讨论帖 19,793 条）的 `created_utc` 精确化。规则：Reddit 帖日期比基线更早
  则采用（说明基线偏保守），否则保留基线（官方源更权威）。
- **仍在售模型**的寿命为右删失（right-censored，截至 2026-06）。

## 图表

![Model Lifecycle](model-lifecycle.png)

- **左图**：各家连续新模型发布间隔天数（箱线图 + 散点）。
- **右图**：各版本从发布到退市天数（x = 已退市，o = 仍在售/右删失）。

## 发布间隔统计

| Provider | Models | Min (days) | Median | Max | Mean |
|---|---|---|---|---|---|
| OpenAI | 30 | 0 | 31 | 1003 | 73 |
| Anthropic | 18 | 0 | 31 | 153 | 59 |
| Google | 13 | 0 | 120 | 183 | 79 |
| DeepSeek | 7 | 0 | 212 | 243 | 117 |

## 各版本寿命明细（按寿命降序）

| Provider | Model | Launch | End | Days | Months | Status |
|---|---|---|---|---|---|---|
| OpenAI | GPT-3 Curie | 2020-06 | 2024-01 | 1309 | 43.6 | retired |
| OpenAI | GPT-3 Babbage | 2020-06 | 2024-01 | 1309 | 43.6 | retired |
| OpenAI | GPT-3 Ada | 2020-06 | 2024-01 | 1309 | 43.6 | retired |
| OpenAI | GPT-3 Davinci | 2020-06 | 2023-06 | 1095 | 36.5 | retired (Reddit 2023-06-11) |
| OpenAI | gpt-4o-mini | 2024-07 | 2026-06 | 700 | 23.3 | alive |
| OpenAI | o3 | 2025-04 | 2026-06 | 426 | 14.2 | alive |
| OpenAI | gpt-3.5-turbo-16k-0613 | 2023-06 | 2024-06 | 366 | 12.2 | retired |
| OpenAI | o3-pro | 2025-06 | 2026-06 | 365 | 12.2 | alive |
| OpenAI | gpt-4.1-nano | 2025-04 | 2026-02 | 306 | 10.2 | retired |
| OpenAI | gpt-5 | 2025-08 | 2026-06 | 304 | 10.1 | alive |
| OpenAI | gpt-5-mini | 2025-08 | 2026-06 | 304 | 10.1 | alive |
| OpenAI | gpt-5-nano | 2025-08 | 2026-06 | 304 | 10.1 | alive |
| OpenAI | o1-mini | 2024-09 | 2025-06 | 273 | 9.1 | retired |
| OpenAI | gpt-4-32k | 2023-03 | 2023-11 | 245 | 8.2 | retired (Reddit 2023-11-10) |
| OpenAI | gpt-4.1-mini | 2025-04 | 2025-08 | 122 | 4.1 | retired (Reddit 2025-08-07) |
| OpenAI | gpt-4 (8K) | 2023-03 | 2023-06 | 92 | 3.1 | retired (Reddit 2023-06-11) |
| OpenAI | gpt-5.4 | 2026-03 | 2026-06 | 92 | 3.1 | alive |
| OpenAI | o1-preview | 2024-09 | 2024-12 | 91 | 3.0 | retired (Reddit 2024-12-06) |
| OpenAI | gpt-5.5 | 2026-04 | 2026-06 | 61 | 2.0 | alive |
| OpenAI | gpt-4.5-preview | 2025-02 | 2025-04 | 59 | 2.0 | retired (Reddit 2025-06-16) |
| OpenAI | gpt-3.5-turbo-0301 | 2023-03 | 2023-04 | 31 | 1.0 | retired (Reddit 2023-04-28) |
| OpenAI | gpt-4-turbo (1106-preview) | 2023-11 | 2023-12 | 30 | 1.0 | retired (Reddit 2023-12-07) |
| OpenAI | gpt-4.1 | 2025-04 | 2025-05 | 30 | 1.0 | retired (Reddit 2025-05-14) |
| OpenAI | gpt-4o-2024-05-13 | 2024-05 | 2024-05 | 0 | 0.0 | retired (Reddit 2024-05-19) |
| OpenAI | o1 (GA) | 2024-12 | 2024-12 | 0 | 0.0 | retired (Reddit 2024-12-06) |
| OpenAI | o3-mini | 2025-01 | 2025-01 | 0 | 0.0 | retired (Reddit 2025-01-31) |
| OpenAI | o4-mini | 2025-04 | 2025-04 | 0 | 0.0 | retired (Reddit 2025-04-22) |
| OpenAI | gpt-4o-2024-08-06 | 2024-08 | 2024-05 | -92 | -3.1 | retired (Reddit 2024-05-19) |
| OpenAI | gpt-3.5-turbo-1106 | 2023-11 | 2023-06 | -153 | -5.1 | retired (Reddit 2023-06-14) |
| OpenAI | gpt-3.5-turbo-0125 | 2024-01 | 2023-06 | -214 | -7.1 | retired (Reddit 2023-06-14) |
| Anthropic | Claude 3 Opus | 2024-03 | 2025-06 | 457 | 15.2 | retired |
| Anthropic | Claude 3 Sonnet | 2024-03 | 2025-06 | 457 | 15.2 | retired |
| Anthropic | Claude 3 Haiku | 2024-03 | 2025-06 | 457 | 15.2 | retired |
| Anthropic | Claude Instant 1.2 | 2023-08 | 2024-03 | 213 | 7.1 | retired (Reddit 2025-05-31) |
| Anthropic | Claude Opus 4.5 | 2025-11 | 2026-06 | 212 | 7.1 | alive |
| Anthropic | Claude Sonnet 4.5 | 2025-09 | 2026-02 | 153 | 5.1 | retired |
| Anthropic | Claude Sonnet 4 | 2025-05 | 2025-09 | 123 | 4.1 | retired |
| Anthropic | Claude Haiku 4.5 | 2025-10 | 2026-02 | 123 | 4.1 | retired |
| Anthropic | Claude 3.5 Sonnet | 2024-06 | 2024-10 | 122 | 4.1 | retired |
| Anthropic | Claude Sonnet 4.6 | 2026-02 | 2026-06 | 120 | 4.0 | alive |
| Anthropic | Claude Opus 4 | 2025-05 | 2025-08 | 92 | 3.1 | retired |
| Anthropic | Claude Opus 4.1 | 2025-08 | 2025-11 | 92 | 3.1 | retired |
| Anthropic | Claude Opus 4.6 | 2026-03 | 2026-06 | 92 | 3.1 | alive |
| Anthropic | Claude Opus 4.7 | 2026-04 | 2026-06 | 61 | 2.0 | alive |
| Anthropic | Claude Opus 4.8 | 2026-05 | 2026-06 | 31 | 1.0 | alive |
| Anthropic | Claude 3.5 Haiku (launch) | 2024-11 | 2024-12 | 30 | 1.0 | retired |
| Anthropic | Claude 3.7 Sonnet | 2025-02 | 2025-03 | 28 | 0.9 | retired (Reddit 2025-03-23) |
| Anthropic | Claude 2.1 | 2023-11 | 2023-07 | -123 | -4.1 | retired (Reddit 2023-07-20) |
| Google | Gemini 2.0 Flash | 2025-02 | 2026-06 | 485 | 16.2 | retired |
| Google | Gemini 1.5 Flash (<=128K) | 2024-05 | 2025-06 | 396 | 13.2 | retired |
| Google | Gemini 2.0 Flash-Lite | 2025-02 | 2026-03 | 393 | 13.1 | retired (Reddit 2026-03-27) |
| Google | Gemini 2.5 Pro (<=200K) | 2025-06 | 2026-06 | 365 | 12.2 | alive |
| Google | Gemini 2.5 Flash | 2025-06 | 2026-06 | 365 | 12.2 | alive |
| Google | Gemini 2.5 Flash-Lite | 2025-06 | 2026-06 | 365 | 12.2 | alive |
| Google | PaLM 2 text-bison | 2023-06 | 2024-04 | 305 | 10.2 | retired |
| Google | Gemini 1.5 Flash-8B (<=128K) | 2024-10 | 2025-06 | 243 | 8.1 | retired |
| Google | Gemini 3.1 Pro (<=200K) | 2025-12 | 2026-06 | 182 | 6.1 | alive |
| Google | Gemini 1.5 Pro (<=128K) | 2024-05 | 2024-10 | 153 | 5.1 | retired |
| Google | Gemini 1.0 Pro | 2023-12 | 2024-05 | 152 | 5.1 | retired (Reddit 2024-05-29) |
| Google | Gemini 3.5 Flash | 2026-01 | 2026-06 | 151 | 5.0 | alive |
| Google | Gemini 3.1 Flash-Lite | 2026-01 | 2026-06 | 151 | 5.0 | alive |
| DeepSeek | DeepSeek-R1 (deepseek-reasoner) | 2025-01 | 2026-06 | 516 | 17.2 | alive |
| DeepSeek | DeepSeek-V3.2-Exp | 2025-09 | 2026-06 | 273 | 9.1 | alive |
| DeepSeek | DeepSeek-V2 (deepseek-chat) | 2024-05 | 2024-12 | 214 | 7.1 | retired |
| DeepSeek | DeepSeek-V3 (promo) | 2024-12 | 2025-02 | 62 | 2.1 | retired (Reddit 2025-09-06) |
| DeepSeek | DeepSeek-V4 Flash | 2026-04 | 2026-06 | 61 | 2.0 | alive |
| DeepSeek | DeepSeek-V3.1 (unified) | 2025-09 | 2025-09 | 0 | 0.0 | retired |
| DeepSeek | DeepSeek-V4 Pro (promo 75% off) | 2026-04 | 2026-01 | -90 | -3.0 | retired (Reddit 2026-01-20) |

## Reddit 精确化的退市日期

基线日期 vs Reddit 最早退市帖日期。以下模型的退市日期被 Reddit 帖前移：

| Model | Baseline | Refined | Reddit date | Score | Title |
|---|---|---|---|---|---|
| GPT-3 Davinci | 2024-01 | 2023-06 | 2023-06-11 | 15 | 14 models removed from the API |
| gpt-3.5-turbo-0301 | 2024-06 | 2023-04 | 2023-04-28 | 16 | GPT-3.5 Turbo Model Gone |
| gpt-3.5-turbo-1106 | 2024-06 | 2023-06 | 2023-06-14 | 74 | 16k context for OpenAI GPT-3.5 API |
| gpt-3.5-turbo-0125 | 2024-06 | 2023-06 | 2023-06-14 | 74 | 16k context for OpenAI GPT-3.5 API |
| gpt-4 (8K) | 2025-06 | 2023-06 | 2023-06-11 | 15 | 14 models removed from the API |
| gpt-4-32k | 2025-06 | 2023-11 | 2023-11-10 | 5 | After June 2024, OpenAI will offer no models in th |
| gpt-4-turbo (1106-preview) | 2024-12 | 2023-12 | 2023-12-07 | 20 | Follow the money. Mystery solved that GPT-4 Pro ha |
| gpt-4o-2024-05-13 | 2024-10 | 2024-05 | 2024-05-19 | 24 | [Case Study] GPT-4 succeeded on a coding project,  |
| gpt-4o-2024-08-06 | 2026-02 | 2024-05 | 2024-05-19 | 24 | [Case Study] GPT-4 succeeded on a coding project,  |
| gpt-4.1 | 2026-02 | 2025-05 | 2025-05-14 | 55 | GPT-4o is still "SOTA model" because they haven't  |
| gpt-4.1-mini | 2026-02 | 2025-08 | 2025-08-07 | 23 | >**Model deprecations and old conversations** >Whe |
| o1-preview | 2025-02 | 2024-12 | 2024-12-06 | 130 | I have my suspicions on why they removed o1-previe |
| o1 (GA) | 2025-06 | 2024-12 | 2024-12-06 | 341 | O1 is less powerful than O1-preview due to the les |
| o3-mini | 2025-06 | 2025-01 | 2025-01-31 | 27 | It makes perfect sense but needs to be explained b |
| o4-mini | 2026-02 | 2025-04 | 2025-04-22 | 295 | o3/o4-mini is a regression |
| Claude 2.1 | 2025-03 | 2023-07 | 2023-07-20 | 53 | SillyTavern Main release 1.9 |
| Claude 3.7 Sonnet | 2025-06 | 2025-03 | 2025-03-23 | 429 | New "nebula" model on LMArena, likely Gemini 2.0 P |
| Gemini 1.0 Pro | 2025-02 | 2024-05 | 2024-05-29 | 21 | Gemini 1.0 Ultra is pretty much deprecated now. It |
| Gemini 2.0 Flash-Lite | 2026-06 | 2026-03 | 2026-03-27 | 6 | gemini-2.5-flash-lite alternative? |
| DeepSeek-V4 Pro (promo 75% off) | 2026-06 | 2026-01 | 2026-01-20 | 72 | I think Giga Potato:free in Kilo Code is Deepseek  |
