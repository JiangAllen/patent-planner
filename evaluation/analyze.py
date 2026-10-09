"""彙整多個 run 的評分：整體指標、依類型 exact match、錯誤分布、action 混淆矩陣、圖表與失敗案例。"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

from evaluation.score import bootstrap_ci, classify_errors, score_sample
from planner.schema import parse_output

REPO = Path(__file__).resolve().parents[1]
SPLITS = ["test_id", "test_ood"]
CATS = ["single", "parallel", "chain", "dag", "clarify", "refuse"]
ACTIONS = ["plan", "clarify", "refuse", "invalid"]

# dataviz 參考色盤（light），依 --runs 順序固定指派；已用 validate_palette.js 驗證。
# 黃、綠對白底低於 3:1，以長條數值標籤與 results.md 表格補足。
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def score_run(run: str, split: str) -> list[dict]:
    gold = {r["id"]: r for r in load_jsonl(REPO / "data" / f"{split}.jsonl")}
    rows = []
    for p in load_jsonl(REPO / "results" / "preds" / run / f"{split}.jsonl"):
        g = gold[p["id"]]
        pred = parse_output(p["raw"])
        m = score_sample(g["gold"], pred)
        rows.append({"id": p["id"], "category": g["category"], "structure_id": g["structure_id"],
                     "gold_action": g["gold"]["action"], **m, "errors": classify_errors(g["gold"], pred, m)})
    if len(rows) != len(gold):
        raise SystemExit(f"{run}/{split} 預測 {len(rows)} 筆，但資料有 {len(gold)} 筆；推論可能沒跑完")
    return rows


def _rate(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def summarize(rows: list[dict]) -> dict:
    plan = [r for r in rows if r["deps_ok"] is not None]
    tp, fp, fn = (sum(r[k] for r in rows) for k in ("tool_tp", "tool_fp", "tool_fn"))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {
        "n": len(rows),
        "exact": bootstrap_ci([float(r["exact"]) for r in rows]),
        "json_ok": _rate(r["parse_ok"] for r in rows),
        "schema_ok": _rate(r["schema_ok"] for r in rows),
        "action_acc": _rate(r["action_ok"] for r in rows),
        "tool_f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0,
        "distractor": _rate(r["distractor"] for r in plan),
        "lit_acc": sum(r["lit_ok"] for r in plan) / max(1, sum(r["lit_n"] for r in plan)),
        "ref_acc": sum(r["ref_ok"] for r in plan) / max(1, sum(r["ref_n"] for r in plan)),
        "deps_acc": _rate(r["deps_ok"] for r in plan),
    }


def _ci(t) -> str:
    return f"{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]"


def _report(data: dict, runs: list[str]) -> str:
    lines = ["# 評估結果", "", "所有數字皆為本批測試集的觀察值；exact match 附 95% bootstrap CI，CI 重疊時不宣稱差異。", "",
             "## 整體指標", "",
             "| run | split | n | exact match [95% CI] | JSON 合法 | schema 合法 | action 準確 | tool F1 | 干擾項誤用 | 字面參數 | 引用參數 | 相依 |",
             "|" + "---|" * 12]
    for (run, sp), rows in data.items():
        s = summarize(rows)
        lines.append(f"| {run} | {sp} | {s['n']} | {_ci(s['exact'])} | {s['json_ok']:.3f} | {s['schema_ok']:.3f} | "
                     f"{s['action_acc']:.3f} | {s['tool_f1']:.3f} | {s['distractor']:.3f} | {s['lit_acc']:.3f} | "
                     f"{s['ref_acc']:.3f} | {s['deps_acc']:.3f} |")

    lines += ["", "## 依任務類型的 exact match", "", "| run | split | " + " | ".join(CATS) + " |", "|" + "---|" * (len(CATS) + 2)]
    for (run, sp), rows in data.items():
        cells = []
        for c in CATS:
            sub = [r["exact"] for r in rows if r["category"] == c]
            cells.append(f"{_rate(sub):.2f} (n={len(sub)})" if sub else "—")
        lines.append(f"| {run} | {sp} | " + " | ".join(cells) + " |")

    tags = sorted({t for rows in data.values() for r in rows for t in r["errors"]})
    lines += ["", "## 錯誤類型（筆數，一筆可有多個 tag）", "", "| run | split | " + " | ".join(tags) + " |",
              "|" + "---|" * (len(tags) + 2)]
    for (run, sp), rows in data.items():
        c = Counter(t for r in rows for t in r["errors"])
        lines.append(f"| {run} | {sp} | " + " | ".join(str(c[t]) for t in tags) + " |")

    lines += ["", "## action 混淆矩陣（列 = gold，欄 = 預測；test_id + test_ood 合計）", ""]
    for run in runs:
        rows = [r for sp in SPLITS for r in data[(run, sp)]]
        c = Counter((r["gold_action"], r["pred_action"]) for r in rows)
        lines += [f"**{run}**", "", "| gold \\ pred | " + " | ".join(ACTIONS) + " |", "|" + "---|" * (len(ACTIONS) + 1)]
        lines += [f"| {g} | " + " | ".join(str(c[(g, p)]) for p in ACTIONS) + " |" for g in ACTIONS[:3]]
        lines.append("")
    return "\n".join(lines) + "\n"


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft JhengHei", "Noto Sans CJK TC", "sans-serif"],
        "axes.unicode_minus": False, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "text.color": INK, "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
        "axes.edgecolor": GRID,
    })
    return plt


def _style(ax, grid_axis: str) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    # 圖例放在繪圖區上方，避免壓到長條
    ax.legend(frameon=False, labelcolor=INK, loc="lower right", bbox_to_anchor=(1, 1.0), ncol=4)


def _plot_by_category(data: dict, runs: list[str], figdir: Path) -> None:
    plt = _plt()
    width = 0.8 / len(runs)
    for sp in SPLITS:
        fig, ax = plt.subplots(figsize=(9, 4))
        for i, run in enumerate(runs):
            vals = [_rate(r["exact"] for r in data[(run, sp)] if r["category"] == c) for c in CATS]
            bars = ax.bar([x + i * width for x in range(len(CATS))], vals, width, label=run,
                          color=SERIES[i % len(SERIES)], edgecolor=SURFACE, linewidth=2)
            ax.bar_label(bars, fmt="%.2f", fontsize=7, color=INK_2, padding=2)
        ax.set_xticks([x + width * (len(runs) - 1) / 2 for x in range(len(CATS))], CATS)
        ax.set_ylim(0, 1.08)
        ax.set_ylabel("plan exact match")
        ax.set_title(f"依任務類型的 exact match（{sp}）", color=INK, loc="left", pad=22)
        _style(ax, "y")
        fig.tight_layout()
        fig.savefig(figdir / f"exact_by_category_{sp}.png", dpi=200)
        plt.close(fig)


def _plot_errors(data: dict, runs: list[str], figdir: Path) -> None:
    counts = {run: Counter(t for sp in SPLITS for r in data[(run, sp)] for t in r["errors"]) for run in runs}
    tags = sorted({t for c in counts.values() for t in c}, key=lambda t: -sum(c[t] for c in counts.values()))
    if not tags:
        return
    plt = _plt()
    height = 0.8 / len(runs)
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(tags) + 1.5))
    for i, run in enumerate(runs):
        bars = ax.barh([y + i * height for y in range(len(tags))], [counts[run][t] for t in tags], height,
                       label=run, color=SERIES[i % len(SERIES)], edgecolor=SURFACE, linewidth=2)
        ax.bar_label(bars, fontsize=7, color=INK_2, padding=2)
    ax.set_yticks([y + height * (len(runs) - 1) / 2 for y in range(len(tags))], tags)
    ax.invert_yaxis()
    ax.set_xlabel("筆數（test_id + test_ood）")
    ax.set_title("錯誤類型分布", color=INK, loc="left", pad=22)
    _style(ax, "x")
    fig.tight_layout()
    fig.savefig(figdir / "error_distribution.png", dpi=200)
    plt.close(fig)


def _dump_failures(run: str, n: int, data: dict, out: Path) -> None:
    lines = [f"# {run} 失敗案例（隨機 {n} 筆，seed 0）", ""]
    pool = []
    for sp in SPLITS:
        gold = {r["id"]: r for r in load_jsonl(REPO / "data" / f"{sp}.jsonl")}
        raw = {p["id"]: p["raw"] for p in load_jsonl(REPO / "results" / "preds" / run / f"{sp}.jsonl")}
        pool += [(sp, r, gold[r["id"]], raw[r["id"]]) for r in data[(run, sp)] if not r["exact"]]
    for sp, r, g, raw in random.Random(0).sample(pool, min(n, len(pool))):
        lines += [f"## {r['id']}（{sp} / {r['category']} / {r['structure_id']}）— {', '.join(r['errors'])}", "",
                  f"- 可用工具：{', '.join(g['available_tools'])}", f"- 需求：{g['request']}", "",
                  "gold：", "```json", json.dumps(g["gold"], ensure_ascii=False, indent=1), "```",
                  "預測：", "```", raw, "```", "", "觀察：", ""]
    (out / f"failures_{run}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--dump-failures", default=None, help="輸出該 run 的失敗案例供人工細讀")
    ap.add_argument("--n", type=int, default=30)
    a = ap.parse_args()

    out = REPO / "reports"
    (out / "scored").mkdir(parents=True, exist_ok=True)
    (out / "figs").mkdir(exist_ok=True)
    data = {(run, sp): score_run(run, sp) for run in a.runs for sp in SPLITS}
    for (run, sp), rows in data.items():
        (out / "scored" / f"{run}_{sp}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    (out / "results.md").write_text(_report(data, a.runs), encoding="utf-8")
    _plot_by_category(data, a.runs, out / "figs")
    _plot_errors(data, a.runs, out / "figs")
    if a.dump_failures:
        _dump_failures(a.dump_failures, a.n, data, out)
    print(f"寫出 {out / 'results.md'}")


if __name__ == "__main__":
    main()
