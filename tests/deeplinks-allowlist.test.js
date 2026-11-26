// Deep links for every trip type are valid https URLs on allow-listed hosts; the outbound allow-list
// rejects open-redirect tricks; affiliate parameters survive; every static outbound href is allow-listed.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");
const B = require(path.join(root, "js/booking-links.js"));
const TP = require(path.join(root, "js/travelpayouts.js"));
let checked = 0;

function assertValid(url, label) {
    assert.ok(typeof url === "string" && url.length, `${label}: empty url`);
    let u;
    assert.doesNotThrow(() => { u = new URL(url); }, `${label}: not a URL: ${url}`);
    assert.strictEqual(u.protocol, "https:", `${label}: must be https: ${url}`);
    assert.ok(!/\s/.test(url), `${label}: whitespace in URL`);
    assert.ok(!/undefined|NaN|null/.test(url), `${label}: placeholder leaked into URL: ${url}`);
    assert.ok(B.isAllowedOutbound(url), `${label}: host not on outbound allow-list: ${url}`);
    checked++;
}

// ---- 1. Allow-list behaviour -----------------------------------------------------------------
const good = [
    "https://www.google.com/travel/flights/search?tfs=abc",
    "https://www.aviasales.com/search/DAC1012BKK1",
    "https://www.trip.com/flights/showfarefirst?dcity=dac&acity=bkk&Allianceid=11059812&SID=333836392",
    "https://fo-usba.ttinteractive.com/Zenith/FrontOffice/USBangla/en-GB/Home",
    TP.aviasalesAffiliateUrl(),
];
for (const u of good) assert.ok(B.isAllowedOutbound(u), `should allow ${u}`);
const bad = [
    "http://www.trip.com/flights",                                  // plain http
    "javascript:alert(1)",
    "data:text/html,hi",
    "//evil.example/x",
    "https://evil.example/?u=https://www.trip.com",
    "https://www.trip.com.evil.example/",                           // suffix trick
    "https://eviltrip.com/",                                        // not a subdomain
    "https://www.google.com@evil.example/",                         // userinfo trick
    "https://www.google.com/url?q=https://evil.example",            // Google open redirect
    "https://www.google.com:8443/travel/flights",
    "https://tp.media/r?marker=791994&u=https%3A%2F%2Fevil.example%2F",  // affiliate redirector to unknown host
    "https://tp.media/r?marker=791994&u=javascript%3Aalert(1)",
    "not a url",
    "",
];
for (const u of bad) assert.ok(!B.isAllowedOutbound(u), `should reject ${u}`);
assert.strictEqual(B.safeOutboundUrl("https://evil.example/", "#"), "#");
const aff = "https://tp.media/r?campaign_id=100&marker=791994&p=4114&sub_id=x&trs=587447&u=https%3A%2F%2Fwww.aviasales.com%2Fsearch%2FDAC1012BKK1";
assert.strictEqual(B.safeOutboundUrl(aff), aff, "safeOutboundUrl must return allowed URLs byte-for-byte (affiliate params preserved)");

// ---- 2. Builders: one-way, round-trip, multi-city, nearby, flexible, market comparison ---------
const dep = "2027-02-10", ret = "2027-02-20";
const routes = [["DAC", "BKK"], ["DAC", "CXB"], ["DAC", "LHR"], ["CGP", "DXB"], ["DAC", "KUL"], ["ZYL", "JED"], ["DAC", "SIN"], ["DAC", "CCU"]];
const paxes = [{}, { adults: 2, children: 1, infants: 1, cabin: "business" }];
for (const [o, d] of routes) {
    for (const p of paxes) {
        for (const tripType of ["oneway", "round"]) {
            const opts = Object.assign({ origin: o, dest: d, depart: dep, returnDate: ret, tripType }, p);
            const gf = B.googleFlightsUrl(opts);
            assertValid(gf, `GF ${tripType} ${o}-${d}`);
            assert.ok(/\/travel\/flights\/search\?tfs=/.test(gf) && !/[?&]q=/.test(gf));
            const gfNear = B.googleFlightsUrl(Object.assign({}, opts, { nearbyAirports: true }));
            assertValid(gfNear, `GF nearby ${o}-${d}`);
            assertValid(B.skyscannerUrl(opts), `Skyscanner ${tripType}`);
            assertValid(B.kayakUrl(opts), `Kayak ${tripType}`);
            const av = B.aviasalesLegUrl(o, d, dep, p, TP.aviasalesAffiliateUrl());
            assertValid(av, "Aviasales leg");
            for (const row of B.cheapBookPath(opts)) if (row.url) assertValid(row.url, `cheapBookPath ${row.id} ${tripType} ${o}-${d}`);
            for (const row of B.nearbyCountryDepartureLinks(opts)) {
                assertValid(row.url, `nearby-country ${row.id}`);
                if (/trip\.com/.test(row.url)) assert.ok(/Allianceid=11059812/.test(row.url) && /SID=333836392/.test(row.url), "Trip.com affiliate params kept");
            }
            for (const row of B.cheaperNearbyAirportLinks(opts)) assertValid(row.url, `nearby airport ${row.code || ""}`);
            for (const row of B.comparatorLinks(opts)) if (row.url) assertValid(row.url, `comparator ${row.id || row.name}`);
            const bundle = B.dateLinkBundle(opts, "2027-02-12");
            if (bundle) JSON.stringify(bundle).replace(/"(https:[^"]+)"/g, (_, u) => { assertValid(u, "dateLinkBundle"); return _; });
            for (const row of B.monthOverviewLinks(opts) || []) if (row.url) assertValid(row.url, "month overview");
        }
    }
}
// Round-trip vs one-way really differ in what they encode.
const ow = B.kayakUrl({ origin: "DAC", dest: "BKK", depart: dep, returnDate: ret, tripType: "oneway" });
const rt = B.kayakUrl({ origin: "DAC", dest: "BKK", depart: dep, returnDate: ret, tripType: "round" });
assert.ok(!ow.includes(ret) && rt.includes(ret), "one-way must not carry a return date; round-trip must");

// Multi-city: 2..6 legs, each leg a dated Aviasales (affiliate) + Google Flights one-way link.
const legs = [
    { origin: "DAC", dest: "BKK", date: "2027-03-01" },
    { origin: "BKK", dest: "HKT", date: "2027-03-05" },
    { origin: "HKT", dest: "KUL", date: "2027-03-09" },
    { origin: "KUL", dest: "DAC", date: "2027-03-14" },
];
const mc = B.multiCityLegLinks(legs, { adults: 2 }, TP.aviasalesAffiliateUrl());
assert.strictEqual(mc.length, 4);
mc.forEach((row, i) => {
    assertValid(row.aviasales, `multi-city leg ${i + 1} aviasales`);
    assertValid(row.google, `multi-city leg ${i + 1} google`);
    const target = decodeURIComponent(new URL(row.aviasales).searchParams.get("u"));
    const dd = legs[i].date.slice(8, 10) + legs[i].date.slice(5, 7);
    assert.strictEqual(target, `https://www.aviasales.com/search/${legs[i].origin}${dd}${legs[i].dest}2`, `leg ${i + 1} target`);
    assert.ok(row.aviasales.includes("marker=791994") && row.aviasales.includes("trs=587447"), "Travelpayouts marker preserved");
});
assert.strictEqual(B.multiCityLegLinks(legs.slice(0, 1)).length, 0, "multi-city needs >= 2 legs");
assert.strictEqual(B.aviasalesLegUrl("DAC", "DAC", "2027-03-01"), null, "same origin/dest rejected");
assert.strictEqual(B.aviasalesLegUrl("DAC", "BKK", "2027-02-30"), null, "impossible date rejected");
assert.strictEqual(B.aviasalesLegUrl("DA<", "BKK", "2027-03-01"), null, "bad IATA rejected");
assert.strictEqual(B.aviasalesLegUrl("DAC", "BKK", "2027-03-01"), "https://www.aviasales.com/search/DAC0103BKK1", "no affiliate -> plain dated search");

// Flexible dates: +/- days stay valid ISO dates.
const flex = B.flexibleNearbyDays ? B.flexibleNearbyDays({ origin: "DAC", dest: "BKK", depart: dep, returnDate: ret, tripType: "round" }) : [];
for (const f of flex || []) JSON.stringify(f).replace(/"(https:[^"]+)"/g, (_, u) => { assertValid(u, "flexible"); return _; });

// Hotels + surface transport links rendered next to flights.
for (const row of B.hotelLinks({ city: B.hotelCityForCode("BKK"), checkin: dep, checkout: ret })) assertValid(row.url, `hotel ${row.id}`);
for (const row of B.bdSurfaceTransportLinks()) assertValid(row.url, `bd-transport ${row.id}`);

// ---- 3. Every static outbound <a href> on the site is allow-listed ---------------------------
function htmlFiles(dir, out = []) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        if ([".git", "node_modules", "tests", "scripts"].includes(e.name)) continue;
        const p = path.join(dir, e.name);
        if (e.isDirectory()) htmlFiles(p, out); else if (e.name.endsWith(".html")) out.push(p);
    }
    return out;
}
let staticLinks = 0;
for (const f of htmlFiles(root)) {
    const s = fs.readFileSync(f, "utf8");
    for (const m of s.matchAll(/<a\b[^>]*\bhref="(https?:[^"]+)"/g)) {
        const url = m[1].replace(/&amp;/g, "&");
        assert.ok(B.isAllowedOutbound(url), `${path.relative(root, f)}: outbound link not on allow-list: ${url}`);
        staticLinks++;
    }
    // Links opened in a new tab must not leak window.opener.
    for (const m of s.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g)) {
        assert.ok(/\brel="/.test(m[0]) && /noopener/.test(m[0]), `${path.relative(root, f)}: target=_blank without noopener: ${m[0].slice(0, 120)}`);
    }
}
// Dynamic hrefs in the homepage go through the outbound guard.
for (const f of ["index.html", "bn/index.html"]) {
    const s = fs.readFileSync(path.join(root, f), "utf8");
    assert.ok(!/href="\$\{item\.(url|sourceUrl)\}"/.test(s), `${f}: dynamic item href must use outHref()`);
    assert.ok(s.includes("function outHref(url)") && s.includes("BookingLinks.safeOutboundUrl"), `${f}: outbound guard missing`);
    assert.ok(s.includes("BookingLinks.aviasalesLegUrl("), `${f}: multi-city legs must use the tested builder`);
}
console.log(`deeplinks-allowlist.test.js OK (${checked} builder URLs valid+allow-listed, ${staticLinks} static outbound links, ${bad.length} redirect tricks rejected)`);
