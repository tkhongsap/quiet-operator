# The Quiet Operator Playbook

A product landing page with Stripe checkout backend for selling "The Quiet Operator Playbook" — a guide for AI developers who want to build real businesses.

## Project Structure

```
landing-page/       # Static frontend (HTML/CSS/JS), served by Express
  index.html        # Main landing page
  styles.css        # Styles
  script.js         # Frontend logic + Stripe checkout calls
  success.html      # Post-purchase success page (minimal: checkmark, Download PDF button, contact)
  The_Quiet_Operator.pdf     # English PDF (copied from content/)
  The_Quiet_Operator_TH.pdf  # Thai PDF (copied from content/)
  serve.json        # Static server config (legacy, cleanUrls disabled)

server/             # Node.js/Express backend (serves both API + static files)
  server.js         # Express server: API endpoints + static file serving
  package.json      # Dependencies: express, cors, stripe, dotenv, resend

content/            # Source playbook PDFs (markdown + PDF)
templates/          # Business templates (markdown)
marketing/          # Marketing copy (markdown)
case-studies/       # Research and case studies
```

## Architecture

- **Single Express server** on port 5000: serves both static files (landing-page/) and API endpoints
- **Payment**: Stripe Checkout (server-side session creation, client-side redirect)
- **Email**: Resend API for post-purchase confirmation emails
- **Deployment**: Autoscale with `node server/server.js`
- API calls from frontend use relative paths (empty API_URL), no cross-origin issues

## Workflows

- **Start application**: `cd server && PORT=5000 node server.js` (port 5000, webview)

## Environment Variables

Managed via Replit Secrets and Environment Variables:

- `STRIPE_SECRET_KEY` (secret) — Stripe secret key (sk_test_... for test mode)
- `STRIPE_PUBLISHABLE_KEY` (env var) — Stripe publishable key (pk_test_...)
- `RESEND_API_KEY` (secret) — Resend API key for sending confirmation emails
- `CLIENT_URL` (optional) — Not set by default; server auto-detects from request headers. Only set if you need to override.

## API Endpoints

- `POST /create-checkout-session/playbook` — Creates a Stripe checkout session. Accepts optional `{ currency: "thb" }` body. Success URL includes `?session_id={CHECKOUT_SESSION_ID}`
- `POST /fulfill` — Sends confirmation email after payment. Accepts `{ session_id }`, validates Stripe payment status, sends styled email via Resend. Idempotent (in-memory guard)
- `GET /pricing?currency=thb` — Returns pricing info for a given currency
- `GET /health` — Health check

## Post-Purchase Email

- Triggered when user lands on success page with a valid Stripe session_id
- From: `Quiet Operator <onboarding@resend.dev>` (Resend default sender)
- Styled HTML email with "You're in" header, Download PDF button, thank-you page link, contact info
- PDF download links to `/download/The_Quiet_Operator.pdf` (served via dedicated endpoint with proper headers)
- Thai version also available at `/download/The_Quiet_Operator_TH.pdf`
- PDFs are served with Content-Type, Content-Disposition, and X-Content-Type-Options headers to prevent browser false-positive virus warnings
- Direct static access to PDF files is blocked (returns 404)
- Contact: @quietoperator67 on X · tk7p7103@gmail.com

## Products

- **The Quiet Operator Playbook**: $29 USD (with locale currency support)

## Locale Currency Support

The frontend detects the user's timezone and maps it to a local currency. Supported currencies:
- USD ($29), THB (฿999), VND (₫749,000), SGD (S$39), MYR (RM129), PHP (₱1,599), IDR (Rp469,000), JPY (¥4,500), KRW (₩39,000), EUR (€27), GBP (£23)
- Prices are fixed per currency (not live exchange rates) and defined in server/server.js PRICING map
- Falls back to USD for unsupported timezones/currencies

## Setup Notes

- Frontend API_URL is empty string (relative paths) — works because Express serves both API and static files
- CORS is configured to allow all origins (`*`)
- Deployment is autoscale: `node server/server.js` — same Express server handles everything
- CLIENT_URL is auto-detected from request headers if env var is not set (supports deployment without manual config)
- PDFs in landing-page/ are copies from content/ — if source PDFs are updated, re-copy them
