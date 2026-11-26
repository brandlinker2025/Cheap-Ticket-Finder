// Mobile check: key pages at 390px wide must not scroll horizontally.
// Run: npm run test:mobile   (needs Playwright + Chromium; third-party requests are blocked for determinism)
const http = require("http");
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) { console.log("NOT TESTED: playwright not installed"); process.exit(0); }

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".webp": "image/webp", ".png": "image/png", ".svg": "image/svg+xml", ".json": "application/json", ".ico": "image/x-icon", ".jpg": "image/jpeg" };
const server = http.createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
    let f = path.join(root, p);
    if (!f.startsWith(root)) { res.writeHead(403); return res.end(); }
    if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, "index.html");
    if (!fs.existsSync(f)) { res.writeHead(404); return res.end("not found"); }
    res.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" });
    fs.createReadStream(f).pipe(res);
});
const PAGES = ["/", "/bn/", "/fare-calendar/", "/air-ticket-price-bangladesh/", "/cheaper-flights-from-kolkata/",
    "/dhaka-to-bangkok-cheap-ticket/", "/hotels/", "/offers/", "/airlines/", "/esim/"];

server.listen(0, "127.0.0.1", async () => {
    const base = `http://127.0.0.1:${server.address().port}`;
    const browser = await chromium.launch();
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
    await ctx.route("**/*", (r) => (r.request().url().startsWith(base) ? r.continue() : r.abort()));
    let fail = 0;
    for (const p of PAGES) {
        const page = await ctx.newPage();
        const resp = await page.goto(base + p, { waitUntil: "load", timeout: 30000 });
        await page.waitForTimeout(400);
        const m = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
        const ok = resp.status() === 200 && m.sw <= m.cw + 1;
        if (!ok) fail++;
        console.log(`${ok ? "PASS" : "FAIL"} ${p} status=${resp.status()} scrollWidth=${m.sw} clientWidth=${m.cw}`);
        await page.close();
    }
    await browser.close();
    server.close();
    console.log(`mobile-390: ${PAGES.length - fail}/${PAGES.length} pages without horizontal scroll`);
    process.exit(fail ? 1 : 0);
});
