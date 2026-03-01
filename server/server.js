require('dotenv').config();
const express = require('express');
const cors = require('cors');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();
const PORT = process.env.PORT || 3000;
const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:5000';

app.use(cors({ origin: '*' }));
app.use(express.json());

const PRODUCT = {
  name: 'The Quiet Operator Playbook',
  description: 'The step-by-step playbook for turning AI skills into recurring revenue.',
  price: 2900, // $29.00 in cents
};

app.post('/create-checkout-session/playbook', async (req, res) => {
  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: PRODUCT.name,
              description: PRODUCT.description,
            },
            unit_amount: PRODUCT.price,
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
