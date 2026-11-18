import { NextRequest, NextResponse } from "next/server";
import { searchOffers } from "@/lib/duffel";
import { badRequest, CACHE_HEADERS, parseQuery, toErrorResponse } from "@/lib/apiHelpers";
import type { ApiError, SearchResponse } from "@/lib/types";

export const runtime = "nodejs";
export const maxDuration = 30;

const MAX_OFFERS = 40;

/** GET /api/search?origin=DAC&destination=DXB&date=2026-12-04 : cheapest offers for one date. */
export async function GET(req: NextRequest): Promise<NextResponse<SearchResponse | ApiError>> {
  const query = parseQuery(req.nextUrl.searchParams);
  if (!query) return badRequest();
  try {
    const offers = await searchOffers(query);
    return NextResponse.json({ offers: offers.slice(0, MAX_OFFERS) }, { headers: CACHE_HEADERS });
  } catch (e) {
    return toErrorResponse(e);
  }
}
