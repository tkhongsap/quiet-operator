# Chapter 4: Build Your First Solution — Three Paths

> *All dollar amounts in this playbook are in USD unless otherwise noted.*

---

Most people never start. They research frameworks, compare tools, read one more article — three months later, nothing shipped.

You are not going to do that. You found your niche. You validated the pain. Now you build the thing that makes it stop.

This chapter gives you three parallel paths to a working prototype. **Pick the one that matches your skills.** Developer takes Path A. Non-technical operator takes Path B. Someone who would rather hire takes Path C. All three end in the same place: a working automation that processes real data.

We use one example throughout — **invoice processing automation**. A small accounting firm receives 50-100 invoices per week via email. A bookkeeper manually extracts vendor name, amount, date, line items, categorizes expenses, and enters them into a Google Sheet. That takes 15-20 hours per week at a 3-5% error rate. Our automation does it in seconds at under 1% error — and the client pays $1,000-2,000/month for it.

Let's build it.

---

## Path A: Developer — Code It Yourself

For developers comfortable with Python, APIs, and the command line.

### Architecture Patterns

Four patterns cover 90% of what quiet operators build.

#### Pattern 1: Single Agent with Tools

```
Trigger: New email in invoices@client.com
→ Extract PDF attachment
→ OCR + LLM extraction (vendor, amount, date, line items)
→ Match against chart of accounts
→ If confidence > 85%: write to Google Sheet
→ If confidence < 85%: flag for human review
→ Send Slack summary either way
```

**Cost to run:** $20-40/month in API costs, $5-10 hosting. On a $1,500/month retainer: 96%+ margin. Not a typo.

#### Pattern 2: Multi-Agent Orchestration

```
Orchestrator reads state.json
→ Role #42: stage = "screening_complete"
→ Dispatch outreach_agent(role=42, shortlist=shortlist_42.json)
→ Role #43: stage = "research_in_progress"
→ Wait
→ Role #44: stage = "new"
→ Dispatch research_agent(role=44, spec=spec_44.json)
```

Do not rely on conversation history for state. Write it to files — debuggable, auditable, survives crashes. **Do not start here.** Build a single agent first. Decompose when complexity forces you to.

#### Pattern 3: Cron-Driven Autonomous Loops

```
Cron: 0 6 * * * (every day at 6 AM)
→ Fetch new inquiries from portal APIs
→ Score leads against criteria
→ Assign to agents (round-robin or rules-based)
→ Send morning briefing
→ Log results to daily_log.json
→ If errors: alert via Slack
```

Our invoice processor uses this — cron runs every 30 minutes, bookkeeper arrives at 9 AM to find everything categorized.

**Non-negotiable: monitoring.** Heartbeat alerts, error notifications, daily summaries. Here's what matters: silent failures kill trust. The automation is half the work. Monitoring is the other half.

#### Pattern 4: State-in-Files

Not a standalone pattern — a **principle**. AI agents are stateless. Your automation must remember what it processed.

```
/state/
  /acme_accounting/
    state.json          # Current automation state
    run_log.jsonl       # Append-only log of every run
    errors.jsonl        # Error log with timestamps
    config.json         # Client-specific configuration
```

Files beat databases at this stage: debuggable, portable, simple. Migrate when you hit 20+ clients. See Chapter 7.2 for scaling.

### The 72-Hour Build Sprint

#### Hours 0-8: Scope and Design

Document: trigger (new email with PDF), input (various invoice formats), processing (extract and categorize), output (Google Sheet + Slack), failure mode (confidence < 85% routes to review). Get 20 real invoices from the client. Write a one-page scope doc, get sign-off, then code.

#### Hours 8-24: Build the Core Pipeline

**Step 1: Gmail Integration**

```python
# gmail_client.py
import base64
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
           'https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_unprocessed_emails(service, after_timestamp):
    """Fetch emails with PDF attachments received after the given timestamp."""
    query = f'has:attachment filename:pdf after:{after_timestamp}'
    results = service.users().messages().list(
        userId='me', q=query, maxResults=50
    ).execute()
    return results.get('messages', [])

def download_attachment(service, message_id, attachment_id, filename):
    """Download a PDF attachment and save to disk."""
    attachment = service.users().messages().attachments().get(
        userId='me', messageId=message_id, id=attachment_id
    ).execute()
    file_data = base64.urlsafe_b64decode(attachment['data'])
    filepath = f'./tmp/{filename}'
    with open(filepath, 'wb') as f:
        f.write(file_data)
    return filepath
```

**Step 2: Invoice Extraction with Claude**

```python
# invoice_extractor.py
import anthropic
import json
import base64

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

EXTRACTION_PROMPT = """You are an invoice data extraction specialist. Extract the following fields from this invoice:

1. vendor_name: The company or person who issued the invoice
2. invoice_number: The invoice number/ID
3. invoice_date: Date of the invoice (YYYY-MM-DD format)
4. due_date: Payment due date (YYYY-MM-DD format), or null if not specified
5. line_items: Array of items, each with description, quantity, unit_price, and total
6. subtotal: Pre-tax total
7. tax_amount: Tax amount, or 0 if not specified
8. total_amount: Final total including tax
9. currency: Currency code (USD, THB, etc.)

Return ONLY valid JSON. No explanation. No markdown.

Also include a "confidence" field (0.0 to 1.0) indicating how confident you are in the extraction accuracy. If the document is blurry, handwritten, or in an unusual format, lower the confidence.

Example output:
{
  "vendor_name": "Acme Corp",
  "invoice_number": "INV-2026-001",
  "invoice_date": "2026-01-15",
  "due_date": "2026-02-15",
  "line_items": [
    {"description": "Consulting services", "quantity": 10, "unit_price": 150.00, "total": 1500.00}
  ],
  "subtotal": 1500.00,
  "tax_amount": 105.00,
  "total_amount": 1605.00,
  "currency": "USD",
  "confidence": 0.95
}"""

def extract_invoice_data(pdf_path: str) -> dict:
    """Extract structured data from an invoice PDF using Claude."""
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode('utf-8')

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64
                    }
                },
                {
                    "type": "text",
                    "text": EXTRACTION_PROMPT
                }
            ]
        }]
    )

    result = json.loads(response.content[0].text)
    return result
```

**Step 3: Expense Categorization**

```python
# categorizer.py
import anthropic
import json

client = anthropic.Anthropic()

def categorize_expense(invoice_data: dict, chart_of_accounts: list[str]) -> dict:
    """Categorize an invoice against the client's chart of accounts."""
    prompt = f"""You are an accounting categorization specialist.

Given this invoice data:
- Vendor: {invoice_data['vendor_name']}
- Description: {json.dumps(invoice_data['line_items'])}
- Total: {invoice_data['total_amount']} {invoice_data['currency']}

And this chart of accounts:
{json.dumps(chart_of_accounts, indent=2)}

Assign the most appropriate expense category for each line item.

Return JSON:
{{
  "category": "the primary expense category from the chart of accounts",
  "reasoning": "one sentence explaining why",
  "confidence": 0.0 to 1.0
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)
```

**Step 4: Google Sheets Output**

```python
# sheets_writer.py
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_client():
    creds = Credentials.from_service_account_file(
        'service_account.json', scopes=SCOPES
    )
    return gspread.authorize(creds)

def write_invoice_to_sheet(spreadsheet_id: str, invoice_data: dict,
                            category_data: dict, sheet_name: str = "Processed"):
    """Write extracted invoice data to Google Sheets."""
    gc = get_sheets_client()
    sheet = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)

    row = [
        invoice_data.get('invoice_date', ''),
        invoice_data.get('vendor_name', ''),
        invoice_data.get('invoice_number', ''),
        invoice_data.get('total_amount', 0),
        invoice_data.get('currency', 'USD'),
        category_data.get('category', 'Uncategorized'),
        category_data.get('confidence', 0),
        invoice_data.get('due_date', ''),
        category_data.get('reasoning', '')
    ]
    sheet.append_row(row, value_input_option='USER_ENTERED')
```

**Step 5: The Main Pipeline**

```python
# main.py
import json
import os
import time
from datetime import datetime, timezone
from gmail_client import get_gmail_service, get_unprocessed_emails, download_attachment
from invoice_extractor import extract_invoice_data
from categorizer import categorize_expense
from sheets_writer import write_invoice_to_sheet
from notifications import send_slack_notification

# Load client config
with open('config.json') as f:
    config = json.load(f)

# Load state
state_file = 'state.json'
if os.path.exists(state_file):
    with open(state_file) as f:
        state = json.load(f)
else:
    state = {
        "last_check": "2026/01/01",
        "processed_ids": [],
        "stats": {"total": 0, "auto": 0, "review": 0}
    }

CONFIDENCE_THRESHOLD = 0.85

def process_invoices():
    gmail = get_gmail_service()
    messages = get_unprocessed_emails(gmail, state['last_check'])

    processed = 0
    flagged = 0
    errors = []

    for msg_meta in messages:
        msg_id = msg_meta['id']
        if msg_id in state['processed_ids']:
            continue

        try:
            # Get full message and find PDF attachments
            msg = gmail.users().messages().get(userId='me', id=msg_id).execute()
            parts = msg.get('payload', {}).get('parts', [])

            for part in parts:
                filename = part.get('filename', '')
                if not filename.lower().endswith('.pdf'):
                    continue

                att_id = part['body'].get('attachmentId')
                if not att_id:
                    continue

                # Download and process
                pdf_path = download_attachment(gmail, msg_id, att_id, filename)
                invoice_data = extract_invoice_data(pdf_path)
                category = categorize_expense(
                    invoice_data, config['chart_of_accounts']
                )

                # Combine confidence scores
                overall_confidence = min(
                    invoice_data.get('confidence', 0),
                    category.get('confidence', 0)
                )

                if overall_confidence >= CONFIDENCE_THRESHOLD:
                    write_invoice_to_sheet(
                        config['spreadsheet_id'], invoice_data, category,
                        sheet_name="Processed"
                    )
                    processed += 1
                else:
                    write_invoice_to_sheet(
                        config['spreadsheet_id'], invoice_data, category,
                        sheet_name="Needs Review"
                    )
                    flagged += 1

                # Clean up temp file
                os.remove(pdf_path)

            state['processed_ids'].append(msg_id)

        except Exception as e:
            errors.append({
                "message_id": msg_id,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    # Update state
    state['last_check'] = datetime.now(timezone.utc).strftime('%Y/%m/%d')
    state['stats']['total'] += processed + flagged
    state['stats']['auto'] += processed
    state['stats']['review'] += flagged

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Log the run
    with open('run_log.jsonl', 'a') as f:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processed": processed,
            "flagged": flagged,
            "errors": len(errors)
        }
        f.write(json.dumps(log_entry) + '\n')

    # Notify
    summary = (
        f"📄 Invoice run complete: {processed} auto-processed, "
        f"{flagged} flagged for review"
    )
    if errors:
        summary += f", {len(errors)} errors"
    send_slack_notification(config['slack_webhook'], summary)

    if errors:
        with open('errors.jsonl', 'a') as f:
            for err in errors:
                f.write(json.dumps(err) + '\n')

if __name__ == '__main__':
    process_invoices()
```

**Step 6: Slack Notifications**

```python
# notifications.py
import requests

def send_slack_notification(webhook_url: str, message: str):
    """Send a notification to Slack via webhook."""
    requests.post(webhook_url, json={"text": message}, timeout=10)
```

**Step 7: Configuration File**

```json
{
  "client_name": "acme_accounting",
  "gmail_inbox": "invoices@acmeaccounting.com",
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
  "slack_webhook": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX",
  "chart_of_accounts": [
    "Office Supplies",
    "Software & Subscriptions",
    "Professional Services",
    "Travel & Entertainment",
    "Utilities",
    "Rent & Facilities",
    "Insurance",
    "Marketing & Advertising",
    "Equipment",
    "Miscellaneous"
  ]
}
```

**Step 8: Cron Setup**

```bash
# Run every 30 minutes during business hours
*/30 8-18 * * 1-5 cd /home/deploy/invoice-processor && python main.py >> cron.log 2>&1
```

#### Hours 24-40: Harden the Pipeline

```python
# retry.py
import time
import functools

def retry(max_attempts=3, backoff_base=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = backoff_base ** attempt
                    time.sleep(wait)
        return wrapper
    return decorator
```

#### Hours 40-56: Reporting Layer

```python
# monthly_report.py
import json
from datetime import datetime

def generate_monthly_report(client_name: str, run_log_path: str,
                             avg_minutes_per_invoice: float = 8.0,
                             hourly_labor_cost: float = 25.0) -> str:
    """Generate a monthly ROI report from run logs."""
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_processed = 0
    total_flagged = 0
    total_errors = 0

    with open(run_log_path) as f:
        for line in f:
            entry = json.loads(line)
            entry_date = datetime.fromisoformat(entry['timestamp'])
            if entry_date >= month_start:
                total_processed += entry.get('processed', 0)
                total_flagged += entry.get('flagged', 0)
                total_errors += entry.get('errors', 0)

    total_items = total_processed + total_flagged
    hours_saved = (total_items * avg_minutes_per_invoice) / 60
    money_saved = hours_saved * hourly_labor_cost
    error_rate = (total_errors / total_items * 100) if total_items > 0 else 0

    report = f"""
📊 Monthly Automation Report — {client_name}
Period: {month_start.strftime('%B %Y')}

ACTIVITY
  Invoices auto-processed:  {total_processed}
  Flagged for review:       {total_flagged}
  Total handled:            {total_items}

TIME SAVED
  Avg processing time (manual): {avg_minutes_per_invoice} min/invoice
  Total time saved:             {hours_saved:.1f} hours
  Equivalent labor cost:        ${money_saved:,.0f}

QUALITY
  Auto-processed:  {total_processed}/{total_items} ({total_processed/total_items*100:.0f}% if total_items else 0)
  Error rate:      {error_rate:.1f}%

ROI
  Monthly retainer:    $1,500
  Monthly savings:     ${money_saved:,.0f}
  Return:              {money_saved/1500:.1f}x
"""
    return report
```

#### Hours 56-72: Test against real client data. Check every output. Deploy.

### TDD: Write Failing Tests First

```python
# test_extractor.py
import pytest
from invoice_extractor import extract_invoice_data

def test_extracts_vendor_name():
    result = extract_invoice_data('test_fixtures/sample_invoice_1.pdf')
    assert result['vendor_name'] is not None
    assert len(result['vendor_name']) > 0

def test_extracts_total_as_number():
    result = extract_invoice_data('test_fixtures/sample_invoice_1.pdf')
    assert isinstance(result['total_amount'], (int, float))
    assert result['total_amount'] > 0

def test_confidence_below_threshold_for_blurry_scan():
    result = extract_invoice_data('test_fixtures/blurry_scan.pdf')
    assert result['confidence'] < 0.85

def test_handles_thai_invoice():
    """Thai invoices with mixed Thai-English text — critical for SEA operators."""
    result = extract_invoice_data('test_fixtures/thai_invoice.pdf')
    assert result['vendor_name'] is not None
    assert result['currency'] in ['THB', 'USD']
```

Write tests first. Watch them fail. Make them pass. That Thai invoice test matters — in Southeast Asia, multilingual extraction is a core requirement.

---

## When AI Gets It Wrong: Building Safeguards

AI will make mistakes. Regularly. The question is whether your system catches bad output before anyone gets hurt. This section determines whether your client trusts you for twelve months or fires you after three.

### Confidence Thresholds

A single threshold is not enough. Use three tiers:
- **High (>0.85):** Auto-process. No human review.
- **Medium (0.60-0.85):** Process but flag for human verification within 24 hours.
- **Low (<0.60):** Route to human. Automation does not act.

Start conservative. Loosen as you gather accuracy data.

### Human-Review Queues

Build a review queue into every automation — even a "Needs Review" tab in a Google Sheet. Safety net, training data source, trust builder.

### Output Validation

Validate before AI output reaches client systems. Type checking (is the amount a number?), range checking (is a $500,000 invoice from a paper supplier plausible?), consistency checking (does the vendor match a known vendor?).

### Audit Trails

Log every AI decision: input, output, confidence, action taken. Not optional. When a client asks "why was this categorized as 'Travel'?" — the audit trail lets you answer, fix, prevent recurrence.

### Bounded Actions

Never let AI take irreversible actions without human approval. Draft an email but do not send it. Categorize an expense but do not submit a tax filing. Score a resume but do not reject a candidate. AI recommends. Humans decide.

---

### Tech Stack Summary (Path A)

| Layer | What I Recommend | Cost |
|-------|---------------|------|
| AI | Claude API (Sonnet for extraction, Haiku for categorization) | $15-30/mo |
| Language | Python 3.11+ | Free |
| Email | Gmail API | Free |
| Output | Google Sheets API | Free |
| Notifications | Slack webhooks | Free |
| Hosting | Railway or a $5 VPS | $5-20/mo |
| Monitoring | Sentry (free tier) + Slack alerts | $0 |
| Scheduling | Cron | Free |
| **Total** | | **$20-50/mo** |

Margins reference Chapter 1.6 — they are excellent.

---

## Path B: No-Code — Build It in n8n

Same problem. Zero code. I recommend n8n — self-hosting gives full control and zero per-operation costs. Make.com ($9-16/mo) for the easiest learning curve, Zapier ($20-49/mo) for the most integrations.

### Invoice Processing in n8n

**Set up n8n:**

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

Or use n8n Cloud (free tier: 2,500 executions/month).

**The workflow:**

```
[Gmail Trigger] → [Extract Attachments] → [AI Agent: Extract Data] → [IF: Confidence Check]
    → High confidence → [Google Sheets: Write to Processed]
    → Low confidence  → [Google Sheets: Write to Review]
→ [Slack: Send Summary]
```

**Gmail Trigger:** Connect via OAuth, filter by Label = "Invoices" with attachments, poll every 5 minutes.

**AI Agent node:** Select Claude (Anthropic):

```
You are an invoice data extraction specialist. Extract the following from this invoice document:

1. vendor_name
2. invoice_number
3. invoice_date (YYYY-MM-DD)
4. due_date (YYYY-MM-DD, or null)
5. line_items (array of: description, quantity, unit_price, total)
6. subtotal
7. tax_amount (0 if not shown)
8. total_amount
9. currency (USD, THB, etc.)
10. confidence (0.0-1.0)

Return ONLY valid JSON. No explanation.
```

Pass PDF data from previous node. Set Output Parsing to JSON.

**IF node:** Condition: `{{ $json.confidence }}` > `0.85`. True: auto-process. False: flag for review.

**Google Sheets:** One node per branch. Processed branch writes to "Processed" sheet, review branch to "Needs Review." Map: Date, Vendor, Invoice #, Amount, Currency, Category, Confidence.

**Slack notification:**

```
📄 Invoice processed: {{ $json.vendor_name }} — {{ $json.total_amount }} {{ $json.currency }}
Category: {{ $json.category }}
Confidence: {{ $json.confidence }}
Status: {{ $json.confidence > 0.85 ? 'Auto-processed ✅' : 'Flagged for review ⚠️' }}
```

For Thai businesses, LINE integration is available via n8n's HTTP Request node. Since LINE is the dominant business channel in Thailand, configure LINE notifications alongside or instead of Slack.

**Test:** Send 10 test invoices, verify every output, then activate.

### No-Code vs. Code

No-code works for standard integrations, linear pipelines, and prototyping. You need code for custom transformations, complex branching, high volume (10,000+/day), or fine-grained error handling. **Hybrid approach:** n8n for orchestration, Python via the Code node for complex processing.

### Cost Comparison

| | n8n (self-hosted) | Make.com | Zapier | Custom Python |
|---|---|---|---|---|
| Platform | $0 | $16-29/mo | $49-69/mo | $0 |
| Hosting | $5-10/mo | Included | Included | $5-10/mo |
| AI API | $15-30/mo | $15-30/mo | $15-30/mo | $15-30/mo |
| **Total** | **$20-40/mo** | **$31-59/mo** | **$64-99/mo** | **$20-40/mo** |

---

## Path C: Hire a Builder

You have the customer but do not want to build it yourself. Legitimate choice. Here is what a good technical brief looks like:

---

**PROJECT: Invoice Processing Automation for [Client Name]**

**Overview:** Automated pipeline: Gmail inbox monitoring, AI-powered PDF data extraction, expense categorization, Google Sheets output, Slack notifications.

**Specs:** Process new emails with PDF attachments every 30 minutes. Extract vendor, invoice number, date, due date, line items, totals, currency. Categorize against 10-category chart of accounts. Route confidence < 85% to human review.

**Output:** Google Sheets (Processed/Needs Review tabs), Slack notifications, state file for duplicate prevention.

**Requirements:** Retry logic (3 attempts, exponential backoff), JSONL logging, Slack alerts on exceptions, no data loss mid-batch, heartbeat monitoring, daily summary.

**Stack (negotiable):** Python 3.11+, Claude API, Gmail/Sheets APIs, Railway or VPS.

**Deliverables:** Working automation, config docs, README, one week bug fixes. **Timeline:** 2 weeks. **Budget:** $2,000-4,000 fixed.

---

### Where to Find Builders

| Source | Typical cost | Notes |
|--------|-------------|-------|
| **Upwork** | $2,000-5,000 fixed | Filter by 90%+ job success |
| **Local communities** | $2,000-4,000 fixed | Bangkok: BKK.js, ThaiPy |
| **Developer Discords** | $2,000-5,000 fixed | n8n, LangChain, Anthropic |
| **Referrals** | Varies | Other operators, indie hacker forums |

**Screening:** Share the brief. Good builders ask clarifying questions. Ask for a similar past project. Test: "What if the PDF is a scanned image?" Check references.

### What to Pay

**Prototype:** $2,000-5,000 fixed. **Hourly:** $40-80/hr, 30-60 hours. **Maintenance:** $500-1,000/month.

### Evaluating the Deliverable

Verify: end-to-end processing, 3+ invoice formats, low-confidence routing, no duplicates, runs unattended. Check error handling (retries, logging, alerts, no data loss), state management (tracks processed emails, persists, human-readable), monitoring (heartbeat, daily summary, run logs), and docs (README covers deployment, config, no hardcoded values).

### Red Flags

Over-engineering (Kubernetes for one client). Skipping error handling. Cannot explain architecture. No state management. No monitoring. Disappears after delivery.

---

## Regardless of Path

You should now have a working prototype, state management, error handling, monitoring, and visible output. It will have bugs. That is fine — it demonstrates value.

Deploy. Show the customer auto-processed invoices. Iterate. Fix fast. "We noticed edge case X and fixed it this morning" — that transparency builds more trust than a perfect launch.

---

## Choosing Your Path

| If you... | Take Path... | Because... |
|-----------|-------------|-----------|
| Write Python and enjoy it | **A** | Full control, lowest cost |
| Comfortable with drag-and-drop | **B (n8n)** | Build in hours, not days |
| Do not build, do not want to learn | **C (Hire)** | Focus on sales |
| Can code but want speed | **B** then **A** | Validate fast, build properly |
| Have budget, no technical skills | **C** then **B** | Earn while learning |

There is no wrong answer. The wrong answer is spending three months deciding.

**For SEA operators:** n8n self-hosted works well globally. LINE integration via webhook nodes. Bangkok's BKK.js and ThaiPy meetups are good for finding builders who know both n8n and Python.

Pick a path. Build it. Deploy for your first customer.

Now we deliver — and we keep them.
