# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
Whitelisted API endpoints for the arkan_help translation workflow.

All endpoints are accessible at::

    /api/method/arkan_help.arkan_help.api.translation.<function_name>
"""

from __future__ import annotations

import frappe

from arkan_help.arkan_help.utils.translation import HelpTranslationManager


# ---------------------------------------------------------------------------
# extract_strings
# ---------------------------------------------------------------------------


@frappe.whitelist()
def extract_strings(app_name: str | None = None):
	"""Extract all translatable strings from help content.

	Returns ``{"strings": [...], "count": int}``.
	"""
	frappe.only_for(["System Manager"])
	mgr = HelpTranslationManager()
	strings = mgr.extract_strings(app_name=app_name)
	return {"strings": strings, "count": len(strings)}


# ---------------------------------------------------------------------------
# export_for_translation
# ---------------------------------------------------------------------------


@frappe.whitelist()
def export_for_translation(
	source_lang: str = "en",
	target_lang: str = "ar",
	format: str = "csv",
	app_name: str | None = None,
):
	"""Export strings for professional translators.

	Returns ``{"filepath": str, "count": int}``.
	"""
	frappe.only_for(["System Manager"])
	mgr = HelpTranslationManager()
	filepath = mgr.export_for_translation(
		source_lang=source_lang,
		target_lang=target_lang,
		format=format,
		app_name=app_name,
	)
	strings = mgr.extract_strings(app_name=app_name)
	return {"filepath": filepath, "count": len(strings)}


# ---------------------------------------------------------------------------
# import_translations
# ---------------------------------------------------------------------------


@frappe.whitelist()
def import_translations(filepath: str, target_lang: str):
	"""Import completed translations from a file.

	Returns ``{"imported": int, "skipped": int, "errors": list}``.
	"""
	frappe.only_for(["System Manager"])
	mgr = HelpTranslationManager()
	return mgr.import_translations(filepath=filepath, target_lang=target_lang)


# ---------------------------------------------------------------------------
# sync_with_frappe
# ---------------------------------------------------------------------------


@frappe.whitelist()
def sync_with_frappe(app_name: str = "arkan_help"):
	"""Sync help translations with Frappe's standard CSV files.

	Returns ``{"languages": [...], "total_written": int}``.
	"""
	frappe.only_for(["System Manager"])
	mgr = HelpTranslationManager()
	return mgr.sync_with_frappe(app_name=app_name)


# ---------------------------------------------------------------------------
# validate_completeness
# ---------------------------------------------------------------------------


@frappe.whitelist()
def validate_completeness(lang: str, app_name: str | None = None):
	"""Check translation coverage for a language.

	Returns ``{"total_strings": int, "translated": int, "missing": [...],
	"coverage_percent": float}``.
	"""
	frappe.only_for(["System Manager"])
	mgr = HelpTranslationManager()
	return mgr.validate_completeness(lang=lang, app_name=app_name)
