"use strict";

const byId = id => document.getElementById(id);
const airports = ["DAC", "DEL", "SXR", "DEL", "DAC"];
const iso = date => date.toISOString().slice(0, 10);
const shift = (day, days) => {
    const date = new Date(day + "T00:00:00Z");
    date.setUTCDate(date.getUTCDate() + days);
    return iso(date);
};
const today = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Dhaka" }).format(new Date());
byId("departure").min = today;
byId("departure").value = today <= "2026-12-04" ? "2026-12-04" : shift(today, 7);

function liveLink(days) {
    const encoded = days.map((day, i) => airports[i] + day.slice(8) + day.slice(5, 7)).join("") + "1";
    const params = new URLSearchParams({
        flightSearch: encoded, origin_airports: "0,1,2,3", destination_airports: "0,1,2,3"
    });
    return "/?" + params + "#wl-flight-results";
}

byId("dates").addEventListener("submit", async event => {
    event.preventDefault();
    const button = event.currentTarget.querySelector("button");
    const departure = byId("departure").value;
    const range = byId("range").value;
    const nights = ["out", "stay", "back"].map(id => Number(byId(id).value));
    const offset = [0];
    for (const night of nights) offset.push(offset.at(-1) + night);
    const start = range === "month" ? departure.slice(0, 7) + "-01" : shift(departure, -Number(range));
    const dates = [];
    for (let i = 0; i < (range === "month" ? 31 : Number(range) * 2 + 1); i++) {
        const day = shift(start, i);
        if (day >= today && (range !== "month" || day.startsWith(departure.slice(0, 7)))) {
            dates.push(offset.map(days => shift(day, days)));
        }
    }
    button.disabled = true;
    byId("results").replaceChildren();
    byId("status").textContent = "তারিখ ও ভাড়ার তথ্য খোঁজা হচ্ছে…";
    const requests = new Map();
    const key = (index, day) => index + ":" + day.slice(0, 7);
    for (const days of dates) {
        days.forEach((day, index) => {
            const id = key(index, day);
            if (requests.has(id)) return;
            const params = new URLSearchParams({
                origin: airports[index], destination: airports[index + 1], month: day.slice(0, 7)
            });
            requests.set(id, fetch("/api/fare-calendar?" + params, { signal: AbortSignal.timeout(12000) })
                .then(async response => {
                    if (!response.ok) return null;
                    return (await response.json()).fares;
                }).catch(() => null));
        });
    }
    const fareMaps = new Map(await Promise.all([...requests].map(async ([id, promise]) => [id, await promise])));
    const sameDay = nights.includes(0);
    const options = dates.map(days => {
        const fares = days.map((day, index) => fareMaps.get(key(index, day))?.find(fare => fare.date === day));
        const total = !sameDay && fares.every(Boolean) ? fares.reduce((sum, fare) => sum + fare.price, 0) : Infinity;
        return { days, fares, total };
    }).sort((a, b) => a.total - b.total || a.days[0].localeCompare(b.days[0]));
    const covered = options.filter(option => Number.isFinite(option.total)).length;
    byId("status").textContent = sameDay
        ? "একই দিনের কানেকশনের জন্য লাইভ সার্চে সময় মিলিয়ে দেখুন।"
        : covered
            ? options.length + " তারিখের মধ্যে " + covered + " তারিখে চার অংশের ক্যাশড ভাড়া মিলেছে। মোট USD আনুমানিক, একজন যাত্রীর আলাদা টিকিট। ব্যাগেজ ও কানেকশন চেক করুন।"
            : "চার অংশের তুলনাযোগ্য ক্যাশড ভাড়া পাওয়া যায়নি। নিচের লিংক দিয়ে তারিখ ধরে লাইভ দাম চেক করুন।";
    for (const { days, fares, total } of options) {
        const row = document.createElement("li");
        const airlines = fares.map(fare => fare?.airline || "—").join(" / ");
        row.textContent = days.join(" → ") + (Number.isFinite(total)
            ? " · আনুমানিক " + new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(total) + " · " + airlines
            : "") + " · ";
        const link = document.createElement("a");
        link.href = liveLink(days);
        link.textContent = "লাইভ দাম চেক করুন";
        row.append(link);
        for (const [origin, destination, outbound, inbound] of [
            ["DAC", "DEL", days[0], days[3]], ["DEL", "SXR", days[1], days[2]]
        ]) {
            const roundTrip = document.createElement("a");
            const ddmm = day => day.slice(8) + day.slice(5, 7);
            const params = new URLSearchParams({
                flightSearch: origin + ddmm(outbound) + destination + ddmm(inbound) + "1",
                origin_airports: "0,1", destination_airports: "0,1"
            });
            roundTrip.href = "/?" + params + "#wl-flight-results";
            roundTrip.textContent = origin + " ↔ " + destination;
            row.append(" · ", roundTrip);
        }
        byId("results").append(row);
    }
    button.disabled = false;
});

byId("markets").addEventListener("submit", event => {
    event.preventDefault();
    const entries = [...new FormData(event.currentTarget)]
        .map(([market, amount]) => ({ market, amount: Number(amount) }))
        .filter(entry => Number.isFinite(entry.amount) && entry.amount > 0)
        .sort((a, b) => a.amount - b.amount);
    byId("comparison").textContent = entries.length < 2 ? "অন্তত দুই দেশের চেকআউট মূল্য দিন।"
        : entries.map(entry => entry.market + " ৳" + entry.amount.toLocaleString("bn-BD")).join(" · ");
});
