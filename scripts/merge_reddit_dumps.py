#!/usr/bin/env python3
"""把带日期后缀的 Reddit dump 合并进不带后缀的主 JSONL 文件。

arctic-shift 增量下载会生成 `r_<频道>_<posts|comments>-YYYY-MM-DD.jsonl`，
本脚本将其并入主文件 `r_<频道>_<posts|comments>.jsonl`，之后所有挖掘脚本
（analyze_reddit.py 等）只跑主文件即可。

做的事：
  - 按 `id` 去重（增量与主文件在边界日期会重叠）。冲突时保留更新鲜的一条
    （freshness = max(retrieved_on, _meta.retrieved_2nd_on)）。
  - 按 `created_utc` 升序输出（与主文件现有时序一致）。
  - 原子写回：先写临时文件，sanity check 后 os.replace 覆盖主文件。
  - 把已消费的日期后缀文件移到 data/reddit/_merged/，避免下游 glob('*.jsonl')
    重复计数。

内存安全：只把（小的）增量 dump 读进内存；对（可能很大的）主文件做两遍流式扫描，
第一遍定去重胜负，第二遍做二路归并。

用法：
  python3 scripts/merge_reddit_dumps.py                 # 合并 data/reddit/ 下所有日期后缀 dump
  python3 scripts/merge_reddit_dumps.py --data-dir X     # 指定目录
  python3 scripts/merge_reddit_dumps.py --dry-run        # 只报告不写入
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone

# r_LocalLLaMA_posts-2026-04-30.jsonl -> base="r_LocalLLaMA_posts", suffix="2026-04-30"
DATED = re.compile(r"^(?P<base>.+)-(?P<date>\d{4}-\d{2}-\d{2})\.jsonl$")


def freshness(d: dict) -> int:
    """记录的新鲜度：取 retrieved_on 与 _meta.retrieved_2nd_on 的最大值。"""
    vals = []
    r = d.get("retrieved_on")
    if isinstance(r, (int, float)):
        vals.append(int(r))
    meta = d.get("_meta") or {}
    if isinstance(meta, dict):
        r2 = meta.get("retrieved_2nd_on")
        if isinstance(r2, (int, float)):
            vals.append(int(r2))
    return max(vals) if vals else 0


def fmt_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M")


def load_dumps(paths: list[str]) -> dict[str, dict]:
    """把多个增量 dump 读进内存，按 id 去重（dump 之间也可能重叠），保留最新鲜的。"""
    by_id: dict[str, dict] = {}
    for p in paths:
        with open(p, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rid = d.get("id")
                if rid is None:
                    continue
                old = by_id.get(rid)
                if old is None or freshness(d) >= freshness(old):
                    by_id[rid] = d
    return by_id


def merge_base(base: str, main_path: str, dump_paths: list[str], dry_run: bool) -> dict:
    """把 dump_paths 合并进 main_path。返回统计 dict。"""
    new = load_dumps(dump_paths)  # id -> record（增量，小，常驻内存）
    new_ids = set(new)

    main_exists = os.path.exists(main_path)

    # ---- 第一遍：流式扫主文件，定去重胜负 ----
    # drop_from_new: 主文件版本更新鲜（或同等），增量这条作废
    # new_win_ids:   增量版本更新鲜，第二遍要跳过主文件这条
    drop_from_new: set[str] = set()
    main_count = 0
    if main_exists:
        with open(main_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                main_count += 1
                # 只需在重叠时解析；用廉价子串预判 id 是否可能在 new 里太脆弱，直接解析
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rid = d.get("id")
                if rid in new_ids:
                    if freshness(d) >= freshness(new[rid]):
                        drop_from_new.add(rid)

    new_win_ids = new_ids - drop_from_new  # 增量胜出的 id（含主文件没有的全新 id）

    # 待并入的增量记录（去掉被主文件压制的），按 created_utc 排序供归并
    emit_new = [new[rid] for rid in new_win_ids]
    emit_new.sort(key=lambda r: int(r.get("created_utc", 0)))

    if dry_run:
        return {
            "base": base, "main_count": main_count, "dump_total": len(new),
            "added": len(emit_new), "dropped_dup": len(drop_from_new),
            "wrote": False,
        }

    # ---- 第二遍：二路归并（主文件流式 + emit_new 内存有序），按 created_utc 升序 ----
    tmp_path = main_path + ".merge.tmp"
    bi = 0
    n_new = len(emit_new)
    written = 0
    main_skipped = 0  # 被增量压制而跳过的主文件行
    with open(tmp_path, "w", encoding="utf-8") as out:
        def flush_new_until(ts: int):
            nonlocal bi, written
            while bi < n_new and int(emit_new[bi].get("created_utc", 0)) <= ts:
                out.write(json.dumps(emit_new[bi], ensure_ascii=False) + "\n")
                bi += 1
                written += 1

        if main_exists:
            with open(main_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    s = line.strip()
                    if not s:
                        continue
                    try:
                        d = json.loads(s)
                    except json.JSONDecodeError:
                        continue
                    rid = d.get("id")
                    if rid in new_win_ids:
                        main_skipped += 1
                        continue  # 增量版本更新鲜，丢弃主文件旧版
                    mc = int(d.get("created_utc", 0))
                    flush_new_until(mc)  # 先吐出所有 created_utc <= 当前主记录的增量
                    out.write(json.dumps(d, ensure_ascii=False) + "\n")
                    written += 1
        # 尾部剩余的增量
        while bi < n_new:
            out.write(json.dumps(emit_new[bi], ensure_ascii=False) + "\n")
            bi += 1
            written += 1

    # ---- sanity check ----
    expected = (main_count - main_skipped) + len(emit_new)
    if written != expected:
        os.remove(tmp_path)
        raise RuntimeError(
            f"[{base}] 行数核对失败：写出 {written} != 预期 {expected} "
            f"(main={main_count} skipped={main_skipped} new={len(emit_new)})"
        )

    os.replace(tmp_path, main_path)
    return {
        "base": base, "main_count": main_count, "dump_total": len(new),
        "added": len(emit_new), "dropped_dup": len(drop_from_new),
        "main_replaced": main_skipped, "final_count": written, "wrote": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="合并带日期后缀的 Reddit dump 进主 JSONL")
    ap.add_argument("--data-dir", default="data/reddit", help="JSONL 所在目录")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不写入、不归档")
    args = ap.parse_args()

    # 收集所有带日期后缀的文件，按 base 分组
    dumps_by_base: dict[str, list[str]] = defaultdict(list)
    for path in sorted(glob.glob(os.path.join(args.data_dir, "*.jsonl"))):
        m = DATED.match(os.path.basename(path))
        if m:
            dumps_by_base[m.group("base")].append(path)

    if not dumps_by_base:
        print(f"[!] {args.data_dir} 下没有带日期后缀的 dump（*-YYYY-MM-DD.jsonl）", file=sys.stderr)
        return 1

    merged_dir = os.path.join(args.data_dir, "_merged")
    summaries = []
    for base, dump_paths in sorted(dumps_by_base.items()):
        main_path = os.path.join(args.data_dir, base + ".jsonl")
        print(f"\n=== {base} ===", file=sys.stderr)
        print(f"  主文件: {'存在' if os.path.exists(main_path) else '不存在（将新建）'}", file=sys.stderr)
        for p in dump_paths:
            print(f"  增量:   {os.path.basename(p)}", file=sys.stderr)
        st = merge_base(base, main_path, dump_paths, args.dry_run)
        summaries.append((st, main_path, dump_paths))
        print(f"  增量唯一: {st['dump_total']:,}  新增: {st['added']:,}  "
              f"被主文件压制(重复): {st['dropped_dup']:,}", file=sys.stderr)
        if st.get("wrote"):
            print(f"  主文件原 {st['main_count']:,} 行，替换旧版 {st['main_replaced']:,}，"
                  f"合并后 {st['final_count']:,} 行 -> {os.path.basename(main_path)}", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] 未写入、未归档。", file=sys.stderr)
        return 0

    # 归档已消费的日期文件，避免下游 glob 双重计数
    os.makedirs(merged_dir, exist_ok=True)
    for st, main_path, dump_paths in summaries:
        for p in dump_paths:
            dst = os.path.join(merged_dir, os.path.basename(p))
            shutil.move(p, dst)
            print(f"  归档: {os.path.basename(p)} -> _merged/", file=sys.stderr)

    print("\n完成。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
