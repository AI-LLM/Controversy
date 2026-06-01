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
OUT_PNG3 = os.path.join(HERE, "tokens-per-task.png")
OUT_PNG4 = os.path.join(HERE, "task-price.png")
OUT_PNG5 = os.path.join(HERE, "task-price-vs-internet-pc.png")
OUT_MD = os.path.join(HERE, "token-price.md")

USAGE_CSV = os.path.join(HERE, "token-usage-amount.csv")

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
PC_ORIGIN = "1975-01"   # 画图起点（Altair 8800 商业微型机），早于此的 PC 数据仅在 md 表格里保留
PC_FULL_HISTORY_ORIGIN = "1951-03"

# 商业化计算机历史价格（日期, 整机售价 USD, MIPS, 备注）
# 通缩指标 = 整机售价 ÷ MIPS = $/MIPS
# 早期 KIPS → MIPS；2015+ 用 GFLOPS（含 SIMD/NPU）近似为 MIPS 同量级
# 来源：US Census Bureau (UNIVAC), IBM Archives, Computer History Museum,
#       Smithsonian, IEEE Spectrum, Stanford, BLS, Intel ARK
PC_PRICES = [
    # (date, 整机价 USD, MIPS, 备注)
    ("1951-03", 1000000.0,    0.00190,  "UNIVAC I：5000 电子管 @ 2.25 MHz；1.9 KIPS"),
    ("1959-10",  150000.0,    0.0115,   "IBM 1401：晶体管 @ 87 KHz；11.5 KIPS"),
    ("1964-04",  133000.0,    0.0345,   "IBM System/360 M30：SLT @ 1 MHz；34.5 KIPS"),
    ("1975-01",     621.0,    0.5,      "Altair 8800：Intel 8080 @ 2.0 MHz；0.5 MIPS"),
    ("1977-06",    1298.0,    0.5,      "Apple II：MOS 6502 @ 1.02 MHz"),
    ("1981-08",    1565.0,    0.75,     "IBM PC 5150：Intel 8088 @ 4.77 MHz"),
    ("1983-12",     199.0,    0.5,      "C64 价格战钉死 $199；MOS 6510"),
    ("1984-01",    2495.0,    1.4,      "Macintosh 128K：MC68000 @ 7.83 MHz"),
    ("1990-06",    2500.0,    2.5,      "Compaq 386SX @ 16 MHz"),
    ("1995-06",    1900.0,    126.0,    "Pentium 75；超标量"),
    ("2000-06",     999.0,   2000.0,    "Athlon / Pentium III @ 1.0 GHz"),
    ("2005-06",     800.0,  10000.0,    "Pentium 4 Prescott @ 3.0 GHz；主频墙"),
    ("2015-06",     650.0, 110000.0,    "i5-6500 4c；~110 GFLOPS"),
    ("2020-06",     710.0, 400000.0,    "Ryzen 5 3600 / i5-10400 6c；~400 GFLOPS"),
    ("2024-06",     680.0, 700000.0,    "i5-14400 10c；~700 GFLOPS"),
    ("2026-06",     660.0, 45000000.0,  "AI PC 12-14c + NPU；~45 TOPS"),
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

    # 把每个 PC 点换算成 $/MIPS（整机价 ÷ MIPS），再缩放
    # 画图只用 PC_ORIGIN（1975-01）之后的数据；早于此的 1951/1959/1964 大型机保留在
    # md 表格里作为历史背景
    pc_plot_rows = [(ym, p, m, n) for ym, p, m, n in PC_PRICES if ym >= PC_ORIGIN]
    pc_per_unit = [(ym, price / mips, price, mips, note)
                   for ym, price, mips, note in pc_plot_rows]
    pc_anchor_per_unit = pc_per_unit[0][1]  # 1975-01 Altair: $621/0.5 = $1242/MIPS
    scale_pc = token_anchor_price / pc_anchor_per_unit
    pc_x = [months_since(ym, PC_ORIGIN) for ym, _, _, _, _ in pc_per_unit]
    pc_y_scaled = [pu * scale_pc for _, pu, _, _, _ in pc_per_unit]
    pc_max = max(pc_x)

    fig, ax = plt.subplots(figsize=(20, 8))
    fig.patch.set_facecolor("white")

    # ---- PC 线（蓝色虚线，标价） ----
    ax.plot(pc_x, pc_y_scaled, "--", color="#c0392b", lw=2.5,
            marker="s", ms=6, dashes=(2, 2),
            label=f"商业化计算机 $/MIPS × {scale_pc:.2e}（1975-01 = 2020-06 锚定）",
            zorder=3)
    for (ym, per_unit, price, mips, note), xv, yv in zip(
            pc_per_unit, pc_x, pc_y_scaled):
        mips_lbl = (f"{mips/1e6:.1f}TIPS" if mips >= 1e6
                    else f"{mips/1e3:.0f}GIPS" if mips >= 1e3
                    else f"{mips:.2f}MIPS" if mips >= 0.1
                    else f"{mips*1e3:.1f}KIPS")
        ax.annotate(f"{ym}\n${per_unit:,.4g}/MIPS\n({mips_lbl}, ${price:,.0f})",
                    (xv, yv), fontsize=5.8,
                    xytext=(5, -28), textcoords="offset points",
                    color="#c0392b", alpha=0.85)

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

    ax.set_ylabel("USD / 1M tokens（PC $/MIPS、互联网 $/Mbps 均按 1975/1993 起点 ≡ "
                  "2020-06 GPT-3 Davinci $60 缩放）", fontsize=9.5)
    ax.set_xlabel("token 真实日期 / 互联网真实年份 / PC 真实年份"
                  "（1975-01 PC、1993-09 互联网 → 2020-06 token 平移对齐）", fontsize=9)
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
    ax.axvline(pc_end_m, color="#c0392b", ls=":", lw=1, alpha=0.5, zorder=1)
    ax.text(pc_end_m + 1, y_top * 0.5,
            "PC 截止\n2026-06", fontsize=7, color="#c0392b", va="top")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8.5, ncol=2, framealpha=0.92)

    final_per_mbps = inet_per_mbps[-1][1]
    final_per_unit = pc_per_unit[-1][1]
    ax.set_title(
        f"商业化计算机 $/MIPS、互联网 $/Mbps、AI token $/1M tokens 三条等比叠加（Y log）\n"
        f"锚定：1975-01 Altair 8800 ${pc_anchor_per_unit:,.0f}/MIPS、"
        f"1993-09 互联网 ${inet_anchor_per_mbps:.0f}/Mbps、"
        f"2020-06 GPT-3 Davinci ${token_anchor_price:.0f}/1M tokens 三点同高\n"
        f"商业计算机 75 年 $/MIPS 从 ${pc_anchor_per_unit:,.0f} 跌到 ${final_per_unit:.2g}"
        f"（≈{pc_anchor_per_unit/final_per_unit:.0e}×）；"
        f"互联网 33 年 $/Mbps 跌 4400×；token 6 年顶 $50–$112、长尾 $0.1",
        fontsize=10.5, pad=12)

    fig.tight_layout()
    fig.savefig(OUT_PNG2, dpi=180, bbox_inches="tight")
    print(f"写入 {OUT_PNG2}")
    plt.close(fig)


def load_usage_rows():
    if not os.path.exists(USAGE_CSV):
        return []
    with open(USAGE_CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def plot_tokens_per_task():
    """token-usage-amount.csv 里 unit=tokens_per_task 的 51 个数据点散点图。
    X 轴时间（2020-06 → 2026-04），Y 轴 log（500 → 数十亿 tokens/task）。
    标注语义异常的"累积/窗口"点为 outlier，剩余画季度中位数趋势线。
    """
    rows = [r for r in load_usage_rows() if r["unit"] == "tokens_per_task"]
    if not rows:
        print(f"[!] {USAGE_CSV} 无 tokens_per_task 数据，跳过")
        return

    # 把语义不是"单 task"的标为 outlier（累积/多任务窗口）
    def is_outlier(r):
        s = (r["subject"] + " " + r.get("notes", "")).lower()
        return any(k in s for k in
                   ("cumulative", "5-hour window", "5h window", "per 5-hour",
                    "agent loop, single message", "single conversation",
                    "audiobook generation"))

    # 过滤：忽略"累积/窗口"语义异常点
    rows = [r for r in rows if not is_outlier(r)]
    for r in rows:
        r["_x"] = months_since(r["effective_date"], TOKEN_ORIGIN)
        r["_y"] = float(r["value"])

    provider_color = {
        "OpenAI": "#10a37f",
        "Anthropic": "#d97706",
        "Cursor": "#a855f7",
        "Google": "#4285f4",
        "DeepSeek": "#1a1a2e",
        "Microsoft": "#0078d4",
        "Self_reported": "#888",
    }
    default_color = "#bbb"
    conf_size = {"high": 70, "medium": 50, "flag": 30, "low": 30}

    fig, ax = plt.subplots(figsize=(15, 7.5))
    fig.patch.set_facecolor("white")

    # 主散点
    by_provider = {}
    for r in rows:
        p = r["provider"]
        by_provider.setdefault(p, []).append(r)
    for p, items in by_provider.items():
        c = provider_color.get(p, default_color)
        xs = [r["_x"] for r in items]
        ys = [r["_y"] for r in items]
        ss = [conf_size.get(r["confidence"], 40) for r in items]
        if xs:
            ax.scatter(xs, ys, s=ss, c=c, alpha=0.75, edgecolors="white",
                       linewidths=0.6, label=p, zorder=3)

    # 季度中位数趋势线（用非 outlier 数据）
    from collections import defaultdict
    qmed = defaultdict(list)
    for r in rows:
        y, m = r["effective_date"].split("-")
        q = (int(m) - 1) // 3
        qkey = (int(y), q)
        qmed[qkey].append(r["_y"])
    import statistics
    qkeys = sorted(qmed.keys())
    qx, qy = [], []
    for y, q in qkeys:
        # 季度中点 = 该季度第二个月
        month = q * 3 + 2
        qx.append(months_since(f"{y}-{month:02d}", TOKEN_ORIGIN))
        qy.append(statistics.median(qmed[(y, q)]))
    ax.plot(qx, qy, "-", color="#444", lw=1.6, alpha=0.55,
            label="季度中位数", zorder=2)

    # 标注几个关键点
    annotated = [
        ("2020-06", 500,       "GPT-3 API\n典型调用", (8, 8)),
        ("2024-06", 600,       "ChatGPT 单轮\n348 词", (8, 8)),
        ("2024-09", 1_000_000, "Claude Dev\nVS Code session", (8, -16)),
        ("2025-04", 3_500_000, "OpenAI Codex\nagentic task", (8, 8)),
        ("2025-07", 7_000_000, "Claude Code\n(bloated CLAUDE.md)", (8, 8)),
    ]
    for ym, v, lbl, off in annotated:
        if ym is None:
            continue
        x = months_since(ym, TOKEN_ORIGIN)
        ax.annotate(lbl, (x, v), fontsize=7, color="#333",
                    xytext=off, textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", color="#888", lw=0.5, alpha=0.6))

    ax.set_yscale("log")
    ax.set_ylim(80, 5e7)
    ax.set_xlim(-3, months_since("2026-06", TOKEN_ORIGIN) + 3)

    # X 轴：每年 6 月一个刻度
    tick_months, tick_labels = [], []
    for year in range(2020, 2027):
        m = months_since(f"{year}-06", TOKEN_ORIGIN)
        if -3 <= m <= months_since("2026-06", TOKEN_ORIGIN) + 3:
            tick_months.append(m)
            tick_labels.append(f"{year}-06")
    ax.set_xticks(tick_months)
    ax.set_xticklabels(tick_labels, fontsize=8, rotation=30, ha="right")
    ax.set_xlabel("帖子日期 / 数据点时间（2020-06 token-price.csv 起点）", fontsize=9)

    ax.set_ylabel("单任务 token 消耗（log）", fontsize=10)
    ax.grid(alpha=0.25, which="both", axis="y")
    ax.grid(alpha=0.15, which="major", axis="x")
    ax.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.92)

    ax.set_title(
        f"单任务 token 消耗的演变（2020-06 → 2026-04，{len(rows)} 个有效数据点；"
        "已剔除累积/窗口语义异常点）\n"
        "GPT-3 时代单次 API 调用 ~500 tokens → 2025 agentic 工作流 1–3M tokens / 单 task\n"
        "marker 颜色 = provider；marker 大小 = confidence(high/medium/flag)；"
        "灰线 = 季度中位数",
        fontsize=10.5, pad=12)

    fig.tight_layout()
    fig.savefig(OUT_PNG3, dpi=180, bbox_inches="tight")
    print(f"写入 {OUT_PNG3}")
    plt.close(fig)


def _monthly_price_lookup(rows, providers):
    """对每个 (provider, YYYY-MM) 返回当月该 provider 在售最贵 blended 价。
    内部用 forward-fill：如果当月没新价，沿用上一个有效价；模型退市后跳过。
    """
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
        models[b].append((r["effective_date"], (i + o) / 2, name))

    def best_at(b, ym):
        best = 0
        for em, bl, name in models[b]:
            if em > ym:
                continue
            dep = DEPRECATED.get(name)
            if dep and dep <= ym:
                continue
            if bl > best:
                best = bl
        return best  # 0 means no model at this time

    return best_at


def compute_task_price_series():
    """返回 (series_usd, series_tpt, providers, price_at, price_rows)。
    每个 series 是按 QUARTERS 顺序的 list（NaN 表示无数据）。
    """
    usage_rows = [r for r in load_usage_rows() if r["unit"] == "tokens_per_task"]
    if not usage_rows:
        return None

    def is_outlier(r):
        s = (r["subject"] + " " + r.get("notes", "")).lower()
        return any(k in s for k in
                   ("cumulative", "5-hour window", "5h window", "per 5-hour",
                    "agent loop, single message", "single conversation",
                    "audiobook generation"))
    usage_rows = [r for r in usage_rows if not is_outlier(r)]

    # provider 字段映射到 token-price.csv 里有的 4 家；映射不到的仅进全平台中位数
    PROVIDER_MAP = {
        "OpenAI": "OpenAI",
        "Anthropic": "Anthropic",
        "Google": "Google",
        "DeepSeek": "DeepSeek",
        "Microsoft": "OpenAI",
        "Cursor": "Anthropic",
        "public_share_analysis": "OpenAI",
        "third_party_benchmark": "Anthropic",
        "calculation": "OpenAI",
        "community_estimate": "Anthropic",
    }
    providers = ["OpenAI", "Anthropic", "Google", "DeepSeek"]
    price_rows = load_rows()
    price_at = _monthly_price_lookup(price_rows, providers)

    # 把每条 usage row 归到季度 + 4 家映射。
    # 季度键用 QUARTERS 中的 (y, q)（q 是 1-indexed Q1=1…Q4=4），从 month 计算 q 时
    # 注意 1-indexed: m=1,2,3→Q1；m=4,5,6→Q2；m=7,8,9→Q3；m=10,11,12→Q4
    import statistics
    from collections import defaultdict
    per_provider_q = {b: defaultdict(list) for b in providers}
    all_q = defaultdict(list)
    for r in usage_rows:
        ym = r["effective_date"][:7]
        y, m = ym.split("-")
        q = (int(m) - 1) // 3 + 1
        qkey = (int(y), q)
        v = float(r["value"])
        all_q[qkey].append(v)
        mapped = PROVIDER_MAP.get(r["provider"])
        if mapped:
            per_provider_q[mapped][qkey].append(v)

    # 4 家各自 forward-fill 系列：tokens/task[本家中位数→全平台中位数→上一季度]
    series_tpt = {b: [] for b in providers}    # tokens/task per quarter
    series_usd = {b: [] for b in providers}    # USD/task per quarter

    last_seen = {b: None for b in providers}
    last_global_tpt = None

    for (y, q), qe in zip(QUARTERS, QEND):
        gq = (y, q)
        # 全平台中位数 fallback
        if all_q[gq]:
            last_global_tpt = statistics.median(all_q[gq])
        for b in providers:
            # 该家本季度中位数
            if per_provider_q[b][gq]:
                tpt = statistics.median(per_provider_q[b][gq])
                last_seen[b] = tpt
            else:
                tpt = last_seen[b] if last_seen[b] is not None else last_global_tpt
            series_tpt[b].append(tpt)
            # 价格 × tokens / 1e6 = USD
            price = price_at(b, qe)
            if tpt is None or price <= 0:
                series_usd[b].append(float("nan"))
            else:
                series_usd[b].append(price * tpt / 1e6)

    return series_usd, series_tpt, providers, price_at, price_rows


def plot_task_price(plus, pro_pt, max20):
    """token-price.png 风格的 task-price 折线图：4 家品牌各一条季度线。"""
    bundle = compute_task_price_series()
    if bundle is None:
        print("[!] 无 tokens_per_task 数据，跳过 task-price 图")
        return
    series_usd, series_tpt, providers, price_at, price_rows = bundle

    # 套餐 per-token 折合（USD / 1M tokens）按季度展开
    # OpenAI Plus：从 plus 列表 forward-fill
    plus_per_token_q = forward_fill(sorted(plus))   # 长度 = QEND
    # Anthropic Pro：从 Claude Pro 上线日起 forward-fill 单值
    pro_pt_q = []
    pro_start_ym = next(r["effective_date"] for r in price_rows
                        if r["product_or_model"] == "Claude Pro")
    for qe in QEND:
        pro_pt_q.append(pro_pt if qe >= pro_start_ym else None)
    # Anthropic Max 20x：从 max20[0] 起 forward-fill
    max20_pt_q = []
    for qe in QEND:
        max20_pt_q.append(max20[4] if qe >= max20[0] else None)

    # 用全平台 tokens/task 季度中位数（forward-fill），让套餐线在 OpenAI/Anthropic
    # 各自 tokens/task 缺失时也有合理 fallback
    series_oai_tpt = series_tpt["OpenAI"]
    series_anth_tpt = series_tpt["Anthropic"]

    def usd_per_task(per_token_q, tpt_q):
        out = []
        for pt, tpt in zip(per_token_q, tpt_q):
            if pt is None or tpt is None:
                out.append(float("nan"))
            else:
                out.append(pt * tpt / 1e6)
        return out

    plus_task = usd_per_task(plus_per_token_q, series_oai_tpt)
    pro_task = usd_per_task(pro_pt_q, series_anth_tpt)
    max20_task = usd_per_task(max20_pt_q, series_anth_tpt)

    # ---- 画图（token-price.png 风格，双 Y 轴） ----
    x = list(range(len(QUARTERS)))
    fig, ax1 = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("white")
    api_colors = {"OpenAI": "#10a37f", "Anthropic": "#d97706",
                  "Google": "#4285f4", "DeepSeek": "#1a1a2e"}
    for b in providers:
        ax1.plot(x, series_usd[b], "-", color=api_colors[b], lw=2.2,
                 marker="o", ms=4, label=f"{b} API max", zorder=3)

    ax1.set_ylabel("API 旗舰 task price (USD/task)", fontsize=10)
    api_max = max((v for b in providers for v in series_usd[b] if v == v), default=50)
    ax1.set_ylim(-2, api_max * 1.1)
    ax1.set_xticks(x)
    sparse_labels = [lbl if lbl.endswith("Q1") or i == 0 or i == len(x) - 1 else ""
                     for i, lbl in enumerate(QLABEL)]
    ax1.set_xticklabels(sparse_labels, rotation=45, ha="right", fontsize=8)
    ax1.grid(axis="y", alpha=0.25)
    ax1.grid(axis="x", alpha=0.12)

    # 右轴：套餐摊销 task price（量级低 30-50×）
    ax2 = ax1.twinx()
    ax2.plot(x, plus_task, "--", color="#10a37f", lw=1.6, marker="s", ms=3,
             alpha=0.85, label="ChatGPT Plus $20 摊销")
    ax2.plot(x, pro_task, "--", color="#d97706", lw=1.6, marker="^", ms=3,
             alpha=0.85, label="Claude Pro $20 摊销")
    ax2.plot(x, max20_task, ":", color="#d97706", lw=1.6, marker="v", ms=3,
             alpha=0.7, label="Claude Max 20x $200 摊销")
    sub_max = max((v for series in (plus_task, pro_task, max20_task)
                   for v in series if v == v), default=2)
    ax2.set_ylim(-sub_max * 0.05, sub_max * 1.15)
    ax2.set_ylabel("套餐摊销 task price (USD/task)", fontsize=10)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=7.8,
               ncol=2, framealpha=0.92)

    ax1.set_title(
        "Task Price = tokens/task × 单价（2020-2026）\n"
        "左轴（实线）= API 旗舰 blended × 本家 tokens/task 中位数；"
        "右轴（虚/点线）= 套餐月费摊销到 task",
        fontsize=10.5, pad=12)

    fig.tight_layout()
    fig.savefig(OUT_PNG4, dpi=180, bbox_inches="tight")
    print(f"写入 {OUT_PNG4}")
    plt.close(fig)


def plot_task_price_vs_internet_pc():
    """token-price-vs-internet-pc.png 风格：把"USD/task"和 PC $/MIPS、
    互联网 $/Mbps 三条等比叠加。
    锚定：2020-06 GPT-3 API typical task = $60/1M × 500 tokens / 1e6 = $0.03
    PC 1975-01 → 2020-06；互联网 1993-09 → 2020-06。
    """
    bundle = compute_task_price_series()
    if bundle is None:
        print("[!] 无 tokens_per_task，跳过 task-price-vs-internet-pc")
        return
    series_usd, _series_tpt, providers, _price_at, _price_rows = bundle

    # 三方锚点都对齐到 task price 2020-06 的 OpenAI USD/task
    # （取 series_usd["OpenAI"] 第一个有效值）
    oai_first = next((v for v in series_usd["OpenAI"] if v == v and v > 0), None)
    if oai_first is None:
        oai_first = 0.03  # 兜底
    task_anchor = oai_first

    # 互联网：1993-09 → 2020-06 = task_anchor
    inet_per_mbps = [(ym, price / mbps, price, mbps, note)
                     for ym, price, mbps, note in INTERNET_PRICES]
    inet_anchor_per_mbps = inet_per_mbps[0][1]
    scale_inet = task_anchor / inet_anchor_per_mbps

    # PC：1976-07 → 2020-06 = task_anchor
    pc_plot_rows = [(ym, p, m, n) for ym, p, m, n in PC_PRICES if ym >= PC_ORIGIN]
    pc_per_unit = [(ym, price / mips, price, mips, note)
                   for ym, price, mips, note in pc_plot_rows]
    pc_anchor_per_unit = pc_per_unit[0][1]
    scale_pc = task_anchor / pc_anchor_per_unit

    inet_x = [months_since(ym, INTERNET_ORIGIN) for ym, _, _, _, _ in inet_per_mbps]
    inet_y_scaled = [pm * scale_inet for _, pm, _, _, _ in inet_per_mbps]
    pc_x = [months_since(ym, PC_ORIGIN) for ym, _, _, _, _ in pc_per_unit]
    pc_y_scaled = [pu * scale_pc for _, pu, _, _, _ in pc_per_unit]
    inet_max = max(inet_x)
    pc_max = max(pc_x)

    fig, ax = plt.subplots(figsize=(20, 8))
    fig.patch.set_facecolor("white")

    # PC 红虚线
    ax.plot(pc_x, pc_y_scaled, "--", color="#c0392b", lw=2.5,
            marker="s", ms=6, dashes=(2, 2),
            label=f"商业化计算机 $/MIPS × {scale_pc:.2e}（1975-01 = 2020-06 锚定）",
            zorder=3)
    for (ym, per_unit, price, mips, note), xv, yv in zip(
            pc_per_unit, pc_x, pc_y_scaled):
        mips_lbl = (f"{mips/1e6:.1f}TIPS" if mips >= 1e6
                    else f"{mips/1e3:.0f}GIPS" if mips >= 1e3
                    else f"{mips:.2f}MIPS" if mips >= 0.1
                    else f"{mips*1e3:.1f}KIPS")
        ax.annotate(f"{ym}\n${per_unit:,.4g}/MIPS\n({mips_lbl}, ${price:,.0f})",
                    (xv, yv), fontsize=5.8,
                    xytext=(5, -28), textcoords="offset points",
                    color="#c0392b", alpha=0.85)

    # 互联网灰虚线
    ax.plot(inet_x, inet_y_scaled, "--", color="#666", lw=2.5,
            marker="o", ms=6, dashes=(5, 3),
            label=f"互联网 $/Mbps × {scale_inet:.4f}（1993-09 = 2020-06 锚定）",
            zorder=4)
    for (ym, per_mbps, price, mbps, note), xv, yv in zip(
            inet_per_mbps, inet_x, inet_y_scaled):
        ax.annotate(f"{ym}\n${per_mbps:.2f}/Mbps\n({mbps}M, ${price:.0f}/月)",
                    (xv, yv), fontsize=5.8,
                    xytext=(5, 7), textcoords="offset points",
                    color="#444", alpha=0.85)

    # AI 4 家 task price 实线（加粗 + 大 marker，token 区域只占整张图 12% 宽度，
    # 易被压扁）
    api_colors = {"OpenAI": "#10a37f", "Anthropic": "#d97706",
                  "Google": "#4285f4", "DeepSeek": "#1a1a2e"}
    for b in providers:
        c = api_colors[b]
        bx = [months_since(qe, TOKEN_ORIGIN) for qe in QEND]
        by = series_usd[b]
        ax.plot(bx, by, "-", color=c, lw=2.4, marker="o", ms=5,
                label=f"{b} API task price", zorder=5)

    # OpenAI 起点显式标注（X=0 容易和 PC 1976-07 标注挤在一起）
    if series_usd["OpenAI"] and series_usd["OpenAI"][0] == series_usd["OpenAI"][0]:
        v0 = series_usd["OpenAI"][0]
        ax.annotate(f"2020-06 OpenAI\nGPT-3 task ${v0:.3f}",
                    (0, v0), fontsize=7.5, color="#10a37f", fontweight="bold",
                    xytext=(8, 22), textcoords="offset points",
                    arrowprops=dict(arrowstyle="->", color="#10a37f", lw=0.9))

    # X 轴三语标签
    x_max = max(pc_max, inet_max) + 12
    ax.set_xlim(-6, x_max)
    token_end_m = months_since("2026-06", TOKEN_ORIGIN)
    inet_end_m = months_since("2026-06", INTERNET_ORIGIN)
    pc_end_m = pc_max
    tick_months, tick_labels = [], []
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

    ax.set_ylabel(f"USD/task（PC $/MIPS、互联网 $/Mbps 均按 1975/1993 起点 ≡ "
                  f"2020-06 GPT-3 API task ${task_anchor:.3f} 缩放）", fontsize=9.5)
    ax.set_xlabel("token 真实日期 / 互联网真实年份 / PC 真实年份"
                  "（1975-01 PC、1993-09 互联网 → 2020-06 task 平移对齐）", fontsize=9)
    ax.set_yscale("log")
    y_top = max(max(inet_y_scaled), max(pc_y_scaled),
                max(v for b in providers for v in series_usd[b] if v == v)) * 1.5
    y_bot = min(min(pc_y_scaled), min(inet_y_scaled)) * 0.5
    ax.set_ylim(y_bot, y_top)

    # 各曲线截止竖线
    ax.axvline(token_end_m, color="#10a37f", ls=":", lw=1, alpha=0.5, zorder=1)
    ax.text(token_end_m + 1, y_top * 0.5,
            "task 截止\n2026-06", fontsize=7, color="#10a37f", va="top")
    ax.axvline(inet_end_m, color="#666", ls=":", lw=1, alpha=0.5, zorder=1)
    ax.text(inet_end_m + 1, y_top * 0.5,
            "互联网截止\n2026-06", fontsize=7, color="#666", va="top")
    ax.axvline(pc_end_m, color="#c0392b", ls=":", lw=1, alpha=0.5, zorder=1)
    ax.text(pc_end_m + 1, y_top * 0.5,
            "PC 截止\n2026-06", fontsize=7, color="#c0392b", va="top")

    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8.5, ncol=2, framealpha=0.92)

    final_pc = pc_per_unit[-1][1]
    final_inet = inet_per_mbps[-1][1]
    task_now = max(v for b in providers for v in series_usd[b] if v == v)
    ax.set_title(
        f"USD/task vs 互联网 $/Mbps vs 商业化计算机 $/MIPS（Y log，三条等比叠加）\n"
        f"锚定：1975-01 Altair 8800 ${pc_anchor_per_unit:,.0f}/MIPS、"
        f"1993-09 互联网 ${inet_anchor_per_mbps:.0f}/Mbps、"
        f"2020-06 GPT-3 API task ${task_anchor:.3f} 三点同高\n"
        f"商业计算机 75 年跌 ~{pc_anchor_per_unit/final_pc:.0e}×；"
        f"互联网 33 年跌 ~{inet_anchor_per_mbps/final_inet:,.0f}×；"
        f"USD/task 6 年从 ${task_anchor:.3f} 涨到 ${task_now:.1f}（≈{task_now/task_anchor:,.0f}× 反向上行）",
        fontsize=10.5, pad=12)

    fig.tight_layout()
    fig.savefig(OUT_PNG5, dpi=180, bbox_inches="tight")
    print(f"写入 {OUT_PNG5}")
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
    for ym, price, mips, note in PC_PRICES:
        mips_lbl = (f"{mips/1e6:.1f} TIPS" if mips >= 1e6
                    else f"{mips/1e3:.0f} GIPS" if mips >= 1e3
                    else f"{mips:.2f} MIPS" if mips >= 0.1
                    else f"{mips*1e3:.1f} KIPS")
        per_unit = price / mips
        pc_tbl.append(
            f"| {ym} | ${price:,.2f} | {mips_lbl} | ${per_unit:,.4g} | {note} |")

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

## 与商业化计算机 $/MIPS、互联网 $/Mbps 的三条等比叠加

把商业化计算机（1951-）、美国互联网接入（1993-）、AI token（2020-）三条曲线统一到
token 坐标系：

- **时间平移**：三条线各自起点对齐到 token 2020-06，
  - 商业微机 1975-01 Altair 8800 → 2020-06（+545 月，**45 年**），最后点 2026-06 落到 token 2071-06；
    *（更早的 UNIVAC I 1951 / IBM 1401 1959 / System/360 1964 三个大型机点见数据表，仅作历史背景，不进图。）*
  - 互联网 1993-09 → 2020-06（+321 月），最后点 2026-06 落到 token 2053-03；
  - token 自身原位。
- **指标统一**：均取"行业核心通缩指标"——
  - 计算机：**$/MIPS**（整机售价 ÷ 每秒指令数）。横跨电子管（UNIVAC 1.9 KIPS）→
    晶体管（IBM 1401 11.5 KIPS）→ 集成电路（System/360 34.5 KIPS）→ 微处理器（Intel 8080）→
    多核（i5 4-10c）→ NPU（45 TOPS）。
  - 互联网：**$/Mbps**（月费 ÷ 典型下行速率）；
  - token：**$/1M tokens**（API 最贵模型 blended）。
- **等比缩放**：三条线起点价 ≡ 2020-06 GPT-3 Davinci $60/1M tokens，
  - 计算机：1975-01 Altair 8800 约 **$1242/MIPS**（$621 ÷ 0.5 MIPS）→ $60；
  - 互联网：1993-09 约 $691/Mbps → $60；
  - token 不缩放。
- **Y 轴 log**：商业微机 45 年 $/MIPS 从 $1242 跌到 ~$1.47e-5（≈**8400 万倍**），
  若把更早的 1951 UNIVAC I（$526M/MIPS）算进来，75 年跨度跌 ~3.6e13 倍；
  互联网 33 年 $/Mbps 跌 ~4400×，token 6 年最贵在 $50–$112 + 长尾 $0.1。

![商业计算机 + 互联网 + token 三条等比叠加](token-price-vs-internet-pc.png)

- **红虚线**：商业微机 $/MIPS，方形 marker（从 1975 Altair 8800 起；早于此的大型机
  数据见下表）。
- **灰虚线**：互联网 $/Mbps，圆形 marker。
- **彩实线**：各家 token API 最贵模型 blended。

**观感**：log 空间里 45 年商业微机 $/MIPS 曲线接近完美指数下行——可清晰看到 1995 Pentium
超标量切一刀、2000 千兆赫兹再切一刀、2015+ 多核 + AVX 再降几阶、2026 NPU 跳一阶。
互联网斜率明显比微机缓；**而 token 最贵端 6 年几乎横盘**——OpenAI $60 → $90 → $112.5 → $50
震荡一圈净跌 ~17%，Anthropic $45 横盘到 $15。**DeepSeek 把同等天花板按到 $0.1**（≈600×）
那是"模型规模阶梯"（小模型替代旗舰、混合精度），不是同一模型连续降价。
所以 token 最贵端跟微机 / 互联网"单位资源指数通缩"的曲线形态是断开的——前者横盘，
后两者持续下行。下一节 USD/task 视角揭示横盘背后的真相：单价不跌，但单任务用量涨 ~1000×，
**用户净支出反而上行**。

### 商业化计算机整机价 → $/MIPS 数据点

| 日期 | 整机售价 | 算力 | $/MIPS | 备注 |
|---|---|---|---|---|
{chr(10).join(pc_tbl)}

数据来源：US Census Bureau（UNIVAC I）、IBM Archives（1401 / System/360 / IBM PC）、
Computer History Museum、Smithsonian（Altair 8800）、Apple Inc. 官方目录（Apple II）、
NYT Archive（1983 TI 退出）、IEEE Spectrum（C64 价格战）、Stanford "Making the Macintosh"、
PC Magazine via Google Books、Washington Post（1995 Pentium）、Gartner/IDC（2000 $999 价格战）、
BLS Computer Price Deflation、Intel ARK / AMD 官方处理器规格。

### 互联网月费 → $/Mbps 数据点

| 日期 | 名义月费 | 速率 (Mbps) | $/Mbps | 备注 |
|---|---|---|---|---|
{chr(10).join(inet_tbl)}

互联网数据来源：EH.Net、NYT Archive (1994)、Computerworld、CNET、Smithsonian、Pew Research、
FCC Historical Reports、WSJ、Bruce Kushnick / Teletruth、**USTelecom Broadband Pricing Index**、
NCTA、BLS CPI (Internet Access Services)。

## 单任务 token 消耗的演变

token 单价跌了，但**单任务消耗的 token 量同期也涨了**——这是判断"用户实际净支出"是否真降的
关键变量。数据来自 `token-usage-amount.csv`（含 agent web 研究 + 从 Reddit 三步法挖出的
163 个高置信度数据点），其中 `unit=tokens_per_task` 原始 51 条，**剔除"累积/窗口"语义异常点
（如 Claude Code 5h 窗口聚合 20–40M、Cursor agent loop 单 message 241M、Claude Code app dev
累积 2.2B 等）后剩 45 个有效数据点**，时间跨 **2020-06 → 2026-04**。

![单任务 token 消耗](tokens-per-task.png)

- **散点**：每个数据点 = 一次"单任务/单 session"用量观察；颜色按 provider（OpenAI 绿、
  Anthropic 橙、Cursor 紫、其他灰），marker 大小按 confidence。
- **灰实线**：季度中位数趋势——直观看到 2020 → 2024 中位数从 ~500 tokens 涨到 ~10K-100K，
  2025 agentic 工作流后跳到 1–3M tokens/task 量级。

**结论**：单任务 token 量在 6 年内涨了 **~1000×–10000×**（GPT-3 API 调用 ~500 → Claude Code
session 1–3M）。同期最贵 API 单价大约跌 ~50%（$60 → $25–$50），便宜端跌 ~500×（DeepSeek $0.1）。
**净影响**：用户实际净支出仍在涨——单任务花钱量级是 6 年前的 ~10–100 倍。这与各家平台
吞吐 20–50× / 年的增长是同源现象（更长任务 + 更多用户 + 更高频调用）。

## 单 task 实际花费 USD（task-price）

把 **tokens/task** 和 **单价** 按品牌相乘，得到"用该家旗舰跑一个 task 要花多少钱"的
季度演变。与 token-price.png 同风格：4 家 API 实线 + 3 条套餐摊销虚线/点线，X 轴季度。

![单 task 实际花费 USD](task-price.png)

- **实线（4 条 API 旗舰）**：task price = 该家季度旗舰 blended × 该家季度 tokens/task 中位数 ÷ 1e6。
- **虚/点线（3 条套餐摊销）**：
  - **ChatGPT Plus $20 摊销** = OpenAI Plus 每 token 折合 × OpenAI tokens/task 中位数 ÷ 1e6
  - **Claude Pro $20 摊销** = Anthropic Pro per-token × Anthropic tokens/task 中位数
  - **Claude Max 20x $200 摊销** = Max20x per-token × Anthropic tokens/task 中位数
- **fallback 顺序**：本家本季度数据 → 全平台本季度中位数 → 上一季度沿用（forward-fill）。
- **provider 映射**：Cursor → Anthropic、Microsoft → OpenAI、community_estimate /
  third_party_benchmark / public_share_analysis / calculation 按归属厂家映射；
  Aggregator / Self_reported 不归本家、仅进全平台中位数。

**语义**：token-price.png（单价）× tokens-per-task.png（用量）= 用户实际感知的
**「每完成一件事要花多少钱」**。单价跌 ~10–100×、用量涨 ~1000–10000×，**净花费仍上行**
——这就是 ChatGPT Plus / Claude Pro / Cursor $20–$200 套餐 2025–2026 年纷纷加套使用限制
（周限、autocompact、premium request 配额）的根因。

## USD/task 与商业微机 $/MIPS、互联网 $/Mbps 的等比叠加

用与 token 单价等比叠加图相同的方法（微机 1975-01、互联网 1993-09、token 2020-06 三起点
平移到同一 Y 高度，Y 轴 log），把"按 API 价计算的 USD/task"作为 token 端的对照量替进去。
锚点：**2020-06 GPT-3 API typical task ≈ $0.03/task**（$60/1M × 500 tokens）。

![USD/task vs 互联网 vs 微机 等比叠加](task-price-vs-internet-pc.png)

- **红虚线**：商业微机 $/MIPS，从 1975 Altair 8800 起（更早的大型机仅在数据表中）。
- **灰虚线**：互联网 $/Mbps。
- **彩实线**：4 家 API 旗舰 task price，2020-06 OpenAI 起 $0.03，2024–2026 agentic 后蹿到 $1–$45。

**核心反差**：商业微机 45 年 $/MIPS 跌 ~8400 万倍、互联网 33 年 $/Mbps 跌 ~4400×——
这两条都是**指数下行**；而 USD/task 6 年从 $0.03 **反向上行到 $20–$45**（≈1000×）。
**当历史上"单位资源价格 → 0"的曲线在 AI 时代是"单任务花费 → ∞"**。

## 假设与局限

- **每条消息 {TOKENS_PER_MESSAGE} token** 是折算口径；改它整体平移套餐线但不改品牌相对关系。
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
- **商业计算机 $/MIPS** 统一了 75 年的算力指标，但口径在不同时代有偏差：
  早期电子管 / 晶体管 / 集成电路时代的 KIPS / MIPS 是直接每秒指令数；
  Pentium 之后 superscalar + OOO 使 IPC > 1，2015+ 用 GFLOPS 近似 MIPS（FLOPS 包含 SIMD），
  2026 加上 NPU TOPS（AI 加速、非通用算力）——这些数字间存在 ~2–5× 的口径差，
  但量级上不影响曲线的指数下行斜率。
"""
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"写入 {OUT_MD}")

    plot_vs_internet(rows, env, order, plus, anth_plans, pro_pt, max20)
    plot_tokens_per_task()
    plot_task_price(plus, pro_pt, max20)
    plot_task_price_vs_internet_pc()

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
