const assert = require("assert");
const fs = require("fs");
for (const f of ["index.html", "bn/index.html"]) {
  const s = fs.readFileSync(f, "utf8");
  assert.ok(s.includes("const destination = leg.dest;"), f + ": multi-city must keep the final destination (Aviasales drops the last flight without it)");
  assert.ok(s.includes('id="multiLegHelp"') && s.includes("renderMultiLegHelp();"), f + ": leg-by-leg help must render");
}
console.log("multicity ok");
