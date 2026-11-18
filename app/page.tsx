"use client";

import { useState } from "react";
import FareCalendar from "@/components/FareCalendar";
import FlightSearch from "@/components/FlightSearch";
import { SERVICE_FEE } from "@/lib/config";
import { todayIso } from "@/lib/dates";

const ROUTES = [
  ["DAC", "DXB", "Dhaka → Dubai"],
  ["DAC", "DEL", "Dhaka → Delhi"],
  ["DAC", "BKK", "Dhaka → Bangkok"],
  ["DAC", "KUL", "Dhaka → Kuala Lumpur"],
  ["DAC", "SIN", "Dhaka → Singapore"],
  ["DAC", "LHR", "Dhaka → London"],
] as const;

export default function Page() {
  const [i, setI] = useState(0);
  const [date, setDate] = useState(() => todayIso());
  const [origin, destination] = ROUTES[i];
  return (
    <main>
      <h1>Cheap Ticket Finder</h1>
      <p style={{ color: "#486581" }}>Final price per adult: base fare + taxes, nothing hidden.</p>
      <label>
        Route{" "}
        <select value={i} onChange={(e) => setI(Number(e.target.value))}>
          {ROUTES.map((r, idx) => (
            <option key={r[2]} value={idx}>{r[2]}</option>
          ))}
        </select>
      </label>
      <FareCalendar origin={origin} destination={destination} serviceFee={SERVICE_FEE} onUseDate={setDate} />
      <FlightSearch origin={origin} destination={destination} date={date} onDateChange={setDate} />
    </main>
  );
}
