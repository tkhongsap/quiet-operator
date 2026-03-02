# บทที่ 4: สร้าง Solution แรกของคุณ — สามเส้นทาง

> *จำนวนเงินทั้งหมดใน playbook นี้เป็นสกุล USD ยกเว้นระบุไว้เป็นอย่างอื่น*

---

คนส่วนใหญ่ไม่เคยเริ่มต้น พวกเขาศึกษา framework เปรียบเทียบเครื่องมือ อ่านบทความอีกสักชิ้น — สามเดือนผ่านไปก็ยังไม่ได้ ship อะไรเลย

คุณจะไม่เป็นแบบนั้น คุณเจอ niche ของตัวเองแล้ว คุณ validate ปัญหาแล้ว ตอนนี้คุณต้องสร้างสิ่งที่ทำให้ปัญหานั้นหมดไป

บทนี้จะให้เส้นทางสามเส้นทางคู่ขนานไปสู่ prototype ที่ใช้งานได้จริง **เลือกเส้นทางที่เข้ากับทักษะของคุณ** Developer เลือก Path A ผู้ดำเนินงานที่ไม่ได้เป็นสาย technical เลือก Path B คนที่อยากจ้างมากกว่าสร้างเองเลือก Path C ทั้งสามเส้นทางจบที่เดียวกัน: automation ที่ใช้งานได้จริงและประมวลผลข้อมูลจริง

เราจะใช้ตัวอย่างเดียวตลอดทั้งบท — **automation สำหรับประมวลผลใบแจ้งหนี้**

สำนักงานบัญชีขนาดเล็กรับใบแจ้งหนี้ 50-100 ฉบับต่อสัปดาห์ทาง email พนักงานบัญชีสกัดชื่อผู้ขาย ยอดเงิน วันที่ รายการสินค้า จัดหมวดหมู่ค่าใช้จ่าย แล้วกรอกลง Google Sheet ใช้เวลา 15-20 ชั่วโมงต่อสัปดาห์ อัตราผิดพลาด 3-5%

automation ของเราทำได้ในไม่กี่วินาทีต่อฉบับ อัตราผิดพลาดต่ำกว่า 1% — และลูกค้ายินดีจ่าย $1,000-2,000/เดือนสำหรับ solution นี้

มาสร้างกันเลย

---

## Path A: Developer — เขียน Code เอง

สำหรับ developer ที่ถนัด Python, API และ command line

### Architecture Patterns

สี่ pattern ครอบคลุม 90% ของสิ่งที่ quiet operator สร้าง

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

**ต้นทุนการใช้งาน:** $20-40/เดือนค่า API, $5-10 ค่า hosting เมื่อเทียบกับ retainer $1,500/เดือน: margin 96%+ ไม่ได้พิมพ์ผิด

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

อย่าพึ่งพา conversation history สำหรับ state เขียนลงไฟล์เสมอ — debug ได้ ตรวจสอบได้ อยู่รอดแม้ระบบ crash

**อย่าเริ่มจากตรงนี้** สร้าง single agent ก่อน แยกเป็น agent เฉพาะทางเมื่อความซับซ้อนบังคับให้ทำ

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

ตัวประมวลผลใบแจ้งหนี้ของเราใช้ pattern นี้ — cron ทำงานทุก 30 นาที พนักงานบัญชีมาถึงตอน 9 โมงเช้าแล้วเจอทุกอย่างจัดหมวดหมู่เรียบร้อย

**สิ่งที่ขาดไม่ได้: monitoring**

Heartbeat alert, แจ้งเตือน error, สรุปรายวัน สิ่งสำคัญที่ต้องจำไว้คือ: ความล้มเหลวแบบเงียบๆ ทำลายความไว้วางใจ ตัว automation เป็นแค่ครึ่งเดียวของงาน monitoring คืออีกครึ่งที่ขาดไม่ได้

#### Pattern 4: State-in-Files

ไม่ใช่ pattern แบบแยกเดี่ยว — แต่เป็น **หลักการ** ที่ใช้ได้กับทุก pattern ข้างต้น AI agent ไม่มี state ระหว่าง session automation ของคุณต้องจำได้ว่าประมวลผลอะไรไปแล้ว

```
/state/
  /acme_accounting/
    state.json          # Current automation state
    run_log.jsonl       # Append-only log of every run
    errors.jsonl        # Error log with timestamps
    config.json         # Client-specific configuration
```

ไฟล์ดีกว่า database ในขั้นตอนนี้: debug ได้ พกพาได้ เรียบง่าย ย้ายไป database เมื่อมีลูกค้า 20+ ราย ดูรายละเอียดการ scale ในบทที่ 7.2

### Build Sprint 72 ชั่วโมง

#### ชั่วโมงที่ 0-8: กำหนด Scope และ Design

บันทึกให้ชัดเจน:

- trigger (email ใหม่ที่มีไฟล์แนบ PDF)
- input (ใบแจ้งหนี้หลายรูปแบบ)
- การประมวลผล (สกัดข้อมูลและจัดหมวดหมู่)
- output (Google Sheet + แจ้งเตือน Slack)
- failure mode (confidence < 85% ส่งไปตรวจสอบด้วยคน)

ขอใบแจ้งหนี้จริง 20 ฉบับจากลูกค้า เขียนเอกสาร scope หนึ่งหน้า ขอ sign-off แล้วค่อยเริ่มเขียน code

#### ชั่วโมงที่ 8-24: สร้าง Core Pipeline

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

**Step 2: Invoice Extraction ด้วย Claude**

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

**Step 3: จัดหมวดหมู่ค่าใช้จ่าย**

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

**Step 5: Main Pipeline**

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

**Step 6: แจ้งเตือนผ่าน Slack**

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

**Step 8: ตั้ง Cron**

```bash
# Run every 30 minutes during business hours
*/30 8-18 * * 1-5 cd /home/deploy/invoice-processor && python main.py >> cron.log 2>&1
```

#### ชั่วโมงที่ 24-40: ทำให้ Pipeline แข็งแกร่ง

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

#### ชั่วโมงที่ 40-56: Reporting Layer

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

#### ชั่วโมงที่ 56-72: ทดสอบกับข้อมูลจริงของลูกค้า ตรวจสอบทุก output แล้ว deploy

### TDD: เขียน Test ที่ Fail ก่อน

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

เขียน test ก่อน ดูมัน fail แล้วทำให้มัน pass

test ใบแจ้งหนี้ภาษาไทยสำคัญมาก — ในเอเชียตะวันออกเฉียงใต้ การสกัดข้อมูลจากเอกสารหลายภาษาเป็น core requirement ที่ต้องรองรับ

---

## เมื่อ AI ทำผิดพลาด: การสร้าง Safeguard

AI จะทำผิดพลาด เป็นประจำ คำถามคือระบบของคุณจับ output ที่ผิดพลาดได้ก่อนที่จะเกิดความเสียหายหรือไม่ ส่วนนี้เป็นตัวกำหนดว่าลูกค้าจะไว้วางใจคุณไปอีกสิบสองเดือน หรือบอกเลิกภายในสามเดือน

### Confidence Threshold แบบ 3 ระดับ

threshold เดียวไม่เพียงพอ ใช้สามระดับ:

- **สูง (>0.85):** ประมวลผลอัตโนมัติ ไม่ต้องให้คนตรวจสอบ
- **กลาง (0.60-0.85):** ประมวลผลแต่ flag ให้คนตรวจสอบภายใน 24 ชั่วโมง
- **ต่ำ (<0.60):** ส่งให้คนจัดการ automation ไม่ดำเนินการ

เริ่มแบบ conservative ก่อน ค่อยผ่อนคลายเมื่อสะสมข้อมูลความแม่นยำได้มากพอ

### Human-Review Queue

สร้าง review queue ในทุก automation — แม้จะเป็นแค่ tab "Needs Review" ใน Google Sheet ก็ยังดี

ทำหน้าที่สามอย่างพร้อมกัน: เป็น safety net สำหรับข้อมูลที่ไม่แน่ใจ เป็นแหล่ง training data สำหรับปรับปรุงระบบ และเป็นตัวสร้างความไว้วางใจกับลูกค้า

### Output Validation

ตรวจสอบก่อนที่ output ของ AI จะเข้าถึงระบบของลูกค้า

- ตรวจ type: ยอดเงินเป็นตัวเลขหรือไม่?
- ตรวจ range: ใบแจ้งหนี้ $500,000 จากร้านขายกระดาษ — สมเหตุสมผลหรือไม่?
- ตรวจ consistency: ชื่อผู้ขายตรงกับรายชื่อผู้ขายที่รู้จักหรือไม่?

### Audit Trail

บันทึกทุกการตัดสินใจของ AI: input, output, confidence, action ที่ดำเนินการ ไม่ใช่ทางเลือก เป็นสิ่งจำเป็น

เมื่อลูกค้าถามว่า "ทำไมถึงจัดหมวดหมู่รายการนี้เป็น 'Travel'?" — audit trail ช่วยให้คุณตอบได้ แก้ไขได้ และป้องกันไม่ให้เกิดซ้ำอีก

### Bounded Action

ห้ามให้ AI ดำเนินการแบบย้อนกลับไม่ได้โดยไม่มีคนอนุมัติ

ร่าง email แต่อย่าส่ง จัดหมวดหมู่ค่าใช้จ่ายแต่อย่ายื่นภาษี ให้คะแนน resume แต่อย่าปฏิเสธผู้สมัคร

AI แนะนำ คนตัดสินใจ

---

### สรุป Tech Stack (Path A)

| Layer | สิ่งที่ผมแนะนำ | ต้นทุน |
|-------|---------------|------|
| AI | Claude API (Sonnet สำหรับสกัดข้อมูล, Haiku สำหรับจัดหมวดหมู่) | $15-30/เดือน |
| ภาษา | Python 3.11+ | ฟรี |
| Email | Gmail API | ฟรี |
| Output | Google Sheets API | ฟรี |
| แจ้งเตือน | Slack webhooks | ฟรี |
| Hosting | Railway หรือ VPS $5 | $5-20/เดือน |
| Monitoring | Sentry (free tier) + Slack alerts | $0 |
| Scheduling | Cron | ฟรี |
| **รวม** | | **$20-50/เดือน** |

ดู margin ในบทที่ 1.6 — ตัวเลขดีมาก

---

## Path B: No-Code — สร้างด้วย n8n

ปัญหาเดียวกัน ไม่ต้องเขียน code ผมแนะนำ n8n — self-hosting ให้คุณควบคุมเต็มที่และไม่มีค่าใช้จ่ายต่อ operation

ใช้ Make.com ($9-16/เดือน) สำหรับการเรียนรู้ที่ง่ายที่สุด ใช้ Zapier ($20-49/เดือน) สำหรับ integration ที่มากที่สุด

### ประมวลผลใบแจ้งหนี้ใน n8n

**ติดตั้ง n8n:**

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

หรือใช้ n8n Cloud (free tier: 2,500 execution/เดือน)

**Workflow:**

```
[Gmail Trigger] → [Extract Attachments] → [AI Agent: Extract Data] → [IF: Confidence Check]
    → High confidence → [Google Sheets: Write to Processed]
    → Low confidence  → [Google Sheets: Write to Review]
→ [Slack: Send Summary]
```

**Gmail Trigger:** เชื่อมต่อผ่าน OAuth, กรองตาม Label = "Invoices" พร้อมไฟล์แนบ, poll ทุก 5 นาที

**AI Agent node:** เลือก Claude (Anthropic):

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

ส่งข้อมูล PDF จาก node ก่อนหน้า ตั้ง Output Parsing เป็น JSON

**IF node:** เงื่อนไข: `{{ $json.confidence }}` > `0.85`

True: ประมวลผลอัตโนมัติ False: flag สำหรับตรวจสอบ

**Google Sheets:** node ละ branch

- Processed branch เขียนไปที่ sheet "Processed"
- Review branch เขียนไปที่ "Needs Review"
- Map: Date, Vendor, Invoice #, Amount, Currency, Category, Confidence

**Slack notification:**

```
📄 Invoice processed: {{ $json.vendor_name }} — {{ $json.total_amount }} {{ $json.currency }}
Category: {{ $json.category }}
Confidence: {{ $json.confidence }}
Status: {{ $json.confidence > 0.85 ? 'Auto-processed ✅' : 'Flagged for review ⚠️' }}
```

สำหรับธุรกิจไทย สามารถเพิ่ม LINE integration ผ่าน HTTP Request node ของ n8n ได้ เนื่องจาก LINE เป็นช่องทางสื่อสารธุรกิจหลักในประเทศไทย ให้ตั้งค่าการแจ้งเตือนผ่าน LINE ควบคู่หรือแทนที่ Slack ก็ได้

**ทดสอบ:** ส่งใบแจ้งหนี้ทดสอบ 10 ฉบับ ตรวจสอบทุก output ให้ครบ แล้วค่อยเปิดใช้งาน

### No-Code vs. Code

No-code เหมาะสำหรับ integration มาตรฐาน, pipeline แบบเส้นตรง และการทำ prototype อย่างรวดเร็ว

ต้องเขียน code เมื่อต้องการแปลงข้อมูลแบบ custom, มีตรรกะแยกสาขาซับซ้อน, ประมวลผลปริมาณสูง (10,000+ รายการ/วัน) หรือต้องการควบคุม error handling อย่างละเอียด

**แนวทางผสม:** ใช้ n8n สำหรับ orchestration แล้วเรียก Python ผ่าน Code node สำหรับการประมวลผลที่ซับซ้อน

### เปรียบเทียบต้นทุน

| | n8n (self-hosted) | Make.com | Zapier | Custom Python |
|---|---|---|---|---|
| Platform | $0 | $16-29/เดือน | $49-69/เดือน | $0 |
| Hosting | $5-10/เดือน | รวมแล้ว | รวมแล้ว | $5-10/เดือน |
| AI API | $15-30/เดือน | $15-30/เดือน | $15-30/เดือน | $15-30/เดือน |
| **รวม** | **$20-40/เดือน** | **$31-59/เดือน** | **$64-99/เดือน** | **$20-40/เดือน** |

---

## Path C: จ้างคนสร้าง

คุณมีลูกค้าแต่ไม่อยากสร้างเอง ทางเลือกที่สมเหตุสมผล นี่คือตัวอย่าง technical brief ที่ใช้ได้จริง:

---

**PROJECT: Invoice Processing Automation สำหรับ [ชื่อลูกค้า]**

**ภาพรวม:** Pipeline อัตโนมัติ: monitor กล่องข้อความ Gmail, สกัดข้อมูลจาก PDF ด้วย AI, จัดหมวดหมู่ค่าใช้จ่าย, เขียน output ไปยัง Google Sheets, ส่งแจ้งเตือนทาง Slack

**Spec:** ประมวลผล email ใหม่ที่มีไฟล์แนบ PDF ทุก 30 นาที สกัดชื่อผู้ขาย เลขที่ใบแจ้งหนี้ วันที่ วันครบกำหนด รายการสินค้า ยอดรวม สกุลเงิน จัดหมวดหมู่ตามผังบัญชี 10 หมวด ถ้า confidence < 85% ให้ส่งไปตรวจสอบด้วยคน

**Output:** Google Sheets (tab Processed/Needs Review), แจ้งเตือนทาง Slack, state file สำหรับป้องกันการประมวลผลซ้ำ

**ข้อกำหนด:** Retry logic (3 ครั้ง, exponential backoff), JSONL logging, Slack alert เมื่อเกิด exception, ห้ามสูญเสียข้อมูลกลาง batch, heartbeat monitoring, สรุปรายวัน

**Stack (ต่อรองได้):** Python 3.11+, Claude API, Gmail/Sheets API, Railway หรือ VPS

**สิ่งที่ต้องส่งมอบ:** Automation ที่ใช้งานได้จริง, เอกสาร config, README, แก้ bug หนึ่งสัปดาห์หลัง deploy

**Timeline:** 2 สัปดาห์

**Budget:** $2,000-4,000 ราคาคงที่

---

### หาคนสร้างได้ที่ไหน

| แหล่ง | ต้นทุนโดยทั่วไป | หมายเหตุ |
|--------|-------------|-------|
| **Upwork** | $2,000-5,000 คงที่ | กรองตาม job success 90%+ |
| **ชุมชน developer ในพื้นที่** | $2,000-4,000 คงที่ | กรุงเทพฯ: BKK.js, ThaiPy |
| **Discord server สำหรับ developer** | $2,000-5,000 คงที่ | n8n, LangChain, Anthropic |
| **Referral** | แตกต่างกัน | operator คนอื่น, indie hacker forum |

**คัดกรอง:** แชร์ brief คนสร้างที่ดีจะถามคำถามเพื่อทำความเข้าใจ ไม่ใช่แค่บอกว่า "ทำได้" ขอดู project ที่คล้ายกันที่เคยทำ ทดสอบ: "ถ้า PDF เป็นภาพสแกนจะจัดการอย่างไร?" ตรวจสอบ reference

### จ่ายเท่าไหร่

**Prototype:** $2,000-5,000 ราคาคงที่

**จ้างรายชั่วโมง:** $40-80/ชั่วโมง, คาดว่าใช้ 30-60 ชั่วโมง

**ดูแลต่อเนื่อง:** $500-1,000/เดือน

### วิธีประเมิน Output

ตรวจสอบว่าทำงานได้จริง:
- ประมวลผลจากต้นจนจบ (Gmail ถึง extraction ถึง categorization ถึง Sheets ถึง Slack)
- จัดการใบแจ้งหนี้ 3+ รูปแบบได้ถูกต้อง
- routing รายการ confidence ต่ำไปยัง review tab
- ไม่ประมวลผลข้อมูลซ้ำ
- ทำงานอัตโนมัติตามกำหนดเวลา

ตรวจ error handling: retry, logging, alert, ไม่สูญเสียข้อมูล

ตรวจ state management: ติดตาม email ที่ประมวลผลแล้ว, state คงอยู่เมื่อ restart, อ่านได้ด้วยคน

ตรวจ monitoring: heartbeat, สรุปรายวัน, run log

ตรวจเอกสาร: README ครอบคลุม deployment, config, ไม่มีค่า hardcode

### สัญญาณอันตราย

Over-engineering (Kubernetes สำหรับลูกค้ารายเดียว)

ข้าม error handling อธิบาย architecture ไม่ได้ ไม่มี state management ไม่มี monitoring

หายตัวไปหลังส่งมอบ

---

## ไม่ว่าจะเลือกเส้นทางไหน

ตอนนี้คุณควรมี:
- prototype ที่ใช้งานได้
- state management
- error handling
- monitoring
- output ที่มองเห็นได้

จะมี bug นั่นไม่เป็นไร — มันแสดงคุณค่าได้แล้ว

Deploy แสดงให้ลูกค้าเห็นใบแจ้งหนี้ที่ถูกประมวลผลอัตโนมัติ ปรับปรุง แก้ไขเร็ว

"เราสังเกตเห็น edge case X แล้วแก้ไขเรียบร้อยเมื่อเช้านี้" — ความโปร่งใสแบบนั้นสร้างความไว้วางใจได้มากกว่าการ launch ที่สมบูรณ์แบบ

---

## เลือกเส้นทาง

| ถ้าคุณ... | เลือก Path... | เพราะ... |
|-----------|-------------|-----------|
| เขียน Python ได้และชอบ | **A** | ควบคุมได้เต็มที่ ต้นทุนต่ำสุด |
| ถนัดเครื่องมือแบบ drag-and-drop | **B (n8n)** | สร้างเป็นชั่วโมง ไม่ใช่เป็นวัน |
| ไม่สร้างเองและไม่อยากเรียน | **C (จ้าง)** | โฟกัสที่การขาย |
| เขียน code ได้แต่อยากเร็ว | **B** แล้ว **A** | Validate เร็ว แล้วค่อยสร้างอย่างจริงจัง |
| มี budget แต่ไม่มีทักษะ technical | **C** แล้ว **B** | เริ่มหาเงินระหว่างเรียนรู้ |

ไม่มีคำตอบผิด คำตอบที่ผิดคือการใช้เวลาสามเดือนตัดสินใจ

**สำหรับ operator ในเอเชียตะวันออกเฉียงใต้:** n8n self-hosted ใช้ได้ดีทั่วโลก LINE integration ผ่าน webhook node meetup BKK.js และ ThaiPy ในกรุงเทพฯ เป็นที่ที่ดีสำหรับหาคนสร้างที่คุ้นเคยทั้ง n8n และ Python

เลือกเส้นทาง สร้าง deploy ให้ลูกค้าคนแรก

ตอนนี้เราส่งมอบ — และรักษาลูกค้าไว้
