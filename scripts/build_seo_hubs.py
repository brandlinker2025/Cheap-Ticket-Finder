#!/usr/bin/env python3
"""Builds the fare-price hub pages and the Dhaka-vs-nearby-country fare study.

Fares are real observations (cheapest one-way economy, 1 adult, travel date 10 Dec 2026),
checked on a public fare search on 4 Nov 2026 and spot-checked on Aviasales on 5 Nov 2026.
Non-stop airline lists: FlightConnections, read 5 Nov 2026. Re-run after editing the data.
"""
import html, json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://cheapticketfinder.site"
TEMPLATE = os.path.join(ROOT, "how-to-find-cheap-air-tickets", "index.html")
CHECKED = "4 November 2026"
UPDATED_ISO = "2026-11-05"
UPDATED = "5 November 2026"
TP = "https://tp.media/r?campaign_id=100&marker=791994&p=4114&sub_id=cheapticketfinder-hub&trs=587447&u="

def avia(o, d):
    from urllib.parse import quote
    return TP + quote(f"https://www.aviasales.com/search/{o}1012{d}1", safe="")

def tripcom(o, d):
    return (f"https://www.trip.com/flights/showfarefirst?dcity={o.lower()}&acity={d.lower()}&ddate=2026-12-10&triptype=ow"
            "&class=y&quantity=1&locale=en-XX&curr=USD&Allianceid=11059812&SID=333836392&trip_sub1=hub&trip_sub3=D20343143")

# dest, city, city_bn, guide slug, non-stop airlines from Dhaka, fare from DAC, fare from CCU, DEL, KTM, CMB, CGP
ROUTES = [
    ("CCU", "Kolkata", "কলকাতা", "dhaka-to-kolkata-cheap-ticket", "Biman, US-Bangla (seasonal), IndiGo", 85, None, None, None, None, None),
    ("BKK", "Bangkok", "ব্যাংকক", "dhaka-to-bangkok-cheap-ticket", "Biman, US-Bangla, Thai Airways", 209, 135, 171, 359, 228, None),
    ("SIN", "Singapore", "সিঙ্গাপুর", "dhaka-to-singapore-cheap-ticket", "Biman, US-Bangla, Singapore Airlines", 282, 165, 226, 380, 270, None),
    ("KUL", "Kuala Lumpur", "কুয়ালালামপুর", "dhaka-to-kuala-lumpur-cheap-ticket", "Biman, AirAsia, Batik Air, Malaysia Airlines, US-Bangla (seasonal)", 293, 191, 250, None, 202, None),
    ("DXB", "Dubai", "দুবাই", "dhaka-to-dubai-cheap-ticket", "Biman, US-Bangla, Emirates, flydubai", 296, 245, 257, 510, 170, 316),
    ("DOH", "Doha", "দোহা", "dhaka-to-doha-cheap-ticket", "Biman, US-Bangla, Qatar Airways", 393, 414, 232, 364, 168, 399),
    ("RUH", "Riyadh", "রিয়াদ", "dhaka-to-riyadh-cheap-ticket", "Biman, US-Bangla, Riyadh Air, Saudia", 427, 249, 231, 314, 228, 482),
    ("JED", "Jeddah", "জেদ্দা", "dhaka-to-jeddah-cheap-ticket", "Biman (seasonal), US-Bangla, Saudia", 455, 347, 375, 446, 278, 455),
    ("LHR", "London", "লন্ডন", "dhaka-to-london-cheap-ticket", "Biman (seasonal)", 489, 393, 293, 569, 376, 549),
    ("JFK", "New York", "নিউ ইয়র্ক", None, "None — one stop or more", 534, 576, 548, 980, 488, 593),
    ("YYZ", "Toronto", "টরন্টো", None, "None listed — one stop or more", 895, 792, 570, 1249, 635, None),
]
MORE_GUIDES = [
    ("Delhi", "দিল্লি", "dhaka-to-delhi-cheap-ticket", "Biman, Air India, IndiGo"),
    ("Kathmandu", "কাঠমান্ডু", "dhaka-to-kathmandu-cheap-ticket", "Biman (seasonal), Himalaya Airlines (seasonal)"),
    ("Muscat", "মাসকাট", "dhaka-to-muscat-cheap-ticket", "Biman, US-Bangla, Oman Air, SalamAir"),
    ("Kuwait", "কুয়েত", "dhaka-to-kuwait-cheap-ticket", "Biman (seasonal), Jazeera Airways, Kuwait Airways"),
    ("Istanbul", "ইস্তানবুল", "dhaka-to-istanbul-cheap-ticket", "Turkish Airlines"),
    ("Maldives", "মালদ্বীপ", "dhaka-to-maldives-cheap-ticket", "US-Bangla (seasonal), Maldivian"),
    ("Guangzhou", "গুয়াংজু", "dhaka-to-guangzhou-cheap-ticket", "Biman, China Southern, US-Bangla (seasonal)"),
    ("Kunming", "কুনমিং", "dhaka-to-kunming-cheap-ticket", "China Eastern"),
    ("Beijing", "বেইজিং", "dhaka-to-beijing-cheap-ticket", "Air China, China Southern"),
]
NO_AVIASALES = {"RUH"}  # Aviasales showed "No results found" for these on 5 Nov 2026 — link Trip.com instead

def link(o, d):
    return tripcom(o, d) if d in NO_AVIASALES else avia(o, d)

def a(href, text, cls="text-sky-400 underline", ext=True):
    rel = ' target="_blank" rel="sponsored noopener noreferrer"' if ext else ""
    return f'<a class="{cls}" href="{html.escape(href)}"{rel}>{text}</a>'

def page(path, lang, title, desc, h1, sub, crumb, alt_path, main, faqs, article_name):
    t = open(TEMPLATE, encoding="utf-8").read()
    head_end = t.index("<body")
    head = t[:head_end]
    url = f"{SITE}/{path}"
    en_url = f"{SITE}/{path if lang == 'en' else alt_path}"
    bn_url = f"{SITE}/{alt_path if lang == 'en' else path}"
    head = re.sub(r'<html lang="[a-z]+">', f'<html lang="{lang}">', head) if "<html" in head else head
    head = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", head, count=1)
    for prop in ("description", "og:description", "twitter:description"):
        attr = "name" if prop in ("description", "twitter:description") else "property"
        head = re.sub(rf'(<meta {attr}="{re.escape(prop)}" content=")[^"]*(")', lambda m: m.group(1) + html.escape(desc, quote=True) + m.group(2), head, count=1)
    for prop in ("og:title", "twitter:title"):
        attr = "property" if prop.startswith("og") else "name"
        head = re.sub(rf'(<meta {attr}="{re.escape(prop)}" content=")[^"]*(")', lambda m: m.group(1) + html.escape(title, quote=True) + m.group(2), head, count=1)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', r"\g<1>" + url, head, count=1)
    head = re.sub(r'(<meta property="og:locale" content=")[^"]*', r"\g<1>" + ("bn_BD" if lang == "bn" else "en_US"), head, count=1)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head, count=1)
    head = re.sub(r'<link rel="alternate" hreflang="en" href="[^"]*">', f'<link rel="alternate" hreflang="en" href="{en_url}">', head, count=1)
    head = re.sub(r'<link rel="alternate" hreflang="bn" href="[^"]*">', f'<link rel="alternate" hreflang="bn" href="{bn_url}">', head, count=1)
    head = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', f'<link rel="alternate" hreflang="x-default" href="{en_url}">', head, count=1)
    graph = [
        {"@type": "Article", "@id": url + "#article", "headline": article_name, "description": desc, "inLanguage": lang,
         "url": url, "mainEntityOfPage": url, "datePublished": UPDATED_ISO, "dateModified": UPDATED_ISO,
         "image": f"{SITE}/assets/og-image.png",
         "author": {"@type": "Organization", "name": "Cheap Ticket Finder", "url": SITE + "/"},
         "publisher": {"@id": SITE + "/#organization"}},
        {"@type": "FAQPage", "@id": url + "#faq", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", ans)}} for q, ans in faqs]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + ("/bn/" if lang == "bn" else "/")},
            {"@type": "ListItem", "position": 2, "name": crumb, "item": url}]},
        {"@type": "Organization", "@id": SITE + "/#organization", "name": "Cheap Ticket Finder", "url": SITE + "/",
         "logo": f"{SITE}/icon-v2-512.png", "sameAs": ["https://www.facebook.com/CheapTFBD"]},
    ]
    head = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda m: '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>",
                  head, count=1, flags=re.S)
    body = t[head_end:]
    other = "English" if lang == "bn" else "বাংলায় পড়ুন"
    other_attr = 'hreflang="en"' if lang == "bn" else 'hreflang="bn" lang="bn"'
    home = "/bn/" if lang == "bn" else "/"
    home_txt = "হোম" if lang == "bn" else "Home"
    header = (f'            <nav aria-label="Breadcrumb" class="text-xs mb-2"><a class="text-sky-400 underline" href="{home}">{home_txt}</a> › <span>{html.escape(crumb)}</span> · '
              f'<a class="text-sky-400 underline" href="/{alt_path}" {other_attr}>{other}</a></nav>\n'
              f'            <h1 class="text-3xl sm:text-4xl font-black text-white tracking-tight">{html.escape(h1)}</h1>\n'
              f'            <p class="text-slate-400 text-xs sm:text-sm mt-2 leading-5">{sub}</p>\n')
    if not alt_path:
        head = re.sub(r'\s*<link rel="alternate" hreflang="(bn|en|x-default)" href="[^"]*">', "", head)
        header = re.sub(r' · <a class="text-sky-400 underline" href="/" [^>]*>[^<]*</a>', "", header)
    body = re.sub(r'            <nav aria-label="Breadcrumb".*?</p>\n', lambda m: header, body, count=1, flags=re.S)
    faq_html = "".join(f'<h3 class="font-bold text-white">{html.escape(q)}</h3><p>{ans}</p>' for q, ans in faqs)
    faq_h = "প্রায়ই জিজ্ঞাসিত প্রশ্ন" if lang == "bn" else "Frequently asked questions"
    main_html = (f'<main class="glass-card p-4 sm:p-6 rounded-2xl mb-6 text-sm leading-6 text-slate-300 space-y-4">\n{main}\n'
                 f'            <h2 class="text-base font-bold text-sky-400">{faq_h}</h2>\n            {faq_html}\n        </main>')
    body = re.sub(r"<main.*?</main>", lambda m: main_html, body, count=1, flags=re.S)
    out = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(head + body)
    print("wrote", path)

H2 = lambda t: f'            <h2 class="text-base font-bold text-sky-400">{t}</h2>'
P = lambda t: f"            <p>{t}</p>"
TABLE = lambda head, rows: ('            <div style="overflow-x:auto"><table class="w-full text-left text-xs sm:text-sm"><thead><tr>'
                            + "".join(f'<th class="pr-2 pb-1">{h}</th>' for h in head) + "</tr></thead><tbody>"
                            + "".join("<tr>" + "".join(f'<td class="py-1.5 pr-2 align-top">{c}</td>' for c in r) + "</tr>" for r in rows)
                            + "</tbody></table></div>")

def usd(v, o, d):
    return a(link(o, d), f"US${v}") if v else "—"

def build_hub_en():
    rows = []
    for d, city, _, slug, air, dac, ccu, *_ in ROUTES:
        name = a("/" + slug + "/", f"{city} ({d})", ext=False) if slug else f"{city} ({d})"
        rows.append([name, usd(dac, "DAC", d), usd(ccu, "CCU", d) if d != "CCU" else "—", html.escape(air)])
    more = [[a("/" + s + "/", c, ext=False), html.escape(air)] for c, _, s, air in MORE_GUIDES]
    main = "\n".join([
        H2("Short answer"),
        P('<strong class="text-white">There is no fixed air ticket price in Bangladesh — fares change every day with the date, airline and seats left. '
          'The table below shows real fares we checked, the airlines that fly each route non-stop from Dhaka, and a link to today\'s live price.</strong>'),
        H2(f"Air ticket prices from Dhaka (checked {CHECKED})"),
        TABLE(["Destination", "From Dhaka", "From Kolkata", "Non-stop airlines from Dhaka"], rows),
        P(f'<span class="text-[11px] text-slate-500">Cheapest one-way economy fare for 1 adult, travel date 10 Dec 2026, seen on a public fare search on {CHECKED}. '
          'Taxes included; checked baggage may cost extra. Tap a price for today\'s live fare (Aviasales; Riyadh on Trip.com). Non-stop airline lists: FlightConnections, read 5 Nov 2026.</span>'),
        H2("Why fares from Kolkata are often lower"),
        P('On 8 of the 10 international routes we checked, the cheapest fare starting in Kolkata was lower than from Dhaka — up to 42% (Riyadh) and 41% (Singapore). '
          'Changing only the booking website\'s country made no difference. You need an Indian visa and must add the cost of getting to Kolkata. '
          + a("/cheaper-flights-from-kolkata/", "Read the full fare study →", "text-sky-400 underline font-bold", ext=False)),
        H2("More route guides"),
        TABLE(["Route from Dhaka", "Non-stop airlines"], more),
        H2("How to pay less"),
        '            <ol class="list-decimal pl-5 space-y-1"><li>Search a few days before and after your date — the cheapest day can be much lower.</li>'
        '<li>Compare the total with baggage, not the first price you see.</li>'
        '<li>Open the airline\'s own website for the same flight; book where the total is lower.</li>'
        '<li>Check bank-card offers (for example EBL, City Amex) on Bangladeshi booking sites.</li>'
        '<li>For long trips, compare starting from Kolkata, Delhi, Kathmandu or Colombo.</li></ol>',
        P(a("/", "→ Search your route and dates now", "text-sky-400 underline font-bold", ext=False)),
    ])
    faqs = [
        ("What is the air ticket price from Dhaka to Dubai?", f"On {CHECKED} the cheapest one-way fare we saw for 10 December 2026 was US$296 from Dhaka and US$245 from Kolkata. Prices change daily — use the search for today's fare."),
        ("Which airline is cheapest from Bangladesh?", "No single airline is always cheapest. Low-cost carriers such as AirAsia, IndiGo and flydubai are often lower before baggage; compare the total with baggage for your date."),
        ("Is it cheaper to buy a ticket from another country?", "Changing only the website's country made no difference in our check. Starting the flight in a nearby country such as India was often cheaper."),
        ("Does Cheap Ticket Finder sell tickets?", "No. We compare and link to partner sites and airlines. The final price is shown and paid there."),
    ]
    page("air-ticket-price-bangladesh/", "en",
         "Air Ticket Price from Bangladesh 2026 — Real Fares by Route | Cheap Ticket Finder",
         "Air ticket prices from Dhaka to Dubai, Saudi Arabia, Malaysia, Singapore, London and more: real fares we checked, non-stop airlines and today's live price.",
         "Air Ticket Price from Bangladesh", f"Real fares by route, non-stop airlines and live prices. Last updated: {UPDATED} (Asia/Dhaka). This site does not sell tickets.",
         "Air ticket price", "bn/air-ticket-price-bangladesh/", main, faqs, "Air Ticket Price from Bangladesh (2026)")

def build_hub_bn():
    rows = []
    for d, city, city_bn, slug, air, dac, ccu, *_ in ROUTES:
        name = a("/bn/" + slug + "/", f"{city_bn} ({d})", ext=False) if slug else f"{city_bn} ({d})"
        rows.append([name, usd(dac, "DAC", d), usd(ccu, "CCU", d) if d != "CCU" else "—", html.escape(air)])
    more = [[a("/bn/" + s + "/", cb, ext=False), html.escape(air)] for _, cb, s, air in MORE_GUIDES]
    main = "\n".join([
        H2("সংক্ষেপে"),
        P('<strong class="text-white">বাংলাদেশে বিমান টিকিটের কোনো নির্দিষ্ট দাম নেই — তারিখ, এয়ারলাইন আর বাকি সিট অনুযায়ী প্রতিদিন দাম বদলায়। '
          'নিচের টেবিলে আমাদের যাচাই করা আসল দাম, ঢাকা থেকে কোন এয়ারলাইন ননস্টপ যায়, আর আজকের লাইভ দামের লিংক আছে।</strong>'),
        H2("ঢাকা থেকে বিমান টিকিটের দাম (যাচাই: ৪ নভেম্বর ২০২৬)"),
        TABLE(["গন্তব্য", "ঢাকা থেকে", "কলকাতা থেকে", "ঢাকা থেকে ননস্টপ এয়ারলাইন"], rows),
        P('<span class="text-[11px] text-slate-500">১০ ডিসেম্বর ২০২৬ তারিখের ১ জন প্রাপ্তবয়স্কের ইকোনমি ওয়ান-ওয়ে সবচেয়ে কম ভাড়া, ৪ নভেম্বর ২০২৬-এ একটি পাবলিক ফেয়ার সার্চে দেখা। '
          'ট্যাক্সসহ; চেকড ব্যাগেজের খরচ আলাদা হতে পারে। আজকের লাইভ দাম দেখতে দামে চাপ দিন।</span>'),
        H2("কলকাতা থেকে কেন প্রায়ই সস্তা"),
        P('আমাদের যাচাই করা ১০টি আন্তর্জাতিক রুটের ৮টিতে কলকাতা থেকে শুরু করলে দাম ঢাকার চেয়ে কম ছিল — রিয়াদে ৪২% আর সিঙ্গাপুরে ৪১% পর্যন্ত। '
          'শুধু বুকিং সাইটের দেশ বদলালে দাম বদলায়নি। এর জন্য ভারতের ভিসা লাগবে, আর কলকাতা যাওয়ার খরচ যোগ করতে হবে। '
          + a("/cheaper-flights-from-kolkata/", "পুরো ফেয়ার স্টাডি পড়ুন (ইংরেজি) →", "text-sky-400 underline font-bold", ext=False)),
        H2("আরও রুট গাইড"),
        TABLE(["ঢাকা থেকে রুট", "ননস্টপ এয়ারলাইন"], more),
        H2("কীভাবে কম দামে টিকিট কাটবেন"),
        '            <ol class="list-decimal pl-5 space-y-1"><li>আপনার তারিখের আগে-পরে কয়েক দিন সার্চ করুন — সবচেয়ে সস্তা দিনে দাম অনেক কম হতে পারে।</li>'
        '<li>প্রথম দেখা দাম নয়, ব্যাগেজসহ মোট দাম তুলনা করুন।</li>'
        '<li>একই ফ্লাইট এয়ারলাইনের নিজের সাইটে দেখুন; যেখানে মোট দাম কম সেখানে কিনুন।</li>'
        '<li>বাংলাদেশি বুকিং সাইটে ব্যাংক কার্ডের অফার (যেমন EBL, City Amex) দেখুন।</li>'
        '<li>লম্বা যাত্রায় কলকাতা, দিল্লি, কাঠমান্ডু বা কলম্বো থেকে শুরু করে তুলনা করুন।</li></ol>',
        P(a("/bn/", "→ এখনই আপনার রুট ও তারিখ সার্চ করুন", "text-sky-400 underline font-bold", ext=False)),
    ])
    faqs = [
        ("ঢাকা থেকে দুবাই বিমান টিকিটের দাম কত?", "৪ নভেম্বর ২০২৬-এ ১০ ডিসেম্বরের জন্য সবচেয়ে কম ওয়ান-ওয়ে ভাড়া দেখেছি ঢাকা থেকে US$296 আর কলকাতা থেকে US$245। দাম প্রতিদিন বদলায় — আজকের দাম সার্চে দেখুন।"),
        ("বাংলাদেশ থেকে কোন এয়ারলাইন সবচেয়ে সস্তা?", "সবসময় একটি এয়ারলাইন সবচেয়ে সস্তা নয়। AirAsia, IndiGo, flydubai-এর মতো লো-কস্ট এয়ারলাইন ব্যাগেজ ছাড়া প্রায়ই কম; আপনার তারিখে ব্যাগেজসহ মোট দাম তুলনা করুন।"),
        ("অন্য দেশ থেকে টিকিট কাটলে কি সস্তা হয়?", "শুধু ওয়েবসাইটের দেশ বদলালে আমাদের যাচাইয়ে দাম বদলায়নি। ভারতের মতো কাছের দেশ থেকে ফ্লাইট শুরু করলে প্রায়ই সস্তা ছিল।"),
        ("Cheap Ticket Finder কি টিকিট বিক্রি করে?", "না। আমরা পার্টনার সাইট ও এয়ারলাইনের দাম তুলনা করে লিংক দিই। চূড়ান্ত দাম ও পেমেন্ট সেখানেই হয়।"),
    ]
    page("bn/air-ticket-price-bangladesh/", "bn",
         "বিমান টিকিটের দাম ২০২৬ — ঢাকা থেকে দুবাই, সৌদি, মালয়েশিয়া, লন্ডন | Cheap Ticket Finder",
         "ঢাকা থেকে দুবাই, সৌদি আরব, মালয়েশিয়া, সিঙ্গাপুর, লন্ডনসহ বিমান টিকিটের দাম: যাচাই করা আসল ভাড়া, ননস্টপ এয়ারলাইন ও আজকের লাইভ দাম।",
         "বিমান টিকিটের দাম — বাংলাদেশ থেকে", "রুট অনুযায়ী আসল ভাড়া, ননস্টপ এয়ারলাইন ও লাইভ দাম। সর্বশেষ আপডেট: ৫ নভেম্বর ২০২৬। এই সাইট টিকিট বিক্রি করে না।",
         "বিমান টিকিটের দাম", "air-ticket-price-bangladesh/", main, faqs, "বিমান টিকিটের দাম — বাংলাদেশ থেকে (২০২৬)")

def build_study():
    rows = []
    wins = 0
    for d, city, _, _, _, dac, ccu, dl, ktm, cmb, cgp in ROUTES:
        if d == "CCU":
            continue
        vals = {"DAC": dac, "CCU": ccu, "DEL": dl, "KTM": ktm, "CMB": cmb, "CGP": cgp}
        best = min((v, k) for k, v in vals.items() if v)
        if ccu and ccu < dac:
            wins += 1
        cells = [f"{city} ({d})"] + [(f"<b>US${v}</b>" if (v and k == best[1]) else (f"US${v}" if v else "—")) for k, v in vals.items()]
        rows.append(cells)
    main = "\n".join([
        H2("Key findings"),
        f'            <ul class="list-disc pl-5 space-y-1"><li>On <b>{wins} of 10</b> international routes, the cheapest fare starting in <b>Kolkata (CCU)</b> was lower than from Dhaka.</li>'
        '<li>Biggest savings from Kolkata: Riyadh −42%, Singapore −41%, Kuala Lumpur −35%, Bangkok −35%, Jeddah −24%, London −20%.</li>'
        '<li>Kolkata was <b>not</b> cheaper to Doha and New York on this date.</li>'
        '<li>Changing only the booking website\'s country (Bangladesh, India, UAE, Malaysia, Nepal, Sri Lanka, Vietnam, China, USA) gave the <b>same</b> fare for the same Dhaka flights.</li>'
        '<li>Colombo and Delhi were often the lowest of all, but they are far from Bangladesh, so the trip there usually removes the saving.</li></ul>',
        H2("Cheapest one-way fare by starting airport (US$)"),
        TABLE(["Destination", "Dhaka", "Kolkata", "Delhi", "Kathmandu", "Colombo", "Chattogram"], rows),
        P(f'<span class="text-[11px] text-slate-500">Bold = lowest for that destination. — = no fare returned.</span>'),
        H2("Method"),
        P(f'We searched one-way economy fares for 1 adult on 10 December 2026 from six South Asian airports to 10 popular destinations for Bangladeshi travellers, on a public fare search on {CHECKED}, '
          'and recorded the lowest fare including taxes. We repeated the Dhaka searches with the website set to nine different countries. On 5 November 2026 we re-opened the Kolkata searches on Aviasales; '
          'fares were similar or lower (for example London US$312, Toronto US$520), and Aviasales returned no results for Riyadh, which Trip.com listed from US$245.'),
        P("Limits: one travel date only; fares change daily; baggage rules differ; the cost of travelling to Kolkata (and an Indian visa) is not included."),
        H2("How to use this"),
        '            <ol class="list-decimal pl-5 space-y-1"><li>Search your trip on our homepage, then tap <b>“Check same trip from Kolkata”</b> in the results.</li>'
        '<li>Add the Dhaka–Kolkata cost (bus, train or a short flight) and an Indian visa.</li>'
        '<li>Book the two journeys separately with at least one night as a buffer.</li>'
        '<li>Buy only if the total is still lower than flying from Dhaka.</li></ol>',
        P(a("/", "→ Compare your own route now", "text-sky-400 underline font-bold", ext=False) + " · " + a("/air-ticket-price-bangladesh/", "Air ticket prices by route", ext=False)),
    ])
    faqs = [
        ("Is it cheaper to fly from Kolkata than from Dhaka?", f"Often, yes. On {wins} of 10 routes we checked for 10 December 2026 the cheapest fare from Kolkata was lower, by up to 42%. Add the cost of getting to Kolkata and an Indian visa before deciding."),
        ("Does buying on another country's website make the ticket cheaper?", "In our check, no. The same Dhaka flights showed the same fare when the booking website was set to nine different countries."),
        ("Do I need two tickets?", "Usually yes: one to Kolkata and one from Kolkata. Airlines do not protect a missed connection on separate tickets, so leave a buffer."),
    ]
    page("cheaper-flights-from-kolkata/", "en",
         "Dhaka vs Kolkata Flight Prices: Fare Study Nov 2026 | Cheap Ticket Finder",
         "Original fare study: is it cheaper to fly from Kolkata, Delhi, Kathmandu or Colombo than from Dhaka? Real fares for 10 routes, method and limits.",
         "Is it Cheaper to Fly from Kolkata than Dhaka?", f"Original fare study by Cheap Ticket Finder. Fares checked {CHECKED}; updated {UPDATED}.",
         "Dhaka vs Kolkata fare study", "", main, faqs, "Dhaka vs Kolkata flight prices: fare study, November 2026")

if __name__ == "__main__":
    build_hub_en()
    build_hub_bn()
    build_study()
