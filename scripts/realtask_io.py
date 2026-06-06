#!/usr/bin/env python3
"""realtask（小模型完成真实任务）两段式 Workflow 的批切分与合并。

  split-haiku  : realtask_candidates.json -> _rt/haiku_in/b_NNN.json（轻字段，40/批）
  [Workflow A] : Haiku 读批写裁决到 _rt/haiku_out/b_NNN.json
  merge-haiku  : 合并裁决，选正例(非 not_task) -> _rt/sonnet_in/s_NNN.json（富字段，15/批）
  [Workflow B] : Sonnet 读批写事件到 _rt/sonnet_out/s_NNN.json
  merge-sonnet : 合并 -> realtask_events.csv
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
from collections import Counter

HAIKU_BATCH = 40
SONNET_BATCH = 15
POSITIVE = {"task_done", "task_partial", "task_failed"}

HAIKU_LIGHT = ["id", "kind", "date", "score", "title", "snippet",
               "sizes_b", "active_params_b", "model_families", "hardware"]

EVENT_FIELDS = ["model", "size_b", "active_size_b", "task", "task_domain",
                "outcome", "replaced_cloud", "replaced_what", "hardware",
                "is_self_built", "community_reaction"]


def _dir(base, *p):
    d = os.path.join(base, "_rt", *p)
    os.makedirs(d, exist_ok=True)
    return d


def split_haiku(dd):
    cands = json.load(open(os.path.join(dd, "realtask_candidates.json")))
    out = _dir(dd, "haiku_in")
    n = 0
    for i in range(0, len(cands), HAIKU_BATCH):
        batch = [{k: c[k] for k in HAIKU_LIGHT} for c in cands[i:i + HAIKU_BATCH]]
        json.dump(batch, open(os.path.join(out, f"b_{n:03d}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        n += 1
    print(f"split-haiku: {len(cands)} -> {n} 批 ({HAIKU_BATCH}/批)", file=sys.stderr)
    print(n)


def merge_haiku(dd):
    verdicts = {}
    for p in sorted(glob.glob(os.path.join(_dir(dd, "haiku_out"), "*.json"))):
        for v in json.load(open(p)):
            verdicts[v["id"]] = v
    cands = json.load(open(os.path.join(dd, "realtask_candidates.json")))
    by_id = {c["id"]: c for c in cands}
    json.dump(verdicts, open(os.path.join(dd, "realtask_verdicts.json"), "w", encoding="utf-8"), ensure_ascii=False)

    pos = [by_id[i] for i, v in verdicts.items() if v.get("verdict") in POSITIVE and i in by_id]
    for c in pos:
        c["haiku_verdict"] = verdicts[c["id"]].get("verdict")
    pos.sort(key=lambda c: -c["score"])
    out = _dir(dd, "sonnet_in")
    n = 0
    for i in range(0, len(pos), SONNET_BATCH):
        json.dump(pos[i:i + SONNET_BATCH], open(os.path.join(out, f"s_{n:03d}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        n += 1
    print(f"merge-haiku: 裁决分布 {dict(Counter(v.get('verdict') for v in verdicts.values()).most_common())}", file=sys.stderr)
    print(f"  正例 {len(pos)} -> {n} Sonnet 批", file=sys.stderr)
    print(n)


def merge_sonnet(dd):
    rows = []
    for p in sorted(glob.glob(os.path.join(_dir(dd, "sonnet_out"), "*.json"))):
        try:
            recs = json.load(open(p))
        except json.JSONDecodeError as e:
            print(f"[skip] {os.path.basename(p)} JSON 损坏: {e}", file=sys.stderr)
            continue
        for rec in recs:
            base = {"id": rec.get("id", ""), "haiku_verdict": rec.get("haiku_verdict", ""),
                    "verdict_check": rec.get("verdict_check", "")}
            evs = rec.get("events") or []
            if not evs:
                rows.append({**base, **{k: "" for k in EVENT_FIELDS}})
            for e in evs:
                rows.append({**base, **{k: e.get(k, "") for k in EVENT_FIELDS}})
    cands = {c["id"]: c for c in json.load(open(os.path.join(dd, "realtask_candidates.json")))}
    for r in rows:
        c = cands.get(r["id"], {})
        r["date"] = c.get("date", "")
        r["score"] = c.get("score", "")
        r["permalink"] = c.get("permalink", "")
        r["title"] = c.get("title", "")
    rows.sort(key=lambda r: (str(r.get("date") or ""), r["id"]))
    out_csv = os.path.join(dd, "realtask_events.csv")
    fn = ["date", "id", "haiku_verdict", "verdict_check"] + EVENT_FIELDS + ["score", "permalink", "title"]
    w = csv.DictWriter(open(out_csv, "w", encoding="utf-8", newline=""), fieldnames=fn, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    print(f"merge-sonnet: {len(rows)} 行 -> {out_csv}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["split-haiku", "merge-haiku", "merge-sonnet"])
    ap.add_argument("--data-dir", default="data/reddit")
    a = ap.parse_args()
    {"split-haiku": split_haiku, "merge-haiku": merge_haiku, "merge-sonnet": merge_sonnet}[a.stage](a.data_dir)


if __name__ == "__main__":
    main()
