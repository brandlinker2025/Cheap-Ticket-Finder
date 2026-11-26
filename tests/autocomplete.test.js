// Airport / city autocomplete: runs the real ranking code from the page against the built-in (local) dataset.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

function load(file) {
    const html = fs.readFileSync(path.join(__dirname, "..", file), "utf8");
    const a = html.indexOf("const COUNTRY_AIRPORTS = [");
    const b = html.indexOf("\n        ];", a) + "\n        ];".length;
    const c = html.indexOf("function cleanString(");
    const end = html.indexOf("function filterModalAirports(");
    assert.ok(a > 0 && b > a && c > 0 && end > c, `${file}: autocomplete code not found`);
    const code = html.slice(a, b) + "\n" + html.slice(c, end) + "\n;this.COUNTRY_AIRPORTS = COUNTRY_AIRPORTS; this.rankAirports = rankAirports;";
    const ctx = {};
    vm.runInNewContext(code, ctx);
    return ctx;
}

for (const file of ["index.html", "bn/index.html"]) {
    const { COUNTRY_AIRPORTS: list, rankAirports } = load(file);
    assert.ok(list.length >= 40, `${file}: local airport dataset should not be empty (${list.length})`);
    for (const a of list) {
        assert.ok(/^[a-z0-9]{3}$/.test(a.code), `${file}: bad IATA ${a.code}`);
        assert.ok(a.name && a.city && a.country, `${file}: incomplete airport ${a.code}`);
    }
    const codes = list.map((a) => a.code);
    assert.strictEqual(new Set(codes).size, codes.length, `${file}: duplicate airport codes in local dataset`);

    const top = (q) => rankAirports(list, q).map((a) => a.code);
    assert.strictEqual(top("dac")[0], "dac", "exact IATA first");
    assert.strictEqual(top("DAC")[0], "dac", "case-insensitive IATA");
    assert.strictEqual(top("dhaka")[0], "dac", "city name");
    assert.strictEqual(top("Shahjalal")[0], "dac", "airport name");
    assert.ok(top("cox").includes("cxb") && top("coxs bazar")[0] === "cxb", "Cox's Bazar spelling variants");
    assert.strictEqual(top("bangladesh")[0], "dac", "country search: busiest airport first");
    assert.strictEqual(top("bd")[0], "dac", "country alias BD");
    assert.ok(top("bangkok").includes("bkk"), "Bangkok -> BKK");
    assert.ok(top("uae").includes("dxb"), "UAE alias -> DXB");
    assert.ok(top("london").some((c) => ["lhr", "lgw", "stn", "ltn"].includes(c)), "London -> a London airport");
    assert.strictEqual(top("zzzzqqq").length, 0, "no match -> empty list");
    assert.ok(rankAirports(list, "").length > 0 && rankAirports(list, "").length <= 80, "empty query -> capped default list");
    // Input is treated as text, never as a pattern.
    assert.doesNotThrow(() => rankAirports(list, "(*[\\"));
    assert.strictEqual(top("<script>").length, 0);
}
console.log("autocomplete.test.js OK (local dataset + ranking, en + bn)");
