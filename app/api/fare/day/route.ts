import { NextRequest, NextResponse } from "next/server";
import { cheapestForDay } from "@/lib/duffel";
import { badRequest, CACHE_HEADERS, parseQuery, toErrorResponse } from "@/lib/apiHelpers";
import type { ApiError, DayFareResponse } from "@/lib/types";

export const runtime = "nodejs";
export const maxDuration = 30;

/** GET /api/fare/day?origin=DAC&destination=DXB&date=2026-12-04[&directOnly=1] */
export async function GET(req: NextRequest): Promise<NextResponse<DayFareResponse | ApiError>> {
  const query = parseQuery(req.nextUrl.searchParams);
  if (!query) return badRequest();
  try {
    const fare = await cheapestForDay(query, req.nextUrl.searchParams.get("directOnly") === "1");
    return NextResponse.json({ fare }, { headers: CACHE_HEADERS });
  } catch (e) {
    return toErrorResponse(e);
  }
}
