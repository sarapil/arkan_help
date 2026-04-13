# Navbar Help Panel — Screen Specification
# مواصفات شاشة لوحة المساعدة في شريط التنقل

## Screen Identity

- **Route**: N/A (overlay component)
- **Title**: Help / المساعدة
- **Roles**: All users
- **Serves Scenarios**: DS-002, DS-003 from [user.md](../scenarios/user.md)

---

## Layout Structure

```
┌─────────────────────────────────────────┐
│  🔍 Search help...              [×]     │
├─────────────────────────────────────────┤
│                                          │
│  📄 Sales Order                          │
│  Help for the current page               │
│  ────────────────────────────            │
│                                          │
│  ## Creating a Sales Order               │
│                                          │
│  1. Navigate to Selling > Sales Order    │
│  2. Click "+ Add Sales Order"            │
│  3. Select Customer                      │
│  4. Add items...                         │
│                                          │
│  [Read more →]                           │
│                                          │
├─────────────────────────────────────────┤
│  Related Topics                          │
│  ├─ Customer Management                  │
│  ├─ Items & Pricing                      │
│  └─ Delivery Note                        │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │ Was this helpful?  [👍] [👎]   │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## frappe_visual Components Used

| Component | Usage | Configuration |
|-----------|-------|---------------|
| `FloatingWindow` | Panel container | position: sidebar-opposite |
| `CommandBar` | Search ⌘K integration | help-specific actions |
| `ContextPanel` | Content display | scrollable, resizable |
| `Ripple` | Click feedback | button interactions |
| `bilingualTooltip` | AR/EN hints | auto for all elements |

---

## CSS Effect Classes (minimum 3)

1. `.fv-fx-glass` — Panel background with blur
2. `.fv-fx-page-enter` — Slide-in animation
3. `.fv-fx-hover-lift` — Related topic cards
4. `.fv-fx-ripple` — Button click effect

---

## Responsive Breakpoints

| Breakpoint | Behavior | Notes |
|------------|----------|-------|
| **Desktop** (>1024px) | Floating panel, 380px width | Opens opposite sidebar |
| **Tablet** (768-1024px) | Floating panel, 340px width | Same behavior |
| **Mobile** (<768px) | Full-width BottomSheet | Swipe down to close |

---

## RTL Support

- Panel opens on LEFT for RTL (opposite of sidebar)
- Search input direction: auto
- Content flows RTL for Arabic
- Close button stays at top-right
- Related topics list flows RTL

---

## Dark Mode

- Panel uses `var(--modal-bg)`
- Text uses `var(--text-color)`
- Links use `var(--primary)`
- Feedback buttons adapt to theme

---

## JavaScript Implementation

```javascript
// Navbar help icon click handler
class NavbarHelp {
  constructor() {
    this.panel = null;
    this.bindEvents();
  }

  bindEvents() {
    $(document).on("click", ".navbar-help-icon", () => this.toggle());
    frappe.router.on("change", () => this.updateContent());
  }

  async toggle() {
    if (this.panel) {
      this.panel.close();
      this.panel = null;
      return;
    }

    this.panel = await frappe.visual.floatingWindow({
      title: __("Help"),
      position: document.dir === "rtl" ? "left" : "right",
      width: 380,
      cssClass: "navbar-help-panel fv-fx-glass fv-fx-page-enter",
      content: await this.getHelpContent(),
      onClose: () => { this.panel = null; },
    });
  }

  async getHelpContent() {
    const route = frappe.get_route();
    const doctype = this.getDocTypeFromRoute(route);
    
    const help = await frappe.call({
      method: "arkan_help.api.v1.help.get_help",
      args: { doctype, route: route.join("/") },
    });

    return this.renderHelp(help.message);
  }

  renderHelp(data) {
    if (!data) {
      return `
        <div class="no-help">
          <p>${__("No help available for this page.")}</p>
          <button class="btn btn-sm btn-primary">
            ${__("Request Help")}
          </button>
        </div>
      `;
    }

    return `
      <div class="help-content">
        <h4>${data.title}</h4>
        <div class="help-body">${frappe.markdown(data.content)}</div>
        ${this.renderRelated(data.related)}
        ${this.renderFeedback(data.name)}
      </div>
    `;
  }

  renderRelated(related) {
    if (!related?.length) return "";
    
    return `
      <div class="related-topics">
        <h5>${__("Related Topics")}</h5>
        <ul>
          ${related.map(r => `
            <li>
              <a href="#" data-help="${r.name}">${r.title}</a>
            </li>
          `).join("")}
        </ul>
      </div>
    `;
  }

  renderFeedback(helpName) {
    return `
      <div class="help-feedback">
        <span>${__("Was this helpful?")}</span>
        <button class="btn-feedback" data-helpful="1" data-help="${helpName}">
          👍
        </button>
        <button class="btn-feedback" data-helpful="0" data-help="${helpName}">
          👎
        </button>
      </div>
    `;
  }
}

// Initialize
frappe.provide("arkan_help");
arkan_help.navbarHelp = new NavbarHelp();
```

---

## Search Behavior

| Action | Behavior |
|--------|----------|
| Type in search | Debounced (300ms) instant search |
| Enter key | Navigate to first result |
| Arrow keys | Navigate results |
| Escape | Clear search / Close panel |
| Click result | Show help content |

---

## Feedback Flow

1. User clicks 👍 or 👎
2. Feedback sent to `arkan_help.api.v1.feedback.submit`
3. Button shows selected state
4. Thank you message appears
5. Optional: Show follow-up prompt for 👎

---

## GSAP Animations

```javascript
// Panel slide-in
gsap.from(".navbar-help-panel", {
  duration: 0.3,
  x: document.dir === "rtl" ? -100 : 100,
  opacity: 0,
  ease: "power2.out",
});

// Content fade-in
gsap.from(".help-content > *", {
  duration: 0.4,
  y: 10,
  opacity: 0,
  stagger: 0.05,
  ease: "power2.out",
});

// Feedback button click
gsap.to(".btn-feedback.clicked", {
  scale: 1.2,
  duration: 0.1,
  yoyo: true,
  repeat: 1,
});
```

---

## Accessibility

- Panel has `role="dialog"` and `aria-label`
- Search input has `role="searchbox"`
- Close button has `aria-label="Close"`
- Focus trapped within panel when open
- Escape key closes panel
- Results announced to screen reader

---

## Cache Strategy

- Help content cached in localStorage
- Cache key: `ah_help_{route}_{lang}`
- TTL: 5 minutes
- Invalidated on Help Content update via realtime

---

## Error States

| State | Display |
|-------|---------|
| Loading | Skeleton loader animation |
| No content | "No help available" + request link |
| Network error | Retry button + offline notice |
| Offline | Show cached content if available |
