#!/usr/bin/env python3
"""根据 chat/token-price.csv 生成 token-price.md。

旗舰 = 同一厂家在同一时段 API 目录里最贵的模型（含推理模型），
而非钉死某个产品线。模型退市后自动让位次高价。

套餐折算假设用户全用这个最贵的模型（因为套餐内模型不加价），
最高折合 = 最便宜套餐榨满配额，最低折合 = 最贵套餐榨满配额。
全部画在一张图上比较。
"""
from __future__ import annotations

import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "chat", "token-price.csv")
OUT = os.path.join(HERE, "token-price.md")

TOKENS_PER_MESSAGE = 2000

# 排除非文本模型（音频、embeddings、off-peak 机制行等）
EXCLUDE = {"OpenAI audio models", "text-embedding-ada-002", "Off-peak discount"}

# 模型退市时间（YYYY-MM），之后不再计入「当期最贵」
DEPRECATED = {
    # OpenAI
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
    "gpt-4.5-preview":          "2025-04",
    "o1-preview":               "2025-02",
    "o1-mini":                  "2025-06",
    # Anthropic
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
    # Google
    "PaLM 2 text-bison":        "2024-04",
    "Gemini 1.0 Pro":           "2025-02",
    "Gemini 1.5 Flash (<=128K)":"2025-06",
    "Gemini 1.5 Flash (<=128K cut)":"2025-06",
    "Gemini 1.5 Flash-8B (<=128K)":"2025-06",
    "Gemini 2.0 Flash":         "2026-06",
    "Gemini 2.0 Flash-Lite":    "2026-06",
    # Google (price-cut supersedes original row)
    "Gemini 1.5 Pro (<=128K)":  "2024-10",   # superseded by <=128K cut
    # DeepSeek
    "DeepSeek-V3 (promo)":      "2025-02",
    "DeepSeek-V2 (deepseek-chat)":"2024-12",
    "deepseek-chat V2 + context caching":"2024-12",
    "DeepSeek-V3 (standard)":   "2025-09",
    "DeepSeek-V3.1 (unified)":  "2025-09",
    "DeepSeek-V4 Pro (promo 75% off)":"2026-06",
}

QUARTERS = [(y, q) for y in range(2023, 2027) for q in (1, 2, 3, 4)
            if not (y == 2026 and q > 2)]
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


# ---- 核心：每季度每家取 API 目录里在售的最贵模型 ----

def max_envelope(rows, providers):
    """返回 {brand: (quarterly_vals, quarterly_models)}"""
    # 先收集每家所有 API 模型
    models = {b: [] for b in providers}     # (ym, blended, in, out, name)
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
            # 遍历所有已发布且未退市的模型，取最贵
            for ym, bl, inp, out, name in models[b]:
                if ym > qe:
                    continue           # 还没发布
                dep = DEPRECATED.get(name)
                if dep and dep <= qe:
                    continue           # 已退市
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


def main():
    rows = load_rows()
    order = ["OpenAI", "Anthropic", "Google", "DeepSeek"]
    env = max_envelope(rows, order)

    # ---- 套餐折合 ----
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

    # ---- 单张图 ----
    series = [
        ("OpenAI API 最贵", env["OpenAI"][0]),
        ("Anthropic API 最贵", env["Anthropic"][0]),
        ("Google API 最贵", env["Google"][0]),
        ("DeepSeek API 最贵", env["DeepSeek"][0]),
        ("OpenAI Plus 榨满", plus_line),
        ("Anthropic Pro 榨满(最高)", anth_high),
        ("Anthropic Max20x 榨满(最低)", anth_low),
    ]
    ymax = max(max(v) for _, v in series)
    ymax = (int(ymax / 5) + 1) * 5

    chart = ["```mermaid", "xychart-beta",
             '    title "各品牌最贵 API 价 + 套餐榨满折合 (USD/1M tokens)"',
             "    x-axis [" + ", ".join(QLABEL) + "]",
             f'    y-axis "USD per 1M tokens" 0 --> {ymax}']
    for _, vals in series:
        chart.append("    line [" + ", ".join(f"{v:.1f}" for v in vals) + "]")
    chart.append("```")
    chart_str = "\n".join(chart)

    legend = []
    for i, (label, vals) in enumerate(series, 1):
        legend.append(f"{i}. **{label}** — 终值 ${vals[-1]:.1f}/1M")

    # ---- 旗舰明细：每季度最贵的是谁 ----
    flagship_tbl = []
    for b in order:
        vals, names = env[b]
        prev = ""
        for ql, v, nm in zip(QLABEL, vals, names):
            if nm != prev:
                flagship_tbl.append(f"| {b} | {ql} | {nm} | {v:.2f} |")
                prev = nm

    # ---- 套餐折合表 ----
    sub_tbl = []
    for ym, pt in sorted(plus):
        sub_tbl.append(f"| OpenAI | {ym} | ChatGPT Plus | $20 | {pt:.2f} |")
    for ym, name, p, tok, pt in anth_plans:
        sub_tbl.append(f"| Anthropic | {ym} | {name} | ${p:g} | {pt:.2f} |")

    md = f"""# 各品牌最贵 API 价格 + 套餐榨满折合 per-token（2023–2026）

**旗舰 = 同一厂家在同一时段 API 目录里最贵的文本模型**（含推理模型），
而不是钉死某个产品线。模型退市后自动让位给次高价。
这样看到的是**各品牌能卖出的天花板价**随时间的变化。

套餐折算假设用户全用这个最贵的模型（因为套餐内用哪个模型不影响价格）。
全部画在一张图上比较。数据源 `chat/token-price.csv`，本文由 `token-price.py` 生成。

## 折算口径

- **API 最贵模型** blended =（input + output）/ 2，每季度取目录中**在售且最贵**的那个。
  模型退市（DEPRECATED 表）后自动让位给次高价。排除音频 / embedding 等非文本模型。
- **套餐折合 per-token**：只看「把配额用满」。每条消息 = {TOKENS_PER_MESSAGE} token。
  - **最高折合（最便宜套餐榨满）**：折扣率低、单价高。
  - **最低折合（最贵套餐榨满）**：批量折扣大、单价低。
  - 相对配额「N× Pro」= 倍数 × Pro token 配额。/N 小时按 24×7 满载。

## 对比图

线序（颜色按此顺序）：

{chr(10).join(legend)}

{chart_str}

## 各季度最贵模型是谁（变更点）

| 品牌 | 季度 | 当期最贵模型 | blended $/1M |
|---|---|---|---|
{chr(10).join(flagship_tbl)}

## 套餐榨满折合明细

| 品牌 | 生效 | 套餐 | 月价 | 榨满折合 $/1M |
|---|---|---|---|---|
{chr(10).join(sub_tbl)}

## 假设与局限

- **每条消息 {TOKENS_PER_MESSAGE} token** 是折算口径；改它会整体平移套餐线但不改品牌间相对关系。
- **模型退市时间**来自 CSV notes + 官方公告，部分为近似（±1 月）。退市判断影响「某季度谁最贵」的答案，
  但跨品牌相对高低不受单条退市日期影响。
- **可量化套餐有限**：OpenAI 只有 Plus $20 可量化（Pro $200 标称无限，无配额可榨满）；
  Anthropic 借「N× Pro」得到 Pro→Max20x 区间。Google（无数字配额）、DeepSeek（免费无付费档）、
  Cursor（按量透传 ≈ API 价）无法折算，未入图。
- 套餐配额取自 CSV `usage_limit`，多为 Reddit 实测某时点观察（OpenAI 多次静默改配额）；
  Claude Pro 后期叠加的周限未量化。
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"写入 {OUT}")
    for b in order:
        vals, names = env[b]
        print(f"  {b:10s} 最贵演进：", end="")
        prev = ""
        for ql, v, nm in zip(QLABEL, vals, names):
            if nm != prev:
                print(f" [{ql}]{nm}=${v:.1f}", end="")
                prev = nm
        print()
    print(f"y 轴上限 {ymax}；线数 {len(series)}")


if __name__ == "__main__":
    main()
