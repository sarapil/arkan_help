app_name = "arkan_help"
app_title = "Arkan Help"
app_publisher = "Arkan"
app_description = "Contextual Help System for Frappe"
app_email = "ahmedshaheen@example.com"
app_license = "mit"

required_apps = ["frappe"]

# Fixtures — export default Help Settings on bench export-fixtures
fixtures = [
	{"dt": "Help Settings"},
]

app_include_js = [
	"/assets/arkan_help/js/help_widget.js",
	"/assets/arkan_help/js/field_help.js",
	"/assets/arkan_help/js/navbar_help.js",
]

app_include_css = [
	"/assets/arkan_help/css/help.css",
]

# Pass Help Settings to the client via frappe.boot
extend_bootinfo = "arkan_help.arkan_help.boot.extend_bootinfo"

# ---------------------------------------------------------------------------
# Doc Events — invalidate help cache on content changes
# ---------------------------------------------------------------------------

_help_cache_hook = "arkan_help.arkan_help.utils.resolver.on_help_doc_change"

doc_events = {
	"Help Content": {
		"on_update": _help_cache_hook,
		"on_trash": _help_cache_hook,
	},
	"Help Topic": {
		"on_update": _help_cache_hook,
		"on_trash": _help_cache_hook,
	},
	"Help Context": {
		"on_update": _help_cache_hook,
		"on_trash": _help_cache_hook,
	},
	"Help Settings": {
		"on_update": _help_cache_hook,
	},
}

# ---------------------------------------------------------------------------

# ─── Post-Migration Seed ───
after_migrate = ["arkan_help.arkan_help.seed.seed_data"]

# Translation — auto-sync Frappe CSV on Help Content changes
# ---------------------------------------------------------------------------

# Schedule a lightweight sync after each Help Content save so the
# standard translations/{lang}.csv stays up-to-date.
# Uses the same doc_events hook (handled inside on_help_doc_change).
# For a full manual sync run:
#   bench execute arkan_help.arkan_help.utils.translation.sync_with_frappe

# CAPS Integration — Capability-Based Access Control
# ------------------------------------------------------------
caps_capabilities = [
    {"name": "AH_manage_topics", "category": "Module", "description": "Manage help topics and content"},
    {"name": "AH_manage_translations", "category": "Action", "description": "Manage help translations"},
    {"name": "AH_view_analytics", "category": "Report", "description": "View help analytics"},
]
