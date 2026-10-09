"""Planner QLoRA 微調：unsloth 4-bit + LoRA，只對 assistant 段計算 loss，MLflow 全程記錄。

用法（WSL；先在 Windows 執行 ollama stop 釋放 VRAM）：
    smoke：uv run python train_qlora.py --run-name smoke --max-steps 20
    全量：uv run python train_qlora.py --run-name qlora-r16
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")  # MLflow 3.x 的 file store 需顯式開啟

import mlflow  # noqa: E402

from planner.prompt import build_messages, gold_text  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
INSTRUCTION_PART, RESPONSE_PART = "<|im_start|>user\n", "<|im_start|>assistant\n"  # Qwen 系列 chat template


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", required=True)
    ap.add_argument("--base", default="unsloth/Qwen3-4B-Instruct-2507")
    ap.add_argument("--max-seq-length", type=int, default=2048, help="超長樣本直接剔除，不截斷")
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--alpha", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--train-file", default="train", help="data/ 下的 train 檔名（不含 .jsonl），第二輪用 train_v2")
    ap.add_argument("--max-steps", type=int, default=-1, help="smoke 用；-1 = 跑滿 epochs")
    a = ap.parse_args()

    # unsloth 必須在 trl / transformers 之前 import（靠 monkey-patch 生效）
    from unsloth import FastLanguageModel  # noqa: I001
    from unsloth.chat_templates import train_on_responses_only
    from datasets import Dataset
    from transformers import EarlyStoppingCallback
    from trl import SFTConfig, SFTTrainer

    data_dir, out_dir = REPO / "data", REPO / "outputs" / "adapters" / a.run_name
    model, tok = FastLanguageModel.from_pretrained(a.base, max_seq_length=a.max_seq_length, load_in_4bit=True)
    model = FastLanguageModel.get_peft_model(
        model, r=a.rank, lora_alpha=a.alpha, lora_dropout=0.0,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth", random_state=42)

    # 不用 load_dataset("json")：Arrow 會把各樣本不同鍵的 args 合併成同一個 struct，
    # 缺的鍵補 null，gold JSON 會被污染。自己讀 JSONL，只把轉好的文字交給 Dataset。
    def load_text(split: str) -> Dataset:
        rows = [json.loads(line) for line in (data_dir / f"{split}.jsonl").read_text(encoding="utf-8").splitlines()]
        # 不直接 render sft_messages：此 template 會在最後一則 assistant 前補空的 <think></think>，
        # 推論的 generation prompt 卻沒有；改成「推論 prompt + gold」確保訓練與推論逐字一致。
        return Dataset.from_list([{"text": tok.apply_chat_template(build_messages(r), tokenize=False,
                                                                   add_generation_prompt=True)
                                   + gold_text(r["gold"]) + "<|im_end|>\n"} for r in rows])

    ds = {"train": load_text(a.train_file), "val": load_text("val")}
    sample_text = ds["train"][0]["text"]
    assert "<think>" not in sample_text, "訓練文字出現 <think>，與推論 prompt 不一致"
    print(sample_text)
    lengths = [len(tok(t).input_ids) for t in ds["train"]["text"]]
    print(f"train token 長度：max={max(lengths)}，p95={sorted(lengths)[int(len(lengths) * 0.95)]}")
    dropped = {}
    for split in ds:
        before = len(ds[split])
        ds[split] = ds[split].filter(lambda r: len(tok(r["text"]).input_ids) <= a.max_seq_length)
        dropped[split] = before - len(ds[split])

    mlflow.set_tracking_uri(f"file://{REPO / 'mlruns'}")
    mlflow.set_experiment("patent-planner")
    with mlflow.start_run(run_name=a.run_name):
        manifest = json.loads((data_dir / ("manifest_v2.json" if a.train_file == "train_v2" else "manifest.json")).read_text(encoding="utf-8"))
        mlflow.log_params({
            "base_model": a.base, "dataset_version": manifest["version"], "lora_rank": a.rank,
            "lora_alpha": a.alpha, "max_seq_length": a.max_seq_length, "epochs": a.epochs,
            "max_steps": a.max_steps, "train_samples": len(ds["train"]), "val_samples": len(ds["val"]),
            "dropped_overlong": json.dumps(dropped), "train_file": a.train_file, "train_sha256": _sha(data_dir / f"{a.train_file}.jsonl"),
            "chat_template_sha": hashlib.sha256((tok.chat_template or "").encode()).hexdigest()[:16],
        })
        trainer = SFTTrainer(
            model=model, processing_class=tok, train_dataset=ds["train"], eval_dataset=ds["val"],
            args=SFTConfig(
                output_dir=str(out_dir / "checkpoints"),
                per_device_train_batch_size=4, gradient_accumulation_steps=4,  # 有效 batch 16
                num_train_epochs=a.epochs, max_steps=a.max_steps,
                learning_rate=2e-4, lr_scheduler_type="cosine", warmup_steps=10, logging_steps=5,
                eval_strategy="steps" if a.max_steps > 0 else "epoch", eval_steps=10 if a.max_steps > 0 else None,
                save_strategy="steps" if a.max_steps > 0 else "epoch", save_steps=10 if a.max_steps > 0 else None,
                load_best_model_at_end=True, metric_for_best_model="eval_loss", greater_is_better=False,
                save_total_limit=2, per_device_eval_batch_size=4, prediction_loss_only=True,
                bf16=True, seed=42, report_to="mlflow",
            ),
            callbacks=[EarlyStoppingCallback(early_stopping_patience=1)],
        )
        trainer = train_on_responses_only(trainer, instruction_part=INSTRUCTION_PART, response_part=RESPONSE_PART)

        # masking fail-fast：response marker 對不上時，訓練照樣會跑，但會學錯東西
        labels = trainer.data_collator([trainer.train_dataset[0]])["labels"][0]
        masked, trained = int((labels == -100).sum()), int((labels != -100).sum())
        assert masked > 0 and trained > 0, f"loss masking 失效（masked={masked}, trained={trained}）"
        mlflow.log_metric("train_mask_ratio", round(masked / (masked + trained), 4))

        trainer.train()
        model.save_pretrained(str(out_dir))
        tok.save_pretrained(str(out_dir))
        print(f"TRAIN_OK adapter={out_dir}")


if __name__ == "__main__":
    main()
