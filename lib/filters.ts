import type { Offer } from "./types";

export type TimeBucket = "night" | "morning" | "afternoon" | "evening";
export type SortKey = "price" | "duration" | "departure";

export interface Filters {
  directOnly: boolean;
  /** null = any number of stops */
  maxStops: 0 | 1 | null;
  /** Selected airline names; empty = all airlines. */
  airlines: string[];
  baggageOnly: boolean;
  /** Selected departure windows; empty = any time. */
  times: TimeBucket[];
}

export const DEFAULT_FILTERS: Filters = { directOnly: false, maxStops: null, airlines: [], baggageOnly: false, times: [] };

export const TIME_LABELS: Record<TimeBucket, string> = {
  night: "Night (00:00 to 05:59)",
  morning: "Morning (06:00 to 11:59)",
  afternoon: "Afternoon (12:00 to 17:59)",
  evening: "Evening (18:00 to 23:59)",
};

export function bucketOf(departAt: string): TimeBucket {
  const h = Number(departAt.slice(11, 13));
  return h < 6 ? "night" : h < 12 ? "morning" : h < 18 ? "afternoon" : "evening";
}

export function applyFilters(offers: Offer[], f: Filters): Offer[] {
  return offers.filter((o) => {
    if (f.directOnly && o.stops !== 0) return false;
    if (f.maxStops !== null && o.stops > f.maxStops) return false;
    if (f.airlines.length && !f.airlines.includes(o.airline.name)) return false;
    if (f.baggageOnly && !o.baggageIncluded) return false;
    if (f.times.length && !f.times.includes(bucketOf(o.departAt))) return false;
    return true;
  });
}

export function sortOffers(offers: Offer[], key: SortKey): Offer[] {
  const by: Record<SortKey, (a: Offer, b: Offer) => number> = {
    price: (a, b) => a.total - b.total,
    duration: (a, b) => a.durationMin - b.durationMin || a.total - b.total,
    departure: (a, b) => (a.departAt < b.departAt ? -1 : a.departAt > b.departAt ? 1 : a.total - b.total),
  };
  return [...offers].sort(by[key]);
}
