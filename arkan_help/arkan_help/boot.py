# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
Boot module — extends ``frappe.boot`` with Help Settings so the
frontend JS can read feature flags (``enable_field_help``,
``enable_navbar_help``, etc.) without an extra API call.
"""

import frappe


def extend_bootinfo(bootinfo):
	"""Called via ``extend_bootinfo`` hook in hooks.py.

	Injects a minimal ``arkan_help_settings`` dict into ``frappe.boot``
	containing only the fields the frontend needs.
	"""
	try:
		settings = frappe.get_cached_doc("Help Settings")
		bootinfo.arkan_help_settings = {
			"enable_field_help": settings.enable_field_help,
			"enable_navbar_help": settings.enable_navbar_help,
			"enable_form_help": settings.enable_form_help,
			"enable_file_based_help": settings.enable_file_based_help,
			"analytics_enabled": settings.analytics_enabled,
			"help_icon": settings.help_icon or "help-circle",
			"modal_width": settings.modal_width or "md",
			"cache_ttl": settings.cache_ttl or 3600,
		}
	except Exception:
		# If Help Settings hasn't been created yet (fresh install),
		# provide safe defaults so the JS doesn't break.
		bootinfo.arkan_help_settings = {
			"enable_field_help": 0,
			"enable_navbar_help": 0,
			"enable_form_help": 0,
			"enable_file_based_help": 0,
			"analytics_enabled": 0,
			"help_icon": "help-circle",
			"modal_width": "md",
			"cache_ttl": 3600,
		}
