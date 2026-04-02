# Arkan Help — Scenarios & Impact Matrix
# مساعدة أركان

> DocType/API/Page scenarios with business impact assessment.

## Core Scenarios

### 1. Contextual Help Lookup
| Aspect | Detail |
|--------|--------|
| **Trigger** | User opens a form or clicks ⓘ icon |
| **Flow** | field_help.js → get_field_help_map → HelpResolver matches context |
| **DocTypes** | Help Topic, Help Content, Help Context |
| **APIs** | `get_help`, `get_field_help_map`, `check_help_available` |
| **Impact** | HIGH — core functionality |

### 2. Multilingual Help Content Management
| Aspect | Detail |
|--------|--------|
| **Trigger** | Admin creates/edits help topics |
| **Flow** | Help Topic → Help Content (per language) → Help Context (mapping) |
| **DocTypes** | Help Topic, Help Content, Help Content Role |
| **APIs** | Standard CRUD |
| **Impact** | HIGH — content management |

### 3. Translation Workflow
| Aspect | Detail |
|--------|--------|
| **Trigger** | Admin exports strings for translation |
| **Flow** | extract_strings → export_for_translation → translator edits → import_translations → sync |
| **APIs** | `extract_strings`, `export_for_translation`, `import_translations`, `sync_translations`, `check_coverage` |
| **Impact** | MEDIUM — localization |

### 4. Help Analytics Tracking
| Aspect | Detail |
|--------|--------|
| **Trigger** | User views help content |
| **Flow** | help_widget.js → track_help_view → realtime event |
| **APIs** | `track_help_view` |
| **Impact** | LOW — analytics |

### 5. Navbar Help Indicator
| Aspect | Detail |
|--------|--------|
| **Trigger** | Page load |
| **Flow** | navbar_help.js → check_help_available → show/hide badge |
| **Impact** | MEDIUM — discoverability |


---

## Impact Legend
- **HIGH** — Core functionality, blocks usage if broken
- **MEDIUM** — Important but has workarounds
- **LOW** — Nice-to-have, minimal disruption if unavailable
