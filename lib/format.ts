/** ISO-8601 duration ("PT7H30M", "P1DT2H") to minutes. */
export function parseDuration(iso: string): number {
  const m = /^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?$/.exec(iso);
  if (!m) return 0;
  return Number(m[1] ?? 0) * 1440 + Number(m[2] ?? 0) * 60 + Number(m[3] ?? 0);
}

export const formatDuration = (min: number): string => `${Math.floor(min / 60)}h ${String(min % 60).padStart(2, "0")}m`;

export const timeOf = (iso: string): string => iso.slice(11, 16);

export const money = (v: number, currency: string): string =>
  new Intl.NumberFormat("en-US", { style: "currency", currency, maximumFractionDigits: 2 }).format(v);
