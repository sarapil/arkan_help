// Copyright (c) 2024, Arkan Lab — https://arkan.it.com
// License: MIT

frappe.pages["arkan-help-onboarding"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Arkan Help Onboarding"),
        single_column: true,
    });

    page.main.addClass("arkan-help-onboarding-page");
    const $container = $('<div class="fv-onboarding-container"></div>').appendTo(page.main);

    const steps = [
        {
                "title": "Enable Help Settings",
                "description": "Activate field help, navbar help, and file-based help in Help Settings.",
                "icon": "settings"
        },
        {
                "title": "App Structure",
                "description": "See Arkan Help modules.",
                "icon": "sitemap",
                "component": "app-map"
        },
        {
                "title": "Create Help Topics",
                "description": "Write help content for your DocTypes using the Help Topic form.",
                "icon": "file-text"
        },
        {
                "title": "Data Model",
                "description": "How Help Topics, Content, and Contexts relate.",
                "icon": "hierarchy-2",
                "component": "erd",
                "doctype": "Help Topic"
        },
        {
                "title": "File-Based Help",
                "description": "Create markdown files in app/help/en/ and app/help/ar/ directories.",
                "icon": "markdown"
        },
        {
                "title": "Verify Integration",
                "description": "Check that \u24d8 icons appear on forms and \u2753 works in navbar.",
                "icon": "rocket"
        }
];

    // Use frappe.visual.generator for premium wizard rendering
    const renderWithGenerator = () => {
        try {
            frappe.visual.generator.onboardingWizard(
                $container[0],
                "Arkan Help",
                steps.map(s => ({
                    ...s,
                    onComplete: s.title.includes("rocket") || s.title.includes("Ready") || s.title.includes("Go Live") || s.title.includes("Start")
                        ? () => frappe.set_route("app")
                        : undefined,
                }))
            );
        } catch(e) {
            console.warn("Generator failed, using fallback:", e);
            renderFallback($container, steps);
        }
    };

    const renderFallback = ($el, steps) => {
        const stepsHtml = steps.map((s, i) => `
            <div style="display:flex;gap:16px;padding:20px 0;border-bottom:1px solid var(--border-color)">
                <div style="width:40px;height:40px;border-radius:50%;background:rgba(99,102,241,0.1);color:#10B981;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">${i+1}</div>
                <div><h3 style="font-size:1rem;font-weight:600;margin-bottom:4px">${__(s.title)}</h3><p style="font-size:0.9rem;color:var(--text-muted)">${__(s.description)}</p></div>
            </div>
        `).join('');
        $el.html(`
            <div style="text-align:center;padding:60px 20px">
                <h1>🚀 ${__("Get Started with Arkan Help")}</h1>
                <p style="color:var(--text-muted)">${__("Follow these steps to set up and master Arkan Help.")}</p>
            </div>
            <div style="max-width:700px;margin:0 auto;padding:0 20px">${stepsHtml}</div>
        `);
    };

    if (frappe.visual && frappe.visual.generator) {
        renderWithGenerator();
    } else {
        frappe.require("frappe_visual.bundle.js", () => {
            if (frappe.visual && frappe.visual.generator) {
                renderWithGenerator();
            } else {
                renderFallback($container, steps);
            }
        });
    }
};
