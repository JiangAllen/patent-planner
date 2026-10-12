"""敏感度分析：把「嵌在句子裡的單一引用」（如 "新期限為 $s2.deadline"）還原成純引用後重算 exact match。

主指標不變；這只回答「有多少失敗其實是引用寫法的格式約定，而不是規劃錯誤」。
用法：uv run python -m evaluation.sensitivity --runs zeroshot fewshot qlora-r16
      uv run python -m evaluation.sensitivity --paired qlora-r16 qlora-r16-v2   # 同題配對 bootstrap
"""
import argparse
import random
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


def paired_diff(a: list[float], b: list[float], n_boot: int = 10000, seed: int = 0) -> tuple[float, float, float]:
    """同一組題目上 b − a 的平均差與 95% 配對 bootstrap CI；比兩個獨立 CI 是否重疊更有檢定力。"""
    if not a or len(a) != len(b):
        raise ValueError(f"配對資料長度不符或為空：{len(a)} vs {len(b)}")
    d = [y - x for x, y in zip(a, b)]
    rng = random.Random(seed)
    boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(n_boot))
    return sum(d) / len(d), boots[int(n_boot * 0.025)], boots[int(n_boot * 0.975)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+")
    ap.add_argument("--paired", nargs=2, metavar=("A", "B"), help="讀 reports/scored，算 B − A 的配對差")
    a = ap.parse_args()
    if a.paired:
        for sp in SPLITS:
            ex = [{r["id"]: float(r["exact"]) for r in load_jsonl(REPO / "reports" / "scored" / f"{run}_{sp}.jsonl")}
                  for run in a.paired]
            if set(ex[0]) != set(ex[1]):
                raise ValueError(f"{sp}：兩組預測的題目 id 不一致")
            ids = sorted(ex[0])
            m, lo, hi = paired_diff([ex[0][i] for i in ids], [ex[1][i] for i in ids])
            print(f"{a.paired[1]} − {a.paired[0]} | {sp} | n={len(ids)} | {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        return
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
