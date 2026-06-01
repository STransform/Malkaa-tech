/** @odoo-module **/

const TRACKED_KEY = "sigma_backend_theme_visit_tracked";

async function trackSigmaThemeVisit() {
    if (sessionStorage.getItem(TRACKED_KEY)) {
        return;
    }
    sessionStorage.setItem(TRACKED_KEY, "1");
    try {
        await fetch("/sigma_backend_theme/track_visit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {},
                id: Date.now(),
            }),
        });
    } catch {
        // Tracking must never interrupt the Odoo backend.
    }
}

trackSigmaThemeVisit();
