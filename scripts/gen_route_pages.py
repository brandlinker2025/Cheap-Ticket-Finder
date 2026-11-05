#!/usr/bin/env python3
"""Generate route guide pages (English + Bangla) from ROUTES data.

Add-only: writes new folders; never touches existing English route pages.
Run from repo root:  python3 scripts/gen_route_pages.py
"""
import html, json, os

SITE = "https://cheapticketfinder.site"
UPDATED_EN = "2 November 2026 (Asia/Dhaka)"
UPDATED_BN = "২ নভেম্বর ২০২৬"
TRIP = "Allianceid=11059812&SID=333836392&trip_sub3=D20343143"

# new=True -> also generate the English page (existing English pages are left untouched)
ROUTES = [
    dict(slug="dhaka-to-singapore-cheap-ticket", new=True, city="Singapore", city_bn="সিঙ্গাপুর", code="DAC → SIN",
         desc="Dhaka to Singapore (DAC–SIN) cheap ticket guide: compare non-stop and one-stop fares, baggage and total cost with flexible dates.",
         intro="Singapore is one of the busiest routes from Dhaka for work, study, medical visits and transit. Non-stop and one-stop options can differ a lot in total cost once baggage is added.",
         intro_bn="কাজ, পড়াশোনা, চিকিৎসা ও ট্রানজিটের জন্য ঢাকা থেকে সিঙ্গাপুর অন্যতম ব্যস্ত রুট। ব্যাগেজ যোগ করলে ননস্টপ আর এক-স্টপ ফ্লাইটের মোট দামে অনেক পার্থক্য হতে পারে।",
         airlines="Non-stop service has been operated by Biman Bangladesh, US-Bangla and Singapore Airlines. One-stop options via Kuala Lumpur or Bangkok can be cheaper on some dates, but check total travel time.",
         airlines_bn="এই রুটে বিমান বাংলাদেশ, ইউএস-বাংলা ও সিঙ্গাপুর এয়ারলাইনস ননস্টপ ফ্লাইট চালিয়েছে। কিছু তারিখে কুয়ালালামপুর বা ব্যাংকক হয়ে এক-স্টপ ফ্লাইট সস্তা হতে পারে, তবে মোট সময় দেখে নিন।",
         tips=["Compare non-stop with one-stop via KUL or BKK — a cheaper connection may add many hours.",
               "Workers on employment passes: check the airline's baggage rules for heavier checked bags.",
               "Changi transit is smooth, but separate tickets on low-cost carriers do not protect missed connections."],
         tips_bn=["ননস্টপের সাথে KUL বা BKK হয়ে এক-স্টপ তুলনা করুন — সস্তা কানেকশনে অনেক ঘণ্টা বেশি লাগতে পারে।",
                  "কাজের ভিসায় গেলে বেশি ব্যাগেজের নিয়ম এয়ারলাইনের সাইটে দেখে নিন।",
                  "আলাদা আলাদা টিকিটে কানেকশন মিস হলে এয়ারলাইন দায় নেয় না।"],
         entry="Confirm Singapore entry requirements (visa, SG Arrival Card) and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে সিঙ্গাপুরের ভিসা, SG Arrival Card ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-delhi-cheap-ticket", new=True, city="Delhi", city_bn="দিল্লি", code="DAC → DEL",
         desc="Dhaka to Delhi (DAC–DEL) cheap ticket guide: compare direct and via-Kolkata fares, baggage and total cost with flexible dates.",
         intro="Delhi is a common route for medical treatment, study and business. Direct flights are convenient; routing via Kolkata is sometimes cheaper but takes longer.",
         intro_bn="চিকিৎসা, পড়াশোনা ও ব্যবসার জন্য ঢাকা–দিল্লি জনপ্রিয় রুট। সরাসরি ফ্লাইট সুবিধাজনক; কলকাতা হয়ে গেলে কখনো সস্তা হয়, তবে সময় বেশি লাগে।",
         airlines="IndiGo and Air India have operated Dhaka to Delhi flights. Connecting itineraries via Kolkata are also common, so compare total time and baggage.",
         airlines_bn="ইন্ডিগো ও এয়ার ইন্ডিয়া ঢাকা–দিল্লি ফ্লাইট চালিয়েছে। কলকাতা হয়ে কানেকশনও প্রচলিত, তাই মোট সময় ও ব্যাগেজ তুলনা করুন।",
         tips=["Medical travellers: pick flights with enough buffer before hospital appointments.",
               "Compare the direct fare with DAC–CCU + CCU–DEL on one ticket.",
               "Low-cost fares often include only cabin baggage — add checked bags before comparing totals."],
         tips_bn=["চিকিৎসার জন্য গেলে হাসপাতালের অ্যাপয়েন্টমেন্টের আগে যথেষ্ট সময় রেখে ফ্লাইট নিন।",
                  "সরাসরি ভাড়ার সাথে এক টিকিটে DAC–CCU–DEL তুলনা করুন।",
                  "লো-কস্ট ভাড়ায় অনেক সময় শুধু কেবিন ব্যাগ থাকে — চেকড ব্যাগ যোগ করে মোট দাম দেখুন।"],
         entry="Confirm India visa type (tourist or medical) and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে ভারতের ভিসার ধরন (টুরিস্ট বা মেডিকেল) ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-kathmandu-cheap-ticket", new=True, city="Kathmandu", city_bn="কাঠমান্ডু", code="DAC → KTM",
         desc="Dhaka to Kathmandu (DAC–KTM) cheap ticket guide: compare short-haul fares, baggage and total cost with flexible dates.",
         intro="Kathmandu is a short, popular holiday route from Dhaka, especially in the dry season. Fares can rise quickly around holidays, so flexible dates help.",
         intro_bn="ঢাকা থেকে কাঠমান্ডু ছোট ও জনপ্রিয় ছুটির রুট, বিশেষ করে শুকনো মৌসুমে। ছুটির সময় ভাড়া দ্রুত বাড়ে, তাই তারিখ নমনীয় রাখুন।",
         airlines="Biman Bangladesh, US-Bangla and Himalaya Airlines have operated non-stop flights on this route. Check which carriers fly on your dates in the search.",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা ও হিমালয়া এয়ারলাইনস এই রুটে ননস্টপ ফ্লাইট চালিয়েছে। আপনার তারিখে কে চলছে সার্চে দেখে নিন।",
         tips=["Peak periods (Eid, winter holidays) sell out early — compare nearby dates.",
               "Weather in Kathmandu can delay flights; avoid tight onward plans on the same day.",
               "Trekking gear is heavy — check checked-baggage allowance before choosing the cheapest fare."],
         tips_bn=["ঈদ ও শীতের ছুটিতে আগেই সিট শেষ হয় — আশেপাশের তারিখ তুলনা করুন।",
                  "আবহাওয়ার কারণে কাঠমান্ডুতে ফ্লাইট দেরি হতে পারে; একই দিনে টাইট প্ল্যান রাখবেন না।",
                  "ট্রেকিং গিয়ার ভারী — সস্তা ভাড়া বাছার আগে চেকড ব্যাগেজ দেখুন।"],
         entry="Confirm Nepal entry rules for Bangladeshi passport holders and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে বাংলাদেশি পাসপোর্টধারীদের জন্য নেপালের প্রবেশের নিয়ম ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-jeddah-cheap-ticket", new=True, city="Jeddah", city_bn="জেদ্দা", code="DAC → JED",
         desc="Dhaka to Jeddah (DAC–JED) cheap ticket guide for Umrah and work travel: compare fares, baggage and total cost with flexible dates.",
         intro="Jeddah is a key route for Umrah pilgrims and workers in Saudi Arabia. Fares swing a lot around Ramadan and Hajj season, and baggage rules matter on this route.",
         intro_bn="উমরাহ যাত্রী ও সৌদি আরবে কর্মরতদের জন্য ঢাকা–জেদ্দা গুরুত্বপূর্ণ রুট। রমজান ও হজ মৌসুমে ভাড়া অনেক ওঠানামা করে, আর এই রুটে ব্যাগেজের নিয়ম খুব জরুরি।",
         airlines="Biman Bangladesh, Saudia and US-Bangla have operated non-stop flights, and Saudi low-cost carriers such as flynas and flyadeal have also served Dhaka. One-stop options via Gulf hubs are common.",
         airlines_bn="বিমান বাংলাদেশ, সৌদিয়া ও ইউএস-বাংলা ননস্টপ ফ্লাইট চালিয়েছে; ফ্লাইনাস ও ফ্লাইএডিলের মতো সৌদি লো-কস্ট এয়ারলাইনও ঢাকায় এসেছে। উপসাগরীয় হাব হয়ে এক-স্টপ ফ্লাইটও প্রচলিত।",
         tips=["Umrah travellers: Zamzam water rules differ by airline — check before you fly back.",
               "Compare fares into Jeddah and Madinah; an open-jaw ticket can fit Umrah plans better.",
               "Low-cost Saudi carriers may charge extra for checked bags — compare the full total."],
         tips_bn=["উমরাহ যাত্রী: জমজম পানি আনার নিয়ম এয়ারলাইনভেদে আলাদা — ফেরার আগে দেখে নিন।",
                  "জেদ্দা ও মদিনা দুই জায়গার ভাড়া তুলনা করুন; ওপেন-জ টিকিট উমরাহ পরিকল্পনায় সুবিধাজনক হতে পারে।",
                  "সৌদি লো-কস্ট এয়ারলাইনে চেকড ব্যাগের জন্য আলাদা টাকা লাগতে পারে — মোট দাম তুলনা করুন।"],
         entry="Confirm Saudi visa type (Umrah, work or visit) and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে সৌদি ভিসার ধরন (উমরাহ, কাজ বা ভিজিট) ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-doha-cheap-ticket", new=True, city="Doha", city_bn="দোহা", code="DAC → DOH",
         desc="Dhaka to Doha (DAC–DOH) cheap ticket guide: compare fares, baggage and total cost with flexible dates.",
         intro="Doha is both a destination for workers in Qatar and a major transit hub to Europe, Africa and the Americas. Prices vary by season and fare family.",
         intro_bn="দোহা কাতারে কর্মরতদের গন্তব্য এবং ইউরোপ, আফ্রিকা ও আমেরিকায় যাওয়ার বড় ট্রানজিট হাব। মৌসুম ও ভাড়ার ধরন অনুযায়ী দাম বদলায়।",
         airlines="Qatar Airways, Biman Bangladesh and US-Bangla have operated non-stop flights on this route. Compare their baggage allowances for your fare.",
         airlines_bn="কাতার এয়ারওয়েজ, বিমান বাংলাদেশ ও ইউএস-বাংলা এই রুটে ননস্টপ ফ্লাইট চালিয়েছে। আপনার ভাড়ায় ব্যাগেজ কত, তুলনা করুন।",
         tips=["If Doha is only a transit point, search your final destination instead — a through ticket is often cheaper.",
               "Workers: compare fare families with 30 kg+ checked baggage.",
               "Avoid Eid peaks when possible; compare a few days before and after."],
         tips_bn=["দোহা শুধু ট্রানজিট হলে চূড়ান্ত গন্তব্য সার্চ করুন — এক টিকিটে প্রায়ই সস্তা হয়।",
                  "কর্মীরা ৩০ কেজি বা বেশি চেকড ব্যাগেজের ভাড়া তুলনা করুন।",
                  "সম্ভব হলে ঈদের ভিড় এড়িয়ে আগে-পরের কয়েকটি দিন তুলনা করুন।"],
         entry="Confirm Qatar entry/visa requirements and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে কাতারের ভিসা/প্রবেশের নিয়ম ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-london-cheap-ticket", new=True, city="London", city_bn="লন্ডন", code="DAC → LON",
         desc="Dhaka to London (DAC–LHR/LGW/STN) cheap ticket guide: compare non-stop and one-stop fares, baggage and total cost with flexible dates.",
         intro="London is the main long-haul route for the British-Bangladeshi community and students. One-stop fares via Gulf or Turkish hubs often compete with non-stop flights.",
         intro_bn="ব্রিটিশ-বাংলাদেশি কমিউনিটি ও শিক্ষার্থীদের জন্য লন্ডন প্রধান দূরপাল্লার রুট। উপসাগরীয় বা তুর্কি হাব হয়ে এক-স্টপ ভাড়া প্রায়ই ননস্টপের সাথে প্রতিযোগিতা করে।",
         airlines="Biman Bangladesh operates non-stop flights to London Heathrow. One-stop options via Dubai, Doha, Istanbul and other hubs are widely available — compare total time and baggage.",
         airlines_bn="বিমান বাংলাদেশ লন্ডন হিথ্রোতে ননস্টপ ফ্লাইট চালায়। দুবাই, দোহা, ইস্তানবুলসহ অন্যান্য হাব হয়ে এক-স্টপ ফ্লাইটও অনেক — মোট সময় ও ব্যাগেজ তুলনা করুন।",
         tips=["Search all London airports together (Heathrow, Gatwick, Stansted, Luton) — the search tool does this for London.",
               "Students: look for fare families with extra baggage and flexible changes.",
               "December and summer holidays are peak — compare several weeks if your dates are flexible."],
         tips_bn=["লন্ডনের সব এয়ারপোর্ট (হিথ্রো, গ্যাটউইক, স্ট্যানস্টেড, লুটন) একসাথে সার্চ করুন — আমাদের টুল লন্ডনের জন্য এটা করে।",
                  "শিক্ষার্থীরা বেশি ব্যাগেজ ও তারিখ বদলানোর সুবিধাসহ ভাড়া দেখুন।",
                  "ডিসেম্বর ও গ্রীষ্মের ছুটি পিক সময় — তারিখ নমনীয় হলে কয়েক সপ্তাহ তুলনা করুন।"],
         entry="Confirm UK visa and passport validity from official UK government sources before booking. Transit through a hub country may need its own transit rules.",
         entry_bn="বুকিংয়ের আগে যুক্তরাজ্যের ভিসা ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন। ট্রানজিট দেশের নিয়মও আলাদা হতে পারে।"),
    dict(slug="dhaka-to-riyadh-cheap-ticket", new=True, city="Riyadh", city_bn="রিয়াদ", code="DAC → RUH",
         desc="Dhaka to Riyadh (DAC–RUH) air ticket guide for workers and visitors: compare non-stop and one-stop fares, baggage and total cost with flexible dates.",
         intro="Riyadh is one of the busiest routes for Bangladeshi workers in Saudi Arabia. Fares rise sharply around Eid and the end of Ramadan, and checked-baggage allowance matters a lot on this route.",
         intro_bn="সৌদি আরবে কর্মরত বাংলাদেশিদের জন্য ঢাকা–রিয়াদ অন্যতম ব্যস্ত রুট। ঈদ ও রমজানের শেষে ভাড়া অনেক বাড়ে, আর এই রুটে চেকড ব্যাগেজ খুব গুরুত্বপূর্ণ।",
         airlines="Biman Bangladesh, US-Bangla and Saudia are listed as flying Dhaka to Riyadh non-stop. One-stop options via Gulf hubs are also common.",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা ও সৌদিয়া ঢাকা–রিয়াদ ননস্টপ ফ্লাইট চালায় বলে তালিকাভুক্ত। উপসাগরীয় হাব হয়ে এক-স্টপ ফ্লাইটও প্রচলিত।",
         tips=["Workers: compare fare families with 30 kg or more checked baggage before choosing the cheapest fare.",
               "Avoid the week before Eid if you can — compare a few days before and after.",
               "Check the arrival terminal at King Khalid International (RUH) for your airline."],
         tips_bn=["কর্মীরা সস্তা ভাড়া বাছার আগে ৩০ কেজি বা বেশি চেকড ব্যাগেজসহ ভাড়া তুলনা করুন।",
                  "সম্ভব হলে ঈদের আগের সপ্তাহ এড়িয়ে আগে-পরের কয়েকটি দিন তুলনা করুন।",
                  "আপনার এয়ারলাইন রিয়াদ (RUH) এয়ারপোর্টের কোন টার্মিনালে নামে দেখে নিন।"],
         entry="Confirm your Saudi visa type (work, Umrah or visit) and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে সৌদি ভিসার ধরন (কাজ, উমরাহ বা ভিজিট) ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-muscat-cheap-ticket", new=True, city="Muscat", city_bn="মাসকাট", code="DAC → MCT",
         desc="Dhaka to Muscat (DAC–MCT) air ticket guide: compare full-service and low-cost fares, baggage and total cost with flexible dates.",
         intro="Muscat is a key route for Bangladeshi workers in Oman. Both full-service and low-cost airlines fly it, so the cheapest headline fare is not always the cheapest total once baggage is added.",
         intro_bn="ওমানে কর্মরত বাংলাদেশিদের জন্য ঢাকা–মাসকাট গুরুত্বপূর্ণ রুট। ফুল-সার্ভিস ও লো-কস্ট দুই ধরনের এয়ারলাইন চলে, তাই ব্যাগেজ যোগ করলে সবচেয়ে কম দেখানো ভাড়া সবসময় সবচেয়ে সস্তা নয়।",
         airlines="Biman Bangladesh, US-Bangla, Oman Air and SalamAir (low-cost) are listed as flying Dhaka to Muscat. Compare baggage on each fare before you buy.",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা, ওমান এয়ার ও সালাম এয়ার (লো-কস্ট) ঢাকা–মাসকাট ফ্লাইট চালায় বলে তালিকাভুক্ত। কেনার আগে প্রতিটি ভাড়ার ব্যাগেজ তুলনা করুন।",
         tips=["Low-cost fares may include little or no checked baggage — add it before comparing totals.",
               "Compare a few dates around your plan; Eid weeks are the most expensive.",
               "If Muscat is only a transit point, search your final destination instead."],
         tips_bn=["লো-কস্ট ভাড়ায় চেকড ব্যাগ কম বা না-ও থাকতে পারে — যোগ করে মোট দাম দেখুন।",
                  "আশেপাশের কয়েকটি তারিখ তুলনা করুন; ঈদের সপ্তাহ সবচেয়ে দামি।",
                  "মাসকাট শুধু ট্রানজিট হলে চূড়ান্ত গন্তব্য সার্চ করুন।"],
         entry="Confirm Oman visa requirements and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে ওমানের ভিসার নিয়ম ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-kuwait-cheap-ticket", new=True, city="Kuwait", city_bn="কুয়েত", code="DAC → KWI",
         desc="Dhaka to Kuwait (DAC–KWI) air ticket guide: compare fares, baggage and total cost with flexible dates.",
         intro="Kuwait City is a major work destination for Bangladeshis. Fares change a lot by season, so flexible dates and a careful baggage check help most.",
         intro_bn="কুয়েত বাংলাদেশিদের বড় কর্মস্থল। মৌসুম অনুযায়ী ভাড়া অনেক বদলায়, তাই নমনীয় তারিখ আর ব্যাগেজ ভালো করে দেখা সবচেয়ে কাজে দেয়।",
         airlines="Biman Bangladesh, Kuwait Airways and Jazeera Airways (low-cost) are listed as flying Dhaka to Kuwait. One-stop options via other Gulf hubs are also available.",
         airlines_bn="বিমান বাংলাদেশ, কুয়েত এয়ারওয়েজ ও জাজিরা এয়ারওয়েজ (লো-কস্ট) ঢাকা–কুয়েত ফ্লাইট চালায় বলে তালিকাভুক্ত। অন্য উপসাগরীয় হাব হয়ে এক-স্টপ ফ্লাইটও আছে।",
         tips=["Compare the low-cost fare with baggage added against a full-service fare.",
               "Workers: check how many kilograms are included before you pay.",
               "Compare a few days around Eid — prices jump close to the holiday."],
         tips_bn=["ব্যাগেজ যোগ করে লো-কস্ট ভাড়ার সাথে ফুল-সার্ভিস ভাড়া তুলনা করুন।",
                  "কর্মীরা পেমেন্টের আগে কত কেজি ব্যাগেজ আছে দেখে নিন।",
                  "ঈদের আশেপাশে কয়েকটি দিন তুলনা করুন — ছুটির কাছে দাম বাড়ে।"],
         entry="Confirm Kuwait visa requirements and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে কুয়েতের ভিসার নিয়ম ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-maldives-cheap-ticket", new=True, city="Maldives (Malé)", city_bn="মালদ্বীপ (মালে)", code="DAC → MLE",
         desc="Dhaka to Maldives (DAC–MLE) air ticket guide: compare non-stop and one-stop fares to Malé, baggage and total cost with flexible dates.",
         intro="The Maldives is a popular holiday and work destination from Dhaka. Non-stop flights are short, but resort transfers from Malé can cost as much as the flight, so plan the total.",
         intro_bn="ঢাকা থেকে মালদ্বীপ জনপ্রিয় ছুটি ও কাজের গন্তব্য। ননস্টপ ফ্লাইট ছোট, কিন্তু মালে থেকে রিসোর্টে যাওয়ার খরচ ফ্লাইটের সমান হতে পারে, তাই মোট খরচ হিসাব করুন।",
         airlines="US-Bangla and Maldivian are listed as flying Dhaka to Malé non-stop. One-stop options via Colombo and other hubs are also available.",
         airlines_bn="ইউএস-বাংলা ও মালদিভিয়ান ঢাকা–মালে ননস্টপ ফ্লাইট চালায় বলে তালিকাভুক্ত। কলম্বোসহ অন্য হাব হয়ে এক-স্টপ ফ্লাইটও আছে।",
         tips=["Check your resort's transfer (speedboat or seaplane) cost and timing before booking flights.",
               "Seaplanes usually fly only in daylight — late arrivals may need a night in Malé.",
               "Compare the full trip cost: flight + transfer + hotel."],
         tips_bn=["ফ্লাইট বুকের আগে রিসোর্টের ট্রান্সফার (স্পিডবোট বা সি-প্লেন) খরচ ও সময় দেখে নিন।",
                  "সি-প্লেন সাধারণত দিনের আলোতেই চলে — দেরিতে নামলে মালেতে এক রাত থাকতে হতে পারে।",
                  "পুরো খরচ তুলনা করুন: ফ্লাইট + ট্রান্সফার + হোটেল।"],
         entry="Confirm Maldives entry rules (including hotel booking and return ticket) and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে মালদ্বীপে প্রবেশের নিয়ম (হোটেল বুকিং ও ফিরতি টিকিটসহ) ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-istanbul-cheap-ticket", new=True, city="Istanbul", city_bn="ইস্তানবুল", code="DAC → IST",
         desc="Dhaka to Istanbul (DAC–IST) air ticket guide: compare non-stop and one-stop fares, baggage and total cost with flexible dates.",
         intro="Istanbul is both a holiday destination and a major connection point to Europe and the Americas. Non-stop and one-stop fares can differ a lot, so compare total time and price.",
         intro_bn="ইস্তানবুল ছুটির গন্তব্য এবং ইউরোপ-আমেরিকা যাওয়ার বড় কানেকশন পয়েন্ট। ননস্টপ ও এক-স্টপ ভাড়ায় অনেক পার্থক্য হয়, তাই মোট সময় ও দাম তুলনা করুন।",
         airlines="Turkish Airlines is listed as flying Dhaka to Istanbul non-stop. One-stop options via Gulf hubs are widely available.",
         airlines_bn="টার্কিশ এয়ারলাইনস ঢাকা–ইস্তানবুল ননস্টপ ফ্লাইট চালায় বলে তালিকাভুক্ত। উপসাগরীয় হাব হয়ে এক-স্টপ ফ্লাইটও অনেক।",
         tips=["Istanbul has two airports (IST and SAW) — check which one your ticket uses.",
               "If Istanbul is only a transit point, search your final destination for a through ticket.",
               "Long layovers may allow a city visit, but check transit visa rules first."],
         tips_bn=["ইস্তানবুলে দুটি এয়ারপোর্ট (IST ও SAW) — আপনার টিকিট কোনটায় দেখে নিন।",
                  "ইস্তানবুল শুধু ট্রানজিট হলে চূড়ান্ত গন্তব্য সার্চ করে এক টিকিটে কিনুন।",
                  "লম্বা লে-ওভারে শহর ঘোরা যায়, তবে আগে ট্রানজিট ভিসার নিয়ম দেখুন।"],
         entry="Confirm Türkiye visa (or e-Visa eligibility) and passport validity from official sources before booking.",
         entry_bn="বুকিংয়ের আগে তুরস্কের ভিসা (বা ই-ভিসার যোগ্যতা) ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-guangzhou-cheap-ticket", new=True, city="Guangzhou", city_bn="গুয়াংজু", code="DAC → CAN",
         desc="Dhaka to Guangzhou (DAC–CAN) air ticket guide: compare non-stop fares on Biman, China Southern and US-Bangla, baggage and total cost.",
         intro="Guangzhou is the busiest route from Bangladesh to China, used for business, wholesale buying, the Canton Fair, study and transit to other Chinese cities.",
         intro_bn="বাংলাদেশ থেকে চীনের সবচেয়ে ব্যস্ত রুট গুয়াংজু — ব্যবসা, পাইকারি কেনাকাটা, ক্যান্টন ফেয়ার, পড়াশোনা ও চীনের অন্য শহরে যাওয়ার জন্য।",
         airlines="Non-stop flights are listed on Biman Bangladesh, China Southern Airlines and (seasonally) US-Bangla. One-stop options via Kuala Lumpur, Bangkok or Hong Kong are also available.",
         airlines_bn="এই রুটে বিমান বাংলাদেশ, চায়না সাউদার্ন এয়ারলাইনস ও (মৌসুমি) ইউএস-বাংলার ননস্টপ ফ্লাইট তালিকাভুক্ত। কুয়ালালামপুর, ব্যাংকক বা হংকং হয়ে এক-স্টপ ফ্লাইটও আছে।",
         tips=["Canton Fair runs every spring and autumn — book early, fares rise near the fair dates.",
               "Traders carrying samples: check checked-baggage allowance before comparing fares.",
               "Going on to Yiwu or Shenzhen? Compare a through ticket with a separate train or domestic flight."],
         tips_bn=["ক্যান্টন ফেয়ার প্রতি বসন্ত ও শরতে হয় — আগে বুক করুন, ফেয়ারের কাছাকাছি ভাড়া বাড়ে।",
                  "ব্যবসার স্যাম্পল নিলে আগে চেকড ব্যাগেজের সীমা দেখে নিন।",
                  "ইউ বা শেনজেন যাবেন? এক টিকিটের সাথে আলাদা ট্রেন বা অভ্যন্তরীণ ফ্লাইট তুলনা করুন।"],
         entry="Confirm China visa requirements and passport validity from the Chinese embassy or visa centre before booking.",
         entry_bn="বুকিংয়ের আগে চীনের ভিসার নিয়ম ও পাসপোর্টের মেয়াদ চীনা দূতাবাস বা ভিসা সেন্টার থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-kunming-cheap-ticket", new=True, city="Kunming", city_bn="কুনমিং", code="DAC → KMG",
         desc="Dhaka to Kunming (DAC–KMG) air ticket guide: compare China Eastern non-stop fares, connections, baggage and total cost.",
         intro="Kunming is the closest major Chinese city to Bangladesh, with a short non-stop flight. It is used for study, business and onward connections across China.",
         intro_bn="কুনমিং বাংলাদেশের সবচেয়ে কাছের বড় চীনা শহর, ননস্টপ ফ্লাইটে অল্প সময় লাগে। পড়াশোনা, ব্যবসা ও চীনের অন্য শহরে যেতে এই রুট ব্যবহার হয়।",
         airlines="China Eastern Airlines is listed as flying Dhaka to Kunming non-stop. It also connects in Kunming to many Chinese cities.",
         airlines_bn="চায়না ইস্টার্ন এয়ারলাইনস ঢাকা–কুনমিং ননস্টপ ফ্লাইট চালায় বলে তালিকাভুক্ত। কুনমিং হয়ে চীনের অনেক শহরে কানেকশনও আছে।",
         tips=["Heading to Chengdu, Shanghai or Beijing? Compare a through ticket via Kunming with a non-stop to Guangzhou or Beijing.",
               "Students: check the baggage allowance for your first trip.",
               "Search a few days either side — the route has fewer flights, so dates matter."],
         tips_bn=["চেংদু, সাংহাই বা বেইজিং যাবেন? কুনমিং হয়ে এক টিকিটের সাথে গুয়াংজু বা বেইজিং ননস্টপ তুলনা করুন।",
                  "শিক্ষার্থীরা প্রথম যাত্রায় ব্যাগেজের সীমা দেখে নিন।",
                  "আগে-পরে কয়েক দিন সার্চ করুন — এই রুটে ফ্লাইট কম, তাই তারিখে দাম বদলায়।"],
         entry="Confirm China visa requirements and passport validity from the Chinese embassy or visa centre before booking.",
         entry_bn="বুকিংয়ের আগে চীনের ভিসার নিয়ম ও পাসপোর্টের মেয়াদ চীনা দূতাবাস বা ভিসা সেন্টার থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-beijing-cheap-ticket", new=True, city="Beijing", city_bn="বেইজিং", code="DAC → PEK/PKX",
         desc="Dhaka to Beijing (DAC–PEK/PKX) air ticket guide: compare Air China and China Southern non-stop fares, baggage and total cost.",
         intro="Beijing has non-stop flights from Dhaka to both of its airports. It is used for study, official visits, business and connections to northern China.",
         intro_bn="ঢাকা থেকে বেইজিংয়ের দুই এয়ারপোর্টেই ননস্টপ ফ্লাইট আছে। পড়াশোনা, অফিসিয়াল সফর, ব্যবসা ও উত্তর চীনে যাওয়ার জন্য এই রুট ব্যবহার হয়।",
         airlines="Air China is listed as flying Dhaka to Beijing Capital (PEK) and China Southern to Beijing Daxing (PKX), both non-stop.",
         airlines_bn="এয়ার চায়না ঢাকা–বেইজিং ক্যাপিটাল (PEK) এবং চায়না সাউদার্ন ঢাকা–বেইজিং দাশিং (PKX) ননস্টপ ফ্লাইট চালায় বলে তালিকাভুক্ত।",
         tips=["Beijing has two airports (PEK and PKX) far apart — check which one your ticket uses.",
               "Compare non-stop with one-stop via Guangzhou or Kunming on the same ticket.",
               "Winter in Beijing is very cold; pack for it if you travel December–February."],
         tips_bn=["বেইজিংয়ে দুটি এয়ারপোর্ট (PEK ও PKX), অনেক দূরে — টিকিট কোনটায় দেখে নিন।",
                  "ননস্টপের সাথে এক টিকিটে গুয়াংজু বা কুনমিং হয়ে এক-স্টপ তুলনা করুন।",
                  "ডিসেম্বর–ফেব্রুয়ারিতে বেইজিং খুব ঠান্ডা — সেই প্রস্তুতি নিন।"],
         entry="Confirm China visa requirements and passport validity from the Chinese embassy or visa centre before booking.",
         entry_bn="বুকিংয়ের আগে চীনের ভিসার নিয়ম ও পাসপোর্টের মেয়াদ চীনা দূতাবাস বা ভিসা সেন্টার থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-sylhet-air-ticket-price", new=True, domestic=True, city="Sylhet", city_bn="সিলেট", code="DAC → ZYL",
         desc="Dhaka to Sylhet (DAC–ZYL) air ticket price guide: compare domestic airlines, fare types and total cost with flexible dates.",
         intro="Dhaka to Sylhet is one of the busiest domestic routes, popular with travellers and families of expatriates. Weekend and holiday fares rise quickly.",
         intro_bn="ঢাকা–সিলেট দেশের অন্যতম ব্যস্ত ঘরোয়া রুট, ভ্রমণকারী ও প্রবাসী পরিবারের কাছে জনপ্রিয়। ছুটি ও সপ্তাহান্তে ভাড়া দ্রুত বাড়ে।",
         airlines="Biman Bangladesh, US-Bangla, Novoair and Air Astra are listed as flying Dhaka to Sylhet. Compare fare types and baggage for your date.",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা, নভোএয়ার ও এয়ার অ্যাস্ট্রা ঢাকা–সিলেট ফ্লাইট চালায় বলে তালিকাভুক্ত। আপনার তারিখে ভাড়ার ধরন ও ব্যাগেজ তুলনা করুন।",
         tips=["Mid-week flights are often cheaper than Thursday and Friday.",
               "Air Astra publishes a website promo code — check the offers page before booking with them.",
               "Compare with train and bus if your budget is tight; the homepage has those links."],
         tips_bn=["সপ্তাহের মাঝের ফ্লাইট প্রায়ই বৃহস্পতি-শুক্রবারের চেয়ে সস্তা।",
                  "এয়ার অ্যাস্ট্রার ওয়েবসাইটে প্রোমো কোড থাকে — বুকের আগে অফার পাতা দেখুন।",
                  "বাজেট কম হলে ট্রেন ও বাসের সাথেও তুলনা করুন; হোমপেজে লিংক আছে।"],
         entry="Carry your NID or passport for domestic flights and check the airline's check-in time.",
         entry_bn="ঘরোয়া ফ্লাইটে জাতীয় পরিচয়পত্র বা পাসপোর্ট সাথে রাখুন এবং এয়ারলাইনের চেক-ইন সময় দেখে নিন।"),
    dict(slug="dhaka-to-saidpur-air-ticket-price", new=True, domestic=True, city="Saidpur", city_bn="সৈয়দপুর", code="DAC → SPD",
         desc="Dhaka to Saidpur (DAC–SPD) air ticket price guide for Rangpur and north Bengal: compare domestic airlines and total cost with flexible dates.",
         intro="Saidpur airport serves Rangpur, Dinajpur, Nilphamari and the wider north. Flying saves many hours compared with the road, especially around holidays.",
         intro_bn="সৈয়দপুর এয়ারপোর্ট রংপুর, দিনাজপুর, নীলফামারীসহ উত্তরবঙ্গের মানুষকে সেবা দেয়। বিশেষ করে ছুটির সময় সড়কপথের চেয়ে অনেক ঘণ্টা বাঁচে।",
         airlines="Biman Bangladesh, US-Bangla and Novoair are listed as flying Dhaka to Saidpur. Compare fare types and baggage for your date.",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা ও নভোএয়ার ঢাকা–সৈয়দপুর ফ্লাইট চালায় বলে তালিকাভুক্ত। আপনার তারিখে ভাড়ার ধরন ও ব্যাগেজ তুলনা করুন।",
         tips=["Eid weeks sell out early on this route — book as soon as your dates are fixed.",
               "Winter fog can delay flights — check the airline's notices before leaving for the airport.",
               "Plan the road transfer from Saidpur to your final town."],
         tips_bn=["ঈদের সপ্তাহে এই রুটের সিট আগেই শেষ হয় — তারিখ ঠিক হলেই বুক করুন।",
                  "শীতে কুয়াশায় ফ্লাইট দেরি হতে পারে — এয়ারলাইনের নোটিশ দেখে নিন।",
                  "সৈয়দপুর থেকে নিজের শহরে যাওয়ার পরিবহন আগে ঠিক করুন।"],
         entry="Carry your NID or passport for domestic flights and check the airline's check-in time.",
         entry_bn="ঘরোয়া ফ্লাইটে জাতীয় পরিচয়পত্র বা পাসপোর্ট সাথে রাখুন এবং এয়ারলাইনের চেক-ইন সময় দেখে নিন।"),
    dict(slug="dhaka-to-jashore-air-ticket-price", new=True, domestic=True, city="Jashore", city_bn="যশোর", code="DAC → JSR",
         desc="Dhaka to Jashore (DAC–JSR) air ticket price guide for Jashore, Khulna and the south-west: compare domestic airlines and total cost.",
         intro="Jashore airport is the main air link for Jashore, Khulna and nearby districts. Since the Padma Bridge opened, compare the flight with road options too.",
         intro_bn="যশোর এয়ারপোর্ট যশোর, খুলনা ও আশেপাশের জেলার প্রধান আকাশপথ। পদ্মা সেতু চালুর পর সড়কপথের সাথেও তুলনা করুন।",
         airlines="Biman Bangladesh, US-Bangla and Novoair are listed as flying Dhaka to Jashore. Compare fare types and baggage for your date.",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা ও নভোএয়ার ঢাকা–যশোর ফ্লাইট চালায় বলে তালিকাভুক্ত। আপনার তারিখে ভাড়ার ধরন ও ব্যাগেজ তুলনা করুন।",
         tips=["Khulna travellers: add the Jashore–Khulna road time when comparing with a direct bus.",
               "Mid-week flights are often cheaper than weekend flights.",
               "Check winter fog notices from the airline before leaving for the airport."],
         tips_bn=["খুলনার যাত্রীরা সরাসরি বাসের সাথে তুলনার সময় যশোর–খুলনা সড়কের সময়ও যোগ করুন।",
                  "সপ্তাহের মাঝের ফ্লাইট প্রায়ই সপ্তাহান্তের চেয়ে সস্তা।",
                  "শীতে এয়ারপোর্টে রওনার আগে এয়ারলাইনের কুয়াশা-নোটিশ দেখুন।"],
         entry="Carry your NID or passport for domestic flights and check the airline's check-in time.",
         entry_bn="ঘরোয়া ফ্লাইটে জাতীয় পরিচয়পত্র বা পাসপোর্ট সাথে রাখুন এবং এয়ারলাইনের চেক-ইন সময় দেখে নিন।"),
    dict(slug="dhaka-to-rajshahi-air-ticket-price", new=True, domestic=True, city="Rajshahi", city_bn="রাজশাহী", code="DAC → RJH",
         desc="Dhaka to Rajshahi (DAC–RJH) air ticket price guide: compare domestic airlines, fare types and total cost with flexible dates.",
         intro="Rajshahi is a short flight from Dhaka and a long road or train journey. Seats are limited, so prices can move quickly near weekends and holidays.",
         intro_bn="ঢাকা থেকে রাজশাহী ফ্লাইটে অল্প সময়, সড়ক বা ট্রেনে অনেক সময়। সিট কম, তাই সপ্তাহান্ত ও ছুটির কাছে দাম দ্রুত বদলায়।",
         airlines="Biman Bangladesh, US-Bangla and Novoair are listed as flying Dhaka to Rajshahi. Compare fare types and baggage for your date.",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা ও নভোএয়ার ঢাকা–রাজশাহী ফ্লাইট চালায় বলে তালিকাভুক্ত। আপনার তারিখে ভাড়ার ধরন ও ব্যাগেজ তুলনা করুন।",
         tips=["Compare with the train if you travel light and have time — the homepage links to Bangladesh Railway.",
               "Book early for Eid; this route has few daily flights.",
               "Check winter fog notices from the airline."],
         tips_bn=["হালকা ব্যাগ আর সময় থাকলে ট্রেনের সাথে তুলনা করুন — হোমপেজে বাংলাদেশ রেলওয়ের লিংক আছে।",
                  "ঈদে আগে বুক করুন; এই রুটে দৈনিক ফ্লাইট কম।",
                  "শীতে এয়ারলাইনের কুয়াশা-নোটিশ দেখুন।"],
         entry="Carry your NID or passport for domestic flights and check the airline's check-in time.",
         entry_bn="ঘরোয়া ফ্লাইটে জাতীয় পরিচয়পত্র বা পাসপোর্ট সাথে রাখুন এবং এয়ারলাইনের চেক-ইন সময় দেখে নিন।"),
    dict(slug="dhaka-to-barishal-air-ticket-price", new=True, domestic=True, city="Barishal", city_bn="বরিশাল", code="DAC → BZL",
         desc="Dhaka to Barishal (DAC–BZL) air ticket price guide: compare domestic flights with launch and road options and the total cost.",
         intro="Barishal has a short flight from Dhaka, but launches and the road via the Padma Bridge are popular too. Compare total time and cost before you book.",
         intro_bn="ঢাকা থেকে বরিশাল ফ্লাইটে অল্প সময়, তবে লঞ্চ আর পদ্মা সেতু হয়ে সড়কপথও জনপ্রিয়। বুকের আগে মোট সময় ও খরচ তুলনা করুন।",
         airlines="Biman Bangladesh and US-Bangla are listed as flying Dhaka to Barishal. Compare fare types and baggage for your date.",
         airlines_bn="বিমান বাংলাদেশ ও ইউএস-বাংলা ঢাকা–বরিশাল ফ্লাইট চালায় বলে তালিকাভুক্ত। আপনার তারিখে ভাড়ার ধরন ও ব্যাগেজ তুলনা করুন।",
         tips=["Compare with the overnight launch — the homepage links to Shohoz launch tickets.",
               "Few flights a day: book early for holidays.",
               "Check winter fog notices from the airline."],
         tips_bn=["রাতের লঞ্চের সাথে তুলনা করুন — হোমপেজে Shohoz লঞ্চ টিকিটের লিংক আছে।",
                  "দিনে ফ্লাইট কম: ছুটিতে আগে বুক করুন।",
                  "শীতে এয়ারলাইনের কুয়াশা-নোটিশ দেখুন।"],
         entry="Carry your NID or passport for domestic flights and check the airline's check-in time.",
         entry_bn="ঘরোয়া ফ্লাইটে জাতীয় পরিচয়পত্র বা পাসপোর্ট সাথে রাখুন এবং এয়ারলাইনের চেক-ইন সময় দেখে নিন।"),
    # Existing English pages: only Bangla versions are generated
    dict(slug="dhaka-to-bangkok-cheap-ticket", new=False, city="Bangkok", city_bn="ব্যাংকক", code="DAC → BKK/DMK",
         intro_bn="ঢাকা থেকে ব্যাংকক সবচেয়ে জনপ্রিয় ছুটি ও চিকিৎসার রুটগুলোর একটি। ব্যাংককের দুটি এয়ারপোর্ট (সুবর্ণভূমি BKK ও ডন মুয়াং DMK) একসাথে দেখলে সস্তা অপশন বেশি পাওয়া যায়।",
         airlines_bn="থাই এয়ারওয়েজ, বিমান বাংলাদেশ ও ইউএস-বাংলা ঢাকা–ব্যাংকক সরাসরি ফ্লাইট চালায়। এই রুটে সরাসরি লো-কস্ট ফ্লাইট যাচাই করা যায়নি, তাই ব্যাগেজসহ মোট দাম তুলনা করুন।",
         tips_bn=["BKK ও DMK দুই এয়ারপোর্টের ভাড়া একসাথে তুলনা করুন।",
                  "লো-কস্ট ভাড়ায় চেকড ব্যাগ আলাদা কিনতে হতে পারে — মোট দাম দেখুন।",
                  "থাইল্যান্ডের ভেতরের ফ্লাইট (ফুকেট, চিয়াং মাই) আলাদা টিকিটে প্রায়ই সস্তা।"],
         entry_bn="বুকিংয়ের আগে থাইল্যান্ডের ভিসা ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-kolkata-cheap-ticket", new=False, city="Kolkata", city_bn="কলকাতা", code="DAC → CCU",
         intro_bn="ঢাকা থেকে কলকাতা খুব ছোট আন্তর্জাতিক রুট। সবচেয়ে কম দেখানো ভাড়া সবসময় সবচেয়ে কম মোট খরচ নয় — ব্যাগেজ ও সময় হিসাব করুন।",
         airlines_bn="ইন্ডিগো (লো-কস্ট), বিমান বাংলাদেশ ও ইউএস-বাংলা ঢাকা–কলকাতা ফ্লাইট চালায়। ব্যাগেজ ও মোট দাম তুলনা করুন।",
         tips_bn=["অসুবিধাজনক সময়ের সস্তা ফ্লাইটে যাতায়াত খরচ বাড়তে পারে।",
                  "ছোট রুটে চেকড ব্যাগেজের নিয়ম ভালো করে দেখুন।",
                  "আশেপাশের তারিখও তুলনা করুন; সিট ভরলে দাম দ্রুত বদলায়।"],
         entry_bn="বুকিংয়ের আগে ভারতের ভিসা ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-kuala-lumpur-cheap-ticket", new=False, city="Kuala Lumpur", city_bn="কুয়ালালামপুর", code="DAC → KUL",
         intro_bn="ঢাকা–কুয়ালালামপুর কাজ, পড়াশোনা ও ছুটির জন্য ব্যস্ত রুট। লো-কস্ট ও ফুল-সার্ভিস এয়ারলাইনের মোট দামে অনেক পার্থক্য হয়।",
         airlines_bn="এয়ারএশিয়া (লো-কস্ট) ঢাকা–কুয়ালালামপুর সরাসরি ফ্লাইট চালায়। মালয়েশিয়া এয়ারলাইনস, বিমান বাংলাদেশ ও ইউএস-বাংলাও এই রুটে চলে, তাই ব্যাগেজসহ মোট দাম তুলনা করুন।",
         tips_bn=["লো-কস্ট ভাড়ায় ব্যাগেজ, সিট ও খাবার আলাদা — সব যোগ করে তুলনা করুন।",
                  "KLIA টার্মিনাল ১ ও ২ আলাদা — কানেকশন থাকলে টার্মিনাল দেখে নিন।",
                  "মালয়েশিয়ার ভেতরের ফ্লাইট (লংকাউই, পেনাং) আলাদা টিকিটে সস্তা হতে পারে।"],
         entry_bn="বুকিংয়ের আগে মালয়েশিয়ার ভিসা, MDAC ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-dubai-cheap-ticket", new=False, city="Dubai", city_bn="দুবাই", code="DAC → DXB",
         intro_bn="দুবাই কর্মী, ব্যবসায়ী ও পর্যটকদের জন্য বড় রুট, আবার ইউরোপ-আমেরিকার ট্রানজিট হাবও। DXB ও DWC দুই এয়ারপোর্ট একসাথে দেখুন।",
         airlines_bn="ফ্লাইদুবাই (লো-কস্ট), এমিরেটস, বিমান বাংলাদেশ ও ইউএস-বাংলা ঢাকা–দুবাই (DXB) ফ্লাইট চালায়। এয়ার অ্যারাবিয়া যায় শারজাহ (SHJ), দুবাই নয় — কেনার আগে নামার এয়ারপোর্ট দেখে নিন।",
         tips_bn=["কর্মীরা বেশি চেকড ব্যাগেজসহ ভাড়া তুলনা করুন।",
                  "দুবাই শুধু ট্রানজিট হলে চূড়ান্ত গন্তব্য সার্চ করুন।",
                  "ঈদের আগে-পরে ভাড়া বাড়ে — আশেপাশের তারিখ দেখুন।"],
         entry_bn="বুকিংয়ের আগে সংযুক্ত আরব আমিরাতের ভিসা ও পাসপোর্টের মেয়াদ অফিসিয়াল সূত্র থেকে নিশ্চিত হোন।"),
    dict(slug="dhaka-to-coxs-bazar-ticket-price", new=False, city="Cox's Bazar", city_bn="কক্সবাজার", code="DAC → CXB",
         intro_bn="ঢাকা–কক্সবাজার দেশের সবচেয়ে জনপ্রিয় ঘরোয়া ফ্লাইট রুট। ছুটির দিনে ও শীতে ভাড়া দ্রুত বাড়ে।",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা ও নভোএয়ার ঢাকা–কক্সবাজার ফ্লাইট চালায়। ভাড়ার ধরন, ব্যাগেজ ও মোট দাম তুলনা করুন। বাসের তুলনাও আমাদের হোমপেজে আছে।",
         tips_bn=["বৃহস্পতি-শুক্রবার ও ছুটিতে ভাড়া বেশি — সপ্তাহের মাঝে দেখুন।",
                  "সকালের ফ্লাইটে দিনটা পুরো কাজে লাগানো যায়।",
                  "বাজেট কম হলে হোমপেজ থেকে বাস/ট্রেনের দামও তুলনা করুন।"],
         entry_bn="ঘরোয়া ফ্লাইটে জাতীয় পরিচয়পত্র বা পাসপোর্ট সাথে রাখুন; এয়ারলাইনের নিয়ম দেখে নিন।"),
    dict(slug="dhaka-to-chattogram-ticket-price", new=False, city="Chattogram", city_bn="চট্টগ্রাম", code="DAC → CGP",
         intro_bn="ঢাকা–চট্টগ্রাম ছোট ঘরোয়া রুট; ফ্লাইট, ট্রেন ও বাস — তিনটাই ভালো অপশন। মোট সময় ও খরচ তুলনা করে বাছুন।",
         airlines_bn="বিমান বাংলাদেশ, ইউএস-বাংলা ও নভোএয়ার ঢাকা–চট্টগ্রাম ফ্লাইট চালায়। ভাড়ার ধরন, ব্যাগেজ ও মোট দাম তুলনা করুন।",
         tips_bn=["এয়ারপোর্টে যাতায়াতের সময়সহ হিসাব করলে ট্রেন কখনো সমান দ্রুত হয়।",
                  "ভোরের ও রাতের ফ্লাইট প্রায়ই সস্তা।",
                  "ট্রেনের টিকিট বাংলাদেশ রেলওয়ের অফিসিয়াল সাইটে কাটুন।"],
         entry_bn="ঘরোয়া ফ্লাইটে জাতীয় পরিচয়পত্র বা পাসপোর্ট সাথে রাখুন; এয়ারলাইনের নিয়ম দেখে নিন।"),
]

HEAD_STYLE = """    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="/assets/luxury.css?v=clear-20261019">
    <style>
        .hero-glow { background: radial-gradient(circle at 20% 20%, rgba(56,189,248,.28), transparent 32%), radial-gradient(circle at 80% 10%, rgba(246,222,156,.55), transparent 30%), linear-gradient(165deg,#7dd3fc,#a5f3fc 26%,#99f6e4 52%,#fde68a 82%,#fed7aa); }
        .glass-card { background: linear-gradient(155deg,#bae6fd,#a5f3fc 30%,#99f6e4 58%,#fde68a 88%,#fed7aa); border: 1px solid rgba(201,162,75,.38); box-shadow: 0 16px 38px rgba(3,105,161,.12); color:#1E293B; }
    </style>
    <link rel="stylesheet" href="/assets/tailwind.css?v=t107">
    <link rel="icon" href="/favicon-v2.ico?v=2" sizes="any">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-v2-32.png?v=2">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-v2-16.png?v=2">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-v2.png?v=2">
    <link rel="manifest" href="/site.webmanifest?v=2">"""

def trip(sub, path):
    return f"https://www.trip.com/{path}?{TRIP.replace('&trip_sub3', '&trip_sub1=' + sub + '&trip_sub3')}"

def book_nav(lang):
    lbl = "Book:" if lang == "en" else "বুক করুন:"
    fs = "On-site flight search" if lang == "en" else "অন-সাইট ফ্লাইট সার্চ"
    return (f'<nav aria-label="Booking path"><p><strong>{lbl}</strong> <a class="text-sky-400 underline" href="/">{fs}</a> · '
            f'<a class="text-sky-400 underline" href="{html.escape(trip("flights","flights"))}" target="_blank" rel="sponsored noopener noreferrer">Trip.com flights</a> · '
            f'<a class="text-sky-400 underline" href="{html.escape(trip("hotels","hotels"))}" target="_blank" rel="sponsored noopener noreferrer">Trip.com hotels</a> · '
            f'<a class="text-sky-400 underline" href="{html.escape(trip("tours","things-to-do/"))}" target="_blank" rel="sponsored noopener noreferrer">Trip.com tours</a></p></nav>')

FOOTER_EN = """        <footer class="text-center text-[10px] text-slate-500 leading-5 pb-4">
            Cheap Ticket Finder does not sell tickets and does not scrape airlines. The final price is on the provider. cheapticketfinder.site
            <nav class="mt-2 flex flex-wrap justify-center gap-x-3 gap-y-1 text-[11px]">
                <a class="text-sky-400 hover:text-sky-300" href="/offers/">Offers</a>
                <a class="text-sky-400 hover:text-sky-300" href="/airlines/">Airlines</a>
                <a class="text-sky-400 hover:text-sky-300" href="/travel-insurance/">Travel Insurance</a>
                <a class="text-sky-400 hover:text-sky-300" href="/about">About</a>
                <a class="text-sky-400 hover:text-sky-300" href="/terms">Terms</a>
                <a class="text-sky-400 hover:text-sky-300" href="/privacy">Privacy</a>
                <a class="text-sky-400 hover:text-sky-300" href="/contact">Contact</a>
                <a class="text-sky-400 hover:text-sky-300" href="https://www.facebook.com/CheapTFBD" target="_blank" rel="noopener noreferrer">Facebook</a>
                <a class="text-sky-400 hover:text-sky-300" href="/disclosure">Disclosure</a>
                <a class="text-sky-400 hover:text-sky-300" href="/about/#brandlinker">A BrandLinker project</a>
            </nav>
        </footer>"""
FOOTER_BN = FOOTER_EN.replace(
    "Cheap Ticket Finder does not sell tickets and does not scrape airlines. The final price is on the provider.",
    "Cheap Ticket Finder টিকিট বিক্রি করে না। চূড়ান্ত দাম এয়ারলাইন বা বুকিং সাইটে নিশ্চিত হয়।")

def faq_en(city):
    return [(f"What is the Dhaka to {city} ticket price today?",
             "It depends on your travel dates, airline and fare family, so we do not print a fixed price here. Open the search tool, pick your dates, and compare prices from partner sites in the on-site flight search."),
            ("Does Cheap Ticket Finder sell tickets?",
             "No. We build the dated search; booking and payment happen with the airline/provider."),
            ("How can I lower the total cost?",
             "Stay flexible with dates, compare the total including baggage, and check both non-stop and connecting options. No specific day guarantees the lowest fare.")]

def faq_bn(city):
    return [(f"আজ ঢাকা থেকে {city} টিকিটের দাম কত?",
             "দাম তারিখ, এয়ারলাইন ও ভাড়ার ধরনের ওপর নির্ভর করে, তাই আমরা এখানে নির্দিষ্ট দাম লিখি না। সার্চ টুলে আপনার তারিখ দিয়ে পার্টনার সাইটগুলোর দাম তুলনা করুন।"),
            ("Cheap Ticket Finder কি টিকিট বিক্রি করে?",
             "না। আমরা তারিখসহ সার্চ তৈরি করে দিই; বুকিং ও পেমেন্ট হয় এয়ারলাইন বা বুকিং সাইটে।"),
            ("মোট খরচ কীভাবে কমাব?",
             "তারিখ নমনীয় রাখুন, ব্যাগেজসহ মোট দাম তুলনা করুন, আর ননস্টপ ও কানেকশন দুটোই দেখুন। কোনো নির্দিষ্ট দিন সবচেয়ে কম দামের নিশ্চয়তা দেয় না।")]

def ld(faqs):
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}, ensure_ascii=False)

def crumbs(url, title):
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": title.split(" — ")[0].split(" & ")[0], "item": url}]}, ensure_ascii=False)

def head(lang, title, desc, url, en_url, bn_url, faqs):
    alt = ""
    if en_url:
        alt += f'    <link rel="alternate" hreflang="en" href="{en_url}">\n'
    alt += f'    <link rel="alternate" hreflang="bn" href="{bn_url}">\n'
    alt += f'    <link rel="alternate" hreflang="x-default" href="{en_url or bn_url}">\n'
    t, d = html.escape(title), html.escape(desc)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t} | Cheap Ticket Finder</title>
    <meta name="description" content="{d}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{url}">
{alt}    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Cheap Ticket Finder">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{t}">
    <meta property="og:description" content="{d}">
    <meta property="og:image" content="{SITE}/assets/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:type" content="image/png">
    <meta property="og:image:alt" content="Cheap Ticket Finder">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{SITE}/assets/og-image.png">
    <meta name="twitter:title" content="{t}">
    <meta name="twitter:description" content="{d}">
    <script type="application/ld+json">{ld(faqs)}</script>
    <script type="application/ld+json">{crumbs(url, title)}</script>
{HEAD_STYLE}
</head>"""

def body(h1, sub, sections, lang):
    footer = FOOTER_EN if lang == "en" else FOOTER_BN
    return f"""
<body class="bg-amber-50 text-slate-800 min-h-screen pb-16 antialiased hero-glow">
    <div class="max-w-3xl mx-auto px-3 sm:px-6 py-5 sm:py-8">
        <header class="text-center mb-6">
            <a href="/" aria-label="Cheap Ticket Finder home" style="display:inline-block;margin-bottom:12px"><img class="ctf-logo" src="/assets/brand/ctf-logo-header.webp" alt="Cheap Ticket Finder" width="321" height="112" style="display:block;height:56px;width:auto;max-width:100%"></a>
            <h1 class="text-3xl sm:text-4xl font-black text-white tracking-tight">{html.escape(h1)}</h1>
            <p class="text-slate-400 text-xs sm:text-sm mt-2 leading-5">{sub}</p>
        </header>
        <main class="glass-card p-4 sm:p-6 rounded-2xl mb-6 text-sm leading-6 text-slate-300 space-y-4">
{sections}
        </main>
{footer}
    </div>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""

def h2(t): return f'            <h2 class="text-base font-bold text-sky-400">{t}</h2>'
def ul(items): return '            <ul class="list-disc pl-5 space-y-1">' + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>"
def p(t): return f"            <p>{t}</p>"

def en_page(r, others):
    city = r["city"]
    faqs = faq_en(city)
    url = f"{SITE}/{r['slug']}/"; bn = f"{SITE}/bn/{r['slug']}/"
    secs = [
        "            " + book_nav("en"),
        p(html.escape(r["intro"]) + " Use this guide to check your exact dates — no invented live price is shown here."),
        h2("How to find the cheapest dates (3 steps)"),
        f'            <ol class="list-decimal pl-5 space-y-1"><li>Open the <a class="text-sky-400 underline" href="/">Cheap Ticket Finder search tool</a>, set From = Dhaka and To = {html.escape(city)}, and pick flexible dates on the calendar.</li><li>Open the on-site flight search and compare prices from partner sites. The final price is confirmed on the booking site.</li><li>Before paying, compare the total with baggage, seat and payment fees added. The lowest headline fare is not always the lowest total.</li></ol>',
        h2(f"Route tips — Dhaka to {html.escape(city)}"), ul(r["tips"]),
        h2("Airlines on this route"), p(html.escape(r["airlines"]) + " Schedules change, so always check the search for your dates."),
        h2("Baggage &amp; total-cost warning"),
        p('Checked baggage, cabin baggage, seat selection, meals and change/refund rules depend on the airline and the exact fare family. Always confirm the allowance on the airline or provider page for the fare you are about to buy. Compare the final payable total, not a base fare example. Nothing on this page is <strong class="text-white">a live fare</strong>.'),
        h2("ID &amp; check-in" if r.get("domestic") else "Visa &amp; entry check"), p(html.escape(r["entry"]) + ("" if r.get("domestic") else " This guide does not give visa advice.")),
        h2("FAQ"),
    ]
    for q, a in faqs:
        secs += [f'            <h3 class="font-bold text-white">{html.escape(q)}</h3>', p(html.escape(a))]
    secs += [p(f'<a class="text-sky-400 underline font-bold" href="/">→ Check Dhaka to {html.escape(city)} dates in the search tool</a>'),
             "            " + book_nav("en"),
             p("More route guides: " + " · ".join(f'<a class="text-sky-400 underline" href="/{o["slug"]}/">Dhaka to {html.escape(o["city"])}</a>' for o in others))]
    sub = f"{r['code']} — how to check the cheapest real fare for your dates. Last updated: {UPDATED_EN}. No live fare is published on this page."
    title = f"Dhaka to {city} Air Ticket Price & Cheap Flights"
    return head("en", title, r["desc"], url, url, bn, faqs) + body(f"Dhaka to {city} Cheap Ticket", sub, "\n".join(secs), "en")

def bn_page(r, others):
    c = r["city_bn"]
    faqs = faq_bn(c)
    en = f"{SITE}/{r['slug']}/"; url = f"{SITE}/bn/{r['slug']}/"
    secs = [
        "            " + book_nav("bn"),
        p(html.escape(r["intro_bn"]) + " এই পাতায় কোনো বানানো লাইভ দাম নেই — আপনার তারিখে আসল দাম দেখতে সার্চ টুল ব্যবহার করুন।"),
        h2("সবচেয়ে সস্তা তারিখ খোঁজার ৩টি ধাপ"),
        f'            <ol class="list-decimal pl-5 space-y-1"><li><a class="text-sky-400 underline" href="/">Cheap Ticket Finder সার্চ টুল</a> খুলুন, From = Dhaka আর To = {html.escape(r["city"])} দিন, ক্যালেন্ডারে নমনীয় তারিখ বাছুন।</li><li>অন-সাইট ফ্লাইট সার্চে পার্টনার সাইটগুলোর দাম তুলনা করুন। চূড়ান্ত দাম বুকিং সাইটে নিশ্চিত হয়।</li><li>পেমেন্টের আগে ব্যাগেজ, সিট ও পেমেন্ট ফি যোগ করে মোট দাম তুলনা করুন। সবচেয়ে কম দেখানো ভাড়া সবসময় সবচেয়ে কম মোট খরচ নয়।</li></ol>',
        h2(f"রুট টিপস — ঢাকা থেকে {c}"), ul(r["tips_bn"]),
        h2("এই রুটের এয়ারলাইন"), p(html.escape(r["airlines_bn"]) + " সময়সূচি বদলায়, তাই আপনার তারিখে সার্চ করে দেখুন।"),
        h2("ব্যাগেজ ও মোট খরচ"),
        p("চেকড ব্যাগেজ, কেবিন ব্যাগ, সিট, খাবার ও টিকিট বদল/রিফান্ডের নিয়ম এয়ারলাইন ও ভাড়ার ধরনের ওপর নির্ভর করে। যে ভাড়া কিনছেন, তার ব্যাগেজ এয়ারলাইন বা বুকিং সাইটে নিশ্চিত করুন। এই পাতার কিছুই <strong class=\"text-white\">লাইভ দাম নয়</strong>।"),
        h2("পরিচয়পত্র ও চেক-ইন" if r.get("domestic") else "ভিসা ও প্রবেশের নিয়ম"), p(html.escape(r["entry_bn"]) + ("" if r.get("domestic") else " এই গাইড ভিসা পরামর্শ দেয় না।")),
        h2("সাধারণ প্রশ্ন (FAQ)"),
    ]
    for q, a in faqs:
        secs += [f'            <h3 class="font-bold text-white">{html.escape(q)}</h3>', p(html.escape(a))]
    secs += [p(f'<a class="text-sky-400 underline font-bold" href="/">→ সার্চ টুলে ঢাকা থেকে {c} তারিখ দেখুন</a>'),
             p(f'Read in English: <a class="text-sky-400 underline" href="/{r["slug"]}/">Dhaka to {html.escape(r["city"])} cheap ticket</a>'),
             "            " + book_nav("bn"),
             p("আরও রুট গাইড: " + " · ".join(f'<a class="text-sky-400 underline" href="/bn/{o["slug"]}/">ঢাকা–{o["city_bn"]}</a>' for o in others)),
             p('আরও পড়ুন: <a class="text-sky-400 underline" href="/bn/how-to-find-cheap-air-tickets/">কম দামে বিমান টিকিট পাওয়ার ৭টি ধাপ</a>')]
    sub = f"{r['code']} — আপনার তারিখে আসল সবচেয়ে কম ভাড়া কীভাবে দেখবেন। সর্বশেষ আপডেট: {UPDATED_BN}। এই পাতায় কোনো লাইভ দাম নেই।"
    title = f"ঢাকা থেকে {c} সস্তা বিমান টিকিট — দাম দেখার গাইড"
    desc = f"ঢাকা থেকে {c} ({r['code']}) সস্তা বিমান টিকিট গাইড: নমনীয় তারিখে ভাড়া, ব্যাগেজ ও মোট খরচ তুলনা করুন।"
    return head("bn", title, desc, url, en, url, faqs) + body(f"ঢাকা থেকে {c} সস্তা বিমান টিকিট", sub, "\n".join(secs), "bn")

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    DOMESTIC = {"dhaka-to-coxs-bazar-ticket-price", "dhaka-to-chattogram-ticket-price"} | {r["slug"] for r in ROUTES if r.get("domestic")}
    intl = [r for r in ROUTES if r["slug"] not in DOMESTIC]
    dom = [r for r in ROUTES if r["slug"] in DOMESTIC]
    for r in ROUTES:
        others = [o for o in ROUTES if o is not r][:8]
        if r["new"]:
            pool = dom if r.get("domestic") else intl
            en_others = [o for o in pool if o is not r][:8]
            write(f"{r['slug']}/index.html", en_page(r, en_others))
        write(f"bn/{r['slug']}/index.html", bn_page(r, others))
    print("generated", sum(r["new"] for r in ROUTES), "EN +", len(ROUTES), "BN pages")

    # keep the Bangla/English switch on regenerated pages
    os.system("python3 scripts/add_lang_switch.py")
