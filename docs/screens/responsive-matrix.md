# Responsive Matrix — مصفوفة الاستجابة

## Breakpoints

| Breakpoint | Width           | Layout                      | Touch Target |
| ---------- | --------------- | --------------------------- | ------------ |
| Mobile     | 320px – 767px   | Single column, BottomSheet  | 44px minimum |
| Tablet     | 768px – 1023px  | Two column, collapsible     | 40px minimum |
| Desktop    | 1024px – 1439px | Full layout with sidebar    | Standard     |
| Large      | 1440px+         | Extended layout with panels | Standard     |

---

## Per-Screen Behavior

| Screen                 | Mobile                      | Tablet               | Desktop           | Large             |
| ---------------------- | --------------------------- | -------------------- | ----------------- | ----------------- |
| **Dashboard**          | ✅ 2-col KPIs, scene hidden | ✅ Scene simplified  | ✅ Full scene     | ✅ Extended       |
| **Help Content Form**  | ❌ Not recommended          | ✅ Full width editor | ✅ With preview   | ✅ Side-by-side   |
| **Navbar Help Panel**  | ✅ BottomSheet              | ✅ Floating 340px    | ✅ Floating 380px | ✅ Floating 380px |
| **Field Help Tooltip** | ✅ Bottom aligned           | ✅ Standard          | ✅ Standard       | ✅ Standard       |
| **Help Center**        | ✅ Accordion                | ✅ Grid              | ✅ Grid + sidebar | ✅ Full           |
| **Analytics Report**   | ✅ Stacked charts           | ✅ Grid              | ✅ Dashboard      | ✅ Extended       |

---

## Component-Specific Behaviors

### Scene Dashboard

| Breakpoint | Behavior                            |
| ---------- | ----------------------------------- |
| Mobile     | Hidden, replaced with KPI grid only |
| Tablet     | Simplified scene (no animation)     |
| Desktop    | Full scene with all elements        |
| Large      | Extended scene with more detail     |

### Navbar Help Panel

| Breakpoint | Behavior                                   |
| ---------- | ------------------------------------------ |
| Mobile     | BottomSheet (swipe to dismiss)             |
| Tablet     | Floating panel, reduced width              |
| Desktop    | Floating panel on opposite side of sidebar |
| Large      | Same as desktop                            |

### Help Content Editor

| Breakpoint | Behavior                            |
| ---------- | ----------------------------------- |
| Mobile     | Not supported (redirect to desktop) |
| Tablet     | Full-width, modal preview           |
| Desktop    | Editor with inline preview          |
| Large      | Side-by-side: editor + live preview |

---

## Touch Interaction Matrix

| Element          | Mobile                   | Tablet             |
| ---------------- | ------------------------ | ------------------ |
| KPI Cards        | Tap → detail sheet       | Tap → detail modal |
| Tree nodes       | Tap → expand/collapse    | Same               |
| Search           | Focus → virtual keyboard | Same as desktop    |
| Help icon (ⓘ)    | Long press → tooltip     | Tap → tooltip      |
| Feedback buttons | Tap → confirm            | Tap                |

---

## Animation Adjustments

| Breakpoint | GSAP                              | Scene          | Transitions  |
| ---------- | --------------------------------- | -------------- | ------------ |
| Mobile     | Disabled (prefers-reduced-motion) | None           | Fade only    |
| Tablet     | Simplified                        | Static         | Slide + fade |
| Desktop    | Full                              | Animated       | Full effects |
| Large      | Full                              | Full animation | Full effects |

---

## Testing Checklist

- [ ] Test at exactly 320px width
- [ ] Test at 768px boundary
- [ ] Test at 1024px boundary
- [ ] Test with touch simulation
- [ ] Test with RTL + all breakpoints
- [ ] Test with dark mode + all breakpoints
- [ ] Verify no horizontal scroll
- [ ] Verify touch targets ≥ 44px on mobile
