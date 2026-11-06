const assert = require("assert");
const fs = require("fs");
const B = require("../js/booking-links.js");
const o = { city: "Bangkok", checkin: "2026-12-10", checkout: "2026-12-12", adults: 2, rooms: 1 };
const L = B.hotelCompareLinks(o);
assert.deepStrictEqual(L.map(x => x.id), ["agoda", "tripcom", "booking", "google-hotels"]);
assert.ok(L[0].url.includes("city=9395") && L[0].url.includes("checkIn=2026-12-10"));
assert.ok(L[1].url.includes("city=359") && L[1].url.includes("Allianceid=11059812"));
assert.ok(L[2].url.includes("group_adults=2"));
assert.strictEqual(B.hotelCityInfo("KUL").name, "Kuala Lumpur");
assert.strictEqual(B.hotelCityInfo("coxs bazar").name, "Cox's Bazar");
assert.strictEqual(B.hotelCityInfo("Dhaka (DAC)").agoda, 1390);
// unknown city: no broken deep link, falls back to the site home
const U = B.hotelCompareLinks(Object.assign({}, o, { city: "Nowhereville" }));
assert.strictEqual(U[0].url, "https://www.agoda.com/");
assert.ok(U[1].url.startsWith("https://www.trip.com/hotels?"));
assert.strictEqual(B.nightsBetween("2026-12-10", "2026-12-12"), 2);
// rooms never exceed adults
assert.ok(B.agodaHotelUrl({ city: "Dubai", checkin: "2026-12-10", checkout: "2026-12-11", adults: 1, rooms: 3 }).includes("rooms=1"));
// after-flight hotel list keeps the old two and adds two
assert.deepStrictEqual(B.hotelLinks(o).map(x => x.id), ["google-hotels", "booking", "agoda", "tripcom-hotels"]);
const html = fs.readFileSync(__dirname + "/../index.html", "utf8");
assert.ok(html.includes('id="hotelSearchForm"') && html.includes("Book hotels on Klook"), "hotel form added, old links kept");
console.log("hotel-compare.test.js OK");
