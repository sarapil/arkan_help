# Arkan Help — Technical Context

> **Contextual Help System for Frappe Applications**
> نظام المساعدة السياقية لتطبيقات فريب

Provides context-aware, multilingual help content tied to specific DocTypes, fields,
views, and user roles. Supports field-level help icons (ⓘ), navbar indicators,
modal help panels, and analytics tracking.

## Architecture

```
arkan_help/
├── arkan_help/
│   ├── hooks.py              # App config — JS/CSS injection, cache hooks, boot
│   ├── api/
│   │   ├── help.py           # 4 endpoints: get_help, get_field_help_map, check_help_available, track_help_view
│   │   └── translation.py    # 5 endpoints: extract/export/import/sync/check translations
│   ├── boot.py               # Injects Help Settings feature flags to client
│   ├── seed.py               # Post-migrate seed data
│   ├── exceptions.py         # Custom exception hierarchy
│   ├── utils/
│   │   ├── resolver.py       # HelpResolver class — core resolution logic
│   │   └── translation.py    # HelpTranslationManager class
│   └── arkan_help/           # Module: Arkan Help
│       └── doctype/
│           ├── help_topic/           # Organized help entries (autoname: prompt)
│           ├── help_content/         # Multilingual content per topic (markdown/HTML/video)
│           ├── help_context/         # Maps help to doctype/field/view/action + role + priority
│           ├── help_settings/        # Single — language, feature toggles, display options
│           └── help_content_role/    # Child table — role links for Help Content
├── public/
│   ├── js/
│   │   ├── help_widget.js    # Main help widget UI (modal panel)
│   │   ├── field_help.js     # Field-level ⓘ icons on forms
│   │   └── navbar_help.js    # Navbar help indicator badge
│   └── css/
│       └── help.css          # Help styling
└── translations/
    └── ar.csv                # Arabic translations
```

## DocTypes (5)

| DocType | Type | Purpose |
|---------|------|---------|
| Help Topic | Regular | Help entries with key, title, app, context type, icon, sort_order |
| Help Content | Regular | Multilingual content per topic — markdown/HTML, video URL, target_roles |
| Help Context | Regular | Maps help to doctype/field/view/action with role + priority |
| Help Settings | Single | Default language, feature toggles, display options, cache TTL |
| Help Content Role | Child Table | Links roles to Help Content entries |

## API Endpoints (9 total)

| Endpoint | Description |
|----------|-------------|
| `api.help.get_help` | Main context-aware help lookup via HelpResolver |
| `api.help.get_field_help_map` | Returns fields that have help content (for ⓘ icons) |
| `api.help.check_help_available` | Lightweight check if help exists for a route |
| `api.help.track_help_view` | Analytics — logs help view events via realtime |
| `api.translation.extract_strings` | Extract translatable strings from help content |
| `api.translation.export_for_translation` | Export strings for translators (CSV) |
| `api.translation.import_translations` | Import completed translations from file |
| `api.translation.sync_translations` | Sync with Frappe's standard translation CSV files |
| `api.translation.check_coverage` | Check translation coverage percentage |

## Frontend Integration

- `app_include_js` — help_widget.js, field_help.js, navbar_help.js (loaded on every desk page)
- `app_include_css` — help.css
- `extend_bootinfo` — Injects Help Settings feature flags into `frappe.boot`
- Cache invalidation hooks on Help Content, Help Topic, Help Context, Help Settings changes

## Help Resolution Flow

```
User opens form/page → field_help.js checks get_field_help_map
                     → navbar_help.js checks check_help_available
                     → User clicks ⓘ → help_widget.js calls get_help
                     → HelpResolver matches context (doctype/field/view/role/language)
                     → Returns ranked help content (priority-based)
```

## Dependencies

- **frappe** >= 16.0.0, < 17.0.0
- Python >= 3.10
