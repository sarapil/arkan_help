# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

__version__ = "0.0.1"


def has_app_permission():
	"""Check if the current user has permission to access the Arkan Help app.
	Returns True for all desk users (help is available to everyone).
	Used by add_to_apps_screen in hooks.py.
	"""
	import frappe
	return frappe.session.user != "Guest"
