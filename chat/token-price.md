# 各品牌最贵 API 价格 + 套餐榨满折合 per-token（2023–2026）

**旗舰 = 同一厂家在同一时段 API 目录里最贵的文本模型**（含推理模型），
模型退市后自动让位给次高价。这样看到的是**各品牌天花板价**随时间的变化。

套餐折算假设用户全用最贵模型（套餐内用哪个不影响价格）。
数据源 `token-price.csv`，本文由 `token-price.py` 生成。

## 对比图

![各品牌最贵 API 价 + 套餐榨满折合](token-price.png)

- **左轴（实线）**：各家 API 目录中在售最贵模型的 blended 价（(input+output)/2，USD/1M tokens）。
  线上标注了当期最贵模型名。
- **右轴（虚线）**：套餐把配额用满后的折合 per-token。每条消息按 2000 token 折算。
  - **最高折合**（最便宜套餐榨满）= 折扣率低、单价高。
  - **最低折合**（最贵套餐榨满）= 批量折扣大、单价低。

## 折算口径

- API blended 每季度取在售最贵；退市模型（DEPRECATED 表）让位次高价。排除音频/embedding 模型。
- 套餐折合 = 月价 ÷（月配额 × 2000）。相对配额「N× Pro」= 倍数 × Pro 配额。
  /N 小时按 24×7 满载。

## 各季度最贵模型是谁（变更点）

| 品牌 | 季度 | 当期最贵模型 | blended $/1M |
|---|---|---|---|
| OpenAI | 23Q1 | gpt-4-32k | 90.00 |
| OpenAI | 25Q1 | gpt-4.5-preview | 112.50 |
| OpenAI | 25Q2 | o3-pro | 50.00 |
| Anthropic | 23Q3 | Claude Instant 1.2 | 3.57 |
| Anthropic | 23Q4 | Claude 2.1 | 21.85 |
| Anthropic | 24Q1 | Claude 3 Opus | 45.00 |
| Anthropic | 25Q2 | Claude Opus 4 | 45.00 |
| Anthropic | 25Q3 | Claude Opus 4.1 | 45.00 |
| Anthropic | 25Q4 | Claude Opus 4.5 | 15.00 |
| Google | 23Q2 | PaLM 2 text-bison | 0.38 |
| Google | 23Q4 | Gemini 1.0 Pro | 1.00 |
| Google | 24Q2 | Gemini 1.5 Pro (<=128K) | 14.00 |
| Google | 24Q4 | Gemini 1.5 Pro (<=128K cut) | 1.88 |
| Google | 25Q2 | Gemini 2.5 Pro (<=200K) | 5.62 |
| Google | 25Q4 | Gemini 3.1 Pro (<=200K) | 7.00 |
| DeepSeek | 24Q2 | DeepSeek-V2 (deepseek-chat) | 0.21 |
| DeepSeek | 24Q4 | DeepSeek-V3 (promo) | 0.21 |
| DeepSeek | 25Q1 | DeepSeek-R1 (deepseek-reasoner) | 1.37 |
| DeepSeek | 26Q2 | DeepSeek-V4 Pro (standard) | 2.61 |

## 套餐榨满折合明细

| 品牌 | 生效 | 套餐 | 月价 | 榨满折合 $/1M |
|---|---|---|---|---|
| OpenAI | 2023-03 | ChatGPT Plus | $20 | 1.67 |
| OpenAI | 2023-07 | ChatGPT Plus | $20 | 0.83 |
| OpenAI | 2023-11 | ChatGPT Plus | $20 | 1.04 |
| OpenAI | 2024-05 | ChatGPT Plus | $20 | 0.52 |
| OpenAI | 2025-08 | ChatGPT Plus | $20 | 0.52 |
| OpenAI | 2026-03 | ChatGPT Plus | $20 | 0.78 |
| Anthropic | 2023-09 | Claude Pro | $20 | 1.11 |
| Anthropic | 2025-04 | Claude Max 5x | $100 | 1.11 |
| Anthropic | 2025-04 | Claude Max 20x | $200 | 0.56 |

## 与互联网接入价格的同尺度对比

把美国互联网接入服务的价格历史起点（**1993-09 AOL 开放公众接入**）对齐到 token-price.csv
的最早时间点（**2020-06 OpenAI GPT-3 API**），用同一坐标观察两条曲线。

![互联网月费 vs AI token 价格](token-price-vs-internet.png)

- **上图**：1993-09 → 2026-06 共 33 年的美国家庭互联网名义月费。早期高频波动以月为单位标注，
  后期成熟阶段以年度 USTelecom BPI 数值标注。
- **下图**：2020-06 → 2026-06 共 6 年的 AI token API 与套餐价格演化，X 轴起点（2020-06）
  与上图起点（1993-09）共用 figure 左侧位置。
- **结论**：互联网用 33 年从"计时拨号 $9.95+$3.50/h"走到"光纤 $39.50/月、单 Mbps 下降 90%"；
  AI token 仅 6 年就在同等量级走完了"$60/1M 旗舰 → $5/1M Opus 4.5 / $0.14/1M DeepSeek"
  的演化。**两条线放进同一图里看，6 年 AI 价格变化 ≈ 33 年互联网价格变化的覆盖宽度**。

### 互联网月费数据点

| 日期 | 名义月费 | 备注 |
|---|---|---|
| 1993-09 | $9.95 | AOL $9.95/月含5h, 超 $3.50/h |
| 1994-12 | $9.95 | AOL 跟进 Prodigy 降价: 超额$2.50/h |
| 1995-02 | $24.95 | CompuServe $24.95/20h 过渡套餐 |
| 1996-03 | $19.95 | 独立 ISP $19.95 不限时拨号 |
| 1996-07 | $19.95 | AOL 双轨: $9.95/5h 或 $19.95/20h |
| 1996-12 | $19.95 | AOL $19.95/月 无限拨号普及全美 |
| 1997-06 | $20.95 | 全行业拨号锁死 $19.95–21.95 |
| 2000-06 | $49.99 | 早期宽带 3–6 Mbps $49.99 |
| 2002-06 | $34.95 | ADSL 抢市场降至 $34.95 |
| 2005-06 | $47.50 | 宽带稳定 $45–50/月 |
| 2015-06 | $65.62 | USTelecom BPI: 43 Mbps avg |
| 2021-06 | $48.42 | BPI: 85 Mbps avg |
| 2022-06 | $45.97 | BPI: 98 Mbps avg |
| 2023-06 | $41.31 | BPI: 141 Mbps avg |
| 2025-06 | $39.90 | BPI: 200+ Mbps |
| 2026-06 | $39.50 | BPI: 250+ Mbps |

数据来源：EH.Net、NYT Archive (1994)、Computerworld、CNET、Smithsonian、Pew Research、
FCC Historical Reports、WSJ、Bruce Kushnick / Teletruth、**USTelecom Broadband Pricing Index**、
NCTA、BLS CPI (Internet Access Services)。

## 假设与局限

- **每条消息 2000 token** 是折算口径；改它整体平移套餐线但不改品牌相对关系。
- **模型退市时间**来自 CSV notes + Reddit 退市帖 + 官方公告，部分近似（±1 月）。
- **可量化套餐有限**：OpenAI 只有 Plus $20（Pro $200 无限不可榨满）；Anthropic 借「N× Pro」
  得到区间。Google/DeepSeek/Cursor 无法独立折算。
- 套餐配额多为 Reddit 实测某时点观察；Claude Pro 后期叠加的周限未量化。
- **互联网价格是名义月费**，未做通胀调整，也未折算到"每 Mbps"；对比的是**用户每月掏多少钱**
  与"AI 套餐每月掏多少钱 / API 每 1M token 多少钱"两条独立轴。
