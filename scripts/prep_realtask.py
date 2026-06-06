#!/usr/bin/env python3
"""为"小模型完成真实任务"搜索准备富化候选集。

与越级（capability Level-2）不同：这里找的是**用户报告用小模型把真实任务/活儿干成**
的帖子，不要求有跨模型对比。

候选口径（Tier B）：有小模型尺寸（≤34B 档）+ score>=5 + 真实使用/任务信号——
  强信号：第一人称"造了东西/替代了云/生产用"（build/replace/production）；
  或 "用 X 来做 Y" + 应用类名词（agent/app/bot/rag/pipeline…）。

复用 prep_capability_level2.enrich 做回复 join + 正文补全。
输出 data/reddit/realtask_candidates.json。
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

from prep_capability_level2 import enrich  # 复用富化逻辑

SMALL = {"<1B", "1-3B", "4-6B", "7-9B", "11-15B", "20-34B"}

BUILD = re.compile(r"\b(i|we)\b.{0,30}\b(built|build|made|made it|created|wrote|developed|deployed|shipped|fine[- ]?tun\w*|trained)\b", re.I)
REPL = re.compile(r"\breplac\w+|switch\w+ (from|to)|cancel\w+ (my|the).{0,20}(subscri|chatgpt|claude|api)|no longer (need|pay|use)|ditch\w+|instead of (gpt|chatgpt|claude|the api|openai|cloud)", re.I)
PROD = re.compile(r"\b(in production|production[- ]ready|daily driver|use ?case|powering|powers? my|runs? my|for (my |our )?(business|company|clients?|customers?|job|work))\b", re.I)
APP = re.compile(r"\b(agent|app|bot|chatbot|assistant|pipeline|rag|tool|workflow|automation|integrat\w+)\b", re.I)
USE = re.compile(r"\b(i|we|my)\b.{0,30}\b(use|using|used|run|running)\b.{0,30}\b(for|to)\b", re.I)


def select(csv_path: str, min_score: int) -> dict[str, dict]:
    cand: dict[str, dict] = {}
    csv.field_size_limit(10 * 1024 * 1024)
    for r in csv.DictReader(open(csv_path, encoding="utf-8")):
        bks = set(b for b in r["size_buckets"].split("|") if b)
        if not (bks & SMALL):
            continue
        try:
            sc = int(r["score"] or 0)
        except ValueError:
            sc = 0
        if sc < min_score:
            continue
        t = r["title"] + " " + r["snippet"]
        strong = BUILD.search(t) or REPL.search(t) or PROD.search(t)
        if not (strong or (USE.search(t) and APP.search(t))):
            continue
        pl = r["permalink"]
        if "/#" in pl:
            rid = pl.rsplit("/#", 1)[-1]
            kind = "comment"
        else:
            m = re.search(r"/comments/([a-z0-9]+)/", pl)
            rid = m.group(1) if m else ""
            kind = "post"
        if not rid:
            continue
        cand[rid] = {
            "id": rid, "kind": kind, "date": r["date"], "score": sc,
            "title": r["title"], "snippet": r["snippet"],
            "sizes_b": r["sizes_b"], "active_params_b": r["active_params_b"],
            "model_families": r["model_families"], "hardware": r["hardware"],
            "size_buckets": r["size_buckets"], "permalink": pl,
            "body": "", "upvote_ratio": "", "num_comments": "", "top_replies": [],
        }
    return cand


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/reddit")
    ap.add_argument("--min-score", type=int, default=5)
    ap.add_argument("--channel", default="LocalLLaMA")
    args = ap.parse_args()

    csv_path = os.path.join(args.data_dir, "capability_mentions.csv")
    posts = os.path.join(args.data_dir, f"r_{args.channel}_posts.jsonl")
    comments = os.path.join(args.data_dir, f"r_{args.channel}_comments.jsonl")
    out = os.path.join(args.data_dir, "realtask_candidates.json")

    cand = select(csv_path, args.min_score)
    print(f"真实任务候选: {len(cand)} "
          f"(帖 {sum(1 for c in cand.values() if c['kind']=='post')}, "
          f"评论 {sum(1 for c in cand.values() if c['kind']=='comment')})", file=sys.stderr)
    print("富化中（join 回复 + 补正文）...", file=sys.stderr)
    enrich(cand, posts, comments)

    items = sorted(cand.values(), key=lambda c: (c["date"], -c["score"]))
    json.dump(items, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"写入 {out}：{len(items)} 候选，挂 {sum(len(c['top_replies']) for c in items)} 条回复", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
