#!/usr/bin/env python3
"""根据 chat/token-price.csv 生成 token-price.png + token-price.md。

旗舰 = 同一厂家在同一时段 API 目录里最贵的模型（含推理模型），
模型退市后自动让位次高价。

套餐折算假设用户全用最贵模型（套餐内模型不加价），
最高折合 = 最便宜套餐榨满配额，最低折合 = 最贵套餐榨满配额。

输出 matplotlib png（带图例、标注、双 Y 轴），替代 mermaid xychart-beta。
"""
from __future__ import annotations

import csv
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "Arial Unicode MS",
                                    "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "token-price.csv")
OUT_PNG = os.path.join(HERE, "token-price.png")
OUT_PNG2 = os.path.join(HERE, "token-price-vs-internet.png")
OUT_MD = os.path.join(HERE, "token-price.md")

TOKENS_PER_MESSAGE = 2000

# 美国互联网接入服务历史价格（年/月 -> 名义月费 USD, 典型下行速率 Mbps）
# 来源：EH.Net, NYT, Computerworld, CNET, Smithsonian, Pew, FCC, WSJ,
#       Bruce Kushnick / Teletruth, USTelecom BPI, NCTA, BLS CPI
# 早期高频段以月为单位，2015 后用 USTelecom BPI 年度报告值。
# 拨号年代速率为该时段主流 modem 标准（14.4k → 28.8k → V.90 56k）；
# 宽带初期速率为入门 tier 典型；2015+ 用 BPI avg 下行速率。
INTERNET_PRICES = [
    # (日期, 月费 USD, 速率 Mbps, 备注)
    ("1993-09",  9.95, 0.0144, "AOL $9.95/5h + $3.50/h；14.4k modem"),
    ("1994-12",  9.95, 0.0144, "AOL 跟进 Prodigy；14.4k 仍主流"),
    ("1995-02", 24.95, 0.0288, "CompuServe $24.95/20h；28.8k modem"),
    ("1996-03", 19.95, 0.0288, "独立 ISP $19.95 不限时；28.8k"),
    ("1996-07", 19.95, 0.0288, "AOL 双轨套餐；28.8k"),
    ("1996-12", 19.95, 0.0288, "AOL 全美无限拨号；28.8k"),
    ("1997-06", 20.95, 0.056,  "全行业锁死 $19.95–21.95；V.90 56k"),
    ("2000-06", 49.99, 4.5,    "早期宽带 3–6 Mbps；取均值 4.5"),
    ("2002-06", 34.95, 1.0,    "ADSL 入门级 ~1 Mbps（电信抢市场）"),
    ("2005-06", 47.50, 3.0,    "Cable broadband typical 3 Mbps"),
    ("2015-06", 65.62, 43,     "USTelecom BPI: 43 Mbps avg"),
    ("2021-06", 48.42, 85,     "BPI: 85 Mbps avg"),
    ("2022-06", 45.97, 98,     "BPI: 98 Mbps avg"),
    ("2023-06", 41.31, 141,    "BPI: 141 Mbps avg"),
    ("2025-06", 39.90, 200,    "BPI: 200+ Mbps"),
    ("2026-06", 39.50, 250,    "BPI: 250+ Mbps"),
]

# token-price.csv 最早数据点 = 2020-06。互联网时间轴起点 1993-09 对齐到此。
TOKEN_ORIGIN = "2020-06"
INTERNET_ORIGIN = "1993-09"

EXCLUDE = {"OpenAI audio models", "text-embedding-ada-002", "Off-peak discount"}

DEPRECATED = {
    "GPT-3 Davinci":            "2024-01",
    "GPT-3 Curie":              "2024-01",
    "GPT-3 Babbage":            "2024-01",
    "GPT-3 Ada":                "2024-01",
    "gpt-3.5-turbo-0301":       "2024-06",
    "gpt-3.5-turbo-16k-0613":   "2024-06",
    "gpt-3.5-turbo-1106":       "2024-06",
    "gpt-3.5-turbo-0125":       "2024-06",
    "gpt-4 (8K)":               "2025-06",
    "gpt-4-32k":                "2025-06",
    "gpt-4-turbo (1106-preview)":"2024-12",
    "gpt-4o-2024-05-13":        "2024-10",
    "gpt-4o-2024-08-06":        "2026-02",
    "gpt-4.5-preview":          "2025-04",
    "gpt-4.1":                  "2026-02",
    "gpt-4.1-mini":             "2026-02",
    "gpt-4.1-nano":             "2026-02",
    "o1-preview":               "2025-02",
    "o1-mini":                  "2025-06",
    "o1 (GA)":                  "2025-06",
    "o3-mini":                  "2025-06",
    "o4-mini":                  "2026-02",
    "Claude Instant 1.2":       "2024-03",
    "Claude 2.1":               "2025-03",
    "Claude 3 Opus":            "2025-06",
    "Claude 3 Sonnet":          "2025-06",
    "Claude 3 Haiku":           "2025-06",
    "Claude 3.5 Sonnet":        "2024-10",
    "Claude 3.5 Sonnet (caching)":"2025-06",
    "Claude 3.5 Haiku (launch)":"2024-12",
    "Claude 3.5 Haiku (cut)":   "2025-10",
    "Claude 3.7 Sonnet":        "2025-06",
    "Claude Opus 4":            "2025-08",
    "Claude Sonnet 4":          "2025-09",
    "Claude Opus 4.1":          "2025-11",
    "Claude Sonnet 4.5":        "2026-02",
    "Claude Haiku 4.5":         "2026-02",
    "PaLM 2 text-bison":        "2024-04",
    "Gemini 1.0 Pro":           "2025-02",
    "Gemini 1.5 Flash (<=128K)":"2025-06",
    "Gemini 1.5 Flash (<=128K cut)":"2025-06",
    "Gemini 1.5 Flash-8B (<=128K)":"2025-06",
    "Gemini 2.0 Flash":         "2026-06",
    "Gemini 2.0 Flash-Lite":    "2026-06",
    "Gemini 1.5 Pro (<=128K)":  "2024-10",
    "DeepSeek-V3 (promo)":      "2025-02",
    "DeepSeek-V2 (deepseek-chat)":"2024-12",
    "deepseek-chat V2 + context caching":"2024-12",
    "DeepSeek-V3 (standard)":   "2025-09",
    "DeepSeek-V3.1 (unified)":  "2025-09",
    "DeepSeek-V4 Pro (promo 75% off)":"2026-06",
}

QUARTERS = [(y, q) for y in range(2020, 2027) for q in (1, 2, 3, 4)
            if not (y == 2026 and q > 2) and not (y == 2020 and q == 1)]
QLABEL = [f"{y % 100}Q{q}" for (y, q) in QUARTERS]
QEND = [f"{y}-{q*3:02d}" for (y, q) in QUARTERS]
OPENAI_CHAT_PLUS = {"ChatGPT Plus (GPT-4)", "ChatGPT Plus (GPT-4o)",
                    "ChatGPT Plus (GPT-5 era)", "ChatGPT Plus (2026)"}


def load_rows():
    with open(CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fnum(s):
    s = (s or "").strip()
    return float(s) if s else None


CAP_RE = re.compile(
    r"(\d[\d,]*)\s*(?:msgs?|messages?|queries|prompts?|requests?)\s*"
    r"(?:/|per|every|a|each)?\s*(\d*)\s*(hours?|hrs?|h|days?|weeks?|months?)",
    re.IGNORECASE)
PER_MONTH = {"day": 30.0, "week": 30.0 / 7, "month": 1.0}


def cap_msgs_per_month(text):
    m = CAP_RE.search(text or "")
    if not m:
        return None
    count = float(m.group(1).replace(",", ""))
    n = float(m.group(2)) if m.group(2) else 1.0
    unit = m.group(3).lower().rstrip("s")
    if unit in ("h", "hour", "hr"):
        return count * (30 * 24) / n
    return count * PER_MONTH[unit] / n


def per_token(price, tokens):
    return price / tokens * 1e6


def max_envelope(rows, providers):
    models = {b: [] for b in providers}
    for r in rows:
        b = r["provider"]
        if b not in providers or r["category"] != "API":
            continue
        name = r["product_or_model"]
        if name in EXCLUDE:
            continue
        i, o = fnum(r["input_per_1m_usd"]), fnum(r["output_per_1m_usd"])
        if i is None or o is None:
            continue
        models[b].append((r["effective_date"], (i + o) / 2, i, o, name))
    result = {}
    for b in providers:
        vals, mnames = [], []
        for qe in QEND:
            best, best_name = 0, ""
            for ym, bl, inp, out, name in models[b]:
                if ym > qe:
                    continue
                dep = DEPRECATED.get(name)
                if dep and dep <= qe:
                    continue
                if bl > best:
                    best, best_name = bl, name
            vals.append(best)
            mnames.append(best_name)
        result[b] = (vals, mnames)
    return result


def forward_fill(points):
    pts = sorted(points, key=lambda x: x[0])
    first, vals = pts[0][1], []
    for qe in QEND:
        cur = first
        for ym, v in pts:
            if ym <= qe:
                cur = v
            else:
                break
        vals.append(cur)
    return vals


# ---- 标注：在线条末端（或极值处）标出当期最贵模型名 ----

def ym_to_months(ym):
    y, m = ym.split("-")
    return int(y) * 12 + int(m)


def months_since(ym, origin):
    return ym_to_months(ym) - ym_to_months(origin)


def annotate_changes(ax, x, vals, names, color, yoffset=0):
    prev = ""
    for i, (v, nm) in enumerate(zip(vals, names)):
        if nm != prev and nm and v > 0:
            ax.annotate(nm, (x[i], v), fontsize=5.5, color=color, alpha=0.85,
                        xytext=(4, yoffset), textcoords="offset points",
                        va="center", ha="left",
                        arrowprops=dict(arrowstyle="-", color=color, lw=0.4, alpha=0.4))
            prev = nm


def plot_vs_internet(rows, env, order, plus, anth_plans, pro_pt, max20):
    """画第二张图: 互联网月费与 AI token 价格叠加在一张图里。
    - 时间对齐: 互联网 1993-09 平移到 2020-06（+ 321 个月偏移）
    - 价格缩放: 互联网价格 × (token_at_2020_06 / internet_at_1993_09)，
      即假设 1993-09 互联网月费 ≡ 2020-06 最贵 API 模型 blended。
    - X 轴延到能装下互联网最后一个数据点（1993-09 + 33 年 → 2053 左右）。
    - token 数据到 2026-06 自然结束。
    """
    # 把每个互联网点先换算成 $/Mbps，再做缩放
    inet_per_mbps = [(ym, price / mbps, price, mbps, note)
                     for ym, price, mbps, note in INTERNET_PRICES]
    inet_anchor_per_mbps = inet_per_mbps[0][1]  # 1993-09: $9.95/0.0144 ≈ $691/Mbps
    token_anchor_price = next(  # 2020-06 OpenAI GPT-3 Davinci blended = $60/1M
        ((fnum(r["input_per_1m_usd"]) + fnum(r["output_per_1m_usd"])) / 2
         for r in rows
         if r["effective_date"] == TOKEN_ORIGIN
         and r["category"] == "API"
         and r["product_or_model"] == "GPT-3 Davinci"))
    scale = token_anchor_price / inet_anchor_per_mbps  # 60 / 691 ≈ 0.0868

    inet_x = [months_since(ym, INTERNET_ORIGIN) for ym, _, _, _, _ in inet_per_mbps]
    inet_y_scaled = [pm * scale for _, pm, _, _, _ in inet_per_mbps]
    inet_max = max(inet_x)

    fig, ax = plt.subplots(figsize=(16, 7.5))
    fig.patch.set_facecolor("white")

    # ---- 互联网线（灰色虚粗线，标价） ----
    ax.plot(inet_x, inet_y_scaled, "--", color="#666", lw=2.5,
            marker="o", ms=6, dashes=(5, 3),
            label=f"美国互联网 $/Mbps × {scale:.4f}（1993-09 = 2020-06 锚定）",
            zorder=4)
    for (ym, per_mbps, price, mbps, note), xv, yv in zip(
            inet_per_mbps, inet_x, inet_y_scaled):
        ax.annotate(f"{ym}\n${per_mbps:.2f}/Mbps\n({mbps}M, ${price:.0f}/月)",
                    (xv, yv), fontsize=6,
                    xytext=(5, 7), textcoords="offset points",
                    color="#444", alpha=0.85)

    # ---- token API 线 ----
    api_colors = {"OpenAI": "#10a37f", "Anthropic": "#d97706",
                  "Google": "#4285f4", "DeepSeek": "#1a1a2e"}
    for b in order:
        vals, names = env[b]
        c = api_colors[b]
        bx, by = [], []
        for qe, v in zip(QEND, vals):
            if v > 0:
                bx.append(months_since(qe, TOKEN_ORIGIN))
                by.append(v)
        ax.plot(bx, by, "-", color=c, lw=1.8, marker="o", ms=4,
                label=f"{b} API 最贵 blended", zorder=3)

    # ---- X 轴: 月数 → 双语标签（token 真实日期 + 互联网真实日期） ----
    ax.set_xlim(-6, inet_max + 12)
    # 主刻度: 每两年一格的 token 日历
    tick_months = []
    tick_labels = []
    for m in range(0, inet_max + 12, 24):
        token_y = 2020 + (6 + m) // 12
        token_mo = (6 + m) % 12 or 12
        inet_y_cal = 1993 + (9 + m) // 12
        inet_mo = (9 + m) % 12 or 12
        if m <= months_since("2026-06", TOKEN_ORIGIN):
            tick_labels.append(f"{token_y}-{token_mo:02d}\n(互{inet_y_cal})")
        else:
            tick_labels.append(f"—\n(互{inet_y_cal})")
        tick_months.append(m)
    ax.set_xticks(tick_months)
    ax.set_xticklabels(tick_labels, fontsize=7.5)

    ax.set_ylabel("USD / 1M tokens（互联网 $/Mbps 已按 1993-09 ≡ 2020-06 GPT-3 Davinci 缩放）",
                  fontsize=10)
    ax.set_xlabel("token 真实日期 / (互联网真实年份)，1993-09 → 2020-06 平移对齐", fontsize=9)
    ax.set_yscale("log")
    ax.set_ylim(0.005, max(inet_y_scaled) * 1.5)

    # token 数据截止竖线
    token_end = months_since("2026-06", TOKEN_ORIGIN)
    ax.axvline(token_end, color="#999", ls=":", lw=1, alpha=0.6, zorder=1)
    ax.text(token_end + 1, ax.get_ylim()[1] * 0.5,
            "token 数据截止\n(2026-06)", fontsize=7.5, color="#666", va="top")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8.5, ncol=2, framealpha=0.92)

    final_per_mbps = inet_per_mbps[-1][1]
    ax.set_title(
        f"互联网 $/Mbps 与 AI token $/1M tokens 等比叠加（Y 轴 log）\n"
        f"锚定：1993-09 互联网 ${inet_anchor_per_mbps:.0f}/Mbps ≡ "
        f"2020-06 GPT-3 Davinci ${token_anchor_price:.0f}/1M tokens（× {scale:.4f}）\n"
        f"互联网 33 年 $/Mbps 从 ${inet_anchor_per_mbps:.0f} 跌到 ${final_per_mbps:.2f}"
        f"（≈4400×）；token 6 年内顶价 $50–$112 + 长尾跌到 $0.1",
        fontsize=11, pad=12)

    fig.tight_layout()
    fig.savefig(OUT_PNG2, dpi=180, bbox_inches="tight")
    print(f"写入 {OUT_PNG2}")
    plt.close(fig)


def main():
    rows = load_rows()
    order = ["OpenAI", "Anthropic", "Google", "DeepSeek"]
    env = max_envelope(rows, order)

    # 套餐
    plus = []
    for r in rows:
        if r["product_or_model"] in OPENAI_CHAT_PLUS:
            p, cap = fnum(r["monthly_price_usd"]), cap_msgs_per_month(r["usage_limit"])
            if p and cap:
                plus.append((r["effective_date"], per_token(p, cap * TOKENS_PER_MESSAGE)))
    plus_line = forward_fill(sorted(plus))

    pro_row = next(r for r in rows if r["product_or_model"] == "Claude Pro")
    pro_tokens = cap_msgs_per_month(pro_row["usage_limit"]) * TOKENS_PER_MESSAGE
    pro_price = fnum(pro_row["monthly_price_usd"])
    pro_pt = per_token(pro_price, pro_tokens)
    anth_plans = [(pro_row["effective_date"], "Claude Pro", pro_price, pro_tokens, pro_pt)]
    for r in rows:
        m = re.match(r"Claude Max (\d+)x", r["product_or_model"])
        if m:
            mult = int(m.group(1))
            p = fnum(r["monthly_price_usd"])
            tok = mult * pro_tokens
            anth_plans.append((r["effective_date"], r["product_or_model"], p, tok, per_token(p, tok)))
    anth_plans.sort(key=lambda x: (x[0], x[2]))
    max20 = next(x for x in anth_plans if x[1] == "Claude Max 20x")
    anth_high = forward_fill([(pro_row["effective_date"], pro_pt)])
    anth_low = forward_fill([(pro_row["effective_date"], pro_pt), (max20[0], max20[4])])

    x = list(range(len(QUARTERS)))

    # ---- 画图 ----
    fig, ax1 = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("white")

    # API lines (left Y axis, solid thick)
    api_colors = {"OpenAI": "#10a37f", "Anthropic": "#d97706",
                  "Google": "#4285f4", "DeepSeek": "#1a1a2e"}
    for b in order:
        vals, names = env[b]
        c = api_colors[b]
        ax1.plot(x, vals, "-", color=c, lw=2.2, marker="o", ms=4,
                 label=f"{b} API max", zorder=3)
        annotate_changes(ax1, x, vals, names, c, yoffset=3)

    ax1.set_ylabel("API most-expensive model blended (USD / 1M tokens)", fontsize=10)
    ax1.set_ylim(bottom=-2)
    ax1.yaxis.set_major_locator(mticker.MultipleLocator(10))
    ax1.set_xticks(x)
    ax1.set_xticklabels(QLABEL, rotation=45, ha="right", fontsize=8)
    ax1.grid(axis="y", alpha=0.25)
    ax1.grid(axis="x", alpha=0.12)

    # Subscription lines (right Y axis, dashed thin)
    ax2 = ax1.twinx()
    ax2.plot(x, plus_line, "--", color="#10a37f", lw=1.5, marker="s", ms=3,
             alpha=0.8, label="OpenAI Plus $20 maxed-out")
    ax2.plot(x, anth_high, "--", color="#d97706", lw=1.5, marker="^", ms=3,
             alpha=0.8, label="Anthropic Pro $20 maxed (highest)")
    ax2.plot(x, anth_low, ":", color="#d97706", lw=1.5, marker="v", ms=3,
             alpha=0.6, label="Anthropic Max20x $200 maxed (lowest)")
    ax2.set_ylabel("Subscription maxed-out per-token (USD / 1M tokens)", fontsize=10)
    sub_max = max(max(plus_line), max(anth_high), max(anth_low))
    ax2.set_ylim(-0.05, sub_max * 1.3)
    ax2.yaxis.set_major_locator(mticker.MultipleLocator(0.2))

    # 合并图例
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=7.5, ncol=2,
               framealpha=0.9)

    ax1.set_title("Most-Expensive API Price + Subscription Maxed-Out per-Token (2023-2026)\n"
                  "Left: API max model blended (in+out)/2  |  Right: subscription quota maxed-out",
                  fontsize=11, pad=12)

    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=180, bbox_inches="tight")
    print(f"写入 {OUT_PNG}")
    plt.close(fig)

    # ---- 生成 md（引用 png，附明细表） ----
    flagship_tbl = []
    for b in order:
        vals, names = env[b]
        prev = ""
        for ql, v, nm in zip(QLABEL, vals, names):
            if nm != prev:
                flagship_tbl.append(f"| {b} | {ql} | {nm} | {v:.2f} |")
                prev = nm

    sub_tbl = []
    for ym, pt in sorted(plus):
        sub_tbl.append(f"| OpenAI | {ym} | ChatGPT Plus | $20 | {pt:.2f} |")
    for ym, name, p, tok, pt in anth_plans:
        sub_tbl.append(f"| Anthropic | {ym} | {name} | ${p:g} | {pt:.2f} |")

    inet_tbl = []
    for ym, price, mbps, note in INTERNET_PRICES:
        inet_tbl.append(f"| {ym} | ${price:.2f} | {mbps} | ${price / mbps:.2f} | {note} |")

    md = f"""# 各品牌最贵 API 价格 + 套餐榨满折合 per-token（2023–2026）

**旗舰 = 同一厂家在同一时段 API 目录里最贵的文本模型**（含推理模型），
模型退市后自动让位给次高价。这样看到的是**各品牌天花板价**随时间的变化。

套餐折算假设用户全用最贵模型（套餐内用哪个不影响价格）。
数据源 `token-price.csv`，本文由 `token-price.py` 生成。

## 对比图

![各品牌最贵 API 价 + 套餐榨满折合](token-price.png)

- **左轴（实线）**：各家 API 目录中在售最贵模型的 blended 价（(input+output)/2，USD/1M tokens）。
  线上标注了当期最贵模型名。
- **右轴（虚线）**：套餐把配额用满后的折合 per-token。每条消息按 {TOKENS_PER_MESSAGE} token 折算。
  - **最高折合**（最便宜套餐榨满）= 折扣率低、单价高。
  - **最低折合**（最贵套餐榨满）= 批量折扣大、单价低。

## 折算口径

- API blended 每季度取在售最贵；退市模型（DEPRECATED 表）让位次高价。排除音频/embedding 模型。
- 套餐折合 = 月价 ÷（月配额 × {TOKENS_PER_MESSAGE}）。相对配额「N× Pro」= 倍数 × Pro 配额。
  /N 小时按 24×7 满载。

## 各季度最贵模型是谁（变更点）

| 品牌 | 季度 | 当期最贵模型 | blended $/1M |
|---|---|---|---|
{chr(10).join(flagship_tbl)}

## 套餐榨满折合明细

| 品牌 | 生效 | 套餐 | 月价 | 榨满折合 $/1M |
|---|---|---|---|---|
{chr(10).join(sub_tbl)}

## 与互联网 $/Mbps 价格的等比叠加对比

把美国互联网接入服务的价格历史**先换算成 $/Mbps**（每月费 ÷ 该时段典型下行速率），
再**平移并等比缩放**到 token 坐标系：

- **时间平移**：假设互联网 1993-09 那一刻发生在 token 的 2020-06，即互联网每个日历日期 +321 个月
  落到 token 时间轴上。互联网最后一个数据点 2026-06 落到 token 时间 2053 附近，X 轴顺延到装下。
- **$/Mbps 等比缩放**：用 1993-09 互联网 ≈$691/Mbps（$9.95 ÷ 14.4k modem 0.0144 Mbps）
  ≡ 2020-06 GPT-3 Davinci $60/1M tokens 作锚点，互联网所有 $/Mbps × **0.0868** 后画到同一 Y 轴。
- **Y 轴 log**：互联网 $/Mbps 从 $691 跌到 $0.16（≈4400×），跨 ~3.6 个数量级，线性轴
  会把后期点压成 0。
- 2026-06 后 token 没数据则留空（图中竖虚线标出 token 数据截止）。

![互联网 $/Mbps 等比缩放叠加 AI token 价格](token-price-vs-internet.png)

- **灰线**：缩放后的互联网 $/Mbps，标签同时给出真实日期、原始 $/Mbps、速率、月费。
- **彩线**：各家 API 最贵模型 blended（与第一张图一致）。
- **观感**：换成 $/Mbps 后互联网线呈现**指数下行**——拨号 33 年压缩成几段台阶，2000 年宽带
  普及后陡降一个量级，2015 后 USTelecom BPI 时代再降两个量级。**token 6 年的最贵 API 在
  $50–$112 区间小幅波动，但 DeepSeek 已把同等天花板的便宜端按到 $0.1 量级**——
  与互联网 $/Mbps 跌幅相比，AI token 的下行斜率更陡，时间窗仅互联网的 1/5。

### 互联网月费 → $/Mbps 数据点

| 日期 | 名义月费 | 速率 (Mbps) | $/Mbps | 备注 |
|---|---|---|---|---|
{chr(10).join(inet_tbl)}

数据来源：EH.Net、NYT Archive (1994)、Computerworld、CNET、Smithsonian、Pew Research、
FCC Historical Reports、WSJ、Bruce Kushnick / Teletruth、**USTelecom Broadband Pricing Index**、
NCTA、BLS CPI (Internet Access Services)。

## 假设与局限

- **每条消息 {TOKENS_PER_MESSAGE} token** 是折算口径；改它整体平移套餐线但不改品牌相对关系。
- **模型退市时间**来自 CSV notes + Reddit 退市帖 + 官方公告，部分近似（±1 月）。
- **可量化套餐有限**：OpenAI 只有 Plus $20（Pro $200 无限不可榨满）；Anthropic 借「N× Pro」
  得到区间。Google/DeepSeek/Cursor 无法独立折算。
- 套餐配额多为 Reddit 实测某时点观察；Claude Pro 后期叠加的周限未量化。
- **互联网价格是名义月费**，未做通胀调整，也未折算到"每 Mbps"；对比的是**用户每月掏多少钱**
  与"AI 套餐每月掏多少钱 / API 每 1M token 多少钱"两条独立轴。
"""
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"写入 {OUT_MD}")

    plot_vs_internet(rows, env, order, plus, anth_plans, pro_pt, max20)

    for b in order:
        vals, names = env[b]
        print(f"  {b:10s} 最贵演进：", end="")
        prev = ""
        for ql, v, nm in zip(QLABEL, vals, names):
            if nm != prev:
                print(f" [{ql}]{nm}=${v:.1f}", end="")
                prev = nm
        print()


if __name__ == "__main__":
    main()
