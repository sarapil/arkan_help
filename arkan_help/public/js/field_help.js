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
