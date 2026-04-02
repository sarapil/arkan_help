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
