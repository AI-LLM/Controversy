#!/usr/bin/env python3
"""根据 chat/token-price.csv 生成 token-price.md 中的对比图表。

把两类价格归一到同一根轴 —— **USD / 1M tokens(blended，取输入输出均值)**，
再取 log10，便于跨品牌横向、跨时间纵向比较：

1. 各家旗舰模型 API blended 价随时间变化（log10 $/1M）。
2. 消费套餐按用量折合的 per-token 区间 [最低, 最高]（log10 $/1M）：
   - 套餐不按 token 计费，故设「每条消息 = TOKENS_PER_MESSAGE token」。
   - 最低（地板）= 月价 ÷ 把配额用满时的月 token 数（重度用户）。
   - 最高（天花板）= 月价 ÷ 轻度基线 CASUAL_MSGS_PER_MONTH 条的 token 数。

图表用 mermaid xychart-beta。xychart-beta 无图例，故每图正文标注线序与终值。
"""
from __future__ import annotations

import csv
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "chat", "token-price.csv")
OUT = os.path.join(HERE, "token-price.md")

# ---- 折算假设（全部可调，已在正文披露） ----
TOKENS_PER_MESSAGE = 2000       # 每条消息折合 token（1k 入 + 1k 出，blended）
CASUAL_MSGS_PER_MONTH = 30      # 轻度用户基线：约每天 1 条

# ---- 旗舰模型链（按 product_or_model 精确匹配 CSV，单一数据源） ----
FLAGSHIP = {
    "OpenAI": ["gpt-4 (8K)", "gpt-4-turbo (1106-preview)", "gpt-4o-2024-05-13",
               "gpt-4o-2024-08-06", "gpt-4.1", "gpt-5", "gpt-5.4", "gpt-5.5"],
    "Anthropic": ["Claude 2.1", "Claude 3 Opus", "Claude Opus 4", "Claude Opus 4.1",
                  "Claude Opus 4.5", "Claude Opus 4.6", "Claude Opus 4.7", "Claude Opus 4.8"],
    "Google": ["Gemini 1.0 Pro", "Gemini 1.5 Pro (<=128K)", "Gemini 1.5 Pro (<=128K cut)",
               "Gemini 2.5 Pro (<=200K)", "Gemini 3.1 Pro (<=200K)"],
    "DeepSeek": ["DeepSeek-V2 (deepseek-chat)", "deepseek-chat V2 + context caching",
                 "DeepSeek-V3 (promo)", "DeepSeek-V3 (standard)", "DeepSeek-V3.1 (unified)",
                 "DeepSeek-V3.2-Exp", "DeepSeek-V4 Pro (promo 75% off)", "DeepSeek-V4 Pro (standard)"],
}

# 季度时间轴 2023Q1 .. 2026Q2
QUARTERS = [(y, q) for y in range(2023, 2027) for q in (1, 2, 3, 4)]
QUARTERS = [(y, q) for (y, q) in QUARTERS if not (y == 2026 and q > 2)]
QLABEL = [f"{y % 100}Q{q}" for (y, q) in QUARTERS]
QEND = [f"{y}-{q*3:02d}" for (y, q) in QUARTERS]   # 每季度末月 YYYY-MM


def load_rows():
    with open(CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fnum(s):
    s = (s or "").strip()
    return float(s) if s else None


def flagship_series(rows):
    """返回 {brand: [(ym, blended, in, out, model), ...]} 按日期排序。"""
    out = {}
    for brand, names in FLAGSHIP.items():
        pts = []
        for r in rows:
            if r["provider"] == brand and r["category"] == "API" and r["product_or_model"] in names:
                i, o = fnum(r["input_per_1m_usd"]), fnum(r["output_per_1m_usd"])
                if i is not None and o is not None:
                    pts.append((r["effective_date"], (i + o) / 2, i, o, r["product_or_model"]))
        out[brand] = sorted(pts, key=lambda x: x[0])
    return out


def forward_fill(points):
    """points=[(ym, val)] -> 每个季度一个值（取 <= 季末的最近值；季前 pad 首值）。"""
    pts = sorted(points, key=lambda x: x[0])
    vals, first = [], pts[0][1]
    for qe in QEND:
        cur = first
        for ym, v in pts:
            if ym <= qe:
                cur = v
            else:
                break
        vals.append(cur)
    return vals


CAP_RE = re.compile(
    r"(\d[\d,]*)\s*(?:msgs?|messages?|queries|prompts?|requests?)\s*"
    r"(?:/|per|every|a|each)?\s*(\d*)\s*(hours?|hrs?|h|days?|weeks?|months?)",
    re.IGNORECASE,
)
PERIOD_PER_MONTH = {"h": None, "hour": None, "hr": None,
                    "day": 30.0, "week": 30.0 / 7, "month": 1.0}


def cap_to_msgs_per_month(text):
    """从 usage_limit 文本解析「消息/月」上限；解析不出返回 None。"""
    m = CAP_RE.search(text or "")
    if not m:
        return None
    count = float(m.group(1).replace(",", ""))
    n = float(m.group(2)) if m.group(2) else 1.0
    unit = m.group(3).lower().rstrip("s")
    if unit in ("h", "hour", "hr"):                 # 每 n 小时：理论满载（24/7）
        windows = (30 * 24) / n
        return count * windows
    return count * PERIOD_PER_MONTH[unit] / n


def per_token_band(price, msgs_per_month):
    """返回 (min_per_1M, max_per_1M)：下限=榨满配额，上限=轻度基线。"""
    floor = price / (msgs_per_month * TOKENS_PER_MESSAGE) * 1e6
    casual_msgs = min(CASUAL_MSGS_PER_MONTH, msgs_per_month)
    ceil = price / (casual_msgs * TOKENS_PER_MESSAGE) * 1e6
    return floor, ceil


def lg(v):
    return round(math.log10(v), 3)


def sub_series(rows, prefix):
    """挑选 product_or_model 以 prefix 开头、可解析配额的套餐行。"""
    pts = []
    for r in rows:
        if r["product_or_model"].startswith(prefix):
            price = fnum(r["monthly_price_usd"])
            cap = cap_to_msgs_per_month(r["usage_limit"])
            if price and cap:
                lo, hi = per_token_band(price, cap)
                pts.append((r["effective_date"], r["product_or_model"], price, cap, lo, hi))
    return sorted(pts, key=lambda x: x[0])


def xychart(title, yaxis, ymin, ymax, lines):
    """lines=[(label, [values...])]，返回 mermaid 代码块字符串。"""
    out = ["```mermaid", "xychart-beta", f'    title "{title}"',
           "    x-axis [" + ", ".join(QLABEL) + "]",
           f'    y-axis "{yaxis}" {ymin} --> {ymax}']
    for _, vals in lines:
        out.append("    line [" + ", ".join(f"{v:.2f}" for v in vals) + "]")
    out.append("```")
    return "\n".join(out)


def main():
    rows = load_rows()

    # ===== 图1：旗舰 API blended（log10） =====
    fs = flagship_series(rows)
    order = ["OpenAI", "Anthropic", "Google", "DeepSeek"]
    lines1, legend1, appendix = [], [], []
    for b in order:
        pts = fs[b]
        vals = forward_fill([(ym, blend) for ym, blend, *_ in pts])
        lines1.append((b, [lg(v) for v in vals]))
        last_ym, last_blend, last_in, last_out, last_model = pts[-1]
        first_ym = pts[0][0]
        legend1.append(f"- **{b}**：{first_ym} 起；终值（{last_model}）blended ${last_blend:.2f}/1M"
                       f"（in ${last_in:g} / out ${last_out:g}），log10={lg(last_blend)}")
        for ym, blend, i, o, model in pts:
            appendix.append(f"| {b} | {ym} | {model} | {i:g} | {o:g} | {blend:.2f} |")

    chart1 = xychart("旗舰模型 API 价格（blended, log10 USD per 1M tokens）",
                     "log10($/1M)", -1, 2, lines1)

    # ===== 图2：ChatGPT Plus 折合 per-token 区间（log10） =====
    # 只用「通用聊天旗舰」配额线，排除 o1/o3 等推理模型的周配额（语义不同）
    CHAT_PLUS = {"ChatGPT Plus (GPT-4)", "ChatGPT Plus (GPT-4o)",
                 "ChatGPT Plus (GPT-5 era)", "ChatGPT Plus (2026)"}
    plus = [p for p in sub_series(rows, "ChatGPT Plus") if p[1] in CHAT_PLUS]
    lo_vals = forward_fill([(ym, lo) for ym, _, _, _, lo, _ in plus])
    hi_vals = forward_fill([(ym, hi) for ym, _, _, _, _, hi in plus])
    chart2 = xychart("ChatGPT Plus（$20）折合 per-token 区间（log10 USD per 1M tokens）",
                     "log10($/1M)", -0.5, 2.7,
                     [("min", [lg(v) for v in lo_vals]), ("max", [lg(v) for v in hi_vals])])

    # ===== 套餐折合对照表（所有可解析配额的套餐） =====
    sub_table = []
    for prefix in ("ChatGPT Plus", "ChatGPT Agent", "ChatGPT Go", "Claude Pro", "Cursor"):
        for ym, model, price, cap, lo, hi in sub_series(rows, prefix):
            sub_table.append(f"| {ym} | {model} | ${price:g} | {cap:,.0f} | "
                             f"${lo:.2f} | ${hi:.0f} |")

    # ===== 写 md =====
    md = f"""# AI 价格对比：旗舰 API 与套餐折合 per-token（2023–2026）

把两类价格归一到同一根轴 —— **USD / 1M tokens（blended，输入输出均值）**，取 log10，
便于跨品牌横向、跨时间纵向比较。数据源 `chat/token-price.csv`，本文由 `token-price.py` 生成。

## 折算算法

- **旗舰 API blended**：每家取「通用旗舰」模型链（OpenAI 的 GPT-4→GPT-5.5、Anthropic 的 Opus 线、
  Google 的 Gemini Pro 线、DeepSeek 的 chat 线），blended =（input + output）/ 2，按季度 forward-fill
  （价格在下次变动前保持有效）。DeepSeek input 取 cache-miss。
- **套餐折合 per-token**：套餐不按 token 计费，设 **每条消息 = {TOKENS_PER_MESSAGE} token**（1k 入 + 1k 出）。
  - **最低（地板，重度用户）** = 月价 ÷（把配额用满时的月 token 数）。按 /N 小时 的配额取理论满载（24×7）。
  - **最高（天花板，轻度用户）** = 月价 ÷（轻度基线 **{CASUAL_MSGS_PER_MONTH} 条/月** 的 token 数）。
  - 区间 [最低, 最高] 夹住该套餐相对 API 逐 token 价的位置：榨满时通常比 API 便宜（被补贴），
    轻用时远贵于 API。
- **对数轴**：价格跨约三个数量级（DeepSeek ~$0.2/1M 到 GPT-4 ~$45/1M），故 Y 轴为 log10($/1M)。
  xychart-beta 无图例，线序见每图正文。

## 图1：旗舰模型 API 价格随时间变化

线序（自上而下按图例）：{" / ".join(order)}。

{chart1}

{chr(10).join(legend1)}

## 图2：ChatGPT Plus 折合 per-token 区间

两条线：上 = max（轻度天花板），下 = min（榨满地板）。Plus 月价始终 $20，故天花板恒为
${plus[0][5]:.0f}/1M（轻度用户严重溢价）；地板随配额放宽而下探，榨满时一度低至
${min(lo for *_, lo, _ in plus):.2f}/1M（比同期旗舰 API 更便宜，即套餐补贴）。

{chart2}

## 套餐折合 per-token 对照表

每条消息按 {TOKENS_PER_MESSAGE} token 折算；月配额为理论满载；下限=榨满，上限=轻度（{CASUAL_MSGS_PER_MONTH} 条/月）。

| 生效 | 套餐 | 月价 | 月配额(消息) | 折合下限 $/1M | 折合上限 $/1M |
|---|---|---|---|---|---|
{chr(10).join(sub_table)}

**不可折算的套餐**（配额为「无限」或相对量）：ChatGPT Pro $200、Claude Max 5x/20x（$100/$200）、
Cursor Ultra $200 等标称无限或「N× Pro」，地板随用量趋近于 0、无固定上限，故不入表。
示意：$200 套餐若月推 50M token → $4/1M；月推 200M → $1/1M —— 完全取决于用量。

## 旗舰 API 数据明细（blended 来源）

| 品牌 | 生效 | 模型 | 输入 $/1M | 输出 $/1M | blended $/1M |
|---|---|---|---|---|---|
{chr(10).join(appendix)}

## 假设与局限

- **每条消息 {TOKENS_PER_MESSAGE} token、轻度基线 {CASUAL_MSGS_PER_MONTH} 条/月** 是折算口径，非厂商口径；
  改这两个常数会整体平移套餐曲线，但不改变品牌间相对关系（横向比较稳健）。
- **/N 小时配额按 24×7 满载折算**，是理论地板，真实重度用户达不到；用于界定区间下界。
- 套餐配额取自 CSV `usage_limit`，多为 Reddit 实测的某一时点观察（OpenAI 多次静默改配额），
  非厂商公布的稳定值；详见 CSV 中标 FLAG 的行。
- 旗舰链为「通用旗舰」判断：刻意排除一次性高价款（gpt-4.5-preview $75/$150）与推理专用款
  （o 系列、DeepSeek-R1），以保持各家可比的主力对话模型曲线。
- forward-fill 在模型未更新期间保持上次价格；各家曲线仅在其首个数据点之后有意义
  （季前为 pad 的平线）。
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"写入 {OUT}")
    print(f"旗舰链数据点：" + ", ".join(f"{b}={len(fs[b])}" for b in order))
    print(f"ChatGPT Plus 折算点：{len(plus)}；套餐表行数：{len(sub_table)}")


if __name__ == "__main__":
    main()
