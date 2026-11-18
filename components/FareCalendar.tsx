"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import styles from "./FareCalendar.module.css";
import type { ApiError, DayFare, DayFareResponse } from "@/lib/types";
import { daysInMonth, firstWeekday, formatDate, monthDates, shiftMonth, todayIso } from "@/lib/dates";
import { CONCURRENCY } from "@/lib/config";
import { runPool } from "@/lib/pool";
import { money } from "@/lib/format";

const MONTHS_AHEAD = 11;

type Cell =
  | { status: "loading" }
  | { status: "none" } // searched, no offers
  | { status: "error"; message: string }
  | { status: "ok"; fare: DayFare };

interface Props {
  origin: string;
  destination: string;
  /** Extra amount your own business adds on top of Duffel's total (default none). */
  serviceFee?: number;
  /** Called when the user presses "Search this day" in the summary. */
  onUseDate?: (date: string) => void;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export default function FareCalendar({ origin, destination, serviceFee = 0, onUseDate }: Props) {
  const today = useMemo(() => todayIso(), []);
  const minMonth = today.slice(0, 7);
  const maxMonth = shiftMonth(minMonth, MONTHS_AHEAD);

  const [month, setMonth] = useState(minMonth);
  const [directOnly, setDirectOnly] = useState(false);
  const [cells, setCells] = useState<Record<string, Cell>>({});
  const [running, setRunning] = useState(false);
  const [first, setFirst] = useState<string | null>(null);
  const [last, setLast] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const dates = useMemo(() => monthDates(month).filter((d) => d >= today), [month, today]);

  // Changing route, month or filter invalidates results and cancels in-flight searches.
  useEffect(() => {
    abortRef.current?.abort();
    setCells({});
    setFirst(null);
    setLast(null);
    setRunning(false);
  }, [origin, destination, month, directOnly]);
  useEffect(() => () => abortRef.current?.abort(), []);

  const fetchDay = useCallback(
    async (date: string, signal: AbortSignal): Promise<Cell> => {
      const qs = new URLSearchParams({ origin, destination, date });
      if (directOnly) qs.set("directOnly", "1");
      for (let attempt = 0; attempt < 2; attempt++) {
        const res = await fetch(`/api/fare/day?${qs}`, { signal });
        if (res.status === 429 && attempt === 0) {
          await sleep((Number(res.headers.get("retry-after")) || 5) * 1000);
          continue;
        }
        const body = (await res.json().catch(() => ({}))) as DayFareResponse & ApiError;
        if (!res.ok) return { status: "error", message: body.error ?? "Could not load this day." };
        return body.fare ? { status: "ok", fare: body.fare } : { status: "none" };
      }
      return { status: "error", message: "Too many searches. Try again shortly." };
    },
    [origin, destination, directOnly],
  );

  /** Loads every day that has no result yet, a few at a time, filling the grid as results arrive. */
  const loadMonth = useCallback(async () => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    const todo = dates.filter((d) => cells[d]?.status !== "ok" && cells[d]?.status !== "none");
    if (!todo.length) return;
    setRunning(true);
    setCells((prev) => ({ ...prev, ...Object.fromEntries(todo.map((d) => [d, { status: "loading" } as Cell])) }));

    await runPool(todo, CONCURRENCY, async (d) => {
      let cell: Cell;
      try {
        cell = await fetchDay(d, ctrl.signal);
      } catch {
        if (ctrl.signal.aborted) return;
        cell = { status: "error", message: "Network problem. Please retry." };
      }
      if (!ctrl.signal.aborted) setCells((prev) => ({ ...prev, [d]: cell }));
    }, ctrl.signal);
    if (!ctrl.signal.aborted) setRunning(false);
  }, [dates, cells, fetchDay]);

  // ---- derived data -----------------------------------------------------------------
  const okFares = useMemo(
    () => dates.flatMap((d) => (cells[d]?.status === "ok" ? [(cells[d] as { fare: DayFare }).fare] : [])),
    [dates, cells],
  );
  const loadedCount = dates.filter((d) => cells[d] && cells[d].status !== "loading").length;
  const errorCount = dates.filter((d) => cells[d]?.status === "error").length;
  const range = first ? (last && last < first ? [last, first] : [first, last ?? first]) : null;

  const inScope = useMemo(
    () => (range ? okFares.filter((f) => f.date >= range[0] && f.date <= range[1]) : okFares),
    [okFares, range],
  );
  const ranked = useMemo(() => [...inScope].sort((a, b) => a.total - b.total || (a.date < b.date ? -1 : 1)), [inScope]);
  const best = ranked[0];

  const tier = useMemo(() => {
    const s = okFares.map((f) => f.total).sort((a, b) => a - b);
    const lo = s[Math.floor(s.length / 3)];
    const hi = s[Math.floor((s.length * 2) / 3)];
    return (v: number) => (v <= lo ? styles.low : v <= hi ? styles.mid : styles.high);
  }, [okFares]);

  const pick = (d: string) => {
    if (!first || last) {
      setFirst(d);
      setLast(null);
    } else setLast(d);
  };

  // ---- render -----------------------------------------------------------------------
  const blanks = firstWeekday(month);
  const total = daysInMonth(month);

  return (
    <section className={styles.wrap} aria-label={`Low fare calendar ${origin} to ${destination}`}>
      <div className={styles.bar}>
        <button type="button" onClick={() => setMonth(shiftMonth(month, -1))} disabled={month <= minMonth} aria-label="Previous month">
          ‹ Prev
        </button>
        <strong>{new Date(`${month}-01T00:00:00Z`).toLocaleDateString("en-GB", { month: "long", year: "numeric", timeZone: "UTC" })}</strong>
        <button type="button" onClick={() => setMonth(shiftMonth(month, 1))} disabled={month >= maxMonth} aria-label="Next month">
          Next ›
        </button>
      </div>

      <div className={styles.controls}>
        <label className={styles.check}>
          <input type="checkbox" checked={directOnly} onChange={(e) => setDirectOnly(e.target.checked)} /> Direct flights only
        </label>
        <button type="button" className={styles.primary} onClick={loadMonth} disabled={running || !dates.length}>
          {running ? `Loading… ${loadedCount}/${dates.length}` : errorCount ? `Retry ${errorCount} failed day(s)` : loadedCount ? "Reload missing days" : `Load prices (${dates.length} searches)`}
        </button>
      </div>

      <p className={styles.muted} role="status" aria-live="polite">
        {!loadedCount && !running && "Prices load only when you press the button, so searches are never wasted."}
        {loadedCount > 0 && !running && okFares.length === 0 && "No flights found for this route in this month. Try another month, or untick “Direct flights only”."}
        {okFares.length > 0 && "Prices are the final total per adult (base fare + taxes), one-way, economy."}
      </p>

      <div className={styles.grid}>
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
          <div key={d} className={styles.dow}>{d}</div>
        ))}
        {Array.from({ length: blanks }, (_, i) => <div key={`b${i}`} />)}
        {Array.from({ length: total }, (_, i) => {
          const day = i + 1;
          const iso = `${month}-${String(day).padStart(2, "0")}`;
          const cell = cells[iso];
          const past = iso < today;
          const isBest = best && !range && cell?.status === "ok" && cell.fare.date === best.date;
          const selected = range && (iso === range[0] || iso === range[1]);
          const between = range && range[0] !== range[1] && iso >= range[0] && iso <= range[1];
          const cls = [
            styles.cell,
            cell?.status === "ok" ? tier(cell.fare.total) : "",
            cell?.status === "loading" ? styles.loading : "",
            cell?.status === "error" ? styles.err : "",
            isBest ? styles.best : "",
            selected ? styles.sel : "",
            between ? styles.between : "",
          ].join(" ");
          return (
            <button
              key={iso}
              type="button"
              className={cls}
              disabled={past || cell?.status !== "ok"}
              onClick={() => pick(iso)}
              title={cell?.status === "error" ? cell.message : undefined}
              aria-label={`${formatDate(iso)}: ${cell?.status === "ok" ? money(cell.fare.total + serviceFee, cell.fare.currency) : cell?.status ?? "not loaded"}`}
            >
              <span className={styles.d}>{day}</span>
              <span className={styles.p}>
                {cell?.status === "ok" ? money(cell.fare.total + serviceFee, cell.fare.currency) : cell?.status === "error" ? "!" : cell?.status === "none" ? "–" : ""}
              </span>
            </button>
          );
        })}
      </div>

      {best && (
        <div className={styles.summary}>
          <h3>{range && range[0] !== range[1] ? `Cheapest between ${formatDate(range[0])} and ${formatDate(range[1])}` : range ? "Selected day" : "Cheapest day this month"}</h3>
          <div className={styles.best3}>
            {best.airline.logo && /* eslint-disable-next-line @next/next/no-img-element */ <img src={best.airline.logo} alt="" width={32} height={32} />}
            <div>
              <strong>{formatDate(best.date)}</strong> · {best.airline.name} · {best.stops === 0 ? "Direct" : `${best.stops} stop${best.stops > 1 ? "s" : ""}`}
            </div>
          </div>
          <dl className={styles.breakdown}>
            <div><dt>Base fare</dt><dd>{money(best.base, best.currency)}</dd></div>
            <div><dt>Taxes & carrier charges</dt><dd>{money(best.tax, best.currency)}</dd></div>
            <div><dt>Service fee</dt><dd>{money(serviceFee, best.currency)}</dd></div>
            <div className={styles.totalRow}><dt>Total</dt><dd>{money(best.total + serviceFee, best.currency)}</dd></div>
          </dl>
          {onUseDate && <button type="button" className={styles.primary} onClick={() => onUseDate(best.date)}>Search flights for {formatDate(best.date)}</button>}
          {ranked.length > 1 && (
            <ol className={styles.top}>
              {ranked.slice(1, 5).map((f) => (
                <li key={f.date}>{formatDate(f.date)}: {money(f.total + serviceFee, f.currency)} · {f.airline.name}</li>
              ))}
            </ol>
          )}
        </div>
      )}
    </section>
  );
}
