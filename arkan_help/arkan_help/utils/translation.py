# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
Help Translation Manager
========================

Provides a complete translation workflow for help content:

* **extract**   – gather translatable strings from DB and markdown files
* **export**    – produce files for professional translators (CSV, XLIFF, JSON, PO)
* **import**    – ingest completed translations back into Frappe
* **sync**      – write Frappe-standard ``translations/{lang}.csv``
* **validate**  – report coverage percentage and missing strings
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import frappe
from frappe.utils import cstr, now_datetime

from arkan_help.arkan_help.utils.resolver import (
	_FIELD_ANCHOR_RE,
	_extract_field_sections,
	_parse_frontmatter,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
_PARAGRAPH_RE = re.compile(r"(?:^|\n\n)([^\n#>|`\-*\d].+?)(?:\n\n|\Z)", re.DOTALL)
_LIST_ITEM_RE = re.compile(r"^\s*[\-*\d.]+\s+(.+)$", re.MULTILINE)

# Minimum string length worth translating
_MIN_STRING_LEN = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _app_translations_dir(app_name: str = "arkan_help") -> Path:
	"""Return ``{app}/translations/`` creating it if needed."""
	app_path = Path(frappe.get_app_path(app_name))
	tr_dir = app_path.parent / "translations"
	tr_dir.mkdir(parents=True, exist_ok=True)
	return tr_dir


def _app_custom_translations_dir(app_name: str = "arkan_help") -> Path:
	"""Return ``{app}/translations/custom/`` creating it if needed."""
	d = _app_translations_dir(app_name) / "custom"
	d.mkdir(parents=True, exist_ok=True)
	return d


def _extract_md_strings(text: str) -> list[str]:
	"""Pull translatable text fragments from a markdown string.

	We extract:
	- headings (``# Title``)
	- paragraph blocks
	- list items
	"""
	strings: list[str] = []

	for m in _HEADING_RE.finditer(text):
		s = m.group(1).strip()
		if len(s) >= _MIN_STRING_LEN:
			strings.append(s)

	for m in _LIST_ITEM_RE.finditer(text):
		s = m.group(1).strip()
		if len(s) >= _MIN_STRING_LEN:
			strings.append(s)

	for m in _PARAGRAPH_RE.finditer(text):
		s = m.group(1).strip()
		# Skip if it's just a heading or list item already captured
		if s and len(s) >= _MIN_STRING_LEN and not s.startswith("#"):
			strings.append(s)

	return strings


def _dedupe_preserve_order(items: list[str]) -> list[str]:
	seen: set[str] = set()
	out: list[str] = []
	for s in items:
		if s not in seen:
			seen.add(s)
			out.append(s)
	return out


# ---------------------------------------------------------------------------
# XLIFF helpers
# ---------------------------------------------------------------------------


def _build_xliff(
	units: list[dict],
	source_lang: str,
	target_lang: str,
) -> str:
	"""Build XLIFF 1.2 XML string from a list of translation units.

	Each *unit* is ``{"id": ..., "source": ..., "target": ..., "context": ...}``.
	"""
	xliff = ET.Element("xliff", version="1.2", xmlns="urn:oasis:names:tc:xliff:document:1.2")
	file_el = ET.SubElement(
		xliff,
		"file",
		original="arkan_help",
		datatype="plaintext",
		**{"source-language": source_lang, "target-language": target_lang},
	)
	body = ET.SubElement(file_el, "body")

	for u in units:
		tu = ET.SubElement(body, "trans-unit", id=str(u["id"]))
		src = ET.SubElement(tu, "source")
		src.text = u["source"]
		tgt = ET.SubElement(tu, "target")
		tgt.text = u.get("target") or ""
		if u.get("context"):
			note = ET.SubElement(tu, "note")
			note.text = u["context"]

	tree = ET.ElementTree(xliff)
	buf = io.BytesIO()
	tree.write(buf, encoding="utf-8", xml_declaration=True)
	return buf.getvalue().decode("utf-8")


def _parse_xliff(content: str) -> list[dict]:
	"""Parse XLIFF 1.2 and return list of ``{"source", "target", "context"}``."""
	ns = {"x": "urn:oasis:names:tc:xliff:document:1.2"}
	root = ET.fromstring(content)
	units: list[dict] = []

	# Handle with or without namespace
	for tu in root.iter():
		if tu.tag.endswith("trans-unit") or tu.tag == "trans-unit":
			source = target = context = ""
			for child in tu:
				tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
				if tag == "source":
					source = child.text or ""
				elif tag == "target":
					target = child.text or ""
				elif tag == "note":
					context = child.text or ""
			if source:
				units.append({"source": source, "target": target, "context": context})

	return units


# ---------------------------------------------------------------------------
# PO helpers
# ---------------------------------------------------------------------------


def _build_po(
	units: list[dict],
	target_lang: str,
) -> str:
	"""Build a minimal PO-format string."""
	lines: list[str] = [
		"# Translation file for arkan_help",
		f"# Language: {target_lang}",
		f'msgid ""',
		f'msgstr ""',
		f'"Content-Type: text/plain; charset=UTF-8\\n"',
		f'"Language: {target_lang}\\n"',
		"",
	]
	for u in units:
		if u.get("context"):
			lines.append(f"#. {u['context']}")
		lines.append(f'msgid "{_po_escape(u["source"])}"')
		lines.append(f'msgstr "{_po_escape(u.get("target") or "")}"')
		lines.append("")

	return "\n".join(lines)


def _parse_po(content: str) -> list[dict]:
	"""Minimal PO parser – extracts msgid/msgstr pairs."""
	units: list[dict] = []
	current_id = current_str = ""
	state = None

	for line in content.splitlines():
		line = line.strip()
		if line.startswith("#"):
			continue
		if line.startswith("msgid "):
			state = "id"
			current_id = _po_unescape(line[6:].strip().strip('"'))
		elif line.startswith("msgstr "):
			state = "str"
			current_str = _po_unescape(line[7:].strip().strip('"'))
		elif line.startswith('"') and state:
			text = _po_unescape(line.strip('"'))
			if state == "id":
				current_id += text
			else:
				current_str += text
		elif not line:
			if current_id:
				units.append({"source": current_id, "target": current_str})
			current_id = current_str = ""
			state = None

	# Last pair
	if current_id:
		units.append({"source": current_id, "target": current_str})

	return units


def _po_escape(s: str) -> str:
	return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _po_unescape(s: str) -> str:
	return s.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")


# ---------------------------------------------------------------------------
# HelpTranslationManager
# ---------------------------------------------------------------------------


class HelpTranslationManager:
	"""Manages the full translation lifecycle for arkan_help content."""

	# ------------------------------------------------------------------
	# extract_strings
	# ------------------------------------------------------------------

	def extract_strings(self, app_name: str | None = None) -> list[str]:
		"""Extract all translatable strings from help sources.

		Sources scanned:

		1. **Help Topic** — ``title`` field
		2. **Help Content** — markdown/HTML ``content`` field
		3. **File-based** — ``{app}/help/{lang}/*.md`` headings, paragraphs, list items

		Returns a deduplicated list preserving first-seen order.
		"""
		strings: list[str] = []

		# --- 1. Help Topic titles ---
		topics = frappe.get_all(
			"Help Topic",
			filters={"enabled": 1},
			fields=["title", "topic_key"],
		)
		for t in topics:
			if t.title:
				strings.append(t.title)

		# --- 2. Help Content bodies ---
		contents = frappe.get_all(
			"Help Content",
			fields=["content", "content_type", "topic"],
		)
		for c in contents:
			if c.content and c.content_type in ("markdown", "html"):
				strings.extend(_extract_md_strings(c.content))

		# --- 3. File-based markdown ---
		apps = [app_name] if app_name else frappe.get_installed_apps()
		for app in apps:
			try:
				app_path = Path(frappe.get_app_path(app))
			except Exception:
				continue

			help_dir = app_path / "help"
			if not help_dir.is_dir():
				continue

			for lang_dir in sorted(help_dir.iterdir()):
				if not lang_dir.is_dir():
					continue
				for md_file in sorted(lang_dir.glob("*.md")):
					try:
						text = md_file.read_text(encoding="utf-8")
					except Exception:
						continue
					meta, body = _parse_frontmatter(text)
					# Frontmatter title
					if meta.get("title"):
						strings.append(meta["title"])
					if meta.get("title_en"):
						strings.append(meta["title_en"])
					# Body strings
					strings.extend(_extract_md_strings(body))

		return _dedupe_preserve_order(strings)

	# ------------------------------------------------------------------
	# export_for_translation
	# ------------------------------------------------------------------

	def export_for_translation(
		self,
		source_lang: str = "en",
		target_lang: str = "ar",
		format: str = "csv",
		app_name: str | None = None,
	) -> str:
		"""Export a translation file for professional translators.

		Parameters
		----------
		source_lang : str
			Language code of the source strings.
		target_lang : str
			Language code of the target translation.
		format : str
			One of ``csv``, ``xliff``, ``json``, ``po``.
		app_name : str, optional
			Restrict to a specific app's file-based help.

		Returns
		-------
		str
			File path of the exported file.
		"""
		strings = self.extract_strings(app_name=app_name)

		# Pre-load existing translations for the target language
		existing = self._load_existing_translations(target_lang)

		units: list[dict] = []
		for idx, src in enumerate(strings, 1):
			units.append({
				"id": idx,
				"source": src,
				"target": existing.get(src, ""),
				"context": "",
			})

		# Build output
		ts = int(time.time())
		out_dir = _app_translations_dir()

		if format == "csv":
			content = self._build_csv(units)
			out_path = out_dir / f"{target_lang}_export_{ts}.csv"
		elif format == "xliff":
			content = _build_xliff(units, source_lang, target_lang)
			out_path = out_dir / f"{target_lang}_export_{ts}.xliff"
		elif format == "json":
			content = self._build_json(units)
			out_path = out_dir / f"{target_lang}_export_{ts}.json"
		elif format == "po":
			content = _build_po(units, target_lang)
			out_path = out_dir / f"{target_lang}_export_{ts}.po"
		else:
			frappe.throw(f"Unsupported export format: {format}")

		out_path.write_text(content, encoding="utf-8")
		return str(out_path)

	# ------------------------------------------------------------------
	# import_translations
	# ------------------------------------------------------------------

	def import_translations(
		self,
		filepath: str,
		target_lang: str,
	) -> dict:
		"""Import completed translations from a file.

		Auto-detects format from the file extension (.csv, .xliff, .json, .po).

		Returns
		-------
		dict
			``{"imported": int, "skipped": int, "errors": list[str]}``
		"""
		path = Path(filepath)
		if not path.is_file():
			frappe.throw(f"File not found: {filepath}")

		content = path.read_text(encoding="utf-8")
		ext = path.suffix.lower()

		if ext == ".csv":
			pairs = self._parse_csv(content)
		elif ext in (".xliff", ".xlf"):
			pairs = _parse_xliff(content)
		elif ext == ".json":
			pairs = self._parse_json(content)
		elif ext == ".po":
			pairs = _parse_po(content)
		else:
			frappe.throw(f"Unsupported file format: {ext}")

		imported = 0
		skipped = 0
		errors: list[str] = []

		# Load existing custom translations
		custom_path = _app_custom_translations_dir() / f"{target_lang}.json"
		existing: dict[str, str] = {}
		if custom_path.is_file():
			try:
				existing = json.loads(custom_path.read_text(encoding="utf-8"))
			except Exception:
				pass

		for pair in pairs:
			source = pair.get("source", "").strip()
			target = pair.get("target", "").strip()

			if not source:
				skipped += 1
				continue

			if not target:
				skipped += 1
				continue

			try:
				existing[source] = target
				imported += 1
			except Exception as e:
				errors.append(f"Error for '{source[:50]}…': {e}")

		# Persist to custom JSON
		custom_path.write_text(
			json.dumps(existing, ensure_ascii=False, indent=2),
			encoding="utf-8",
		)

		# Also sync to Frappe CSV
		self._write_frappe_csv(target_lang, existing)

		return {"imported": imported, "skipped": skipped, "errors": errors}

	# ------------------------------------------------------------------
	# sync_with_frappe
	# ------------------------------------------------------------------

	def sync_with_frappe(self, app_name: str = "arkan_help") -> dict:
		"""Sync help translations into Frappe-standard ``translations/{lang}.csv``.

		Merges:
		1. Strings from custom JSON files in ``translations/custom/{lang}.json``
		2. Existing ``translations/{lang}.csv`` (preserves non-help entries)

		Returns ``{"languages": [...], "total_written": int}``.
		"""
		custom_dir = _app_custom_translations_dir(app_name)
		tr_dir = _app_translations_dir(app_name)
		languages: list[str] = []
		total = 0

		for json_file in sorted(custom_dir.glob("*.json")):
			lang = json_file.stem
			try:
				pairs = json.loads(json_file.read_text(encoding="utf-8"))
			except Exception:
				continue

			if not isinstance(pairs, dict):
				continue

			self._write_frappe_csv(lang, pairs, tr_dir)
			languages.append(lang)
			total += len(pairs)

		return {"languages": languages, "total_written": total}

	# ------------------------------------------------------------------
	# validate_completeness
	# ------------------------------------------------------------------

	def validate_completeness(self, lang: str, app_name: str | None = None) -> dict:
		"""Check translation coverage for a given language.

		Returns
		-------
		dict
			``{"total_strings": int, "translated": int, "missing": list[str],
			   "coverage_percent": float}``
		"""
		all_strings = self.extract_strings(app_name=app_name)
		existing = self._load_existing_translations(lang)

		translated = 0
		missing: list[str] = []

		for s in all_strings:
			if s in existing and existing[s]:
				translated += 1
			else:
				missing.append(s)

		total = len(all_strings)
		pct = round((translated / total) * 100, 1) if total else 100.0

		return {
			"total_strings": total,
			"translated": translated,
			"missing": missing,
			"coverage_percent": pct,
		}

	# ------------------------------------------------------------------
	# Private helpers
	# ------------------------------------------------------------------

	def _load_existing_translations(self, lang: str) -> dict[str, str]:
		"""Load translations from multiple sources, in priority order:

		1. ``translations/custom/{lang}.json``
		2. ``translations/{lang}.csv`` (Frappe standard)
		3. Help Content entries in the target language
		"""
		pairs: dict[str, str] = {}

		# --- Help Content DB entries ---
		contents = frappe.get_all(
			"Help Content",
			filters={"language": lang},
			fields=["topic", "content", "content_type"],
		)
		for c in contents:
			# Map the topic title
			topic_title = frappe.db.get_value("Help Topic", c.topic, "title")
			if topic_title and c.content:
				# For markdown content, the whole body is the "translation"
				# of the topic.  We also map extracted sub-strings.
				for s in _extract_md_strings(c.content):
					pairs[s] = s  # identity (content IS the target lang)

		# --- Frappe CSV ---
		csv_path = _app_translations_dir() / f"{lang}.csv"
		if csv_path.is_file():
			try:
				for row in csv.reader(csv_path.open(encoding="utf-8")):
					if len(row) >= 2 and row[0] != "source_text":
						pairs[row[0]] = row[1]
			except Exception:
				pass

		# --- Custom JSON (highest priority) ---
		json_path = _app_custom_translations_dir() / f"{lang}.json"
		if json_path.is_file():
			try:
				data = json.loads(json_path.read_text(encoding="utf-8"))
				if isinstance(data, dict):
					pairs.update(data)
			except Exception:
				pass

		return pairs

	def _write_frappe_csv(
		self,
		lang: str,
		pairs: dict[str, str],
		tr_dir: Path | None = None,
	) -> Path:
		"""Write (or merge into) the Frappe-standard ``translations/{lang}.csv``.

		Frappe format::

			source_text,translated_text,context
		"""
		tr_dir = tr_dir or _app_translations_dir()
		csv_path = tr_dir / f"{lang}.csv"

		# Load existing rows to preserve non-help entries
		existing: dict[str, tuple[str, str]] = {}  # source → (translated, context)
		if csv_path.is_file():
			try:
				for row in csv.reader(csv_path.open(encoding="utf-8")):
					if len(row) >= 2 and row[0] != "source_text":
						ctx = row[2] if len(row) > 2 else ""
						existing[row[0]] = (row[1], ctx)
			except Exception:
				pass

		# Merge new pairs
		for source, target in pairs.items():
			if source and target:
				existing[source] = (target, existing.get(source, ("", ""))[1])

		# Write
		buf = io.StringIO()
		writer = csv.writer(buf)
		writer.writerow(["source_text", "translated_text", "context"])
		for src in sorted(existing.keys()):
			translated, ctx = existing[src]
			writer.writerow([src, translated, ctx])

		csv_path.write_text(buf.getvalue(), encoding="utf-8")
		return csv_path

	# ── CSV format ────────────────────────────────────────────────

	@staticmethod
	def _build_csv(units: list[dict]) -> str:
		buf = io.StringIO()
		writer = csv.writer(buf)
		writer.writerow(["source_text", "translated_text", "context"])
		for u in units:
			writer.writerow([u["source"], u.get("target", ""), u.get("context", "")])
		return buf.getvalue()

	@staticmethod
	def _parse_csv(content: str) -> list[dict]:
		pairs: list[dict] = []
		for row in csv.reader(io.StringIO(content)):
			if len(row) >= 2 and row[0] != "source_text":
				pairs.append({
					"source": row[0],
					"target": row[1],
					"context": row[2] if len(row) > 2 else "",
				})
		return pairs

	# ── JSON format ───────────────────────────────────────────────

	@staticmethod
	def _build_json(units: list[dict]) -> str:
		data = {}
		for u in units:
			data[u["source"]] = u.get("target", "")
		return json.dumps(data, ensure_ascii=False, indent=2)

	@staticmethod
	def _parse_json(content: str) -> list[dict]:
		data = json.loads(content)
		if isinstance(data, dict):
			return [{"source": k, "target": v} for k, v in data.items()]
		if isinstance(data, list):
			return data
		return []


# ---------------------------------------------------------------------------
# Module-level convenience functions (for bench execute)
# ---------------------------------------------------------------------------


def extract_strings(app_name: str | None = None) -> list[str]:
	"""``bench execute arkan_help.arkan_help.utils.translation.extract_strings``"""
	mgr = HelpTranslationManager()
	result = mgr.extract_strings(app_name=app_name)
	frappe.logger().info(f"arkan_help: extracted {len(result)} translatable strings")
	return result


def export_for_translation(
	source_lang: str = "en",
	target_lang: str = "ar",
	format: str = "csv",
	app_name: str | None = None,
) -> str:
	"""``bench execute arkan_help.arkan_help.utils.translation.export_for_translation``"""
	mgr = HelpTranslationManager()
	path = mgr.export_for_translation(
		source_lang=source_lang,
		target_lang=target_lang,
		format=format,
		app_name=app_name,
	)
	frappe.logger().info(f"arkan_help: exported translations to {path}")
	return path


def import_translations(filepath: str, target_lang: str) -> dict:
	"""``bench execute arkan_help.arkan_help.utils.translation.import_translations``"""
	mgr = HelpTranslationManager()
	result = mgr.import_translations(filepath=filepath, target_lang=target_lang)
	frappe.logger().info(
		f"arkan_help: imported {result['imported']} translations, "
		f"skipped {result['skipped']}, errors {len(result['errors'])}"
	)
	return result


def sync_with_frappe(app_name: str = "arkan_help") -> dict:
	"""``bench execute arkan_help.arkan_help.utils.translation.sync_with_frappe``"""
	mgr = HelpTranslationManager()
	result = mgr.sync_with_frappe(app_name=app_name)
	frappe.logger().info(
		f"arkan_help: synced {result['total_written']} strings "
		f"for languages {result['languages']}"
	)
	return result


def validate_completeness(lang: str, app_name: str | None = None) -> dict:
	"""``bench execute arkan_help.arkan_help.utils.translation.validate_completeness``"""
	mgr = HelpTranslationManager()
	result = mgr.validate_completeness(lang=lang, app_name=app_name)
	frappe.logger().info(
		f"arkan_help: {lang} coverage = {result['coverage_percent']}% "
		f"({result['translated']}/{result['total_strings']})"
	)
	return result
