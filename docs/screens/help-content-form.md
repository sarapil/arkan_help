# Help Content Form — Screen Specification
# مواصفات شاشة نموذج محتوى المساعدة

## Screen Identity

- **Route**: `/app/help-content/{name}`
- **Title**: Help Content / محتوى المساعدة
- **Roles**: Help Author (edit), Help Admin (full)
- **Serves Scenarios**: DS-001 to DS-004 from [author.md](../scenarios/author.md)

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ Toolbar: [Save] [Preview] [Publish] [❓ Help]                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Title* _________________________________________________ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐   │
│  │ DocType*        │  │ Field Name      │  │ Language*     │   │
│  │ [Select...]    ▼│  │ [optional]      │  │ [English]    ▼│   │
│  └─────────────────┘  └─────────────────┘  └───────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Content (Markdown Editor)                                │  │
│  │ ┌────────────────────────────────────────────────────┐   │  │
│  │ │ [B] [I] [U] [H1] [H2] [•] [1.] ["] [---] [🔗] [📷]│   │  │
│  │ ├────────────────────────────────────────────────────┤   │  │
│  │ │                                                     │   │  │
│  │ │  # How to create a Sales Order                      │   │  │
│  │ │                                                     │   │  │
│  │ │  Follow these steps...                              │   │  │
│  │ │                                                     │   │  │
│  │ │                                                     │   │  │
│  │ └────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────┐  ┌─────────────────────────┐  │
│  │ Category                    │  │ Tags                    │  │
│  │ [Getting Started         ▼]│  │ [sales, order, create]  │  │
│  └─────────────────────────────┘  └─────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Roles (who sees this help)                               │  │
│  │ ☑ All Users  ☐ Sales User  ☐ Sales Manager  ☐ Admin      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Related Topics (child table)                             │  │
│  │ ┌──────────────────────────────────────────────────────┐ │  │
│  │ │ Help Content          │ Relation Type               │ │  │
│  │ ├──────────────────────────────────────────────────────┤ │  │
│  │ │ Customer Overview     │ See Also                    │ │  │
│  │ │ Sales Invoice Guide   │ Next Step                   │ │  │
│  │ └──────────────────────────────────────────────────────┘ │  │
│  │ [+ Add Row]                                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## frappe_visual Components Used

| Component | Usage | Configuration |
|-----------|-------|---------------|
| `CommandBar` | Quick actions ⌘K | Insert actions |
| `Typewriter` | Title input effect | Placeholder animation |
| `FloatingWindow` | Preview panel | Side-by-side view |
| `ContextMenu` | Right-click editor | Formatting options |
| `ShortcutManager` | ⌘B, ⌘I, etc. | Markdown shortcuts |

---

## CSS Effect Classes (minimum 3)

1. `.fv-fx-glass` — Form card container
2. `.fv-fx-page-enter` — Form entrance animation
3. `.fv-fx-hover-shine` — Toolbar buttons
4. `.fv-fx-gradient-text` — Title when focused

---

## Responsive Breakpoints

| Breakpoint | Layout | Notes |
|------------|--------|-------|
| **Desktop** (>1024px) | Full editor with sidebars | Preview in floating window |
| **Tablet** (768-1024px) | Full width editor | Preview in modal |
| **Mobile** (<768px) | Simplified toolbar | Preview toggle |

---

## RTL Support

- Markdown editor supports RTL input
- Toolbar icons don't mirror (standard)
- Preview respects document direction
- Tag input flows RTL
- Field labels align end

---

## Dark Mode

- Editor background: `var(--control-bg)`
- Syntax highlighting: dark theme
- Toolbar: dark surface with light icons
- Preview: matches user theme

---

## Form Events

```javascript
frappe.ui.form.on("Help Content", {
  refresh(frm) {
    // Add Preview button
    frm.add_custom_button(__("Preview"), () => {
      frappe.visual.floatingWindow({
        title: __("Preview"),
        content: frappe.markdown(frm.doc.content),
        position: "right",
        width: 400,
      });
    });

    // Add Publish button for admins
    if (frappe.user.has_role("Help Admin") && frm.doc.status === "Draft") {
      frm.add_custom_button(__("Publish"), () => {
        frm.set_value("status", "Published");
        frm.save();
      }, __("Actions"));
    }
  },

  content(frm) {
    // Live Markdown validation
    const errors = validateMarkdown(frm.doc.content);
    if (errors.length) {
      frm.set_df_property("content", "description", 
        `⚠️ ${errors.length} ${__("issues found")}`
      );
    }
  },
});
```

---

## Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| Title | Required, max 200 chars | "Title is required" |
| DocType | Required, must exist | "Invalid DocType" |
| Language | Required, valid code | "Select a language" |
| Content | Required, valid Markdown | "Content required" |
| Field Name | If set, must exist in DocType | "Field not found" |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| ⌘+S | Save |
| ⌘+B | Bold |
| ⌘+I | Italic |
| ⌘+K | Insert link |
| ⌘+Shift+P | Preview |
| Escape | Close preview |

---

## Help Integration

- **❓ in Toolbar**: Opens meta-help about creating help content
- **Field ⓘ Icons**: Each field has tooltip
- **Smart Suggestions**: Auto-suggests related topics based on content

---

## GSAP Animations

```javascript
// Form load animation
gsap.from(".form-section", {
  duration: 0.4,
  y: 10,
  opacity: 0,
  stagger: 0.08,
  ease: "power2.out",
});

// Preview slide-in
gsap.from(".preview-panel", {
  duration: 0.3,
  x: 100,
  opacity: 0,
  ease: "power2.out",
});
```

---

## Accessibility

- Markdown editor has ARIA labels
- Toolbar buttons have tooltips
- Focus trap in preview modal
- High contrast editor option
- Screen reader announces save status
