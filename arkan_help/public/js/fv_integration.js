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

    // ─────────────────────────────────────────────────────────────────────
    // Scene Dashboard for Help Center
    // ─────────────────────────────────────────────────────────────────────
    async function initHelpDashboard(container) {
        if (!frappe.visual || !frappe.visual.scenePresetLibrary) return;

        try {
            // Library scene is perfect for help/documentation
            const scene = await frappe.visual.scenePresetLibrary({
                container: container,
                theme: frappe.ui.color.is_dark() ? "dark" : "warm",
                frames: [
                    { label: __("Topics"), value: "0", status: "info" },
                    { label: __("Views"), value: "0K", status: "success" },
                    { label: __("Rating"), value: "0%", status: "warning" },
                    { label: __("Authors"), value: "0", status: "info" },
                ],
                books: [
                    { label: __("Help Content"), href: "/app/help-content", color: "#10B981" },
                    { label: __("Help Topics"), href: "/app/help-topic", color: "#06B6D4" },
                    { label: __("Settings"), href: "/app/help-settings", color: "#8B5CF6" },
                ],
                documents: [
                    { label: __("Pending Reviews"), count: 0, color: "#F59E0B" },
                ],
            });

            // Bind live data to KPI frames
            await frappe.visual.sceneDataBinder({
                engine: scene,
                frames: [
                    {
                        label: "Topics",
                        doctype: "Help Content",
                        aggregate: "count",
                        filters: { status: "Published" },
                    },
                    {
                        label: "Views",
                        doctype: "Help View Log",
                        aggregate: "sum",
                        field: "view_count",
                        format: (v) => v > 1000 ? `${(v/1000).toFixed(1)}K` : v.toString(),
                    },
                    {
                        label: "Rating",
                        doctype: "Help Feedback",
                        aggregate: "avg",
                        field: "helpful",
                        format: (v) => `${Math.round(v * 100)}%`,
                        status_rules: { ">80": "success", ">60": "warning", "<=60": "danger" },
                    },
                    {
                        label: "Authors",
                        custom: async () => {
                            const r = await frappe.call({
                                method: "frappe.client.get_count",
                                args: {
                                    doctype: "Help Content",
                                    distinct: true,
                                    fields: ["owner"],
                                },
                            });
                            return r.message || 0;
                        },
                    },
                ],
                documents: [
                    {
                        label: "Pending Reviews",
                        doctype: "Help Content",
                        aggregate: "count",
                        filters: { status: "Draft" },
                    },
                ],
                refreshInterval: 30000,
            });

            return scene;
        } catch (e) {
            console.warn("Scene dashboard init failed:", e);
        }
    }

    // ─────────────────────────────────────────────────────────────────────
    // KPI Grid Component
    // ─────────────────────────────────────────────────────────────────────
    function renderKPIGrid(container) {
        const kpis = [
            { id: "topics", label: __("Total Topics"), value: 0, icon: "book", color: "#10B981" },
            { id: "views", label: __("Total Views"), value: 0, icon: "eye", color: "#3B82F6" },
            { id: "rating", label: __("Helpful Rate"), value: "0%", icon: "thumbs-up", color: "#F59E0B" },
            { id: "coverage", label: __("Coverage"), value: "0%", icon: "check-circle", color: "#8B5CF6" },
        ];

        const grid = document.createElement("div");
        grid.className = "ah-kpi-grid fv-fx-page-enter";
        grid.innerHTML = kpis.map(kpi => `
            <div class="ah-kpi-card fv-fx-glass fv-fx-hover-lift" data-kpi="${kpi.id}">
                <div class="ah-kpi-icon" style="color: ${kpi.color}">
                    <i data-feather="${kpi.icon}"></i>
                </div>
                <div class="ah-kpi-value" data-counter>${kpi.value}</div>
                <div class="ah-kpi-label">${kpi.label}</div>
            </div>
        `).join("");

        container.appendChild(grid);

        // Animate numbers on load
        animateKPIValues();

        return grid;
    }

    function animateKPIValues() {
        if (typeof gsap === "undefined") return;

        document.querySelectorAll(".ah-kpi-value[data-counter]").forEach(el => {
            const value = parseInt(el.textContent.replace(/[^\d]/g, "")) || 0;
            gsap.from(el, {
                textContent: 0,
                duration: 1.5,
                ease: "power2.out",
                snap: { textContent: 1 },
                onUpdate: function() {
                    const current = Math.round(gsap.getProperty(el, "textContent"));
                    if (el.dataset.kpi === "rating" || el.dataset.kpi === "coverage") {
                        el.textContent = current + "%";
                    } else if (current > 1000) {
                        el.textContent = (current / 1000).toFixed(1) + "K";
                    } else {
                        el.textContent = current;
                    }
                },
            });
        });
    }

    // ─────────────────────────────────────────────────────────────────────
    // Route-based visual page rendering
    // ─────────────────────────────────────────────────────────────────────
    $(document).on("page-change", function() {
        if (!frappe.visual || !frappe.visual.generator) return;

        const route = frappe.get_route_str();

        // Help Dashboard with Scene
        if (route === "arkan-help" || route === "Workspace/Arkan Help") {
            const page = frappe.container.page;
            if (page && page.main) {
                const container = page.main[0] || page.main;

                // Clear and add scene dashboard
                const header = document.createElement("div");
                header.className = "ah-scene-dashboard";
                header.id = "ah-scene-container";
                container.insertBefore(header, container.firstChild);

                initHelpDashboard(header);
            }
        }

        // Visual Settings Page
        if (route === "arkan-help-settings") {
            const page = frappe.container.page;
            if (page && page.main && frappe.visual.generator) {
                frappe.visual.generator.settingsPage(
                    page.main[0] || page.main,
                    "Help Settings"
                );
            }
        }

        // Visual Reports Hub
        if (route === "arkan-help-reports") {
            const page = frappe.container.page;
            if (page && page.main && frappe.visual.generator) {
                frappe.visual.generator.reportsHub(
                    page.main[0] || page.main,
                    "Arkan Help"
                );
            }
        }
    });

    // ─────────────────────────────────────────────────────────────────────
    // Form Enhancer — Visual Stats on Help Content Form
    // ─────────────────────────────────────────────────────────────────────
    $(document).on("form-refresh", function(e, frm) {
        if (frm.doctype !== "Help Content") return;
        if (!frappe.visual || !frappe.visual.formEnhancer) return;

        // Add view stats ribbon
        if (frm.doc.name && !frm.is_new()) {
            frappe.call({
                method: "arkan_help.api.v1.help.get_content_stats",
                args: { name: frm.doc.name },
                callback: (r) => {
                    if (r.message) {
                        addStatsRibbon(frm, r.message);
                    }
                },
            });
        }
    });

    function addStatsRibbon(frm, stats) {
        const ribbon = document.createElement("div");
        ribbon.className = "ah-stats-ribbon fv-fx-glass";
        ribbon.innerHTML = `
            <div class="ah-stat">
                <span class="ah-stat-value">${stats.views || 0}</span>
                <span class="ah-stat-label">${__("Views")}</span>
            </div>
            <div class="ah-stat">
                <span class="ah-stat-value">${stats.helpful_rate || 0}%</span>
                <span class="ah-stat-label">${__("Helpful")}</span>
            </div>
            <div class="ah-stat">
                <span class="ah-stat-value">${stats.related_count || 0}</span>
                <span class="ah-stat-label">${__("Related")}</span>
            </div>
        `;

        const header = frm.page.page_title;
        if (header) {
            header.parentNode.insertBefore(ribbon, header.nextSibling);
        }
    }

    // Export for external use
    frappe.provide("arkan_help.visual");
    arkan_help.visual = {
        initHelpDashboard,
        renderKPIGrid,
        animateKPIValues,
    };
})();
