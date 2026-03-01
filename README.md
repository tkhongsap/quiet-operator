# The Quiet Operator Playbook — Landing Page + Stripe Checkout

## Project Structure

```
qop/
├── landing-page/          # Static frontend
│   ├── index.html         # Landing page
│   ├── styles.css         # Styles
│   ├── script.js          # Frontend JS (checkout + animations)
│   └── success.html       # Post-purchase thank you page
├── server/                # Node.js backend
│   ├── server.js          # Express + Stripe Checkout Sessions
│   ├── package.json       # Dependencies
│   └── .env               # Stripe secret key (DO NOT COMMIT)
├── content/               # Playbook content (Markdown)
├── templates/             # Deliverable templates
└── README.md              # This file
```

## Running Locally

### 1. Start the backend

```bash
cd server
npm install
npm start
# Server runs on http://localhost:4242
```

### 2. Serve the frontend

Use any static file server. For example:

```bash
cd landing-page
npx serve -l 5500
# Or: python3 -m http.server 5500
```

Open `http://localhost:5500` in your browser.

### 3. Test a purchase

Click any "Get the Playbook" button → redirects to Stripe Checkout (test mode).

Use Stripe test card: `4242 4242 4242 4242`, any future expiry, any CVC.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `STRIPE_SECRET_KEY` | Stripe secret key | (required) |
| `CLIENT_URL` | Frontend URL (for CORS + redirects) | `http://localhost:5500` |
| `PORT` | Backend port | `4242` |

## Switching from Test to Live Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Toggle from "Test" to "Live"
3. Replace `STRIPE_SECRET_KEY` in `server/.env` with your live secret key (`sk_live_...`)
4. Update `API_URL` in `landing-page/script.js` to your production backend URL
5. Update `CLIENT_URL` in `server/.env` to your production frontend URL

## Deploy to Replit

1. Create a new Replit → Import from GitHub or upload the `server/` directory
2. Set environment variables in Replit Secrets:
   - `STRIPE_SECRET_KEY` = your Stripe secret key
   - `CLIENT_URL` = your frontend URL (e.g., your Replit URL or custom domain)
3. The `landing-page/` can be served from the same Replit by adding `express.static`:
   ```js
   app.use(express.static('../landing-page'));
   ```
   Or deploy it separately on Vercel/Netlify/GitHub Pages.
4. Update `API_URL` in `script.js` to your Replit backend URL.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/create-checkout-session/early-bird` | Creates $149 checkout session |
| `POST` | `/create-checkout-session/full-price` | Creates $299 checkout session |
| `GET` | `/health` | Health check |
