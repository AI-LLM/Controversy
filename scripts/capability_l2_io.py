#!/usr/bin/env python3
"""capability Level-2 的批文件切分与合并（配合两段式 Workflow）。

流程：
  1) split-haiku   ：把 capability_l2_candidates.json 切成 Haiku 输入批（轻字段）
                     -> data/reddit/_cap/haiku_in/b_NNN.json
  2) [Workflow A]  ：每个 Haiku agent 读 b_NNN.json，写裁决到 haiku_out/b_NNN.json
  3) merge-haiku   ：合并 haiku_out/*，选正例（verified_underdog/benchmark_only/refuted），
                     切成 Sonnet 输入批（富字段）-> sonnet_in/s_NNN.json
  4) [Workflow B]  ：每个 Sonnet agent 读 s_NNN.json，写事件到 sonnet_out/s_NNN.json
  5) merge-sonnet  ：合并 sonnet_out/* -> capability_events.csv

每步幂等，可重跑。批数打印到 stderr 供 Workflow 用。
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys

HAIKU_BATCH = 40
SONNET_BATCH = 15
POSITIVE_VERDICTS = {"verified_underdog", "benchmark_only", "refuted"}

HAIKU_LIGHT_FIELDS = [
    "id", "kind", "date", "score", "title", "snippet",
    "sizes_b", "active_params_b", "model_families", "frontier_targets",
]


def _dir(base: str, *parts: str) -> str:
    p = os.path.join(base, "_cap", *parts)
    os.makedirs(p, exist_ok=True)
    return p


def split_haiku(data_dir: str) -> int:
    cands = json.load(open(os.path.join(data_dir, "capability_l2_candidates.json")))
    out = _dir(data_dir, "haiku_in")
    n = 0
    for i in range(0, len(cands), HAIKU_BATCH):
        batch = [{k: c[k] for k in HAIKU_LIGHT_FIELDS} for c in cands[i:i + HAIKU_BATCH]]
        with open(os.path.join(out, f"b_{n:03d}.json"), "w", encoding="utf-8") as fh:
            json.dump(batch, fh, ensure_ascii=False)
        n += 1
    print(f"split-haiku: {len(cands)} 候选 -> {n} 批（{HAIKU_BATCH}/批）写入 {out}", file=sys.stderr)
    print(n)  # stdout：批数供脚本读取
    return n


def merge_haiku(data_dir: str) -> int:
    # 合并裁决
    verdicts: dict[str, dict] = {}
    for path in sorted(glob.glob(os.path.join(_dir(data_dir, "haiku_out"), "*.json"))):
        for v in json.load(open(path)):
            verdicts[v["id"]] = v
    # 回挂到富候选
    cands = json.load(open(os.path.join(data_dir, "capability_l2_candidates.json")))
    by_id = {c["id"]: c for c in cands}
    # 落盘全量裁决（供成文统计 marketing_hype/sentiment_only 等占比）
    with open(os.path.join(data_dir, "capability_verdicts.json"), "w", encoding="utf-8") as fh:
        json.dump(verdicts, fh, ensure_ascii=False)

    positives = [by_id[i] for i, v in verdicts.items()
                 if v.get("verdict") in POSITIVE_VERDICTS and i in by_id]
    # 附上 haiku 裁决，供 Sonnet 校验
    for c in positives:
        c["haiku_verdict"] = verdicts[c["id"]].get("verdict")
        c["haiku_confidence"] = verdicts[c["id"]].get("confidence")
    positives.sort(key=lambda c: -c["score"])

    out = _dir(data_dir, "sonnet_in")
    n = 0
    for i in range(0, len(positives), SONNET_BATCH):
        with open(os.path.join(out, f"s_{n:03d}.json"), "w", encoding="utf-8") as fh:
            json.dump(positives[i:i + SONNET_BATCH], fh, ensure_ascii=False)
        n += 1
    from collections import Counter
    dist = Counter(v.get("verdict") for v in verdicts.values())
    print(f"merge-haiku: {len(verdicts)} 裁决，分布 {dict(dist.most_common())}", file=sys.stderr)
    print(f"  正例 {len(positives)} -> {n} Sonnet 批（{SONNET_BATCH}/批）写入 {out}", file=sys.stderr)
    print(n)
    return n


def merge_sonnet(data_dir: str) -> None:
    rows: list[dict] = []
    for path in sorted(glob.glob(os.path.join(_dir(data_dir, "sonnet_out"), "*.json"))):
        for rec in json.load(open(path)):
            base = {
                "id": rec.get("id", ""),
                "verdict_check": rec.get("verdict_check", ""),
                "haiku_verdict": rec.get("haiku_verdict", ""),
            }
            evs = rec.get("events") or []
            if not evs:
                rows.append({**base, **{k: "" for k in EVENT_FIELDS}})
            for e in evs:
                rows.append({**base, **{k: e.get(k, "") for k in EVENT_FIELDS}})

    # 回挂候选元数据（date/score/permalink/title）
    cands = {c["id"]: c for c in json.load(
        open(os.path.join(data_dir, "capability_l2_candidates.json")))}
    for r in rows:
        c = cands.get(r["id"], {})
        r["date"] = c.get("date", "")
        r["score"] = c.get("score", "")
        r["permalink"] = c.get("permalink", "")
        r["title"] = c.get("title", "")

    rows.sort(key=lambda r: (str(r.get("date") or ""), r["id"]))
    out_csv = os.path.join(data_dir, "capability_events.csv")
    fieldnames = ["date", "id", "haiku_verdict", "verdict_check"] + EVENT_FIELDS + \
                 ["score", "permalink", "title"]
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"merge-sonnet: {len(rows)} 行（事件展开）-> {out_csv}", file=sys.stderr)


EVENT_FIELDS = [
    "small_model", "small_size_b", "active_size_b", "beaten_target", "target_size_b",
    "task_domain", "claim_strength", "evidence_type", "timing", "effective_date",
    "is_marketing", "community_reaction",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["split-haiku", "merge-haiku", "merge-sonnet"])
    ap.add_argument("--data-dir", default="data/reddit")
    args = ap.parse_args()
    if args.stage == "split-haiku":
        split_haiku(args.data_dir)
    elif args.stage == "merge-haiku":
        merge_haiku(args.data_dir)
    else:
        merge_sonnet(args.data_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
