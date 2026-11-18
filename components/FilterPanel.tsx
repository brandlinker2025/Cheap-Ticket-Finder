"use client";

import styles from "./FlightSearch.module.css";
import { Filters, TIME_LABELS, TimeBucket } from "@/lib/filters";

interface Props {
  filters: Filters;
  airlines: string[];
  onChange: (f: Filters) => void;
}

const toggle = <T,>(list: T[], v: T): T[] => (list.includes(v) ? list.filter((x) => x !== v) : [...list, v]);

export default function FilterPanel({ filters, airlines, onChange }: Props) {
  const set = (patch: Partial<Filters>) => onChange({ ...filters, ...patch });
  return (
    <aside className={styles.filters} aria-label="Filters">
      <h3>Filters</h3>

      <label className={styles.check}>
        <input type="checkbox" checked={filters.directOnly} onChange={(e) => set({ directOnly: e.target.checked })} /> Direct flights only
      </label>

      <fieldset disabled={filters.directOnly}>
        <legend>Stops</legend>
        {([[null, "Any"], [1, "Up to 1 stop"], [0, "Direct"]] as const).map(([v, label]) => (
          <label key={label} className={styles.check}>
            <input type="radio" name="stops" checked={filters.maxStops === v} onChange={() => set({ maxStops: v })} /> {label}
          </label>
        ))}
      </fieldset>

      <label className={styles.check}>
        <input type="checkbox" checked={filters.baggageOnly} onChange={(e) => set({ baggageOnly: e.target.checked })} /> Checked baggage included
      </label>

      <fieldset>
        <legend>Departure time</legend>
        {(Object.keys(TIME_LABELS) as TimeBucket[]).map((t) => (
          <label key={t} className={styles.check}>
            <input type="checkbox" checked={filters.times.includes(t)} onChange={() => set({ times: toggle(filters.times, t) })} /> {TIME_LABELS[t]}
          </label>
        ))}
      </fieldset>

      <fieldset>
        <legend>Airlines</legend>
        {airlines.length === 0 && <small>Appear after a search.</small>}
        {airlines.map((a) => (
          <label key={a} className={styles.check}>
            <input type="checkbox" checked={filters.airlines.includes(a)} onChange={() => set({ airlines: toggle(filters.airlines, a) })} /> {a}
          </label>
        ))}
      </fieldset>
    </aside>
  );
}
