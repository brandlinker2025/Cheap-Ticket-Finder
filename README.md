# Cheap Ticket Finder

Static Bangladesh-friendly search page for **cheapticketfinder.site**. It does **not** sell tickets and it does **not** invent ৳ fares.

## What it does

Pick From / To, then dates on **one empty calendar** (nothing is pre-selected). Cheap Ticket Finder then shows **one cheap ticket path**:

- **Primary:** Open Google Flights (`tfs` search). Book with the airline there — that is the real, authentic airline-issued ticket (e.g. a US-Bangla ৳ on Google Flights). City metros are encoded together in that tfs link (DAC → London is LHR + LGW + STN + LTN, not LHR only; same for NYC, BKK+DMK, IST+SAW, DXB+DWC, Paris CDG+ORY, Tokyo NRT+HND). A **Cheaper Nearby Airport** list (code + city + ~km, about 50–150 km) opens a dated tfs search for that one dest. We do not invent ৳.
- **Secondary:** official airline engines for **this From–To only** (they often show a higher fare family such as Flex). US-Bangla TTI appears when that airline is on the route. AIR ASTRA / Novoair only on Bangladesh domestic routes. A published checkout code sits beside that airline (AIRASTRA15 on AIR ASTRA).
- **Official packages:** only if the searched destination country has a real official holiday URL. Thailand (and any country without a URL we publish) omits the packages block. No always-on four-package grid.

There is no public fare API without secrets, so this page does not print a made-up ৳. We show the official **up to X%** on the matching checkout. If a real fare is ever known, fare after that percent is labeled an estimate from official %.

There is **one place** for cards/codes: beside each airline/OTA search/book row. There is no separate BANK / CARD CAMPAIGNS grid. There is no always-on tools grid.

There is no public fare API without secrets, so this page does not print a made-up ৳. We show the official **up to X%** on the matching checkout. If a real fare is ever known, fare after that percent is labeled an estimate from official %.

There is **one place** for cards/codes: beside each airline/OTA search/book row. There is no separate BANK / CARD CAMPAIGNS grid.

ShareTrip dated `/flight/search` is not linked (404). EBL Stellar codes use ShareTrip home only.

## What this is not

- No estimated fares
- No extra month calendar, nearby ±7 strip, or Google/Skyscanner/Kayak triplet
- No card-discount or promo-voucher math
- No airline scraping

## Live

- Production: https://cheap-ticket-finder.vercel.app
- Custom domain: https://cheapticketfinder.site (attach this Vercel project)

## Tech

Static `index.html` on Vercel. Dated URLs are built in `js/booking-links.js`.

## Google Search Console — one owner sign-in step left (prepared 19 Oct 2026, Asia/Dhaka)

SEO files are live-ready in this repo: `/robots.txt`, `/sitemap.xml`, canonical/OG tags and route-guide pages. Search Console itself is **not verified yet** — only RS Lina can do the final sign-in.

1. Go to https://search.google.com/search-console and sign in with her own Google account.
2. Add property → **URL prefix** → `https://cheapticketfinder.site/` (or Domain property for `cheapticketfinder.site` if she prefers; URL-prefix is simplest).
3. Verification options Google will offer:
   - **HTML meta tag (recommended, easiest with this repo):** copy only the `content="..."` value Google gives her and send it to the agent — one `<meta name="google-site-verification" ...>` line will be added to `index.html` head, deployed, then she clicks **Verify**.
   - **HTML file:** Google gives a file like `googleXXXXXXXXXXXX.html` — send that exact filename/content to the agent; it will be placed in the repo root, deployed, then she clicks **Verify**. Do not invent this file — its name/content come only from her Search Console account.
   - DNS TXT record is an alternative if she manages DNS.
4. After verification: Search Console → Sitemaps → submit `sitemap.xml`.
5. Use **URL Inspection → Request indexing** for `/` and the six route-guide pages. This asks Google to crawl; it does not guarantee ranking or timing.

No ranking is promised: indexing can take days–weeks and positions depend on Google, competition and fresh, honest content.
