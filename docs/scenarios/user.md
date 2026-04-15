# Help User — Usage Scenarios

# سيناريوهات استخدام مستخدم المساعدة

## Role Overview

- **Title**: Help User / مستخدم المساعدة
- **CAPS Capabilities**: None required (read-only access)
- **Primary DocTypes**: None (consumes help content only)
- **Device**: Desktop / Tablet / Mobile

---

## Daily Scenarios (يومي)

### DS-001: Access Field-Level Help

- **Goal**: Understand what a specific form field does
- **Pre-conditions**: Help content exists for the field
- **Steps**:
  1. Open any DocType form (e.g., Sales Order)
  2. Locate field in question
  3. Click the **ⓘ** info icon next to field label
  4. Read help content in floating panel
  5. Click **Close** or click outside to dismiss
  6. Verify: Help content matches user's language preference
- **Screen**: [field-help-tooltip.md](../screens/field-help-tooltip.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]
- **Error scenarios**:
  - No help for field → "No help available" message with suggestion link

### DS-002: Use Navbar Help Icon

- **Goal**: Access contextual help for current page
- **Pre-conditions**: User is on any desk page
- **Steps**:
  1. Click **❓** help icon in navbar
  2. Help panel opens showing help for current route/DocType
  3. Browse related topics in sidebar
  4. Use search box to find specific topic
  5. Click topic to view content
  6. Rate content as helpful/not helpful
  7. Verify: Help panel respects RTL for Arabic users
- **Screen**: [navbar-help-panel.md](../screens/navbar-help-panel.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

### DS-003: Search Help Content

- **Goal**: Find help on a specific topic
- **Pre-conditions**: Help content exists
- **Steps**:
  1. Click **❓** help icon in navbar
  2. Type search query in search box
  3. Review search results (instant as-you-type)
  4. Click on relevant result
  5. Read help content
  6. Use **Back** to return to results if needed
  7. Verify: Search works in Arabic and English
- **Screen**: [navbar-help-panel.md](../screens/navbar-help-panel.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

### DS-004: Access Form Toolbar Help

- **Goal**: Get help while editing a document
- **Pre-conditions**: On a DocType form
- **Steps**:
  1. Open any DocType form
  2. Click **❓** button in form toolbar
  3. Help panel slides in from right
  4. Shows help for this specific DocType
  5. Scroll through content
  6. Click to close or keep open while working
  7. Verify: Panel doesn't block form fields
- **Screen**: [form-help-sidebar.md](../screens/form-help-sidebar.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ❌]

---

## Weekly Scenarios (أسبوعي)

### WS-001: Browse Help Center

- **Goal**: Explore available help topics
- **Pre-conditions**: None
- **Steps**:
  1. Navigate to Help Center (`/app/arkan-help`)
  2. Browse topic categories
  3. Click on category to expand
  4. Select specific topic
  5. Read content and related articles
  6. Use breadcrumb to navigate back
  7. Verify: All topics accessible without special permissions
- **Screen**: [help-center.md](../screens/help-center.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

### WS-002: Follow Onboarding Tutorial

- **Goal**: Learn a new feature through guided walkthrough
- **Pre-conditions**: Onboarding content exists
- **Steps**:
  1. Navigate to relevant feature page
  2. Click **Take Tour** button if visible
  3. Follow step-by-step highlights
  4. Click **Next** to proceed through steps
  5. Complete actions as prompted
  6. Click **Finish** when done
  7. Verify: Progress is saved if user exits early
- **Screen**: [onboarding-tour.md](../screens/onboarding-tour.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ❌]

### WS-003: View Getting Started Guide

- **Goal**: Learn the basics of an app
- **Pre-conditions**: App has getting started content
- **Steps**:
  1. Navigate to app workspace
  2. Click **Getting Started** card
  3. Read overview content
  4. Follow links to key features
  5. Try suggested first steps
  6. Mark steps as complete
  7. Verify: Progress persists across sessions
- **Screen**: [getting-started.md](../screens/getting-started.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

---

## Monthly Scenarios (شهري)

### MS-001: Provide Help Feedback

- **Goal**: Report that help content is incorrect or missing
- **Pre-conditions**: Viewing help content
- **Steps**:
  1. Read help content
  2. Click **Not Helpful** if content doesn't help
  3. Optional: Enter specific feedback in text box
  4. Click **Submit Feedback**
  5. Verify: Thank you message displayed
- **Screen**: [feedback-form.md](../screens/feedback-form.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

### MS-002: Request New Help Topic

- **Goal**: Ask for help on a topic not covered
- **Pre-conditions**: None
- **Steps**:
  1. Open navbar help panel
  2. Search for topic (no results)
  3. Click **Request Help on This Topic**
  4. Describe what you need help with
  5. Specify which DocType/feature
  6. Submit request
  7. Verify: Confirmation shown, request tracked
- **Screen**: [topic-request.md](../screens/topic-request.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

---

## Exception Scenarios (استثنائي)

### ES-001: Help Not Available

- **Goal**: Handle missing help content gracefully
- **Pre-conditions**: No help content for current context
- **Steps**:
  1. Click field ⓘ icon or navbar ❓
  2. See "No help available for this item" message
  3. View suggested related topics
  4. Or click "Request help for this topic"
  5. Verify: User not blocked, alternatives provided
- **Screen**: [no-help-available.md](../screens/no-help-available.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

### ES-002: Offline Help Access

- **Goal**: Access help when disconnected
- **Pre-conditions**: Previously viewed help content
- **Steps**:
  1. Lose network connectivity
  2. Click on help icon
  3. See cached help content (if available)
  4. Or see "You're offline" message
  5. View download option for offline pack
  6. Verify: Graceful degradation, no errors
- **Screen**: [offline-message.md](../screens/offline-message.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

### ES-003: Language Fallback

- **Goal**: Get help when preferred language not available
- **Pre-conditions**: User's language = Arabic, content only in English
- **Steps**:
  1. Click help for item without Arabic content
  2. System shows English content with notice
  3. Banner: "This content is not yet available in Arabic"
  4. User can still read English version
  5. Optional: Request Arabic translation
  6. Verify: Fallback is seamless, user informed
- **Screen**: [language-fallback.md](../screens/language-fallback.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]
