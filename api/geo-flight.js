// Duffel offer lookup (server-side only). Fails closed:
// - no token          -> 503 not_configured (never sample data)
// - Duffel TEST token -> 503 test_mode (test-mode offers are not real fares and must never be shown)
// - bad input         -> 400
// Upstream errors are not echoed to the client.
const IATA = /^[A-Z]{3}$/;
const CURRENCIES = new Set(["USD", "EUR", "GBP", "BDT", "INR", "MYR", "AED", "SGD", "THB"]);

function validDate(s) {
  if (typeof s !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
  const d = new Date(s + "T00:00:00Z");
  if (isNaN(d) || d.toISOString().slice(0, 10) !== s) return false;
  const today = new Date(); today.setUTCHours(0, 0, 0, 0);
  const max = new Date(today); max.setUTCDate(max.getUTCDate() + 360);
  return d >= today && d <= max;
}

function parse(query) {
  const q = query || {};
  const origin = String(q.origin || "").trim().toUpperCase();
  const destination = String(q.destination || "").trim().toUpperCase();
  const date = String(q.date || "").trim();
  const currency = String(q.currency || "USD").trim().toUpperCase();
  if (!IATA.test(origin) || !IATA.test(destination) || origin === destination) return { error: "Invalid airport pair." };
  if (!validDate(date)) return { error: "Invalid or past departure date (YYYY-MM-DD, within 360 days)." };
  if (!CURRENCIES.has(currency)) return { error: "Unsupported currency." };
  return { origin, destination, date, currency };
}

async function geoFlight(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "GET") return res.status(405).json({ success: false, error: "Method not allowed" });
  const input = parse(req.query);
  if (input.error) return res.status(400).json({ success: false, error: input.error });

  const token = process.env.DUFFEL_ACCESS_TOKEN;
  if (!token) return res.status(503).json({ success: false, status: "not_configured", error: "Live flight offers are not configured." });
  if (/^duffel_test_/.test(token)) return res.status(503).json({ success: false, status: "test_mode", error: "Flight offer source is in test mode; no live prices are shown." });

  try {
    const response = await fetch("https://api.duffel.com/air/offer_requests?return_offers=true", {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json", "Duffel-Version": "v2", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ data: { slices: [{ origin: input.origin, destination: input.destination, departure_date: input.date }], passengers: [{ type: "adult" }] } }),
      signal: AbortSignal.timeout(10000)
    });
    if (!response.ok) return res.status(502).json({ success: false, status: "unavailable", error: "Flight offer source is unavailable." });
    const json = await response.json();
    const offers = (json.data && Array.isArray(json.data.offers) ? json.data.offers : []).filter((o) => o && o.live_mode === true);
    return res.status(200).json({
      success: true,
      source: "Duffel",
      fetched_at: new Date().toISOString(),
      data: offers.slice(0, 5).map((o) => ({
        total_amount: o.total_amount,
        total_currency: o.total_currency,
        owner: o.owner && o.owner.name ? String(o.owner.name).slice(0, 80) : null,
        expires_at: o.expires_at || null
      }))
    });
  } catch (e) {
    return res.status(502).json({ success: false, status: "unavailable", error: "Flight offer source is unavailable." });
  }
}
module.exports = geoFlight;
module.exports.parse = parse;
