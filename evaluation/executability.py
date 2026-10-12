"""可執行率：把每份預測計畫丟進 mock Executor，看能否跑完（不檢查對錯）。

用來對照 exact match：「跑得完」與「計畫正確」差多少。
用法：uv run python -m evaluation.executability --runs fewshot qlora-r16 qlora-r16-v2
"""
import argparse
from collections import Counter

from evaluation.analyze import REPO, SPLITS, load_jsonl
from planner.executor import execute
from planner.schema import parse_output, validate


def outcome(raw: str) -> str:
    p = parse_output(raw)
    if p is None or validate(p):
        return "invalid"
    if p["action"] != "plan":
        return p["action"]
    try:
        execute(p, log=lambda m: None)
        return "ok"
    except (KeyError, IndexError, TypeError, RuntimeError) as e:  # 引用了不存在的欄位或索引
        return type(e).__name__


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    a = ap.parse_args()
    print("| run | split | plan 數 | 可執行 | 執行失敗 |\n|---|---|---|---|---|")
    for run in a.runs:
        for sp in SPLITS:
            c = Counter(outcome(p["raw"]) for p in load_jsonl(REPO / "results" / "preds" / run / f"{sp}.jsonl"))
            fail = sum(v for k, v in c.items() if k not in ("ok", "invalid", "clarify", "refuse"))
            print(f"| {run} | {sp} | {c['ok'] + fail} | {c['ok']} | {fail} |")


if __name__ == "__main__":
    main()
