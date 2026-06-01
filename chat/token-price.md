# 各品牌最贵 API 价格 + 套餐榨满折合 per-token（2020–2026）

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
| OpenAI | 20Q2 | GPT-3 Davinci | 60.00 |
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

## 与 PC $/(core·GHz)、互联网 $/Mbps 的三条等比叠加

把美国 PC（1976-）、互联网接入（1993-）、AI token（2020-）三条曲线统一到 token 坐标系：

- **时间平移**：三条线各自起点对齐到 token 2020-06，
  - PC 1976-07 → 2020-06（+528 月），最后点 2026-06 落到 token 2070-06；
  - 互联网 1993-09 → 2020-06（+321 月），最后点 2026-06 落到 token 2053-03；
  - token 自身原位。
- **指标统一**：均取"行业核心通缩指标"——
  - PC：**$/(core·GHz)**（整机售价 ÷ 核心数 ÷ 主频 GHz）。该指标在 1976–2005 由主频拉动，
    2005–2026 由核心数拉动；横跨"频率战"和"多核战"两个阶段。
  - 互联网：**$/Mbps**（月费 ÷ 典型下行速率）；
  - token：**$/1M tokens**（API 最贵模型 blended）。
- **等比缩放**：三条线起点价 ≡ 2020-06 GPT-3 Davinci $60/1M tokens，
  - PC ×9.18e-5（1976-07 Apple I $653,588/(core·GHz) → $60）；
  - 互联网 ×0.0868（1993-09 $691/Mbps → $60）；
  - token 不缩放。
- **Y 轴 log**：PC $/(core·GHz) 50 年跌 ~45,000×（$653K → $14.5），
  互联网 $/Mbps 33 年跌 4400×，token 6 年最贵在 $50–$112 + 长尾 $0.1。

![PC + 互联网 + token 三条等比叠加](token-price-vs-internet-pc.png)

- **红虚线**：PC $/(core·GHz)，方形 marker。
- **灰虚线**：互联网 $/Mbps，圆形 marker。
- **彩实线**：各家 token API 最贵模型 blended。

**观感**：log 空间里 PC 50 年画出一条接近指数下行的直线，可分两段——
1976–2005 的**频率战**（单核主频从 1 MHz 飙到 3 GHz，3000×）和 2005–2026 的**多核战**
（核心数从 1 涨到 13+ 而绝对售价不变）。互联网斜率明显比 PC 缓；**token 6 年的下行斜率
（最贵小幅波动 + 长尾陡降）若延长，理论上 5–6 年就能覆盖 PC 50 年走过的下行幅度**——
这是 AI token 价格相对于历史科技品类的"加速倍率"的直观印证。

### PC 整机价 → $/(core·GHz) 数据点

| 日期 | 整机售价 | 核心 | 主频 | $/(core·GHz) | 备注 |
|---|---|---|---|---|---|
| 1976-07 | $666.66 | 1 | 1.02 MHz | $653,588 | Apple I; MOS 6502 @ 1.02 MHz |
| 1977-06 | $1298.00 | 1 | 1.02 MHz | $1,272,549 | Apple II; MOS 6502 @ 1.02 MHz |
| 1981-08 | $1565.00 | 1 | 4.77 MHz | $328,092 | IBM PC 5150; Intel 8088 @ 4.77 MHz |
| 1982-01 | $595.00 | 1 | 1.02 MHz | $583,333 | Commodore 64; MOS 6510 @ 1.02 MHz |
| 1983-06 | $99.00 | 1 | 3.00 MHz | $33,000 | TI-99/4A 倾销价; TMS9900 @ 3 MHz |
| 1984-01 | $2495.00 | 1 | 7.83 MHz | $318,646 | Macintosh 128K; MC68000 @ 7.83 MHz |
| 1990-06 | $2500.00 | 1 | 16.00 MHz | $156,250 | Compaq 386SX @ 16 MHz |
| 1995-06 | $1900.00 | 1 | 75.00 MHz | $25,333 | Pentium 75; 超标量 |
| 2000-06 | $999.00 | 1 | 1.0 GHz | $999 | Athlon / Pentium III @ 1.0 GHz |
| 2005-06 | $800.00 | 1 | 3.0 GHz | $267 | Pentium 4 Prescott @ 3.0 GHz；主频墙 |
| 2015-06 | $650.00 | 4 | 3.2 GHz | $51 | Intel Core i5-6500 |
| 2020-06 | $710.00 | 6 | 3.6 GHz | $33 | AMD Ryzen 5 3600 / Intel i5-10400 |
| 2024-06 | $680.00 | 10 | 2.5 GHz | $27 | Intel Core i5-14400（6P+4E） |
| 2026-06 | $660.00 | 13 | 3.5 GHz | $15 | AI PC 主流（多核混合架构） |

数据来源：Smithsonian（Apple I）、Apple Computer Inc. Archive（Apple II）、Computer History
Museum（TRS-80）、IBM Archives（IBM PC）、NYT Archive（1983 TI 退出）、Stanford "Making the
Macintosh"、PC Magazine via Google Books、Washington Post（1995 Pentium）、Gartner/IDC
（2000 $999 价格战）、BLS Computer Price Deflation、Intel ARK / AMD 官方处理器规格。

### 互联网月费 → $/Mbps 数据点

| 日期 | 名义月费 | 速率 (Mbps) | $/Mbps | 备注 |
|---|---|---|---|---|
| 1993-09 | $9.95 | 0.0144 | $690.97 | AOL $9.95/5h + $3.50/h；14.4k modem |
| 1994-12 | $9.95 | 0.0144 | $690.97 | AOL 跟进 Prodigy；14.4k 仍主流 |
| 1995-02 | $24.95 | 0.0288 | $866.32 | CompuServe $24.95/20h；28.8k modem |
| 1996-03 | $19.95 | 0.0288 | $692.71 | 独立 ISP $19.95 不限时；28.8k |
| 1996-07 | $19.95 | 0.0288 | $692.71 | AOL 双轨套餐；28.8k |
| 1996-12 | $19.95 | 0.0288 | $692.71 | AOL 全美无限拨号；28.8k |
| 1997-06 | $20.95 | 0.056 | $374.11 | 全行业锁死 $19.95–21.95；V.90 56k |
| 2000-06 | $49.99 | 4.5 | $11.11 | 早期宽带 3–6 Mbps；取均值 4.5 |
| 2002-06 | $34.95 | 1.0 | $34.95 | ADSL 入门级 ~1 Mbps（电信抢市场） |
| 2005-06 | $47.50 | 3.0 | $15.83 | Cable broadband typical 3 Mbps |
| 2015-06 | $65.62 | 43 | $1.53 | USTelecom BPI: 43 Mbps avg |
| 2021-06 | $48.42 | 85 | $0.57 | BPI: 85 Mbps avg |
| 2022-06 | $45.97 | 98 | $0.47 | BPI: 98 Mbps avg |
| 2023-06 | $41.31 | 141 | $0.29 | BPI: 141 Mbps avg |
| 2025-06 | $39.90 | 200 | $0.20 | BPI: 200+ Mbps |
| 2026-06 | $39.50 | 250 | $0.16 | BPI: 250+ Mbps |

互联网数据来源：EH.Net、NYT Archive (1994)、Computerworld、CNET、Smithsonian、Pew Research、
FCC Historical Reports、WSJ、Bruce Kushnick / Teletruth、**USTelecom Broadband Pricing Index**、
NCTA、BLS CPI (Internet Access Services)。

## 假设与局限

- **每条消息 2000 token** 是折算口径；改它整体平移套餐线但不改品牌相对关系。
- **模型退市时间**来自 CSV notes + Reddit 退市帖 + 官方公告，部分近似（±1 月）。
- **可量化套餐有限**：OpenAI 只有 Plus $20（Pro $200 无限不可榨满）；Anthropic 借「N× Pro」
  得到区间。Google/DeepSeek/Cursor 无法独立折算。
- 套餐配额多为 Reddit 实测某时点观察；Claude Pro 后期叠加的周限未量化。
- **互联网 $/Mbps** 由"名义月费 ÷ 该时段典型下行速率"算出，**未做通胀调整**。
  - **拨号时代速率**用主流 modem 标准估算（1993-1995 取 14.4k = 0.0144 Mbps、1995-1996 取
    28.8k = 0.0288 Mbps、1997 取 V.90 56k = 0.056 Mbps）——这是 ITU 标准 + 行业普及曲线
    的合理近似，但并非用户实测带宽（实际拨号常因线路衰减跑不满）。
  - **宽带初期速率**（2000–2005）用入门 tier 典型值：2000-06 取 4.5 Mbps（早期宽带 3–6 Mbps
    均值）、2002-06 取 1 Mbps（ADSL 入门级）、2005-06 取 3 Mbps（Cable 入门）；不同 tier
    取值会让 $/Mbps 上下浮动 ~2×。
  - **2015 后速率**采用 USTelecom Broadband Pricing Index 的 avg 下行——这是带宽与套餐价
    最权威的年度配对数据，置信度最高。
  - 月费均为名义美元；如做 CPI 调整后 1990s 价格还要再上浮 ~70%，会让早期 $/Mbps 更高，
    与现代的差距进一步拉大。
- **PC $/(core·GHz)** 把"频率战"和"多核战"两阶段揉到同一指标：
  早期主频是真实算力的瓶颈，2005 后多核才是；用核心数 × 主频做线性合成是粗略简化，没考虑
  IPC（每周期指令数）的提升——若纳入 IPC，1976→2026 真实算力差距应再 × 数十倍。
