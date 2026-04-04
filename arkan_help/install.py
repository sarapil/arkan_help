# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
Arkan Help — Post-Install Setup
Runs after `bench install-app arkan_help`.
"""

import frappe
from frappe import _


def after_install():
    """Post-installation setup for Arkan Help."""
    # ── Desktop Icon injection (Frappe v16 /desk) ──
    from arkan_help.desktop_utils import inject_app_desktop_icon
    inject_app_desktop_icon(
        app="arkan_help",
        label="Arkan Help",
        route="/app/arkan-help",
        logo_url="/assets/arkan_help/images/arkan_help-logo.svg",
        bg_color="#10B981",
    )
    print(f"✅ {_("Arkan Help")}: post-install complete")


def inject_desktop_icon():
    """Create desktop shortcut icon for Arkan Help."""
    if frappe.db.exists("Desktop Icon", {"module_name": "Arkan Help"}):
        return

    try:
        frappe.get_doc({
            "doctype": "Desktop Icon",
            "module_name": "Arkan Help",
            "label": _("Arkan Help"),
            "icon": "octicon octicon-bookmark",
            "color": "#10B981",
            "type": "module",
            "standard": 1,
        }).insert(ignore_permissions=True)
    except Exception:
        pass  # May not exist in all Frappe versions
