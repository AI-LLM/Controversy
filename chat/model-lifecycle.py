#!/usr/bin/env python3
"""AI 模型生命周期分析：发布间隔 + 版本寿命。

多数据源：
  1. token-price.csv      → 发布日期（effective_date）
  2. DEPRECATED 基线表     → 退市日期初始值（来自官方公告 + 手工校准）
  3. deprecation_events.csv → Reddit 退市讨论帖，用 created_utc 精确化退市日期

输出 model-lifecycle.png + model-lifecycle.md
"""
from __future__ import annotations

import csv
import os
import re
from datetime import datetime
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "token-price.csv")
DEP_CSV = os.path.join(HERE, "..", "data", "reddit", "deprecation_events.csv")
OUT_PNG = os.path.join(HERE, "model-lifecycle.png")
OUT_MD = os.path.join(HERE, "model-lifecycle.md")

NOW = "2026-06"

# 同模型降价/缓存变体/促销切换——不算新模型发布
SKIP_RELEASES = {
    "o3 (price cut)", "Claude 3.5 Sonnet (caching)", "Claude 3.5 Haiku (cut)",
    "deepseek-chat V2 + context caching", "DeepSeek-V3 (standard)",
    "DeepSeek-V4 Pro (standard)", "Gemini 1.5 Pro (<=128K cut)",
    "Gemini 1.5 Flash (<=128K cut)", "OpenAI audio models",
    "text-embedding-ada-002", "Off-peak discount",
}

# 基线退市日期（YYYY-MM），来自官方公告 + 手工校准
DEPRECATED_BASELINE = {
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
    "Claude 3.5 Sonnet (caching)": "2025-06",
    "Claude 3.5 Haiku (launch)": "2024-12",
    "Claude 3.5 Haiku (cut)": "2025-10",
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
    "DeepSeek-V3 (standard)": "2025-09",
    "DeepSeek-V3.1 (unified)": "2025-09",
    "DeepSeek-V4 Pro (promo 75% off)": "2026-06",
}

# CSV 模型名 → Reddit 帖子里对应的搜索关键词（小写）
MODEL_TO_REDDIT_KEYS = {
    "GPT-3 Davinci": ["davinci", "text-davinci"],
    "GPT-3 Curie": ["curie"],
    "GPT-3 Babbage": ["babbage"],
    "GPT-3 Ada": ["gpt-3 ada", "text-ada"],
    "gpt-3.5-turbo-0301": ["gpt-3.5-turbo", "gpt-3.5 turbo"],
    "gpt-3.5-turbo-16k-0613": ["gpt-3.5-turbo-16k"],
    "gpt-3.5-turbo-1106": ["gpt-3.5-turbo"],
    "gpt-3.5-turbo-0125": ["gpt-3.5-turbo"],
    "gpt-4 (8K)": ["gpt-4 ", "gpt4 "],
    "gpt-4-32k": ["gpt-4-32k"],
    "gpt-4-turbo (1106-preview)": ["gpt-4-turbo", "gpt-4 turbo", "gpt4-turbo"],
    "gpt-4o-2024-05-13": ["gpt-4o"],
    "gpt-4o-2024-08-06": ["gpt-4o"],
    "gpt-4.5-preview": ["gpt-4.5"],
    "gpt-4.1": ["gpt-4.1"],
    "gpt-4.1-mini": ["gpt-4.1-mini", "gpt-4.1 mini"],
    "gpt-4.1-nano": ["gpt-4.1-nano", "gpt-4.1 nano"],
    "o1-preview": ["o1-preview"],
    "o1-mini": ["o1-mini"],
    "o1 (GA)": ["o1 "],
    "o3-mini": ["o3-mini"],
    "o4-mini": ["o4-mini"],
    "Claude Instant 1.2": ["claude instant"],
    "Claude 2.1": ["claude 2.1", "claude 2"],
    "Claude 3 Opus": ["claude 3 opus"],
    "Claude 3 Sonnet": ["claude 3 sonnet"],
    "Claude 3 Haiku": ["claude 3 haiku"],
    "Claude 3.5 Sonnet": ["claude 3.5 sonnet"],
    "Claude 3.5 Haiku (launch)": ["claude 3.5 haiku"],
    "Claude 3.7 Sonnet": ["claude 3.7"],
    "Claude Opus 4": ["claude opus 4 ", "opus 4 "],
    "Claude Sonnet 4": ["claude sonnet 4 ", "sonnet 4 "],
    "Claude Opus 4.1": ["opus 4.1"],
    "Claude Sonnet 4.5": ["sonnet 4.5"],
    "Claude Haiku 4.5": ["haiku 4.5"],
    "PaLM 2 text-bison": ["palm"],
    "Gemini 1.0 Pro": ["gemini 1.0"],
    "Gemini 1.5 Pro (<=128K)": ["gemini 1.5 pro"],
    "Gemini 1.5 Flash (<=128K)": ["gemini 1.5 flash"],
    "Gemini 1.5 Flash-8B (<=128K)": ["gemini 1.5 flash-8b", "flash-8b"],
    "Gemini 2.0 Flash": ["gemini 2.0 flash"],
    "Gemini 2.0 Flash-Lite": ["gemini 2.0 flash-lite", "flash-lite"],
    "DeepSeek-V2 (deepseek-chat)": ["deepseek-v2", "deepseek v2"],
    "DeepSeek-V3 (promo)": ["deepseek-v3", "deepseek v3"],
    "DeepSeek-V3.1 (unified)": ["deepseek-v3.1", "v3.1"],
    "DeepSeek-V4 Pro (promo 75% off)": ["deepseek-v4", "deepseek v4"],
}

DEP_KEYWORDS = ("deprecat", "retir", "sunset", "no longer", "removed", "end of life", "shut down")

COLORS = {"OpenAI": "#10a37f", "Anthropic": "#d97706",
          "Google": "#4285f4", "DeepSeek": "#1a1a2e"}
PROVIDERS = ["OpenAI", "Anthropic", "Google", "DeepSeek"]


def ym_to_dt(ym):
    return datetime.strptime(ym, "%Y-%m")


def load_models():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    seen = set()
    api = defaultdict(list)
    for r in rows:
        if r["category"] != "API":
            continue
        nm = r["product_or_model"]
        if nm in SKIP_RELEASES:
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


def refine_deprecated_from_reddit():
    """用 deprecation_events.csv 精确化基线退市日期。

    规则：对每个 DEPRECATED 模型，找 Reddit 里 score>=10 的退市讨论帖中
    最早的 date（YYYY-MM-DD），取其 YYYY-MM。如果比基线更早，用 Reddit 日期；
    如果一致或更晚，保留基线（基线来自官方公告，更权威）。
    """
    dep = dict(DEPRECATED_BASELINE)

    if not os.path.exists(DEP_CSV):
        print(f"  [!] {DEP_CSV} not found, using baseline only", flush=True)
        return dep, {}

    dep_rows = list(csv.DictReader(open(DEP_CSV, encoding="utf-8")))
    reddit_evidence = {}

    for model, search_keys in MODEL_TO_REDDIT_KEYS.items():
        if model not in dep:
            continue
        best = None
        for r in dep_rows:
            # 只信 Haiku 判为 model_retirement 的帖子
            if r.get("llm_verdict") != "model_retirement":
                continue
            ms = r["models_mentioned"].lower()
            if not any(k in ms for k in search_keys):
                continue
            sc = int(r["score"] or 0)
            if sc < 5:
                continue
            d = r["date"]
            if best is None or d < best[0]:
                best = (d, sc, r["title"][:50], r["permalink"])
        if best:
            reddit_ym = best[0][:7]
            reddit_evidence[model] = best
            if reddit_ym < dep[model]:
                dep[model] = reddit_ym

    return dep, reddit_evidence


def compute_intervals(models_by_prov):
    result = {}
    for prov in PROVIDERS:
        pts = sorted(models_by_prov[prov], key=lambda x: x[0])
        dates = [ym_to_dt(ym) for ym, _ in pts]
        intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        result[prov] = intervals
    return result


def compute_lifespans(models_by_prov, dep):
    result = {}
    now_dt = ym_to_dt(NOW)
    for prov in PROVIDERS:
        spans = []
        for ym, nm in models_by_prov[prov]:
            launch = ym_to_dt(ym)
            dep_ym = dep.get(nm)
            if dep_ym:
                end = ym_to_dt(dep_ym)
                spans.append((nm, ym, dep_ym, (end - launch).days, True))
            else:
                spans.append((nm, ym, NOW, (now_dt - launch).days, False))
        result[prov] = spans
    return result


def main():
    api = load_models()
    dep, reddit_ev = refine_deprecated_from_reddit()
    intervals = compute_intervals(api)
    lifespans = compute_lifespans(api, dep)

    # 统计哪些退市日期被 Reddit 精确化了
    refined = []
    for model, (rd, sc, title, plink) in reddit_ev.items():
        bl = DEPRECATED_BASELINE.get(model, "")
        final = dep.get(model, "")
        if final != bl:
            refined.append((model, bl, final, rd, sc, title))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor("white")

    # ---- Chart 1: Release intervals ----
    positions = list(range(len(PROVIDERS)))
    bp_data = [intervals[p] for p in PROVIDERS]
    bp = ax1.boxplot(bp_data, positions=positions, widths=0.5, patch_artist=True,
                     showfliers=False, zorder=2)
    for i, (patch, prov) in enumerate(zip(bp["boxes"], PROVIDERS)):
        c = COLORS[prov]
        patch.set_facecolor(c); patch.set_alpha(0.25); patch.set_edgecolor(c)
        for key in ("whiskers", "caps"):
            bp[key][i*2].set_color(c); bp[key][i*2+1].set_color(c)
        bp["medians"][i].set_color(c); bp["medians"][i].set_linewidth(2)
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
    ax1.grid(axis="y", alpha=0.25); ax1.set_ylim(bottom=-10)

    # ---- Chart 2: Version lifespan ----
    bp_data2 = [[d for *_, d, _ in lifespans[p]] for p in PROVIDERS]
    bp2 = ax2.boxplot(bp_data2, positions=positions, widths=0.5, patch_artist=True,
                      showfliers=False, zorder=2)
    for i, (patch, prov) in enumerate(zip(bp2["boxes"], PROVIDERS)):
        c = COLORS[prov]
        patch.set_facecolor(c); patch.set_alpha(0.25); patch.set_edgecolor(c)
        for key in ("whiskers", "caps"):
            bp2[key][i*2].set_color(c); bp2[key][i*2+1].set_color(c)
        bp2["medians"][i].set_color(c); bp2["medians"][i].set_linewidth(2)
    for i, prov in enumerate(PROVIDERS):
        spans = lifespans[prov]
        rng = np.random.default_rng(7)
        for nm, _, _, d, retired in spans:
            j = rng.uniform(-0.15, 0.15)
            marker = "x" if retired else "o"
            ec = "none" if retired else "white"
            ax2.scatter(i + j, d, color=COLORS[prov], marker=marker,
                        alpha=0.7 if retired else 0.5, s=30, zorder=3,
                        edgecolors=ec, linewidths=0.5)
        days_list = [d for *_, d, _ in spans]
        med = sorted(days_list)[len(days_list)//2] if days_list else 0
        n_ret = sum(1 for *_, r in spans if r)
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
    ax2.grid(axis="y", alpha=0.25); ax2.set_ylim(bottom=-20)

    fig.suptitle("AI Model Lifecycle: Release Cadence & Version Lifespan (2023-2026)",
                 fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=180, bbox_inches="tight")
    print(f"wrote {OUT_PNG}")
    plt.close(fig)

    # ---- md ----
    int_tbl = []
    for prov in PROVIDERS:
        vals = intervals[prov]
        if not vals:
            continue
        vals_s = sorted(vals)
        med = vals_s[len(vals_s)//2]
        int_tbl.append(f"| {prov} | {len(vals)+1} | {min(vals)} | {med} | {max(vals)} | {sum(vals)/len(vals):.0f} |")

    life_tbl = []
    for prov in PROVIDERS:
        for nm, launch, end, d, retired in sorted(lifespans[prov], key=lambda x: -x[3]):
            status = "retired" if retired else "alive"
            ev = reddit_ev.get(nm)
            src = ""
            if ev:
                src = f" (Reddit {ev[0]})"
            life_tbl.append(f"| {prov} | {nm} | {launch} | {end} | {d} | {d/30:.1f} | {status}{src} |")

    refined_tbl = []
    for model, bl, final, rd, sc, title in refined:
        refined_tbl.append(f"| {model} | {bl} | {final} | {rd} | {sc} | {title} |")

    md = f"""# AI Model Lifecycle: Release Cadence & Version Lifespan

## 数据源

- **发布日期**：`token-price.csv` 的 `effective_date`（去除降价/缓存等非新发布事件）
- **退市日期**：基线来自官方公告（DEPRECATED_BASELINE），叠加 `deprecation_events.csv`
  （Reddit 退市讨论帖 19,793 条）的 `created_utc` 精确化。规则：Reddit 帖日期比基线更早
  则采用（说明基线偏保守），否则保留基线（官方源更权威）。
- **仍在售模型**的寿命为右删失（right-censored，截至 {NOW}）。

## 图表

![Model Lifecycle](model-lifecycle.png)

- **左图**：各家连续新模型发布间隔天数（箱线图 + 散点）。
- **右图**：各版本从发布到退市天数（x = 已退市，o = 仍在售/右删失）。

## 发布间隔统计

| Provider | Models | Min (days) | Median | Max | Mean |
|---|---|---|---|---|---|
{chr(10).join(int_tbl)}

## 各版本寿命明细（按寿命降序）

| Provider | Model | Launch | End | Days | Months | Status |
|---|---|---|---|---|---|---|
{chr(10).join(life_tbl)}

{"## Reddit 精确化的退市日期" + chr(10) + chr(10) + "基线日期 vs Reddit 最早退市帖日期。以下模型的退市日期被 Reddit 帖前移：" + chr(10) + chr(10) + "| Model | Baseline | Refined | Reddit date | Score | Title |" + chr(10) + "|---|---|---|---|---|---|" + chr(10) + chr(10).join(refined_tbl) if refined_tbl else "所有退市日期与 Reddit 一致或 Reddit 更晚（基线未被修改）。"}
"""
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {OUT_MD}")

    print(f"\n发布事件: " + ", ".join(f"{p}={len(api[p])}" for p in PROVIDERS))
    print(f"退市模型: {len(dep)} (其中 {len(refined)} 被 Reddit 精确化)")
    if refined:
        for model, bl, final, rd, sc, title in refined:
            print(f"  {model:30s}  {bl} -> {final}  (Reddit {rd}, {sc}up)")


if __name__ == "__main__":
    main()
