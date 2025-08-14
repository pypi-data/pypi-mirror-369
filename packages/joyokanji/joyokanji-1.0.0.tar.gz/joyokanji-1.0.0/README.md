# joyo-kanji
  
[日本語](./README_Ja.md) / [English](./README.md)  
  
`joyokanji` is a tiny, fast Python library that converts old-form kanji (Japanese: *kyūjitai*, 舊字/旧字) to new-form kanji (*shinjitai*, 新字) using a mapping grounded in the Agency for Cultural Affairs’ **Jōyō Kanji list** (常用漢字表). See the source list (Japanese) published by the Government of Japan: [https://www.bunka.go.jp/kokugo\_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/](https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/).

> **What’s kyūjitai vs. shinjitai?**
> After WWII, Japan simplified the shapes of many commonly used kanji. The older shapes are *kyūjitai* (e.g., **鹽 → 塩**, **國 → 国**, **體 → 体**), and the simplified shapes are *shinjitai*. This library helps normalize text by replacing old forms with their modern counterparts.

---

## Table of Contents

* [Features](#features)
* [Installation](#installation)
* [Quick Start](#quick-start)
* [How It Works](#how-it-works)
* [Examples](#examples)
* [Scope & Limitations](#scope--limitations)
* [Data Source & Attribution](#data-source--attribution)
* [Performance Notes](#performance-notes)
* [When to Use / Not to Use](#when-to-use--not-to-use)
* [Contributing](#contributing)
* [License](#license)

---

## Features

* converts old-form (kyūjitai) kanji to modern (shinjitai) forms.
* Mapping-based, deterministic behavior — no surprises.
* Fast single-pass conversion using `str.translate` (linear time O(n)).
* Loads mapping once from `joyokanji/config/kanji.json` and caches it.
* Pure-Python, minimal footprint, easy to embed in pipelines.

## Installation

```bash
pip install joyokanji
```

> If your package name differs on PyPI, update the command above accordingly.

## Quick Start

```python
import joyokanji

text = "鹽と黃と黑と點と發"
print(joyokanji.convert(text))  # => 塩と黄と黒と点と発
```

## How It Works

* On first use, the library loads a JSON dictionary (`joyokanji/config/kanji.json`) of old→new pairs (e.g., `{"鹽": "塩"}`) and builds a translation table with `str.maketrans`.
* Conversion is then a single pass over your string using `str.translate`, which is both simple and efficient.
* The table is cached in memory for subsequent calls.

## Examples

Input → Output:

| Kyūjitai | Shinjitai |
| -------- | --------- |
| 鹽        | 塩         |
| 黃        | 黄         |
| 黑        | 黒         |
| 點        | 点         |
| 發        | 発         |


*Only characters listed in the mapping are transformed; all others remain unchanged.*

## Scope & Limitations

* **Coverage**: The mapping focuses on characters relevant to modern Japanese usage and the Jōyō Kanji context. It is **not** a general Traditional ↔ Simplified Chinese converter and is **not** intended for zh-Hant texts (Taiwan/Hong Kong).
* **Context-free**: Conversion is character-to-character. The library does **not** inspect context, readings, or word boundaries.
* **Proper nouns & personal names**: Historical documents, proper nouns, and person names may intentionally use old forms (e.g., in legal names). Automatic conversion can be undesirable in such use cases. Review outputs when accuracy matters.
* **Normalization**: The library does not perform Unicode normalization (e.g., NFKC) by itself. If you need it, run normalization **before or after** conversion according to your pipeline’s needs.
* **Ambiguous variants**: Some characters have multiple historical variants. The mapping chooses a widely accepted modern form; if you need domain-specific variants, consider customizing the mapping.

## Data Source & Attribution

* Primary reference: the **Jōyō Kanji list** (常用漢字表) as published by Japan’s Agency for Cultural Affairs: [https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/pdf/joyokanjihyo_20101130.pdf](https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/pdf/joyokanjihyo_20101130.pdf).
* The included mapping is derived from this reference and related historical simplifications. Any omissions or edge cases are welcomed as issues or PRs.

## Performance Notes

* Building the translation table happens once per process. Subsequent calls are memory-only and very fast.
* The complexity is O(n) with low constant overhead, making it suitable for batch text processing.

## When to Use / Not to Use

**Use when:** you need to normalize legacy texts into modern Japanese (OCR outputs, historical corpora, or mixed-form datasets).

**Avoid or review carefully when:** processing legal names, brand names, or scholarly editions where the original glyph choices carry meaning.

## Contributing

* Issues and PRs are welcome, especially for: (1) mapping improvements, (2) tests covering edge cases, (3) documentation in English/Japanese.
* If proposing new pairs, please include a source/rationale and examples.

## License

Apache License 2.0