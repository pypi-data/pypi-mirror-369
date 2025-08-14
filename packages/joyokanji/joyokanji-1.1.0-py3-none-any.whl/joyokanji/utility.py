import json
import re
import shutil
from pathlib import Path
from typing import Dict


def extract_text_from_pdf(pdf_path: Path) -> str:
	"""
	Try to extract text directly from a PDF using pdfminer.six.
	Keep this simple and dependency-light. If pdfminer is missing, raise
	a helpful error so the caller can decide what to do.
	"""
	try:
		from pdfminer.high_level import extract_text  # type: ignore
	except Exception as e:
		raise RuntimeError(
			"pdfminer.six is required to extract text. Install with 'pip install pdfminer.six'."
		) from e

	text = extract_text(str(pdf_path))
	# Normalize common whitespace variations
	text = text.replace("\r\n", "\n").replace("\r", "\n")
	return text


def _is_kanji(ch: str) -> bool:
	"""Return True if the character is a CJK unified ideograph (incl. ext A..G) or common marks like 々/〆/ヶ."""
	if not ch:
		return False
	code = ord(ch)
	# Basic + Extension A
	if 0x4E00 <= code <= 0x9FFF or 0x3400 <= code <= 0x4DBF:
		return True
	# Compatibility Ideographs
	if 0xF900 <= code <= 0xFAFF:
		return True
	# Extensions B..G (Supplementary Planes)
	if 0x20000 <= code <= 0x2A6DF or 0x2A700 <= code <= 0x2B73F or 0x2B740 <= code <= 0x2B81F \
	   or 0x2B820 <= code <= 0x2CEAF or 0x2CEB0 <= code <= 0x2EBEF or 0x30000 <= code <= 0x3134F:
		return True
	# Common Japanese iteration marks etc.
	if ch in {"々", "〆", "ヵ", "ヶ"}:
		return True
	return False


def parse_kanji_pairs(text: str) -> Dict[str, str]:
	"""
	Parse strings like: 漢字1文字\t（漢字1文字） and return
	a dict mapping { inside_parenthesis: outside }.

	Be flexible with whitespace and parentheses variants.
	"""
	# Full/half width parentheses. Require at least one tab between the two characters
	# to match the requested pattern: 漢字1文字\t（漢字1文字）
	pattern = re.compile(r"(\S)\s*\t+\s*[（(]\s*(\S)\s*[)）]")

	mapping: Dict[str, str] = {}

	# Search over whole text; finditer is fine. If the PDF has line-based layout,
	# line breaks are already in the text.
	for m in pattern.finditer(text):
		outside = m.group(1)
		inside = m.group(2)
		if _is_kanji(outside) and _is_kanji(inside):
			# If duplicates appear, last one wins (deterministic and simple)
			mapping[inside] = outside
	return mapping


def write_json(data: Dict[str, str], out_path: Path) -> None:
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open("w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def generate_kanji_map(
	pdf_path: Path = Path(__file__).parent / "config" / "joyokanjihyo_20101130.pdf",
	out_path: Path = Path(__file__).parent / "config" / "kanji.json",
) -> Path:
	"""
	Extract text from the PDF, parse kanji pairs, and write JSON mapping.
	Returns the output path.
	"""
	if not pdf_path.exists():
		raise FileNotFoundError(f"PDF not found: {pdf_path}")

	text = extract_text_from_pdf(pdf_path)
	mapping = parse_kanji_pairs(text)

	# If no mappings found, try OCR fallback (for scanned PDFs)
	if not mapping:
		ocr_text = _ocr_pdf_text_if_available(pdf_path)
		if ocr_text:
			mapping = parse_kanji_pairs(ocr_text)
	write_json(mapping, out_path)
	return out_path


def _ocr_pdf_text_if_available(pdf_path: Path) -> str:
	"""
	Best-effort OCR using pypdfium2 for rendering and pytesseract for OCR.
	Requires the 'tesseract' binary on PATH. If not present, return empty string.
	Keep implementation simple; process pages sequentially.
	"""
	if shutil.which("tesseract") is None:
		# Tesseract not installed; skip OCR.
		return ""

	try:
		import pytesseract  # type: ignore
		import pypdfium2 as pdfium  # type: ignore
	except Exception:
		return ""

	# Render pages and OCR
	text_chunks = []
	try:
		pdf = pdfium.PdfDocument(str(pdf_path))
		for i in range(len(pdf)):
			page = pdf[i]
			# Render at 200 dpi equivalent for a balance of speed/accuracy
			pil_image = page.render(scale=2).to_pil()
			try:
				# Prefer Japanese model if available
				chunk = pytesseract.image_to_string(pil_image, lang="jpn")
			except pytesseract.TesseractError:
				# Fallback to default (may be poor for Japanese)
				chunk = pytesseract.image_to_string(pil_image)
			text_chunks.append(chunk)
	except Exception:
		return ""

	text = "\n".join(text_chunks)
	return text.replace("\r\n", "\n").replace("\r", "\n")

if __name__ == "__main__":
	file = generate_kanji_map()
	print(f"Generated: {file}")
