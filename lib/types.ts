/** Shared types between the API routes and the UI. */

export interface Airline {
  name: string;
  iata: string | null;
  logo: string | null;
}

/** One flight option (outbound slice of a Duffel offer) in the shape the UI needs. */
export interface Offer {
  id: string;
  /** Departure date YYYY-MM-DD (from the first segment). */
  date: string;
  /** Local departure/arrival timestamps as returned by Duffel, e.g. 2026-12-04T09:15:00. */
  departAt: string;
  arriveAt: string;
  origin: string;
  destination: string;
  durationMin: number;
  /** 0 = direct. */
  stops: number;
  airline: Airline;
  /** True when every segment includes at least one checked bag. */
  baggageIncluded: boolean;
  /** Final price per adult (base + taxes), as returned by Duffel. */
  total: number;
  base: number;
  tax: number;
  /** ISO 4217 currency, e.g. "USD". */
  currency: string;
}

/** Cheapest option for one date, used by the calendar. */
export interface DayFare {
  date: string;
  total: number;
  base: number;
  tax: number;
  currency: string;
  airline: Airline;
  stops: number;
}

export interface DayFareResponse {
  fare: DayFare | null;
}

export interface SearchResponse {
  offers: Offer[];
}

export interface ApiError {
  error: string;
}
