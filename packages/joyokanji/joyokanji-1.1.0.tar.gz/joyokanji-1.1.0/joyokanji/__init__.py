"""joyokanji: Convert historical/variant Kanji to Joyo (modern) forms.

Public API:
- convert(text: str) -> str

This loads a character-to-character mapping from `config/kanji.json` once,
builds a fast translation table, and applies it with str.translate for speed.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict, Mapping

__all__ = ["convert"]


# Module-level caches for speed on repeated calls
_MAP: Dict[str, str] | None = None
_TABLE: Mapping[int, int | str] | None = None
_VARIANTS_MAP: Dict[str, str] | None = None
_TABLE_WITH_VARIANTS: Mapping[int, int | str] | None = None
_INIT_LOCK = threading.Lock()


def _package_dir() -> Path:
	return Path(__file__).resolve().parent


def _kanji_json_path() -> Path:
	return _package_dir() / "config" / "kanji.json"


def _variants_json_path() -> Path:
	return _package_dir() / "config" / "variants.json"


def _load_map() -> Dict[str, str]:
	path = _kanji_json_path()
	try:
		with path.open("r", encoding="utf-8") as f:
			data = json.load(f)
	except FileNotFoundError:
		# If the mapping file is missing, fall back to identity (no-op)
		return {}

	# Keep only one-character to one-character mappings to guarantee O(n) translate
	out: Dict[str, str] = {}
	for k, v in data.items():
		if isinstance(k, str) and isinstance(v, str) and len(k) == 1 and len(v) == 1:
			out[k] = v
	return out


def _load_variants_map() -> Dict[str, str]:
	path = _variants_json_path()
	try:
		with path.open("r", encoding="utf-8") as f:
			data = json.load(f)
	except FileNotFoundError:
		return {}

	out: Dict[str, str] = {}
	for k, v in data.items():
		if isinstance(k, str) and isinstance(v, str) and len(k) == 1 and len(v) == 1:
			out[k] = v
	return out


def _ensure_initialized(base_only: bool = True) -> None:
	"""Initialize translation tables.

	If base_only=True, ensure only the base table (kanji.json) is built.
	If base_only=False, also ensure the merged table with variants is built.
	"""
	global _MAP, _TABLE, _VARIANTS_MAP, _TABLE_WITH_VARIANTS
	if base_only:
		if _TABLE is not None:
			return
	else:
		if _TABLE_WITH_VARIANTS is not None:
			return
	with _INIT_LOCK:
		# Base table
		if _TABLE is None:
			if _MAP is None:
				_MAP = _load_map()
			_TABLE = {ord(k): ord(v) for k, v in _MAP.items()}
		# Variants-merged table
		if not base_only and _TABLE_WITH_VARIANTS is None:
			if _VARIANTS_MAP is None:
				_VARIANTS_MAP = _load_variants_map()
			merged: Dict[str, str] = {}
			if _MAP is None:
				_MAP = _load_map()
			merged.update(_MAP)
			merged.update(_VARIANTS_MAP or {})
			_TABLE_WITH_VARIANTS = {ord(k): ord(v) for k, v in merged.items()}


def convert(text: str, variants: bool=False) -> str:
	"""Convert any characters in `text` that have mappings to their modern forms.

	- Input: arbitrary Python str
	- Output: str with per-character replacements applied in a single pass
	- Performance: uses a prebuilt translation table and str.translate (C-accelerated)
	"""
	if not isinstance(text, str):
		raise TypeError("convert() expects a str input")
	_ensure_initialized(base_only=not variants)
	table = _TABLE_WITH_VARIANTS if variants else _TABLE
	return text.translate(table or {})

