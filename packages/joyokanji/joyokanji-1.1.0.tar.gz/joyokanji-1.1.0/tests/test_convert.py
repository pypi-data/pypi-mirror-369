import json
from pathlib import Path

import joyokanji


def test_basic_conversion():
    assert joyokanji.convert("鹽黃黑點發") == "塩黄黒点発"


def test_mixed_text_no_change_for_unmapped():
    text = "今日は良い天気!"
    assert joyokanji.convert(text) == text


def test_mixed_replacement():
    text = "黑い點と黃いろ、そして點黑"
    expected = "黒い点と黄いろ、そして点黒"
    assert joyokanji.convert(text) == expected


def test_idempotent():
    text = "鹽と黃と黑と點と發"
    once = joyokanji.convert(text)
    twice = joyokanji.convert(once)
    assert once == twice


def test_every_mapping_char_replaced_to_expected():
    # Ensure all single-char keys in kanji.json convert to their mapped value
    mapping_path = Path(__file__).resolve().parents[1] / "joyokanji" / "config" / "kanji.json"
    data = json.loads(mapping_path.read_text(encoding="utf-8"))
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str) and len(k) == 1 and len(v) == 1:
            assert joyokanji.convert(k) == v


def test_empty_string():
    assert joyokanji.convert("") == ""


def test_variants_default_off():
    # characters like 髙 or 𠮷 should not change unless variants=True
    text = "髙橋𠮷野屋"
    assert joyokanji.convert(text) == text


def test_variants_on_changes_applied():
    text = "髙橋𠮷野屋﨑田隆之介突練視難響羽"
    expected = "高橋吉野屋崎田隆之介突練視難響羽"
    assert joyokanji.convert(text, variants=True) == expected
