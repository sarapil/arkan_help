# Help Dashboard — Screen Specification

# مواصفات شاشة لوحة تحكم المساعدة

## Screen Identity

- **Route**: `/app/arkan-help`
- **Title**: Help Dashboard / لوحة تحكم المساعدة
- **Roles**: All users (view), Help Admin (full)
- **Serves Scenarios**: DS-001, WS-001 from [admin.md](../scenarios/admin.md)

---

## Layout Structure

```
┌────────────────────────────────────────────────────────────────┐
│  Scene Header (SVG Office Scene with KPI Frames)               │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                          │
│  │Topics│ │Views │ │Rating│ │Authors│                         │
│  │ 156  │ │28.4K │ │ 87%  │ │  12  │                          │
│  └──────┘ └──────┘ └──────┘ └──────┘                          │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐ ┌─────────────────────┐              │
│  │ Top Viewed Topics   │ │ Recent Activity     │              │
│  │ ├─ Sales Order      │ │ ├─ Content updated  │              │
│  │ ├─ Customer         │ │ ├─ New topic added  │              │
│  │ ├─ Purchase Order   │ │ └─ Translation done │              │
│  │ └─ Item             │ └─────────────────────┘              │
│  └─────────────────────┘                                       │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐ ┌─────────────────────┐              │
│  │ Missing Help        │ │ Needs Translation   │              │
│  │ ├─ Journal Entry    │ │ ├─ Sales Order (AR) │              │
│  │ ├─ Stock Entry      │ │ ├─ Customer (AR)    │              │
│  │ └─ Asset            │ │ └─ Item (AR)        │              │
│  └─────────────────────┘ └─────────────────────┘              │
└────────────────────────────────────────────────────────────────┘
```

---

## frappe_visual Components Used

| Component           | Usage                  | Configuration                            |
| ------------------- | ---------------------- | ---------------------------------------- |
| `scenePresetOffice` | Header with KPI frames | 4 frames: topics, views, rating, authors |
| `sceneDataBinder`   | Live KPI data binding  | 30s refresh interval                     |
| `DataCard`          | Statistic cards        | CSS class: `.fv-fx-hover-lift`           |
| `VisualTreeView`    | Topic hierarchy        | Expandable tree                          |
| `timeline`          | Recent activity feed   | Auto-scroll                              |
| `Sparkline`         | View trends            | 7-day mini chart                         |
| `BottomSheet`       | Mobile actions         | Slide-up on mobile                       |

---

## CSS Effect Classes (minimum 3)

1. `.fv-fx-glass` — Scene dashboard container
2. `.fv-fx-hover-lift` — KPI cards on hover
3. `.fv-fx-page-enter` — Fade-in entrance animation
4. `.fv-fx-gradient-animated` — Header gradient background
5. `.fv-fx-mouse-glow` — Cards follow cursor glow

---

## Responsive Breakpoints

| Breakpoint              | Layout                     | Notes                    |
| ----------------------- | -------------------------- | ------------------------ |
| **Desktop** (>1024px)   | 2-column grid below scene  | Full scene dashboard     |
| **Tablet** (768-1024px) | Stacked cards              | Scene simplified         |
| **Mobile** (<768px)     | Single column, BottomSheet | Scene hidden, cards only |

---

## RTL Support

- Scene elements mirror in RTL mode
- KPI frames read right-to-left
- Tree view expander icons flip
- Activity timeline flows RTL
- All margins use `margin-inline-start`

---

## Dark Mode

All colors via CSS variables:

- `--ah-primary: #10B981`
- `--ah-surface: var(--card-bg)`
- `--ah-text: var(--text-color)`
- Scene theme auto-switches: warm → dark

---

## JavaScript Implementation

```javascript
// Dashboard initialization
frappe.pages["arkan-help"].on_page_load = async function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __("Help Dashboard"),
    single_column: true,
  });

  // Scene Dashboard Header
  const scene = await frappe.visual.scenePresetOffice({
    container: page.main,
    theme: frappe.ui.color.is_dark() ? "dark" : "warm",
    frames: [
      { label: __("Topics"), value: "0", status: "info" },
      { label: __("Views"), value: "0", status: "success" },
      { label: __("Rating"), value: "0%", status: "warning" },
      { label: __("Authors"), value: "0", status: "info" },
    ],
  });

  // Bind live data
  await frappe.visual.sceneDataBinder({
    engine: scene,
    frames: [
      {
        label: "Topics",
        doctype: "Help Content",
        aggregate: "count",
        filters: { status: "Published" },
      },
      {
        label: "Views",
        doctype: "Help View Log",
        aggregate: "count",
        format: "%sk",
      },
      {
        label: "Rating",
        doctype: "Help Feedback",
        aggregate: "avg",
        field: "rating",
        format: "%s%",
      },
      {
        label: "Authors",
        doctype: "Help Content",
        aggregate: "distinct",
        field: "owner",
      },
    ],
    refreshInterval: 30000,
  });
};
```

---

## Data Requirements

### API Endpoints

| Endpoint                                     | Method | Purpose            |
| -------------------------------------------- | ------ | ------------------ |
| `arkan_help.api.v1.dashboard.get_stats`      | GET    | Dashboard KPIs     |
| `arkan_help.api.v1.dashboard.get_top_topics` | GET    | Most viewed topics |
| `arkan_help.api.v1.dashboard.get_activity`   | GET    | Recent activity    |
| `arkan_help.api.v1.dashboard.get_coverage`   | GET    | Coverage report    |

### KPIs

| KPI            | Source        | Formula                     |
| -------------- | ------------- | --------------------------- |
| Total Topics   | Help Content  | `COUNT(status='Published')` |
| Total Views    | Help View Log | `SUM(view_count)`           |
| Helpful Rate   | Help Feedback | `AVG(helpful=1) * 100`      |
| Active Authors | Help Content  | `COUNT(DISTINCT owner)`     |

---

## Accessibility

- All KPI frames have `aria-label`
- Tree view supports keyboard navigation
- Color contrast ratio ≥ 4.5:1
- Focus indicators visible
- Screen reader announces live data updates

---

## GSAP Animations

```javascript
// Entrance animation
gsap.from(".ah-dashboard-card", {
  duration: 0.6,
  y: 20,
  opacity: 0,
  stagger: 0.1,
  ease: "power2.out",
});

// KPI number animation
gsap.from(".kpi-value", {
  textContent: 0,
  duration: 1,
  ease: "power1.out",
  snap: { textContent: 1 },
});
```

---

## Help Integration

- **❓ Button**: Opens help for "Help Dashboard" topic
- **Tooltip**: KPI labels have hover explanations
- **Link**: "How to use this dashboard" at bottom
