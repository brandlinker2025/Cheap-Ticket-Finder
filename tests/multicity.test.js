const assert = require("assert");
const BookingLinks = require("../js/booking-links.js");

const legs = [
    { origin: "dac", dest: "kul", date: "2026-11-30" },
    { origin: "KUL", dest: "hkt", date: "2026-12-05" }
];

assert.strictEqual(
    BookingLinks.aviasalesFlightSearch(legs, "1"),
    "DAC3011KUL0512HKT1",
    "connected multi-city path collapses the repeated airport"
);

assert.strictEqual(
    BookingLinks.aviasalesFlightSearch([
        { origin: "DAC", dest: "KUL", date: "2026-11-30" },
        { origin: "BKK", dest: "HKT", date: "2026-12-05" }
    ], "1"),
    "DAC3011KULBKK0512HKT1",
    "open-jaw multi-city path keeps the next origin"
);

assert.strictEqual(BookingLinks.aviasalesFlightSearch([
    { origin: "DAC", dest: "KUL", date: "2026-11-30" },
    { origin: "KUL", dest: "HKT", date: "2026-12-05" },
    { origin: "HKT", dest: "SIN", date: "2026-12-09" }
], "c21"), "DAC3011KUL0512HKT0912SINc21");

assert.strictEqual(BookingLinks.multiCityLegsReady(legs), true);
assert.strictEqual(BookingLinks.multiCityLegsReady([legs[0]]), false, "one flight is not multi-city");
assert.strictEqual(BookingLinks.multiCityLegsReady([
    legs[0],
    { origin: "KUL", dest: "HKT", date: "2026-11-29" }
]), false, "a later flight cannot leave before the previous one");
assert.strictEqual(BookingLinks.multiCityLegsReady([
    legs[0],
    { origin: "KUL", dest: "HKT", date: "2026-11-30" }
]), true, "same-day connections are allowed");
assert.strictEqual(BookingLinks.multiCityLegsReady([
    { origin: "DAC", dest: "DAC", date: "2026-11-30" },
    legs[1]
]), false, "a flight cannot depart and arrive at the same airport");

assert.strictEqual(BookingLinks.compactAirportLabel({ city: "Dhaka", code: "dac", name: "Hazrat Shahjalal Int. (DAC)" }), "Dhaka (DAC)");
assert.strictEqual(BookingLinks.compactAirportLabel({ city: "Bangkok (Main Hub)", code: "bkk" }), "Bangkok (BKK)");
assert.strictEqual(BookingLinks.compactAirportLabel({ city: "Kuala Lumpur", code: "kul" }), "Kuala Lumpur (KUL)");

const opts = { tripType: "multicity", legs, adults: 1, children: 0, infants: 0, cabin: "economy" };
const kayak = BookingLinks.kayakUrl(opts);
assert.ok(kayak.includes("DAC-KUL/2026-11-30/KUL-HKT/2026-12-05"), kayak);
const sky = BookingLinks.skyscannerUrl(opts);
assert.ok(sky.includes("/dac/kul/261130/kul/hkt/261205/"), sky);
const trip = BookingLinks.tripComFlightsUrl(opts);
assert.ok(trip.includes("triptype=mt"), trip);
assert.ok(trip.includes("dcity1=dac") && trip.includes("acity1=kul") && trip.includes("ddate1=2026-11-30"), trip);
assert.ok(trip.includes("dcity2=kul") && trip.includes("acity2=hkt") && trip.includes("ddate2=2026-12-05"), trip);

const oldMulti = BookingLinks.kayakUrl({
    origin: "DAC",
    dest: "BKK",
    stop: "HKT",
    depart: "2026-11-01",
    returnDate: "2026-11-08",
    tripType: "multicity"
});
assert.ok(oldMulti.includes("DAC-BKK/2026-11-01/BKK-HKT/2026-11-08"), "existing stopover links stay intact");

console.log("multicity.test.js passed");
