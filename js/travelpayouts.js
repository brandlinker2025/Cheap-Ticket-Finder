/**
 * Cheap Ticket Finder — Travelpayouts / Aviasales affiliate link.
 *
 * Configured with RS Lina's own generated link (project 587447, marker 791994).
 * Dashboard-generated full tp.media link — do not hand-build a dated Aviasales URL.
 * Google Flights stays the primary / cheap path; this only adds a secondary row.
 */
(function (root, factory) {
    const api = factory();
    if (typeof module === "object" && module.exports) {
        module.exports = api;
    } else {
        root.TravelpayoutsAffiliate = api;
    }
})(typeof self !== "undefined" ? self : this, function () {
    "use strict";

    const TRAVELPAYOUTS_MARKER = "791994";
    const GENERATED_AFFILIATE_LINK = "https://tp.media/r?campaign_id=100&marker=791994&p=4114&sub_id=cheapticketfinder-site&trs=587447&u=https%3A%2F%2Faviasales.com";

    function isConfigured(marker, link) {
        const m = String(marker || "").trim();
        const u = String(link || "").trim();
        if (!m || m === "[TRAVELPAYOUTS MARKER]") return false;
        if (!/^https:\/\//i.test(u)) return false;
        return u.includes("marker=" + encodeURIComponent(m)) || u.includes(m);
    }

    function aviasalesAffiliateUrl() {
        if (!isConfigured(TRAVELPAYOUTS_MARKER, GENERATED_AFFILIATE_LINK)) return null;
        return GENERATED_AFFILIATE_LINK;
    }

    const DISCLOSURE_EN = "Affiliate link — we may earn a commission if you book; your price does not increase. See /disclosure.";
    const DISCLOSURE_BN = "অ্যাফিলিয়েট লিংক — বুক করলে আমরা কমিশন পেতে পারি; আপনার দাম বাড়বে না।";

    return { TRAVELPAYOUTS_MARKER, GENERATED_AFFILIATE_LINK, isConfigured, aviasalesAffiliateUrl, DISCLOSURE_EN, DISCLOSURE_BN };
});
