# Arkan Help — Architecture
# مساعدة أركان — الهيكلية

> Contextual Help System

## Overview

Single module: Help Topics → Help Content (multilingual) → Help Contexts (mapping). Client-side: help_widget.js, field_help.js, navbar_help.js.

## Technology Stack

- **Backend**: Python 3.14+ / Frappe 16.x
- **Database**: MariaDB 11.x
- **Frontend**: Frappe UI / JavaScript
- **Real-time**: Socket.IO via Redis
- **Cache/Queue**: Redis

## Integration Points

- **Frappe Core** — DocType CRUD, permissions, workflow
- **ERPNext** — Financial transactions (where applicable)
- **CAPS** — Capability-based access control
- **frappe_visual** — Visual components (graphs, dashboards)

## Security

- All APIs require authentication (except explicitly guest-allowed)
- Permission guards via `frappe.only_for()`, `@require_capability`, `.check_permission()`
- Field-level access via CAPS capability maps
