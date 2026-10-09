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


def test_simplified_chars_are_converted_to_traditional():
    out = "请帮我把 OA-2026-0331 的第一件引证跟被驳回的第一项请求项比对"
    text, ok = paraphrase(ORIG, ["OA-2026-0331"], seed=0, fn=lambda t, s: out, sleep=lambda s: None)
    assert ok and "幫" in text and "帮" not in text and "OA-2026-0331" in text


def test_retries_until_valid():
    outs = iter(["壞掉", GOOD])
    text, ok = paraphrase(ORIG, ["OA-2026-0331"], seed=0, fn=lambda t, s: next(outs), sleep=lambda s: None)
    assert ok and text == GOOD
