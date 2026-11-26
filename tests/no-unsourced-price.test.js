// Rule: the site never shows a flight price unless it is either
//   (a) live data from a configured fare API (rendered at runtime, with source + fetched time), or
//   (b) a dated historical snapshot wrapped in <!-- fare-snapshot:start recorded=".." source=".." --> ... end
//       with a visible "not a live price" label.
// Any other hard-coded currency amount in page text or structured data fails this test.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");

// Non-flight pages whose amounts are published fees / coverage minimums with a cited source on the page.
const NON_FARE_SOURCED = {
    "medical/index.html": /সূত্র|Source/,
    "travel-insurance/index.html": /Schengen|schengen/,
};
const MONEY = /(US\$|\$|৳|€|£|₹|\bBDT|\bUSD|\bINR|\bMYR|\bTk\.?|\bRM)\s?[0-9০-৯][0-9০-৯,.]*|[0-9০-৯][0-9০-৯,]{2,}\s?(টাকা|taka|BDT|USD|ডলার)/g;

function htmlFiles(dir, out = []) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        if ([".git", "node_modules", "tests", "scripts", "logo-options"].includes(e.name)) continue;
        const p = path.join(dir, e.name);
        if (e.isDirectory()) htmlFiles(p, out);
        else if (e.name.endsWith(".html")) out.push(p);
    }
    return out;
}

let regions = 0, pages = 0;
for (const file of htmlFiles(root)) {
    const rel = path.relative(root, file).split(path.sep).join("/");
    let s = fs.readFileSync(file, "utf8");
    pages++;
    // Structured data: a money amount must sit in a sentence that says it is a dated snapshot.
    for (const m of s.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
        const data = JSON.parse(m[1]);
        const walk = (v) => {
            if (typeof v === "string") {
                if (v.match(MONEY) && !NON_FARE_SOURCED[rel]) assert.ok(/historical snapshot|পুরোনো স্ন্যাপশট/i.test(v), `${rel}: JSON-LD text has a price without a snapshot label: ${v.slice(0, 120)}`);
            } else if (v && typeof v === "object") {
                for (const [k, x] of Object.entries(v)) {
                    assert.ok(!["price", "lowPrice", "highPrice", "priceCurrency"].includes(k), `${rel}: JSON-LD must not declare ${k} (no live fare source)`);
                    walk(x);
                }
            }
        };
        walk(data);
    }
    s = s.replace(/<script\b[\s\S]*?<\/script>/g, "").replace(/<style\b[\s\S]*?<\/style>/g, "");
    // Snapshot regions: must carry recorded date + source + visible label.
    s = s.replace(/<!-- fare-snapshot:start ([^>]*?)-->([\s\S]*?)<!-- fare-snapshot:end -->/g, (all, attrs, body) => {
        regions++;
        assert.ok(/recorded="\d{4}-\d{2}-\d{2}"/.test(attrs), `${rel}: snapshot region needs recorded="YYYY-MM-DD"`);
        assert.ok(/source="[^"]{8,}"/.test(attrs), `${rel}: snapshot region needs a source`);
        assert.ok(/class="fare-snapshot-label[^"]*"/.test(body), `${rel}: snapshot region needs a visible label`);
        assert.ok(/not (a )?live price|লাইভ দাম নয়/i.test(body), `${rel}: snapshot label must say it is not a live price`);
        return "";
    });
    assert.ok(!s.includes("fare-snapshot:start"), `${rel}: unterminated fare-snapshot region`);
    const text = s.replace(/<[^>]+>/g, " ");
    const hits = text.match(MONEY) || [];
    if (hits.length && NON_FARE_SOURCED[rel]) {
        assert.ok(NON_FARE_SOURCED[rel].test(text), `${rel}: published amounts need a cited source`);
        continue;
    }
    // A snapshot price quoted in prose must say so in the same sentence.
    for (const sentence of text.split(/(?<=[.!?।])\s+/)) {
        if (!sentence.match(MONEY)) continue;
        assert.ok(/historical snapshot|পুরোনো স্ন্যাপশট/i.test(sentence), `${rel}: unsourced price in text: "${sentence.trim().slice(0, 160)}"`);
    }
}
assert.ok(regions >= 5, "expected the dated fare snapshots to be wrapped (home en/bn, Kolkata study, price hub en/bn)");

// Runtime builders must never emit a price.
const B = require(path.join(root, "js/booking-links.js"));
const d = "2027-01-10", r = "2027-01-17";
for (const [o, dest] of [["DAC", "BKK"], ["DAC", "CXB"], ["DAC", "LHR"], ["CGP", "DXB"]]) {
    for (const tripType of ["oneway", "round"]) {
        const rows = B.cheapBookPath({ origin: o, dest, depart: d, returnDate: r, tripType });
        for (const row of rows) {
            for (const k of ["price", "fare", "amount", "total"]) assert.ok(!(k in row) || row[k] == null, `cheapBookPath row ${row.id} has ${k}`);
            const label = `${row.name || ""} ${row.note || ""} ${row.blurb || ""}`;
            assert.ok(!label.match(MONEY), `cheapBookPath row text shows an amount: ${label}`);
        }
    }
}

// Fare calendar API: no token -> 503 honest "not configured", never sample data.
const api = require(path.join(root, "api/fare-calendar.js"));
function mockRes() { const r = { code: 0, body: null, headers: {} }; r.status = (c) => { r.code = c; return r; }; r.json = (b) => { r.body = b; return r; }; r.setHeader = (k, v) => { r.headers[k] = v; }; return r; }
(async () => {
    const saved = process.env.TRAVELPAYOUTS_API_TOKEN; delete process.env.TRAVELPAYOUTS_API_TOKEN;
    const res = mockRes();
    await api({ method: "GET", query: { origin: "DAC", destination: "DXB", month: "2027-01" } }, res);
    assert.strictEqual(res.code, 503);
    assert.ok(!("fares" in res.body), "no fares without a configured source");
    if (saved !== undefined) process.env.TRAVELPAYOUTS_API_TOKEN = saved;
    console.log(`no-unsourced-price.test.js OK (${pages} pages scanned, ${regions} dated snapshot regions, builders + API price-free)`);
})().catch((e) => { console.error(e); process.exit(1); });
