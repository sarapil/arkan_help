# Help Author — Usage Scenarios
# سيناريوهات استخدام مؤلف المساعدة

## Role Overview

- **Title**: Help Author / مؤلف المساعدة
- **CAPS Capabilities**: `AH_author_content`, `AH_manage_topics`
- **Primary DocTypes**: Help Content, Help Topic, Help Context
- **Device**: Desktop / Tablet

---

## Daily Scenarios (يومي)

### DS-001: Create New Help Content

- **Goal**: Author a new help article for a DocType or field
- **Pre-conditions**: User has `AH_author_content` capability
- **Steps**:
  1. Navigate to Help Content List (`/app/help-content`)
  2. Click **+ Add Help Content** button
  3. Select target DocType from dropdown
  4. Optionally specify field name for field-level help
  5. Select language (Arabic/English)
  6. Write content using Markdown editor
  7. Add tags and category
  8. Click **Save** (creates Draft)
  9. Preview content using **Preview** button
  10. Verify: Draft is created with author attribution
- **Screen**: [help-content-form.md](../screens/help-content-form.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ❌]
- **Error scenarios**: 
  - Missing required fields → Validation error with field highlight
  - Duplicate content for same DocType+field+language → Warning prompt

### DS-002: Edit Existing Help Content

- **Goal**: Update an existing help article
- **Pre-conditions**: Content exists, user has edit permission
- **Steps**:
  1. Navigate to Help Content List
  2. Use search/filter to find target content
  3. Click on content row to open form
  4. Modify content in Markdown editor
  5. Use **Preview** to verify changes
  6. Click **Save**
  7. Verify: Modified timestamp updated, version history recorded
- **Screen**: [help-content-form.md](../screens/help-content-form.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ❌]
- **Error scenarios**:
  - Concurrent edit conflict → Merge dialog shown

### DS-003: Link Related Topics

- **Goal**: Connect help articles with related content
- **Pre-conditions**: Multiple help contents exist
- **Steps**:
  1. Open Help Content form
  2. Scroll to **Related Topics** section
  3. Click **Add Row** in child table
  4. Search and select related Help Content
  5. Save the parent document
  6. Verify: Related topics appear in help viewer sidebar
- **Screen**: [help-content-form.md](../screens/help-content-form.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ❌]

### DS-004: Add Images to Help Content

- **Goal**: Embed screenshots or diagrams in help article
- **Pre-conditions**: Image files ready
- **Steps**:
  1. Open Help Content in edit mode
  2. Position cursor in Markdown editor
  3. Click **Insert Image** toolbar button
  4. Upload image via file dialog or drag-and-drop
  5. Add alt text for accessibility
  6. Save and preview
  7. Verify: Image renders correctly in preview
- **Screen**: [help-content-form.md](../screens/help-content-form.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ❌]
- **Error scenarios**:
  - File too large → Size limit error
  - Unsupported format → Format error message

---

## Weekly Scenarios (أسبوعي)

### WS-001: Review Content Analytics

- **Goal**: Understand which help content is most/least useful
- **Pre-conditions**: User has `AH_view_analytics` capability
- **Steps**:
  1. Navigate to Help Dashboard (`/app/arkan-help`)
  2. Review **Top Viewed Topics** section
  3. Check **Least Viewed Topics** for potential improvements
  4. Review **User Satisfaction** metrics
  5. Export report if needed
  6. Verify: Data reflects recent activity (within 24h)
- **Screen**: [dashboard.md](../screens/dashboard.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

### WS-002: Manage Topic Hierarchy

- **Goal**: Organize help topics into categories
- **Pre-conditions**: User has `AH_manage_topics` capability
- **Steps**:
  1. Navigate to Help Topic List
  2. Create new topic or edit existing
  3. Set parent topic for hierarchy
  4. Set display order (priority)
  5. Save changes
  6. Verify: Topic tree reflects new structure
- **Screen**: [topic-management.md](../screens/topic-management.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ❌]

### WS-003: Add Translations

- **Goal**: Create Arabic translation for English content
- **Pre-conditions**: English content exists, user has `AH_manage_translations`
- **Steps**:
  1. Open Help Content (English version)
  2. Click **Add Translation** button
  3. Select Arabic language
  4. Use side-by-side view: English source | Arabic target
  5. Translate content maintaining Markdown structure
  6. Save translation
  7. Verify: Help viewer shows Arabic for Arabic users
- **Screen**: [translation-editor.md](../screens/translation-editor.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ❌] [mobile ❌]

---

## Monthly Scenarios (شهري)

### MS-001: Content Audit

- **Goal**: Review all help content for accuracy and completeness
- **Pre-conditions**: Sufficient content exists
- **Steps**:
  1. Navigate to Help Content List
  2. Filter by **Last Modified** > 30 days ago
  3. Review each item for accuracy
  4. Mark outdated content for update
  5. Archive obsolete content
  6. Document findings in audit log
  7. Verify: Content freshness improved
- **Screen**: [help-content-list.md](../screens/help-content-list.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ❌]

### MS-002: Coverage Report

- **Goal**: Identify DocTypes without help content
- **Pre-conditions**: Admin access
- **Steps**:
  1. Navigate to Help Analytics Report
  2. Run **Coverage Report**
  3. Review list of DocTypes missing help
  4. Prioritize high-traffic DocTypes
  5. Create task list for new content
  6. Verify: Coverage percentage calculated
- **Screen**: [analytics-report.md](../screens/analytics-report.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ✅] [mobile ✅]

---

## Exception Scenarios (استثنائي)

### ES-001: Handle Content Conflict

- **Goal**: Resolve when two authors edit same content simultaneously
- **Pre-conditions**: Concurrent editing detected
- **Steps**:
  1. System shows conflict notification
  2. Review conflicting changes in diff view
  3. Choose: Accept mine / Accept theirs / Merge manually
  4. If merge: Edit combined content
  5. Save resolved version
  6. Verify: Single canonical version exists
- **Screen**: [conflict-resolution.md](../screens/conflict-resolution.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ❌] [mobile ❌]

### ES-002: Bulk Import Help Content

- **Goal**: Import multiple help articles from files
- **Pre-conditions**: User has `AH_manage_topics`, files prepared
- **Steps**:
  1. Navigate to Help Settings
  2. Click **Import Content**
  3. Upload ZIP with Markdown files following naming convention
  4. Review import preview with mapped DocTypes
  5. Confirm import
  6. Review import log for errors
  7. Verify: Content appears in list with correct metadata
- **Screen**: [import-wizard.md](../screens/import-wizard.md)
- **Breakpoints**: Works on [desktop ✅] [tablet ❌] [mobile ❌]
- **Error scenarios**:
  - Invalid file format → Format error with details
  - Partial import failure → Log shows which files failed
