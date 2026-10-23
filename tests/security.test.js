const assert = require("assert");
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");
const cfg = JSON.parse(fs.readFileSync(path.join(root, "vercel.json"), "utf8"));
const block = (cfg.headers || []).find((h) => h.source === "/(.*)");
assert.ok(block, "vercel.json must set global headers");
const map = Object.fromEntries(block.headers.map((h) => [h.key.toLowerCase(), h.value]));
const must = {
  "strict-transport-security": "max-age=31536000; includeSubDomains",
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
  "x-frame-options": "SAMEORIGIN",
};
for (const [k, v] of Object.entries(must)) assert.strictEqual(map[k], v, `${k} must be ${v}`);
assert.ok(map["permissions-policy"].includes("camera=()") && map["permissions-policy"].includes("microphone=()") && map["permissions-policy"].includes("geolocation=()"), "Permissions-Policy must disable camera/mic/geo");
const csp = map["content-security-policy"] || "";
for (const needle of ["default-src 'self'", "object-src 'none'", "frame-ancestors 'self'", "base-uri 'self'", "https://tp-em.com", "https://*.tp.media", "https://cdnjs.cloudflare.com", "https://formsubmit.co", "upgrade-insecure-requests"]) {
  assert.ok(csp.includes(needle), `CSP missing: ${needle}`);
}
assert.ok(!csp.includes("http://"), "CSP must not allow plain-http sources");
// Money/tracking assets must survive hardening.
const home = fs.readFileSync(path.join(root, "index.html"), "utf8");
assert.ok(home.includes("https://tp-em.com/NTg3NDQ3.js?t=587447"), "Drive script must stay");
for (const c of ["campaign_id=100", "campaign_id=137", "campaign_id=633", "campaign_id=541", "campaign_id=1&marker=791994", "marker=791994", "trs=587447"]) assert.ok(home.includes(c), `affiliate missing ${c}`);
assert.ok(fs.existsSync(path.join(root, "google8930e47481034007.html")), "Search Console file must stay");
// No committed secrets (patterns only, never values).
const bad = /(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)/;
(function walk(d) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { if (e.name === ".git") continue; const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else if (/\.(html|js|json|md|txt|yml|toml|py)$/.test(e.name)) assert.ok(!bad.test(fs.readFileSync(p, "utf8")), `secret-like token in ${p}`); } })(root);
const contact = fs.readFileSync(path.join(root, "contact/index.html"), "utf8");
assert.ok(contact.includes('name="_honey"'), "contact form must keep honeypot");
assert.ok(contact.includes("formLoadedAt"), "contact form must keep timing trap");
assert.ok(contact.includes('maxlength="3000"'), "contact message must be length-limited");
assert.ok(!contact.includes("mailto:jara"), "contact page must not expose a mailto address");
assert.ok(contact.includes("https://formsubmit.co/ajax/"), "contact form must keep FormSubmit delivery");
console.log("security.test.js OK (headers + CSP allowances + Drive/affiliates + no secret patterns)");
