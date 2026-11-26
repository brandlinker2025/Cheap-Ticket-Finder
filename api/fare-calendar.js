module.exports = async function fareCalendar(req, res) {
    if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });
    const q = req.query || {};
    const origin = typeof q.origin === "string" ? q.origin.trim().toUpperCase() : q.origin;
    const destination = typeof q.destination === "string" ? q.destination.trim().toUpperCase() : q.destination;
    const month = q.month;
    if (![origin, destination].every(code => typeof code === "string" && /^[A-Z]{3}$/.test(code)) ||
        origin === destination || typeof month !== "string" || !/^20\d{2}-(0[1-9]|1[0-2])$/.test(month)) {
        return res.status(400).json({ error: "Invalid airport pair or month." });
    }
    const token = process.env.TRAVELPAYOUTS_API_TOKEN;
    if (!token) return res.status(503).json({ error: "Fare data is not connected.", status: "not_configured" });

    const params = new URLSearchParams({
        origin, destination, departure_at: month, currency: "usd", one_way: "true",
        direct: "true", limit: "100", sorting: "price"
    });
    try {
        const response = await fetch("https://api.travelpayouts.com/aviasales/v3/prices_for_dates?" + params, {
            headers: { "X-Access-Token": token }, signal: AbortSignal.timeout(8000)
        });
        if (!response.ok) return res.status(502).json({ error: "Fare source temporarily unavailable." });
        const result = await response.json();
        if (!result.success || result.currency?.toLowerCase() !== "usd" || !Array.isArray(result.data)) {
            return res.status(502).json({ error: "Fare source returned an unexpected response." });
        }
        const fares = result.data.filter(row =>
            row.origin_airport === origin && row.destination_airport === destination &&
            row.transfers === 0 && !row.return_at && Number.isFinite(row.price) && row.price > 0 &&
            typeof row.departure_at === "string" && row.departure_at.startsWith(month + "-")
        ).map(row => {
            const out = { date: row.departure_at.slice(0, 10), price: row.price, airline: typeof row.airline === "string" ? row.airline.slice(0, 3) : null };
            // Pass through the upstream "found at" time only when the source actually sends it.
            if (typeof row.found_at === "string" && !isNaN(Date.parse(row.found_at))) out.found_at = row.found_at;
            return out;
        });
        res.setHeader("Vercel-CDN-Cache-Control", "public, s-maxage=900");
        return res.status(200).json({
            currency: "USD",
            source: "Travelpayouts Data API (cached Aviasales search results)",
            source_url: "https://www.travelpayouts.com/",
            fetched_at: new Date().toISOString(),
            max_cache_seconds: 900,
            fares
        });
    } catch {
        return res.status(502).json({ error: "Fare source temporarily unavailable." });
    }
};
