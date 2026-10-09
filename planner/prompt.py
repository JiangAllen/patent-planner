"""Planner 的 prompt 組裝。訓練、baseline 與評估一律用這裡，確保三者看到同一份 prompt。"""
import json

from planner.tools import render_tools

SYSTEM_PROMPT = """你是專利答辯 Agent 的 Planner。根據使用者需求與「可用工具」，只輸出一個 JSON 物件，不要輸出任何其他文字。

輸出必須是以下三種之一：
1. 可以完成：{"action":"plan","steps":[{"id":"s1","tool":"工具名","args":{...},"depends_on":[]}]}
   - step id 依序為 s1、s2、s3…
   - args 的值可以是字面值，或用 "$s1.欄位" 引用前一步的回傳，例如 "$s1.cited_refs[0]"
   - 引用了哪一步，就必須把該 step id 列入 depends_on；彼此無相依的步驟 depends_on 為 []，可平行執行
   - 只使用完成需求所需的工具，只填需求中提到的參數
2. 缺少必要資訊：{"action":"clarify","missing":["缺少的參數名"]}
3. 可用工具無法完成需求：{"action":"refuse","reason":"no_capable_tool"}"""

FEWSHOT_CATEGORIES = ("dag", "clarify", "refuse")


def user_content(available_tools: list[str], request: str) -> str:
    return f"可用工具：\n{render_tools(available_tools)}\n\n需求：{request}"


def gold_text(gold: dict) -> str:
    return json.dumps(gold, ensure_ascii=False, separators=(",", ":"))


def build_messages(sample: dict, shots: list[dict] | None = None) -> list[dict]:
    """推論用 messages（不含答案）；shots 會以 user / assistant 輪次插在問題之前。"""
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for shot in shots or []:
        msgs.append({"role": "user", "content": user_content(shot["available_tools"], shot["request"])})
        msgs.append({"role": "assistant", "content": gold_text(shot["gold"])})
    msgs.append({"role": "user", "content": user_content(sample["available_tools"], sample["request"])})
    return msgs


def sft_messages(sample: dict) -> list[dict]:
    """訓練用 messages：zero-shot prompt 加上 gold 答案。"""
    return build_messages(sample) + [{"role": "assistant", "content": gold_text(sample["gold"])}]


def pick_shots(train_rows: list[dict]) -> list[dict]:
    """few-shot 範例：依檔案順序，取 dag / clarify / refuse 各第一筆，固定不變以利重現。"""
    return [next(r for r in train_rows if r["category"] == c) for c in FEWSHOT_CATEGORIES]
