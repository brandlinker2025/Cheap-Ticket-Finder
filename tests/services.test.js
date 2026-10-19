const assert = require("assert");
const fs = require("fs");
const path = require("path");
const read = (p) => fs.readFileSync(path.join(__dirname, "..", p), "utf8");
const home = read("index.html");
const hotels = read("hotels/index.html");
const packages = read("packages/index.html");
const esim = read("esim/index.html");
const transfer = read("airport-transfer/index.html");
const sitemap = read("sitemap.xml");

for (const [name, html, campaign, partner] of [
  ["hotels", hotels, "campaign_id=137", "Klook"],
  ["packages", packages, "campaign_id=633", "KKday"],
  ["esim", esim, "campaign_id=541", "Airalo"],
  ["airport-transfer", transfer, "campaign_id=1&", "KiwiTaxi"],
]) {
  assert.ok(html.includes("marker=791994"), `${name} must carry marker=791994`);
  assert.ok(html.includes(campaign), `${name} must carry ${campaign}`);
  assert.ok(html.includes("trs=587447"), `${name} must carry trs=587447`);
  assert.ok(html.includes(partner), `${name} must name ${partner}`);
  assert.ok(html.includes('rel="sponsored noopener noreferrer"'), `${name} affiliate CTA must use sponsored rel`);
  assert.ok(html.includes("/disclosure"), `${name} must link disclosure`);
  assert.ok(html.includes("/assets/luxury.css"), `${name} must use shared luxury theme`);
  assert.ok(!/৳\s?\d|BDT\s?\d|\$\s?\d+\s*(per night|per person|only)/i.test(html), `${name} must not invent prices`);
}
assert.ok(hotels.includes("not a pure hotel-only site"), "hotels must honestly describe Klook");
assert.ok(home.includes("campaign_id=137") && home.includes("marker=791994"), "homepage must contain hotels affiliate link");
assert.ok(home.includes("campaign_id=633"), "homepage must contain packages affiliate link");
assert.ok(packages.includes("pid=P00326733") && packages.includes("https://www.viator.com/?pid=P00326733&uid=U00880752&mcid=58086&currency=USD"), "packages must contain verified Viator link");
assert.ok(packages.includes("Viator") && packages.includes("KKday (Asia tours)") && packages.includes("worldwide tours"), "packages must label KKday Asia / Viator worldwide");
assert.ok(home.includes("pid=P00326733"), "homepage must contain Viator secondary link");
assert.ok((packages.match(/pid=P00326733/g)||[]).length>=1 && packages.includes('rel="sponsored noopener noreferrer"'), "Viator CTA must use sponsored rel");
assert.ok(home.includes("campaign_id=100"), "homepage must keep flight affiliate link");
assert.ok(home.includes("campaign_id=541") && home.includes("cheapticketfinder-esim"), "homepage must contain eSIM affiliate link");
assert.ok(home.includes("campaign_id=1&marker=791994") && home.includes("cheapticketfinder-transfer"), "homepage must contain transfer affiliate link");
assert.ok(home.includes('href="/esim/"') && home.includes('href="/airport-transfer/"'), "homepage must link /esim/ and /airport-transfer/");
assert.ok(!home.includes("12go") && !esim.includes("12go") && !transfer.includes("12go"), "12Go is under review and must not be added");
assert.ok((home.match(/rel="sponsored noopener noreferrer"/g) || []).length >= 3, "homepage affiliate CTAs must use sponsored rel");
assert.ok(home.includes('href="/hotels/"') && home.includes('href="/packages/"'), "homepage must link /hotels/ and /packages/");
assert.ok(home.includes('id="servicesSection"'), "homepage must have services section");
assert.ok(sitemap.includes("https://cheapticketfinder.site/hotels/"), "sitemap must include hotels");
assert.ok(sitemap.includes("https://cheapticketfinder.site/packages/"), "sitemap must include packages");
assert.ok(sitemap.includes("https://cheapticketfinder.site/esim/"), "sitemap must include esim");
assert.ok(sitemap.includes("https://cheapticketfinder.site/airport-transfer/"), "sitemap must include airport-transfer");
assert.ok(!home.includes("trip.com") && !hotels.includes("trip.com") && !packages.includes("booking.com/"), "locked partners must not be linked");
console.log("services.test.js OK (hotels 137 + packages 633 KKday + Viator P00326733 + esim 541 + transfer 1, marker 791994)");
