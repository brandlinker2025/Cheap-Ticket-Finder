"use client";

import { useState } from "react";
import styles from "./FlightSearch.module.css";
import type { Offer } from "@/lib/types";
import { formatDuration, money, timeOf } from "@/lib/format";
import { formatDate } from "@/lib/dates";

/** One flight option: price first, then times, duration, stops, airline. */
export default function ResultCard({ offer, serviceFee }: { offer: Offer; serviceFee: number }) {
  const [open, setOpen] = useState(false);
  const total = offer.total + serviceFee;
  const stops = offer.stops === 0 ? "Direct" : `${offer.stops} stop${offer.stops > 1 ? "s" : ""}`;

  return (
    <article className={styles.card}>
      <div className={styles.main}>
        <div className={styles.airline}>
          {offer.airline.logo ? /* eslint-disable-next-line @next/next/no-img-element */ <img src={offer.airline.logo} alt="" width={36} height={36} /> : <span className={styles.logoFallback}>{offer.airline.iata ?? "✈"}</span>}
          <span>{offer.airline.name}</span>
        </div>

        <div className={styles.times}>
          <div><strong>{timeOf(offer.departAt)}</strong><small>{offer.origin}</small></div>
          <div className={styles.mid}>
            <small>{formatDuration(offer.durationMin)}</small>
            <hr />
            <small className={offer.stops === 0 ? styles.direct : ""}>{stops}</small>
          </div>
          <div><strong>{timeOf(offer.arriveAt)}</strong><small>{offer.destination}</small></div>
        </div>

        <div className={styles.priceBox}>
          <div className={styles.price}>{money(total, offer.currency)}</div>
          <small>Total, taxes included</small>
          <button type="button" className={styles.link} onClick={() => setOpen(!open)} aria-expanded={open}>
            {open ? "Hide price details" : "Price details"}
          </button>
        </div>
      </div>

      <div className={styles.tags}>
        <span>{formatDate(offer.date)}</span>
        <span className={offer.baggageIncluded ? styles.ok : styles.warn}>{offer.baggageIncluded ? "Checked bag included" : "No checked bag"}</span>
      </div>

      {open && (
        <dl className={styles.breakdown}>
          <div><dt>Base fare</dt><dd>{money(offer.base, offer.currency)}</dd></div>
          <div><dt>Taxes &amp; carrier charges</dt><dd>{money(offer.tax, offer.currency)}</dd></div>
          <div><dt>Service fee</dt><dd>{money(serviceFee, offer.currency)}</dd></div>
          <div className={styles.totalRow}><dt>Total</dt><dd>{money(total, offer.currency)}</dd></div>
        </dl>
      )}
    </article>
  );
}
