import { NextResponse } from "next/server";
import { DuffelError } from "./duffel";
import { isIsoDate, todayIso } from "./dates";
import type { ApiError } from "./types";

const IATA = /^[A-Z]{3}$/;

export interface Query {
  origin: string;
  destination: string;
  date: string;
}

/** Validate ?origin&destination&date. Returns null when invalid. */
export function parseQuery(q: URLSearchParams): Query | null {
  const origin = (q.get("origin") ?? "").toUpperCase();
  const destination = (q.get("destination") ?? "").toUpperCase();
  const date = q.get("date") ?? "";
  if (!IATA.test(origin) || !IATA.test(destination) || origin === destination || !isIsoDate(date) || date < todayIso()) return null;
  return { origin, destination, date };
}

export const badRequest = (): NextResponse<ApiError> => NextResponse.json({ error: "Invalid route or date." }, { status: 400 });

export function toErrorResponse(e: unknown): NextResponse<ApiError> {
  if (e instanceof DuffelError) {
    const headers: Record<string, string> = e.retryAfter ? { "Retry-After": String(e.retryAfter) } : {};
    return NextResponse.json({ error: e.message }, { status: e.status, headers });
  }
  console.error("api failed", e);
  return NextResponse.json({ error: "Something went wrong." }, { status: 500 });
}

/** CDN caches identical queries, which protects your Duffel search quota. */
export const CACHE_HEADERS = { "Cache-Control": "public, s-maxage=1800, stale-while-revalidate=3600" };
