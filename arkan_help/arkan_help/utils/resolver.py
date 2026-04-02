# Copyright (c) 2026, Arkan and contributors
# For license information, please see license.txt

"""
Help Context Resolver
=====================

Resolves the best-matching help content for a given UI context by
walking a specificity ladder from the most-exact match down to
file-based and fallback-language lookups.

Resolution priority
-------------------
1. Exact match   – doctype + fieldname + role + language
2. Field match   – doctype + fieldname + language  (any role)
3. DocType+Role  – doctype + role + language
4. DocType only  – doctype + language
5. File-based    – {app}/help/{lang}/{doctype}.md#{fieldname}
6. Fallback lang – repeat 1-5 with fallback_language from Help Settings
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from pathlib import Path
from typing import Any

import frappe
from frappe.utils.data import md_to_html

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RTL_LANGUAGES = frozenset({
	"ar", "he", "fa", "ur", "ps", "sd", "yi", "ku", "dv", "ckb",
})

CACHE_PREFIX = "help"

# Regex to extract YAML-ish frontmatter between --- fences
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Field-anchor pattern:  ## # fieldname
_FIELD_ANCHOR_RE = re.compile(r"^##\s*#\s*(\w+)\s*$", re.MULTILINE)

# YouTube / Vimeo URL → embed
_VIDEO_PATTERNS: list[tuple[re.Pattern, str]] = [
	# YouTube (various URL formats)
	(
		re.compile(
			r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)"
			r"([\w\-]{11})"
		),
		'<iframe width="100%" height="400" src="https://www.youtube.com/embed/{0}" '
		'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
		'gyroscope; picture-in-picture" allowfullscreen></iframe>',
	),
	# Vimeo
	(
		re.compile(r"(?:https?://)?(?:www\.)?(?:vimeo\.com|player\.vimeo\.com/video)/(\d+)"),
		'<iframe width="100%" height="400" src="https://player.vimeo.com/video/{0}" '
		'frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen>'
		"</iframe>",
	),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _settings() -> "frappe._dict":
	"""Return cached Help Settings singleton values."""
	return frappe.get_cached_doc("Help Settings").as_dict()


def _role_hash(roles: list[str] | str | None) -> str:
	"""Deterministic short hash for a set of roles – used as part of the cache key."""
	if not roles:
		return "none"
	if isinstance(roles, str):
		roles = [roles]
	joined = ",".join(sorted(roles))
	return hashlib.md5(joined.encode(), usedforsecurity=False).hexdigest()[:10]


def _cache_key(
	doctype: str | None = None,
	fieldname: str | None = None,
	lang: str | None = None,
	role_hash: str | None = None,
	prefix: str = "",
) -> str:
	"""Build a namespaced cache key.

	Format: ``help:{prefix}:{doctype}:{field}:{lang}:{role_hash}``
	"""
	parts = [
		CACHE_PREFIX,
		prefix or "ctx",
		doctype or "*",
		fieldname or "*",
		lang or "*",
		role_hash or "*",
	]
	return ":".join(parts)


def _video_embed(url: str | None) -> str | None:
	"""Convert a YouTube / Vimeo URL to an embeddable ``<iframe>`` string."""
	if not url:
		return None
	for pattern, template in _VIDEO_PATTERNS:
		m = pattern.search(url)
		if m:
			return template.format(m.group(1))
	# Unknown provider – return a clickable link instead
	return f'<a href="{frappe.utils.escape_html(url)}" target="_blank">{frappe.utils.escape_html(url)}</a>'


def _render_content(raw: str | None, content_type: str) -> str:
	"""Render raw content to HTML depending on its type."""
	if not raw:
		return ""
	if content_type == "markdown":
		return str(md_to_html(raw) or "")
	# html / interactive – return as-is
	return raw


def _is_rtl(lang: str | None) -> bool:
	if not lang:
		return False
	return lang.split("-")[0].lower() in RTL_LANGUAGES


def _parse_frontmatter(text: str) -> tuple[dict, str]:
	"""Parse YAML-ish frontmatter from a markdown file.

	Returns ``(metadata_dict, body_without_frontmatter)``.
	We do a *simple* key: value / key: [v1, v2] parse to avoid
	depending on PyYAML.
	"""
	m = _FRONTMATTER_RE.match(text)
	if not m:
		return {}, text

	meta: dict[str, Any] = {}
	for line in m.group(1).splitlines():
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		if ":" not in line:
			continue
		key, _, value = line.partition(":")
		key = key.strip().lower()
		value = value.strip()
		# Simple list: [item1, item2]
		if value.startswith("[") and value.endswith("]"):
			meta[key] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
		else:
			meta[key] = value

	body = text[m.end():]
	return meta, body


def _extract_field_sections(body: str) -> dict[str, str]:
	"""Split markdown body into field-specific sections using ``## # fieldname`` anchors.

	Returns a dict mapping ``fieldname → section_markdown``.
	"""
	sections: dict[str, str] = {}
	parts = _FIELD_ANCHOR_RE.split(body)
	# parts = [preamble, fieldname1, section1, fieldname2, section2, ...]
	for i in range(1, len(parts) - 1, 2):
		fieldname = parts[i].strip()
		content = parts[i + 1].strip()
		if fieldname and content:
			sections[fieldname] = content
	return sections


# ---------------------------------------------------------------------------
# Analytics logger
# ---------------------------------------------------------------------------


def _log_access(
	topic_key: str | None,
	doctype: str | None,
	fieldname: str | None,
	source: str = "database",
) -> None:
	"""Fire-and-forget analytics event when Help Settings.analytics_enabled is on."""
	try:
		settings = _settings()
		if not settings.get("analytics_enabled"):
			return
		frappe.publish_realtime(
			"help_access",
			{
				"topic_key": topic_key,
				"doctype": doctype,
				"fieldname": fieldname,
				"source": source,
				"user": frappe.session.user,
				"timestamp": time.time(),
			},
			after_commit=True,
		)
	except Exception:
		# Analytics must never break the help flow
		pass


# ---------------------------------------------------------------------------
# HelpResolver
# ---------------------------------------------------------------------------


class HelpResolver:
	"""Resolves the best-matching help content for a given UI context.

	Usage::

	    resolver = HelpResolver()
	    result = resolver.resolve({
	        "doctype": "Sales Order",
	        "fieldname": "customer",
	        "view_type": "form",
	        "action": "create",
	        "role": "Sales User",
	        "language": "ar",
	    })
	"""

	# ------------------------------------------------------------------
	# Initialisation
	# ------------------------------------------------------------------

	def __init__(self) -> None:
		self._settings: dict | None = None

	@property
	def settings(self) -> "frappe._dict":
		if self._settings is None:
			self._settings = _settings()
		return self._settings

	@property
	def cache_ttl(self) -> int:
		return int(self.settings.get("cache_ttl") or 0)

	@property
	def fallback_language(self) -> str:
		return self.settings.get("fallback_language") or "en"

	# ------------------------------------------------------------------
	# Cache helpers
	# ------------------------------------------------------------------

	def _cache_get(self, key: str) -> Any | None:
		if not self.cache_ttl:
			return None
		return frappe.cache().get_value(key)

	def _cache_set(self, key: str, value: Any) -> None:
		if not self.cache_ttl:
			return
		frappe.cache().set_value(key, value, expires_in_sec=self.cache_ttl)

	# ------------------------------------------------------------------
	# Public: main resolve()
	# ------------------------------------------------------------------

	def resolve(self, context: dict) -> dict | None:
		"""Resolve the best-matching help content for *context*.

		Parameters
		----------
		context : dict
		    Keys: ``doctype``, ``fieldname`` (opt), ``view_type`` (opt),
		    ``action`` (opt), ``role`` (opt/str or list), ``language``.

		Returns
		-------
		dict | None
		    Resolved help payload or *None* when nothing matches.
		"""
		doctype = context.get("doctype")
		fieldname = context.get("fieldname")
		view_type = context.get("view_type")
		action = context.get("action")
		roles = context.get("role") or context.get("roles")
		lang = context.get("language") or self.fallback_language

		if isinstance(roles, str):
			roles = [roles]

		rh = _role_hash(roles)
		cache_key = _cache_key(doctype=doctype, fieldname=fieldname, lang=lang, role_hash=rh)
		cached = self._cache_get(cache_key)
		if cached is not None:
			return cached if cached != "__MISS__" else None

		# Build the language chain:  requested language → fallback
		lang_chain = [lang]
		if lang != self.fallback_language:
			lang_chain.append(self.fallback_language)

		for try_lang in lang_chain:
			result = self._resolve_from_db(
				doctype=doctype,
				fieldname=fieldname,
				view_type=view_type,
				action=action,
				roles=roles,
				lang=try_lang,
			)
			if result:
				self._cache_set(cache_key, result)
				_log_access(result.get("topic_key"), doctype, fieldname, source="database")
				return result

		# File-based lookup (only if enabled)
		if self.settings.get("enable_file_based_help"):
			for try_lang in lang_chain:
				result = self._resolve_from_file(
					doctype=doctype,
					fieldname=fieldname,
					lang=try_lang,
					roles=roles,
				)
				if result:
					self._cache_set(cache_key, result)
					_log_access(result.get("topic_key"), doctype, fieldname, source="file")
					return result

		# Nothing found – cache the miss so we don't re-query
		self._cache_set(cache_key, "__MISS__")
		return None

	# ------------------------------------------------------------------
	# Public: convenience helpers
	# ------------------------------------------------------------------

	def get_field_help(self, doctype: str, fieldname: str, lang: str | None = None) -> str | None:
		"""Quick tooltip text for a single field.

		Returns rendered HTML string or *None*.
		"""
		lang = lang or self.fallback_language
		result = self.resolve({
			"doctype": doctype,
			"fieldname": fieldname,
			"view_type": "form",
			"language": lang,
		})
		if result:
			return result.get("content")
		return None

	def get_form_help(
		self,
		doctype: str,
		lang: str | None = None,
		roles: list[str] | None = None,
	) -> dict | None:
		"""Return form-level help banner data (no fieldname)."""
		lang = lang or self.fallback_language
		return self.resolve({
			"doctype": doctype,
			"view_type": "form",
			"language": lang,
			"roles": roles,
		})

	def get_navbar_help(self, route: str, lang: str | None = None) -> dict | None:
		"""Lookup help for a page route (used by the navbar help icon).

		The *route* is matched against Help Topic ``context_reference`` where
		``context_type == 'page'``.
		"""
		lang = lang or self.fallback_language

		cache_key = _cache_key(prefix="navbar", doctype=route, lang=lang)
		cached = self._cache_get(cache_key)
		if cached is not None:
			return cached if cached != "__MISS__" else None

		lang_chain = [lang]
		if lang != self.fallback_language:
			lang_chain.append(self.fallback_language)

		for try_lang in lang_chain:
			result = self._resolve_navbar(route, try_lang)
			if result:
				self._cache_set(cache_key, result)
				_log_access(result.get("topic_key"), None, None, source="database")
				return result

		self._cache_set(cache_key, "__MISS__")
		return None

	def discover_file_help(self, app_name: str | None = None) -> list[dict]:
		"""Scan ``{app}/help/{lang}/*.md`` across installed apps and return
		a list of parsed help file descriptors.

		Each dict::

		    {
		        "app": "erpnext",
		        "language": "en",
		        "file": "sales_order.md",
		        "path": "/abs/path/to/file",
		        "mtime": 1711929600.0,
		        "meta": {<frontmatter>},
		        "fields": ["customer", "delivery_date"],
		    }
		"""
		results: list[dict] = []
		apps = [app_name] if app_name else frappe.get_installed_apps()

		for app in apps:
			try:
				app_path = Path(frappe.get_app_path(app))
			except Exception:
				continue

			help_dir = app_path / "help"
			if not help_dir.is_dir():
				continue

			for lang_dir in sorted(help_dir.iterdir()):
				if not lang_dir.is_dir():
					continue
				lang_code = lang_dir.name

				for md_file in sorted(lang_dir.glob("*.md")):
					try:
						text = md_file.read_text(encoding="utf-8")
					except Exception:
						continue

					meta, body = _parse_frontmatter(text)
					field_sections = _extract_field_sections(body)

					results.append({
						"app": app,
						"language": lang_code,
						"file": md_file.name,
						"path": str(md_file),
						"mtime": md_file.stat().st_mtime,
						"meta": meta,
						"fields": list(field_sections.keys()),
					})

		return results

	# ------------------------------------------------------------------
	# Internal: database resolution
	# ------------------------------------------------------------------

	def _resolve_from_db(
		self,
		doctype: str | None,
		fieldname: str | None,
		view_type: str | None,
		action: str | None,
		roles: list[str] | None,
		lang: str,
	) -> dict | None:
		"""Walk the specificity ladder against Help Context → Help Topic → Help Content."""

		# Fetch all candidate Help Context rows for this doctype, ordered by priority DESC
		filters: dict[str, Any] = {}
		if doctype:
			filters["doctype_link"] = doctype

		contexts = frappe.get_all(
			"Help Context",
			filters=filters,
			fields=[
				"name", "topic", "doctype_link", "fieldname",
				"view_type", "action", "role", "priority",
			],
			order_by="priority desc",
		)

		if not contexts:
			# Also try topics that have context_type='doctype' and context_reference matching
			return self._resolve_topic_direct(doctype, lang, roles)

		# Score each context row
		scored: list[tuple[int, dict]] = []
		for ctx in contexts:
			score = self._score_context(ctx, fieldname, view_type, action, roles)
			if score >= 0:
				scored.append((score, ctx))

		if not scored:
			# Fall back to topic-direct lookup
			return self._resolve_topic_direct(doctype, lang, roles)

		# Sort descending by score, then by priority
		scored.sort(key=lambda x: (x[0], x[1].get("priority", 0)), reverse=True)

		# Try to find content for each candidate in score order
		for _score, ctx in scored:
			topic_key = ctx.get("topic")
			if not topic_key:
				continue
			result = self._load_content(topic_key, lang, roles)
			if result:
				return result

		return None

	def _score_context(
		self,
		ctx: dict,
		fieldname: str | None,
		view_type: str | None,
		action: str | None,
		roles: list[str] | None,
	) -> int:
		"""Score a Help Context row against the request.

		Returns -1 if this context is incompatible, otherwise a positive
		integer where higher = better match.
		"""
		score = 0

		# --- fieldname ---
		ctx_field = ctx.get("fieldname")
		if fieldname and ctx_field:
			if ctx_field == fieldname:
				score += 100  # exact field match is most valuable
			else:
				return -1  # wrong field – skip
		elif fieldname and not ctx_field:
			pass  # generic context, still acceptable
		elif not fieldname and ctx_field:
			return -1  # caller didn't ask for a field, but context is field-specific

		# --- view_type ---
		ctx_view = ctx.get("view_type")
		if ctx_view and view_type:
			if ctx_view == view_type:
				score += 10
			else:
				return -1
		elif ctx_view and not view_type:
			pass  # accept – we don't penalise

		# --- action ---
		ctx_action = ctx.get("action")
		if ctx_action and ctx_action != "any" and action:
			if ctx_action == action:
				score += 5
			else:
				return -1

		# --- role ---
		ctx_role = ctx.get("role")
		if ctx_role and roles:
			if ctx_role in roles:
				score += 50
			else:
				return -1  # role mismatch
		elif ctx_role and not roles:
			return -1  # context demands a role but none supplied

		return score

	def _resolve_topic_direct(
		self,
		doctype: str | None,
		lang: str,
		roles: list[str] | None,
	) -> dict | None:
		"""Fallback: find Help Topics whose ``context_type='doctype'`` and
		``context_reference`` matches *doctype*, then load content."""
		if not doctype:
			return None

		topics = frappe.get_all(
			"Help Topic",
			filters={
				"context_type": "doctype",
				"context_reference": doctype,
				"enabled": 1,
			},
			fields=["name", "topic_key", "title", "icon"],
			order_by="sort_order asc",
		)

		for topic in topics:
			result = self._load_content(topic["name"], lang, roles)
			if result:
				return result
		return None

	def _resolve_navbar(self, route: str, lang: str) -> dict | None:
		"""Find a Help Topic where ``context_type='page'`` and
		``context_reference`` matches the *route*."""
		topics = frappe.get_all(
			"Help Topic",
			filters={
				"context_type": "page",
				"context_reference": route,
				"enabled": 1,
			},
			fields=["name", "topic_key", "title", "icon"],
			order_by="sort_order asc",
			limit_page_length=1,
		)
		if not topics:
			return None

		topic = topics[0]
		return self._load_content(topic["name"], lang)

	# ------------------------------------------------------------------
	# Internal: load Help Content for a topic + language
	# ------------------------------------------------------------------

	def _load_content(
		self,
		topic_name: str,
		lang: str,
		roles: list[str] | None = None,
	) -> dict | None:
		"""Given a Help Topic *name* (== topic_key), find the matching
		Help Content row for *lang* and return a result dict."""

		# Fetch the topic
		topic = frappe.db.get_value(
			"Help Topic",
			topic_name,
			["name", "topic_key", "title", "icon", "app_name"],
			as_dict=True,
		)
		if not topic:
			return None

		# Fetch content
		content_row = frappe.db.get_value(
			"Help Content",
			{"topic": topic_name, "language": lang},
			[
				"name", "content_type", "content", "video_url",
				"version", "last_reviewed",
			],
			as_dict=True,
		)
		if not content_row:
			return None

		# Role filtering — if the content has target_roles, ensure the
		# caller has at least one matching role
		if roles:
			target_roles = frappe.get_all(
				"Help Content Role",
				filters={"parent": content_row.name},
				pluck="role",
			)
			if target_roles and not set(roles).intersection(target_roles):
				return None  # content restricted and user lacks required role

		# Build rendered content
		rendered = _render_content(content_row.content, content_row.content_type)

		# Video embed
		video_embed = None
		if content_row.content_type == "video" and content_row.video_url:
			video_embed = _video_embed(content_row.video_url)

		# Related topics (same doctype, different topic_key)
		related = self._get_related_topics(topic_name, topic.get("app_name"))

		is_rtl = _is_rtl(lang)

		return {
			"topic_key": topic.topic_key,
			"title": topic.title,
			"content": rendered,
			"content_raw": content_row.content,
			"content_type": content_row.content_type,
			"source": "database",
			"video_url": content_row.video_url,
			"video_embed": video_embed,
			"icon": topic.icon,
			"language": lang,
			"is_rtl": is_rtl,
			"dir": "rtl" if is_rtl else "ltr",
			"version": content_row.version,
			"last_reviewed": str(content_row.last_reviewed) if content_row.last_reviewed else None,
			"related_topics": related,
		}

	def _get_related_topics(
		self, exclude_topic: str, app_name: str | None = None
	) -> list[dict]:
		"""Return a small list of sibling Help Topics from the same app/module."""
		filters: dict[str, Any] = {
			"enabled": 1,
			"name": ("!=", exclude_topic),
		}
		if app_name:
			filters["app_name"] = app_name

		return frappe.get_all(
			"Help Topic",
			filters=filters,
			fields=["topic_key", "title", "icon"],
			order_by="sort_order asc",
			limit_page_length=5,
		)

	# ------------------------------------------------------------------
	# Internal: file-based resolution
	# ------------------------------------------------------------------

	def _resolve_from_file(
		self,
		doctype: str | None,
		fieldname: str | None,
		lang: str,
		roles: list[str] | None = None,
	) -> dict | None:
		"""Scan ``{app}/help/{lang}/{doctype_slug}.md`` and optionally
		extract a field-specific section."""
		if not doctype:
			return None

		doctype_slug = frappe.scrub(doctype)  # "Sales Order" → "sales_order"

		for app in frappe.get_installed_apps():
			try:
				app_path = Path(frappe.get_app_path(app))
			except Exception:
				continue

			md_path = app_path / "help" / lang / f"{doctype_slug}.md"
			if not md_path.is_file():
				continue

			# Check file-level cache using mtime
			file_cache_key = _cache_key(
				prefix="file",
				doctype=doctype_slug,
				fieldname=fieldname or "*",
				lang=lang,
			)
			mtime = md_path.stat().st_mtime
			cached = self._cache_get(file_cache_key)
			if cached and isinstance(cached, dict) and cached.get("_mtime") == mtime:
				payload = cached.get("_payload")
				return payload if payload != "__MISS__" else None

			try:
				text = md_path.read_text(encoding="utf-8")
			except Exception:
				continue

			meta, body = _parse_frontmatter(text)

			# Role check
			meta_roles = meta.get("roles")
			if meta_roles and roles:
				if not set(roles).intersection(meta_roles):
					# Cache the miss keyed to mtime so we don't re-read
					self._cache_set(file_cache_key, {"_mtime": mtime, "_payload": "__MISS__"})
					continue
			elif meta_roles and not roles:
				self._cache_set(file_cache_key, {"_mtime": mtime, "_payload": "__MISS__"})
				continue

			# If a fieldname was requested, extract that section
			content_md = body
			if fieldname:
				sections = _extract_field_sections(body)
				if fieldname in sections:
					content_md = sections[fieldname]
				else:
					# Field not found in file – cache miss but continue to
					# next app in case another app provides it
					self._cache_set(file_cache_key, {"_mtime": mtime, "_payload": "__MISS__"})
					continue

			rendered = _render_content(content_md, "markdown")
			is_rtl = _is_rtl(lang)

			topic_key = f"file:{app}:{doctype_slug}"
			if fieldname:
				topic_key += f":{fieldname}"

			payload = {
				"topic_key": topic_key,
				"title": meta.get("title", doctype),
				"content": rendered,
				"content_raw": content_md,
				"content_type": "markdown",
				"source": "file",
				"video_url": None,
				"video_embed": None,
				"icon": None,
				"language": lang,
				"is_rtl": is_rtl,
				"dir": "rtl" if is_rtl else "ltr",
				"version": None,
				"last_reviewed": None,
				"related_topics": [],
			}

			self._cache_set(file_cache_key, {"_mtime": mtime, "_payload": payload})
			return payload

		return None

	# ------------------------------------------------------------------
	# Cache invalidation (called from doc_events hooks)
	# ------------------------------------------------------------------

	@staticmethod
	def invalidate_cache(
		topic_key: str | None = None,
		doctype: str | None = None,
	) -> None:
		"""Flush all help-related cache entries.

		Called from ``doc_events`` on Help Content / Help Topic / Help Context
		save and delete.  We delete by wildcard pattern to cover all
		language / role combinations.
		"""
		try:
			frappe.cache().delete_keys(f"{CACHE_PREFIX}:*")
		except Exception:
			pass

	@staticmethod
	def invalidate_all() -> None:
		"""Nuclear option – drop every ``help:*`` key."""
		try:
			frappe.cache().delete_keys(f"{CACHE_PREFIX}:*")
		except Exception:
			pass


# ---------------------------------------------------------------------------
# Hook callback — referenced from hooks.py doc_events
# ---------------------------------------------------------------------------


def on_help_doc_change(doc, method=None):
	"""Called by ``doc_events`` in hooks.py whenever a help-related
	DocType is saved or deleted.  Flushes the entire help cache and
	notifies all connected browser clients to clear their JS caches."""
	HelpResolver.invalidate_all()

	# Notify frontend clients so they clear their Map caches
	try:
		frappe.publish_realtime("help_cache_clear", after_commit=True)
	except Exception:
		pass
