#!/usr/bin/env python3
"""画 r/LocalLLaMA"小模型干成真实任务"事件的任务域季度曲线图。

每个 task_domain 一条线，横轴季度，纵轴每季事件数，图例标注各域总量。
数据来自 data/reddit/realtask_events.csv（realtask Level-2 抽取产物）。
输出 chat/realtask_domain_quarterly (2026-06-06).png。

从仓库根目录运行：
    python3 "chat/realtask_domain_quarterly.py"
"""
import csv
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "data/reddit/realtask_events.csv"
OUT = "chat/realtask_domain_quarterly (2026-06-06).png"


def quarter(d: str):
    if not d or len(d) < 7:
        return None
    y, m = d[:7].split("-")
    return (int(y), (int(m) - 1) // 3 + 1)


def main() -> None:
    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8"))
            if r["model"] and r["task_domain"]]

    qs = sorted({quarter(r["date"]) for r in rows if quarter(r["date"])})
    qlabels = [f"{y}Q{q}" for (y, q) in qs]
    qidx = {qv: i for i, qv in enumerate(qs)}

    dom_q = defaultdict(lambda: [0] * len(qs))
    dom_tot = Counter()
    for r in rows:
        qv = quarter(r["date"])
        if qv is None:
            continue
        dom_q[r["task_domain"]][qidx[qv]] += 1
        dom_tot[r["task_domain"]] += 1

    doms = [d for d, _ in dom_tot.most_common()]   # 按总量排序
    cmap = plt.get_cmap("tab20")

    fig, ax = plt.subplots(figsize=(13, 7))
    for i, d in enumerate(doms):
        ax.plot(range(len(qs)), dom_q[d], marker="o", ms=4, lw=1.8,
                color=cmap(i % 20), label=f"{d} ({dom_tot[d]})")
    ax.set_xticks(range(len(qs)))
    ax.set_xticklabels(qlabels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("events per quarter")
    ax.set_title("r/LocalLLaMA: real-task events by domain (quarterly)\n"
                 "(small models completing real user tasks; 2026Q2 partial = Apr-Jun)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="domain (total)", ncol=2, fontsize=8, loc="upper left")
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=130)
    print("saved", OUT)
    print("季度范围:", qlabels[0], "->", qlabels[-1], f"({len(qs)} 季度)")


if __name__ == "__main__":
    main()
