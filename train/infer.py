"""批次推論：zero-shot / few-shot / adapter，只輸出原始文字；評分在 Windows 端用 evaluation.analyze 做。

用法（WSL；先在 Windows 執行 ollama stop 釋放 VRAM）：
    uv run python infer.py --run-name zeroshot
    uv run python infer.py --run-name fewshot --shots 3
    uv run python infer.py --run-name qlora-r16 --model ../outputs/adapters/qlora-r16
"""
import argparse
import json
from pathlib import Path

from planner.prompt import build_messages, pick_shots

REPO = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", required=True)
    ap.add_argument("--model", default="unsloth/Qwen3-4B-Instruct-2507", help="HF model id 或 adapter 目錄")
    ap.add_argument("--shots", type=int, default=0, choices=[0, 3])
    ap.add_argument("--splits", nargs="+", default=["test_id", "test_ood"])
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="smoke 用；0 = 全部")
    a = ap.parse_args()

    from unsloth import FastLanguageModel  # 有 CUDA side-effect，放在 main 內讓 --help 不佔 GPU
    import torch

    model, tok = FastLanguageModel.from_pretrained(a.model, max_seq_length=4096, load_in_4bit=True)
    FastLanguageModel.for_inference(model)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    shots = pick_shots(load_jsonl(REPO / "data" / "train.jsonl")) if a.shots else None

    out_dir = REPO / "results" / "preds" / a.run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    for split in a.splits:
        rows = load_jsonl(REPO / "data" / f"{split}.jsonl")[: a.limit or None]
        with (out_dir / f"{split}.jsonl").open("w", encoding="utf-8") as f:
            for i in range(0, len(rows), a.batch_size):
                batch = rows[i:i + a.batch_size]
                texts = [tok.apply_chat_template(build_messages(r, shots), tokenize=False,
                                                 add_generation_prompt=True) for r in batch]
                enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
                with torch.no_grad():
                    gen = model.generate(**enc, max_new_tokens=512, do_sample=False)
                for r, g in zip(batch, gen[:, enc["input_ids"].shape[1]:]):
                    f.write(json.dumps({"id": r["id"], "raw": tok.decode(g, skip_special_tokens=True)},
                                       ensure_ascii=False) + "\n")
                print(f"{split} {min(i + a.batch_size, len(rows))}/{len(rows)}", flush=True)
    (out_dir / "meta.json").write_text(json.dumps(vars(a), ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
