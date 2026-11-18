"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import styles from "./FlightSearch.module.css";
import FilterPanel from "./FilterPanel";
import ResultCard from "./ResultCard";
import type { ApiError, Offer, SearchResponse } from "@/lib/types";
import { applyFilters, DEFAULT_FILTERS, Filters, sortOffers, SortKey } from "@/lib/filters";
import { withNearby } from "@/lib/airports";
import { CONCURRENCY, MAX_SEARCHES, SERVICE_FEE } from "@/lib/config";
import { runPool } from "@/lib/pool";
import { formatDate, todayIso } from "@/lib/dates";

interface Job { origin: string; destination: string; date: string }

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** Dates within ±days of `date` that are not in the past. */
function datesAround(date: string, days: number, today: string): string[] {
  const base = new Date(`${date}T00:00:00Z`).getTime();
  return Array.from({ length: days * 2 + 1 }, (_, i) => new Date(base + (i - days) * 86_400_000).toISOString().slice(0, 10)).filter((d) => d >= today);
}

interface Props {
  origin: string;
  destination: string;
  /** Date coming from the calendar ("Search this day"). */
  date: string;
  onDateChange: (d: string) => void;
}

export default function FlightSearch({ origin, destination, date, onDateChange }: Props) {
  const today = useMemo(() => todayIso(), []);
  const [flexible, setFlexible] = useState(false);
  const [nearby, setNearby] = useState(false);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [sort, setSort] = useState<SortKey>("price");
  const [progress, setProgress] = useState({ done: 0, total: 0, failed: 0 });
  const [running, setRunning] = useState(false);
  const [searched, setSearched] = useState(false);
  const [note, setNote] = useState("");
  const abortRef = useRef<AbortController | null>(null);

  // A new route invalidates old results.
  useEffect(() => {
    abortRef.current?.abort();
    setOffers([]);
    setSearched(false);
    setRunning(false);
    setNote("");
  }, [origin, destination]);
  useEffect(() => () => abortRef.current?.abort(), []);

  const search = async () => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    let jobs: Job[] = [];
    for (const o of withNearby(origin, nearby))
      for (const d of withNearby(destination, nearby))
        for (const dt of flexible ? datesAround(date, 3, today) : date >= today ? [date] : [])
          if (o !== d) jobs.push({ origin: o, destination: d, date: dt });

    if (!jobs.length) {
      setNote("Pick a departure date that is today or later.");
      return;
    }
    const capped = jobs.length > MAX_SEARCHES;
    if (capped) jobs = jobs.slice(0, MAX_SEARCHES);
    setNote(capped ? `Showing the first ${MAX_SEARCHES} date and airport combinations. Turn off nearby airports or flexible dates to narrow it.` : "");

    setOffers([]);
    setSearched(true);
    setRunning(true);
    setProgress({ done: 0, total: jobs.length, failed: 0 });

    await runPool(jobs, CONCURRENCY, async (job) => {
      const qs = new URLSearchParams(job as unknown as Record<string, string>);
      let ok = false;
      let found: Offer[] = [];
      try {
        for (let attempt = 0; attempt < 2 && !ok; attempt++) {
          const res = await fetch(`/api/search?${qs}`, { signal: ctrl.signal });
          if (res.status === 429 && attempt === 0) {
            await sleep((Number(res.headers.get("retry-after")) || 5) * 1000);
            continue;
          }
          const body = (await res.json().catch(() => ({}))) as Partial<SearchResponse & ApiError>;
          if (res.ok && body.offers) { found = body.offers; ok = true; }
          else break;
        }
      } catch {
        if (ctrl.signal.aborted) return;
      }
      if (ctrl.signal.aborted) return;
      setOffers((prev) => { const seen = new Set(prev.map((o) => o.id)); return [...prev, ...found.filter((o) => !seen.has(o.id))]; });
      setProgress((p) => ({ ...p, done: p.done + 1, failed: p.failed + (ok ? 0 : 1) }));
    }, ctrl.signal);
    if (!ctrl.signal.aborted) setRunning(false);
  };

  const airlines = useMemo(() => [...new Set(offers.map((o) => o.airline.name))].sort(), [offers]);
  const shown = useMemo(() => sortOffers(applyFilters(offers, filters), sort), [offers, filters, sort]);

  return (
    <section className={styles.wrap} aria-label="Flight search">
      <div className={styles.form}>
        <label>Departure date
          <input type="date" min={today} value={date} onChange={(e) => onDateChange(e.target.value)} />
        </label>
        <label className={styles.check}><input type="checkbox" checked={flexible} onChange={(e) => setFlexible(e.target.checked)} /> Flexible dates (±3 days)</label>
        <label className={styles.check}><input type="checkbox" checked={nearby} onChange={(e) => setNearby(e.target.checked)} /> Include nearby airports</label>
        <button type="button" className={styles.primary} onClick={search} disabled={running || !date}>
          {running ? `Searching… ${progress.done}/${progress.total}` : "Search flights"}
        </button>
      </div>

      {note && <p className={styles.notice}>{note}</p>}
      {searched && progress.failed > 0 && !running && (
        <p className={`${styles.notice} ${styles.err}`}>{progress.failed} search(es) failed, so some options may be missing. Press “Search flights” to retry.</p>
      )}

      {searched && (
        <div className={styles.layout}>
          <FilterPanel filters={filters} airlines={airlines} onChange={setFilters} />
          <div>
            <div className={styles.sortBar}>
              <span role="status" aria-live="polite">
                {running && offers.length === 0 ? "Searching…" : `${shown.length} of ${offers.length} option(s)`}
                {flexible && ` · ${formatDate(date)} ±3 days`}
              </span>
              <label>Sort by{" "}
                <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)}>
                  <option value="price">Lowest price</option>
                  <option value="duration">Shortest duration</option>
                  <option value="departure">Earliest departure</option>
                </select>
              </label>
            </div>

            {running && offers.length === 0 && (
              <div aria-hidden>{[0, 1, 2].map((i) => <div key={i} className={`${styles.card} ${styles.skeleton}`} />)}</div>
            )}
            {!running && offers.length === 0 && progress.failed === 0 && <p className={styles.notice}>No flights found for these dates. Try different dates or turn on nearby airports.</p>}
            {!running && offers.length > 0 && shown.length === 0 && <p className={styles.notice}>No flights match your filters. Loosen a filter to see more.</p>}

            {shown.map((o) => <ResultCard key={o.id} offer={o} serviceFee={SERVICE_FEE} />)}
          </div>
        </div>
      )}
    </section>
  );
}
