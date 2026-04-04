# Arkan Help — Contextual Help System

<p align="center">
  <img src="arkan_help/public/images/arkan_help-logo.svg" alt="Arkan Help Logo" width="120">
</p>

<h3 align="center">نظام المساعدة السياقية</h3>

<p align="center">
  <a href="https://github.com/ArkanLab/arkan_help/actions/workflows/ci.yml">
    <img src="https://github.com/ArkanLab/arkan_help/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/ArkanLab/arkan_help/actions/workflows/linters.yml">
    <img src="https://github.com/ArkanLab/arkan_help/actions/workflows/linters.yml/badge.svg" alt="Linters">
  </a>
  <img src="https://img.shields.io/badge/Frappe-v16-blue" alt="Frappe v16">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
  <img src="https://img.shields.io/badge/i18n-Arabic%20%2B%20English-brightgreen" alt="Bilingual">
</p>

---

> Universal contextual help system for Frappe v16. Provides in-app help topics, multilingual content, and context-aware help mapping for DocTypes, pages, and reports.

## ✨ Features

- ❓ **Navbar Help Icon** — Global ❓ icon in the navbar that opens contextual help for the current page
- ⓘ **Field-Level Help** — Info icons on form fields with hover tooltips and click-to-expand
- 📚 **Help Topics** — Organized help entries with machine-readable keys and rich content
- 🌐 **Multilingual Content** — Markdown, HTML, video, and interactive content per language
- 🎯 **6-Level Resolution** — Smart priority system: exact field+role+lang → DocType → file-based → fallback
- 📂 **File-Based Help** — Apps provide `help/{lang}/{doctype}.md` files with field anchors
- 🔐 **Role-Based Visibility** — Show help content based on user roles and permissions
- ⚙️ **Global Settings** — Configure help behavior (field icons, navbar, caching, fallback language)
- 🔄 **RTL Support** — Full Arabic/RTL layout with directional CSS

## 📦 Installation

```bash
bench get-app https://github.com/ArkanLab/arkan_help --branch main
bench --site <site_name> install-app arkan_help
bench migrate
```

### Requirements

- Frappe Framework v16+
- frappe_visual (UI component library)

## 🏗️ Architecture

| Component | Purpose |
|-----------|---------|
| Help Topic | Main content container with keys and categories |
| Help Content | Rich content blocks (Markdown/HTML/Video) per language |
| Help Context | Maps help to DocTypes, fields, views, and routes |
| Help Settings | Global behavior configuration (Single DocType) |
| HelpResolver | 873-line resolution engine with 6-level priority |
| navbar_help.js | Navbar ❓ icon integration |
| help_widget.js | Modal/tooltip display |
| field_help.js | Field ⓘ icon injection |

### Help Resolution Priority

1. Exact match: doctype + fieldname + role + language
2. Field match: doctype + fieldname + language (any role)
3. DocType+Role: doctype + role + language
4. DocType only: doctype + language
5. File-based: `{app}/help/{lang}/{doctype_slug}.md#{fieldname}`
6. Fallback language: repeat 1–5 with fallback_language

### API Endpoints

```python
arkan_help.api.help.get_help(doctype, fieldname, view_type, role)
arkan_help.api.help.get_fields_with_help(doctype)
arkan_help.api.help.has_route_help(route)
arkan_help.api.help.log_help_view(topic)
```

## 📝 Authoring Help Content

Every app should provide file-based help in `{app}/help/{en,ar}/`:

```markdown
---
title: Sales Order
icon: clipboard
context_type: doctype
context_reference: Sales Order
priority: 10
roles: [Sales User, Sales Manager]
---

# Sales Order
Help content for the form.

## # customer
Select the **customer** for this order.
```

## 🤝 Contributing

```bash
cd apps/arkan_help
pre-commit install
```

Tools: ruff, eslint, prettier, pyupgrade

## 📄 License

MIT
