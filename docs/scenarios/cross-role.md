# Cross-Role Scenarios — Help Workflows

# سيناريوهات متعددة الأدوار — سير عمل المساعدة

## Overview

This document describes scenarios that involve multiple roles working together on help content workflows.

---

## Workflow CR-001: Content Creation to Publication

**Roles Involved**: Help Author → Help Admin → Help User

### Phase 1: Author Creates Content

- **Actor**: Help Author
- **Scenario**: DS-001 from [author.md](author.md)
- **Output**: Help Content in Draft status

### Phase 2: Admin Reviews and Publishes

- **Actor**: Help Admin
- **Pre-conditions**: Draft content exists
- **Steps**:
  1. Navigate to Help Content List
  2. Filter by status = "Draft"
  3. Open content for review
  4. Check accuracy, formatting, language
  5. If changes needed: Add review comments, return to author
  6. If approved: Change status to "Published"
  7. Click Save
  8. Verify: Content now visible to users
- **Screen**: [help-content-form.md](../screens/help-content-form.md)

### Phase 3: User Consumes Content

- **Actor**: Help User
- **Scenario**: DS-001 from [user.md](user.md)
- **Verification**: User can access newly published content

---

## Workflow CR-002: Translation Workflow

**Roles Involved**: Help Author (English) → Help Author (Arabic) → Help Admin

### Phase 1: English Content Created

- **Actor**: Help Author (English expertise)
- **Output**: English Help Content, Published

### Phase 2: Arabic Translation

- **Actor**: Help Author (Arabic expertise)
- **Pre-conditions**: English content published
- **Steps**:
  1. Open English Help Content
  2. Click "Add Translation" → Arabic
  3. Use side-by-side translation view
  4. Translate maintaining structure
  5. Save as Draft (Arabic)
  6. Request review

### Phase 3: Admin Reviews Translation

- **Actor**: Help Admin (bilingual)
- **Steps**:
  1. Review Arabic translation against English
  2. Check RTL formatting
  3. Verify terminology consistency
  4. Publish Arabic version
  5. Verify: Arabic users now see Arabic content

---

## Workflow CR-003: Feedback Loop

**Roles Involved**: Help User → Help Admin → Help Author

### Phase 1: User Reports Issue

- **Actor**: Help User
- **Steps**:
  1. User reads help content
  2. Finds error or missing information
  3. Clicks "Report Issue" or "Not Helpful"
  4. Describes the problem
  5. Submits feedback
- **Output**: Feedback record created

### Phase 2: Admin Triages Feedback

- **Actor**: Help Admin
- **Steps**:
  1. Navigate to Help Feedback List
  2. Review new feedback entries
  3. Categorize: Error / Missing / Enhancement / Invalid
  4. If valid: Assign to appropriate author
  5. Set priority based on view count of content
- **Output**: Task assigned to author

### Phase 3: Author Fixes Content

- **Actor**: Help Author
- **Steps**:
  1. Receive notification of assigned feedback
  2. Review feedback details
  3. Edit content to address issue
  4. Link commit to feedback item
  5. Mark feedback as resolved
  6. Request re-review if needed
- **Output**: Updated content, closed feedback

### Phase 4: User Confirmation

- **Actor**: Help User (optional)
- **Steps**:
  1. Receive notification that feedback was addressed
  2. Verify fix meets expectations
  3. Mark as satisfactory or reopen
- **Screen**: [feedback-resolution.md](../screens/feedback-resolution.md)

---

## Workflow CR-004: New Feature Documentation

**Roles Involved**: Developer → Help Author → Help Admin → Users

### Phase 1: Developer Documents Feature

- **Actor**: Developer
- **Trigger**: New feature merged to main branch
- **Steps**:
  1. Create help markdown file in app's `help/` directory
  2. Follow file naming convention: `{doctype_slug}.md`
  3. Include field-level anchors: `## # fieldname`
  4. Add both English and Arabic content (or English only initially)
  5. Commit with help files

### Phase 2: Help System Syncs

- **Actor**: System (automatic)
- **Steps**:
  1. `after_migrate` hook runs
  2. Help sync job detects new files
  3. Creates Help Content records from markdown
  4. Sets status to Draft for review

### Phase 3: Author/Admin Reviews

- **Actor**: Help Author or Help Admin
- **Steps**:
  1. Review auto-imported content
  2. Enhance with additional context
  3. Add related topics links
  4. Add images/screenshots
  5. Publish content

### Phase 4: Users Access

- **Actor**: Help Users
- **Verify**: Help available for new feature

---

## Workflow CR-005: Bulk Content Migration

**Roles Involved**: Help Admin → System → Help Authors

### Phase 1: Admin Initiates Import

- **Actor**: Help Admin
- **Pre-conditions**: Legacy docs prepared in standard format
- **Steps**:
  1. Prepare content in ZIP with markdown files
  2. Navigate to Help Settings
  3. Use Import wizard
  4. Map file paths to DocTypes
  5. Preview import
  6. Execute import

### Phase 2: System Processes

- **Actor**: System
- **Steps**:
  1. Extract and parse files
  2. Create Help Content records
  3. Set all as Draft
  4. Generate import report
  5. Send notification to admin

### Phase 3: Authors Review

- **Actor**: Multiple Help Authors
- **Steps**:
  1. Divide imported content by topic/app
  2. Each author reviews their portion
  3. Enhance metadata, tags, categories
  4. Request publication

### Phase 4: Admin Publishes

- **Actor**: Help Admin
- **Steps**:
  1. Run bulk publish on reviewed content
  2. Verify coverage report
  3. Announce content availability

---

## Workflow CR-006: Analytics-Driven Improvement

**Roles Involved**: Help Admin → Help Authors

### Phase 1: Admin Analyzes Metrics

- **Actor**: Help Admin
- **Frequency**: Weekly
- **Steps**:
  1. Open Help Dashboard
  2. Review "Least Viewed Topics"
  3. Review "Lowest Rated Content"
  4. Review "Missing Help" report
  5. Identify improvement areas

### Phase 2: Admin Creates Tasks

- **Actor**: Help Admin
- **Steps**:
  1. Create improvement tasks for authors
  2. Prioritize by user impact
  3. Set deadlines
  4. Assign based on expertise

### Phase 3: Authors Improve Content

- **Actor**: Help Authors
- **Steps**:
  1. Address assigned improvements
  2. Rewrite low-performing content
  3. Add missing content
  4. Submit for review

### Phase 4: Admin Tracks Progress

- **Actor**: Help Admin
- **Steps**:
  1. Review improvements
  2. Publish updates
  3. Track metric changes over time
  4. Report on content quality trends

---

## Emergency Scenarios

### CR-E01: Critical Help Error

**Roles**: Help User → Help Admin

- **Trigger**: User reports critical error in help (e.g., wrong instructions could cause data loss)
- **Admin Response**:
  1. Immediately unpublish content
  2. Notify users if widely viewed
  3. Fast-track correction
  4. Republish with annotation
- **SLA**: 2 hours for critical, 24 hours for major

### CR-E02: Mass Content Refresh

**Roles**: Help Admin → All Authors

- **Trigger**: Major software update changes many DocTypes
- **Admin Response**:
  1. Identify affected content
  2. Bulk mark as "Needs Review"
  3. Coordinate author assignments
  4. Track completion
  5. Publish updates in coordinated release
- **SLA**: Complete within release window
