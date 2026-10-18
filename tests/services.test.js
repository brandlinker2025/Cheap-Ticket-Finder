const assert = require("assert");
const fs = require("fs");
const path = require("path");
const read = (p) => fs.readFileSync(path.join(__dirname, "..", p), "utf8");
const home = read("index.html");
const hotels = read("hotels/index.html");
const packages = read("packages/index.html");
const sitemap = read("sitemap.xml");

for (const [name, html, campaign, partner] of [
  ["hotels", hotels, "campaign_id=137", "Klook"],
  ["packages", packages, "campaign_id=633", "KKday"],
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
assert.ok(home.includes("campaign_id=100"), "homepage must keep flight affiliate link");
assert.ok((home.match(/rel="sponsored noopener noreferrer"/g) || []).length >= 3, "homepage affiliate CTAs must use sponsored rel");
assert.ok(home.includes('href="/hotels/"') && home.includes('href="/packages/"'), "homepage must link /hotels/ and /packages/");
assert.ok(home.includes('id="servicesSection"'), "homepage must have services section");
assert.ok(sitemap.includes("https://cheapticketfinder.site/hotels/"), "sitemap must include hotels");
assert.ok(sitemap.includes("https://cheapticketfinder.site/packages/"), "sitemap must include packages");
assert.ok(!home.includes("trip.com") && !hotels.includes("trip.com") && !packages.includes("booking.com/"), "locked partners must not be linked");
console.log("services.test.js OK (hotels 137 + packages 633, marker 791994)");
