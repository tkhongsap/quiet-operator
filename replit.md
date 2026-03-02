# The Quiet Operator Playbook

A product landing page with Stripe checkout backend for selling "The Quiet Operator Playbook" — a guide for AI developers who want to build real businesses.

## Project Structure

```
landing-page/       # Static frontend (HTML/CSS/JS)
  index.html        # Main landing page
  styles.css        # Styles
  script.js         # Frontend logic + Stripe checkout calls
  success.html      # Post-purchase success page (minimal: checkmark, Download PDF button, contact)

server/             # Node.js/Express backend
  server.js         # Express API server (Stripe checkout sessions)
  package.json      # Dependencies: express, cors, stripe, dotenv
  .env              # Environment variables (not committed)
  .env.example      # Example env file

content/            # Playbook content (markdown)
templates/          # Business templates (markdown)
marketing/          # Marketing copy (markdown)
case-studies/       # Research and case studies
```

## Architecture

- **Frontend**: Static HTML/CSS/JS served via `npx serve` on port 5000
- **Backend**: Express.js API on port 3000, handles Stripe checkout session creation
- **Payment**: Stripe Checkout (server-side session creation, client-side redirect)

## Workflows

- **Start application**: `npx serve landing-page -p 5000 -l tcp://0.0.0.0:5000` (port 5000, webview)
- **Backend API**: `cd server && node server.js` (port 3000, console)

## Environment Variables

Managed via Replit Secrets and Environment Variables:

- `STRIPE_SECRET_KEY` (secret) — Stripe secret key (sk_test_... for test mode)
- `STRIPE_PUBLISHABLE_KEY` (env var) — Stripe publishable key (pk_test_...)
- `CLIENT_URL` (env var) — Public URL of the frontend (Replit domain)
- `PORT` (env var) — Backend port (3000)

## API Endpoints

- `POST /create-checkout-session/playbook` — Creates a Stripe checkout session. Accepts optional `{ currency: "thb" }` body for local currency pricing
- `GET /pricing?currency=thb` — Returns pricing info for a given currency (amount, symbol, display string, supported currencies)
- `GET /health` — Health check

## Products

- **The Quiet Operator Playbook**: $29 USD (with locale currency support)

## Locale Currency Support

The frontend detects the user's timezone and maps it to a local currency. Supported currencies:
- USD ($29), THB (฿999), VND (₫749,000), SGD (S$39), MYR (RM129), PHP (₱1,599), IDR (Rp469,000), JPY (¥4,500), KRW (₩39,000), EUR (€27), GBP (£23)
- Prices are fixed per currency (not live exchange rates) and defined in server/server.js PRICING map
- Falls back to USD for unsupported timezones/currencies

## Setup Notes

- The frontend's `API_URL` in `script.js` points to the Replit public domain on port 3000
- CORS is configured to allow all origins (`*`) for Replit environment compatibility
- Deployment is configured as a static site (landing-page directory)
- The backend needs its own deployment or the API_URL should be updated when deploying
