<!-- Post Type: Community Forum | Platform: discuss.frappe.io, GitHub Discussions -->
<!-- Target: Frappe developers and power users -->
<!-- Last Updated: 2026-04-04 -->

# [Announcement] Arkan Help — Contextual Help System for Frappe Apps | Open Source

Hi Frappe Community! 👋

We're excited to share **Arkan Help**, a new open-source documentation app for Frappe/ERPNext.

## What it does

✅ Field-Level Help Icons (ⓘ)
✅ Navbar Help Button (❓)
✅ 6-Level Specificity Resolution
✅ File-Based Help (Markdown)
✅ Role-Specific Help Content
✅ Bilingual (Arabic/English) Support
✅ Help Analytics & Tracking

## Why we built it

- Users don't know how to use Frappe forms
- Training costs for new employees
- No inline help system in Frappe
- Help content not role-specific

We couldn't find a good documentation solution that integrates natively with ERPNext, so we built one.

## Tech Stack

- **Backend:** Python, Frappe Framework v16
- **Frontend:** JavaScript, Frappe UI, frappe_visual components
- **Database:** MariaDB (standard Frappe)
- **License:** MIT
- **Dependencies:** frappe_visual, caps, arkan_help

## Installation

```bash
bench get-app https://github.com/sarapil/arkan_help
bench --site your-site install-app arkan_help
bench --site your-site migrate
```

## Screenshots

[Screenshots will be added to the GitHub repository]

## Roadmap

We're actively developing and would love community feedback on:
1. What features would you like to see?
2. What integrations are most important?
3. Any bugs or issues you encounter?

## Links

- 🔗 **GitHub:** https://github.com/sarapil/arkan_help
- 📖 **Docs:** https://arkan.it.com/arkan_help/docs
- 🏪 **Marketplace:** Frappe Cloud Marketplace
- 📧 **Contact:** support@arkan.it.com

## About Arkan Lab

We're building a complete ecosystem of open-source business apps for Frappe/ERPNext, covering hospitality, construction, CRM, communications, coworking, and more. All apps are designed to work together seamlessly.

Check out our full portfolio: https://arkan.it.com

---

*Feedback and contributions welcome! Star ⭐ the repo if you find it useful.*
