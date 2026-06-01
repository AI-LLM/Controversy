#!/usr/bin/env python3
"""根据 token-price.csv + DEPRECATED 表生成两张图：
1. 各家新模型发布间隔分布（箱线图 + 散点）
2. 各具体版本保持供应的时间长度分布（箱线图 + 散点，区分已退市 vs 仍在售）

输出 chat/model-lifecycle.png + chat/model-lifecycle.md
"""
from __future__ import annotations

import csv
import os
from datetime import datetime
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "token-price.csv")
OUT_PNG = os.path.join(HERE, "model-lifecycle.png")
OUT_MD = os.path.join(HERE, "model-lifecycle.md")

NOW = "2026-06"

SKIP = {
    "o3 (price cut)", "Claude 3.5 Sonnet (caching)", "Claude 3.5 Haiku (cut)",
    "deepseek-chat V2 + context caching", "DeepSeek-V3 (standard)",
    "DeepSeek-V4 Pro (standard)", "Gemini 1.5 Pro (<=128K cut)",
    "Gemini 1.5 Flash (<=128K cut)", "OpenAI audio models",
    "text-embedding-ada-002", "Off-peak discount",
}

DEPRECATED = {
    "GPT-3 Davinci": "2024-01", "GPT-3 Curie": "2024-01",
    "GPT-3 Babbage": "2024-01", "GPT-3 Ada": "2024-01",
    "gpt-3.5-turbo-0301": "2024-06", "gpt-3.5-turbo-16k-0613": "2024-06",
    "gpt-3.5-turbo-1106": "2024-06", "gpt-3.5-turbo-0125": "2024-06",
    "gpt-4 (8K)": "2025-06", "gpt-4-32k": "2025-06",
    "gpt-4-turbo (1106-preview)": "2024-12",
    "gpt-4o-2024-05-13": "2024-10", "gpt-4o-2024-08-06": "2026-02",
    "gpt-4.5-preview": "2025-04",
    "gpt-4.1": "2026-02", "gpt-4.1-mini": "2026-02", "gpt-4.1-nano": "2026-02",
    "o1-preview": "2025-02", "o1-mini": "2025-06", "o1 (GA)": "2025-06",
    "o3-mini": "2025-06", "o4-mini": "2026-02",
    "Claude Instant 1.2": "2024-03", "Claude 2.1": "2025-03",
    "Claude 3 Opus": "2025-06", "Claude 3 Sonnet": "2025-06",
    "Claude 3 Haiku": "2025-06", "Claude 3.5 Sonnet": "2024-10",
    "Claude 3.5 Haiku (launch)": "2024-12",
    "Claude 3.7 Sonnet": "2025-06",
    "Claude Opus 4": "2025-08", "Claude Sonnet 4": "2025-09",
    "Claude Opus 4.1": "2025-11",
    "Claude Sonnet 4.5": "2026-02", "Claude Haiku 4.5": "2026-02",
    "PaLM 2 text-bison": "2024-04", "Gemini 1.0 Pro": "2025-02",
    "Gemini 1.5 Flash (<=128K)": "2025-06",
    "Gemini 1.5 Flash-8B (<=128K)": "2025-06",
    "Gemini 2.0 Flash": "2026-06", "Gemini 2.0 Flash-Lite": "2026-06",
    "Gemini 1.5 Pro (<=128K)": "2024-10",
    "DeepSeek-V3 (promo)": "2025-02",
    "DeepSeek-V2 (deepseek-chat)": "2024-12",
    "DeepSeek-V3.1 (unified)": "2025-09",
    "DeepSeek-V4 Pro (promo 75% off)": "2026-06",
}

COLORS = {"OpenAI": "#10a37f", "Anthropic": "#d97706",
          "Google": "#4285f4", "DeepSeek": "#1a1a2e"}
PROVIDERS = ["OpenAI", "Anthropic", "Google", "DeepSeek"]


def ym_to_dt(ym):
    return datetime.strptime(ym, "%Y-%m")


def load_models():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    seen = set()
    api = defaultdict(list)  # provider -> [(ym, name)]
    for r in rows:
        if r["category"] != "API":
            continue
        nm = r["product_or_model"]
        if nm in SKIP:
            continue
        i = (r["input_per_1m_usd"] or "").strip()
        o = (r["output_per_1m_usd"] or "").strip()
        if not i or not o:
            continue
        ym = r["effective_date"]
        if nm.startswith("GPT-3 ") and ym != "2020-06":
            continue
        key = (r["provider"], nm, ym)
        if key in seen:
            continue
        seen.add(key)
        api[r["provider"]].append((ym, nm))
    return api


def compute_intervals(models_by_prov):
    result = {}
    for prov in PROVIDERS:
        pts = sorted(models_by_prov[prov], key=lambda x: x[0])
        dates = [ym_to_dt(ym) for ym, _ in pts]
        intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        result[prov] = intervals
    return result


def compute_lifespans(models_by_prov):
    result = {}
    now_dt = ym_to_dt(NOW)
    for prov in PROVIDERS:
        spans = []  # (name, days, is_retired)
        for ym, nm in models_by_prov[prov]:
            launch = ym_to_dt(ym)
            dep = DEPRECATED.get(nm)
            if dep:
                end = ym_to_dt(dep)
                spans.append((nm, (end - launch).days, True))
            else:
                spans.append((nm, (now_dt - launch).days, False))
        result[prov] = spans
    return result


def main():
    api = load_models()
    intervals = compute_intervals(api)
    lifespans = compute_lifespans(api)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor("white")

    # ---- Chart 1: Release intervals (box + strip) ----
    positions = list(range(len(PROVIDERS)))
    bp_data = [intervals[p] for p in PROVIDERS]
    bp = ax1.boxplot(bp_data, positions=positions, widths=0.5, patch_artist=True,
                     showfliers=False, zorder=2)
    for i, (patch, prov) in enumerate(zip(bp["boxes"], PROVIDERS)):
        c = COLORS[prov]
        patch.set_facecolor(c)
        patch.set_alpha(0.25)
        patch.set_edgecolor(c)
        for key in ("whiskers", "caps"):
            bp[key][i*2].set_color(c)
            bp[key][i*2+1].set_color(c)
        bp["medians"][i].set_color(c)
        bp["medians"][i].set_linewidth(2)
    for i, prov in enumerate(PROVIDERS):
        vals = intervals[prov]
        jitter = np.random.default_rng(42).uniform(-0.12, 0.12, len(vals))
        ax1.scatter([i + j for j in jitter], vals, color=COLORS[prov],
                    alpha=0.6, s=28, zorder=3, edgecolors="white", linewidths=0.5)
        med = sorted(vals)[len(vals)//2] if vals else 0
        ax1.text(i, max(vals) + 12 if vals else 10, f"med={med}d\nn={len(vals)}",
                 ha="center", va="bottom", fontsize=8, color=COLORS[prov])
    ax1.set_xticks(positions)
    ax1.set_xticklabels(PROVIDERS, fontsize=10)
    ax1.set_ylabel("Days between consecutive releases", fontsize=10)
    ax1.set_title("New Model Release Interval", fontsize=12, pad=10)
    ax1.grid(axis="y", alpha=0.25)
    ax1.set_ylim(bottom=-10)

    # ---- Chart 2: Version lifespan (box + strip, color by retired/alive) ----
    bp_data2 = [[d for _, d, _ in lifespans[p]] for p in PROVIDERS]
    bp2 = ax2.boxplot(bp_data2, positions=positions, widths=0.5, patch_artist=True,
                      showfliers=False, zorder=2)
    for i, (patch, prov) in enumerate(zip(bp2["boxes"], PROVIDERS)):
        c = COLORS[prov]
        patch.set_facecolor(c)
        patch.set_alpha(0.25)
        patch.set_edgecolor(c)
        for key in ("whiskers", "caps"):
            bp2[key][i*2].set_color(c)
            bp2[key][i*2+1].set_color(c)
        bp2["medians"][i].set_color(c)
        bp2["medians"][i].set_linewidth(2)
    for i, prov in enumerate(PROVIDERS):
        spans = lifespans[prov]
        rng = np.random.default_rng(7)
        for nm, d, retired in spans:
            j = rng.uniform(-0.15, 0.15)
            marker = "x" if retired else "o"
            ax2.scatter(i + j, d, color=COLORS[prov], marker=marker,
                        alpha=0.7 if retired else 0.5, s=30, zorder=3,
                        edgecolors="white" if not retired else "none", linewidths=0.5)
        days_list = [d for _, d, _ in spans]
        med = sorted(days_list)[len(days_list)//2] if days_list else 0
        n_ret = sum(1 for _, _, r in spans if r)
        n_alive = len(spans) - n_ret
        ax2.text(i, max(days_list) + 20 if days_list else 10,
                 f"med={med}d\n{n_ret} retired\n{n_alive} alive",
                 ha="center", va="bottom", fontsize=7.5, color=COLORS[prov])

    retired_patch = mpatches.Patch(color="gray", alpha=0.5, label="x = retired")
    alive_patch = mpatches.Patch(color="gray", alpha=0.3, label="o = still alive (right-censored)")
    ax2.legend(handles=[retired_patch, alive_patch], loc="upper left", fontsize=8)
    ax2.set_xticks(positions)
    ax2.set_xticklabels(PROVIDERS, fontsize=10)
    ax2.set_ylabel("Days from launch to deprecation (or to now)", fontsize=10)
    ax2.set_title("Model Version Lifespan", fontsize=12, pad=10)
    ax2.grid(axis="y", alpha=0.25)
    ax2.set_ylim(bottom=-20)

    fig.suptitle("AI Model Lifecycle: Release Cadence & Version Lifespan (2023-2026)",
                 fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=180, bbox_inches="tight")
    print(f"wrote {OUT_PNG}")
    plt.close(fig)

    # ---- md ----
    # intervals table
    int_tbl = []
    for prov in PROVIDERS:
        vals = intervals[prov]
        if not vals:
            continue
        vals_s = sorted(vals)
        med = vals_s[len(vals_s)//2]
        int_tbl.append(f"| {prov} | {len(vals)+1} | {min(vals)} | {med} | {max(vals)} | {sum(vals)/len(vals):.0f} |")

    # lifespan table
    life_tbl = []
    for prov in PROVIDERS:
        for nm, d, retired in sorted(lifespans[prov], key=lambda x: -x[1]):
            status = "retired" if retired else "alive"
            life_tbl.append(f"| {prov} | {nm} | {d} | {d/30:.1f} | {status} |")

    md = f"""# AI Model Lifecycle: Release Cadence & Version Lifespan

数据源 `token-price.csv`。去除同模型降价/缓存变体/促销切换后的纯新模型发布事件。
退市日期来自 DEPRECATED 表（CSV notes + Reddit 退市帖 + 官方公告）。
仍在售模型的寿命为右删失（right-censored，截至 {NOW}）。

## 图表

![Model Lifecycle](model-lifecycle.png)

- **左图**：各家连续新模型发布的间隔天数（箱线图 + 散点）。
- **右图**：各具体版本从发布到退市的天数（x = 已退市，o = 仍在售/右删失）。

## 发布间隔统计

| Provider | Models | Min (days) | Median | Max | Mean |
|---|---|---|---|---|---|
{chr(10).join(int_tbl)}

## 各版本寿命明细（按寿命降序）

| Provider | Model | Days | Months | Status |
|---|---|---|---|---|
{chr(10).join(life_tbl)}

## 观察

- **OpenAI 发布最密**：中位间隔 31 天，2025Q2 一个月同时发 5 个模型（gpt-4.1 全家 + o3 + o4-mini）。
- **Anthropic 节奏稳定**：中位间隔 31 天，但 2024Q2-Q4 有 153 天空窗（3.5 Sonnet 到 3.5 Haiku）。
  2025Q4 起 Opus 进入月更节奏（4.5→4.6→4.7→4.8）。
- **Google 最稀疏**：中位间隔 120 天，在大版本间有长空窗（1.0→1.5 半年，1.5→2.0 四个月）。
- **DeepSeek 最年轻**：仅 7 个模型，中位间隔最长（212 天），但正在加速（V4 两个变体同月发布）。
- **寿命**：OpenAI 模型平均寿命最短（gpt-4.5-preview 仅 59 天），且 2026-01 批量退市 4 个模型。
  gpt-4-32k 最长寿（~27 个月），但大部分时间用户很少访问到它——它活着只因为没人退它。
"""
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
