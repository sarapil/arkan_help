// Copyright (c) 2024, Arkan Lab — https://arkan.it.com
// License: MIT

frappe.pages["arkan-help-about"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("About Arkan Help"),
        single_column: true,
    });

    page.main.addClass("arkan-help-about-page");
    const $container = $('<div class="fv-about-container"></div>').appendTo(page.main);

    // Use frappe.visual.generator for premium rendering
    const renderWithGenerator = async () => {
        try {
            await frappe.visual.generator.aboutPage(
                $container[0],
                "arkan_help",
                {
                    color: "#10B981",
                    mainDoctype: "Help Topic",
                    features: [
        {
                "icon": "help-circle",
                "title": "Contextual Help",
                "description": "6-level specificity ladder \u2014 exact field+role match to fallback language."
        },
        {
                "icon": "file-text",
                "title": "File-Based Help",
                "description": "Markdown help files per DocType with field-level anchors."
        },
        {
                "icon": "info-circle",
                "title": "Field Help Icons",
                "description": "\u24d8 icons on form fields with inline help tooltips."
        },
        {
                "icon": "compass",
                "title": "Navbar Help",
                "description": "\u2753 icon in navbar for page-level contextual help."
        },
        {
                "icon": "language",
                "title": "Multilingual",
                "description": "Arabic + English with automatic fallback resolution."
        },
        {
                "icon": "layout-dashboard",
                "title": "Help Dashboard",
                "description": "Track help coverage, views, and missing content."
        }
],
                    roles: [
        {
                "name": "Help Author",
                "icon": "edit",
                "description": "Create and edit help content for all DocTypes."
        },
        {
                "name": "Help Admin",
                "icon": "shield-check",
                "description": "Configure help settings and manage help coverage."
        }
],
                    ctas: [
                        { label: __("Start Onboarding"), route: "arkan-help-onboarding", primary: true },
                        { label: __("Open Settings"), route: "app/help-settings" },
                    ],
                }
            );
        } catch(e) {
            console.warn("Generator failed, using fallback:", e);
            renderFallback($container);
        }
    };

    const renderFallback = ($el) => {
        $el.html(`
            <div style="text-align:center;padding:60px 20px">
                <h1 style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#10B981,#333);-webkit-background-clip:text;-webkit-text-fill-color:transparent">${__("Arkan Help")}</h1>
                <p style="font-size:1.15rem;color:var(--text-muted);max-width:600px;margin:16px auto">${__("6-level specificity ladder — exact field+role match to fallback language.")}</p>
                <div style="margin-top:24px">
                    <a href="/app/arkan-help-onboarding" class="btn btn-primary btn-lg">${__("Start Onboarding")}</a>
                </div>
            </div>
        `);
    };

    if (frappe.visual && frappe.visual.generator) {
        renderWithGenerator();
    } else {
        frappe.require("frappe_visual.bundle.js", () => {
            if (frappe.visual && frappe.visual.generator) {
                renderWithGenerator();
            } else {
                renderFallback($container);
            }
        });
    }
};
