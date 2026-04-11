/* arkan_help — Combined JS (reduces HTTP requests) */
/* Auto-generated from 4 individual files */


/* === help_widget.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * arkan_help — Global Help Widget
 *
 * Provides arkan_help.HelpWidget: a modal / tooltip system that fetches
 * context-aware help from the server and renders it with proper RTL,
 * video-embed, and markdown support.
 */
frappe.provide("arkan_help");

arkan_help.HelpWidget = class HelpWidget {
	constructor() {
		this.modal = null;
		this.tooltip = null;
		this.cache = new Map();
		this._modal_width_map = { sm: "400px", md: "600px", lg: "800px", xl: "1000px" };
	}

	// ── Public API ──────────────────────────────────────────────────

	/**
	 * Show help in a modal dialog.
	 * @param {Object} context  — { doctype, fieldname, view_type, action, route }
	 */
	async show(context = {}) {
		const data = await this._fetch(context);
		if (!data) {
			frappe.show_alert({ message: __("No help available for this context."), indicator: "yellow" });
			return;
		}
		this._renderModal(data);
		this._logView(data);
	}

	/**
	 * Show a lightweight tooltip anchored to *element*.
	 * @param {HTMLElement} element
	 * @param {Object}      context
	 */
	async showTooltip(element, context = {}) {
		this.hideTooltip();

		const data = await this._fetch(context);
		if (!data) return;

		const tip = this._createTooltipEl(data, element);
		document.body.appendChild(tip);
		this.tooltip = tip;

		// Position near the element
		this._positionTooltip(tip, element);

		// Close on outside click
		const closeFn = (e) => {
			if (!tip.contains(e.target) && e.target !== element) {
				this.hideTooltip();
				document.removeEventListener("mousedown", closeFn);
			}
		};
		setTimeout(() => document.addEventListener("mousedown", closeFn), 0);

		this._logView(data);
	}

	/** Remove any open tooltip */
	hideTooltip() {
		if (this.tooltip) {
			this.tooltip.remove();
			this.tooltip = null;
		}
	}

	/**
	 * Render resolved help data into HTML.
	 * @param {Object} data — resolved payload from server
	 * @returns {string} HTML
	 */
	renderContent(data) {
		if (!data) return "";

		const dir = data.dir || "ltr";
		let html = `<div class="help-content-body" dir="${dir}">`;

		// Video embed
		if (data.content_type === "video" && data.video_embed) {
			html += `<div class="help-video-embed">${data.video_embed}</div>`;
		}

		// Main content
		if (data.content) {
			html += `<div class="help-content-text">${data.content}</div>`;
		}

		// Related topics
		if (data.related_topics && data.related_topics.length) {
			html += `<div class="help-related-topics mt-4">`;
			html += `<h6 class="text-muted">${__("Related Topics")}</h6><ul class="list-unstyled">`;
			for (const t of data.related_topics) {
				const icon = t.icon ? `<i class="${t.icon} mr-1"></i>` : "";
				html += `<li>
					<a href="#" class="help-related-link" data-topic-key="${frappe.utils.escape_html(t.topic_key)}">
						${icon}${frappe.utils.escape_html(t.title)}
					</a>
				</li>`;
			}
			html += `</ul></div>`;
		}

		html += `</div>`;
		return html;
	}

	// ── Private ─────────────────────────────────────────────────────

	/** Fetch help from server (with client-side cache). */
	async _fetch(context) {
		const key = JSON.stringify(context);
		if (this.cache.has(key)) return this.cache.get(key);

		try {
			const res = await frappe.xcall(
				"arkan_help.arkan_help.api.help.get_help",
				{
					doctype: context.doctype || undefined,
					fieldname: context.fieldname || undefined,
					view_type: context.view_type || "form",
					action: context.action || undefined,
					route: context.route || undefined,
				}
			);
			const data = res || null;
			this.cache.set(key, data);
			return data;
		} catch (e) {
			console.error("arkan_help: fetch failed", e);
			return null;
		}
	}

	/** Render the full-size modal. */
	_renderModal(data) {
		if (this.modal) {
			this.modal.hide();
			this.modal = null;
		}

		const dir = data.dir || "ltr";
		const body = this.renderContent(data);

		this.modal = new frappe.ui.Dialog({
			title: data.title || __("Help"),
			size: this._getModalSize(),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "help_html",
					options: body,
				},
			],
		});

		// Apply RTL and custom class
		const $wrapper = this.modal.$wrapper;
		$wrapper.addClass("help-modal");
		if (dir === "rtl") {
			$wrapper.attr("dir", "rtl");
		}

		// Wire up related-topic links
		$wrapper.find(".help-related-link").on("click", (e) => {
			e.preventDefault();
			const topicKey = $(e.currentTarget).data("topic-key");
			if (topicKey) {
				this.modal.hide();
				this.show({ route: topicKey });
			}
		});

		this.modal.show();
	}

	/** Create a tooltip DOM element. */
	_createTooltipEl(data, _anchor) {
		const dir = data.dir || "ltr";
		const div = document.createElement("div");
		div.className = "help-tooltip";
		div.setAttribute("dir", dir);
		div.innerHTML = `
			<div class="help-tooltip-title font-weight-bold mb-1">
				${frappe.utils.escape_html(data.title || "")}
			</div>
			<div class="help-tooltip-body">
				${data.content || ""}
			</div>
			${
				data.content_type === "video" && data.video_url
					? `<a href="${frappe.utils.escape_html(data.video_url)}" target="_blank" class="text-muted small mt-1 d-block">
						<i class="fa fa-play-circle mr-1"></i>${__("Watch Video")}
					   </a>`
					: ""
			}
			<div class="help-tooltip-more mt-2">
				<a href="#" class="help-tooltip-expand small text-primary">${__("Read more…")}</a>
			</div>
		`;

		// "Read more" opens the full modal
		div.querySelector(".help-tooltip-expand")?.addEventListener("click", (e) => {
			e.preventDefault();
			this.hideTooltip();
			this._renderModal(data);
		});

		return div;
	}

	/** Position tooltip near an anchor element. */
	_positionTooltip(tip, anchor) {
		const rect = anchor.getBoundingClientRect();
		const tipWidth = 300;

		let left = rect.right + 8;
		let top = rect.top + window.scrollY;

		// Flip left if overflowing viewport
		if (left + tipWidth > window.innerWidth) {
			left = rect.left - tipWidth - 8;
		}
		// Clamp
		if (left < 4) left = 4;
		if (top < 4) top = 4;

		tip.style.position = "absolute";
		tip.style.zIndex = "1060";
		tip.style.left = `${left}px`;
		tip.style.top = `${top}px`;
		tip.style.width = `${tipWidth}px`;
	}

	/** Read modal_width from Help Settings (cached during bootinfo). */
	_getModalSize() {
		const width =
			(frappe.boot.arkan_help_settings || {}).modal_width || "md";
		// frappe.ui.Dialog accepts 'small', 'large', 'extra-large' or nothing (default)
		const map = { sm: "small", md: null, lg: "large", xl: "extra-large" };
		return map[width] || null;
	}

	/** Fire analytics log if enabled. */
	_logView(data) {
		if (!data || !data.topic_key) return;
		frappe.xcall("arkan_help.arkan_help.api.help.log_help_view", {
			topic_key: data.topic_key,
			doctype: data.doctype || undefined,
			fieldname: data.fieldname || undefined,
		}).catch(() => {});
	}
};

// Global singleton
arkan_help.widget = new arkan_help.HelpWidget();


/* === field_help.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * arkan_help — Field-Level Help Icons
 *
 * Injects ⓘ icons next to field labels on forms for fields that have
 * associated help content.  Clicking the icon opens a tooltip (or modal
 * on mobile) with the field-specific help.
 *
 * Activation is controlled by Help Settings → enable_field_help.
 */
frappe.provide("arkan_help");

arkan_help.field_help = {
	/** Cache: doctype → Set<fieldname> */
	_fields_cache: {},

	/**
	 * Main entry point — called on every form refresh.
	 * @param {Object} frm — Frappe form controller
	 */
	async injectFieldHelp(frm) {
		if (!this._isEnabled()) return;
		if (!frm || !frm.doctype) return;

		const fields = await this._getFieldsWithHelp(frm.doctype);
		if (!fields || !fields.length) return;

		const fieldSet = new Set(fields);

		for (const field of frm.fields) {
			if (!field.df || !field.df.fieldname) continue;
			if (!fieldSet.has(field.df.fieldname)) continue;

			const wrapper = field.$wrapper || (field.wrapper && $(field.wrapper));
			if (!wrapper || !wrapper.length) continue;

			// Don't inject twice
			if (wrapper.find(".arkan-help-icon").length) continue;

			const $label = wrapper.find(".control-label, .like-disabled-input label, label").first();
			if (!$label.length) continue;

			const $icon = $(`
				<span class="arkan-help-icon help-icon" title="${__("Help")}"
				      data-fieldname="${frappe.utils.escape_html(field.df.fieldname)}"
				      data-doctype="${frappe.utils.escape_html(frm.doctype)}">
					<svg class="icon icon-sm" aria-hidden="true">
						<use href="#icon-help"></use>
					</svg>
				</span>
			`);

			$label.after($icon);

			// Bind click → tooltip (desktop) or modal (mobile)
			$icon.on("click", (e) => {
				e.preventDefault();
				e.stopPropagation();
				const ctx = {
					doctype: frm.doctype,
					fieldname: field.df.fieldname,
					view_type: "form",
					action: frm.is_new() ? "create" : "edit",
				};

				if (frappe.dom.is_touchscreen()) {
					arkan_help.widget.show(ctx);
				} else {
					arkan_help.widget.showTooltip($icon[0], ctx);
				}
			});
		}
	},

	/** Check boot flag for enable_field_help. */
	_isEnabled() {
		const s = frappe.boot.arkan_help_settings;
		return s && cint(s.enable_field_help);
	},

	/** Fetch (and cache) the list of fields with help for a doctype. */
	async _getFieldsWithHelp(doctype) {
		if (this._fields_cache[doctype] !== undefined) {
			return this._fields_cache[doctype];
		}

		try {
			const fields = await frappe.xcall(
				"arkan_help.arkan_help.api.help.get_fields_with_help",
				{ doctype }
			);
			this._fields_cache[doctype] = fields || [];
			return this._fields_cache[doctype];
		} catch (e) {
			console.error("arkan_help: get_fields_with_help failed", e);
			this._fields_cache[doctype] = [];
			return [];
		}
	},

	/** Invalidate client-side caches (called when help docs change). */
	clearCache() {
		this._fields_cache = {};
		if (arkan_help.widget) {
			arkan_help.widget.cache.clear();
		}
	},
};

// Convenience alias used in prompt specification
arkan_help.injectFieldHelp = function (frm) {
	arkan_help.field_help.injectFieldHelp(frm);
};

// ---------------------------------------------------------------------------
// Global form hook — inject field help on every form refresh
// ---------------------------------------------------------------------------
$(document).on("app_ready", () => {
	if (!arkan_help.field_help._isEnabled()) return;

	// Hook into form refresh
	frappe.ui.form.on("*", {
		refresh(frm) {
			// Use setTimeout to run after the form has fully rendered
			setTimeout(() => arkan_help.field_help.injectFieldHelp(frm), 300);
		},
	});
});

// Listen for realtime cache-bust from server
frappe.realtime.on("help_cache_clear", () => {
	arkan_help.field_help.clearCache();
});


/* === navbar_help.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * arkan_help — Navbar Help Integration
 *
 * Adds a help icon to the navbar that shows context-aware help for the
 * current route.  An indicator dot appears when help is available.
 */
frappe.provide("arkan_help");

arkan_help.navbar_help = {
	$link: null,
	$indicator: null,
	_last_route: null,
	_route_cache: {},

	/** Bootstrap the navbar link.  Called once on app_ready. */
	init() {
		if (!this._isEnabled()) return;

		this._injectNavLink();
		this._bindRouteChange();

		// Initial check
		setTimeout(() => this._onRouteChange(), 500);
	},

	// ── Private ──────────────────────────────────────────────────

	_isEnabled() {
		const s = frappe.boot.arkan_help_settings;
		return s && cint(s.enable_navbar_help);
	},

	/** Add the help icon into .navbar-right (before the user dropdown). */
	_injectNavLink() {
		const iconClass = (frappe.boot.arkan_help_settings || {}).help_icon || "help-circle";

		const html = `
			<li class="nav-item arkan-help-nav-item">
				<a class="nav-link arkan-help-nav-link" id="arkan-help-link"
				   href="#" title="${__("Help")}" aria-label="${__("Help")}">
					<svg class="icon icon-md" aria-hidden="true">
						<use href="#icon-${frappe.utils.escape_html(iconClass)}"></use>
					</svg>
					<span class="arkan-help-indicator" style="display:none"></span>
				</a>
			</li>
		`;

		// Insert before the last item in the right navbar (typically user avatar)
		const $right = $(".navbar-right, .navbar-nav:last");
		if ($right.length) {
			const $items = $right.children(".nav-item");
			if ($items.length) {
				$(html).insertBefore($items.last());
			} else {
				$right.prepend(html);
			}
		}

		this.$link = $("#arkan-help-link");
		this.$indicator = this.$link.find(".arkan-help-indicator");

		this.$link.on("click", (e) => {
			e.preventDefault();
			this._onLinkClick();
		});
	},

	/** Watch for Frappe route changes. */
	_bindRouteChange() {
		// Frappe fires 'after_ajax' or we can poll the route
		frappe.router.on("change", () => this._onRouteChange());

		// Fallback: hashchange for older Frappe versions
		$(window).on("hashchange", () => {
			setTimeout(() => this._onRouteChange(), 200);
		});
	},

	/** Called when the route changes — check for help availability. */
	async _onRouteChange() {
		const route = frappe.get_route_str();
		if (!route || route === this._last_route) return;
		this._last_route = route;

		const hasHelp = await this._hasHelp(route);
		if (this.$indicator) {
			this.$indicator.toggle(!!hasHelp);
		}
	},

	/** Lightweight check — returns boolean. */
	async _hasHelp(route) {
		if (this._route_cache[route] !== undefined) {
			return this._route_cache[route];
		}

		try {
			const res = await frappe.xcall(
				"arkan_help.arkan_help.api.help.has_route_help",
				{ route }
			);
			const val = res && res.has_help;
			this._route_cache[route] = val;
			return val;
		} catch {
			return false;
		}
	},

	/** Handle navbar help link click. */
	_onLinkClick() {
		const route = frappe.get_route_str();
		const parts = frappe.get_route();
		let ctx = { route };

		// If on a form, pass doctype context for richer help
		if (parts && parts[0] === "Form" && parts[1]) {
			ctx.doctype = parts[1];
			ctx.view_type = "form";
			ctx.action = parts[2] ? "edit" : "create";
		} else if (parts && parts[0] === "List" && parts[1]) {
			ctx.doctype = parts[1];
			ctx.view_type = "list";
		}

		arkan_help.widget.show(ctx);
	},

	/** Clear cached route checks. */
	clearCache() {
		this._route_cache = {};
		this._last_route = null;
	},
};

// ---------------------------------------------------------------------------
// Initialise on app ready
// ---------------------------------------------------------------------------
$(document).on("app_ready", () => {
	arkan_help.navbar_help.init();
});

// Bust route cache when help docs change
frappe.realtime.on("help_cache_clear", () => {
	arkan_help.navbar_help.clearCache();
});


/* === fv_integration.js === */
// Copyright (c) 2024, Arkan Lab — https://arkan.it.com
// License: MIT
// frappe_visual Integration for Arkan Help

(function() {
    "use strict";

    // App branding registration
    const APP_CONFIG = {
        name: "arkan_help",
        title: "Arkan Help",
        color: "#10B981",
        module: "Arkan Help",
    };

    // Initialize visual enhancements when ready
    $(document).on("app_ready", function() {
        // Register app color with visual theme system
        if (frappe.visual && frappe.visual.ThemeManager) {
            try {
                document.documentElement.style.setProperty(
                    "--arkan-help-primary",
                    APP_CONFIG.color
                );
            } catch(e) {}
        }

        // Initialize bilingual tooltips for Arabic support
        if (frappe.visual && frappe.visual.bilingualTooltip) {
            // bilingualTooltip auto-initializes — just ensure it's active
        }
    });

    // Route-based visual page rendering
    $(document).on("page-change", function() {
        if (!frappe.visual || !frappe.visual.generator) return;

    // Visual Settings Page
    if (frappe.get_route_str() === 'arkan-help-settings') {
        const page = frappe.container.page;
        if (page && page.main && frappe.visual.generator) {
            frappe.visual.generator.settingsPage(
                page.main[0] || page.main,
                "Help Settings"
            );
        }
    }

    // Visual Reports Hub
    if (frappe.get_route_str() === 'arkan-help-reports') {
        const page = frappe.container.page;
        if (page && page.main && frappe.visual.generator) {
            frappe.visual.generator.reportsHub(
                page.main[0] || page.main,
                "Arkan Help"
            );
        }
    }
    });
})();

