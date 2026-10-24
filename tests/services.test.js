const assert = require("assert");
const fs = require("fs");
const path = require("path");
const read = (p) => fs.readFileSync(path.join(__dirname, "..", p), "utf8");
const home = read("index.html");
const hotels = read("hotels/index.html");
const packages = read("packages/index.html");
const esim = read("esim/index.html");
const transfer = read("airport-transfer/index.html");
const insurance = read("travel-insurance/index.html");
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
assert.ok(sitemap.includes("https://cheapticketfinder.site/travel-insurance/"), "sitemap must include travel-insurance");
assert.ok(insurance.includes("https://ektatraveling.com/"), "travel-insurance must contain EKTA link");
assert.ok(insurance.includes("EKTA") && insurance.includes("policy terms"), "travel-insurance must name EKTA and tell users to check policy terms");
assert.ok(packages.includes("https://tiqets.tpo.lv/zc9OgjmX") && packages.includes("Tiqets"), "packages must contain Tiqets link");
assert.ok(esim.includes("https://yesim.tpo.lv/ZAsUxhwZ") && esim.includes("Yesim"), "esim must contain Yesim link as second option");
assert.ok(!(home + insurance).includes("ektatraveling.tpo.lv/ArgAETEF"), "broken EKTA tpo.lv link (marker not subscribed) must stay removed");
assert.ok(home.includes("https://ektatraveling.com/") && home.includes('href="/travel-insurance/"'), "homepage services card must contain EKTA link and travel-insurance guide");
for (const [name, url] of [["Tiqets", "https://tiqets.tpo.lv/zc9OgjmX"], ["Yesim", "https://yesim.tpo.lv/ZAsUxhwZ"]]) {
  const all = home + packages + esim + insurance;
  assert.ok(all.includes(`href="${url}" target="_blank" rel="sponsored noopener noreferrer"`), `${name} CTA must use exact sponsored rel`);
}
for (const [label, url] of [
  ["flights", "https://www.trip.com/flights?Allianceid=11059812&SID=333836392&trip_sub1=flights&trip_sub3=D20343143"],
  ["hotels", "https://www.trip.com/hotels?Allianceid=11059812&SID=333836392&trip_sub1=hotels&trip_sub3=D20343143"],
  ["tours", "https://www.trip.com/things-to-do/?Allianceid=11059812&SID=333836392&trip_sub1=tours&trip_sub3=D20343143"],
  ["transfers", "https://www.trip.com/airport-transfers/index/?Allianceid=11059812&SID=333836392&trip_sub1=transfer&trip_sub3=D20343143"],
  ["homepage", "https://www.trip.com/?Allianceid=11059812&SID=333836392&trip_sub1=homepage&trip_sub3=D20343143"],
]) {
  assert.ok(home.includes(`href="${url}"`), `homepage must keep the approved Trip.com ${label} link`);
  assert.ok(home.includes(`href="${url}" target="_blank" rel="sponsored noopener noreferrer"`), `Trip.com ${label} link must use sponsored rel`);
}
assert.ok(!hotels.includes("trip.com") && !packages.includes("trip.com") && !packages.includes("booking.com/"), "Trip.com stays on the homepage; other pages stay unchanged");
console.log("services.test.js OK (hotels 137 + packages 633 KKday + Viator P00326733 + esim 541 + transfer 1, marker 791994)");
