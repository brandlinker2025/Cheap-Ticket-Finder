const assert = require("assert");
const TP = require("../js/travelpayouts");
// Live configured state: Lina's own marker 791994 + dashboard-generated tp.media link.
assert.strictEqual(TP.TRAVELPAYOUTS_MARKER, "791994");
const url = TP.aviasalesAffiliateUrl();
assert.ok(url, "configured affiliate URL must be emitted");
assert.ok(url.startsWith("https://tp.media/r?"), "must use the full tp.media link");
assert.ok(url.includes("marker=791994"), "link must carry marker=791994");
assert.ok(url.includes("sub_id=cheapticketfinder-site"), "link must carry sub_id");
assert.ok(url.includes("trs=587447"), "link must carry project trs=587447");
// isConfigured guards stay intact.
assert.strictEqual(TP.isConfigured("[TRAVELPAYOUTS MARKER]", "https://example.com/?marker=x"), false);
assert.strictEqual(TP.isConfigured("791994", ""), false);
assert.strictEqual(TP.isConfigured("791994", "https://example.com/?marker=999"), false);
assert.strictEqual(TP.isConfigured("791994", url), true);
assert.ok(TP.DISCLOSURE_EN.includes("/disclosure"));
assert.ok(TP.DISCLOSURE_BN.length > 0);
console.log("travelpayouts.test.js OK (live marker 791994)");

// Integration: cheapBookPath keeps Google Flights primary and adds Aviasales secondary.
global.TravelpayoutsAffiliate = TP;
const BookingLinks = require("../js/booking-links");
const path = BookingLinks.cheapBookPath({ origin: "DAC", dest: "BKK", depart: "2026-12-08", returnDate: "2026-12-17", tripType: "round" });
assert.strictEqual(path[0].id, "google-flights");
assert.strictEqual(path[0].tier, "primary");
const av = path.find((r) => r.id === "aviasales-affiliate");
assert.ok(av, "Aviasales affiliate row must appear when configured");
assert.strictEqual(av.tier, "secondary");
assert.strictEqual(av.affiliate, true);
assert.strictEqual(av.url, url);
assert.ok(path.indexOf(av) > 0, "Aviasales must be after Google Flights primary");
assert.ok(path.some((r) => r.id === "gozayaan"), "existing GoZayaan row must not break");
console.log("travelpayouts integration OK (Google primary, Aviasales secondary)");
