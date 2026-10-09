"""把 gold 當成預測寫成 oracle run；analyze 的結果必須全部是 1.000，否則代表評分器或資料有 bug。"""
import json
from pathlib import Path

from planner.prompt import gold_text

REPO = Path(__file__).resolve().parents[1]

for split in ("test_id", "test_ood"):
    rows = [json.loads(line) for line in (REPO / "data" / f"{split}.jsonl").read_text(encoding="utf-8").splitlines()]
    out = REPO / "results" / "preds" / "oracle" / f"{split}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps({"id": r["id"], "raw": gold_text(r["gold"])}, ensure_ascii=False) + "\n"
                           for r in rows), encoding="utf-8")
print("oracle 寫出完成")
