import type { Offer } from "./types";
import { parseDuration } from "./format";

/** Subset of Duffel's offer payload that we read. */
export interface DuffelOffer {
  id: string;
  total_amount: string;
  total_currency: string;
  base_amount: string;
  tax_amount: string | null;
  owner: { name: string; iata_code: string | null; logo_symbol_url: string | null };
  slices: Array<{
    duration: string | null;
    origin: { iata_code: string };
    destination: { iata_code: string };
    segments: Array<{
      departing_at: string;
      arriving_at: string;
      passengers?: Array<{ baggages?: Array<{ type: string; quantity: number }> }>;
    }>;
  }>;
}

/** Convert a Duffel offer to our flat Offer. Returns null for malformed offers. */
export function normalizeOffer(o: DuffelOffer): Offer | null {
  const slice = o.slices?.[0];
  const segs = slice?.segments;
  if (!slice || !segs?.length) return null;
  const total = Number(o.total_amount);
  if (!Number.isFinite(total)) return null;
  const first = segs[0];
  const last = segs[segs.length - 1];
  const checked = segs.every((s) =>
    (s.passengers?.[0]?.baggages ?? []).some((b) => b.type === "checked" && b.quantity > 0),
  );
  return {
    id: o.id,
    date: first.departing_at.slice(0, 10),
    departAt: first.departing_at,
    arriveAt: last.arriving_at,
    origin: slice.origin.iata_code,
    destination: slice.destination.iata_code,
    durationMin: slice.duration ? parseDuration(slice.duration) : 0,
    stops: segs.length - 1,
    airline: { name: o.owner.name, iata: o.owner.iata_code, logo: o.owner.logo_symbol_url },
    baggageIncluded: checked,
    total,
    base: Number(o.base_amount),
    tax: Number(o.tax_amount ?? 0),
    currency: o.total_currency,
  };
}
