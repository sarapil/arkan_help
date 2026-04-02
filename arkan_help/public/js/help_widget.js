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
