#!/usr/bin/env python3
"""画 r/LocalLLaMA"小模型替代云端付费模型"事件的【按被替代厂商】年度曲线图。

每个被替代的云厂商一条线，横轴年份（2023–2026），纵轴每年替代事件数。
2026 只有不到半年的数据，按"全年匀速"年化（× 365 / 最晚事件 day-of-year）；
2025→2026 段画虚线表示是年化估算。2023 自 3 月起、未年化。
数据来自 data/reddit/realtask_events.csv 里 replaced_cloud=True 的事件。
输出 chat/realtask_replaced_cloud_yearly (2026-06-06).png。

从仓库根目录运行：
    python3 "chat/realtask_replaced_cloud_yearly.py"
"""
import csv
import datetime
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "data/reddit/realtask_events.csv"
OUT = "chat/realtask_replaced_cloud_yearly (2026-06-06).png"
YEARS = ["2023", "2024", "2025", "2026"]


def vendor(w: str) -> str:
    w = (w or "").lower()
    if "copilot" in w:
        return "GitHub Copilot"
    if "claude" in w or "anthropic" in w:
        return "Claude / Anthropic"
    if "gemini" in w or "google" in w:
        return "Gemini / Google"
    if "gpt" in w or "chatgpt" in w or "openai" in w or w.startswith("o1") or "o3" in w:
        return "ChatGPT / OpenAI"
    return "other / generic cloud"


def main() -> None:
    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8"))
            if r["model"] and r["date"]]
    repl = [r for r in rows if r["replaced_cloud"] == "True"]

    d26 = [r["date"] for r in rows if r["date"][:4] == "2026"]
    doy = datetime.date(*map(int, max(d26).split("-"))).timetuple().tm_yday
    factor = 365 / doy

    ven_y = defaultdict(lambda: {y: 0 for y in YEARS})
    ven_tot = Counter()
    for r in repl:
        y = r["date"][:4]
        if y in YEARS:
            v = vendor(r["replaced_what"])
            ven_y[v][y] += 1
            ven_tot[v] += 1

    vens = [v for v, _ in ven_tot.most_common()]
    cmap = plt.get_cmap("tab10")

    fig, ax = plt.subplots(figsize=(11, 7))
    x = list(range(len(YEARS)))
    for i, v in enumerate(vens):
        vals = [ven_y[v][y] for y in YEARS]
        vals[-1] = round(vals[-1] * factor)          # 2026 年化
        c = cmap(i % 10)
        ax.plot(x[:3], vals[:3], marker="o", ms=6, lw=2.0, color=c,
                label=f"{v} ({ven_tot[v]})")
        ax.plot(x[2:], vals[2:], marker="o", ms=6, lw=2.0, color=c, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels(["2023", "2024", "2025", "2026*"], fontsize=10)
    ax.set_ylabel("cloud-replacement events per year")
    ax.set_title("r/LocalLLaMA: replacing cloud/paid models with local small models\n"
                 f"by replaced target, yearly (* 2026 annualized x{factor:.2f}; dashed = estimate)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="replaced target (total)", fontsize=9, loc="upper left")
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=130)
    print("saved", OUT, "| 年化系数 =", round(factor, 3))
    for v in vens:
        d = ven_y[v]
        print(f"  {v:22} 2023={d['2023']} 2024={d['2024']} 2025={d['2025']} "
              f"2026={d['2026']}->年化{round(d['2026']*factor)}")


if __name__ == "__main__":
    main()
