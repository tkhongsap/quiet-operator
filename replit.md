# The Quiet Operator Playbook

A product landing page with Stripe checkout backend for selling "The Quiet Operator Playbook" — a guide for AI developers who want to build real businesses.

## Project Structure

```
landing-page/       # Static frontend (HTML/CSS/JS)
  index.html        # Main landing page
  styles.css        # Styles
  script.js         # Frontend logic + Stripe checkout calls
  success.html      # Post-purchase success page

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

- `POST /create-checkout-session/:tier` — Creates a Stripe checkout session. Tier can be `early-bird` ($149) or `full-price` ($299)
- `GET /health` — Health check

## Products

- **Early Bird**: $149 (normally $299)
- **Full Price**: $299

## Setup Notes

- The frontend's `API_URL` in `script.js` points to the Replit public domain on port 3000
- CORS is configured to allow all origins (`*`) for Replit environment compatibility
- Deployment is configured as a static site (landing-page directory)
- The backend needs its own deployment or the API_URL should be updated when deploying
