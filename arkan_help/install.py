"""
Arkan Help — Post-Install Setup
Runs after `bench install-app arkan_help`.
"""

import frappe
from frappe import _


def after_install():
    """Post-installation setup for Arkan Help."""
    inject_desktop_icon()
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
