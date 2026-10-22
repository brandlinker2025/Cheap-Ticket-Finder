#!/usr/bin/env node
/**
 * Dead-link checker for Cheap Ticket Finder.
 * Usage: node scripts/check-links.js [--base https://preview.example] [--json out.json]
 * Collects every http(s) href in *.html and every URL literal in js/*.js, plus the
 * dynamic links BookingLinks builds for sample routes, then requests each one.
 * DEAD = 404/410 or DNS/connection failure. BLOCKED = 401/403/429/5xx (site refuses bots; check by hand).
 * Exit code 1 if any DEAD link is found.
 */
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");
const args = process.argv.slice(2);
const base = args.includes("--base") ? args[args.indexOf("--base") + 1].replace(/\/$/, "") : "https://cheapticketfinder.site";
const jsonOut = args.includes("--json") ? args[args.indexOf("--json") + 1] : null;

function walk(dir, out = []) {
    for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
        if (["node_modules", ".git", "tests", "shots", ".vercel"].includes(f.name)) continue;
        const p = path.join(dir, f.name);
        if (f.isDirectory()) walk(p, out);
        else if (/\.(html|js)$/.test(f.name) && !p.includes(`${path.sep}scripts${path.sep}`)) out.push(p);
    }
    return out;
}
const urls = new Map();
function add(u, from) {
    u = u.replace(/&amp;/g, "&");
    if (/\$\{|\[|\]|%s|example\.|localhost|schema\.org|w3\.org|tpwdg\.com|_vercel\/insights/.test(u)) return;
    if (!urls.has(u)) urls.set(u, new Set());
    urls.get(u).add(from);
}
for (const file of walk(root)) {
    const rel = path.relative(root, file);
    const txt = fs.readFileSync(file, "utf8");
    for (const m of txt.matchAll(/href="([^"#][^"]*)"/g)) {
        let h = m[1];
        if (/^(mailto|tel|javascript):/.test(h)) continue;
        if (h.startsWith("/")) h = base + h; else if (!/^https?:/.test(h)) continue;
        add(h, rel);
    }
    if (rel.endsWith(".js")) for (const m of txt.matchAll(/["'`](https?:\/\/[^"'`\s]+)["'`]/g)) add(m[1], rel);
}
try {
    const B = require(path.join(root, "js/booking-links.js"));
    const d = new Date(); d.setDate(d.getDate() + 30); const r = new Date(d); r.setDate(r.getDate() + 7);
    for (const [o, dest] of [["DAC", "BKK"], ["DAC", "CXB"], ["DAC", "KUL"], ["DAC", "DXB"]]) {
        const opts = { origin: o, dest, depart: d, returnDate: r, tripType: "round", adults: 2, children: 1, infants: 0, cabin: "economy" };
        for (const row of B.cheapBookPath(opts)) if (row.url) add(row.url, `dynamic ${o}-${dest}`);
        for (const row of B.hotelLinks({ city: B.hotelCityForCode(dest), checkin: B.toISODate(d), checkout: B.toISODate(r) })) add(row.url, `dynamic hotel ${dest}`);
    }
    for (const row of B.bdSurfaceTransportLinks()) add(row.url, "dynamic bd-transport");
} catch (e) { console.warn("dynamic links skipped:", e.message); }

async function check(u) {
    const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 20000);
    try {
        const res = await fetch(u, { redirect: "follow", signal: ctl.signal, headers: { "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36 CTF-linkcheck" } });
        return { status: res.status, final: res.url };
    } catch (e) { return { status: 0, error: String(e.cause && e.cause.code || e.name) }; }
    finally { clearTimeout(t); }
}
(async () => {
    const list = [...urls.keys()]; const results = []; let i = 0;
    async function worker() { while (i < list.length) { const u = list[i++]; const r = await check(u); results.push({ url: u, ...r, from: [...urls.get(u)].slice(0, 3) }); } }
    await Promise.all(Array.from({ length: 8 }, worker));
    for (const r of results) r.verdict = (r.status === 404 || r.status === 410 || (r.status === 0 && /ENOTFOUND|ECONNREFUSED/.test(r.error || ""))) ? "DEAD" : (r.status >= 200 && r.status < 400) ? "OK" : "BLOCKED";
    results.sort((a, b) => a.verdict.localeCompare(b.verdict) || a.url.localeCompare(b.url));
    const sum = { OK: 0, BLOCKED: 0, DEAD: 0 }; results.forEach((r) => sum[r.verdict]++);
    for (const r of results) if (r.verdict !== "OK") console.log(`${r.verdict}\t${r.status || r.error}\t${r.url}\t<- ${r.from.join(", ")}`);
    console.log(`\n${results.length} links: ${sum.OK} OK, ${sum.BLOCKED} BLOCKED (bot-refused/timeout, verify by hand), ${sum.DEAD} DEAD`);
    if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(results, null, 1));
    process.exit(sum.DEAD ? 1 : 0);
})();
