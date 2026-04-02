# 🔗 Arkan Help — Integrations Guide

> **Domain:** Help & Documentation System
> **Prefix:** AH

---

## Integration Map

```
Arkan Help
  ├── All Arkan Lab Apps
  ├── frappe_visual
```

---

## All Arkan Lab Apps

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| Arkan Help | All Arkan Lab Apps | On submit | Document data |
| All Arkan Lab Apps | Arkan Help | On change | Updated data |

### Configuration
```python
# In AH Settings or site_config.json
# all_arkan_lab_apps_enabled = 1
```

---

## frappe_visual

### Connection Type
- **Direction:** Bidirectional
- **Protocol:** Python API / REST
- **Authentication:** Frappe session / API key

### Data Flow
| Source | Target | Trigger | Data |
|--------|--------|---------|------|
| Arkan Help | frappe_visual | On submit | Document data |
| frappe_visual | Arkan Help | On change | Updated data |

### Configuration
```python
# In AH Settings or site_config.json
# frappe_visual_enabled = 1
```

---

## API Endpoints

All integration APIs use the standard response format from `arkan_help.api.response`:

```python
from arkan_help.api.response import success, error

@frappe.whitelist()
def sync_data():
    return success(data={}, message="Sync completed")
```

---

*Part of Arkan Help by Arkan Lab*
