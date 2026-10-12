"""端到端 demo：request → Planner（微調模型）→ Executor（mock tools）。

用法（WSL；先在 Windows 執行 ollama stop 釋放 VRAM）：
    uv run python demo.py "把 TW-2026-0412 的請求項 1 跟 OA-2026-0331 的第一件引證比對"
    uv run python demo.py "<request>" ../outputs/adapters/qlora-r16   # 換 adapter
"""
import json
import sys
import time
from pathlib import Path

from planner.executor import execute
from planner.prompt import build_messages
from planner.schema import parse_output, validate
from planner.tools import TOOLS

REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    request = sys.argv[1]
    adapter = sys.argv[2] if len(sys.argv) > 2 else str(REPO / "outputs" / "adapters" / "qlora-r16-v2")
    from unsloth import FastLanguageModel

    model, tok = FastLanguageModel.from_pretrained(adapter, max_seq_length=4096, load_in_4bit=True)
    FastLanguageModel.for_inference(model)
    sample = {"available_tools": list(TOOLS), "request": request}
    text = tok.apply_chat_template(build_messages(sample), tokenize=False, add_generation_prompt=True)
    enc = tok(text, return_tensors="pt", add_special_tokens=False).to("cuda")
    t0 = time.time()
    out = model.generate(**enc, max_new_tokens=512, do_sample=False)
    raw = tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    print(f"[Planner] 產生計畫（{time.time() - t0:.1f} 秒）")
    plan = parse_output(raw)
    if plan is None or validate(plan):
        print(f"計畫格式錯誤：{raw}")
        return
    print(json.dumps(plan, ensure_ascii=False, indent=1))
    if plan["action"] != "plan":
        print(f"[Agent] {'需要補充資訊：' + ', '.join(plan['missing']) if plan['action'] == 'clarify' else '無法完成此需求'}")
        return
    print("[Executor] 開始執行")
    execute(plan)
    print(f"[完成] 共 {len(plan['steps'])} 步")


if __name__ == "__main__":
    main()
