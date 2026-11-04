const axios = require('axios');

module.exports = async (req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const origin = req.query.origin || 'DAC';
    const destination = req.query.destination || 'BKK';
    const date = req.query.date || new Date().toISOString().split('T')[0];
    const currency = req.query.currency || 'EUR';

    const response = await axios.post(
      'https://api.duffel.com/air/offer_requests',
      {
        data: {
          slices: [
            {
              origin,
              destination,
              departure_date: date
            }
          ],
          passengers: [{ type: 'adult' }],
          currency
        }
      },
      {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Duffel-Version': 'v2',
          'Authorization': `Bearer ${process.env.DUFFEL_ACCESS_TOKEN}`
        }
      }
    );

    const offers = response.data?.data?.offers || [];

    res.status(200).json({
      success: true,
      source: 'Duffel Geo-Pricing',
      currency,
      data: offers.slice(0, 5)
    });
  } catch (error) {
    console.error(error.response?.data || error.message);
    res.status(500).json({
      success: false,
      error: error.response?.data?.errors?.[0]?.message || error.message
    });
  }
};
