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
OUT_PNG2 = os.path.join(HERE, "token-price-vs-internet-pc.png")
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

# token-price.csv 最早数据点 = 2020-06。互联网 / PC 时间轴起点对齐到此。
TOKEN_ORIGIN = "2020-06"
INTERNET_ORIGIN = "1993-09"
PC_ORIGIN = "1976-07"

# 个人电脑历史价格（日期, 整机售价 USD, RAM 容量 KB, 备注）
# 通缩指标 = 整机售价 ÷ RAM 容量 = $/KB
# 来源：Smithsonian, IBM Archives, Computer History Museum, NYT (1983),
#       Stanford Mac history, PC Magazine, WaPo, BLS PPI, Our World in Data
PC_PRICES = [
    ("1976-07",  666.66,        4,        "Apple I（4KB 主板）"),
    ("1977-06", 2638.00,       48,        "Apple II 48KB 满配"),
    ("1981-08", 1565.00,       16,        "IBM PC 5150 基础"),
    ("1982-01",  595.00,       64,        "Commodore 64 首发"),
    ("1983-12",  199.00,       64,        "C64 价格战钉死 $199"),
    ("1984-01", 2495.00,      128,        "Macintosh 128K + GUI"),
    ("1990-06", 2500.00,     4 * 1024,    "386 PC 典型, 4 MB"),
    ("1995-06", 1900.00,     8 * 1024,    "Pentium 75 + Win95, 8 MB"),
    ("2000-06",  999.00,    64 * 1024,    "$999 价格战, 64 MB"),
    ("2005-06",  800.00,   512 * 1024,    "ASP < $800, 512 MB"),
    ("2015-06",  650.00,     8 * 1024**2, "BLS ASP, 8 GB"),
    ("2020-06",  710.00,    16 * 1024**2, "疫情供应链, 16 GB"),
    ("2024-06",  680.00,    16 * 1024**2, "ASP, 16 GB"),
    ("2026-06",  660.00,    16 * 1024**2, "ASP, 16 GB"),
]

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
    scale_inet = token_anchor_price / inet_anchor_per_mbps  # ≈ 0.0868

    inet_x = [months_since(ym, INTERNET_ORIGIN) for ym, _, _, _, _ in inet_per_mbps]
    inet_y_scaled = [pm * scale_inet for _, pm, _, _, _ in inet_per_mbps]
    inet_max = max(inet_x)

    # 把每个 PC 点换算成 $/KB（整机价 ÷ RAM 容量），再缩放
    pc_per_kb = [(ym, price / kb, price, kb, note)
                 for ym, price, kb, note in PC_PRICES]
    pc_anchor_per_kb = pc_per_kb[0][1]  # 1976-07: $666.66/4 = $166.665/KB
    scale_pc = token_anchor_price / pc_anchor_per_kb  # 60 / 166.665 ≈ 0.36
    pc_x = [months_since(ym, PC_ORIGIN) for ym, _, _, _, _ in pc_per_kb]
    pc_y_scaled = [pk * scale_pc for _, pk, _, _, _ in pc_per_kb]
    pc_max = max(pc_x)

    fig, ax = plt.subplots(figsize=(20, 8))
    fig.patch.set_facecolor("white")

    # ---- PC 线（蓝色虚线，标价） ----
    ax.plot(pc_x, pc_y_scaled, "--", color="#2b5b9b", lw=2.5,
            marker="s", ms=6, dashes=(2, 2),
            label=f"个人电脑 $/KB RAM × {scale_pc:.4f}（1976-07 = 2020-06 锚定）",
            zorder=3)
    for (ym, per_kb, price, kb, note), xv, yv in zip(
            pc_per_kb, pc_x, pc_y_scaled):
        if kb >= 1024 ** 2:
            ram_lbl = f"{kb // (1024 ** 2)}GB"
        elif kb >= 1024:
            ram_lbl = f"{kb // 1024}MB"
        else:
            ram_lbl = f"{kb}KB"
        ax.annotate(f"{ym}\n${per_kb:.3g}/KB\n({ram_lbl}, ${price:.0f})",
                    (xv, yv), fontsize=5.8,
                    xytext=(5, -22), textcoords="offset points",
                    color="#2b5b9b", alpha=0.85)

    # ---- 互联网线（灰色虚粗线，标价） ----
    ax.plot(inet_x, inet_y_scaled, "--", color="#666", lw=2.5,
            marker="o", ms=6, dashes=(5, 3),
            label=f"美国互联网 $/Mbps × {scale_inet:.4f}（1993-09 = 2020-06 锚定）",
            zorder=4)
    for (ym, per_mbps, price, mbps, note), xv, yv in zip(
            inet_per_mbps, inet_x, inet_y_scaled):
        ax.annotate(f"{ym}\n${per_mbps:.2f}/Mbps\n({mbps}M, ${price:.0f}/月)",
                    (xv, yv), fontsize=5.8,
                    xytext=(5, 7), textcoords="offset points",
                    color="#444", alpha=0.85)

    # ---- token API 线 ----
    api_colors = {"OpenAI": "#10a37f", "Anthropic": "#d97706",
                  "Google": "#4285f4", "DeepSeek": "#1a1a2e"}
    for b in order:
        vals, names = env[b]
        c = api_colors[b]
        bx = [months_since(qe, TOKEN_ORIGIN) for qe in QEND]
        by = [float("nan") if v == 0 else v for v in vals]
        ax.plot(bx, by, "-", color=c, lw=1.8, marker="o", ms=4,
                label=f"{b} API 最贵 blended", zorder=3)

    # ---- X 轴: 月数 → 三语标签（token / 互联网 / PC 真实日期） ----
    x_max = max(pc_max, inet_max) + 12
    ax.set_xlim(-6, x_max)
    token_end_m = months_since("2026-06", TOKEN_ORIGIN)
    inet_end_m = months_since("2026-06", INTERNET_ORIGIN)
    pc_end_m = pc_max
    tick_months = []
    tick_labels = []
    for m in range(0, int(x_max), 48):
        token_y = 2020 + (6 + m) // 12
        token_mo = (6 + m) % 12 or 12
        inet_y_cal = 1993 + (9 + m) // 12
        pc_y_cal = 1976 + (7 + m) // 12
        token_part = (f"{token_y}-{token_mo:02d}"
                      if m <= token_end_m else "—")
        inet_part = f"互{inet_y_cal}" if m <= inet_end_m else "互—"
        pc_part = f"PC{pc_y_cal}" if m <= pc_end_m else "PC—"
        tick_labels.append(f"{token_part}\n{inet_part}\n{pc_part}")
        tick_months.append(m)
    ax.set_xticks(tick_months)
    ax.set_xticklabels(tick_labels, fontsize=7)

    ax.set_ylabel("USD / 1M tokens（PC $/KB、互联网 $/Mbps 均按 1976/1993 起点 ≡ "
                  "2020-06 GPT-3 Davinci $60 缩放）", fontsize=9.5)
    ax.set_xlabel("token 真实日期 / 互联网真实年份 / PC 真实年份"
                  "（1976-07 PC、1993-09 互联网 → 2020-06 token 平移对齐）", fontsize=9)
    ax.set_yscale("log")
    y_top = max(max(inet_y_scaled), max(pc_y_scaled)) * 1.5
    y_bot = min(min(pc_y_scaled), min(inet_y_scaled)) * 0.5
    ax.set_ylim(y_bot, y_top)

    # 各曲线数据截止竖线
    ax.axvline(token_end_m, color="#10a37f", ls=":", lw=1, alpha=0.5, zorder=1)
    ax.text(token_end_m + 1, y_top * 0.5,
            "token 截止\n2026-06", fontsize=7, color="#10a37f", va="top")
    ax.axvline(inet_end_m, color="#666", ls=":", lw=1, alpha=0.5, zorder=1)
    ax.text(inet_end_m + 1, y_top * 0.5,
            "互联网截止\n2026-06", fontsize=7, color="#666", va="top")
    ax.axvline(pc_end_m, color="#2b5b9b", ls=":", lw=1, alpha=0.5, zorder=1)
    ax.text(pc_end_m + 1, y_top * 0.5,
            "PC 截止\n2026-06", fontsize=7, color="#2b5b9b", va="top")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8.5, ncol=2, framealpha=0.92)

    final_per_mbps = inet_per_mbps[-1][1]
    final_per_kb = pc_per_kb[-1][1]
    ax.set_title(
        f"PC $/KB、互联网 $/Mbps、AI token $/1M tokens 三条等比叠加（Y log）\n"
        f"锚定：1976-07 PC ${pc_anchor_per_kb:.1f}/KB、"
        f"1993-09 互联网 ${inet_anchor_per_mbps:.0f}/Mbps、"
        f"2020-06 GPT-3 Davinci ${token_anchor_price:.0f}/1M tokens 三点同高\n"
        f"PC 50 年 $/KB 从 ${pc_anchor_per_kb:.1f} 跌到 ${final_per_kb:.2g}"
        f"（≈{pc_anchor_per_kb/final_per_kb:.0e}×）；"
        f"互联网 33 年 $/Mbps 跌 4400×；token 6 年顶 $50–$112、长尾 $0.1",
        fontsize=10.5, pad=12)

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
        # 缺数据的季度用 NaN，让 matplotlib 断线而不是接到 0
        masked = [float("nan") if v == 0 else v for v in vals]
        ax1.plot(x, masked, "-", color=c, lw=2.2, marker="o", ms=4,
                 label=f"{b} API max", zorder=3)
        annotate_changes(ax1, x, masked, names, c, yoffset=3)

    ax1.set_ylabel("API most-expensive model blended (USD / 1M tokens)", fontsize=10)
    api_max = max(max(env[b][0]) for b in order)
    ax1.set_ylim(-2, api_max * 1.1)
    ax1.yaxis.set_major_locator(mticker.MultipleLocator(10))
    ax1.set_xticks(x)
    sparse_labels = [lbl if lbl.endswith("Q1") or i == 0 or i == len(x) - 1 else ""
                     for i, lbl in enumerate(QLABEL)]
    ax1.set_xticklabels(sparse_labels, rotation=45, ha="right", fontsize=8)
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

    ax1.set_title("Most-Expensive API Price + Subscription Maxed-Out per-Token (2020-2026)\n"
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

    pc_tbl = []
    for ym, price, kb, note in PC_PRICES:
        if kb >= 1024 ** 2:
            ram = f"{kb // (1024 ** 2)} GB"
        elif kb >= 1024:
            ram = f"{kb // 1024} MB"
        else:
            ram = f"{kb} KB"
        pc_tbl.append(f"| {ym} | ${price:.2f} | {ram} | ${price / kb:.3g} | {note} |")

    md = f"""# 各品牌最贵 API 价格 + 套餐榨满折合 per-token（2020–2026）

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

## 与 PC $/KB、互联网 $/Mbps 的三条等比叠加

把美国 PC（1976-）、互联网接入（1993-）、AI token（2020-）三条曲线统一到 token 坐标系：

- **时间平移**：三条线各自起点对齐到 token 2020-06，
  - PC 1976-07 → 2020-06（+528 月），最后点 2026-06 落到 token 2070-06；
  - 互联网 1993-09 → 2020-06（+321 月），最后点 2026-06 落到 token 2053-03；
  - token 自身原位。
- **指标统一**：均取"行业核心通缩指标"——
  - PC：**$/KB RAM**（整机售价 ÷ RAM 容量，单位 $/KB）；
  - 互联网：**$/Mbps**（月费 ÷ 典型下行速率）；
  - token：**$/1M tokens**（API 最贵模型 blended）。
- **等比缩放**：三条线起点价 ≡ 2020-06 GPT-3 Davinci $60/1M tokens，
  - PC ×0.36（1976-07 $166.66/KB → $60）；
  - 互联网 ×0.0868（1993-09 $691/Mbps → $60）；
  - token 不缩放。
- **Y 轴 log**：PC $/KB 50 年跌 ~400 万倍（$166.7 → $0.0000394，≈4.2e6×），
  互联网 $/Mbps 33 年跌 ~4400×，token 6 年最贵在 $50–$112 + 长尾 $0.1。

![PC + 互联网 + token 三条等比叠加](token-price-vs-internet-pc.png)

- **蓝虚线**：PC $/KB RAM，方形 marker。
- **灰虚线**：互联网 $/Mbps，圆形 marker。
- **彩实线**：各家 token API 最贵模型 blended。

**观感**：log 空间里 PC 50 年画出一条几乎完美的指数下行直线（接近经典 Hennessy & Patterson
半导体每年 ~40% 通缩）；互联网斜率明显比 PC 缓；**token 6 年的斜率（最贵小幅波动 + 长尾陡降）
若延长，理论上 5–6 年就能覆盖 PC 50 年走过的下行幅度**。这是 AI token 价格相对于历史
科技品类的"加速倍率"的直观印证。

### PC 整机价 → $/KB RAM 数据点

| 日期 | 整机售价 | RAM | $/KB | 备注 |
|---|---|---|---|---|
{chr(10).join(pc_tbl)}

数据来源：Smithsonian（Apple I）、Apple Computer Inc. Archive（Apple II）、Computer History
Museum（TRS-80）、IBM Archives（IBM PC）、NYT Archive（1983 TI 退出）、Stanford "Making the
Macintosh"、PC Magazine via Google Books、Washington Post（1995 Pentium）、Gartner/IDC（2000
$999 价格战）、BLS Computer Price Deflation、Our World in Data（Memory/Storage 历史价）。

### 互联网月费 → $/Mbps 数据点

| 日期 | 名义月费 | 速率 (Mbps) | $/Mbps | 备注 |
|---|---|---|---|---|
{chr(10).join(inet_tbl)}

互联网数据来源：EH.Net、NYT Archive (1994)、Computerworld、CNET、Smithsonian、Pew Research、
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
