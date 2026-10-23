"""Generate the images used in README.md (light + dark SVG variants).

Every number here is copied from results already recorded in the repo
(Roadmap, data/paper_eval_criteria.yaml, docs/CHAT_75aab7d5_NEXT_STEPS.md,
docs/CLAUDE_SONNET_REVIEW_VERIFIED_ROADMAP.md, the archived README) or
counted from the source tree. Nothing is re-run.

Needs matplotlib (not in requirements.txt) and the Inter font installed;
matplotlib falls back to its default font without it.

Usage: python scripts/make_readme_charts.py
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"
DPI = 100
FONT = "Inter"
DISPLAY = "Inter Display"

# Apple system colors. Cards sit on a transparent page so they work on
# GitHub's light (#ffffff) and dark (#0d1117) backgrounds.
THEMES = {
    "light": {
        "card": "#f5f5f7",
        "ink": "#1d1d1f",
        "ink2": "#6e6e73",
        "muted": "#86868b",
        "grid": "#e3e3e8",
        "blue": "#0071e3",
        "red": "#ff3b30",
        "track": "#e3e3e8",
        "band": "#e5effc",
    },
    "dark": {
        "card": "#1c1c1e",
        "ink": "#f5f5f7",
        "ink2": "#a1a1a6",
        "muted": "#8e8e93",
        "grid": "#2c2c2e",
        "blue": "#0a84ff",
        "red": "#ff453a",
        "track": "#3a3a3c",
        "band": "#11253f",
    },
}


# ---------------------------------------------------------------- helpers

def _fig(w, h):
    fig = plt.figure(figsize=(w, h), dpi=DPI)
    fig.patch.set_alpha(0)
    return fig


def _card(fig, t, x=0.0, y=0.0, w=1.0, h=1.0, radius=0.22):
    """Rounded card in figure-inch space (radius in inches)."""
    W, H = fig.get_size_inches()
    pad = 0.04
    fig.patches.append(FancyBboxPatch(
        (x * W + pad, y * H + pad), w * W - 2 * pad, h * H - 2 * pad,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        transform=fig.dpi_scale_trans, facecolor=t["card"], edgecolor="none", zorder=-10,
    ))


def _head(fig, t, eyebrow, title, sub=None):
    H = fig.get_size_inches()[1]
    top = 1 - 0.42 / H
    fig.text(0.045, top, eyebrow.upper(), color=t["blue"], fontsize=9, fontweight="semibold",
             family=FONT, va="top")
    fig.text(0.045, top - 0.27 / H, title, color=t["ink"], fontsize=17, fontweight="semibold",
             family=DISPLAY, va="top")
    if sub:
        fig.text(0.045, top - 0.66 / H, sub, color=t["ink2"], fontsize=10, family=FONT, va="top")


def _axes(fig, t, rect, grid="x"):
    ax = fig.add_axes(rect)
    ax.patch.set_alpha(0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(colors=t["muted"], length=0, labelsize=9, pad=8)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_family(FONT)
    if grid:
        ax.grid(axis=grid, color=t["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    return ax


def _ylabels(ax, t, labels):
    ax.set_yticks(range(len(labels)), labels)
    for lbl in ax.get_yticklabels():
        lbl.set_color(t["ink"])
        lbl.set_family(FONT)
        lbl.set_fontsize(10)


def _rbar(ax, x0, y0, x1, y1, color, r_px=5.0):
    """Rounded bar from data corners, drawn in inch space so corners stay round."""
    fig = ax.figure
    (px0, py0), (px1, py1) = ax.transData.transform([(x0, y0), (x1, y1)])
    lx, rx = sorted((px0, px1))
    by, ty = sorted((py0, py1))
    w, h = rx - lx, ty - by
    if w <= 0 or h <= 0:
        return
    r = min(r_px, w / 2, h / 2)
    fig.patches.append(FancyBboxPatch(
        (lx / DPI, by / DPI), w / DPI, h / DPI,
        boxstyle=f"round,pad=0,rounding_size={r / DPI}",
        transform=fig.dpi_scale_trans, facecolor=color, edgecolor="none", zorder=5,
    ))


def _save(fig, name, mode):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}-{mode}.svg", transparent=True)
    plt.close(fig)


# ---------------------------------------------------------------- hero + tiles

def hero(t, mode):
    fig = _fig(10, 3.0)
    fig.text(0.5, 0.80, "AN EXPERIMENT WITH CLAUDE OPUS 4.6", color=t["blue"], fontsize=11,
             fontweight="semibold", family=FONT, ha="center", va="center")
    fig.text(0.5, 0.54, "Trading Bot", color=t["ink"], fontsize=50, fontweight="bold",
             family=DISPLAY, ha="center", va="center")
    fig.text(0.5, 0.27, "An AI built a trading strategy, then built the tests to check it.",
             color=t["ink2"], fontsize=15, family=DISPLAY, ha="center", va="center")
    fig.text(0.5, 0.15, "The tests won.", color=t["ink2"], fontsize=15, family=DISPLAY,
             ha="center", va="center")
    _save(fig, "hero", mode)


def tiles(t, mode, total_lines):
    items = [
        ("30", "days", "first commit to archive"),
        (f"{total_lines // 1000 * 1000:,}+", "", "lines of code and docs"),
        ("0 of 5", "", "tickers passed validation"),
        ("6 of 23", "", "ETFs beat buy and hold"),
    ]
    fig = _fig(10, 1.7)
    n = len(items)
    gap = 0.012
    w = (1 - gap * (n - 1)) / n
    for i, (big, unit, label) in enumerate(items):
        x = i * (w + gap)
        _card(fig, t, x, 0, w, 1, radius=0.2)
        cx = x + w / 2
        txt = f"{big} {unit}".strip()
        fig.text(cx, 0.6, txt, color=t["ink"], fontsize=27, fontweight="semibold",
                 family=DISPLAY, ha="center", va="center")
        fig.text(cx, 0.29, label, color=t["ink2"], fontsize=10, family=FONT,
                 ha="center", va="center")
    _save(fig, "stats", mode)


# ---------------------------------------------------------------- charts

def chart_pvalues(t, mode):
    rows = [
        ("Trend following, 23 ETFs vs buy and hold", 0.998),
        ("Mean reversion, SPY out-of-sample", 0.529),
        ("Trend following, XLE", 0.274),
        ("Trend following, GLD", 0.188),
        ("Mean reversion, SPY in-sample gate", 0.178),
    ]
    fig = _fig(10, 4.2)
    _card(fig, t)
    _head(fig, t, "Results", "No test got under p = 0.05.",
          "p-value of each primary significance test. Anything in the blue strip would have counted as an edge.")
    ax = _axes(fig, t, [0.34, 0.12, 0.6, 0.52])
    ax.set_xlim(0, 1.04)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.axvspan(0, 0.05, color=t["band"], zorder=0, linewidth=0)
    ax.text(0.06, len(rows) - 0.55, "p = 0.05", color=t["blue"], fontsize=8.5, family=FONT, va="bottom")
    for y, (_, p) in enumerate(rows):
        _rbar(ax, 0, y - 0.09, 1.0, y + 0.09, t["track"], r_px=3)
        _rbar(ax, 0, y - 0.09, p, y + 0.09, t["blue"], r_px=3)
        ax.text(p + 0.015 if p < 0.9 else p - 0.015, y + 0.32, f"{p:.3f}", color=t["ink"],
                fontsize=9.5, family=FONT, fontweight="medium", ha="left" if p < 0.9 else "right")
    _ylabels(ax, t, [r[0] for r in rows])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "0.25", "0.50", "0.75", "1"])
    ax.grid(False)
    _save(fig, "pvalues", mode)


def chart_tf_folds(t, mode):
    data = {
        # fold returns, recorded avg OOS return, recorded avg vs buy and hold
        "SPY": ([-3.3, -1.9, 7.9, 10.1, 5.0, -15.5, 19.9], 3.2, -3.6),
        "GLD": ([0.0, 3.0, -4.4, 15.4, 5.0, 8.4, 15.6], 6.2, -6.0),
    }
    fig = _fig(10, 4.4)
    _card(fig, t)
    _head(fig, t, "Trend following", "Making money isn't the same as an edge.",
          "Return in each ~6-month out-of-sample walk-forward fold, 5 years of daily data.")
    for i, (sym, (folds, avg, vs_bh)) in enumerate(data.items()):
        x0 = 0.08 + i * 0.465
        ax = _axes(fig, t, [x0, 0.1, 0.4, 0.46], grid="y")
        ax.set_xlim(0.4, len(folds) + 0.6)
        ax.set_ylim(-20, 25)
        ax.set_yticks([-20, -10, 0, 10, 20])
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%" if v else "0")
        ax.set_xticks(range(1, len(folds) + 1), [str(k) for k in range(1, len(folds) + 1)])
        ax.axhline(0, color=t["muted"], linewidth=0.8, zorder=1)
        for k, v in enumerate(folds, start=1):
            _rbar(ax, k - 0.3, 0, k + 0.3, v, t["blue"] if v >= 0 else t["red"], r_px=4)
        fig.text(x0, 0.64, sym, color=t["ink"], fontsize=13, fontweight="semibold", family=DISPLAY)
        fig.text(x0 + 0.055, 0.64, f"avg {avg:+.1f}% per fold   ·   {vs_bh:+.1f}% vs buy and hold",
                 color=t["ink2"], fontsize=9.5, family=FONT)
    _save(fig, "tf_folds", mode)


def chart_review(t, mode):
    rows = [
        ("Plausible, never checked", 6),
        ("Already fixed or outdated", 4),
        ("Partly right", 2),
        ("Confirmed in the code", 9),
    ]
    fig = _fig(10, 3.5)
    _card(fig, t)
    _head(fig, t, "Second opinion", "Sonnet 4.6 reviewed the work. 9 of 21 claims were confirmed.",
          "Each claim in docs/CLAUDE_SONNET_REVIEW_VERIFIED_ROADMAP.md, grouped by verdict.")
    ax = _axes(fig, t, [0.3, 0.12, 0.62, 0.42], grid=None)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    for y, (_, n) in enumerate(rows):
        _rbar(ax, 0, y - 0.24, n, y + 0.24, t["blue"], r_px=5)
        ax.text(n + 0.15, y, str(n), color=t["ink"], fontsize=10, family=FONT, fontweight="medium",
                va="center")
    _ylabels(ax, t, [r[0] for r in rows])
    ax.set_xticks([])
    _save(fig, "sonnet_review", mode)


def _count(paths):
    return sum(len(p.read_text(encoding="utf-8").splitlines()) for p in paths)


def code_split():
    src = ROOT / "src"
    groups = {
        "Backtesting and validation": [
            src / f for f in ("walk_forward.py", "run_wfo.py", "backtest.py", "stats_utils.py",
                              "validation_routing.py", "paper_trade.py")
        ] + [ROOT / "scripts" / f for f in ("pool_validation.py", "apply_multiple_testing_correction.py",
                                             "run_paper.py", "verify_vix.py")],
        "Signals, indicators, data": [
            src / f for f in ("indicators.py", "indicator_scores.py", "signals.py", "signals_trend.py",
                              "hybrid.py", "regime.py", "expert.py", "intrinsic.py",
                              "config_resolver.py", "data.py", "utils.py")
        ],
        "Bot commands, charts, news": [ROOT / "main.py"] + [
            src / f for f in ("charts.py", "stock.py", "recap.py", "recap_queue.py", "tutorial.py",
                              "watchlist.py", "news.py", "daytrade.py", "indices.py", "stop.py",
                              "market_hours.py", "stocks.py")
        ],
        "Tests": sorted((ROOT / "tests").glob("test_*.py")),
        "Research docs": sorted((ROOT / "docs").rglob("*.md")) + [ROOT / "Roadmap"],
    }
    return [(k, _count(v)) for k, v in groups.items()]


def chart_code(t, mode, rows):
    rows = sorted(rows, key=lambda r: r[1])
    top = max(n for _, n in rows)
    fig = _fig(10, 3.8)
    _card(fig, t)
    _head(fig, t, "Effort", "Lots of validation. Very few tests.",
          "Lines in each part of the repo when it was archived.")
    ax = _axes(fig, t, [0.3, 0.1, 0.6, 0.48], grid=None)
    ax.set_xlim(0, top * 1.14)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    for y, (_, n) in enumerate(rows):
        _rbar(ax, 0, y - 0.26, n, y + 0.26, t["blue"], r_px=5)
        ax.text(n + top * 0.015, y, f"{n:,}", color=t["ink"], fontsize=10, family=FONT,
                fontweight="medium", va="center")
    _ylabels(ax, t, [r[0] for r in rows])
    ax.set_xticks([])
    _save(fig, "code_split", mode)


def roadmap_counts():
    text = (ROOT / "Roadmap").read_text(encoding="utf-8")
    phases, cur = [], None
    for line in text.splitlines():
        m = re.match(r"## Phase (\d) — (.+)", line)
        if m:
            cur = [f"{m.group(1)}  {m.group(2)}", 0, 0]
            phases.append(cur)
        elif cur and line.startswith("- [x]"):
            cur[1] += 1
        elif cur and line.startswith("- [ ]"):
            cur[2] += 1
    return phases


def chart_roadmap(t, mode, phases):
    rows = list(reversed(phases))
    fig = _fig(10, 4.4)
    _card(fig, t)
    _head(fig, t, "Scope", "It planned a business before it had a strategy.",
          "Roadmap checklist items built vs planned. No strategy ever passed, so phases 3 to 7 never started.")
    ax = _axes(fig, t, [0.34, 0.08, 0.56, 0.56], grid=None)
    ax.set_xlim(0, 33)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    for y, (_, d, n) in enumerate(rows):
        _rbar(ax, 0, y - 0.24, d + n, y + 0.24, t["track"], r_px=5)
        if d:
            _rbar(ax, 0, y - 0.24, d, y + 0.24, t["blue"], r_px=5)
        ax.text(d + n + 0.5, y, f"{d} of {d + n}", color=t["ink2"], fontsize=9.5, family=FONT,
                va="center")
    _ylabels(ax, t, [r[0] for r in rows])
    ax.set_xticks([])
    # legend as two inline swatches, bottom right where the short bars leave room
    for k, (label, color) in enumerate((("Built", t["blue"]), ("Planned", t["track"]))):
        lx = 0.78 + k * 0.09
        fig.patches.append(FancyBboxPatch((lx * 10, 0.15 * 4.4), 0.13, 0.13,
                                          boxstyle="round,pad=0,rounding_size=0.035",
                                          transform=fig.dpi_scale_trans, facecolor=color,
                                          edgecolor="none"))
        fig.text(lx + 0.018, 0.155, label, color=t["ink2"], fontsize=9.5, family=FONT, va="bottom")
    _save(fig, "roadmap", mode)


def main():
    plt.rcParams["font.family"] = FONT
    rows = code_split()
    phases = roadmap_counts()
    total = sum(n for _, n in rows)
    for mode, t in THEMES.items():
        hero(t, mode)
        tiles(t, mode, total)
        chart_pvalues(t, mode)
        chart_tf_folds(t, mode)
        chart_review(t, mode)
        chart_code(t, mode, rows)
        chart_roadmap(t, mode, phases)
    print("lines:", rows, "total", total)
    print("roadmap:", phases)


if __name__ == "__main__":
    main()
