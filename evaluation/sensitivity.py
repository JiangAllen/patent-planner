"""敏感度分析：把「嵌在句子裡的單一引用」（如 "新期限為 $s2.deadline"）還原成純引用後重算 exact match。

主指標不變；這只回答「有多少失敗其實是引用寫法的格式約定，而不是規劃錯誤」。
用法：uv run python -m evaluation.sensitivity --runs zeroshot fewshot qlora-r16
"""
import argparse
import re

from evaluation.analyze import SPLITS, load_jsonl, REPO
from evaluation.score import score_sample
from planner.schema import parse_output

EMBEDDED = re.compile(r"\$s\d+\.[A-Za-z_][\w\[\]\.]*")


def unwrap(obj):
    """字串參數裡若恰好只有一個引用，就把整個字串換成該引用。"""
    if isinstance(obj, dict) and obj.get("action") == "plan":
        for step in obj.get("steps") or []:
            args = step.get("args") if isinstance(step, dict) else None
            for k, v in (args or {}).items():
                if isinstance(v, str) and len(refs := EMBEDDED.findall(v)) == 1:
                    args[k] = refs[0]
    return obj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    a = ap.parse_args()
    print("| run | split | n | exact（主指標） | exact（還原嵌入引用） |\n|---|---|---|---|---|")
    for run in a.runs:
        for sp in SPLITS:
            gold = {r["id"]: r["gold"] for r in load_jsonl(REPO / "data" / f"{sp}.jsonl")}
            preds = load_jsonl(REPO / "results" / "preds" / run / f"{sp}.jsonl")
            strict = sum(score_sample(gold[p["id"]], parse_output(p["raw"]))["exact"] for p in preds)
            loose = sum(score_sample(gold[p["id"]], unwrap(parse_output(p["raw"])))["exact"] for p in preds)
            print(f"| {run} | {sp} | {len(preds)} | {strict / len(preds):.3f} | {loose / len(preds):.3f} |")


if __name__ == "__main__":
    main()
