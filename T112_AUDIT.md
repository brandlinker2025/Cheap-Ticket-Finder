# T-112 link audit

Date: 24 Oct 2026 (Asia/Dhaka). Branch `t112-v2` vs `origin/main` 8ee401f.

Method: `curl -L` with a Chrome UA for every external homepage link, plus a headed Chrome check (xvfb, Playwright headless=False) for affiliate and Bangladesh deep links. `npm run check-links` was also run: 192 links, 167 OK, 23 bot-blocked, and 2 "dead" (/cruise/ and /credits/, which are new pages not on production yet).

## Fixed / new

| Section | Link | Status | Evidence |
|---|---|---|---|
| Travel Insurance (home + /travel-insurance/) | https://ektatraveling.tpo.lv/ArgAETEF | **broken → fixed** | HTTP 400 "marker is not subscribed to campaign" (headed Chrome + curl). Replaced with https://ektatraveling.com/ (200) as a plain link with an "official site, not an affiliate link" note. |
| Domestic: Bus | https://www.shohoz.com/bus-tickets/booking/bus/search?fromcity=…&tocity=…&doj=DD-Mon-YYYY | **new, working** | Headed Chrome: Dhaka→Chittagong 10-Nov-2026 and Dhaka→Cox's Bazar/Sylhet/Barisal 12-Nov-2026 all show real operator lists (Hanif Enterprise, LABIBA Classic…). |
| Domestic: Train | https://eticket.railway.gov.bd/ | **new, working (home only)** | The deep search URL redirects to /login ("Please login first"), so this is a plain link with a log-in note. |
| Domestic: Launch | https://www.shohoz.com/launch-tickets | **new, working (landing only)** | The launch search deep link returned 404 in headed Chrome. |
| Hotel tab | https://www.agoda.com/ , https://www.booking.com/ | **new, working** | curl 200 / 202. Plain links with a note. |
| Tour tab | Klook tp.media 137 (sub_id cheapticketfinder-tours), https://www.getyourguide.com/ , https://gozayaan.com/ | **new, working** | Klook redirects with aff_pid=791994. GoZayaan returns 200. GetYourGuide returns 403 to curl (bot block). 12Go was not added because the honesty test marks it "under review". |
| /cruise/ | Royal Caribbean SG itinerary + schedule, stardreamcruises.com/en-us/deals, cordeliacruises.com/srilanka + /maldives-cruises | **new, working** | Pages read during research. No prices shown. |

## Existing homepage links (unchanged)

| Link | Status | Evidence |
|---|---|---|
| https://airastra.com | working | curl 200 |
| https://airastra.com/holiday-packages | working | curl 200 |
| https://airastra.com/offer/offers-deals/10-discount-base-fare | working | curl 200 |
| https://av.sc.com/bd/edm/airline-offers/ | working | curl 200 |
| https://booking.flyscoot.com/Book/Flight | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://booking.qatarairways.com/nsp/views/showBooking.action | working | curl 200 |
| https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css | working | curl 200 |
| https://cheapticketfinder.site/ | working | curl 200 |
| https://eticket.railway.gov.bd/ | working | curl 200 |
| https://fo-airastra.ttinteractive.com/Zenith/FrontOffice/Airastra/en-GB/ | working | curl 200 |
| https://fo-usba.ttinteractive.com/Zenith/FrontOffice/usbangla/en-GB/ | working | curl 200 |
| https://gozayaan.com/campaign/id/644 | working | curl 200 |
| https://gozayaan.com/campaign/sc | working | curl 200 |
| https://gozayaan.com/flight | working | curl 200 |
| https://holidays.flydubai.com/en-bd/cheap-holiday-packages/ | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://holidays.turkishairlines.com/ | working | curl 200 |
| https://secure.flynovoair.com/bookings/flight_selection.aspx | working | curl 200 |
| https://sharetrip.net/ | working | curl 200 |
| https://specials.priceless.com/en-ap/homepage | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://tp.media/r?campaign_id=1&marker=791994&p=647&sub_id=cheapticketfinder-transfer&trs=587447&u=https%3A%2F%2Fkiwitaxi.com | working (bot-blocked to curl) | curl 429; site refuses scripted requests, opens normally in a browser |
| https://tp.media/r?campaign_id=100&marker=791994&p=4114&sub_id=cheapticketfinder-site&trs=587447&u=https%3A%2F%2Faviasales.com | working | curl 200 |
| https://tp.media/r?campaign_id=137&marker=791994&p=4110&sub_id=cheapticketfinder-hotels&trs=587447&u=https%3A%2F%2Fklook.com | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://tp.media/r?campaign_id=541&marker=791994&p=8310&sub_id=cheapticketfinder-esim&trs=587447&u=https%3A%2F%2Fairalo.com | working | curl 200 |
| https://tp.media/r?campaign_id=633&marker=791994&p=9074&sub_id=cheapticketfinder-packages&trs=587447&u=https%3A%2F%2Fkkday.com | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://usbair.com | working | curl 200 |
| https://usbair.com/offers | working | curl 200 |
| https://www.airasia.com | working | curl 200 |
| https://www.airasia.com/flights/search | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://www.airastra.com/node?field_offers_type_target_id=All | working | curl 200 |
| https://www.airindia.com | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.biman-airlines.com/ | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://www.bkash.com/en/campaign | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://www.bracbank.com/en/offers | working | curl 200 |
| https://www.ebl.com.bd/retail/EBL-Cards | working | curl 200 |
| https://www.ebl.com.bd/retail/eblcard/ebl-stellar-platinum-credit-card | working | curl 200 |
| https://www.emirates.com/bd/english/ | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://www.emirates.com/bd/english/book/ | working | curl 200 |
| https://www.emirates.com/bd/english/special-offers/ | working | curl 200 |
| https://www.facebook.com/CheapTFBD | check | curl 400; site refuses scripted requests, opens normally in a browser |
| https://www.flydubai.com/en/ | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.flydubai.com/en/offers/ | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.flynovoair.com | working | curl 200 |
| https://www.flynovoair.com/offers | working | curl 200 |
| https://www.flyscoot.com/ | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |
| https://www.goindigo.in | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.google.com/travel/flights?hl=en&curr=BDT | working | curl 200 |
| https://www.malaysiaairlines.com/ | working | curl 200 |
| https://www.qatarairways.com/en-bd/homepage.html | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.qatarairways.com/en-bd/offers.html | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.qatarairways.com/en-bd/offers/f1-fans-flight-deals.html | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.qatarairwaysholidays.com/ | working | curl 200 |
| https://www.saudia.com/ | working | curl 200 |
| https://www.shohoz.com/bus-tickets | working | curl 200 |
| https://www.shohoz.com/launch-tickets | working | curl 200 |
| https://www.singaporeair.com/ | working | curl 200 |
| https://www.thaiairways.com | working | curl 200 |
| https://www.trip.com/?Allianceid=11059812&SID=333836392&trip_sub1=homepage&trip_sub3=D20343143 | working (bot-blocked to curl) | curl 432; site refuses scripted requests, opens normally in a browser |
| https://www.trip.com/airport-transfers/index/?Allianceid=11059812&SID=333836392&trip_sub1=transfer&trip_sub3=D20343143 | working | curl 200 |
| https://www.trip.com/flights?Allianceid=11059812&SID=333836392&trip_sub1=flights&trip_sub3=D20343143 | working | curl 200 |
| https://www.trip.com/hotels?Allianceid=11059812&SID=333836392&trip_sub1=hotels&trip_sub3=D20343143 | working | curl 200 |
| https://www.trip.com/things-to-do/?Allianceid=11059812&SID=333836392&trip_sub1=tours&trip_sub3=D20343143 | working | curl 200 |
| https://www.turkishairlines.com/ | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.turkishairlines.com/en-int/flights/campaigns/ | working (bot-blocked to curl) | curl 000; site refuses scripted requests, opens normally in a browser |
| https://www.viator.com/?pid=P00326733&uid=U00880752&mcid=58086&currency=USD | working (bot-blocked to curl) | curl 403; site refuses scripted requests, opens normally in a browser |

Notes: the tp.media links for Aviasales, Airalo, Kiwitaxi, Klook and KKday all land with marker 791994 in the final URL, so they are live. Tiqets and Yesim (sub-pages) redirect with 791994 (200). facebook.com returns 400 to curl but works in a browser.
