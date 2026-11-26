// SEO readiness (sitemap, canonical, robots, JSON-LD, ads.txt) + /api input validation.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");
const ORIGIN = "https://cheapticketfinder.site";

// robots + ads.txt
const robots = read("robots.txt");
assert.ok(robots.includes(`Sitemap: ${ORIGIN}/sitemap.xml`), "robots.txt must point at the sitemap");
assert.ok(!/^Disallow:\s*\/\s*$/m.test(robots), "robots.txt must not block the whole site");
assert.ok(/^google\.com, pub-\d{16}, DIRECT, f08c47fec0942fa0$/m.test(read("ads.txt")), "ads.txt AdSense line");

// sitemap: well-formed, unique, every <loc> maps to a real page with a matching canonical
const sm = read("sitemap.xml");
assert.ok(sm.startsWith('<?xml version="1.0" encoding="UTF-8"?>') && sm.includes('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'));
assert.strictEqual((sm.match(/<url>/g) || []).length, (sm.match(/<\/url>/g) || []).length, "unbalanced <url>");
const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
assert.ok(locs.length >= 50, "sitemap too small");
assert.strictEqual(new Set(locs).size, locs.length, "duplicate sitemap URLs");
for (const m of sm.matchAll(/<lastmod>([^<]+)<\/lastmod>/g)) assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(m[1]), `bad lastmod ${m[1]}`);
const norm = (u) => u.replace(/\/$/, "");
for (const loc of locs) {
    assert.ok(loc.startsWith(ORIGIN + "/"), `sitemap URL off-site: ${loc}`);
    const rel = new URL(loc).pathname.replace(/^\//, "");
    const file = rel === "" ? "index.html" : /\.[a-z]+$/.test(rel) ? rel : path.join(rel, "index.html");
    assert.ok(fs.existsSync(path.join(root, file)), `sitemap URL has no page: ${loc}`);
    if (!file.endsWith(".html")) continue;
    const html = read(file);
    const canon = (html.match(/<link rel="canonical" href="([^"]+)"/) || [])[1];
    assert.ok(canon, `${file}: missing canonical`);
    assert.strictEqual(norm(canon), norm(loc), `${file}: canonical ${canon} != sitemap ${loc}`);
    assert.ok(/<meta name="viewport" content="width=device-width/.test(html), `${file}: missing mobile viewport`);
    assert.ok(/<title>[^<]{5,}<\/title>/.test(html), `${file}: missing title`);
    assert.ok(!/<meta name="robots" content="[^"]*noindex/.test(html), `${file}: sitemap page is noindex`);
    for (const j of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
        let data;
        assert.doesNotThrow(() => { data = JSON.parse(j[1]); }, `${file}: invalid JSON-LD`);
        assert.strictEqual(data["@context"], "https://schema.org", `${file}: JSON-LD @context`);
    }
}

// /api input validation (no network: every case below fails before any fetch)
function mockRes() { const r = { code: 0, body: null, headers: {} }; r.status = (c) => { r.code = c; return r; }; r.json = (b) => { r.body = b; return r; }; r.setHeader = (k, v) => { r.headers[k] = v; }; return r; }
const fare = require(path.join(root, "api/fare-calendar.js"));
const geo = require(path.join(root, "api/geo-flight.js"));
const future = new Date(Date.now() + 30 * 864e5).toISOString().slice(0, 10);
(async () => {
    const call = async (fn, method, query) => { const r = mockRes(); await fn({ method, query }, r); return r; };
    assert.strictEqual((await call(fare, "POST", {})).code, 405);
    for (const q of [{}, { origin: "DAC", destination: "DAC", month: "2027-01" }, { origin: "DA", destination: "BKK", month: "2027-01" },
        { origin: "DAC", destination: "BKK", month: "2027-13" }, { origin: ["DAC"], destination: "BKK", month: "2027-01" },
        { origin: "DAC'--", destination: "BKK", month: "2027-01" }]) {
        assert.strictEqual((await call(fare, "GET", q)).code, 400, `fare-calendar should reject ${JSON.stringify(q)}`);
    }
    const saved = { tp: process.env.TRAVELPAYOUTS_API_TOKEN, df: process.env.DUFFEL_ACCESS_TOKEN };
    delete process.env.TRAVELPAYOUTS_API_TOKEN; delete process.env.DUFFEL_ACCESS_TOKEN;
    const nc = await call(fare, "GET", { origin: "dac", destination: "bkk", month: "2027-01" });
    assert.strictEqual(nc.code, 503); assert.strictEqual(nc.body.status, "not_configured");

    assert.strictEqual((await call(geo, "POST", {})).code, 405);
    for (const q of [{}, { origin: "DAC", destination: "BKK" }, { origin: "DAC", destination: "BKK", date: "2020-01-01" },
        { origin: "DAC", destination: "BKK", date: "2027-02-30" }, { origin: "DAC", destination: "DAC", date: future },
        { origin: "<x>", destination: "BKK", date: future }, { origin: "DAC", destination: "BKK", date: future, currency: "XXX" }]) {
        const r = await call(geo, "GET", q);
        assert.strictEqual(r.code, 400, `geo-flight should reject ${JSON.stringify(q)}`);
        assert.strictEqual(r.body.success, false);
    }
    const g1 = await call(geo, "GET", { origin: "dac", destination: "bkk", date: future });
    assert.strictEqual(g1.code, 503); assert.strictEqual(g1.body.status, "not_configured"); assert.ok(!("data" in g1.body));
    process.env.DUFFEL_ACCESS_TOKEN = "duffel_test_dummy";
    const g2 = await call(geo, "GET", { origin: "DAC", destination: "BKK", date: future });
    assert.strictEqual(g2.code, 503); assert.strictEqual(g2.body.status, "test_mode", "Duffel test-mode offers are never shown as prices");
    for (const [k, v] of [["TRAVELPAYOUTS_API_TOKEN", saved.tp], ["DUFFEL_ACCESS_TOKEN", saved.df]]) { if (v === undefined) delete process.env[k]; else process.env[k] = v; }
    console.log(`seo-api.test.js OK (${locs.length} sitemap URLs with canonicals + valid JSON-LD; API validation 405/400/503 cases)`);
})().catch((e) => { console.error(e); process.exit(1); });
