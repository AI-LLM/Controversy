#!/usr/bin/env python3
"""画 r/LocalLLaMA"小模型干成真实任务"事件的任务域月度曲线图。

每个 task_domain 一条线，横轴月份，纵轴每月事件数，图例标注各域总量。
数据来自 data/reddit/realtask_events.csv（realtask Level-2 抽取产物）。
输出 chat/realtask_domain_monthly (2026-06-06).png。

从仓库根目录运行：
    python3 "chat/realtask_domain_monthly.py"
"""
import csv
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "data/reddit/realtask_events.csv"
OUT = "chat/realtask_domain_monthly (2026-06-06).png"


def month(d: str):
    return d[:7] if d and len(d) >= 7 else None


def main() -> None:
    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8"))
            if r["model"] and r["task_domain"]]

    months = sorted({month(r["date"]) for r in rows if month(r["date"])})
    midx = {m: i for i, m in enumerate(months)}

    dom_m = defaultdict(lambda: [0] * len(months))
    dom_tot = Counter()
    for r in rows:
        m = month(r["date"])
        if m is None:
            continue
        dom_m[r["task_domain"]][midx[m]] += 1
        dom_tot[r["task_domain"]] += 1

    doms = [d for d, _ in dom_tot.most_common()]   # 按总量排序
    cmap = plt.get_cmap("tab20")

    fig, ax = plt.subplots(figsize=(15, 7))
    for i, d in enumerate(doms):
        ax.plot(range(len(months)), dom_m[d], marker="o", ms=3, lw=1.5,
                color=cmap(i % 20), label=f"{d} ({dom_tot[d]})")
    # 月份多，每 2 个月显示一个刻度标签，避免拥挤
    step = 2
    ticks = list(range(0, len(months), step))
    ax.set_xticks(ticks)
    ax.set_xticklabels([months[i] for i in ticks], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("events per month")
    ax.set_title("r/LocalLLaMA: real-task events by domain (monthly)\n"
                 "(small models completing real user tasks; 2026-06 partial)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="domain (total)", ncol=2, fontsize=8, loc="upper left")
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=130)
    print("saved", OUT)
    print("月份范围:", months[0], "->", months[-1], f"({len(months)} 个月)")
    # 打印 coding / agentic 的月度峰值，便于更新正文
    for d in ("coding", "agentic"):
        series = dom_m[d]
        peak = max(range(len(series)), key=lambda i: series[i])
        print(f"  {d} 月度峰值: {series[peak]} @ {months[peak]}")


if __name__ == "__main__":
    main()
