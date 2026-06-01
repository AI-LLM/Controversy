#!/usr/bin/env python3
"""分析 arctic-shift 下载的 Reddit 频道数据，抽取价格相关帖子。

数据来源：https://arctic-shift.photon-reddit.com/download-tool 导出的
submission JSONL（每行一个帖子，PushShift/arctic-shift schema）。

两种模式：

  默认（price）：抽取价格信号（美元金额 / token 费率 / 用量上限）。
    python3 scripts/analyze_reddit_prices.py                # 扫 data/reddit/*.jsonl
    python3 scripts/analyze_reddit_prices.py --min-score 5  # 只要 5 赞以上
    python3 scripts/analyze_reddit_prices.py --since 2024-01 --until 2024-12

  退市（deprecation）：抽取模型退市/下架事件。
    python3 scripts/analyze_reddit_prices.py --mode deprecation
    python3 scripts/analyze_reddit_prices.py --mode deprecation --min-score 3

输出 data/reddit/price_mentions.csv 或 deprecation_events.csv。
再下载更多频道（放进 data/reddit/）后直接重跑即可，无需改代码。
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 价格信号正则。分类抽取，方便事后按 signal_type 过滤。
# ---------------------------------------------------------------------------

# token 逐价：$3 / 1M tokens、3 per million tokens、$0.15/MTok、per 1k tokens
# 简化以避免回溯爆炸；只对正文含 "tok" 的帖运行（见 analyze_post 预过滤）。
RE_TOKEN_RATE = re.compile(
    r"\$?\d[\d.]*\s*(?:/|per|a)?\s*"
    r"(?:1\s?[MmKk]|million|thousand|mil)\s*"
    r"(?:input|output|cached|in|out)?\s*tok"
    r"|\$?\d[\d.]*\s*/\s*M?Tok\b"
    r"|per\s+(?:1\s?[MmKk]|million)\s+tok",
    re.IGNORECASE,
)

# 订阅价：$20/mo、$20 per month、$200 a month、$100/year、$17 monthly、$8/month
RE_SUB_PRICE = re.compile(
    r"\$\s?\d[\d,]*\.?\d*\s*"
    r"(?:/|per|a|each)?\s*"
    r"(?:mo|month|months|monthly|/mo|yr|year|years|annually|annual|seat|user|week)\b",
    re.IGNORECASE,
)

# 用量上限：25 messages every 3 hours、50 msgs/3h、300 requests per month、10 prompts a day
RE_USAGE_LIMIT = re.compile(
    r"\d[\d,]*\s*"
    r"(?:messages?|msgs?|prompts?|requests?|queries|completions?|generations?|calls?)\s*"
    r"(?:per|/|every|a|each|in)\s*"
    r"\d*\s*"
    r"(?:hour|hours|hr|hrs|h|day|days|week|weeks|month|months|min|minutes?)\b",
    re.IGNORECASE,
)

# premium request 配额（GitHub Copilot 2025 计费模型）
RE_PREMIUM_REQ = re.compile(r"\d*\s*premium\s+requests?", re.IGNORECASE)

# 裸美元金额（兜底，置信度低，需正文有定价语境词才计入）
RE_BARE_DOLLAR = re.compile(r"\$\s?\d[\d,]*\.?\d*")

# 定价语境词（裸美元命中时要求出现，过滤掉 "$5 worth of compute" 之类噪声）
RE_PRICE_CONTEXT = re.compile(
    r"\b(pric|cost|subscri|plan|tier|billing|charge|paid|pay|"
    r"per token|/mo|/month|per month|premium request|rate limit|"
    r"message limit|quota|cap|overage|refund|invoice|upgrade|downgrade)\w*",
    re.IGNORECASE,
)

# 产品 / 模型识别，便于归类到 token-price.csv 的 provider
PRODUCT_PATTERNS = [
    ("ChatGPT/GPT", re.compile(r"\b(chatgpt|gpt-?[0-9o]|gpt 4|davinci|o[134]-?(mini|pro|preview)?)\b", re.IGNORECASE)),
    ("Claude", re.compile(r"\b(claude|anthropic|opus|sonnet|haiku)\b", re.IGNORECASE)),
    ("Gemini", re.compile(r"\b(gemini|bard|palm|google ai|aistudio|vertex)\b", re.IGNORECASE)),
    ("Copilot", re.compile(r"\b(copilot)\b", re.IGNORECASE)),
    ("Cursor", re.compile(r"\b(cursor)\b", re.IGNORECASE)),
    ("Codex", re.compile(r"\bcodex\b", re.IGNORECASE)),
    ("DeepSeek", re.compile(r"\bdeepseek\b", re.IGNORECASE)),
    ("API-generic", re.compile(r"\bapi\b", re.IGNORECASE)),
]

MAX_TEXT = 6000   # 截断超长 selftext，控制开销
MAX_SNIPPET = 240  # 输出片段长度
MAX_MATCHES = 6    # 每类最多记几个抽取值

# ---------------------------------------------------------------------------
# 退市/下架事件检测（--mode deprecation）
# ---------------------------------------------------------------------------

RE_DEPRECATION = re.compile(
    r"\b(deprecat\w*|sunset\w*|retired|retiring|"
    r"end[- ]of[- ]life|eol|removed?\b|removing|"
    r"no longer available|discontinued|shut\w* down|"
    r"replaced by|superseded|phase[d ]? out|"
    r"will be removed|being removed|"
    r"legacy|shutdown|sundown)\b",
    re.IGNORECASE,
)

# 模型名正则（抽取退市的是哪个模型）
MODEL_PATTERNS = [
    # OpenAI
    re.compile(r"\bgpt-?4\.?5[- ]?preview\b", re.IGNORECASE),
    re.compile(r"\bgpt-?4-?32k\b", re.IGNORECASE),
    re.compile(r"\bgpt-?4[- ]?turbo\b", re.IGNORECASE),
    re.compile(r"\bgpt-?4o?(?:-(?:mini|2024\S+))?\b", re.IGNORECASE),
    re.compile(r"\bgpt-?4\.1(?:-(?:mini|nano))?\b", re.IGNORECASE),
    re.compile(r"\bgpt-?3\.?5[- ]?turbo\w*\b", re.IGNORECASE),
    re.compile(r"\bgpt-?5(?:\.[\d]+)?(?:-(?:mini|nano|pro))?\b", re.IGNORECASE),
    re.compile(r"\bo[134]-?(?:mini|pro|preview)?\b", re.IGNORECASE),
    re.compile(r"\bdavinci\b", re.IGNORECASE),
    re.compile(r"\btext-davinci-\d+\b", re.IGNORECASE),
    re.compile(r"\bcode-davinci\b", re.IGNORECASE),
    # Anthropic
    re.compile(r"\bclaude[- ]?(?:instant|[234]\S*|opus|sonnet|haiku)\b", re.IGNORECASE),
    # Google
    re.compile(r"\bgemini[- ]?(?:\d\S*|pro|flash|ultra|nano)\b", re.IGNORECASE),
    re.compile(r"\bpalm[- ]?2?\b", re.IGNORECASE),
    re.compile(r"\bbard\b", re.IGNORECASE),
    # DeepSeek
    re.compile(r"\bdeepseek[- ]?(?:v\d\S*|r\d\S*|coder|chat)\b", re.IGNORECASE),
]


def extract_models(text: str) -> list[str]:
    seen = []
    for pat in MODEL_PATTERNS:
        for m in pat.finditer(text):
            s = m.group(0).strip()
            norm = s.lower().replace(" ", "-")
            if norm not in [x.lower().replace(" ", "-") for x in seen]:
                seen.append(s)
    return seen[:8]


def analyze_deprecation(d: dict) -> dict | None:
    title = d.get("title") or ""
    selftext = d.get("selftext") or ""
    if selftext in ("[deleted]", "[removed]"):
        selftext = ""
    text = (title + "\n" + selftext)[:MAX_TEXT]
    if not text.strip():
        return None

    dep_matches = find_all(RE_DEPRECATION, text, limit=4)
    if not dep_matches:
        return None

    models = extract_models(text)
    products = detect_products(text)
    if not models and not products:
        return None

    ts = d.get("created_utc")
    try:
        date = datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        date = ""

    permalink = d.get("permalink") or ""
    if permalink and not permalink.startswith("http"):
        permalink = "https://reddit.com" + permalink

    dep_kw = dep_matches[0].lower() if dep_matches else ""
    snippet = make_snippet(text, dep_kw)

    # 子分类：是宣布退市、讨论退市影响、还是担心即将退市
    event_type = "deprecation"
    low = text.lower()
    if any(w in low for w in ("will be", "going to", "plan to", "rumor", "might")):
        event_type = "upcoming"
    elif any(w in low for w in ("replaced by", "superseded", "upgrade to", "migrate")):
        event_type = "replacement"

    return {
        "date": date,
        "subreddit": d.get("subreddit") or "",
        "event_type": event_type,
        "deprecation_keywords": " | ".join(dep_matches),
        "models_mentioned": " | ".join(models),
        "products": "|".join(products),
        "score": d.get("score", ""),
        "num_comments": d.get("num_comments", ""),
        "title": re.sub(r"\s+", " ", title).strip()[:200],
        "permalink": permalink,
        "snippet": snippet,
    }


def find_all(pat: re.Pattern, text: str, limit: int = MAX_MATCHES) -> list[str]:
    seen: list[str] = []
    for m in pat.finditer(text):
        s = re.sub(r"\s+", " ", m.group(0)).strip()
        if s not in seen:
            seen.append(s)
        if len(seen) >= limit:
            break
    return seen


def detect_products(text: str) -> list[str]:
    return [name for name, pat in PRODUCT_PATTERNS if pat.search(text)]


def make_snippet(text: str, anchor: str) -> str:
    """取第一个价格信号附近的一段文字做预览。"""
    idx = text.lower().find(anchor.lower()) if anchor else -1
    if idx < 0:
        idx = 0
    start = max(0, idx - 60)
    snip = text[start:start + MAX_SNIPPET]
    return re.sub(r"\s+", " ", snip).strip()


def analyze_post(d: dict) -> dict | None:
    title = d.get("title") or ""
    selftext = d.get("selftext") or ""
    if selftext in ("[deleted]", "[removed]"):
        selftext = ""
    text = (title + "\n" + selftext)[:MAX_TEXT]
    if not text.strip():
        return None

    # 廉价预过滤：先做小写子串判断，只对可能命中的帖跑（昂贵的）正则，
    # 避免在 15 万帖上无差别回溯。
    low = text.lower()
    has_dollar = "$" in text
    has_tok = "tok" in low
    has_limit_cue = any(c in low for c in (
        "message", "msg", "request", "prompt", "quer", "completion", "generation"))

    token_rates = find_all(RE_TOKEN_RATE, text) if has_tok else []
    sub_prices = find_all(RE_SUB_PRICE, text) if has_dollar else []
    usage_limits = find_all(RE_USAGE_LIMIT, text) if has_limit_cue else []
    premium = find_all(RE_PREMIUM_REQ, text) if "premium" in low else []

    signal_types: list[str] = []
    if token_rates:
        signal_types.append("token_rate")
    if sub_prices:
        signal_types.append("sub_price")
    if usage_limits:
        signal_types.append("usage_limit")
    if premium:
        signal_types.append("premium_request")

    # 兜底：裸美元 + 定价语境词
    bare = []
    if not signal_types and has_dollar:
        bare = find_all(RE_BARE_DOLLAR, text)
        if bare and RE_PRICE_CONTEXT.search(text):
            signal_types.append("bare_dollar")

    if not signal_types:   # 既无结构化信号、也无（带语境的）裸美元 -> 丢弃
        return None

    # 置信度：有结构化信号=high；只有裸美元=low
    confidence = "low" if signal_types == ["bare_dollar"] else "high"

    ts = d.get("created_utc")
    try:
        date = datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        date = ""

    anchor = (token_rates + sub_prices + premium + usage_limits + bare or [""])[0]
    permalink = d.get("permalink") or ""
    if permalink and not permalink.startswith("http"):
        permalink = "https://reddit.com" + permalink

    return {
        "date": date,
        "subreddit": d.get("subreddit") or "",
        "signal_types": "|".join(signal_types),
        "confidence": confidence,
        "products": "|".join(detect_products(text)),
        "dollar_amounts": " ; ".join(sub_prices + bare),
        "token_rates": " ; ".join(token_rates),
        "usage_limits": " ; ".join(usage_limits),
        "premium_requests": " ; ".join(premium),
        "score": d.get("score", ""),
        "num_comments": d.get("num_comments", ""),
        "title": re.sub(r"\s+", " ", title).strip()[:200],
        "permalink": permalink,
        "snippet": make_snippet(text, anchor),
    }


def parse_ym(s: str | None) -> str | None:
    """把 --since/--until 的 YYYY-MM 或 YYYY-MM-DD 规整成可比较的 YYYY-MM-DD。"""
    if not s:
        return None
    parts = s.split("-")
    if len(parts) == 2:
        return f"{parts[0]}-{parts[1]}-01" if s == "since" else s + "-01"
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description="抽取 Reddit 频道数据里的价格或退市信息")
    ap.add_argument("--mode", choices=["price", "deprecation"], default="price",
                    help="price=价格信号（默认）；deprecation=模型退市/下架事件")
    ap.add_argument("--data-dir", default="data/reddit", help="JSONL 所在目录")
    ap.add_argument("--out", default=None, help="输出 CSV 路径（默认按 mode 自动选）")
    ap.add_argument("--min-score", type=int, default=0, help="最低赞数")
    ap.add_argument("--since", default=None, help="起始日期 YYYY-MM 或 YYYY-MM-DD")
    ap.add_argument("--until", default=None, help="截止日期 YYYY-MM 或 YYYY-MM-DD")
    ap.add_argument("--keyword", default=None, help="标题/正文须含该关键词（不分大小写）")
    ap.add_argument("--high-only", action="store_true", help="（仅 price 模式）只保留 high 置信度")
    args = ap.parse_args()

    if args.out is None:
        args.out = os.path.join(args.data_dir,
                                "deprecation_events.csv" if args.mode == "deprecation"
                                else "price_mentions.csv")

    files = sorted(glob.glob(os.path.join(args.data_dir, "*.jsonl")))
    if not files:
        print(f"[!] {args.data_dir} 下没有 .jsonl 文件", file=sys.stderr)
        return 1

    since = (args.since + "-01") if (args.since and len(args.since) == 7) else args.since
    until = (args.until + "-31") if (args.until and len(args.until) == 7) else args.until
    kw = args.keyword.lower() if args.keyword else None

    analyze_fn = analyze_deprecation if args.mode == "deprecation" else analyze_post

    scanned = 0
    rows: list[dict] = []
    by_subreddit = Counter()
    by_signal = Counter()
    by_month = Counter()

    for path in files:
        fname = os.path.basename(path)
        file_hits = 0
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                scanned += 1
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rec = analyze_fn(d)
                if rec is None:
                    continue
                if args.min_score and (int(rec["score"] or 0) < args.min_score):
                    continue
                if since and rec["date"] and rec["date"] < since:
                    continue
                if until and rec["date"] and rec["date"] > until:
                    continue
                if args.mode == "price" and args.high_only and rec.get("confidence") != "high":
                    continue
                if kw and kw not in (rec["title"] + rec.get("snippet", "")).lower():
                    continue
                rows.append(rec)
                file_hits += 1
                by_subreddit[rec["subreddit"]] += 1
                if args.mode == "price":
                    for s in rec["signal_types"].split("|"):
                        by_signal[s] += 1
                else:
                    by_signal[rec.get("event_type", "")] += 1
                if rec["date"]:
                    by_month[rec["date"][:7]] += 1
        print(f"  {fname:42s} -> {file_hits:6d} hits", file=sys.stderr)

    rows.sort(key=lambda r: (r["date"], r["subreddit"]))

    if args.mode == "deprecation":
        fieldnames = [
            "date", "subreddit", "event_type", "deprecation_keywords",
            "models_mentioned", "products", "score", "num_comments",
            "title", "permalink", "snippet",
        ]
    else:
        fieldnames = [
            "date", "subreddit", "signal_types", "confidence", "products",
            "dollar_amounts", "token_rates", "usage_limits", "premium_requests",
            "score", "num_comments", "title", "permalink", "snippet",
        ]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # ---- 终端摘要 ----
    print("\n" + "=" * 60, file=sys.stderr)
    print(f"[{args.mode}] 扫描: {scanned:,}   命中: {len(rows):,}   写入: {args.out}", file=sys.stderr)
    print("\n按类型:", file=sys.stderr)
    for k, v in by_signal.most_common():
        print(f"  {k:18s} {v:6d}", file=sys.stderr)
    print("\n按频道:", file=sys.stderr)
    for k, v in by_subreddit.most_common():
        print(f"  r/{k:24s} {v:6d}", file=sys.stderr)
    print("\n命中最多的月份 (Top 12):", file=sys.stderr)
    for k, v in sorted(by_month.items(), key=lambda x: -x[1])[:12]:
        print(f"  {k}  {v:5d}", file=sys.stderr)
    print(f"\n高赞帖 (Top 20 by score):", file=sys.stderr)
    for r in sorted(rows, key=lambda r: -int(r["score"] or 0))[:20]:
        extra = r.get("models_mentioned", r.get("signal_types", ""))[:24]
        print(f"  [{r['date']}] {r['score']:>5} r/{r['subreddit']:14s} "
              f"{extra:24s} {r['title'][:52]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
