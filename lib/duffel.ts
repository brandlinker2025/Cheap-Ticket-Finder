import "server-only";
import type { DayFare, Offer } from "./types";
import { normalizeOffer, type DuffelOffer } from "./normalize";

/**
 * Duffel has no "price calendar" endpoint, so every date is one search:
 * POST /air/offer_requests?return_offers=true (one-way, 1 adult, economy).
 * Results are cached, so the calendar and the result list share the same search.
 */

// DUFFEL_API_URL lets you point at a mock server in tests; leave unset in production.
const DUFFEL_URL = `${process.env.DUFFEL_API_URL ?? "https://api.duffel.com"}/air/offer_requests?return_offers=true&supplier_timeout=12000`;

export class DuffelError extends Error {
  constructor(message: string, public status: number, public retryAfter?: number) {
    super(message);
  }
}

// --- in-memory cache (per server instance) + in-flight de-duplication --------------------
const TTL_MS = 30 * 60 * 1000;
const MAX_ENTRIES = 300;
const cache = new Map<string, { at: number; offers: Offer[] }>();
const inflight = new Map<string, Promise<Offer[]>>();

export interface SearchParams {
  origin: string;
  destination: string;
  date: string;
}

/** All offers for one route and date, cheapest first. */
export async function searchOffers(p: SearchParams): Promise<Offer[]> {
  const key = `${p.origin}-${p.destination}-${p.date}`;
  const hit = cache.get(key);
  if (hit && Date.now() - hit.at < TTL_MS) return hit.offers;
  const running = inflight.get(key);
  if (running) return running;

  const job = fetchOffers(p)
    .then((offers) => {
      if (cache.size >= MAX_ENTRIES) cache.delete(cache.keys().next().value as string); // drop oldest
      cache.set(key, { at: Date.now(), offers });
      return offers;
    })
    .finally(() => inflight.delete(key));
  inflight.set(key, job);
  return job;
}

/** Cheapest option for a date (optionally direct only), for the calendar. */
export async function cheapestForDay(p: SearchParams, directOnly: boolean): Promise<DayFare | null> {
  const offers = await searchOffers(p);
  const best = (directOnly ? offers.filter((o) => o.stops === 0) : offers)[0];
  if (!best) return null;
  const { date, total, base, tax, currency, airline, stops } = best;
  return { date, total, base, tax, currency, airline, stops };
}

async function fetchOffers(p: SearchParams): Promise<Offer[]> {
  const token = process.env.DUFFEL_ACCESS_TOKEN;
  if (!token) throw new DuffelError("Fare search is not configured.", 503);

  let res: Response;
  try {
    res = await fetch(DUFFEL_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Duffel-Version": "v2",
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        data: {
          slices: [{ origin: p.origin, destination: p.destination, departure_date: p.date }],
          passengers: [{ type: "adult" }],
          cabin_class: "economy",
        },
      }),
      signal: AbortSignal.timeout(25_000),
      cache: "no-store",
    });
  } catch {
    throw new DuffelError("The fare provider timed out. Please try again.", 504);
  }

  if (res.status === 429) {
    throw new DuffelError("Too many searches right now. Please wait a moment.", 429, Number(res.headers.get("retry-after")) || 10);
  }
  if (!res.ok) {
    console.error("duffel error", res.status, await res.text().catch(() => "")); // server log only
    throw new DuffelError("The fare provider is unavailable. Please try again.", 502);
  }

  const json = (await res.json()) as { data?: { offers?: DuffelOffer[] } };
  return (json.data?.offers ?? [])
    .map(normalizeOffer)
    .filter((o): o is Offer => o !== null)
    .sort((a, b) => a.total - b.total);
}
