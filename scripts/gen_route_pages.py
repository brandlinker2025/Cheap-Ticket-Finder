#!/usr/bin/env python3
"""Generate route guide pages (English + Bangla) from ROUTES data.

Add-only: writes new folders; never touches existing English route pages.
Run from repo root:  python3 scripts/gen_route_pages.py
"""
import html, json, os

SITE = "https://cheapticketfinder.site"
UPDATED_EN = "1 November 2026 (Asia/Dhaka)"
UPDATED_BN = "১ নভেম্বর ২০২৬"
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
        h2("Visa &amp; entry check"), p(html.escape(r["entry"]) + " This guide does not give visa advice."),
        h2("FAQ"),
    ]
    for q, a in faqs:
        secs += [f'            <h3 class="font-bold text-white">{html.escape(q)}</h3>', p(html.escape(a))]
    secs += [p(f'<a class="text-sky-400 underline font-bold" href="/">→ Check Dhaka to {html.escape(city)} dates in the search tool</a>'),
             p(f'বাংলায় পড়ুন: <a class="text-sky-400 underline" href="/bn/{r["slug"]}/">ঢাকা থেকে {r["city_bn"]} সস্তা টিকিট</a>'),
             "            " + book_nav("en"),
             p("More route guides: " + " · ".join(f'<a class="text-sky-400 underline" href="/{o["slug"]}/">Dhaka to {html.escape(o["city"])}</a>' for o in others))]
    sub = f"{r['code']} — how to check the cheapest real fare for your dates. Last updated: {UPDATED_EN}. No live fare is published on this page."
    title = f"Dhaka to {city} Cheap Ticket — Flight Price Guide"
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
        h2("ভিসা ও প্রবেশের নিয়ম"), p(html.escape(r["entry_bn"]) + " এই গাইড ভিসা পরামর্শ দেয় না।"),
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
    intl = [r for r in ROUTES if r["slug"] not in ("dhaka-to-coxs-bazar-ticket-price", "dhaka-to-chattogram-ticket-price")]
    for r in ROUTES:
        others = [o for o in ROUTES if o is not r][:8]
        if r["new"]:
            en_others = [o for o in intl if o is not r][:8]
            write(f"{r['slug']}/index.html", en_page(r, en_others))
        write(f"bn/{r['slug']}/index.html", bn_page(r, others))
    print("generated", sum(r["new"] for r in ROUTES), "EN +", len(ROUTES), "BN pages")

    # keep the Bangla/English switch on regenerated pages
    os.system("python3 scripts/add_lang_switch.py")
