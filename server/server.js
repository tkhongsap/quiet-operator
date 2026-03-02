if (require('fs').existsSync('.env')) require('dotenv').config();
const path = require('path');
const express = require('express');
const cors = require('cors');
const { Resend } = require('resend');

if (!process.env.STRIPE_SECRET_KEY) {
  console.error('FATAL: STRIPE_SECRET_KEY is not set. Add it as a secret in the Replit Secrets tab.');
  process.exit(1);
}

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const resend = process.env.RESEND_API_KEY ? new Resend(process.env.RESEND_API_KEY) : null;

if (!resend) {
  console.warn('WARNING: RESEND_API_KEY is not set. Confirmation emails will not be sent.');
}

const app = express();
const PORT = process.env.PORT || 5000;
const CLIENT_URL = process.env.CLIENT_URL || `http://localhost:${PORT}`;

function getBaseUrl(req) {
  if (process.env.CLIENT_URL) return process.env.CLIENT_URL;
  const proto = req.headers['x-forwarded-proto'] || req.protocol || 'https';
  const host = req.headers['x-forwarded-host'] || req.headers.host;
  return `${proto}://${host}`;
}

app.use(cors({ origin: '*' }));
app.use(express.json());

app.use(express.static(path.join(__dirname, '..', 'landing-page')));

const PRODUCT = {
  en: {
    name: 'The Quiet Operator Playbook',
    description: 'The step-by-step playbook for turning AI skills into recurring revenue.',
  },
  th: {
    name: 'The Quiet Operator Playbook',
    description: 'Playbook แบบ step-by-step สำหรับเปลี่ยนทักษะ AI ให้เป็นรายได้ประจำ',
  },
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

const fulfilledSessions = new Set();

function buildConfirmationEmail(baseUrl) {
  const pdfUrl = `${baseUrl}/The_Quiet_Operator.pdf`;
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:40px 20px;">
    <tr>
      <td align="center">
        <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
          <tr>
            <td align="center" style="padding-bottom:32px;">
              <h1 style="margin:0;font-size:28px;font-weight:700;color:#d4a843;font-style:italic;">You're in</h1>
            </td>
          </tr>
          <tr>
            <td style="background:#ffffff;border-radius:8px;padding:40px 36px;">
              <p style="margin:0 0 8px;font-size:15px;color:#1a1a1a;line-height:1.6;">
                Thanks for grabbing <strong>The Quiet Operator Playbook</strong>.
              </p>
              <p style="margin:0 0 32px;font-size:15px;color:#1a1a1a;line-height:1.6;">
                Click below to download your copy:
              </p>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:32px;">
                    <a href="${pdfUrl}" style="display:inline-block;background:#d4a843;color:#0a0a0a;font-size:15px;font-weight:600;text-decoration:none;padding:14px 32px;border-radius:6px;">Download PDF</a>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 16px;font-size:13px;color:#666;line-height:1.6;">
                You can also access your thank-you page anytime at:<br>
                <a href="${baseUrl}/success.html" style="color:#d4a843;text-decoration:none;">${baseUrl}/success.html</a>
              </p>
              <p style="margin:0;font-size:13px;color:#1a1a1a;line-height:1.6;">
                <strong>Need help?</strong> Reply to this email or find me on X — I personally answer questions from playbook buyers.
              </p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-top:28px;">
              <p style="margin:0;font-size:12px;color:#666;">
                Questions? <a href="https://x.com/quietoperator67" style="color:#666;text-decoration:none;">@quietoperator67</a> · <a href="mailto:tk7p7103@gmail.com" style="color:#666;text-decoration:none;">tk7p7103@gmail.com</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;
}

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
  const locale = req.body.locale === 'th' ? 'th' : 'en';
  const product = PRODUCT[locale];

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: currency,
            product_data: {
              name: product.name,
              description: product.description,
            },
            unit_amount: pricing.amount,
          },
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: `${getBaseUrl(req)}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${getBaseUrl(req)}/`,
    });

    res.json({ url: session.url });
  } catch (err) {
    console.error('Stripe error:', err.message);
    res.status(500).json({ error: 'Failed to create checkout session.' });
  }
});

app.post('/fulfill', async (req, res) => {
  const { session_id } = req.body;

  if (!session_id) {
    return res.status(400).json({ error: 'Missing session_id' });
  }

  if (fulfilledSessions.has(session_id)) {
    return res.json({ status: 'already_sent' });
  }

  try {
    const session = await stripe.checkout.sessions.retrieve(session_id);

    if (session.payment_status !== 'paid') {
      return res.status(400).json({ error: 'Payment not completed' });
    }

    const customerEmail = session.customer_details?.email;
    if (!customerEmail) {
      return res.status(400).json({ error: 'No customer email found' });
    }

    if (!resend) {
      console.warn('Resend not configured — skipping email to', customerEmail);
      fulfilledSessions.add(session_id);
      return res.json({ status: 'skipped', reason: 'email_not_configured' });
    }

    await resend.emails.send({
      from: 'Quiet Operator <onboarding@resend.dev>',
      to: customerEmail,
      subject: "You're in — here's your playbook",
      html: buildConfirmationEmail(getBaseUrl(req)),
    });

    console.log('Confirmation email sent to', customerEmail);
    fulfilledSessions.add(session_id);

    res.json({ status: 'sent', email: customerEmail });
  } catch (err) {
    console.error('Fulfill error:', err.message);
    res.status(500).json({ error: 'Failed to fulfill order' });
  }
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});
