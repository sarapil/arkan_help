# Usage Scenarios — سيناريوهات الاستخدام

This directory contains per-role usage scenarios for **Arkan Help**.

Each scenario file documents:
- Daily / Weekly / Monthly / Exception workflows
- Pre-conditions and expected outcomes
- Screen references (links to `../screens/`)
- Device breakpoint compatibility (desktop/tablet/mobile)

---

## Files

| File | Role | Description |
|------|------|-------------|
| [admin.md](admin.md) | System Admin | Setup, configuration, analytics, user management |
| [author.md](author.md) | Help Author | Content creation, editing, translations |
| [user.md](user.md) | Help User | Consuming help content, field help, search |
| [cross-role.md](cross-role.md) | Multi-Role | Workflows involving multiple roles |

---

## Scenario Taxonomy

| Code | Meaning | Frequency |
|------|---------|-----------|
| DS-XXX | Daily Scenario | Every day |
| WS-XXX | Weekly Scenario | Once per week |
| MS-XXX | Monthly Scenario | Once per month |
| ES-XXX | Exception Scenario | When errors occur |

---

## Roles in Arkan Help

| Role | Arabic | CAPS Capabilities | Primary Actions |
|------|--------|-------------------|-----------------|
| **Help Admin** | مسؤول المساعدة | All AH_* | Configure, manage users, analytics |
| **Help Author** | مؤلف المساعدة | `AH_author_content`, `AH_manage_topics` | Create/edit help content |
| **Help User** | مستخدم المساعدة | None (read-only) | View help, provide feedback |

---

## How to Use

1. **Identify** which role you are developing for
2. **Read** the role's scenario file
3. **Map** each scenario to screen designs in `../screens/`
4. **Write** tests that cover each scenario ID
5. **Verify** breakpoint compatibility matches spec

---

## Scenario → Screen Mapping

| Scenario | Screen(s) |
|----------|-----------|
| DS-001 (User: Field Help) | [field-help-tooltip.md](../screens/field-help-tooltip.md) |
| DS-001 (Author: Create Content) | [help-content-form.md](../screens/help-content-form.md) |
| DS-002 (User: Navbar Help) | [navbar-help-panel.md](../screens/navbar-help-panel.md) |
| WS-001 (Author: Analytics) | [dashboard.md](../screens/dashboard.md) |

---

## Cross-Reference

- **Tests**: `arkan_help/tests/` — test files should reference scenario IDs
- **Screens**: `docs/screens/` — screen specs link back to scenarios
- **Help Content**: Each scenario should have help content for users
