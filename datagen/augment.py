"""第二輪補資料：只對 TEMPLATES_V2 產生樣本、改寫，接在 v1 train 後面寫成 data/train_v2.jsonl。

val / test 不動，v1 與 v2 才能在同一份測試集上比較。
用法：uv run python -m datagen.augment
"""
import hashlib
import json
import random
import sys
from collections import Counter

from datagen.generate import REPO, build_sample
from datagen.paraphrase import MODEL, _ollama_ready, paraphrase
from datagen.templates import TEMPLATES_V2


def generate_v2(seed: int = 7, per: int = 100) -> list[dict]:
    rng = random.Random(seed)
    return [{**build_sample(t, rng), "split": "train"} for t in TEMPLATES_V2 for _ in range(per)]


def merge(v1_train: list[dict], new: list[dict], eval_requests: set[str]) -> list[dict]:
    """剔除與 val / test 同句的（防洩漏）以及與既有 train 重複的，再接在 v1 後面。"""
    keys = {(r["request"], tuple(sorted(r["available_tools"]))) for r in v1_train}
    out = list(v1_train)
    for r in new:
        key = (r["request"], tuple(sorted(r["available_tools"])))
        if key in keys or r["request"] in eval_requests:
            continue
        keys.add(key)
        out.append({"id": f"train-v2-{len(out) - len(v1_train):05d}", **r})
    return out


def _load(name: str) -> list[dict]:
    return [json.loads(line) for line in (REPO / "data" / name).read_text(encoding="utf-8").splitlines()]


def main() -> None:
    if not _ollama_ready():
        sys.exit(f"Ollama 未啟動或沒有 {MODEL}")
    new = generate_v2()
    cache_path = REPO / "data" / "paraphrase_cache_v2.jsonl"
    cache = {}
    if cache_path.exists():
        cache = {e["key"]: e for e in map(json.loads, cache_path.read_text(encoding="utf-8").splitlines())}
    with cache_path.open("a", encoding="utf-8") as cf:
        for i, row in enumerate(new):
            key = hashlib.sha1(f"v2|{i}|{row['request_original']}".encode()).hexdigest()
            if key not in cache:
                text, ok = paraphrase(row["request_original"], row["surfaces"], seed=100000 + i)
                cache[key] = {"key": key, "text": text, "ok": ok}
                cf.write(json.dumps(cache[key], ensure_ascii=False) + "\n")
                cf.flush()
            row["request"], row["paraphrased"] = cache[key]["text"], cache[key]["ok"]
            if i % 50 == 0:
                print(f"{i}/{len(new)}", file=sys.stderr)

    v1 = _load("train.jsonl")
    eval_requests = {r["request"] for s in ("val", "test_id", "test_ood") for r in _load(f"{s}.jsonl")}
    rows = merge(v1, new, eval_requests)
    (REPO / "data" / "train_v2.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    manifest = {
        "version": "v2", "base": "v1 train + TEMPLATES_V2", "paraphrase_model": MODEL,
        "paraphrase_ok_rate": round(sum(r["paraphrased"] for r in new) / len(new), 4),
        "added": dict(Counter(r["structure_id"] for r in rows[len(v1):])),
        "dropped": len(new) - (len(rows) - len(v1)), "train_total": len(rows),
    }
    (REPO / "data" / "manifest_v2.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                                     encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
