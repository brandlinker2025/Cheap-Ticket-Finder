const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
assert.ok(html.includes('id="returnDateField"'), "return date control must exist");
assert.ok(html.includes(">Pick return date<"), "return date control must start as Pick return date");
assert.ok(html.includes("function focusReturnPick"), "return date control must have a handler");
assert.ok(!html.includes("we do not put Skyscanner"), "homepage must not say Skyscanner is kept off the page");

const scanStart = html.indexOf("function triggerFullScan");
const scanFn = html.slice(scanStart, html.indexOf("renderCalendars();", scanStart));
assert.ok(scanFn.includes("focusReturnPick"), "missing return date must open return picking instead of stopping");

assert.ok(!html.includes("https://www.skyscanner.com/"), "homepage must not link out to Skyscanner");
assert.ok(!html.includes("Search on Skyscanner"), "homepage must not offer a Search on Skyscanner button");
assert.ok(html.includes('href="#wl-flight-results"'), "homepage search shortcut points at the on-site results");
assert.ok(!/impact\.com|partners\.skyscanner\.net/i.test(html), "do not add Impact or affiliate-programme tracking");

function extractFn(name, signature) {
    const start = html.indexOf(`function ${name}(${signature})`);
    assert.ok(start > 0, `missing function ${name}`);
    const end = html.indexOf("\n        function ", start + 10);
    return html.slice(start, end);
}

const sandbox = {
    currentTripType: "round",
    calendarPhase: "depart",
    selectedDeptDate: null,
    selectedRetDate: null,
    calMonth: new Date(),
    renderCalls: 0,
    scanCalls: 0,
    resetCalls: 0,
    renderCalendars() { sandbox.renderCalls += 1; },
    triggerFullScan() { sandbox.scanCalls += 1; },
    resetResultsUntilDates() { sandbox.resetCalls += 1; },
    console
};
vm.createContext(sandbox);
vm.runInContext(`
function datesReady() {
    if (!selectedDeptDate) return false;
    if (currentTripType === "oneway") return true;
    return Boolean(selectedRetDate);
}
` + extractFn("selectDate", "y, m, d"), sandbox);

function ymd(offset) {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + offset);
    return d;
}

const depart = ymd(12);
const ret = ymd(19);
sandbox.selectDate(depart.getFullYear(), depart.getMonth(), depart.getDate());
assert.strictEqual(sandbox.calendarPhase, "return", "after departure, picker must wait for a return date");
assert.strictEqual(Object.prototype.toString.call(sandbox.selectedDeptDate), "[object Date]", "departure must be stored");
assert.strictEqual(sandbox.selectedRetDate, null, "departure tap must not invent a return");
assert.strictEqual(sandbox.scanCalls, 0, "search must wait until the return date is chosen");

sandbox.selectDate(ret.getFullYear(), ret.getMonth(), ret.getDate());
assert.strictEqual(Object.prototype.toString.call(sandbox.selectedRetDate), "[object Date]", "return date must be selectable");
assert.strictEqual(sandbox.selectedRetDate.getDate(), ret.getDate());
assert.ok(sandbox.selectedRetDate >= sandbox.selectedDeptDate, "return must not be before departure");
assert.strictEqual(sandbox.scanCalls, 1, "round trip with a return date must be ready to search");

const later = ymd(26);
sandbox.calendarPhase = "return";
sandbox.selectDate(later.getFullYear(), later.getMonth(), later.getDate());
assert.strictEqual(sandbox.selectedRetDate.getDate(), later.getDate(), "an active return pick must update the return date");
assert.strictEqual(sandbox.selectedDeptDate.getDate(), depart.getDate(), "changing the return must keep the departure");

sandbox.currentTripType = "oneway";
sandbox.calendarPhase = "depart";
sandbox.selectedRetDate = new Date();
const one = ymd(15);
sandbox.selectDate(one.getFullYear(), one.getMonth(), one.getDate());
assert.strictEqual(sandbox.selectedRetDate, null, "one-way must clear the return date");
assert.strictEqual(sandbox.calendarPhase, "depart");

const BookingLinks = require("../js/booking-links.js");
const iso = (d) => {
    const p = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
};
const opts = {
    origin: "DAC",
    dest: "BKK",
    depart: iso(depart),
    returnDate: iso(ret),
    tripType: "round"
};
const gf = BookingLinks.googleFlightsUrl(opts);
const skyUrl = BookingLinks.skyscannerUrl(opts);
const kayak = BookingLinks.kayakUrl(opts);
assert.ok(gf.includes("tfs="), "Google Flights search URL must be built");
assert.ok(skyUrl.includes(`/${BookingLinks.toSkyDate(opts.depart)}/${BookingLinks.toSkyDate(opts.returnDate)}/`), "Skyscanner URL must include the return date");
assert.ok(kayak.includes(`/${opts.depart}/${opts.returnDate}`), "Kayak URL must include the return date");
assert.ok(!skyUrl.includes("marker="), "dated Skyscanner URL must stay non-affiliate");
const oneUrl = BookingLinks.skyscannerUrl({ ...opts, tripType: "oneway", returnDate: "" });
assert.ok(!oneUrl.includes(BookingLinks.toSkyDate(opts.returnDate)), "one-way Skyscanner URL must not keep a return date");

console.log("return-date.test.js passed");
