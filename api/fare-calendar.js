module.exports = async function fareCalendar(req, res) {
    if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });
    const { origin, destination, month } = req.query;
    if (![origin, destination].every(code => typeof code === "string" && /^[A-Z]{3}$/.test(code)) ||
        origin === destination || typeof month !== "string" || !/^20\d{2}-(0[1-9]|1[0-2])$/.test(month)) {
        return res.status(400).json({ error: "Invalid airport pair or month." });
    }
    const token = process.env.TRAVELPAYOUTS_API_TOKEN;
    if (!token) return res.status(503).json({ error: "Fare data is not connected." });

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
        ).map(row => ({ date: row.departure_at.slice(0, 10), price: row.price, airline: row.airline }));
        res.setHeader("Vercel-CDN-Cache-Control", "public, s-maxage=900");
        return res.status(200).json({ currency: "USD", fares });
    } catch {
        return res.status(502).json({ error: "Fare source temporarily unavailable." });
    }
};
