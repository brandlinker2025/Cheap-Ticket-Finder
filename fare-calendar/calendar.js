"use strict";
/**
 * Low Fare Calendar (English).
 * Reads the existing /api/fare-calendar endpoint (Travelpayouts cached direct one-way fares, USD).
 * Adds nothing server-side: no existing file is changed.
 */
(function () {
    const $ = id => document.getElementById(id);
    const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

    // "Today" in Dhaka so the first selectable month matches the site audience.
    const todayIso = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Dhaka" }).format(new Date());
    const minMonth = todayIso.slice(0, 7);
    const maxMonth = shiftMonth(minMonth, 11);

    const state = { month: minMonth, origin: "DAC", destination: "DXB", fares: new Map(), first: null, last: null, token: 0 };

    function shiftMonth(ym, delta) {
        const [y, m] = ym.split("-").map(Number);
        const d = new Date(Date.UTC(y, m - 1 + delta, 1));
        return d.getUTCFullYear() + "-" + String(d.getUTCMonth() + 1).padStart(2, "0");
    }
    const daysIn = ym => { const [y, m] = ym.split("-").map(Number); return new Date(Date.UTC(y, m, 0)).getUTCDate(); };
    const firstDow = ym => { const [y, m] = ym.split("-").map(Number); return new Date(Date.UTC(y, m - 1, 1)).getUTCDay(); };
    const pad = n => String(n).padStart(2, "0");
    const niceDate = iso => {
        const [y, m, d] = iso.split("-").map(Number);
        return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
    };

    function readRoute() {
        const [a, b] = $("pair").value.split("-");
        const back = $("dir").value === "back";
        state.origin = back ? b : a;
        state.destination = back ? a : b;
    }

    function showStatus(text, kind) {
        const box = $("status");
        box.className = kind === "err" ? "notice err" : kind === "warn" ? "notice" : "muted";
        box.textContent = text;
    }

    function skeleton() {
        const grid = $("cal");
        grid.className = "grid skel";
        grid.innerHTML = "";
        for (let i = 0; i < 35; i++) grid.insertAdjacentHTML("beforeend", '<div class="cell"><span class="d">&nbsp;</span><span class="p">&nbsp;</span></div>');
    }

    async function load() {
        const token = ++state.token;
        state.first = state.last = null;
        $("summary").hidden = true;
        $("legend").hidden = true;
        $("monthLabel").textContent = MONTHS[Number(state.month.slice(5)) - 1] + " " + state.month.slice(0, 4);
        $("prev").disabled = state.month <= minMonth;
        $("next").disabled = state.month >= maxMonth;
        $("go").disabled = true;
        showStatus("Loading fares…");
        skeleton();
        try {
            const query = new URLSearchParams({ origin: state.origin, destination: state.destination, month: state.month });
            const res = await fetch("/api/fare-calendar?" + query, { headers: { Accept: "application/json" } });
            if (token !== state.token) return; // a newer request replaced this one
            const body = await res.json().catch(() => ({}));
            if (!res.ok) throw new Error(body.error || "Fare data is unavailable right now.");
            state.fares = new Map();
            (body.fares || []).forEach(f => {
                // Keep only the cheapest fare per day.
                const old = state.fares.get(f.date);
                if (!old || f.price < old.price) state.fares.set(f.date, f);
            });
            render();
        } catch (err) {
            if (token !== state.token) return;
            $("cal").className = "grid";
            $("cal").innerHTML = "";
            showStatus((err && err.message) || "Fare data is unavailable right now. Please try again in a minute.", "err");
        } finally {
            if (token === state.token) $("go").disabled = false;
        }
    }

    function tiers(prices) {
        const sorted = [...prices].sort((a, b) => a - b);
        const lo = sorted[Math.floor(sorted.length / 3)];
        const hi = sorted[Math.floor((sorted.length * 2) / 3)];
        return p => (p <= lo ? "low" : p <= hi ? "mid" : "high");
    }

    function render() {
        const grid = $("cal");
        grid.className = "grid";
        grid.innerHTML = "";
        ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].forEach(d => grid.insertAdjacentHTML("beforeend", '<div class="dow">' + d + "</div>"));
        const entries = [...state.fares.values()].filter(f => f.date >= todayIso); // past days are never shown or ranked
        if (!entries.length) {
            showStatus("No recent direct fares found for this route and month. Try another month or route; some routes have no direct flights.", "warn");
            $("summary").hidden = true;
            $("legend").hidden = true;
            return;
        }
        showStatus("Showing the lowest recently found direct fare per day, in USD. Gaps mean no recent fare was found, not that no flight exists.");
        const tier = tiers(entries.map(f => f.price));
        const best = entries.reduce((a, b) => (b.price < a.price ? b : a));
        for (let i = 0; i < firstDow(state.month); i++) grid.insertAdjacentHTML("beforeend", '<div class="cell empty"></div>');
        for (let day = 1; day <= daysIn(state.month); day++) {
            const iso = state.month + "-" + pad(day);
            const fare = state.fares.get(iso);
            const btn = document.createElement("button");
            btn.type = "button";
            btn.dataset.date = iso;
            btn.className = "cell";
            if (fare && iso >= todayIso) {
                btn.classList.add(tier(fare.price));
                if (fare.date === best.date) btn.classList.add("best");
                btn.innerHTML = '<span class="d">' + day + '</span><span class="p">' + money.format(fare.price) + "</span>";
                btn.setAttribute("aria-label", niceDate(iso) + ", " + money.format(fare.price));
            } else {
                btn.classList.add("none");
                btn.disabled = true;
                btn.innerHTML = '<span class="d">' + day + '</span><span class="p">–</span>';
                btn.setAttribute("aria-label", niceDate(iso) + ", no fare found");
            }
            grid.appendChild(btn);
        }
        $("legend").hidden = false;
        paintSelection();
        summarise();
    }

    function range() {
        if (!state.first) return null;
        const a = state.first, b = state.last || state.first;
        return a <= b ? [a, b] : [b, a];
    }

    function paintSelection() {
        const r = range();
        document.querySelectorAll(".cell[data-date]").forEach(el => {
            const d = el.dataset.date;
            el.classList.toggle("sel", !!r && (d === r[0] || d === r[1]));
            el.classList.toggle("inrange", !!r && d >= r[0] && d <= r[1] && r[0] !== r[1]);
        });
    }

    function summarise() {
        const r = range();
        let list = [...state.fares.values()].filter(f => f.date >= todayIso);
        if (r) list = list.filter(f => f.date >= r[0] && f.date <= r[1]);
        list.sort((a, b) => a.price - b.price || (a.date < b.date ? -1 : 1));
        const top = list.slice(0, 5);
        $("summary").hidden = !top.length;
        if (!top.length) return;
        $("sumTitle").textContent = r && r[0] !== r[1] ? "Cheapest days between " + niceDate(r[0]) + " and " + niceDate(r[1]) : r ? "Selected day" : "Cheapest days this month";
        const ol = $("top");
        ol.innerHTML = "";
        top.forEach(f => {
            const li = document.createElement("li");
            li.textContent = niceDate(f.date) + ": " + money.format(f.price) + (f.airline ? " (" + f.airline + ")" : "");
            ol.appendChild(li);
        });
        const d = top[0].date; // DDMM for the Travelpayouts search deep link used elsewhere on the site
        const code = state.origin + d.slice(8) + d.slice(5, 7) + state.destination + "1";
        $("search").href = "/?" + new URLSearchParams({ flightSearch: code, origin_airports: "0", destination_airports: "0" }) + "#wl-flight-results";
        $("search").textContent = "Search live fares for " + niceDate(d);
    }

    $("cal").addEventListener("click", e => {
        const el = e.target.closest(".cell[data-date]");
        if (!el || el.disabled) return;
        const d = el.dataset.date;
        if (!state.first || state.last) { state.first = d; state.last = null; } else { state.last = d; }
        paintSelection();
        summarise();
    });
    $("route").addEventListener("submit", e => { e.preventDefault(); readRoute(); load(); });
    $("pair").addEventListener("change", () => { readRoute(); load(); });
    $("dir").addEventListener("change", () => { readRoute(); load(); });
    $("prev").addEventListener("click", () => { if (state.month > minMonth) { state.month = shiftMonth(state.month, -1); load(); } });
    $("next").addEventListener("click", () => { if (state.month < maxMonth) { state.month = shiftMonth(state.month, 1); load(); } });

    readRoute();
    load();
})();
