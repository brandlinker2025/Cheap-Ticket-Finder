# Cheap Ticket Finder: Duffel Low Fare Calendar (Next.js + TypeScript)

## Run
1. `cp .env.example .env.local` and set `DUFFEL_ACCESS_TOKEN` (use a `duffel_test_...` token first).
2. `npm install && npm run dev`, open http://localhost:3000.
3. Deploy: import the repo in Vercel, add `DUFFEL_ACCESS_TOKEN` under Settings → Environment Variables.

## How the calendar works
Duffel has no price-calendar endpoint. Each day is one search:
`POST https://api.duffel.com/air/offer_requests?return_offers=true` (header `Duffel-Version: v2`).
- `GET /api/fare/day` searches one date and returns the cheapest offer (base, tax, total, airline, stops).
- The browser loads a month with 4 parallel requests, so the grid fills in progressively and no
  serverless call can time out. Results are cached 30 min in memory and at the Vercel CDN.
- Searches start only when the user presses "Load prices" (about 30 searches per month view).
  Check Duffel's pricing/search-to-book policy before enabling this publicly, because many searches with
  few bookings can be charged.

## Features
1. Low Fare Calendar: `components/FareCalendar.tsx` (progressive month grid, range select, direct-only).
2. True total price: every card and the calendar summary show Base fare + Taxes & carrier charges + Service fee = Total. Set your own fee in `lib/config.ts` (`SERVICE_FEE`, default 0).
3. Flexible dates (±3 days) and nearby airports: `components/FlightSearch.tsx`, airport groups in `lib/airports.ts`. One click is capped at 40 searches (`MAX_SEARCHES`).
4. Filters: direct only, stops, airlines, checked baggage, departure time (`lib/filters.ts`, `components/FilterPanel.tsx`).
5. Result cards + sorting (price, duration, departure): `components/ResultCard.tsx`.

## API
- `GET /api/search?origin&destination&date` cheapest 40 offers for one date.
- `GET /api/fare/day?origin&destination&date[&directOnly=1]` cheapest fare for the calendar.
Both share one cached Duffel search per route and date.

## Notes
- Not booking yet: cards show prices only. Booking needs Duffel orders + payment, which is a separate step.
- `DUFFEL_API_URL` (optional) points the server at a mock Duffel for tests.
