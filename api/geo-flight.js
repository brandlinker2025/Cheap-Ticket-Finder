const axios = require('axios');
const { HttpsProxyAgent } = require('https-proxy-agent');
const Amadeus = require('amadeus');

const proxyList = [
  'http://14.161.47.180:8080',
  'http://117.3.73.228:80',
  'http://89.41.168.27:8080',
  'http://185.117.88.20:80',
];

const amadeus = new Amadeus({
  clientId: process.env.AMADEUS_CLIENT_ID,
  clientSecret: process.env.AMADEUS_CLIENT_SECRET
});

async function fetchWithProxyFallback(apiCallFunction) {
  for (const proxyUrl of proxyList) {
    try {
      console.log(`Trying proxy: ${proxyUrl}`);
      const agent = new HttpsProxyAgent(proxyUrl);
      const result = await apiCallFunction(agent);
      return { success: true, data: result, proxyUsed: proxyUrl };
    } catch (error) {
      console.warn(`Proxy failed: ${error.message}`);
    }
  }
  try {
    console.log('Fallback to direct');
    const result = await apiCallFunction(null);
    return { success: true, data: result, proxyUsed: 'Direct' };
  } catch (err) {
    throw new Error(`All failed: ${err.message}`);
  }
}

module.exports = async (req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const origin = req.query.origin || 'DAC';
    const destination = req.query.destination || 'BKK';
    const date = req.query.date || new Date().toISOString().split('T')[0];
    const currency = req.query.currency || 'EUR';

    const flightSearchLogic = async (agent) => {
      const config = agent ? { httpAgent: agent, httpsAgent: agent } : {};
      const response = await amadeus.shopping.flightOffersSearch.get({
        originLocationCode: origin,
        destinationLocationCode: destination,
        departureDate: date,
        adults: '1',
        currencyCode: currency,
        max: 5
      }, config);
      return response.data;
    };

    const flightResult = await fetchWithProxyFallback(flightSearchLogic);

    res.status(200).json({
      success: true,
      source: 'Geo-Pricing Engine',
      currency,
      proxy_used: flightResult.proxyUsed,
      data: flightResult.data
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};
