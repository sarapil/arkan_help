# Screenshots — Marketplace Assets

# صور الشاشة — أصول المتجر

## Purpose

This directory contains high-quality screenshots for:

- Frappe Cloud Marketplace listing
- Documentation illustrations
- Marketing materials
- User guides

## Requirements

### Technical Specifications

| Attribute                | Requirement            |
| ------------------------ | ---------------------- |
| **Minimum Resolution**   | 1280×800 pixels        |
| **Preferred Resolution** | 1920×1080 pixels       |
| **Format**               | PNG (lossless) or WebP |
| **Color Profile**        | sRGB                   |
| **Aspect Ratio**         | 16:9 or 16:10          |

### Content Guidelines

1. **Clean browser chrome** — Use incognito/private window
2. **No personal data** — Use demo/test data only
3. **Consistent theme** — Use default light theme (dark mode optional as separate set)
4. **Full feature visibility** — Show complete screens, not cropped views
5. **Arabic + English** — Provide both language versions when possible
6. **Branded** — Show Arkan Help branding clearly

---

## Required Screenshots (Minimum 5)

### 1. Dashboard Overview (`01-dashboard.png`)

- **Content**: Help Center dashboard with KPIs and scene visualization
- **Focus**: Scene dashboard with topic count, views, rating, authors
- **State**: Data populated, charts active

### 2. Help Content Creation (`02-content-editor.png`)

- **Content**: Help Content form in edit mode
- **Focus**: Markdown editor with live preview
- **State**: Content being edited, preview visible

### 3. Contextual Help (`03-field-help.png`)

- **Content**: Form with field-level help tooltip open
- **Focus**: ⓘ icon clicked, help popup visible
- **State**: Tooltip showing relevant help text

### 4. Navbar Help Panel (`04-navbar-help.png`)

- **Content**: Navbar with help panel open
- **Focus**: Search, content display, related topics
- **State**: Help content visible, search functional

### 5. Analytics & Coverage (`05-analytics.png`)

- **Content**: Help analytics report or coverage view
- **Focus**: Metrics, charts, coverage percentages
- **State**: Data visualizations populated

### 6. Mobile Responsive (Optional) (`06-mobile.png`)

- **Content**: Mobile view of help panel
- **Focus**: BottomSheet behavior
- **State**: Touch-friendly interface

### 7. Dark Mode (Optional) (`07-dark-mode.png`)

- **Content**: Dashboard in dark mode
- **Focus**: Theme consistency
- **State**: Full dark mode active

### 8. RTL Arabic (Optional) (`08-rtl-arabic.png`)

- **Content**: Dashboard with Arabic language
- **Focus**: RTL layout, Arabic text
- **State**: Proper mirroring and text direction

---

## File Naming Convention

```
<order>-<description>[-<variant>].png

Examples:
01-dashboard.png
01-dashboard-dark.png
02-content-editor.png
02-content-editor-ar.png
03-field-help-tooltip.png
```

---

## Screenshot Capture Guide

### Using Browser DevTools

```javascript
// Set consistent viewport
window.resizeTo(1920, 1080);

// Enable high-DPI capture
window.devicePixelRatio = 2;

// Capture full page
// Chrome: ctrl+shift+p → "Capture full size screenshot"
```

### Using Frappe Commands

```bash
# Generate screenshots programmatically (if tool available)
bench --site dev.localhost execute arkan_help.utils.screenshots.capture --args '["dashboard", "content-editor"]'
```

### Manual Checklist

- [ ] Log in as Administrator or demo user
- [ ] Set language to English (and Arabic for AR versions)
- [ ] Load test data if not present
- [ ] Ensure no browser extensions visible
- [ ] Hide bookmarks bar
- [ ] Use consistent zoom level (100%)
- [ ] Capture full screen, not selection
- [ ] Verify no sensitive data visible

---

## Current Status

| Screenshot            | Status     | Language | Dark Mode |
| --------------------- | ---------- | -------- | --------- |
| 01-dashboard.png      | ⏳ Pending | EN       | ❌        |
| 01-dashboard-ar.png   | ⏳ Pending | AR       | ❌        |
| 02-content-editor.png | ⏳ Pending | EN       | ❌        |
| 03-field-help.png     | ⏳ Pending | EN       | ❌        |
| 04-navbar-help.png    | ⏳ Pending | EN       | ❌        |
| 05-analytics.png      | ⏳ Pending | EN       | ❌        |

---

## Usage in Marketplace

Reference in [.github/store/arkan_help.yml](../../../../.github/store/arkan_help.yml):

```yaml
screenshots:
  - path: "docs/screenshots/01-dashboard.png"
    caption:
      en: "Help Center Dashboard — KPIs and scene visualization"
      ar: "لوحة تحكم مركز المساعدة — المؤشرات والعرض المرئي"
  - path: "docs/screenshots/02-content-editor.png"
    caption:
      en: "Markdown Editor — Create help content with live preview"
      ar: "محرر Markdown — إنشاء محتوى المساعدة مع معاينة مباشرة"
  # ...
```
