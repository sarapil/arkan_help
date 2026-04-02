# Copyright (c) 2026, Arkan and contributors
# For license information, please see license.txt

"""
Whitelisted API endpoints for the arkan_help frontend.

All endpoints are accessible at::

    /api/method/arkan_help.arkan_help.api.help.<function_name>
"""

from __future__ import annotations

import json

import frappe

from arkan_help.arkan_help.utils.resolver import HelpResolver


# ---------------------------------------------------------------------------
# get_help — main context-aware lookup
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def get_help(
	doctype: str | None = None,
	fieldname: str | None = None,
	view_type: str = "form",
	action: str | None = None,
	route: str | None = None,
):
	"""Return resolved help content for the given context.

	Called by the frontend ``arkan_help.HelpWidget``.

	Parameters
	----------
	doctype : str, optional
	    The DocType the user is currently viewing.
	fieldname : str, optional
	    A specific field within *doctype*.
	view_type : str
	    One of ``form``, ``list``, ``report``, ``page``.
	action : str, optional
	    One of ``create``, ``edit``, ``view``.
	route : str, optional
	    Current page route (for page-level / navbar help).

	Returns
	-------
	dict | None
	    The resolved help payload, or ``None`` (empty ``message``).
	"""
	resolver = HelpResolver()

	# If a route is supplied without a doctype, treat it as a navbar / page lookup
	if route and not doctype:
		lang = frappe.local.lang or resolver.fallback_language
		return resolver.get_navbar_help(route, lang)

	roles = frappe.get_roles(frappe.session.user)
	lang = frappe.local.lang or resolver.fallback_language

	return resolver.resolve(
		{
			"doctype": doctype,
			"fieldname": fieldname,
			"view_type": view_type,
			"action": action,
			"roles": roles,
			"language": lang,
		}
	)


# ---------------------------------------------------------------------------
# get_fields_with_help — bulk field-availability check
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def get_fields_with_help(doctype: str):
	"""Return a list of fieldnames that have help content for *doctype*.

	The frontend uses this to decide which fields get an ⓘ icon.
	We query Help Context rows that have both ``doctype_link`` and
	``fieldname`` set, plus file-based field anchors when enabled.
	"""
	if not doctype:
		return []

	# 1. Database: fields referenced in Help Context
	db_fields = frappe.get_all(
		"Help Context",
		filters={
			"doctype_link": doctype,
			"fieldname": ("is", "set"),
		},
		pluck="fieldname",
	)
	field_set = set(db_fields)

	# 2. File-based fields (if enabled)
	settings = frappe.get_cached_doc("Help Settings").as_dict()
	if settings.get("enable_file_based_help"):
		resolver = HelpResolver()
		for info in resolver.discover_file_help():
			slug = frappe.scrub(doctype)
			fname = f"{slug}.md"
			if info.get("file") == fname:
				field_set.update(info.get("fields", []))

	return sorted(field_set)


# ---------------------------------------------------------------------------
# has_route_help — lightweight existence check
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def has_route_help(route: str):
	"""Check whether help content exists for the given *route*.

	Returns ``{"has_help": True/False}`` so the navbar can toggle the
	indicator dot without fetching full content.
	"""
	if not route:
		return {"has_help": False}

	# Check for a Help Topic with context_type = "page" and matching reference
	exists = frappe.db.exists(
		"Help Topic",
		{
			"context_type": "page",
			"context_reference": route,
			"enabled": 1,
		},
	)
	if exists:
		return {"has_help": True}

	# Also check doctype-style routes (e.g. "Form/Sales Order/SO-001")
	parts = route.split("/")
	if len(parts) >= 2 and parts[0] in ("Form", "List"):
		dt = parts[1]
		exists = frappe.db.exists(
			"Help Topic",
			{
				"context_type": "doctype",
				"context_reference": dt,
				"enabled": 1,
			},
		)
		if exists:
			return {"has_help": True}

	return {"has_help": False}


# ---------------------------------------------------------------------------
# log_help_view — analytics
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def log_help_view(topic_key: str | None = None, doctype: str | None = None, fieldname: str | None = None):
	"""Log a help view event for analytics.

	Only records when ``Help Settings.analytics_enabled`` is on.
	Fires a ``help_view`` realtime event that can be consumed by
	a dashboard or logged to a custom DocType later.
	"""
	settings = frappe.get_cached_doc("Help Settings").as_dict()
	if not settings.get("analytics_enabled"):
		return {"logged": False}

	import time

	frappe.publish_realtime(
		"help_view",
		{
			"topic_key": topic_key,
			"doctype": doctype,
			"fieldname": fieldname,
			"user": frappe.session.user,
			"timestamp": time.time(),
		},
		after_commit=True,
	)
	return {"logged": True}
