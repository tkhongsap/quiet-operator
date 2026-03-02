if (require('fs').existsSync('.env')) require('dotenv').config();
const express = require('express');
const cors = require('cors');

if (!process.env.STRIPE_SECRET_KEY) {
  console.error('FATAL: STRIPE_SECRET_KEY is not set. Add it as a secret in the Replit Secrets tab.');
  process.exit(1);
}

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();
const PORT = process.env.PORT || 3000;
const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:5000';

app.use(cors({ origin: '*' }));
app.use(express.json());

const PRODUCT = {
  name: 'The Quiet Operator Playbook',
  description: 'The step-by-step playbook for turning AI skills into recurring revenue.',
};

const PRICING = {
  usd: { amount: 2900, symbol: '$', display: '$29' },
  thb: { amount: 99900, symbol: '฿', display: '฿999' },
  vnd: { amount: 74900000, symbol: '₫', display: '₫749,000' },
  sgd: { amount: 3900, symbol: 'S$', display: 'S$39' },
  myr: { amount: 12900, symbol: 'RM', display: 'RM129' },
  php: { amount: 159900, symbol: '₱', display: '₱1,599' },
  idr: { amount: 46900000, symbol: 'Rp', display: 'Rp469,000' },
  jpy: { amount: 4500, symbol: '¥', display: '¥4,500' },
  krw: { amount: 3900000, symbol: '₩', display: '₩39,000' },
  eur: { amount: 2700, symbol: '€', display: '€27' },
  gbp: { amount: 2300, symbol: '£', display: '£23' },
};

app.get('/pricing', (req, res) => {
  const currency = (req.query.currency || 'usd').toLowerCase();
  const pricing = PRICING[currency] || PRICING.usd;
  res.json({
    currency: PRICING[currency] ? currency : 'usd',
    amount: pricing.amount,
    symbol: pricing.symbol,
    display: pricing.display,
    supported: Object.keys(PRICING),
  });
});

app.post('/create-checkout-session/playbook', async (req, res) => {
  const requestedCurrency = (req.body.currency || 'usd').toLowerCase();
  const currency = PRICING[requestedCurrency] ? requestedCurrency : 'usd';
  const pricing = PRICING[currency];

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: currency,
            product_data: {
              name: PRODUCT.name,
              description: PRODUCT.description,
            },
            unit_amount: pricing.amount,
          },
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: `${CLIENT_URL}/success.html`,
      cancel_url: `${CLIENT_URL}/`,
    });

    res.json({ url: session.url });
  } catch (err) {
    console.error('Stripe error:', err.message);
    res.status(500).json({ error: 'Failed to create checkout session.' });
  }
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
