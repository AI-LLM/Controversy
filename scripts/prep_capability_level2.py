#!/usr/bin/env python3
"""为 capability Level-2 LLM 阶段准备富化候选集。

输入：data/reddit/capability_mentions.csv（Level-1 产物）+ 主 jsonl。
输出：data/reddit/capability_l2_candidates.json —— 每个候选含：
  - 轻字段（喂 Haiku 分类）：id, kind, date, score, title, snippet, sizes_b,
    model_families, frontier_targets
  - 富字段（喂 Sonnet 抽取，仅正例用）：body（正文/评论全文，截断）、
    upvote_ratio、num_comments、top_replies（候选帖的高赞回复，社区反应代理）

候选口径（Tier D）：is_crosssize_claim 或（comparison_flag 且有尺寸 且 score>=5）。

做两遍流式扫描主文件（posts + comments），用 link_id 把回复挂到候选帖上。
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict

BODY_CAP = 1600     # Sonnet 用：正文截断
REPLY_CAP = 400     # 单条回复截断
TOP_REPLIES = 5     # 每个候选帖保留的高赞回复数


def select_candidates(csv_path: str, min_score: int) -> dict[str, dict]:
    """从 CSV 选 Tier D 候选，返回 id -> 轻量元数据。"""
    cand: dict[str, dict] = {}
    csv.field_size_limit(10 * 1024 * 1024)
    with open(csv_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                score = int(r["score"] or 0)
            except ValueError:
                score = 0
            has_size = bool(r["sizes_b"] or r["active_params_b"])
            cross = r["is_crosssize_claim"] == "1"
            cmp_size = r["comparison_flag"] == "1" and has_size and score >= min_score
            if not (cross or cmp_size):
                continue
            # 从 permalink 反解 id：posts .../comments/<id>/slug/；comments 末尾 /#<id>
            pl = r["permalink"]
            is_comment = "/#" in pl
            if is_comment:
                rid = pl.rsplit("/#", 1)[-1]
                kind = "comment"
            else:
                m = re.search(r"/comments/([a-z0-9]+)/", pl)
                rid = m.group(1) if m else ""
                kind = "post"
            if not rid:
                continue
            cand[rid] = {
                "id": rid, "kind": kind, "date": r["date"], "score": score,
                "title": r["title"], "snippet": r["snippet"],
                "sizes_b": r["sizes_b"], "active_params_b": r["active_params_b"],
                "model_families": r["model_families"],
                "frontier_targets": r["frontier_targets"],
                "is_crosssize": cross, "permalink": pl,
                "body": "", "upvote_ratio": "", "num_comments": "",
                "top_replies": [],
            }
    return cand


def enrich(cand: dict[str, dict], posts_path: str, comments_path: str) -> None:
    post_ids = {rid for rid, c in cand.items() if c["kind"] == "post"}
    comment_ids = {rid for rid, c in cand.items() if c["kind"] == "comment"}

    # 第一遍：posts —— 补候选帖正文/upvote_ratio
    if os.path.exists(posts_path):
        with open(posts_path, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rid = d.get("id")
                if rid in post_ids:
                    c = cand[rid]
                    body = (d.get("selftext") or "")
                    if body in ("[deleted]", "[removed]"):
                        body = ""
                    c["body"] = re.sub(r"\s+", " ", body).strip()[:BODY_CAP]
                    c["upvote_ratio"] = d.get("upvote_ratio", "")
                    c["num_comments"] = d.get("num_comments", "")

    # 第二遍：comments —— 候选评论全文 + 候选帖的高赞回复（link_id join）
    reply_heap: dict[str, list] = defaultdict(list)
    if os.path.exists(comments_path):
        with open(comments_path, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cid = d.get("id")
                body = d.get("body") or ""
                if body in ("[deleted]", "[removed]"):
                    body = ""
                if cid in comment_ids:
                    cand[cid]["body"] = re.sub(r"\s+", " ", body).strip()[:BODY_CAP]
                # 回复 join：link_id = t3_<postid>
                link = d.get("link_id") or ""
                if link.startswith("t3_"):
                    pid = link[3:]
                    if pid in post_ids and body:
                        try:
                            sc = int(d.get("score") or 0)
                        except (TypeError, ValueError):
                            sc = 0
                        reply_heap[pid].append((sc, re.sub(r"\s+", " ", body).strip()[:REPLY_CAP]))

    for pid, replies in reply_heap.items():
        replies.sort(key=lambda x: x[0], reverse=True)
        cand[pid]["top_replies"] = [{"score": s, "body": b} for s, b in replies[:TOP_REPLIES]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/reddit")
    ap.add_argument("--min-score", type=int, default=5)
    ap.add_argument("--channel", default="LocalLLaMA")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    csv_path = os.path.join(args.data_dir, "capability_mentions.csv")
    posts_path = os.path.join(args.data_dir, f"r_{args.channel}_posts.jsonl")
    comments_path = os.path.join(args.data_dir, f"r_{args.channel}_comments.jsonl")
    out_path = args.out or os.path.join(args.data_dir, "capability_l2_candidates.json")

    cand = select_candidates(csv_path, args.min_score)
    print(f"Tier D 候选: {len(cand)}  "
          f"(帖 {sum(1 for c in cand.values() if c['kind']=='post')}, "
          f"评论 {sum(1 for c in cand.values() if c['kind']=='comment')})", file=sys.stderr)

    print("富化中（join 回复 + 补正文）...", file=sys.stderr)
    enrich(cand, posts_path, comments_path)

    items = sorted(cand.values(), key=lambda c: (c["date"], -c["score"]))
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(items, fh, ensure_ascii=False)
    n_replies = sum(len(c["top_replies"]) for c in items)
    print(f"写入 {out_path}：{len(items)} 候选，挂上 {n_replies} 条回复", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
