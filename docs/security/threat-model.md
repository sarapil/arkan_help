# Threat Model — Arkan Help
# نموذج التهديدات — أركان مساعدة

## Overview

This document describes the security threat model for Arkan Help, a contextual help system for Frappe applications.

**Asset Classification:**
- **Critical**: Help Settings (contains analytics API keys, if any)
- **Sensitive**: User feedback data, view logs
- **Public**: Published help content

---

## Threat Categories (OWASP Top 10 2021)

| # | Threat | Risk | Mitigation | Status |
|---|--------|------|------------|--------|
| A01 | Broken Access Control | Medium | CAPS capability checks on all APIs, role-based content visibility | ✅ Implemented |
| A02 | Cryptographic Failures | Low | No sensitive data stored, uses Frappe's built-in encryption | ✅ N/A |
| A03 | Injection (SQL/XSS) | Medium | Parameterized queries, Markdown sanitization, output encoding | ✅ Implemented |
| A04 | Insecure Design | Low | Thin controller + service layer, principle of least privilege | ✅ Implemented |
| A05 | Security Misconfiguration | Low | Frappe framework defaults, no debug in production | ✅ Implemented |
| A06 | Vulnerable Components | Low | Regular dependency updates, Semgrep scans | ✅ CI/CD |
| A07 | Auth Failures | Low | Uses Frappe session auth, no custom auth | ✅ Framework |
| A08 | Software/Data Integrity | Low | Signed releases, verified sources | ✅ CI/CD |
| A09 | Security Logging | Medium | Help view logging, audit trail for content changes | ✅ Implemented |
| A10 | SSRF | Low | Timeout + allowlist for any external API calls | ✅ Implemented |

---

## Attack Vectors

### 1. Unauthorized Content Modification

**Threat**: Attacker modifies help content to display malicious instructions.

**Attack Surface**:
- Help Content DocType
- Translation files
- File-based help markdown

**Mitigations**:
- CAPS `AH_manage_topics` required for content creation/edit
- Content changes logged in Version DocType
- Status workflow: Draft → Review → Published
- Author attribution tracked

**Residual Risk**: Low (requires authenticated user with capability)

### 2. Cross-Site Scripting (XSS) via Markdown

**Threat**: Attacker injects JavaScript through Markdown content.

**Attack Surface**:
- Help Content `content` field
- User feedback comments

**Mitigations**:
- Frappe's `markdown()` function sanitizes HTML
- No raw HTML allowed in content
- Output encoding on all renders
- CSP headers prevent inline scripts

**Residual Risk**: Very Low (framework protection)

### 3. Information Disclosure via Analytics

**Threat**: Attacker gains insights about system usage patterns.

**Attack Surface**:
- Help View Log
- Dashboard analytics
- Coverage reports

**Mitigations**:
- `AH_view_analytics` capability required
- No PII in view logs (user anonymized after 30 days)
- Rate limiting on analytics APIs

**Residual Risk**: Low (analytics non-sensitive)

### 4. Denial of Service via Help Queries

**Threat**: Attacker floods help resolution API.

**Attack Surface**:
- `get_help` API endpoint
- `search_help` API endpoint

**Mitigations**:
- Redis caching (5-minute TTL)
- Query result size limits
- Rate limiting for unauthenticated users
- Efficient database indexes

**Residual Risk**: Low (caching mitigates)

### 5. File-Based Help Path Traversal

**Threat**: Attacker reads arbitrary files via help file path manipulation.

**Attack Surface**:
- File-based help resolution
- Markdown file loading

**Mitigations**:
- Strict path validation (alphanumeric + underscore only)
- Files must be within `{app}/help/` directory
- No user-controlled file paths
- Symlink resolution blocked

**Residual Risk**: Very Low (path validated)

---

## Data Flow Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Browser   │────▶│  Nginx/Gunicorn  │────▶│  Frappe API     │
│   (Client)  │◀────│  (Reverse Proxy) │◀────│  (Python)       │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                    ┌──────────────────────────────┼───────────┐
                    │                              ▼           │
                    │  ┌─────────────┐     ┌─────────────────┐ │
                    │  │ Help Service│────▶│   Redis Cache   │ │
                    │  └──────┬──────┘     └─────────────────┘ │
                    │         │                                 │
                    │         ▼                                 │
                    │  ┌─────────────┐     ┌─────────────────┐ │
                    │  │   MariaDB   │     │ File System     │ │
                    │  │   (DocTypes)│     │ (Markdown Help) │ │
                    │  └─────────────┘     └─────────────────┘ │
                    │                                           │
                    │           Arkan Help Application          │
                    └───────────────────────────────────────────┘
```

---

## Security Controls by Component

### API Layer (`api/v1/`)

| Endpoint | Auth | CAPS | Rate Limit | Input Validation |
|----------|------|------|------------|------------------|
| `get_help` | Optional | - | 60/min | DocType exists |
| `search_help` | Optional | - | 30/min | Query length < 200 |
| `log_view` | Session | - | 120/min | help_content exists |
| `submit_feedback` | Session | - | 10/min | helpful = boolean |
| `get_stats` | Session | AH_view_analytics | 10/min | - |
| `create_content` | Session | AH_manage_topics | 30/min | Full validation |
| `update_content` | Session | AH_manage_topics | 30/min | Full validation |

### DocType Layer

| DocType | Read | Write | Delete | Sensitive Fields |
|---------|------|-------|--------|------------------|
| Help Content | Public (published) | AH_manage_topics | Admin | - |
| Help Topic | Public | AH_manage_topics | Admin | - |
| Help Settings | Admin | Admin | - | - |
| Help View Log | AH_view_analytics | System | Admin | user (anonymized) |
| Help Feedback | AH_view_analytics | Session | Admin | comment |

---

## Incident Response

### Severity Classification

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| Critical | Data breach, RCE | Immediate | Help content exposes secrets |
| High | Privilege escalation | 4 hours | Non-admin edits published content |
| Medium | Information disclosure | 24 hours | Analytics data leaked |
| Low | DoS, minor issues | 72 hours | Slow help queries |

### Response Procedure

1. **Detect**: Monitor logs for anomalies
2. **Contain**: Disable affected endpoint if critical
3. **Assess**: Determine scope and impact
4. **Remediate**: Deploy fix
5. **Communicate**: Security advisory if needed
6. **Review**: Post-incident analysis

---

## Compliance Notes

- **GDPR**: View logs contain user references; auto-anonymize after 30 days
- **Accessibility**: Help content must be screen-reader compatible
- **i18n**: Bilingual content for all public-facing help
