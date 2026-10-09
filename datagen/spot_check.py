"""每類抽 15 筆，產生人工抽查表 reports/spot_check.md。資料全為合成，可直接閱讀。"""
import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CATS = ["single", "parallel", "chain", "dag", "clarify", "refuse"]


def main() -> None:
    rows = [json.loads(line) for line in (REPO / "data" / "train.jsonl").read_text(encoding="utf-8").splitlines()]
    rng = random.Random(0)
    lines = ["# 改寫抽查表", "", "每筆標記 ✅（語意一致）或 ❌（語意偏移，寫明原因）。", ""]
    for cat in CATS:
        pool = [r for r in rows if r["category"] == cat and r["paraphrased"]]
        lines += [f"## {cat}", "", "| id | 原句 | 改寫 | gold | 標記 |", "|---|---|---|---|---|"]
        for r in rng.sample(pool, min(15, len(pool))):
            gold = json.dumps(r["gold"], ensure_ascii=False).replace("|", "\\|")
            lines.append(f"| {r['id']} | {r['request_original']} | {r['request']} | `{gold}` |  |")
        lines.append("")
    out = REPO / "reports" / "spot_check.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"寫出 {out}")


if __name__ == "__main__":
    main()
