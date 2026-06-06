#!/usr/bin/env python3
"""画 r/LocalLLaMA"小模型干成真实任务"事件的任务域年度曲线图。

每个 task_domain 一条线，横轴年份（2023–2026），纵轴每年事件数。
2026 只有不到半年的数据，按"全年匀速"年化：值 × 365 / (2026 最晚事件的 day-of-year)。
2025→2026 段用虚线表示该点是年化估算。2023 自 3 月起、本身偏少，按要求不年化。
数据来自 data/reddit/realtask_events.csv。
输出 chat/realtask_domain_yearly (2026-06-06).png。

从仓库根目录运行：
    python3 "chat/realtask_domain_yearly.py"
"""
import csv
import datetime
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "data/reddit/realtask_events.csv"
OUT = "chat/realtask_domain_yearly (2026-06-06).png"
YEARS = ["2023", "2024", "2025", "2026"]


def main() -> None:
    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8"))
            if r["model"] and r["task_domain"] and r["date"]]

    # 2026 年化系数：365 / 最晚事件的 day-of-year
    d26 = [r["date"] for r in rows if r["date"][:4] == "2026"]
    doy = datetime.date(*map(int, max(d26).split("-"))).timetuple().tm_yday
    factor = 365 / doy

    dom_y = defaultdict(lambda: {y: 0 for y in YEARS})
    dom_tot = Counter()
    for r in rows:
        y = r["date"][:4]
        if y in YEARS:
            dom_y[r["task_domain"]][y] += 1
            dom_tot[r["task_domain"]] += 1

    doms = [d for d, _ in dom_tot.most_common()]
    cmap = plt.get_cmap("tab20")

    fig, ax = plt.subplots(figsize=(11, 7))
    x = list(range(len(YEARS)))
    for i, d in enumerate(doms):
        vals = [dom_y[d][y] for y in YEARS]
        vals[-1] = round(vals[-1] * factor)          # 2026 年化
        c = cmap(i % 20)
        ax.plot(x[:3], vals[:3], marker="o", ms=5, lw=1.8, color=c,
                label=f"{d} ({dom_tot[d]})")
        ax.plot(x[2:], vals[2:], marker="o", ms=5, lw=1.8, color=c, ls="--")  # 末段虚线=年化
    ax.set_xticks(x)
    ax.set_xticklabels(["2023", "2024", "2025", "2026*"], fontsize=10)
    ax.set_ylabel("events per year")
    ax.set_title("r/LocalLLaMA: real-task events by domain (yearly)\n"
                 f"(* 2026 annualized x{factor:.2f} from Jan-Jun; dashed = estimate; "
                 "2023 from Mar)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="domain (total events)", ncol=2, fontsize=8, loc="upper left")
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=130)
    print("saved", OUT, "| 年化系数 =", round(factor, 3))
    for d in ("coding", "agentic"):
        v = dom_y[d]
        print(f"  {d}: 2023={v['2023']} 2024={v['2024']} 2025={v['2025']} "
              f"2026={v['2026']}->年化{round(v['2026']*factor)}")


if __name__ == "__main__":
    main()
