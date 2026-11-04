#!/usr/bin/env python3
"""Build the Bangla homepage (bn/index.html) as a full copy of index.html with Bangla text.

Same search box, tabs, cards and buttons as the English homepage — only the words change.
Brand and partner names (Trip.com, Aviasales, Klook ...) stay as they are.
Run from repo root after any change to index.html:  python3 scripts/build_bn_home.py
"""
import re, sys

SRC, OUT = "index.html", "bn/index.html"

# Visible text between tags: English -> Bangla (exact match after trimming whitespace)
TEXT = {
    "Offers": "অফার", "Contact": "যোগাযোগ", "Facebook": "ফেসবুক",
    "Air Ticket": "বিমান টিকিট", "Airlines": "এয়ারলাইন", "Hotel Booking": "হোটেল বুকিং",
    "Tour Package": "ট্যুর প্যাকেজ", "Travel SIM": "ট্রাভেল সিম", "Airport Transfer": "এয়ারপোর্ট ট্রান্সফার",
    "Bus / Train / Launch": "বাস / ট্রেন / লঞ্চ",
    "Round Trip": "রাউন্ড ট্রিপ", "One Way": "ওয়ান ওয়ে", "Multi-City": "মাল্টি-সিটি",
    "From": "কোথা থেকে", "To": "কোথায়", "City or airport": "শহর বা এয়ারপোর্ট",
    "Departure date": "যাওয়ার তারিখ", "Select date": "তারিখ বাছুন", "Return date": "ফেরার তারিখ",
    "Traveller / class": "যাত্রী / ক্লাস", "1 adult · Economy": "১ জন প্রাপ্তবয়স্ক · ইকোনমি",
    "Adults": "প্রাপ্তবয়স্ক", "Children": "শিশু", "Infants": "ইনফ্যান্ট", "under 2": "২ বছরের কম",
    "Cabin class": "ক্লাস", "Economy": "ইকোনমি", "Premium Economy": "প্রিমিয়াম ইকোনমি",
    "Business": "বিজনেস", "First": "ফার্স্ট", "Done": "ঠিক আছে", "Search": "খুঁজুন",
    "Pick your route and dates. Search flights and compare prices from partner sites in the on-site flight search and Travelpayouts results. We do not sell tickets.":
        "রুট আর তারিখ দিন, পার্টনার সাইটগুলোর ফ্লাইটের দাম এখানেই তুলনা করুন। আমরা টিকিট বিক্রি করি না।",
    "Open this itinerary on Aviasales": "এই যাত্রাপথ Aviasales-এ দেখুন",
    "+ Add another flight": "+ আরও একটি ফ্লাইট যোগ করুন",
    "Pick a departure date.": "যাওয়ার তারিখ বাছুন।",
    "Depart": "যাওয়া", "Return": "ফেরা", "Today": "আজ",
    "Open on-site flight search": "ফ্লাইট সার্চ খুলুন",
    "Airlines guide": "এয়ারলাইন গাইড",
    "Book hotels on Klook": "Klook-এ হোটেল বুক করুন", "Trip.com hotels": "Trip.com হোটেল",
    "Agoda hotels": "Agoda হোটেল", "Booking.com hotels": "Booking.com হোটেল", "Hotel guide": "হোটেল গাইড",
    "Agoda and Booking.com open the official sites directly; they are not affiliate links yet.":
        "Agoda ও Booking.com সরাসরি তাদের অফিসিয়াল সাইটে খোলে; এগুলো এখনো অ্যাফিলিয়েট লিংক নয়।",
    "Explore Asia packages on KKday": "KKday-তে এশিয়ার প্যাকেজ দেখুন",
    "Or worldwide tours on Viator": "অথবা Viator-এ বিশ্বজুড়ে ট্যুর",
    "Trip.com tours": "Trip.com ট্যুর", "Klook activities": "Klook অ্যাক্টিভিটি",
    "GoZayaan holidays & offers": "GoZayaan হলিডে ও অফার", "Tour guide": "ট্যুর গাইড",
    "GetYourGuide and GoZayaan open the official sites directly; they are not affiliate links.":
        "GetYourGuide ও GoZayaan সরাসরি তাদের অফিসিয়াল সাইটে খোলে; এগুলো অ্যাফিলিয়েট লিংক নয়।",
    "Check eSIM on Airalo": "Airalo-তে eSIM দেখুন", "Travel eSIM guide": "ট্রাভেল eSIM গাইড",
    "Book transfer on KiwiTaxi": "KiwiTaxi-তে ট্রান্সফার বুক করুন",
    "Trip.com airport transfers": "Trip.com এয়ারপোর্ট ট্রান্সফার", "Transfer guide": "ট্রান্সফার গাইড",
    "Bangladesh bus, train and launch tickets. These open the official or operator booking sites; the fare and seats are shown there. We do not sell tickets.":
        "দেশের ভেতরে বাস, ট্রেন ও লঞ্চের টিকিট। এগুলো অফিসিয়াল বা অপারেটরের বুকিং সাইটে খোলে; ভাড়া ও সিট সেখানেই দেখা যায়। আমরা টিকিট বিক্রি করি না।",
    "Where to next?": "এবার কোথায় যাবেন?",
    "Pick a section. Prices are shown only on the provider sites.": "একটি বিভাগ বাছুন। দাম শুধু বুকিং সাইটেই দেখা যায়।",
    "Compare fares": "ভাড়া তুলনা", "Official carriers": "অফিসিয়াল এয়ারলাইন", "Hotel": "হোটেল",
    "Stays in Asia": "এশিয়ায় থাকা", "Tours & activities": "ট্যুর ও অ্যাক্টিভিটি", "eSIM data": "eSIM ডেটা",
    "Arrive in comfort": "আরামে পৌঁছান", "Bangladesh routes": "দেশের ভেতরের রুট", "Cruise": "ক্রুজ",
    "Asian sailings": "এশিয়ার সমুদ্রযাত্রা", "Domestic": "দেশের ভেতরে", "Plan a trip in Bangladesh": "বাংলাদেশে ভ্রমণ পরিকল্পনা",
    "Photos: Wikimedia Commons, see": "ছবি: Wikimedia Commons, দেখুন", "credits": "ক্রেডিট",
    "Live flight prices from our partner Aviasales (Travelpayouts). The final total is confirmed on the booking site.":
        "আমাদের পার্টনার Aviasales (Travelpayouts) থেকে লাইভ ফ্লাইটের দাম। চূড়ান্ত মোট দাম বুকিং সাইটে নিশ্চিত হয়।",
    "Airline offers": "এয়ারলাইন অফার",
    "Domestic (Bangladesh) and International promotions checked on each airline’s official site. Verified 20 Oct 2026. Offers change. The final price is on the airline or provider site.":
        "দেশের ভেতরের ও আন্তর্জাতিক অফার প্রতিটি এয়ারলাইনের অফিসিয়াল সাইটে যাচাই করা। যাচাই: ২০ অক্টোবর ২০২৬। অফার বদলায়; চূড়ান্ত দাম এয়ারলাইন বা বুকিং সাইটে।",
    "VietJet is listed as a regional offer for Thailand–Vietnam and nearby routes. VietJet does not fly to or from Dhaka.":
        "VietJet থাইল্যান্ড–ভিয়েতনাম ও আশেপাশের রুটের অফার হিসেবে দেওয়া। VietJet ঢাকায় আসা-যাওয়া করে না।",
    "See airline offers": "এয়ারলাইন অফার দেখুন",
    "VietJet routes": "VietJet রুট", "IndiGo routes": "IndiGo রুট", "Thai Lion Air routes": "Thai Lion Air রুট",
    "Scoot routes": "Scoot রুট", "SpiceJet routes": "SpiceJet রুট", "Air India Express routes": "Air India Express রুট",
    "Preparing your search…": "আপনার সার্চ তৈরি হচ্ছে…",
    "Tip: compare prices in the flight search first. Airline websites sometimes show a more expensive fare type first (for example “Flex”), so always check the final total before you pay.":
        "টিপস: আগে ফ্লাইট সার্চে দাম তুলনা করুন। এয়ারলাইনের সাইট অনেক সময় আগে বেশি দামের ভাড়া (যেমন “Flex”) দেখায়, তাই পেমেন্টের আগে মোট দাম দেখে নিন।",
    "ROUND TRIP": "রাউন্ড ট্রিপ", "Stay:": "থাকা:",
    "Cheap ticket path": "সস্তা টিকিটের পথ", "Start with the flight search": "ফ্লাইট সার্চ দিয়ে শুরু করুন",
    "Results include every airport of a big city (for example London: Heathrow, Gatwick, Stansted, Luton; Bangkok: BKK and DMK). Promo codes and card offers shown next to an airline are applied at that site’s checkout; any “after discount” figure is only an estimate.":
        "বড় শহরের সব এয়ারপোর্ট একসাথে দেখায় (যেমন লন্ডন: হিথ্রো, গ্যাটউইক, স্ট্যানস্টেড, লুটন; ব্যাংকক: BKK ও DMK)। এয়ারলাইনের পাশে দেখানো প্রোমো কোড ও কার্ড অফার সেই সাইটের চেকআউটে প্রযোজ্য; “ডিসকাউন্টের পর” দাম শুধু আনুমানিক।",
    "Pick your travel dates above to see where to compare and book.": "কোথায় তুলনা ও বুক করবেন দেখতে উপরে তারিখ বাছুন।",
    "Potentially Cheaper Nearby Airports — within 50 km": "কাছের এয়ারপোর্ট, যেখানে সস্তা হতে পারে — ৫০ কিমির মধ্যে",
    "Other airports within 50 km of your destination. Tap one to search it with the same dates — sometimes it is cheaper. We never make up a fare.":
        "গন্তব্যের ৫০ কিমির মধ্যে অন্য এয়ারপোর্ট। একটিতে চাপ দিলে একই তারিখে সার্চ হবে — কখনো সস্তা হয়। আমরা কখনো দাম বানাই না।",
    "Hotels for these dates": "এই তারিখের হোটেল", "Official packages": "অফিসিয়াল প্যাকেজ",
    "Only official holiday pages for this destination country. If we have no real URL, this block stays hidden.":
        "এই দেশের শুধু অফিসিয়াল হলিডে পাতা। আসল লিংক না থাকলে এই অংশ দেখানো হয় না।",
    "Domestic: bus, train & launch": "দেশের ভেতরে: বাস, ট্রেন ও লঞ্চ",
    "Choose a route and date, then continue to the operator's site to see real seats and fares.":
        "রুট ও তারিখ বাছুন, তারপর অপারেটরের সাইটে গিয়ে আসল সিট ও ভাড়া দেখুন।",
    "Dhaka": "ঢাকা", "Chittagong": "চট্টগ্রাম", "Cox's Bazar": "কক্সবাজার", "Sylhet": "সিলেট",
    "Rajshahi": "রাজশাহী", "Khulna": "খুলনা", "Barisal": "বরিশাল", "Rangpur": "রংপুর", "Bogra": "বগুড়া",
    "Jessore": "যশোর", "Comilla": "কুমিল্লা", "Mymensingh": "ময়মনসিংহ", "Dinajpur": "দিনাজপুর",
    "Kuakata": "কুয়াকাটা", "Bandarban": "বান্দরবান", "Rangamati": "রাঙামাটি", "Khagrachari": "খাগড়াছড়ি",
    "Srimangal": "শ্রীমঙ্গল", "Teknaf": "টেকনাফ", "Saidpur": "সৈয়দপুর", "Date": "তারিখ",
    "Bus on Shohoz": "Shohoz-এ বাস", "Train on Bangladesh Railway": "বাংলাদেশ রেলওয়েতে ট্রেন", "Launch on Shohoz": "Shohoz-এ লঞ্চ",
    "Bus opens Shohoz search results for your route and date. Train opens the official Bangladesh Railway e-ticket site; you must log in there, then search your route. Launch opens Shohoz launch tickets; pick your route there. We do not sell tickets.":
        "বাস: আপনার রুট ও তারিখে Shohoz-এর সার্চ খোলে। ট্রেন: বাংলাদেশ রেলওয়ের অফিসিয়াল ই-টিকিট সাইট খোলে; সেখানে লগইন করে রুট খুঁজুন। লঞ্চ: Shohoz-এর লঞ্চ টিকিট খোলে; সেখানে রুট বাছুন। আমরা টিকিট বিক্রি করি না।",
    "Official sites we link to": "যে অফিসিয়াল সাইটে আমরা লিংক দিই",
    "Logos are trademarks of their owners, shown unaltered to identify the sites we link to. Sources:":
        "লোগোগুলো তাদের মালিকের ট্রেডমার্ক; কোন সাইটে লিংক দিচ্ছি বোঝাতে অপরিবর্তিত দেখানো হয়েছে। সূত্র:",
    "Travel Insurance": "ট্রাভেল ইন্স্যুরেন্স", "Check insurance on EKTA": "EKTA-তে ইন্স্যুরেন্স দেখুন",
    "Travel insurance guide": "ট্রাভেল ইন্স্যুরেন্স গাইড",
    "Opens EKTA's official site directly (not an affiliate link).": "সরাসরি EKTA-র অফিসিয়াল সাইট খোলে (অ্যাফিলিয়েট লিংক নয়)।",
    "Local Cheap Flight": "এশিয়ার ভেতরের সস্তা ফ্লাইট",
    "Malaysia, Thailand and Vietnam domestic legs at local-airline prices: compare in the on-site flight search, then buy on the official airline site in MYR/THB/VND.":
        "মালয়েশিয়া, থাইল্যান্ড ও ভিয়েতনামের ভেতরের ফ্লাইট স্থানীয় এয়ারলাইনের দামে: ফ্লাইট সার্চে তুলনা করে অফিসিয়াল এয়ারলাইন সাইটে MYR/THB/VND-তে কিনুন।",
    "Kuala Lumpur to Langkawi cheap flight": "কুয়ালালামপুর–লংকাউই সস্তা ফ্লাইট",
    "Kuala Lumpur to Penang cheap flight": "কুয়ালালামপুর–পেনাং সস্তা ফ্লাইট",
    "Bangkok to Phuket cheap flight": "ব্যাংকক–ফুকেট সস্তা ফ্লাইট",
    "Bangkok to Chiang Mai cheap flight": "ব্যাংকক–চিয়াং মাই সস্তা ফ্লাইট",
    "Ho Chi Minh City to Hanoi cheap flight": "হো চি মিন সিটি–হ্যানয় সস্তা ফ্লাইট",
    "Ho Chi Minh City to Da Nang cheap flight": "হো চি মিন সিটি–দা নাং সস্তা ফ্লাইট",
    "Popular route guides": "জনপ্রিয় রুট গাইড",
    "How to find the cheapest dates for each route in the on-site flight search, plus baggage and total-cost checks. We do not publish invented live fares — check your dates in the tool above.":
        "প্রতিটি রুটে সবচেয়ে সস্তা তারিখ কীভাবে খুঁজবেন, সাথে ব্যাগেজ ও মোট খরচের হিসাব। আমরা বানানো দাম দেখাই না — উপরের টুলে আপনার তারিখ দেখুন।",
    "Open the ticket search tool": "টিকিট সার্চ টুল খুলুন",
    "How can I find a cheap air ticket from Bangladesh?": "বাংলাদেশ থেকে কম দামে বিমান টিকিট কীভাবে পাবো?",
    "Read the 7-step guide": "৭ ধাপের গাইড পড়ুন",
    "Cheap Ticket Finder does not sell tickets and does not scrape airlines. The final price is on the provider. cheapticketfinder.site":
        "Cheap Ticket Finder টিকিট বিক্রি করে না। চূড়ান্ত দাম এয়ারলাইন বা বুকিং সাইটে। cheapticketfinder.site",
    "Hotels": "হোটেল", "Packages": "প্যাকেজ", "Travel eSIM": "ট্রাভেল eSIM", "About": "আমাদের সম্পর্কে",
    "Terms": "শর্তাবলি", "Privacy": "প্রাইভেসি", "Disclosure": "ডিসক্লোজার", "Select Airport": "এয়ারপোর্ট বাছুন",
    "Type a city, airport or country name.": "শহর, এয়ারপোর্ট বা দেশের নাম লিখুন।",
}
# Route-guide chips on the homepage point to the Bangla guides on this page
ROUTES = {
    "Dhaka to Bangkok cheap ticket": ("ঢাকা–ব্যাংকক সস্তা টিকিট", "dhaka-to-bangkok-cheap-ticket"),
    "Dhaka to Cox's Bazar ticket price": ("ঢাকা–কক্সবাজার টিকিটের দাম", "dhaka-to-coxs-bazar-ticket-price"),
    "Dhaka to Kuala Lumpur cheap ticket": ("ঢাকা–কুয়ালালামপুর সস্তা টিকিট", "dhaka-to-kuala-lumpur-cheap-ticket"),
    "Dhaka to Kolkata cheap ticket": ("ঢাকা–কলকাতা সস্তা টিকিট", "dhaka-to-kolkata-cheap-ticket"),
    "Dhaka to Dubai cheap ticket": ("ঢাকা–দুবাই সস্তা টিকিট", "dhaka-to-dubai-cheap-ticket"),
    "Dhaka to Chattogram ticket price": ("ঢাকা–চট্টগ্রাম টিকিটের দাম", "dhaka-to-chattogram-ticket-price"),
    "Dhaka to Singapore cheap ticket": ("ঢাকা–সিঙ্গাপুর সস্তা টিকিট", "dhaka-to-singapore-cheap-ticket"),
    "Dhaka to Delhi cheap ticket": ("ঢাকা–দিল্লি সস্তা টিকিট", "dhaka-to-delhi-cheap-ticket"),
    "Dhaka to Kathmandu cheap ticket": ("ঢাকা–কাঠমান্ডু সস্তা টিকিট", "dhaka-to-kathmandu-cheap-ticket"),
    "Dhaka to Jeddah cheap ticket": ("ঢাকা–জেদ্দা সস্তা টিকিট", "dhaka-to-jeddah-cheap-ticket"),
    "Dhaka to Doha cheap ticket": ("ঢাকা–দোহা সস্তা টিকিট", "dhaka-to-doha-cheap-ticket"),
    "Dhaka to London cheap ticket": ("ঢাকা–লন্ডন সস্তা টিকিট", "dhaka-to-london-cheap-ticket"),
    "Dhaka to Riyadh air ticket": ("ঢাকা–রিয়াদ বিমান টিকিট", "dhaka-to-riyadh-cheap-ticket"),
    "Dhaka to Muscat air ticket": ("ঢাকা–মাসকাট বিমান টিকিট", "dhaka-to-muscat-cheap-ticket"),
    "Dhaka to Kuwait air ticket": ("ঢাকা–কুয়েত বিমান টিকিট", "dhaka-to-kuwait-cheap-ticket"),
    "Dhaka to Maldives air ticket": ("ঢাকা–মালদ্বীপ বিমান টিকিট", "dhaka-to-maldives-cheap-ticket"),
    "Dhaka to Istanbul air ticket": ("ঢাকা–ইস্তানবুল বিমান টিকিট", "dhaka-to-istanbul-cheap-ticket"),
    "Dhaka to Sylhet air ticket price": ("ঢাকা–সিলেট বিমান ভাড়া", "dhaka-to-sylhet-air-ticket-price"),
    "Dhaka to Saidpur air ticket price": ("ঢাকা–সৈয়দপুর বিমান ভাড়া", "dhaka-to-saidpur-air-ticket-price"),
    "Dhaka to Jashore air ticket price": ("ঢাকা–যশোর বিমান ভাড়া", "dhaka-to-jashore-air-ticket-price"),
    "Dhaka to Rajshahi air ticket price": ("ঢাকা–রাজশাহী বিমান ভাড়া", "dhaka-to-rajshahi-air-ticket-price"),
    "Dhaka to Barishal air ticket price": ("ঢাকা–বরিশাল বিমান ভাড়া", "dhaka-to-barishal-air-ticket-price"),
}
ATTR = {
    "Cheap Ticket Finder home": "Cheap Ticket Finder হোম", "Travel categories": "ভ্রমণের বিভাগ",
    "Fewer adults": "প্রাপ্তবয়স্ক কমান", "More adults": "প্রাপ্তবয়স্ক বাড়ান", "Fewer children": "শিশু কমান",
    "More children": "শিশু বাড়ান", "Fewer infants": "ইনফ্যান্ট কমান", "More infants": "ইনফ্যান্ট বাড়ান",
    "Close calendar": "ক্যালেন্ডার বন্ধ করুন", "Previous month": "আগের মাস", "Next month": "পরের মাস",
    "Explore by section": "বিভাগ অনুযায়ী দেখুন",
    "Type country, city, airport or IATA — e.g. India, CMB, DEL...": "দেশ, শহর, এয়ারপোর্ট বা কোড লিখুন — যেমন India, Dhaka, DEL...",
}
# User-facing strings inside the page's own script (string literals only)
JS = [
    ('{ flight: "Flight", remove: "Remove", origin: "From", dest: "To", date: "Departure date", airport: "City or airport" }',
     '{ flight: "ফ্লাইট", remove: "সরান", origin: "কোথা থেকে", dest: "কোথায়", date: "যাওয়ার তারিখ", airport: "শহর বা এয়ারপোর্ট" }'),
    ('Flight ${invalid + 1}: choose two different airports and a departure date in travel order.',
     'ফ্লাইট ${invalid + 1}-এর জন্য দুটি ভিন্ন এয়ারপোর্ট ও সঠিক ক্রমে যাত্রার তারিখ দিন।'),
    ("'Choose a From airport and a To airport.'", "'কোথা থেকে আর কোথায় — দুটো এয়ারপোর্টই বাছুন।'"),
    ("'Departure and destination airports must be different.'", "'যাওয়া আর গন্তব্যের এয়ারপোর্ট আলাদা হতে হবে।'"),
    ("'For Multi-City, the third airport must be different from the first two airports.'", "'মাল্টি-সিটিতে তৃতীয় এয়ারপোর্ট প্রথম দুটি থেকে আলাদা হতে হবে।'"),
    ("'Pick a return date (or choose One Way).'", "'ফেরার তারিখ বাছুন (অথবা ওয়ান ওয়ে বাছুন)।'"),
    ("'Pick a departure date.'", "'যাওয়ার তারিখ বাছুন।'"),
    ("'Now pick a return date (or choose One Way).'", "'এবার ফেরার তারিখ বাছুন (অথবা ওয়ান ওয়ে বাছুন)।'"),
    ("'Dates before departure are unavailable.'", "'যাওয়ার তারিখের আগের দিন বাছা যাবে না।'"),
    ("'Return date' : 'Departure date'", "'ফেরার তারিখ' : 'যাওয়ার তারিখ'"),
    ("'Select date'", "'তারিখ বাছুন'"),
    ("'Type a city, airport or country name.'", "'শহর, এয়ারপোর্ট বা দেশের নাম লিখুন।'"),
    ("' traveller' : ' travellers'", "' জন যাত্রী' : ' জন যাত্রী'"),
    ("'1 adult · '", "'১ জন প্রাপ্তবয়স্ক · '"),
    (">Flight search</div>", ">ফ্লাইট সার্চ</div>"),
    (">Live flight prices</h3>", ">লাইভ ফ্লাইটের দাম</h3>"),
    ("Prices come live from our partner Aviasales. We never make up a fare. The final total is confirmed on the booking site.",
     "দাম আসে সরাসরি আমাদের পার্টনার Aviasales থেকে। আমরা কখনো দাম বানাই না। চূড়ান্ত মোট দাম বুকিং সাইটে নিশ্চিত হয়।"),
    (">Book directly with an airline or a Bangladeshi travel site</h3>", ">সরাসরি এয়ারলাইন বা বাংলাদেশি ট্রাভেল সাইটে বুক করুন</h3>"),
    (">Card &amp; promo offers shown beside each site</span>", ">প্রতিটি সাইটের পাশে কার্ড ও প্রোমো অফার</span>"),
    ("Airline websites sometimes show a pricier fare type first (for example “Flex”), so compare the total with the live prices above. Use these buttons if you have a promo code or a bank card offer for that site.",
     "এয়ারলাইনের সাইট অনেক সময় আগে বেশি দামের ভাড়া (যেমন “Flex”) দেখায়, তাই উপরের লাইভ দামের সাথে মোট দাম তুলনা করুন। সেই সাইটের প্রোমো কোড বা ব্যাংক কার্ড অফার থাকলে এই বোতামগুলো ব্যবহার করুন।"),
    (">official source</a>", ">অফিসিয়াল সূত্র</a>"),
    ('btnText.innerText = "Search"', 'btnText.innerText = "খুঁজুন"'),
    ("'City or airport'", "'শহর বা এয়ারপোর্ট'"),
]

# Text produced by js/booking-links.js after a search; translated on the Bangla page only.
DYNAMIC = {
    "Also compare on Aviasales": "Aviasales-এও তুলনা করুন",
    "Live fare is on Aviasales — we do not invent a fare.": "লাইভ দাম Aviasales-এ — আমরা দাম বানাই না।",
    "may show Flex first": "আগে Flex দেখাতে পারে",
    "Copy": "কপি",
    "Open Google Hotels": "Google Hotels খুলুন", "Open Booking.com": "Booking.com খুলুন",
    "Open GoZayaan with your dates": "আপনার তারিখে GoZayaan খুলুন",
    "Open ShareTrip home, then enter the EBL code": "ShareTrip খুলুন, তারপর EBL কোড দিন",
    "Open official packages": "অফিসিয়াল প্যাকেজ খুলুন",
    "same flight, other country site": "একই ফ্লাইট, অন্য দেশের সাইট",
}
# Pattern rules for generated labels (percent figures are copied through unchanged)
DYN_RULES = [
    [r"^Compare on Trip\.com (.+) \((\w+)\)$", "Trip.com $1 সাইটে দাম দেখুন ($2)"],
    [r"^Open (.+) official site$", "$1-এর অফিসিয়াল সাইট খুলুন"],
    [r"^Open (.+) official booking$", "$1-এর অফিসিয়াল বুকিং খুলুন"],
    [r"^Open (.+) booking$", "$1 বুকিং খুলুন"],
    [r"^(.+): official up to (\d+)% on this OTA$", "$1: এই সাইটে অফিসিয়াল ছাড় সর্বোচ্চ $2%"],
    [r"^(.+): official up to (\d+)% at (.+) checkout$", "$1: $3 চেকআউটে অফিসিয়াল ছাড় সর্বোচ্চ $2%"],
    [r"^(.+): official up to (\d+)% at airline checkout$", "$1: এয়ারলাইন চেকআউটে অফিসিয়াল ছাড় সর্বোচ্চ $2%"],
    [r"^(.+): (\d+)% at airline checkout$", "$1: এয়ারলাইন চেকআউটে $2% ছাড়"],
    [r"^Stay in (.+) from (\S+) to (\S+)\. (.*)$", "$1-এ থাকা: $2 থেকে $3। $4"],
]

def main():
    t = open(SRC, encoding="utf-8").read()
    head_end = t.index("</head>")
    head, body = t[:head_end], t[head_end:]

    # --- head: language, title, description, canonical, hreflang
    head = head.replace('<html lang="en">', '<html lang="bn">', 1)
    head = re.sub(r"<title>[^<]*</title>", "<title>সস্তা বিমান টিকিট — বাংলাদেশ থেকে দাম তুলনা করুন | Cheap Ticket Finder</title>", head, count=1)
    bn_desc = "বাংলাদেশ থেকে সস্তা বিমান টিকিট খুঁজুন: রুট ও তারিখ দিয়ে পার্টনার সাইটের লাইভ দাম তুলনা করুন। আমরা টিকিট বিক্রি করি না, বানানো দামও দেখাই না।"
    head = re.sub(r'(<meta name="description" content=")[^"]*(")', r"\g<1>" + bn_desc + r"\2", head, count=1)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*(")', r"\g<1>" + bn_desc + r"\2", head, count=1)
    head = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', r"\g<1>" + bn_desc + r"\2", head, count=1)
    head = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*(")', r"\1সস্তা বিমান টিকিট — বাংলাদেশ থেকে দাম তুলনা করুন\2", head)
    head = head.replace('<link rel="canonical" href="https://cheapticketfinder.site/">', '<link rel="canonical" href="https://cheapticketfinder.site/bn/">', 1)
    head = head.replace('<meta property="og:url" content="https://cheapticketfinder.site/">', '<meta property="og:url" content="https://cheapticketfinder.site/bn/">', 1)
    head = head.replace('"inLanguage": "en"', '"inLanguage": "bn"')

    # relative script paths must become absolute on /bn/
    body = body.replace('src="js/', 'src="/js/')
    head = head.replace('src="js/', 'src="/js/')

    # --- body: switch link in the top bar becomes "English"
    body = body.replace('<nav class="top-bar" aria-label="Contact">\n',
                        '<nav class="top-bar" aria-label="Contact">\n                <a href="/" hreflang="en" lang="en" title="English version">English</a>\n', 1)
    # The Bangla-guide chips on the English homepage are redundant here (the main chips already go to /bn/)
    body = re.sub(r'\n\s*<p class="[^"]*" lang="bn">বাংলায় রুট গাইড:</p>\s*<nav [^>]*lang="bn">.*?</nav>', "", body, count=1, flags=re.S)

    # remove the English copy of the FAQ (the Bangla FAQ right below it stays)
    body, n = re.subn(r'<h2 id="cheap-guide-h"[^>]*>How can I find a cheap air ticket from Bangladesh\?</h2>\s*<p>Search with flexible dates.*?</p>\s*', "", body, count=1, flags=re.S)
    assert n == 1, "English FAQ block not found"
    body = body.replace('class="text-base font-bold text-sky-400 mt-3" lang="bn">', 'id="cheap-guide-h" class="text-base font-bold text-sky-400" lang="bn">', 1)

    # route chips -> Bangla guides
    for en, (bn, slug) in ROUTES.items():
        body = body.replace(f'href="/{slug}/">{en}</a>', f'href="/bn/{slug}/">{bn}</a>')
    body = body.replace('href="/how-to-find-cheap-air-tickets/">Read the 7-step guide', 'href="/bn/how-to-find-cheap-air-tickets/">Read the 7-step guide')

    # translate the page's own script strings
    for a, b in JS:
        body = body.replace(a, b)

    # translate visible text nodes outside <script>/<style>
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", body, flags=re.S)
    def tx(m):
        lead, txt, trail = m.group(1), m.group(2), m.group(3)
        key = __import__("html").unescape(txt)
        return f">{lead}{TEXT[key] if key in TEXT else txt}{trail}<"
    for i, part in enumerate(parts):
        if part.startswith("<script") or part.startswith("<style"):
            continue
        part = re.sub(r">(\s*)([^<>]*?[A-Za-z][^<>]*?)(\s*)<", tx, part)
        for k, v in ATTR.items():
            for attr in ("aria-label", "placeholder", "title"):
                part = part.replace(f'{attr}="{k}"', f'{attr}="{v}"')
        parts[i] = part
    body = "".join(parts)

    # dynamic results text (from js/booking-links.js) -> Bangla, after each render
    dyn = "<script>(function(){var M=" + __import__("json").dumps(DYNAMIC, ensure_ascii=False) + r""";
var R=""" + __import__("json").dumps(DYN_RULES, ensure_ascii=False) + r""".map(function(r){return [new RegExp(r[0]),r[1]];});
function tr(s){if(M[s])return M[s];for(var i=0;i<R.length;i++){if(R[i][0].test(s))return s.replace(R[i][0],R[i][1]);}return null;}
function walk(n){if(n.nodeType===3){var s=n.nodeValue.trim();var v=s&&tr(s);if(v)n.nodeValue=n.nodeValue.replace(s,v);return;}
if(n.nodeType===1&&!/^(SCRIPT|STYLE)$/.test(n.tagName))for(var c=n.firstChild;c;c=c.nextSibling)walk(c);}
var ids=['googleBookBar','cheapPathResults','hotelSectionWrapper','nearbyAirportSection'];
var mo=new MutationObserver(function(){ids.forEach(function(i){var e=document.getElementById(i);if(e)walk(e);});});
var H=document.documentElement;new MutationObserver(function(){if(H.lang!=='bn')H.lang='bn';}).observe(H,{attributes:true,attributeFilter:['lang']});
document.addEventListener('DOMContentLoaded',function(){ids.forEach(function(i){var e=document.getElementById(i);if(e)mo.observe(e,{childList:true,subtree:true});});});})();</script>
</body>"""
    body = body.replace("</body>", dyn, 1)

    out = head + body
    open(OUT, "w", encoding="utf-8").write(out)
    left = [k for k in TEXT if re.search(r">\s*" + re.escape(k) + r"\s*<", re.sub(r"<script\b.*?</script>", "", out, flags=re.S))]
    print("wrote", OUT, "| untranslated keys left:", left[:10])

if __name__ == "__main__":
    main()
