#!/usr/bin/env python3
"""根据 chat/token-price.csv 生成 token-price.md 的对比图（单张，美元线性轴）。

把三类价格放在同一张图、同一根轴（USD per 1M tokens）上比较：

A. 各家旗舰 API blended 价 =（input + output）/ 2。
B. 各家套餐「最高折合 per-token」= 该家最便宜的套餐，按用量上限榨满，折合每 token
   （折扣率低 → 单价高）。
C. 各家套餐「最低折合 per-token」= 该家最贵的套餐，按用量上限榨满，折合每 token
   （批量折扣大 → 单价低）。

套餐折算只看「把配额用满」，不区分轻重用户。套餐不按 token 计费，故设
每条消息 = TOKENS_PER_MESSAGE token。相对配额（如「20x Pro」）= 倍数 × Pro 的 token 配额。
"""
from __future__ import annotations

import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "chat", "token-price.csv")
OUT = os.path.join(HERE, "token-price.md")

TOKENS_PER_MESSAGE = 2000   # 每条消息折合 token（1k 入 + 1k 出，blended）

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
# OpenAI 通用聊天旗舰的 Plus 配额线（排除 o1/o3 推理模型的小周配额）
OPENAI_CHAT_PLUS = ["ChatGPT Plus (GPT-4)", "ChatGPT Plus (GPT-4o)",
                    "ChatGPT Plus (GPT-5 era)", "ChatGPT Plus (2026)"]

QUARTERS = [(y, q) for y in range(2023, 2027) for q in (1, 2, 3, 4)]
QUARTERS = [(y, q) for (y, q) in QUARTERS if not (y == 2026 and q > 2)]
QLABEL = [f"{y % 100}Q{q}" for (y, q) in QUARTERS]
QEND = [f"{y}-{q*3:02d}" for (y, q) in QUARTERS]


def load_rows():
    with open(CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fnum(s):
    s = (s or "").strip()
    return float(s) if s else None


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


CAP_RE = re.compile(
    r"(\d[\d,]*)\s*(?:msgs?|messages?|queries|prompts?|requests?)\s*"
    r"(?:/|per|every|a|each)?\s*(\d*)\s*(hours?|hrs?|h|days?|weeks?|months?)",
    re.IGNORECASE,
)
PER_MONTH = {"day": 30.0, "week": 30.0 / 7, "month": 1.0}


def cap_msgs_per_month(text):
    m = CAP_RE.search(text or "")
    if not m:
        return None
    count = float(m.group(1).replace(",", ""))
    n = float(m.group(2)) if m.group(2) else 1.0
    unit = m.group(3).lower().rstrip("s")
    if unit in ("h", "hour", "hr"):
        return count * (30 * 24) / n           # 每 n 小时：理论满载 24x7
    return count * PER_MONTH[unit] / n


def per_token(price, tokens_per_month):
    return price / tokens_per_month * 1e6        # USD per 1M tokens


def flagship_blended(rows):
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


def main():
    rows = load_rows()
    fs = flagship_blended(rows)
    order = ["OpenAI", "Anthropic", "Google", "DeepSeek"]

    # ---- 套餐折合 per-token ----
    # OpenAI：最便宜可量化套餐 = Plus $20（聊天旗舰配额）；最贵可量化套餐无（Pro $200 无限）
    plus = []
    for r in rows:
        if r["product_or_model"] in OPENAI_CHAT_PLUS:
            p, cap = fnum(r["monthly_price_usd"]), cap_msgs_per_month(r["usage_limit"])
            if p and cap:
                plus.append((r["effective_date"], per_token(p, cap * TOKENS_PER_MESSAGE)))
    plus = sorted(plus)

    # Anthropic：最便宜 = Claude Pro $20（100/8h）；最贵 = Max 20x $200（20× Pro 配额）
    pro_row = next(r for r in rows if r["product_or_model"] == "Claude Pro")
    pro_tokens = cap_msgs_per_month(pro_row["usage_limit"]) * TOKENS_PER_MESSAGE
    pro_price = fnum(pro_row["monthly_price_usd"])
    pro_pt = per_token(pro_price, pro_tokens)                 # Pro 榨满 折合
    anth_plans = []   # (date, name, price, tokens, per_token)
    anth_plans.append((pro_row["effective_date"], "Claude Pro", pro_price, pro_tokens, pro_pt))
    for r in rows:
        m = re.match(r"Claude Max (\d+)x", r["product_or_model"])
        if m:
            mult = int(m.group(1))
            p = fnum(r["monthly_price_usd"])
            tok = mult * pro_tokens
            anth_plans.append((r["effective_date"], r["product_or_model"], p, tok, per_token(p, tok)))
    anth_plans.sort(key=lambda x: (x[0], x[2]))
    max20 = next(x for x in anth_plans if x[1] == "Claude Max 20x")
    # 最高折合（最便宜套餐=Pro）：Pro 全程；最低折合（最贵套餐=Max20x）：Max 上线前同 Pro
    anth_high = forward_fill([(pro_row["effective_date"], pro_pt)])
    anth_low = forward_fill([(pro_row["effective_date"], pro_pt), (max20[0], max20[4])])

    # ---- 组装单张图（线性 USD/1M） ----
    api_lines = {b: forward_fill([(ym, bl) for ym, bl, *_ in fs[b]]) for b in order}
    plus_line = forward_fill(plus)

    series = [
        ("OpenAI API", api_lines["OpenAI"]),
        ("Anthropic API", api_lines["Anthropic"]),
        ("Google API", api_lines["Google"]),
        ("DeepSeek API", api_lines["DeepSeek"]),
        ("OpenAI 套餐 Plus 榨满", plus_line),
        ("Anthropic 套餐最高 (Pro 榨满)", anth_high),
        ("Anthropic 套餐最低 (Max20x 榨满)", anth_low),
    ]
    ymax = max(max(v) for _, v in series)
    ymax = (int(ymax / 5) + 1) * 5    # 取整到 5 的倍数

    chart = ["```mermaid", "xychart-beta",
             '    title "AI 价格对比：旗舰 API 与套餐榨满折合 per-token (USD/1M tokens)"',
             "    x-axis [" + ", ".join(QLABEL) + "]",
             f'    y-axis "USD per 1M tokens" 0 --> {ymax}']
    for _, vals in series:
        chart.append("    line [" + ", ".join(f"{v:.2f}" for v in vals) + "]")
    chart.append("```")
    chart = "\n".join(chart)

    legend = []
    for i, (label, vals) in enumerate(series, 1):
        legend.append(f"{i}. **{label}** — 终值 ${vals[-1]:.2f}/1M")

    # 旗舰明细表
    appendix = []
    for b in order:
        for ym, bl, i, o, model in fs[b]:
            appendix.append(f"| {b} | {ym} | {model} | {i:g} | {o:g} | {bl:.2f} |")

    # 套餐折合表
    sub_tbl = []
    for ym, pt in plus:
        sub_tbl.append(f"| OpenAI | {ym} | ChatGPT Plus | $20 | {pt:.2f} |")
    for ym, name, p, tok, pt in anth_plans:
        sub_tbl.append(f"| Anthropic | {ym} | {name} | ${p:g} | {pt:.2f} |")

    md = f"""# AI 价格对比：旗舰 API 与套餐榨满折合 per-token（2023–2026）

各家旗舰 API 价、各家套餐「最高/最低折合 per-token」全部画在同一张图、同一根轴
（USD per 1M tokens，线性），便于横向（跨品牌）与纵向（跨时间）比较。
数据源 `chat/token-price.csv`，本文由 `token-price.py` 生成。

## 折算口径

- **旗舰 API blended** =（input + output）/ 2，按季度 forward-fill（价格在下次变动前有效）。
  DeepSeek input 取 cache-miss。旗舰链刻意排除一次性高价款（gpt-4.5-preview）与推理专用款（o 系列 / R1）。
- **套餐折合 per-token**：只看「把用量上限榨满」，不区分轻重用户。套餐不按 token 计费，
  故设 **每条消息 = {TOKENS_PER_MESSAGE} token**（1k 入 + 1k 出）。折合 = 月价 ÷（月配额 × 每消息 token）。
  - **最高折合 = 最便宜的套餐榨满**（折扣率低、单价高）。
  - **最低折合 = 最贵的套餐榨满**（批量折扣大、单价低）。
  - 相对配额（如「20x Pro」）= 倍数 × Pro 的 token 配额。/N 小时 配额按理论满载（24×7）折算。

## 对比图

线序（颜色按此顺序）：

{chr(10).join(legend)}

{chart}

## 套餐榨满折合明细

| 品牌 | 生效 | 套餐 | 月价 | 榨满折合 $/1M |
|---|---|---|---|---|
{chr(10).join(sub_tbl)}

Anthropic 关系：Max 5x 折合 = Pro 折合（$100/5x = $20/1x）；Max 20x 折合 = Pro 的一半
（$200/20x = $10/1x），故 20x 是各家可量化套餐里 per-token 最低的。

## 旗舰 API 数据明细（blended 来源）

| 品牌 | 生效 | 模型 | 输入 $/1M | 输出 $/1M | blended $/1M |
|---|---|---|---|---|---|
{chr(10).join(appendix)}

## 假设与局限

- **每条消息 {TOKENS_PER_MESSAGE} token** 是折算口径，非厂商口径；改它会整体平移套餐线，
  但不改品牌间相对关系。
- **可量化套餐有限**：OpenAI 只有 Plus（$20）配额可量化，Pro（$200）标称无限无法榨满，
  故 OpenAI 只有一条套餐线（最高=最低）。Anthropic 借「N× Pro」相对配额得到 Pro→Max20x 的高低区间。
  Google（Advanced/Ultra 无数字配额）、DeepSeek（免费无付费档）、Cursor（按量透传 ≈ API 价）
  无法独立折算，未入图。
- 套餐配额取自 CSV `usage_limit`，多为 Reddit 实测的某一时点观察（OpenAI 多次静默改配额），
  Claude Pro 后期叠加的周限未量化；详见 CSV 中标 FLAG 的行。
- forward-fill 在未更新期间保持上次值；各家线仅在其首个数据点后有意义（季前为 pad 平线）。
- Y 轴线性、单位 USD/1M：早期旗舰 API（GPT-4 / Opus $45）拉高量程，近年低价区（套餐榨满
  $0.5–1.7、DeepSeek API $0.2–2.6）会挤在底部——这本身即结论：套餐榨满的 per-token 远低于
  同期旗舰 API 列表价（即套餐补贴），而 DeepSeek API 又低于所有人。
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"写入 {OUT}")
    print(f"Pro 榨满折合 ${pro_pt:.3f}/1M；Max20x ${max20[4]:.3f}/1M；Plus 区间 "
          f"${min(p for _, p in plus):.3f}–${max(p for _, p in plus):.3f}/1M")
    print(f"图 y 轴上限 {ymax}；线数 {len(series)}")


if __name__ == "__main__":
    main()
