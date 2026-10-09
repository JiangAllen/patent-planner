# 專利答辯 Agent Planner 微調 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 2026-10-16 二面前，完成一個以合成資料微調 Qwen3-4B 的專利答辯 Planner，含 baseline 對照、分層評估與 error analysis。

**Architecture:** 新 repo `patent-planner`，分成兩個執行環境。Windows 端放純 Python 套件（`planner/` 格式與 prompt、`datagen/` 資料生成、`evaluation/` 評分與報告），用 `uv run pytest` 測試。WSL 端放 GPU 工作（`train/`：QLoRA 訓練、批次推論、demo），以 path dependency 引用同一份 `planner` 套件，確保訓練、baseline、評估用的是同一份 prompt。

**Tech Stack:** Python 3.12、uv、pytest、matplotlib（Windows）；unsloth + TRL + MLflow（WSL）；Ollama `qwen2.5:7b-instruct`（資料改寫）。

**Spec:** `planning/specs/2026-10-09-foxconn-planner-design.md`

### 與 spec 的實作差異（刻意調整，非遺漏）

1. **Tool 清單放在 user turn，不放 system prompt。** few-shot 範例各自有不同的可用工具，放在 user turn 才能讓每個範例自成一體。system prompt 只放輸出規則，三個比較對象共用同一份。
2. **評估套件命名為 `evaluation/`，不用 `eval/`**，避免與 Python 內建 `eval` 混淆。需要 GPU 的推論放在 `train/infer.py`。
3. **Checkpoint 依 val loss 選擇**（`load_best_model_at_end`）。val 的 plan exact match 在訓練完成後另外跑一次，作為健全性檢查，不參與 checkpoint 選擇。
4. **`compare_claims` 直接收專利號**，所以 dag 模板改用「兩個獨立來源匯合」（例：`get_case` ∥ `get_office_action` → `compare_claims`）。這樣可以避免「要不要先 `get_patent`」兩種答案都合理的情況。

## Global Constraints

- Python `>=3.12`，套件與環境一律用 `uv`。
- 🔴 資料全為合成；不讀取、不引用 `Forsetai/Data-Pipeline/data/` 的任何案件，也不沿用 `patent-oa-qlora` adapter。
- Base model：`unsloth/Qwen3-4B-Instruct-2507`。4-bit QLoRA，LoRA r=16、alpha=32、lr 2e-4、有效 batch 16。
- 三個比較對象（zero-shot / few-shot / QLoRA）用同一份 `SYSTEM_PROMPT`，greedy decoding，`max_new_tokens=512`。
- 資料改寫只用本地 Ollama `qwen2.5:7b-instruct`，不呼叫外部 API。
- GPU 工作前，先在 Windows 執行 `ollama stop qwen2.5:7b-instruct` 並以 `ollama ps` 確認已清空（12GB VRAM，訓練與推論互斥）。
- 程式註解、docstring、輸出訊息用繁體中文；技術名詞保留英文。
- 報告中的每個數字都附上 n；95% CI 重疊時不宣稱改善。
- Repo 先設為 private，10/15 轉 public。
- Commit 採 Conventional Commits、繁體中文，結尾附 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`。

## Review Focus

1. 模型輸出被 ` ```json ` 圍欄包住或帶前後說明文字時，仍要擷取得到 JSON（Task 1 `test_parse_output_tolerates_fences_and_trailing_text`）。
2. 預測的 step 編號或平行順序跟 gold 不同，但計畫本身正確時，要判定為 exact（Task 5 `test_renumbered_and_reordered_plan_is_exact`）。
3. 改寫後的 `clarify` request 若被捏造出案號，必須退回原句，否則題目會從「缺資訊」變成「資訊完整」（Task 4 `test_rejects_invented_id_in_clarify`）。
4. val / test_id 的 request 若與 train 某一筆完全相同，必須剔除，否則 test_id 分數虛高（Task 3 `test_finalize_drops_duplicates_and_train_leakage`）。
5. 預測含循環引用時，評分器不能無窮遞迴，並要歸類為 format 錯誤（Task 5 `test_cycle_in_prediction_does_not_hang`）。

## 時程對照

| 日期 | Task |
|---|---|
| 10/9（五） | Task 1、Task 2；WSL 環境安裝（Task 6 Step 1）放背景跑 |
| 10/10（六） | Task 3（**Allen 審模板**）、Task 4 開跑改寫（背景約 1 小時）、Task 5 |
| 10/11（日） | Task 4 抽查、Task 6 baseline 推論、Task 7 報告 |
| 10/12（一） | Task 8 訓練與評估 |
| 10/13（二） | Task 9 error analysis。**主線完成線** |
| 10/14（三） | Task 10（optional demo）、Task 11 凍結結果 |
| 10/15（四） | 簡報與演練（另用 slides artifact 製作，不在本計畫內）；repo 轉 public |

---

### Task 1: Repo 初始化、工具定義與輸出格式驗證

**Files:**
- Create: `C:\Users\USER\Desktop\patent-planner\pyproject.toml`
- Create: `.gitignore`、`README.md`、`planner/__init__.py`、`datagen/__init__.py`、`evaluation/__init__.py`
- Create: `planner/tools.py`、`planner/schema.py`
- Create: `docs/design.md`、`docs/plan.md`（複製自 Data-Pipeline 的 spec 與本計畫）
- Test: `tests/test_schema.py`

**Interfaces:**
- Produces:
  - `planner.tools.TOOLS: dict[str, dict]`：鍵為工具名；值含 `desc: str`、`params: dict[str, tuple[str, bool]]`（型別、是否必填）、`returns: list[str]`
  - `planner.tools.render_tools(names: list[str]) -> str`
  - `planner.schema.REF_RE`：比對 `$s1.path`，group(1) 為 step id，group(2) 為路徑
  - `planner.schema.parse_output(text: str) -> dict | None`
  - `planner.schema.step_refs(step: dict) -> list[str]`
  - `planner.schema.validate(obj: dict, available_tools: list[str] | None = None, strict: bool = False) -> list[str]`：回傳錯誤訊息清單，空清單代表合法。非 strict 只檢查結構；strict 另外檢查工具存在、必填參數、引用欄位，以及引用是否列入 `depends_on`

- [ ] **Step 1: 建立 repo 骨架**

```powershell
New-Item -ItemType Directory -Force C:\Users\USER\Desktop\patent-planner\planner, C:\Users\USER\Desktop\patent-planner\datagen, C:\Users\USER\Desktop\patent-planner\evaluation, C:\Users\USER\Desktop\patent-planner\tests, C:\Users\USER\Desktop\patent-planner\docs, C:\Users\USER\Desktop\patent-planner\train, C:\Users\USER\Desktop\patent-planner\data
Copy-Item C:\Users\USER\Desktop\Forsetai\Data-Pipeline\planning\specs\2026-10-09-foxconn-planner-design.md C:\Users\USER\Desktop\patent-planner\docs\design.md
Copy-Item C:\Users\USER\Desktop\Forsetai\Data-Pipeline\planning\plans\2026-10-09-foxconn-planner-implementation.md C:\Users\USER\Desktop\patent-planner\docs\plan.md
```

`pyproject.toml`：

```toml
[project]
name = "patent-planner"
version = "0.1.0"
description = "專利答辯 Agent 的 Planner 微調（合成資料、Qwen3-4B QLoRA）"
requires-python = ">=3.12"
dependencies = ["matplotlib"]

[dependency-groups]
dev = ["pytest", "ruff"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["planner", "datagen", "evaluation"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`.gitignore`：

```gitignore
.venv/
__pycache__/
outputs/
mlruns/
*.pyc
```

`README.md`（之後在 Task 11 補完整）：

```markdown
# patent-planner

專利答辯 Agent 的 Planner 微調：以合成資料對 Qwen3-4B 做 QLoRA，並與 zero-shot / few-shot baseline 比較。設計見 `docs/design.md`。
```

三個 `__init__.py` 都是空檔。

- [ ] **Step 2: 寫失敗測試 `tests/test_schema.py`**

```python
from planner.schema import parse_output, validate
from planner.tools import render_tools

PLAN = {"action": "plan", "steps": [
    {"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
    {"id": "s2", "tool": "calc_deadline", "args": {"issue_date": "$s1.issue_date"}, "depends_on": ["s1"]},
]}


def test_parse_output_tolerates_fences_and_trailing_text():
    raw = '```json\n{"action":"refuse","reason":"no_capable_tool"}\n```\n以上。'
    assert parse_output(raw) == {"action": "refuse", "reason": "no_capable_tool"}


def test_parse_output_returns_none_on_garbage():
    assert parse_output("我不知道") is None
    assert parse_output('{"action": "plan", ') is None
    assert parse_output("[1, 2]") is None


def test_valid_plan_passes_strict():
    assert validate(PLAN, available_tools=["get_office_action", "calc_deadline"], strict=True) == []


def test_strict_rejects_tool_not_available():
    errs = validate(PLAN, available_tools=["get_office_action"], strict=True)
    assert any("calc_deadline" in e for e in errs)


def test_cycle_detected():
    bad = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_patent", "args": {"patent_no": "$s2.patent_no"}, "depends_on": ["s2"]},
        {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.patent_no"}, "depends_on": ["s1"]},
    ]}
    assert "相依關係有循環" in validate(bad)


def test_dangling_ref_detected():
    bad = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_patent", "args": {"patent_no": "$s9.patent_no"}, "depends_on": []},
    ]}
    assert any("s9" in e for e in validate(bad))


def test_strict_flags_ref_missing_from_depends_on_and_bad_field():
    bad = {"action": "plan", "steps": [
        PLAN["steps"][0],
        {"id": "s2", "tool": "calc_deadline", "args": {"issue_date": "$s1.deadline"}, "depends_on": []},
    ]}
    errs = validate(bad, strict=True)
    assert any("depends_on" in e for e in errs)
    assert any("deadline" in e for e in errs)


def test_strict_flags_missing_required_param():
    bad = {"action": "plan", "steps": [{"id": "s1", "tool": "amend_claims",
           "args": {"case_id": "TW-2026-0001", "claim_no": 1}, "depends_on": []}]}
    assert any("instruction" in e for e in validate(bad, strict=True))


def test_clarify_and_refuse_shapes():
    assert validate({"action": "clarify", "missing": ["oa_id"]}) == []
    assert validate({"action": "clarify", "missing": []}) != []
    assert validate({"action": "refuse", "reason": "no_capable_tool"}) == []
    assert validate({"action": "dance"}) != []
    assert validate({"action": "plan", "steps": []}) != []


def test_render_tools_marks_optional_params():
    text = render_tools(["search_prior_art"])
    assert "query: str" in text and "top_k?: int" in text and "results[].patent_no" in text
```

- [ ] **Step 3: 執行測試，確認失敗**

Run: `cd C:\Users\USER\Desktop\patent-planner; uv sync; uv run pytest tests/test_schema.py -v`
Expected: FAIL，出現 `ModuleNotFoundError: No module named 'planner.schema'`

- [ ] **Step 4: 實作 `planner/tools.py`**

```python
"""專利答辯 Agent 的 10 個 mock tool 定義。Planner 只看定義，不會真的執行。"""

# params：參數名 → (型別, 是否必填)
TOOLS: dict[str, dict] = {
    "get_case": {
        "desc": "取得案件資料",
        "params": {"case_id": ("str", True)},
        "returns": ["application_no", "claims", "oa_ids", "status"],
    },
    "get_office_action": {
        "desc": "取得審查意見通知書（OA）",
        "params": {"oa_id": ("str", True)},
        "returns": ["cited_refs", "rejected_claims", "grounds", "issue_date"],
    },
    "get_patent": {
        "desc": "取得專利全文",
        "params": {"patent_no": ("str", True)},
        "returns": ["patent_no", "title", "abstract", "claims"],
    },
    "search_prior_art": {
        "desc": "依關鍵字搜尋先前技術，結果依相關度排序",
        "params": {"query": ("str", True), "date_before": ("str", False), "top_k": ("int", False)},
        "returns": ["results[].patent_no"],
    },
    "compare_claims": {
        "desc": "比對請求項文字與一件引證專利",
        "params": {"claim_text": ("str", True), "reference_patent_no": ("str", True)},
        "returns": ["overlap", "distinguishing_features"],
    },
    "calc_deadline": {
        "desc": "依 OA 發文日計算答辯期限，可指定延長月數",
        "params": {"issue_date": ("str", True), "extension_months": ("int", False)},
        "returns": ["deadline"],
    },
    "amend_claims": {
        "desc": "依指示修正案件的某一項請求項",
        "params": {"case_id": ("str", True), "claim_no": ("int", True), "instruction": ("str", True)},
        "returns": ["amended_claim"],
    },
    "draft_response": {
        "desc": "撰寫答辯書草稿",
        "params": {"oa_id": ("str", True), "arguments": ("str", True), "amendments": ("str", False)},
        "returns": ["draft_id"],
    },
    "translate_text": {
        "desc": "翻譯文字；target_lang 用語言代碼（en、ja、de）",
        "params": {"text": ("str", True), "target_lang": ("str", True)},
        "returns": ["translated"],
    },
    "notify_client": {
        "desc": "傳訊息通知案件的客戶",
        "params": {"case_id": ("str", True), "message": ("str", True)},
        "returns": ["sent"],
    },
}


def render_tools(names: list[str]) -> str:
    """把工具定義轉成 prompt 用的文字，選填參數以 ? 標記。"""
    lines = []
    for name in names:
        tool = TOOLS[name]
        params = ", ".join(f"{p}{'' if req else '?'}: {typ}" for p, (typ, req) in tool["params"].items())
        lines.append(f"- {name}({params}) -> {{{', '.join(tool['returns'])}}}：{tool['desc']}")
    return "\n".join(lines)
```

- [ ] **Step 5: 實作 `planner/schema.py`**

```python
"""Planner 輸出的解析與格式驗證。"""
import json
import re

from planner.tools import TOOLS

REF_RE = re.compile(r"^\$(s\d+)\.(.+)$")
ACTIONS = {"plan", "clarify", "refuse"}


def parse_output(text: str) -> dict | None:
    """擷取輸出中的第一個 JSON 物件；容忍 ```json 圍欄與前後說明文字。失敗回傳 None。"""
    start = text.find("{")
    if start < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def step_refs(step: dict) -> list[str]:
    """回傳 step 的 args 中以 $sN.xxx 引用到的 step id。"""
    return [m.group(1) for v in step.get("args", {}).values()
            if isinstance(v, str) and (m := REF_RE.match(v))]


def _deps(step: dict) -> set[str]:
    return set(step["depends_on"]) | set(step_refs(step))


def _has_cycle(by_id: dict[str, dict]) -> bool:
    state: dict[str, int] = {}  # 1 = 走訪中，2 = 已完成

    def visit(sid: str) -> bool:
        if state.get(sid) == 1:
            return True
        if state.get(sid) == 2:
            return False
        state[sid] = 1
        if any(visit(d) for d in _deps(by_id[sid])):
            return True
        state[sid] = 2
        return False

    return any(visit(sid) for sid in by_id)


def _strict(steps: list[dict], by_id: dict[str, dict], available: list[str] | None) -> list[str]:
    errs = []
    for s in steps:
        tool = TOOLS.get(s["tool"])
        if tool is None:
            errs.append(f"{s['id']} 使用未知工具 {s['tool']}")
            continue
        if available is not None and s["tool"] not in available:
            errs.append(f"{s['id']} 使用不在可用清單的工具 {s['tool']}")
        for p, (_, required) in tool["params"].items():
            if required and p not in s["args"]:
                errs.append(f"{s['id']} 缺少必填參數 {p}")
        for p in s["args"]:
            if p not in tool["params"]:
                errs.append(f"{s['id']} 多出未定義參數 {p}")
        if not set(step_refs(s)) <= set(s["depends_on"]):
            errs.append(f"{s['id']} 的引用未列入 depends_on")
        for v in s["args"].values():
            m = REF_RE.match(v) if isinstance(v, str) else None
            if not m:
                continue
            target = TOOLS.get(by_id[m.group(1)]["tool"])
            field = re.match(r"[a-z_]*", m.group(2)).group(0)
            fields = {r.split("[")[0].split(".")[0] for r in target["returns"]} if target else set()
            if field not in fields:
                errs.append(f"{s['id']} 引用 {m.group(1)} 不存在的欄位 {field or m.group(2)}")
    return errs


def validate(obj: dict, available_tools: list[str] | None = None, strict: bool = False) -> list[str]:
    """回傳錯誤訊息清單；空清單代表合法。非 strict 只檢查結構。"""
    action = obj.get("action")
    if action not in ACTIONS:
        return [f"未知的 action：{action!r}"]
    if action == "clarify":
        missing = obj.get("missing")
        ok = isinstance(missing, list) and missing and all(isinstance(x, str) for x in missing)
        return [] if ok else ["clarify.missing 必須是非空字串陣列"]
    if action == "refuse":
        return [] if isinstance(obj.get("reason"), str) else ["refuse.reason 必須是字串"]

    steps = obj.get("steps")
    if not (isinstance(steps, list) and steps):
        return ["plan.steps 必須是非空陣列"]
    for s in steps:
        if not (isinstance(s, dict) and isinstance(s.get("id"), str) and isinstance(s.get("tool"), str)
                and isinstance(s.get("args"), dict) and isinstance(s.get("depends_on"), list)):
            return [f"step 結構錯誤：{s!r}"]
    ids = [s["id"] for s in steps]
    errs = [] if len(set(ids)) == len(ids) else ["step id 重複"]
    by_id = {s["id"]: s for s in steps}
    for s in steps:
        for d in s["depends_on"] + step_refs(s):
            if d not in by_id:
                errs.append(f"{s['id']} 引用不存在的 step {d}")
    if not errs and _has_cycle(by_id):
        errs.append("相依關係有循環")
    if strict and not errs:
        errs += _strict(steps, by_id, available_tools)
    return errs
```

- [ ] **Step 6: 執行測試，確認通過**

Run: `uv run pytest tests/test_schema.py -v`
Expected: 10 passed

- [ ] **Step 7: 初始化 git、建立 private repo 並 commit**

```powershell
cd C:\Users\USER\Desktop\patent-planner
git init -b main
git add .
git commit -m "feat: 專案骨架、工具定義與 Planner 輸出格式驗證" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
gh repo create JiangAllen/patent-planner --private --source . --push
```

---

### Task 2: Prompt 組裝（訓練、baseline、評估共用）

**Files:**
- Create: `planner/prompt.py`
- Test: `tests/test_prompt.py`

**Interfaces:**
- Consumes: `planner.tools.render_tools`
- Produces:
  - `planner.prompt.SYSTEM_PROMPT: str`
  - `user_content(available_tools: list[str], request: str) -> str`
  - `gold_text(gold: dict) -> str`：緊湊 JSON，保留中文
  - `build_messages(sample: dict, shots: list[dict] | None = None) -> list[dict]`：推論用，不含答案
  - `sft_messages(sample: dict) -> list[dict]`：訓練用，結尾附上 gold
  - `pick_shots(train_rows: list[dict]) -> list[dict]`：依檔案順序，取 `dag`、`clarify`、`refuse` 各第一筆

- [ ] **Step 1: 寫失敗測試 `tests/test_prompt.py`**

```python
from planner.prompt import SYSTEM_PROMPT, build_messages, gold_text, pick_shots, sft_messages

GOLD = {"action": "plan", "steps": [
    {"id": "s1", "tool": "get_patent", "args": {"patent_no": "I712345"}, "depends_on": []}]}
S = {"available_tools": ["get_patent", "notify_client"], "request": "調出 I712345",
     "gold": GOLD, "category": "single"}


def test_user_turn_lists_only_available_tools():
    m = build_messages(S)
    assert m[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert "get_patent(" in m[1]["content"] and "notify_client(" in m[1]["content"]
    assert "calc_deadline(" not in m[1]["content"]
    assert m[1]["content"].endswith("需求：調出 I712345")


def test_shots_precede_query():
    m = build_messages(S, [{**S, "request": "範例"}])
    assert [x["role"] for x in m] == ["system", "user", "assistant", "user"]
    assert m[2]["content"] == gold_text(GOLD)
    assert m[3]["content"].endswith("需求：調出 I712345")


def test_sft_ends_with_gold():
    assert sft_messages(S)[-1] == {"role": "assistant", "content": gold_text(GOLD)}
    assert len(sft_messages(S)) == 3


def test_pick_shots_one_per_category_in_file_order():
    rows = [{**S, "category": c, "id": f"x{i}"}
            for i, c in enumerate(["single", "dag", "clarify", "dag", "refuse"])]
    assert [r["id"] for r in pick_shots(rows)] == ["x1", "x2", "x4"]


def test_gold_text_is_compact_and_keeps_chinese():
    assert gold_text({"a": "中"}) == '{"a":"中"}'
```

- [ ] **Step 2: 執行測試，確認失敗**

Run: `uv run pytest tests/test_prompt.py -v`
Expected: FAIL，出現 `ModuleNotFoundError: No module named 'planner.prompt'`

- [ ] **Step 3: 實作 `planner/prompt.py`**

```python
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
```

- [ ] **Step 4: 執行測試，確認通過**

Run: `uv run pytest tests/test_prompt.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```powershell
git add planner/prompt.py tests/test_prompt.py
git commit -m "feat: 共用 prompt 組裝與 few-shot 範例選取" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: 結構模板與資料生成器

**Files:**
- Create: `datagen/templates.py`、`datagen/generate.py`
- Test: `tests/test_generate.py`

**Interfaces:**
- Consumes: `planner.tools.TOOLS`、`planner.schema.step_refs`、`planner.schema.validate`
- Produces:
  - `datagen.templates.TEMPLATES: list[dict]`，每筆含：
    - `id`、`category`、`requests: list[str]`、`holdout: bool`（選填）
    - plan 類：`steps: list[tuple[str, str, dict]]`
    - clarify / refuse 類：`needs: list[str]`
    - clarify 類另有 `missing: list[str]`；refuse 類另有 `drop: str | None`
  - `datagen.generate.SPLITS = ("train", "val", "test_id", "test_ood")`
  - `needed_tools(t: dict) -> list[str]`
  - `build_sample(t: dict, rng: random.Random) -> dict`：鍵為 `category`、`structure_id`、`available_tools`、`request`、`request_original`、`surfaces`、`gold`
  - `generate(seed=42, per_seen=100, per_ood=25) -> list[dict]`：每筆另含 `split`，尚未給 `id`
  - `finalize(rows: list[dict]) -> list[dict]`：在 split 內去重、剔除與 train 重複的 val / test_id，並給 `id`（`{split}-{nnnnn}`）
  - CLI：`uv run python -m datagen.generate` 會寫出 `data/raw.jsonl`

- [ ] **Step 1: 寫失敗測試 `tests/test_generate.py`**

```python
import random
import re
from collections import Counter

from datagen.generate import build_sample, finalize, generate, needed_tools
from datagen.templates import TEMPLATES
from planner.schema import validate
from planner.tools import TOOLS

SLOT_RE = re.compile(r"\{([A-Z0-9]+)\}")


def test_template_inventory():
    assert Counter(t["category"] for t in TEMPLATES) == {
        "single": 5, "parallel": 5, "chain": 7, "dag": 5, "clarify": 4, "refuse": 4}
    hold = [t for t in TEMPLATES if t.get("holdout")]
    assert Counter(t["category"] for t in hold) == {
        "parallel": 1, "chain": 2, "dag": 1, "clarify": 1, "refuse": 1}
    assert len({t["id"] for t in TEMPLATES}) == 30


def test_every_tool_is_seen_in_training_templates():
    seen = {tool for t in TEMPLATES if not t.get("holdout") for tool in needed_tools(t)}
    assert seen == set(TOOLS)


def test_arg_slots_appear_in_every_request_sentence():
    for t in TEMPLATES:
        arg_slots = {m for _, _, args in t.get("steps", []) for v in args.values()
                     if isinstance(v, str) for m in SLOT_RE.findall(v)}
        for sent in t["requests"]:
            assert arg_slots <= set(SLOT_RE.findall(sent)), (t["id"], sent)


def test_clarify_missing_names_are_real_params_of_needed_tools():
    for t in TEMPLATES:
        if t["category"] == "clarify":
            params = {p for n in t["needs"] for p in TOOLS[n]["params"]}
            assert set(t["missing"]) <= params, t["id"]


def test_generated_gold_is_valid_and_consistent():
    rng = random.Random(0)
    for t in TEMPLATES:
        for _ in range(5):
            s = build_sample(t, rng)
            assert all(x in s["request"] for x in s["surfaces"]), t["id"]
            assert len(s["available_tools"]) == len(set(s["available_tools"]))
            if t["category"] == "refuse":
                assert s["gold"] == {"action": "refuse", "reason": "no_capable_tool"}
                if t.get("drop"):
                    assert t["drop"] not in s["available_tools"]
                continue
            assert validate(s["gold"], s["available_tools"], strict=True) == [], t["id"]
            assert set(needed_tools(t)) <= set(s["available_tools"])
            assert 2 <= len(set(s["available_tools"]) - set(needed_tools(t))) <= 4


def test_generate_is_deterministic_and_splits_by_structure():
    a = generate(seed=1, per_seen=24, per_ood=5)
    assert a == generate(seed=1, per_seen=24, per_ood=5)
    ood_ids = {t["id"] for t in TEMPLATES if t.get("holdout")}
    for r in a:
        assert (r["split"] == "test_ood") == (r["structure_id"] in ood_ids)
    assert {r["split"] for r in a} == {"train", "val", "test_id", "test_ood"}


def test_finalize_drops_duplicates_and_train_leakage():
    base = {"category": "single", "structure_id": "S01", "available_tools": ["get_case"],
            "gold": {}, "surfaces": []}
    rows = [{**base, "split": "train", "request": "A"},
            {**base, "split": "train", "request": "A"},
            {**base, "split": "test_id", "request": "A"},
            {**base, "split": "test_id", "request": "B"},
            {**base, "split": "test_ood", "request": "A"}]
    out = finalize(rows)
    assert [(r["split"], r["request"]) for r in out] == [
        ("train", "A"), ("test_id", "B"), ("test_ood", "A")]
    assert [r["id"] for r in out] == ["train-00000", "test_id-00000", "test_ood-00000"]
```

- [ ] **Step 2: 執行測試，確認失敗**

Run: `uv run pytest tests/test_generate.py -v`
Expected: FAIL，出現 `ModuleNotFoundError: No module named 'datagen.templates'`

- [ ] **Step 3: 實作 `datagen/templates.py`（初稿，Step 7 交給 Allen 審稿）**

```python
"""30 個任務結構模板。

句型中的 {SLOT} 由 generate.py 填入：CASE 案號、OA 通知書號、PAT / PAT2 專利號、DATE 發文日、
CLAIM 請求項編號、MONTHS 延長月數、QUERY 技術主題、LANG 語言、MSG 訊息、INSTR 修正指示。
holdout=True 的 6 個結構只出現在 test_ood。
"""

TEMPLATES: list[dict] = [
    # ── single：1 個工具 ──
    {"id": "S01", "category": "single",
     "steps": [("s1", "get_case", {"case_id": "{CASE}"})],
     "requests": ["查一下 {CASE} 這件目前的狀態", "{CASE} 的案件資料幫我調出來",
                  "我想看 {CASE} 的請求項跟審查進度"]},
    {"id": "S02", "category": "single",
     "steps": [("s1", "get_office_action", {"oa_id": "{OA}"})],
     "requests": ["把 {OA} 這份審查意見通知書打開", "{OA} 的核駁理由是什麼？", "幫我讀一下 {OA} 的內容"]},
    {"id": "S03", "category": "single",
     "steps": [("s1", "get_patent", {"patent_no": "{PAT}"})],
     "requests": ["調出專利 {PAT} 的全文", "{PAT} 這件專利在講什麼？", "幫我查 {PAT} 的摘要和請求項"]},
    {"id": "S04", "category": "single",
     "steps": [("s1", "search_prior_art", {"query": "{QUERY}"})],
     "requests": ["搜尋跟{QUERY}有關的先前技術", "找一些{QUERY}的前案", "有沒有關於{QUERY}的既有專利？"]},
    {"id": "S05", "category": "single",
     "steps": [("s1", "calc_deadline", {"issue_date": "{DATE}"})],
     "requests": ["通知書是 {DATE} 發的，答辯期限是哪天？", "從 {DATE} 起算，幫我算答辯期限",
                  "發文日 {DATE}，最晚什麼時候要回覆？"]},

    # ── parallel：多個工具、彼此無相依 ──
    {"id": "S06", "category": "parallel",
     "steps": [("s1", "get_patent", {"patent_no": "{PAT}"}),
               ("s2", "get_patent", {"patent_no": "{PAT2}"})],
     "requests": ["把 {PAT} 和 {PAT2} 兩件專利都調出來", "同時查 {PAT}、{PAT2} 的內容",
                  "我需要 {PAT} 跟 {PAT2} 這兩篇的全文"]},
    {"id": "S07", "category": "parallel",
     "steps": [("s1", "get_case", {"case_id": "{CASE}"}),
               ("s2", "get_office_action", {"oa_id": "{OA}"})],
     "requests": ["調出 {CASE} 的案件資料，另外也打開 {OA}", "{CASE} 的狀態和 {OA} 的內容都給我看",
                  "同時查案件 {CASE} 跟通知書 {OA}"]},
    {"id": "S08", "category": "parallel",
     "steps": [("s1", "search_prior_art", {"query": "{QUERY}"}),
               ("s2", "get_patent", {"patent_no": "{PAT}"})],
     "requests": ["搜尋{QUERY}相關前案，順便調出 {PAT}", "幫我找{QUERY}的先前技術，另外把 {PAT} 的全文給我",
                  "兩件事：查 {PAT}，還有搜尋{QUERY}的前案"]},
    {"id": "S09", "category": "parallel",
     "steps": [("s1", "amend_claims", {"case_id": "{CASE}", "claim_no": "{CLAIM}", "instruction": "{INSTR}"}),
               ("s2", "notify_client", {"case_id": "{CASE}", "message": "{MSG}"})],
     "requests": ["把 {CASE} 的請求項 {CLAIM} 修正為「{INSTR}」，同時通知客戶「{MSG}」",
                  "{CASE} 請求項 {CLAIM} 要「{INSTR}」；另外跟客戶說「{MSG}」",
                  "通知 {CASE} 的客戶「{MSG}」，也順便把請求項 {CLAIM}「{INSTR}」"]},
    {"id": "S10", "category": "parallel", "holdout": True,
     "steps": [("s1", "calc_deadline", {"issue_date": "{DATE}"}),
               ("s2", "get_patent", {"patent_no": "{PAT}"})],
     "requests": ["算一下 {DATE} 發文的答辯期限，另外調出 {PAT}",
                  "{PAT} 的全文給我，還有 {DATE} 那份通知的期限是哪天",
                  "兩件事：查 {PAT}；算 {DATE} 起算的答辯期限"]},

    # ── chain：串接 ──
    {"id": "S11", "category": "chain",
     "steps": [("s1", "get_office_action", {"oa_id": "{OA}"}),
               ("s2", "calc_deadline", {"issue_date": "$s1.issue_date"})],
     "requests": ["幫我算 {OA} 的答辯期限", "{OA} 最晚什麼時候要回？", "讀 {OA}，然後算出答辯期限"]},
    {"id": "S12", "category": "chain",
     "steps": [("s1", "get_office_action", {"oa_id": "{OA}"}),
               ("s2", "get_patent", {"patent_no": "$s1.cited_refs[0]"})],
     "requests": ["{OA} 引用的第一篇前案幫我調出來", "打開 {OA} 第一件引證的全文",
                  "{OA} 裡第一個引證專利是什麼內容？"]},
    {"id": "S13", "category": "chain",
     "steps": [("s1", "get_case", {"case_id": "{CASE}"}),
               ("s2", "get_office_action", {"oa_id": "$s1.oa_ids[0]"}),
               ("s3", "calc_deadline", {"issue_date": "$s2.issue_date"})],
     "requests": ["{CASE} 第一份通知書的答辯期限是哪天？", "查 {CASE} 的第一份審查意見，算出答辯期限",
                  "{CASE} 收到的第一份 OA 最晚何時要答辯？"]},
    {"id": "S14", "category": "chain",
     "steps": [("s1", "search_prior_art", {"query": "{QUERY}"}),
               ("s2", "get_patent", {"patent_no": "$s1.results[0].patent_no"})],
     "requests": ["搜尋{QUERY}的前案，把最相關那篇的全文給我", "找{QUERY}相關專利，打開排第一的那篇",
                  "{QUERY}的先前技術裡最相關的一篇，幫我調全文"]},
    {"id": "S15", "category": "chain",
     "steps": [("s1", "get_patent", {"patent_no": "{PAT}"}),
               ("s2", "translate_text", {"text": "$s1.abstract", "target_lang": "{LANG}"})],
     "requests": ["把 {PAT} 的摘要翻成{LANG}", "{PAT} 的摘要給我{LANG}版本", "調出 {PAT}，摘要翻譯成{LANG}"]},
    {"id": "S16", "category": "chain", "holdout": True,
     "steps": [("s1", "get_office_action", {"oa_id": "{OA}"}),
               ("s2", "calc_deadline", {"issue_date": "$s1.issue_date", "extension_months": "{MONTHS}"}),
               ("s3", "notify_client", {"case_id": "{CASE}", "message": "$s2.deadline"})],
     "requests": ["算出 {OA} 延長 {MONTHS} 個月後的答辯期限，再通知 {CASE} 的客戶",
                  "{OA} 申請延期 {MONTHS} 個月，新的期限算好後告訴 {CASE} 的客戶",
                  "幫 {CASE} 的客戶算 {OA} 延 {MONTHS} 個月的期限並通知他們"]},
    {"id": "S17", "category": "chain", "holdout": True,
     "steps": [("s1", "get_patent", {"patent_no": "{PAT}"}),
               ("s2", "translate_text", {"text": "$s1.abstract", "target_lang": "{LANG}"}),
               ("s3", "notify_client", {"case_id": "{CASE}", "message": "$s2.translated"})],
     "requests": ["把 {PAT} 的摘要翻成{LANG}，寄給 {CASE} 的客戶",
                  "{PAT} 摘要的{LANG}翻譯做好後通知 {CASE} 的客戶",
                  "翻譯 {PAT} 的摘要成{LANG}並傳給 {CASE} 客戶"]},

    # ── dag：多個來源匯合 ──
    {"id": "S18", "category": "dag",
     "steps": [("s1", "get_case", {"case_id": "{CASE}"}),
               ("s2", "get_office_action", {"oa_id": "{OA}"}),
               ("s3", "compare_claims", {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"})],
     "requests": ["把 {CASE} 的請求項 1 跟 {OA} 的第一件引證比對",
                  "{OA} 引用的第一篇前案，和 {CASE} 請求項 1 差在哪？",
                  "比較 {CASE} 第一項請求項與 {OA} 第一件引證"]},
    {"id": "S19", "category": "dag",
     "steps": [("s1", "get_case", {"case_id": "{CASE}"}),
               ("s2", "search_prior_art", {"query": "{QUERY}"}),
               ("s3", "compare_claims",
                {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"})],
     "requests": ["搜尋{QUERY}的前案，拿最相關那篇跟 {CASE} 的請求項 1 比對",
                  "{CASE} 請求項 1 跟{QUERY}領域最相近的前案比一下",
                  "找{QUERY}的先前技術，用第一名跟 {CASE} 第一項請求項做比對"]},
    {"id": "S20", "category": "dag",
     "steps": [("s1", "get_case", {"case_id": "{CASE}"}),
               ("s2", "get_office_action", {"oa_id": "{OA}"}),
               ("s3", "compare_claims", {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}),
               ("s4", "draft_response", {"oa_id": "{OA}", "arguments": "$s3.distinguishing_features"})],
     "requests": ["比對 {CASE} 請求項 1 和 {OA} 的第一件引證，再根據差異擬答辯書",
                  "{OA} 要答辯：拿 {CASE} 的請求項 1 跟第一件引證比，用找到的差異寫草稿",
                  "幫 {OA} 寫答辯書，論點用 {CASE} 請求項 1 與第一件引證的區別特徵"]},
    {"id": "S21", "category": "dag",
     "steps": [("s1", "get_patent", {"patent_no": "{PAT}"}),
               ("s2", "search_prior_art", {"query": "{QUERY}"}),
               ("s3", "compare_claims",
                {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.results[0].patent_no"})],
     "requests": ["把專利 {PAT} 的請求項 1 和{QUERY}最相關的前案比對",
                  "搜尋{QUERY}前案，取第一名跟 {PAT} 的第一項請求項比較",
                  "{PAT} 請求項 1 與{QUERY}領域排名第一的前案差在哪？"]},
    {"id": "S22", "category": "dag", "holdout": True,
     "steps": [("s1", "get_office_action", {"oa_id": "{OA}"}),
               ("s2", "amend_claims", {"case_id": "{CASE}", "claim_no": "{CLAIM}", "instruction": "{INSTR}"}),
               ("s3", "draft_response",
                {"oa_id": "{OA}", "arguments": "$s1.grounds", "amendments": "$s2.amended_claim"})],
     "requests": ["{OA} 要答辯：把 {CASE} 請求項 {CLAIM} 修正為「{INSTR}」，再針對核駁理由擬答辯書",
                  "先修正 {CASE} 的請求項 {CLAIM}（{INSTR}），然後依 {OA} 的核駁理由寫答辯書",
                  "幫 {OA} 準備答辯書，附上 {CASE} 請求項 {CLAIM} 的修正：{INSTR}"]},

    # ── clarify：缺必要資訊 ──
    {"id": "S23", "category": "clarify", "needs": ["get_office_action", "calc_deadline"], "missing": ["oa_id"],
     "requests": ["這份通知書的答辯期限幫我算一下", "幫我算審查意見通知書的答辯期限", "通知書最晚什麼時候要回覆？"]},
    {"id": "S24", "category": "clarify", "needs": ["get_patent"], "missing": ["patent_no"],
     "requests": ["幫我調出那篇引證專利的全文", "把那件專利的摘要給我", "查一下這件專利在講什麼"]},
    {"id": "S25", "category": "clarify", "needs": ["notify_client"], "missing": ["case_id"],
     "requests": ["通知客戶「{MSG}」", "跟客戶說一聲「{MSG}」", "幫我發訊息給客戶：「{MSG}」"]},
    {"id": "S26", "category": "clarify", "holdout": True, "needs": ["get_case", "compare_claims"],
     "missing": ["case_id", "reference_patent_no"],
     "requests": ["把我們的請求項 1 跟前案比對一下", "請求項 1 和引證案差在哪？", "幫我比對本案請求項 1 與先前技術"]},

    # ── refuse：做不到 ──
    {"id": "S27", "category": "refuse", "needs": [], "drop": None,
     "requests": ["{CASE} 的年費幫我繳掉", "幫 {CASE} 辦理年費減免", "把 {CASE} 的專利證書寄到客戶公司"]},
    {"id": "S28", "category": "refuse", "needs": ["get_patent", "translate_text"], "drop": "translate_text",
     "requests": ["把 {PAT} 的摘要翻成{LANG}", "{PAT} 的摘要給我{LANG}版本", "調出 {PAT}，摘要翻譯成{LANG}"]},
    {"id": "S29", "category": "refuse", "needs": [], "drop": None,
     "requests": ["幫我跟審查委員約面詢時間", "{OA} 直接幫我提行政訴訟", "查一下 {PAT} 的專利權人電話"]},
    {"id": "S30", "category": "refuse", "holdout": True, "needs": ["get_office_action", "calc_deadline"],
     "drop": "calc_deadline",
     "requests": ["幫我算 {OA} 的答辯期限", "{OA} 最晚什麼時候要回？", "讀 {OA}，然後算出答辯期限"]},
]
```

> S28 / S30 刻意與 S15 / S11 共用句型：句子相同，但因為可用工具不同，正確答案也不同。這能檢驗模型是否真的有看工具清單。

- [ ] **Step 4: 實作 `datagen/generate.py`**

```python
"""依模板反向生成資料：先決定答案（gold），再填出題目（request）。"""
import json
import random
from pathlib import Path

from datagen.templates import TEMPLATES
from planner.schema import step_refs
from planner.tools import TOOLS

SPLITS = ("train", "val", "test_id", "test_ood")
TOPICS = ["散熱鰭片", "晶圓級封裝", "矽穿孔", "扇出型封裝", "焊球陣列", "電磁屏蔽層", "覆晶接合", "封裝基板"]
LANGS = [("en", "英文"), ("ja", "日文"), ("de", "德文")]
MSGS = ["答辯書草稿已完成，請確認", "審查意見通知書已收到", "答辯期限即將到期", "修正本已送出"]
INSTRS = ["加入散熱鰭片的結構限定", "刪除重複的附屬項敘述", "限定封裝層厚度小於 50 微米"]
REPO = Path(__file__).resolve().parents[1]


def sample_slots(rng: random.Random) -> dict[str, tuple]:
    """回傳 slot 名 → (填入 args 的值, 出現在句子裡的字面)。"""
    year = rng.choice([2025, 2026])
    pat, pat2 = rng.sample(range(700000, 800000), 2)
    claim, months = rng.randint(1, 20), rng.randint(1, 3)
    plain = {
        "CASE": f"TW-{year}-{rng.randint(1, 9999):04d}",
        "OA": f"OA-{year}-{rng.randint(1, 9999):04d}",
        "PAT": f"I{pat}", "PAT2": f"I{pat2}",
        "DATE": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
        "QUERY": rng.choice(TOPICS), "MSG": rng.choice(MSGS), "INSTR": rng.choice(INSTRS),
    }
    slots = {k: (v, v) for k, v in plain.items()}
    slots["CLAIM"] = (claim, str(claim))
    slots["MONTHS"] = (months, str(months))
    slots["LANG"] = rng.choice(LANGS)
    return slots


def needed_tools(t: dict) -> list[str]:
    return [tool for _, tool, _ in t["steps"]] if "steps" in t else list(t["needs"])


def _fill_arg(v, slots):
    if isinstance(v, str) and v.startswith("{") and v.endswith("}") and v[1:-1] in slots:
        return slots[v[1:-1]][0]
    return v


def build_gold(t: dict, slots: dict) -> dict:
    if t["category"] == "clarify":
        return {"action": "clarify", "missing": list(t["missing"])}
    if t["category"] == "refuse":
        return {"action": "refuse", "reason": "no_capable_tool"}
    steps = []
    for sid, tool, args in t["steps"]:
        step = {"id": sid, "tool": tool, "args": {k: _fill_arg(v, slots) for k, v in args.items()}}
        step["depends_on"] = sorted(set(step_refs(step)))
        steps.append(step)
    return {"action": "plan", "steps": steps}


def build_sample(t: dict, rng: random.Random) -> dict:
    slots = sample_slots(rng)
    sentence = rng.choice(t["requests"])
    used = [k for k in slots if "{" + k + "}" in sentence]
    request = sentence.format(**{k: v[1] for k, v in slots.items()})
    drop = t.get("drop")
    needed = sorted(set(needed_tools(t)) - {drop})
    others = [n for n in TOOLS if n not in needed and n != drop]
    tools = needed + rng.sample(others, min(len(others), rng.randint(2, 4)))
    rng.shuffle(tools)
    return {"category": t["category"], "structure_id": t["id"], "available_tools": tools,
            "request": request, "request_original": request,
            "surfaces": [slots[k][1] for k in used], "gold": build_gold(t, slots)}


def generate(seed: int = 42, per_seen: int = 100, per_ood: int = 25) -> list[dict]:
    """已見結構切成 train / val / test_id（約 1/12 val、1/16 test_id）；holdout 結構全進 test_ood。"""
    rng = random.Random(seed)
    seen, ood = [], []
    for t in TEMPLATES:
        if t.get("holdout"):
            ood += [build_sample(t, rng) for _ in range(per_ood)]
        else:
            seen += [build_sample(t, rng) for _ in range(per_seen)]
    rng.shuffle(seen)
    n_val, n_test = len(seen) // 12, len(seen) // 16
    parts = {"val": seen[:n_val], "test_id": seen[n_val:n_val + n_test],
             "train": seen[n_val + n_test:], "test_ood": ood}
    return [{**r, "split": split} for split in SPLITS for r in parts[split]]


def finalize(rows: list[dict]) -> list[dict]:
    """改寫完成後呼叫：split 內去重、剔除 request 與 train 相同的 val / test_id，最後給 id。"""
    train_reqs = {r["request"] for r in rows if r["split"] == "train"}
    out = []
    for split in SPLITS:
        keys = set()
        for r in rows:
            if r["split"] != split:
                continue
            key = (r["request"], tuple(sorted(r["available_tools"])))
            if key in keys or (split in ("val", "test_id") and r["request"] in train_reqs):
                continue
            keys.add(key)
            out.append({"id": f"{split}-{len(keys) - 1:05d}", **r})
    return out


def main() -> None:
    rows = generate()
    path = REPO / "data" / "raw.jsonl"
    path.parent.mkdir(exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    counts = {s: sum(r["split"] == s for r in rows) for s in SPLITS}
    print(f"寫出 {len(rows)} 筆到 {path}：{counts}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 執行測試，確認通過**

Run: `uv run pytest tests/test_generate.py -v`
Expected: 7 passed

- [ ] **Step 6: 產生原始資料，檢查筆數**

Run: `uv run python -m datagen.generate`
Expected: `寫出 2550 筆到 ...data\raw.jsonl：{'train': 2050, 'val': 200, 'test_id': 150, 'test_ood': 150}`

- [ ] **Step 7: 🔶 Allen 審模板（人工檢查點）**

請 Allen 以專利工程師的角度審 `datagen/templates.py`。檢查重點：

1. 每個句型是否像真實工作中會說的話。
2. 句子的意思是否**只能**對應到該模板的 steps，不會有第二種合理的計畫。
3. clarify 的句子是否真的缺少 `missing` 列出的參數。

修改後重跑 Step 5 與 Step 6，測試必須維持全綠。

- [ ] **Step 8: Commit**

```powershell
git add datagen tests/test_generate.py
git commit -m "feat: 30 個結構模板與反向資料生成器" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

`data/raw.jsonl` 是中間產物，在 Task 4 與最終資料集一起 commit。

---

### Task 4: Ollama 改寫、品質檢查與資料集定版

**Files:**
- Create: `datagen/paraphrase.py`、`datagen/spot_check.py`
- Test: `tests/test_paraphrase.py`
- Output: `data/{train,val,test_id,test_ood}.jsonl`、`data/manifest.json`、`data/paraphrase_cache.jsonl`、`reports/spot_check.md`

**Interfaces:**
- Consumes: `datagen.generate.finalize`、`datagen.generate.SPLITS`
- Produces:
  - `check_paraphrase(original: str, candidate: str, surfaces: list[str]) -> bool`
  - `paraphrase(text: str, surfaces: list[str], seed: int, fn=None, retries: int = 3, sleep=time.sleep) -> tuple[str, bool]`：回傳 (文字, 是否為成功的改寫)；失敗時退回原句
  - 最終 JSONL 每筆的欄位：`id`、`category`、`structure_id`、`available_tools`、`request`、`request_original`、`surfaces`、`gold`、`split`、`paraphrased`

- [ ] **Step 1: 寫失敗測試 `tests/test_paraphrase.py`**

```python
from datagen.paraphrase import check_paraphrase, paraphrase

ORIG = "讀 OA-2026-0331，把第一件引證案跟被駁回的第一項請求項比對"
GOOD = "OA-2026-0331 的第一件引證，請和被駁回的第一項請求項對照看看"


def test_accepts_faithful_rewrite():
    assert check_paraphrase(ORIG, GOOD, ["OA-2026-0331"])


def test_rejects_dropped_value():
    assert not check_paraphrase(ORIG, "把那份通知書的第一件引證拿來跟請求項比對", ["OA-2026-0331"])


def test_rejects_invented_id_in_clarify():
    assert not check_paraphrase("幫我算審查意見通知書的答辯期限", "幫我算 OA-2026-0001 的答辯期限", [])


def test_rejects_multiline_and_length_outliers():
    assert not check_paraphrase(ORIG, "第一行\n第二行 OA-2026-0331 的第一件引證比對", ["OA-2026-0331"])
    assert not check_paraphrase(ORIG, "OA-2026-0331", ["OA-2026-0331"])


def test_falls_back_to_original_when_backend_fails():
    def boom(text, seed):
        raise ConnectionError("down")
    assert paraphrase(ORIG, ["OA-2026-0331"], seed=0, fn=boom, sleep=lambda s: None) == (ORIG, False)


def test_retries_until_valid():
    outs = iter(["壞掉", GOOD])
    text, ok = paraphrase(ORIG, ["OA-2026-0331"], seed=0, fn=lambda t, s: next(outs), sleep=lambda s: None)
    assert ok and text == GOOD
```

- [ ] **Step 2: 執行測試，確認失敗**

Run: `uv run pytest tests/test_paraphrase.py -v`
Expected: FAIL，出現 `ModuleNotFoundError: No module named 'datagen.paraphrase'`

- [ ] **Step 3: 實作 `datagen/paraphrase.py`**

```python
"""用本地 Ollama 改寫 request，並以程式檢查改寫沒有改動參數值、也沒有捏造編號。"""
import hashlib
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

from datagen.generate import SPLITS, finalize

REPO = Path(__file__).resolve().parents[1]
OLLAMA = "http://localhost:11434"
MODEL = "qwen2.5:7b-instruct"
ID_RE = re.compile(r"OA-\d{4}-\d{4}|TW-\d{4}-\d{4}|I\d{6}|\d{4}-\d{2}-\d{2}")
PROMPT = """把下面這句專利事務所內部的工作指示，改寫成另一種自然的繁體中文說法。
規則：意思完全不變；所有編號、日期、數字、「」內的文字必須原樣保留；不可新增任何編號或資訊；只輸出改寫後的一句話。
原句：{text}"""


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
            candidate = fn(text, seed * 10 + i)
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
```

- [ ] **Step 4: 執行測試，確認通過**

Run: `uv run pytest tests/test_paraphrase.py -v`
Expected: 6 passed

- [ ] **Step 5: 確認 Ollama 可用，背景執行改寫（約 1 小時）**

Ollama 在規劃階段曾經沒有回應（`ollama list` 卡住），所以先確認：

```powershell
ollama list            # 應列出 qwen2.5:7b-instruct；若卡住，從系統匣重啟 Ollama
ollama pull qwen2.5:7b-instruct   # 若清單中沒有
uv run python -m datagen.paraphrase
```

Expected：stderr 每 100 筆輸出一次進度，最後印出 manifest。

- `paraphrase_ok_rate` **≥ 0.8**。若低於 0.8，先看 `paraphrase_cache.jsonl` 中 `ok: false` 的樣本是哪一種檢查沒過，調整 `PROMPT` 後刪掉快取重跑。
- `counts` 中 test_id 的 clarify 數量可能偏少（句型沒有 slot，改寫後容易與 train 撞句被剔除），如實記錄即可。

- [ ] **Step 6: 實作 `datagen/spot_check.py`，產生抽查表**

```python
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
```

Run: `uv run python -m datagen.spot_check`

- [ ] **Step 7: 🔶 Allen 抽查（人工檢查點，約 30 分鐘）**

Allen 在 `reports/spot_check.md` 逐筆標記，最後在檔尾寫上：「語意偏移率 = ❌ 筆數 / 90」。

如果偏移率超過 10%，找出最常見的偏移型態，調整 `PROMPT`，或為該型態加一條程式檢查，然後重跑 Step 5。

- [ ] **Step 8: Commit 資料集 v1**

```powershell
git add datagen/paraphrase.py datagen/spot_check.py tests/test_paraphrase.py data reports/spot_check.md
git commit -m "feat: Ollama 改寫與品質檢查，資料集 v1 定版" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: 評分器（正規化 + L0–L5 指標 + 錯誤分類 + bootstrap CI）

**Files:**
- Create: `evaluation/score.py`
- Test: `tests/test_score.py`

**Interfaces:**
- Consumes: `planner.schema.REF_RE`、`planner.schema.validate`
- Produces:
  - `canonical_steps(plan: dict) -> dict[str, str]`
  - `score_sample(gold: dict, pred: dict | None) -> dict`，鍵為：
    - `parse_ok`、`schema_ok`、`action_ok`、`pred_action`（`plan` / `clarify` / `refuse` / `invalid`）、`exact`
    - `tool_tp`、`tool_fp`、`tool_fn`、`distractor`
    - `lit_ok`、`lit_n`、`ref_ok`、`ref_n`
    - `deps_ok`（gold 非 plan 時為 `None`）
  - `classify_errors(gold: dict, pred: dict | None, m: dict) -> list[str]`：tag 為 `format`、`hallucinated_args`、`over_refuse`、`over_clarify`、`missed_refuse`、`wrong_missing`、`distractor`、`missing_step`、`extra_step`、`literal_arg`、`ref_arg`、`dependency`、`other` 之一或多個；exact 時回傳 `[]`
  - `bootstrap_ci(values: list[float], n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]`：(平均, 下界, 上界)

- [ ] **Step 1: 寫失敗測試 `tests/test_score.py`**

```python
from copy import deepcopy

from evaluation.score import bootstrap_ci, canonical_steps, classify_errors, score_sample

GOLD = {"action": "plan", "steps": [
    {"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-0412"}, "depends_on": []},
    {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
    {"id": "s3", "tool": "compare_claims",
     "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"},
     "depends_on": ["s1", "s2"]},
]}


def test_identical_plan_is_exact():
    m = score_sample(GOLD, deepcopy(GOLD))
    assert m["exact"] and m["tool_tp"] == 3 and m["lit_ok"] == 2 and m["ref_ok"] == 2


def test_renumbered_and_reordered_plan_is_exact():
    pred = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
        {"id": "s3", "tool": "compare_claims",
         "args": {"claim_text": "$s2.claims[0]", "reference_patent_no": "$s1.cited_refs[0]"},
         "depends_on": ["s2", "s1"]},
        {"id": "s2", "tool": "get_case", "args": {"case_id": "TW-2026-0412"}, "depends_on": []},
    ]}
    m = score_sample(GOLD, pred)
    assert m["exact"] and m["deps_ok"]
    assert classify_errors(GOLD, pred, m) == []


def test_int_and_str_literals_compare_equal():
    gold = {"action": "plan", "steps": [{"id": "s1", "tool": "amend_claims",
            "args": {"case_id": "TW-2026-0001", "claim_no": 3, "instruction": "x"}, "depends_on": []}]}
    pred = deepcopy(gold)
    pred["steps"][0]["args"]["claim_no"] = "3"
    assert score_sample(gold, pred)["exact"]


def test_wrong_ref_path_is_ref_arg_error():
    pred = deepcopy(GOLD)
    pred["steps"][2]["args"]["claim_text"] = "$s1.claim[0]"
    m = score_sample(GOLD, pred)
    assert not m["exact"] and m["ref_ok"] == 1 and m["ref_n"] == 2
    assert classify_errors(GOLD, pred, m) == ["ref_arg"]


def test_distractor_and_missing_step():
    pred = deepcopy(GOLD)
    pred["steps"][0] = {"id": "s1", "tool": "get_patent", "args": {"patent_no": "TW-2026-0412"}, "depends_on": []}
    m = score_sample(GOLD, pred)
    tags = classify_errors(GOLD, pred, m)
    assert m["distractor"] and {"distractor", "missing_step"} <= set(tags)


def test_missing_dependency_edge():
    pred = deepcopy(GOLD)
    pred["steps"][2]["args"]["reference_patent_no"] = "I700001"
    pred["steps"][2]["depends_on"] = ["s1"]
    m = score_sample(GOLD, pred)
    assert not m["deps_ok"] and {"ref_arg", "dependency"} <= set(classify_errors(GOLD, pred, m))


def test_cycle_in_prediction_does_not_hang():
    pred = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_patent", "args": {"patent_no": "$s2.patent_no"}, "depends_on": ["s2"]},
        {"id": "s2", "tool": "get_patent", "args": {"patent_no": "$s1.patent_no"}, "depends_on": ["s1"]},
    ]}
    m = score_sample(GOLD, pred)
    assert not m["schema_ok"] and classify_errors(GOLD, pred, m) == ["format"]
    assert "<cycle" in "".join(canonical_steps(pred).values())


def test_clarify_scoring():
    gold = {"action": "clarify", "missing": ["oa_id"]}
    assert score_sample(gold, {"action": "clarify", "missing": ["oa_id"]})["exact"]
    pred = {"action": "clarify", "missing": ["issue_date"]}
    m = score_sample(gold, pred)
    assert not m["exact"] and classify_errors(gold, pred, m) == ["wrong_missing"]
    assert m["deps_ok"] is None


def test_action_confusions():
    clarify = {"action": "clarify", "missing": ["oa_id"]}
    refuse = {"action": "refuse", "reason": "no_capable_tool"}
    plan = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0001"}, "depends_on": []}]}
    assert classify_errors(clarify, plan, score_sample(clarify, plan)) == ["hallucinated_args"]
    assert classify_errors(GOLD, refuse, score_sample(GOLD, refuse)) == ["over_refuse"]
    assert classify_errors(GOLD, clarify, score_sample(GOLD, clarify)) == ["over_clarify"]
    assert classify_errors(refuse, plan, score_sample(refuse, plan)) == ["missed_refuse"]


def test_unparseable_prediction():
    m = score_sample(GOLD, None)
    assert not m["parse_ok"] and m["pred_action"] == "invalid"
    assert m["tool_fn"] == 3 and m["ref_n"] == 2 and m["lit_n"] == 2 and m["deps_ok"] is False
    assert classify_errors(GOLD, None, m) == ["format"]


def test_bootstrap_ci_brackets_mean():
    mean, lo, hi = bootstrap_ci([1.0] * 30 + [0.0] * 10)
    assert mean == 0.75 and lo <= mean <= hi and hi - lo > 0
```

- [ ] **Step 2: 執行測試，確認失敗**

Run: `uv run pytest tests/test_score.py -v`
Expected: FAIL，出現 `ModuleNotFoundError: No module named 'evaluation.score'`

- [ ] **Step 3: 實作 `evaluation/score.py`**

```python
"""Planner 輸出的評分：正規化比對、分層指標、錯誤分類與 bootstrap 信賴區間。"""
import random
from collections import Counter

from planner.schema import REF_RE, validate


def _is_ref(v) -> bool:
    return isinstance(v, str) and REF_RE.match(v) is not None


class Canon:
    """把 step 的 $sN 引用遞迴展開成不依賴編號的字串；循環引用以 <cycle> 標記，不會無窮遞迴。"""

    def __init__(self, steps: list[dict]):
        self.by_id = {s.get("id"): s for s in steps}
        self.memo: dict[str, str] = {}

    def step(self, sid: str, stack: tuple = ()) -> str:
        if sid in self.memo:
            return self.memo[sid]
        if sid in stack:
            return f"<cycle:{sid}>"
        if sid not in self.by_id:
            return f"<missing:{sid}>"
        s = self.by_id[sid]
        args = ",".join(f"{k}={self.value(v, stack + (sid,))}" for k, v in sorted(s.get("args", {}).items()))
        self.memo[sid] = f"{s.get('tool')}({args})"
        return self.memo[sid]

    def value(self, v, stack: tuple = ()) -> str:
        if _is_ref(v):
            sid, path = REF_RE.match(v).groups()
            return f"{self.step(sid, stack)}.{path}"
        return str(v).strip()

    def all(self) -> dict[str, str]:
        return {sid: self.step(sid) for sid in self.by_id}


def canonical_steps(plan: dict) -> dict[str, str]:
    return Canon(plan.get("steps", [])).all()


def _edges(steps: list[dict]) -> Counter:
    """相依結構只看「哪個工具等哪個工具」，參數錯誤不會連帶算成相依錯誤。"""
    tool = {s["id"]: s["tool"] for s in steps}
    return Counter((tool.get(d), s["tool"]) for s in steps for d in s["depends_on"])


def score_sample(gold: dict, pred: dict | None) -> dict:
    gold_steps = gold.get("steps", [])
    gold_tools = Counter(s["tool"] for s in gold_steps)
    args = [v for s in gold_steps for v in s["args"].values()]
    m = {"parse_ok": pred is not None, "schema_ok": False, "action_ok": False, "pred_action": "invalid",
         "exact": False, "tool_tp": 0, "tool_fp": 0, "tool_fn": sum(gold_tools.values()),
         "distractor": False, "lit_ok": 0, "lit_n": sum(not _is_ref(v) for v in args),
         "ref_ok": 0, "ref_n": sum(_is_ref(v) for v in args),
         "deps_ok": False if gold["action"] == "plan" else None}
    if pred is None or validate(pred):
        return m

    m["schema_ok"], m["pred_action"] = True, pred["action"]
    m["action_ok"] = pred["action"] == gold["action"]
    pred_steps = pred["steps"] if pred["action"] == "plan" else []
    pred_tools = Counter(s["tool"] for s in pred_steps)
    tp = sum((gold_tools & pred_tools).values())
    m.update(tool_tp=tp, tool_fp=sum(pred_tools.values()) - tp, tool_fn=sum(gold_tools.values()) - tp,
             distractor=any(t not in gold_tools for t in pred_tools))

    if gold["action"] == "clarify":
        m["exact"] = m["action_ok"] and set(pred["missing"]) == set(gold["missing"])
    elif gold["action"] == "refuse":
        m["exact"] = m["action_ok"]
    else:
        g, p = Canon(gold_steps), Canon(pred_steps)
        used: set[str] = set()
        for gs in gold_steps:
            ps = next((x for x in pred_steps if x["tool"] == gs["tool"] and x["id"] not in used), None)
            if ps is not None:
                used.add(ps["id"])
            for k, v in gs["args"].items():
                if ps is not None and k in ps["args"] and p.value(ps["args"][k]) == g.value(v):
                    m["ref_ok" if _is_ref(v) else "lit_ok"] += 1
        m["deps_ok"] = m["action_ok"] and _edges(gold_steps) == _edges(pred_steps)
        m["exact"] = m["deps_ok"] and Counter(g.all().values()) == Counter(p.all().values())
    return m


def classify_errors(gold: dict, pred: dict | None, m: dict) -> list[str]:
    if m["exact"]:
        return []
    if not m["schema_ok"]:
        return ["format"]
    ga, pa = gold["action"], pred["action"]
    if ga != pa:
        if ga == "refuse":
            return ["missed_refuse"]
        if pa == "refuse":
            return ["over_refuse"]
        return ["hallucinated_args" if ga == "clarify" else "over_clarify"]
    if ga == "clarify":
        return ["wrong_missing"]
    gt, pt = Counter(s["tool"] for s in gold["steps"]), Counter(s["tool"] for s in pred["steps"])
    tags = []
    if m["distractor"]:
        tags.append("distractor")
    if m["tool_fn"]:
        tags.append("missing_step")
    if any(pt[t] > gt[t] for t in gt):
        tags.append("extra_step")
    if m["lit_ok"] < m["lit_n"]:
        tags.append("literal_arg")
    if m["ref_ok"] < m["ref_n"]:
        tags.append("ref_arg")
    if not m["deps_ok"]:
        tags.append("dependency")
    return tags or ["other"]


def bootstrap_ci(values: list[float], n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    if not values:
        nan = float("nan")
        return nan, nan, nan
    rng, n = random.Random(seed), len(values)
    means = sorted(sum(rng.choices(values, k=n)) / n for _ in range(n_boot))
    return sum(values) / n, means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]
```

- [ ] **Step 4: 執行測試，確認通過**

Run: `uv run pytest tests/test_score.py -v`
Expected: 11 passed

- [ ] **Step 5: 跑全部測試並 commit**

Run: `uv run pytest -q`
Expected: 全部通過（39 passed）

```powershell
git add evaluation/score.py tests/test_score.py
git commit -m "feat: 評分器（正規化比對、分層指標、錯誤分類、bootstrap CI）" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: WSL 環境、批次推論與 baseline

**Files:**
- Create: `train/pyproject.toml`、`train/infer.py`、`evaluation/make_oracle.py`
- Output: `results/preds/{zeroshot,fewshot,oracle}/{test_id,test_ood}.jsonl`、`results/preds/<run>/meta.json`

**Interfaces:**
- Consumes: `planner.prompt.build_messages`、`planner.prompt.pick_shots`
- Produces:
  - `results/preds/<run>/<split>.jsonl`，每行 `{"id": str, "raw": str}`
  - CLI：`uv run python infer.py --run-name NAME [--model HF_ID_OR_ADAPTER_DIR] [--shots 0|3] [--splits ...] [--limit N]`

- [ ] **Step 1: 建立 WSL 訓練環境（可在 Task 1 完成後就先放背景跑）**

`train/pyproject.toml`：

```toml
[project]
name = "patent-planner-train"
version = "0.1.0"
description = "GPU 子專案（只在 WSL2 跑；venv 放 ext4）"
requires-python = ">=3.12"
dependencies = ["unsloth", "trl", "datasets", "transformers", "mlflow", "patent-planner"]

[tool.uv.sources]
patent-planner = { path = "..", editable = true }
```

在 WSL 執行：

```bash
cd /mnt/c/Users/USER/Desktop/patent-planner/train
export UV_PROJECT_ENVIRONMENT=~/venvs/patent-planner-train   # venv 放 ext4；/mnt/c 上 import torch 會慢到不可用
uv sync
uv run python -c "from unsloth import FastLanguageModel; m, t = FastLanguageModel.from_pretrained('unsloth/Qwen3-4B-Instruct-2507', max_seq_length=2048, load_in_4bit=True); print('LOAD_OK', t.chat_template[:80])"
```

Expected：印出 `LOAD_OK`。若 transformers 版本不認得 Qwen3，執行 `uv lock --upgrade-package transformers --upgrade-package unsloth` 後再 `uv sync`。

- [ ] **Step 2: 實作 `train/infer.py`**

```python
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
```

- [ ] **Step 3: Smoke 推論（每個 split 跑 8 筆）**

```bash
cd /mnt/c/Users/USER/Desktop/patent-planner/train
uv run python infer.py --run-name smoke --limit 8
head -c 600 ../results/preds/smoke/test_id.jsonl
```

Expected：每行有 `id` 與 `raw`，`raw` 看起來是 JSON（zero-shot 可能帶 ``` 圍欄，評分器能處理）。若 `raw` 是空字串或亂碼，先檢查 padding 方向和 chat template，再往下做。

- [ ] **Step 4: 跑 zero-shot 與 few-shot baseline**

```bash
uv run python infer.py --run-name zeroshot
uv run python infer.py --run-name fewshot --shots 3
rm -r ../results/preds/smoke
```

Expected：每個 run 約 300 筆，約 10–20 分鐘。

- [ ] **Step 5: 實作 `evaluation/make_oracle.py`（評分器端到端自我檢查）**

```python
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
```

Run（Windows）：`uv run python -m evaluation.make_oracle`

- [ ] **Step 6: Commit**

```powershell
git add train/pyproject.toml train/uv.lock train/infer.py evaluation/make_oracle.py results/preds
git commit -m "feat: 批次推論與 zero-shot / few-shot baseline 預測" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: 結果彙整報告與圖表

**Files:**
- Create: `evaluation/analyze.py`
- Output: `reports/results.md`、`reports/figs/*.png`、`reports/scored/<run>_<split>.jsonl`、`reports/failures_<run>.md`

**Interfaces:**
- Consumes: `planner.schema.parse_output`、`evaluation.score.score_sample`、`classify_errors`、`bootstrap_ci`
- Produces:
  - CLI：`uv run python -m evaluation.analyze --runs RUN [RUN ...] [--dump-failures RUN] [--n 30]`
  - `score_run(run: str, split: str) -> list[dict]`
  - `summarize(rows: list[dict]) -> dict`

- [ ] **Step 1: 寫圖表前，先載入 `dataviz` skill**，依它的配色與標示規則調整下面 `_plot_*` 的顏色和字體。

- [ ] **Step 2: 實作 `evaluation/analyze.py`**

```python
"""彙整多個 run 的評分：整體指標、依類型 exact match、錯誤分布、action 混淆矩陣、圖表與失敗案例。"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

from evaluation.score import bootstrap_ci, classify_errors, score_sample
from planner.schema import parse_output

REPO = Path(__file__).resolve().parents[1]
SPLITS = ["test_id", "test_ood"]
CATS = ["single", "parallel", "chain", "dag", "clarify", "refuse"]
ACTIONS = ["plan", "clarify", "refuse", "invalid"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def score_run(run: str, split: str) -> list[dict]:
    gold = {r["id"]: r for r in load_jsonl(REPO / "data" / f"{split}.jsonl")}
    rows = []
    for p in load_jsonl(REPO / "results" / "preds" / run / f"{split}.jsonl"):
        g = gold[p["id"]]
        pred = parse_output(p["raw"])
        m = score_sample(g["gold"], pred)
        rows.append({"id": p["id"], "category": g["category"], "structure_id": g["structure_id"],
                     "gold_action": g["gold"]["action"], **m, "errors": classify_errors(g["gold"], pred, m)})
    if len(rows) != len(gold):
        raise SystemExit(f"{run}/{split} 預測 {len(rows)} 筆，但資料有 {len(gold)} 筆；推論可能沒跑完")
    return rows


def _rate(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def summarize(rows: list[dict]) -> dict:
    plan = [r for r in rows if r["deps_ok"] is not None]
    tp, fp, fn = (sum(r[k] for r in rows) for k in ("tool_tp", "tool_fp", "tool_fn"))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {
        "n": len(rows),
        "exact": bootstrap_ci([float(r["exact"]) for r in rows]),
        "json_ok": _rate(r["parse_ok"] for r in rows),
        "schema_ok": _rate(r["schema_ok"] for r in rows),
        "action_acc": _rate(r["action_ok"] for r in rows),
        "tool_f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0,
        "distractor": _rate(r["distractor"] for r in plan),
        "lit_acc": sum(r["lit_ok"] for r in plan) / max(1, sum(r["lit_n"] for r in plan)),
        "ref_acc": sum(r["ref_ok"] for r in plan) / max(1, sum(r["ref_n"] for r in plan)),
        "deps_acc": _rate(r["deps_ok"] for r in plan),
    }


def _ci(t) -> str:
    return f"{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]"


def _report(data: dict, runs: list[str]) -> str:
    lines = ["# 評估結果", "", "所有數字皆為本批測試集的觀察值；exact match 附 95% bootstrap CI，CI 重疊時不宣稱差異。", "",
             "## 整體指標", "",
             "| run | split | n | exact match [95% CI] | JSON 合法 | schema 合法 | action 準確 | tool F1 | 干擾項誤用 | 字面參數 | 引用參數 | 相依 |",
             "|" + "---|" * 12]
    for (run, sp), rows in data.items():
        s = summarize(rows)
        lines.append(f"| {run} | {sp} | {s['n']} | {_ci(s['exact'])} | {s['json_ok']:.3f} | {s['schema_ok']:.3f} | "
                     f"{s['action_acc']:.3f} | {s['tool_f1']:.3f} | {s['distractor']:.3f} | {s['lit_acc']:.3f} | "
                     f"{s['ref_acc']:.3f} | {s['deps_acc']:.3f} |")

    lines += ["", "## 依任務類型的 exact match", "", "| run | split | " + " | ".join(CATS) + " |", "|" + "---|" * (len(CATS) + 2)]
    for (run, sp), rows in data.items():
        cells = []
        for c in CATS:
            sub = [r["exact"] for r in rows if r["category"] == c]
            cells.append(f"{_rate(sub):.2f} (n={len(sub)})" if sub else "—")
        lines.append(f"| {run} | {sp} | " + " | ".join(cells) + " |")

    tags = sorted({t for rows in data.values() for r in rows for t in r["errors"]})
    lines += ["", "## 錯誤類型（筆數，一筆可有多個 tag）", "", "| run | split | " + " | ".join(tags) + " |",
              "|" + "---|" * (len(tags) + 2)]
    for (run, sp), rows in data.items():
        c = Counter(t for r in rows for t in r["errors"])
        lines.append(f"| {run} | {sp} | " + " | ".join(str(c[t]) for t in tags) + " |")

    lines += ["", "## action 混淆矩陣（列 = gold，欄 = 預測；test_id + test_ood 合計）", ""]
    for run in runs:
        rows = [r for sp in SPLITS for r in data[(run, sp)]]
        c = Counter((r["gold_action"], r["pred_action"]) for r in rows)
        lines += [f"**{run}**", "", "| gold \\ pred | " + " | ".join(ACTIONS) + " |", "|" + "---|" * (len(ACTIONS) + 1)]
        lines += [f"| {g} | " + " | ".join(str(c[(g, p)]) for p in ACTIONS) + " |" for g in ACTIONS[:3]]
        lines.append("")
    return "\n".join(lines) + "\n"


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Noto Sans CJK TC", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False
    return plt


def _plot_by_category(data: dict, runs: list[str], figdir: Path) -> None:
    plt = _plt()
    width = 0.8 / len(runs)
    for sp in SPLITS:
        fig, ax = plt.subplots(figsize=(9, 4))
        for i, run in enumerate(runs):
            vals = [_rate(r["exact"] for r in data[(run, sp)] if r["category"] == c) for c in CATS]
            ax.bar([x + i * width for x in range(len(CATS))], vals, width, label=run)
        ax.set_xticks([x + width * (len(runs) - 1) / 2 for x in range(len(CATS))], CATS)
        ax.set_ylim(0, 1)
        ax.set_ylabel("plan exact match")
        ax.set_title(f"依任務類型的 exact match（{sp}）")
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(figdir / f"exact_by_category_{sp}.png", dpi=200)
        plt.close(fig)


def _plot_errors(data: dict, runs: list[str], figdir: Path) -> None:
    plt = _plt()
    counts = {run: Counter(t for sp in SPLITS for r in data[(run, sp)] for t in r["errors"]) for run in runs}
    tags = sorted({t for c in counts.values() for t in c}, key=lambda t: -sum(c[t] for c in counts.values()))
    if not tags:
        return
    height = 0.8 / len(runs)
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(tags) + 1.5))
    for i, run in enumerate(runs):
        ax.barh([y + i * height for y in range(len(tags))], [counts[run][t] for t in tags], height, label=run)
    ax.set_yticks([y + height * (len(runs) - 1) / 2 for y in range(len(tags))], tags)
    ax.invert_yaxis()
    ax.set_xlabel("筆數（test_id + test_ood）")
    ax.set_title("錯誤類型分布")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(figdir / "error_distribution.png", dpi=200)
    plt.close(fig)


def _dump_failures(run: str, n: int, data: dict, out: Path) -> None:
    lines = [f"# {run} 失敗案例（隨機 {n} 筆，seed 0）", ""]
    pool = []
    for sp in SPLITS:
        gold = {r["id"]: r for r in load_jsonl(REPO / "data" / f"{sp}.jsonl")}
        raw = {p["id"]: p["raw"] for p in load_jsonl(REPO / "results" / "preds" / run / f"{sp}.jsonl")}
        pool += [(sp, r, gold[r["id"]], raw[r["id"]]) for r in data[(run, sp)] if not r["exact"]]
    for sp, r, g, raw in random.Random(0).sample(pool, min(n, len(pool))):
        lines += [f"## {r['id']}（{sp} / {r['category']} / {r['structure_id']}）— {', '.join(r['errors'])}", "",
                  f"- 可用工具：{', '.join(g['available_tools'])}", f"- 需求：{g['request']}", "",
                  "gold：", "```json", json.dumps(g["gold"], ensure_ascii=False, indent=1), "```",
                  "預測：", "```", raw, "```", "", "觀察：", ""]
    (out / f"failures_{run}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--dump-failures", default=None, help="輸出該 run 的失敗案例供人工細讀")
    ap.add_argument("--n", type=int, default=30)
    a = ap.parse_args()

    out = REPO / "reports"
    (out / "scored").mkdir(parents=True, exist_ok=True)
    (out / "figs").mkdir(exist_ok=True)
    data = {(run, sp): score_run(run, sp) for run in a.runs for sp in SPLITS}
    for (run, sp), rows in data.items():
        (out / "scored" / f"{run}_{sp}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    (out / "results.md").write_text(_report(data, a.runs), encoding="utf-8")
    _plot_by_category(data, a.runs, out / "figs")
    _plot_errors(data, a.runs, out / "figs")
    if a.dump_failures:
        _dump_failures(a.dump_failures, a.n, data, out)
    print(f"寫出 {out / 'results.md'}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Oracle 自我檢查**

Run：`uv run python -m evaluation.analyze --runs oracle`
Expected：`reports/results.md` 中 oracle 所有比率都是 `1.000`，干擾項誤用是 `0.000`，錯誤表沒有任何 tag。只要有任何一格不是 1，就代表評分器或資料有 bug，**先修好再往下做**。

- [ ] **Step 4: 產生 baseline 報告**

Run：`uv run python -m evaluation.analyze --runs zeroshot fewshot --dump-failures fewshot`
Expected：`reports/results.md` 有兩個 run × 兩個 split 的數字；`reports/figs/` 有 3 張 png。打開圖片確認中文字正常顯示。

- [ ] **Step 5: Commit**

```powershell
git add evaluation/analyze.py reports
git commit -m "feat: 評估彙整報告與圖表，baseline 結果" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: QLoRA 微調與評估

**Files:**
- Create: `train/train_qlora.py`（改寫自 `Forsetai/Data-Pipeline/training/train_qlora.py`）
- Output: `outputs/adapters/<run>/`（gitignore）、`mlruns/`（gitignore）、`results/preds/qlora-r16/`

**Interfaces:**
- Consumes: `planner.prompt.sft_messages`、`data/train.jsonl`、`data/val.jsonl`、`data/manifest.json`
- Produces: adapter 目錄 `outputs/adapters/<run-name>/`，可直接傳給 `infer.py --model`

- [ ] **Step 1: 實作 `train/train_qlora.py`**

```python
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

from planner.prompt import sft_messages  # noqa: E402

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
        return Dataset.from_list([{"text": tok.apply_chat_template(sft_messages(r), tokenize=False)} for r in rows])

    ds = {"train": load_text("train"), "val": load_text("val")}
    sample_text = ds["train"][0]["text"]
    assert "<think>" not in sample_text, "chat template 插入了 <think>，底座不是 Instruct-2507 版本"
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
        manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
        mlflow.log_params({
            "base_model": a.base, "dataset_version": manifest["version"], "lora_rank": a.rank,
            "lora_alpha": a.alpha, "max_seq_length": a.max_seq_length, "epochs": a.epochs,
            "max_steps": a.max_steps, "train_samples": len(ds["train"]), "val_samples": len(ds["val"]),
            "dropped_overlong": json.dumps(dropped), "train_sha256": _sha(data_dir / "train.jsonl"),
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
```

- [ ] **Step 2: Smoke 訓練（20 步）**

```bash
cd /mnt/c/Users/USER/Desktop/patent-planner/train
uv run python train_qlora.py --run-name smoke --max-steps 20
```

Expected：

- 印出一筆完整訓練文字，其中可見 system / user / assistant 三段，**沒有** `<think>`。
- 印出 token 長度統計：p95 應遠小於 2048；若 max 超過 2048，記下被剔除的筆數。
- loss 有下降，最後印出 `TRAIN_OK`。

接著跑 smoke adapter 的推論，確認推論流程能接上 adapter：

```bash
uv run python infer.py --run-name smoke-ft --model ../outputs/adapters/smoke --limit 8
rm -r ../results/preds/smoke-ft ../outputs/adapters/smoke
```

- [ ] **Step 3: 完整訓練（預計 30–60 分鐘）**

```bash
uv run python train_qlora.py --run-name qlora-r16
```

Expected：`TRAIN_OK adapter=.../outputs/adapters/qlora-r16`。若訓練在第 1 個 epoch 後就 early stop，在報告中如實記錄。

- [ ] **Step 4: 微調模型推論，並對 val 做健全性檢查**

```bash
uv run python infer.py --run-name qlora-r16 --model ../outputs/adapters/qlora-r16 --splits val test_id test_ood
```

val 的 exact match 用 Python 單行計算（`analyze` 只處理 test 切分）：

```powershell
uv run python -c "import json; from evaluation.analyze import load_jsonl, REPO; from evaluation.score import score_sample; from planner.schema import parse_output; g={r['id']:r for r in load_jsonl(REPO/'data/val.jsonl')}; p=load_jsonl(REPO/'results/preds/qlora-r16/val.jsonl'); print('val exact', sum(score_sample(g[x['id']]['gold'], parse_output(x['raw']))['exact'] for x in p)/len(p), 'n', len(p))"
```

Expected：val exact 應明顯高於 baseline 的 test_id，且與 qlora 的 test_id 接近。若 val 很高、test_id 卻很低，代表切分有洩漏或推論設定不一致，先排查再往下做。

- [ ] **Step 5: 更新報告並 commit**

```powershell
uv run python -m evaluation.analyze --runs zeroshot fewshot qlora-r16 --dump-failures qlora-r16
git add train/train_qlora.py results/preds/qlora-r16 reports
git commit -m "feat: QLoRA 微調 Qwen3-4B 與三方評估結果" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

MLflow 檢視（Windows，repo 根目錄）：`$env:MLFLOW_ALLOW_FILE_STORE = "true"; uvx mlflow ui --backend-store-uri mlruns`。簡報要用 loss 曲線時，從這裡截圖。

---

### Task 9: Error Analysis 撰寫與 optional 決策

**Files:**
- Create: `reports/error_analysis.md`
- Modify: `reports/failures_qlora-r16.md`（逐筆填寫「觀察」）

- [ ] **Step 1: 細讀失敗案例**

逐筆閱讀 `reports/failures_qlora-r16.md` 的 30 筆，在每筆的「觀察：」後面寫一句話：錯在哪裡、可能原因。重點找自動分類看不出來的模式，例如：

- 錯誤是否集中在某些 `structure_id`
- 是否集中在 3 步以上的計畫
- 模型是否把 S28 / S30 當成 S15 / S11，也就是沒看工具清單
- `clarify` 時是否捏造案號

- [ ] **Step 2: 撰寫 `reports/error_analysis.md`**

固定以下 5 節，每個數字都引用自 `reports/results.md` 並附上 n：

```markdown
# Error Analysis

## 1. 整體結論
（qlora vs few-shot vs zero-shot 的 exact match 與 CI；CI 是否重疊）

## 2. 泛化：test_id vs test_ood
（三個 run 各自的差距；差距代表什麼）

## 3. 依任務類型
（哪一類進步最多、哪一類仍最差；附 exact_by_category 圖）

## 4. 錯誤型態
（錯誤分布圖；微調前後各 tag 的變化；人工細讀歸納出的 2–3 個模式，各附 1 個代表案例 id）

## 5. 限制與下一步
（資料多樣性、模板數、單一 seed、n 的大小；對應的改善方式）
```

- [ ] **Step 3: 🔶 決定 optional 項目（10/13 晚上）**

| 情況 | 決定 |
|---|---|
| qlora 在 test_ood 明顯落後 test_id | 第二輪資料改善：針對最弱的類型增加模板或句型，重訓 `qlora-r16-v2` |
| qlora 的進步主要來自 JSON 合法率 | 補 constrained decoding ablation，回答「微調是不是只學到格式」 |
| 主線結果穩定、時間足夠 | 做 Task 10 Executor demo |
| 10/14 中午前任何一項沒完成 | 停止 optional，直接進 Task 11 |

第二輪訓練或 constrained decoding 若被選中，屆時另外寫一份小計畫，不擠進本計畫。

- [ ] **Step 4: Commit**

```powershell
git add reports
git commit -m "docs: error analysis 與失敗案例逐筆觀察" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10（optional）: Executor demo

**Files:**
- Create: `planner/executor.py`、`train/demo.py`
- Test: `tests/test_executor.py`

**Interfaces:**
- Consumes: `planner.schema.REF_RE`、`planner.prompt.build_messages`、`planner.schema.parse_output`
- Produces:
  - `planner.executor.MOCK: dict[str, Callable[[dict], dict]]`
  - `resolve(value, results: dict[str, dict])`：解析 `$sN.path`
  - `execute(plan: dict, log=print) -> dict[str, dict]`：依相依順序執行並回傳各步結果

- [ ] **Step 1: 寫失敗測試 `tests/test_executor.py`**

```python
import pytest

from planner.executor import execute, resolve

PLAN = {"action": "plan", "steps": [
    {"id": "s3", "tool": "compare_claims",
     "args": {"claim_text": "$s1.claims[0]", "reference_patent_no": "$s2.cited_refs[0]"}, "depends_on": ["s1", "s2"]},
    {"id": "s1", "tool": "get_case", "args": {"case_id": "TW-2026-0412"}, "depends_on": []},
    {"id": "s2", "tool": "get_office_action", "args": {"oa_id": "OA-2026-0331"}, "depends_on": []},
]}


def test_resolve_nested_path():
    results = {"s1": {"results": [{"patent_no": "I700001"}]}}
    assert resolve("$s1.results[0].patent_no", results) == "I700001"
    assert resolve("TW-2026-0412", results) == "TW-2026-0412"


def test_execute_respects_dependencies_regardless_of_order():
    order = []
    results = execute(PLAN, log=lambda msg: order.append(msg))
    assert set(results) == {"s1", "s2", "s3"}
    assert "distinguishing_features" in results["s3"]
    assert [m for m in order if m.startswith("▶")][-1].startswith("▶ s3")


def test_execute_raises_on_unsatisfiable_dependency():
    bad = {"action": "plan", "steps": [
        {"id": "s1", "tool": "get_case", "args": {"case_id": "x"}, "depends_on": ["s9"]}]}
    with pytest.raises(RuntimeError):
        execute(bad, log=lambda msg: None)
```

- [ ] **Step 2: 執行測試，確認失敗**

Run: `uv run pytest tests/test_executor.py -v`
Expected: FAIL，出現 `ModuleNotFoundError: No module named 'planner.executor'`

- [ ] **Step 3: 實作 `planner/executor.py`**

```python
"""Executor：依 depends_on 執行 plan，解析 $sN 引用，並印出每步中間結果。工具是 mock，不會呼叫真實系統。"""
import re

from planner.schema import REF_RE

MOCK = {
    "get_case": lambda a: {"application_no": "112100001", "claims": ["一種半導體封裝結構，包含基板與散熱鰭片…"],
                           "oa_ids": ["OA-2026-0331"], "status": "審查中"},
    "get_office_action": lambda a: {"cited_refs": ["I701234", "I705678"],
                                    "rejected_claims": ["一種半導體封裝結構，包含基板…"],
                                    "grounds": "請求項 1 不具進步性", "issue_date": "2026-09-15"},
    "get_patent": lambda a: {"patent_no": a["patent_no"], "title": "封裝基板及其製法",
                             "abstract": "本發明提供一種封裝基板…", "claims": ["一種封裝基板，包含…"]},
    "search_prior_art": lambda a: {"results": [{"patent_no": "I708888"}, {"patent_no": "I702222"}]},
    "compare_claims": lambda a: {"overlap": 0.62, "distinguishing_features": "散熱鰭片的排列結構"},
    "calc_deadline": lambda a: {"deadline": "2026-11-15" if not a.get("extension_months") else "2027-01-15"},
    "amend_claims": lambda a: {"amended_claim": f"（修正後）請求項 {a['claim_no']}：…{a['instruction']}"},
    "draft_response": lambda a: {"draft_id": "DRAFT-0001"},
    "translate_text": lambda a: {"translated": f"[{a['target_lang']}] translated text"},
    "notify_client": lambda a: {"sent": True},
}


def resolve(value, results: dict[str, dict]):
    m = REF_RE.match(value) if isinstance(value, str) else None
    if not m:
        return value
    cur = results[m.group(1)]
    for tok in re.findall(r"[a-z_]+|\[\d+\]", m.group(2)):
        cur = cur[int(tok[1:-1])] if tok.startswith("[") else cur[tok]
    return cur


def execute(plan: dict, log=print) -> dict[str, dict]:
    results: dict[str, dict] = {}
    pending = list(plan["steps"])
    while pending:
        ready = [s for s in pending if all(d in results for d in s["depends_on"])]
        if not ready:
            raise RuntimeError(f"無法繼續執行：{[s['id'] for s in pending]} 的相依無法滿足")
        for s in ready:
            args = {k: resolve(v, results) for k, v in s["args"].items()}
            log(f"▶ {s['id']} {s['tool']}({', '.join(f'{k}={v!r}' for k, v in args.items())})")
            results[s["id"]] = MOCK[s["tool"]](args)
            log(f"  → {results[s['id']]}")
            pending.remove(s)
    return results
```

- [ ] **Step 4: 執行測試，確認通過**

Run: `uv run pytest tests/test_executor.py -v`
Expected: 3 passed

- [ ] **Step 5: 實作 `train/demo.py`（WSL，載入 adapter 後端到端示範）**

```python
"""端到端 demo：request → Planner（微調模型）→ Executor（mock tools）。

用法（WSL）：uv run python demo.py "把 TW-2026-0412 的請求項 1 跟 OA-2026-0331 的第一件引證比對"
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
    adapter = sys.argv[2] if len(sys.argv) > 2 else str(REPO / "outputs" / "adapters" / "qlora-r16")
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
```

Run（WSL）：`uv run python demo.py "把 TW-2026-0412 的請求項 1 跟 OA-2026-0331 的第一件引證比對"`
Expected：先印出計畫，再依序印出 `▶ s1` / `▶ s2` / `▶ s3` 與結果，最後是 `[完成] 共 3 步`。另外試一個 clarify（「幫我算答辯期限」）和一個 refuse（「幫我繳年費」）。

- [ ] **Step 6: Commit**

```powershell
git add planner/executor.py train/demo.py tests/test_executor.py
git commit -m "feat: Executor demo（mock tools、依相依執行並解析引用）" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: 凍結結果與 README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 全部測試與 oracle 檢查重跑一次**

```powershell
uv run pytest -q
uv run python -m evaluation.analyze --runs oracle
uv run python -m evaluation.analyze --runs zeroshot fewshot qlora-r16
```

Expected：測試全綠；oracle 全部為 1.000；`reports/results.md` 與 Task 8 的版本一致（`git diff reports/results.md` 沒有差異）。

- [ ] **Step 2: 改寫 `README.md`**

```markdown
# patent-planner

專利答辯 Agent 的 Planner 微調：以合成資料對 `Qwen3-4B-Instruct-2507` 做 QLoRA，並與 zero-shot / few-shot baseline 比較。

## 結果摘要
（從 reports/results.md 複製整體指標表，以及 test_id / test_ood 的 exact match 與 CI）

## 架構
Plan-and-Execute：Planner 一次輸出工具呼叫 DAG（JSON），Executor 依 depends_on 執行並解析 `$sN.欄位` 引用。

## 重現步驟
1. 資料：`uv run python -m datagen.generate` → `uv run python -m datagen.paraphrase`（需本地 Ollama `qwen2.5:7b-instruct`；`data/paraphrase_cache.jsonl` 已附，有快取時不需要 Ollama）
2. Baseline 與訓練（WSL / Colab T4）：見 `train/`，`infer.py`、`train_qlora.py`
3. 評估：`uv run python -m evaluation.analyze --runs zeroshot fewshot qlora-r16`

## 文件
- 設計：`docs/design.md`
- 評估結果：`reports/results.md`
- Error analysis：`reports/error_analysis.md`
```

「結果摘要」那一節要填入實際數字後再 commit。

- [ ] **Step 3: Commit 並推送**

```powershell
git add README.md
git commit -m "docs: README 與結果摘要" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push
```

- [ ] **Step 4: 🔶 10/15 轉為 public（由 Allen 確認後執行）**

```powershell
gh repo edit JiangAllen/patent-planner --visibility public --accept-visibility-change-consequences
```

轉 public 前先確認：`git log -p | Select-String -Pattern "矽品|SPIL"` 沒有任何結果，且 `data/` 內只有合成資料。
