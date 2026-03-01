# Pricing Calculator Worksheet

> **Use this worksheet to calculate your pricing for any client engagement.** Fill in the inputs, follow the formulas, and arrive at a recommended setup fee and monthly retainer. All amounts in **USD**.

---

## Step 1: Quantify the Client's Pain

*Get these numbers during your discovery call. Ask directly — clients usually know.*

| Input | Value | Notes |
|-------|-------|-------|
| **Hours saved per week** | _____ hrs | How many hours/week does the manual process take? |
| **Number of staff doing this task** | _____ people | How many people touch this workflow? |
| **Total weekly hours** | _____ hrs | = Hours saved × Staff count |
| **Client's hourly labor cost** | $_____ /hr | Include salary + benefits + overhead. If unknown, estimate $25-40/hr for admin staff, $50-100/hr for professionals |
| **Weekly savings value** | $_____ | = Total weekly hours × Hourly labor cost |
| **Monthly savings value** | $_____ | = Weekly savings × 4.33 |
| **Annual savings value** | $_____ | = Monthly savings × 12 |

---

## Step 2: Calculate Your Costs

| Input | Value | Notes |
|-------|-------|-------|
| **AI API costs (monthly)** | $_____ /mo | Estimate: $15-40/mo per client for moderate volume (100-500 requests/day) |
| **Hosting costs (monthly)** | $_____ /mo | VPS or Railway: $5-20/mo |
| **Communication costs (monthly)** | $_____ /mo | SMS (Twilio), Email (SendGrid): $0-15/mo |
| **Total monthly operating cost** | $_____ /mo | = API + Hosting + Communication |
| **Your build time (hours)** | _____ hrs | First client: 40-80 hrs. After productizing: 8-20 hrs |
| **Your hourly rate (internal)** | $_____ /hr | What's your time worth? Use $75-150/hr as a baseline |
| **Total build cost** | $_____ | = Build time × Your hourly rate |

---

## Step 3: Apply the 10x ROI Rule

**The Rule:** Your total annual price should be ≤10% of the total annual value you create. This makes the buying decision a no-brainer for the client.

| Calculation | Value |
|------------|-------|
| **Annual savings value** (from Step 1) | $_____ |
| **Maximum annual price** (10% of savings) | $_____ |
| **Maximum monthly retainer** (annual price ÷ 12) | $_____ /mo |

> **If 10% feels too low:** In practice, you can charge 20-33% of annual value and still close deals easily. 10x ROI (10%) is the gold standard. 3-5x ROI (20-33%) is still very attractive. Below 3x ROI — you'll face pushback.

---

## Step 4: Set Your Prices

### Setup Fee

| Factor | Calculation |
|--------|------------|
| **Your build cost** | $_____ |
| **Margin on setup** (1.5-2.5x) | × _____ |
| **Recommended setup fee** | **$_____** |

*Typical range: $2,000-$10,000 USD. Round to a clean number.*

### Monthly Retainer

| Factor | Calculation |
|--------|------------|
| **Your monthly operating costs** | $_____ |
| **Monthly support time (hrs)** | _____ × your hourly rate = $_____ |
| **Your total monthly cost** | $_____ |
| **Margin target** (aim for 80-90%) | ÷ (1 - margin %) |
| **Recommended monthly retainer** | **$_____** |

*Cross-check: Is this below your maximum monthly retainer from Step 3? If yes, you're priced right. If no, you may need to demonstrate more value or find a higher-value niche.*

---

## Step 5: Sanity Check

Run your numbers through these checks:

| Check | Target | Your Number | Pass? |
|-------|--------|-------------|-------|
| **Client ROI** (monthly savings ÷ monthly retainer) | ≥ 3x | _____x | ☐ |
| **Your gross margin** ((retainer - operating costs) ÷ retainer) | ≥ 80% | _____% | ☐ |
| **Setup fee payback** (setup fee ÷ monthly margin) | ≤ 2 months | _____ months | ☐ |
| **Price feels "obvious"** to the client | Yes | ☐ | ☐ |

**If all boxes are checked:** Send the proposal.
**If ROI < 3x:** Find more value to automate, or reduce your costs.
**If margin < 80%:** Raise the retainer or reduce operating costs.

---

## Worked Example

**Client:** A property management company with 5 admin staff spending 3 hours/day each on invoice processing.

| Input | Value |
|-------|-------|
| Hours saved/week | 15 hrs (3 hrs/day × 5 staff, automated down to ~30 min/day total) |
| Hourly labor cost | $28/hr |
| Monthly savings | 15 × $28 × 4.33 = **$1,819/mo** |
| Annual savings | **$21,830/yr** |
| API costs | $30/mo |
| Hosting | $10/mo |
| Operating cost | $40/mo |
| Build time | 50 hrs (first client in this niche) |
| Your rate | $100/hr |
| Build cost | $5,000 |

| Output | Value |
|--------|-------|
| **Setup fee** | $5,000 × 1.6 = **$8,000** → round to **$7,500** |
| **Max monthly retainer** (10% annual ÷ 12) | $21,830 × 10% ÷ 12 = **$182/mo** ← too low! |
| **Retainer at 25% of value** | $21,830 × 25% ÷ 12 = **$455/mo** |
| **Retainer at cost + margin** | $40 + ($3/hr × $100) ÷ (1 - 0.85) = ~**$500/mo** |
| **Final retainer** | **$500/mo** |
| **Client ROI** | $1,819 ÷ $500 = **3.6x** ✅ |
| **Your margin** | ($500 - $40) ÷ $500 = **92%** ✅ |

---

## Quick Reference: Typical Pricing by Niche

| Niche | Typical Setup Fee (USD) | Typical Monthly Retainer (USD) |
|-------|------------------------|-------------------------------|
| Dental/medical appointment automation | $2,000-5,000 | $500-1,500 |
| Legal document processing | $5,000-10,000 | $1,500-3,500 |
| Real estate lead qualification | $3,000-6,000 | $1,000-2,500 |
| Property management operations | $4,000-8,000 | $1,000-2,000 |
| Recruitment pipeline automation | $5,000-12,000 | $2,000-5,000 |
| Accounting/bookkeeping automation | $3,000-7,000 | $800-2,000 |

*These are starting points. Your actual pricing depends on the specific value delivered. Always do the math — don't just copy a number.*
