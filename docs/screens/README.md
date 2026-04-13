# Screen Designs — تصاميم الشاشات

This directory contains visual screen design specifications for **Arkan Help**.

---

## Design Standards

Every screen MUST comply with:

- ✅ At least 1 `frappe_visual` component
- ✅ At least 3 `.fv-fx-*` CSS effect classes
- ✅ GSAP entrance animation
- ✅ CSS Logical Properties (no `margin-left`, use `margin-inline-start`)
- ✅ Dark mode compatible (CSS variables only)
- ✅ RTL support
- ✅ Responsive: 320px → 4K

---

## Screen Index

| Screen | File | Primary Role | Serves Scenarios |
|--------|------|--------------|------------------|
| Help Dashboard | [dashboard.md](dashboard.md) | Admin, Author | WS-001 (Author), DS-001 (Admin) |
| Help Content Form | [help-content-form.md](help-content-form.md) | Author | DS-001 to DS-004 (Author) |
| Navbar Help Panel | [navbar-help-panel.md](navbar-help-panel.md) | User | DS-002, DS-003 (User) |

---

## Visual Components by Screen

| Screen | Components Used |
|--------|-----------------|
| Dashboard | `scenePresetLibrary`, `sceneDataBinder`, `DataCard`, `Sparkline`, `timeline` |
| Help Content Form | `CommandBar`, `FloatingWindow`, `ContextMenu`, `ShortcutManager` |
| Navbar Help Panel | `FloatingWindow`, `ContextPanel`, `Ripple`, `bilingualTooltip` |

---

## CSS Effects by Screen

| Screen | Effects |
|--------|---------|
| Dashboard | `.fv-fx-glass`, `.fv-fx-hover-lift`, `.fv-fx-page-enter`, `.fv-fx-gradient-animated` |
| Help Content Form | `.fv-fx-glass`, `.fv-fx-page-enter`, `.fv-fx-hover-shine`, `.fv-fx-gradient-text` |
| Navbar Help Panel | `.fv-fx-glass`, `.fv-fx-page-enter`, `.fv-fx-hover-lift`, `.fv-fx-ripple` |

---

## Responsive Matrix

See [responsive-matrix.md](responsive-matrix.md) for breakpoint behavior across all screens.

---

## Creating a New Screen Spec

1. Copy an existing screen spec as template
2. Update all sections: Layout, Components, CSS Effects, Breakpoints
3. Link to scenarios it serves
4. Add to this README index
5. Update responsive-matrix.md
