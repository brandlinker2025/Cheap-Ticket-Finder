# Cheap Ticket Finder — security audit (23 Oct 2026, Asia/Dhaka)
Branch `sec-hardening` from production `33766db`. Preview: dpl_3Cu8Gvn2T6YrFRZSrfFAFJwuXaWr (not production).

| # | Area | Finding | Severity | Action |
|---|------|---------|----------|--------|
| 1 | HTTPS redirect | http://apex and http://www → 308 to https | OK | none |
| 2 | www TLS | https://www.cheapticketfinder.site: TLS cert does not cover `www` (curl: "no alternative certificate subject name matches") → browsers show cert error | Medium | Needs RS approval: add www as domain/redirect in Vercel project |
| 3 | HSTS | Prod: `max-age=63072000; includeSubDomains; preload` (preload is hard to undo; www has no valid cert) | Low | Fixed in preview: `max-age=31536000; includeSubDomains` |
| 4 | CSP | Already enforced on prod; script-src allows 'unsafe-inline' 'unsafe-eval' (needed by inline code/widget); img/connect/frame-src allow any https | Low | Kept enforced (passes all tests). Tightening needs nonce refactor — later |
| 5 | Framing | frame-ancestors 'self' + X-Frame-Options SAMEORIGIN | OK | none |
| 6 | nosniff / Referrer-Policy / Permissions-Policy | Present (camera, mic, geolocation, payment, usb… disabled) | OK | none |
| 7 | Secrets | gitleaks over 156 commits: no leaks. rg on tree/built JS: no keys. No env vars used (static site). Workflows use `secrets.NETLIFY_AUTH_TOKEN` / `github.token` by reference only | OK | none to rotate |
| 8 | XSS | flightSearch is only written (URLSearchParams) and consumed by the Travelpayouts widget; dynamic text through escapeHtml; remote airport codes validated `^[a-z0-9]{3}$`; href values come from static code data | Low | none needed |
| 9 | Third-party data | Airport DB fetched from raw.githubusercontent / jsDelivr `@master` (unpinned) | Low | Suggest pinning a commit later |
| 10 | Contact form | formsubmit.co, honeypot present, `_captcha:false`; inbox address assembled in JS | Low | Optional: enable captcha (needs RS ok — UX change) |
| 11 | API / serverless | None (no /api, static only) → no rate limiting needed | OK | none |
| 12 | Dependencies | npm audit: 7 (5 high, 2 moderate) all in dev-only tailwindcss 3.4.17 CLI chain (braces, micromatch, chokidar, fast-glob, postcss-*). Not shipped to browsers. Only fix = tailwind v4 (breaking) | Low | Not changed; v4 migration needs approval |
| 13 | Admin pages | None found; /admin 404, /.env 404, /.git 404 (/wp-admin 403 from Vercel) | OK | none |
| 14 | Exposed build files | tailwind.config.js served publicly (200) | Info | Fixed: added to .vercelignore (preview 404) |

Preview-only CSP note: Vercel injects vercel.live toolbar on preview URLs; CSP blocks it (expected, not present on production).
