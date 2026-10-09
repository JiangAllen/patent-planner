"""用本地 Ollama 改寫 request，並以程式檢查改寫沒有改動參數值、也沒有捏造編號。"""
import hashlib
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

from opencc import OpenCC

from datagen.generate import SPLITS, finalize

REPO = Path(__file__).resolve().parents[1]
OLLAMA = "http://localhost:11434"
MODEL = "qwen2.5:7b-instruct"
ID_RE = re.compile(r"OA-\d{4}-\d{4}|TW-\d{4}-\d{4}|I\d{6}|\d{4}-\d{2}-\d{2}")
PROMPT = """把下面這句專利事務所內部的工作指示，改寫成另一種自然的繁體中文說法。
規則：意思完全不變；所有編號、日期、數字、「」內的文字必須原樣保留；不可新增任何編號或資訊；只輸出改寫後的一句話。
原句：{text}"""
_S2TW = OpenCC("s2tw")  # qwen2.5 改寫常混入簡體字；只轉字形不換詞彙（s2twp 會把「屏蔽」改成「遮蔽」，破壞 slot 字詞）


def check_paraphrase(original: str, candidate: str, surfaces: list[str]) -> bool:
    c = candidate.strip()
    if not c or "\n" in c:
        return False
    if not 0.5 <= len(c) / len(original) <= 2.0:
        return False
    if any(s not in c for s in surfaces):
        return False
    return set(ID_RE.findall(c)) <= set(ID_RE.findall(original))


def ollama_paraphrase(text: str, seed: int) -> str:
    body = json.dumps({"model": MODEL, "prompt": PROMPT.format(text=text), "stream": False,
                       "options": {"temperature": 0.9, "seed": seed}}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["response"].strip().strip('"')


def paraphrase(text, surfaces, seed, fn=None, retries=3, sleep=time.sleep):
    """最多嘗試 retries 次；全部失敗（連線錯誤或檢查不過）就退回原句。"""
    fn = fn or ollama_paraphrase
    for i in range(retries):
        try:
            candidate = _S2TW.convert(fn(text, seed * 10 + i))
        except (OSError, ValueError) as e:  # 連線失敗、逾時、回應不是 JSON
            print(f"改寫失敗（第 {i + 1} 次）：{e}", file=sys.stderr)
            sleep(2)
            continue
        if check_paraphrase(text, candidate, surfaces):
            return candidate, True
    return text, False


def _ollama_ready() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=5) as resp:
            return any(m["name"].startswith(MODEL) for m in json.loads(resp.read())["models"])
    except OSError:
        return False


def main() -> None:
    if not _ollama_ready():
        sys.exit(f"Ollama 未啟動或沒有 {MODEL}：先執行 `ollama pull {MODEL}`，並確認 {OLLAMA} 可連線")
    raw = [json.loads(line) for line in (REPO / "data" / "raw.jsonl").read_text(encoding="utf-8").splitlines()]
    cache_path = REPO / "data" / "paraphrase_cache.jsonl"
    cache = {}
    if cache_path.exists():
        for line in cache_path.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            cache[entry["key"]] = entry
    with cache_path.open("a", encoding="utf-8") as cf:
        for i, row in enumerate(raw):
            key = hashlib.sha1(f"{i}|{row['request_original']}".encode()).hexdigest()
            if key not in cache:
                text, ok = paraphrase(row["request_original"], row["surfaces"], seed=i)
                cache[key] = {"key": key, "text": text, "ok": ok}
                cf.write(json.dumps(cache[key], ensure_ascii=False) + "\n")
                cf.flush()  # 中斷後重跑可以從快取續跑
            row["request"], row["paraphrased"] = cache[key]["text"], cache[key]["ok"]
            if i % 100 == 0:
                print(f"{i}/{len(raw)}", file=sys.stderr)

    rows = finalize(raw)
    for split in SPLITS:
        items = [r for r in rows if r["split"] == split]
        (REPO / "data" / f"{split}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items), encoding="utf-8")
    manifest = {
        "version": "v1", "paraphrase_model": MODEL,
        "paraphrase_ok_rate": round(sum(r["paraphrased"] for r in raw) / len(raw), 4),
        "counts": {s: dict(Counter(r["category"] for r in rows if r["split"] == s)) for s in SPLITS},
        "dropped_by_finalize": len(raw) - len(rows),
    }
    (REPO / "data" / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
