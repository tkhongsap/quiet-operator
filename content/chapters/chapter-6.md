# Chapter 6: Deliver & Keep Them

> *All dollar amounts in this playbook are in USD unless otherwise noted.*

---

Getting the customer is the beginning, not the end. But here is what too many operators get wrong: they treat delivery as an afterthought. Chapter 4 gave you a working prototype. Chapter 5 showed you how to land the deal. This chapter is about what happens after the handshake — how you deliver determines whether they stay for 12 months or cancel after 3.

The difference between a one-time project and a retained service is operational excellence. The best system is the one they forget exists — because it just works.

---

## 6.1 Monitoring That Works

Most automations fail silently. The cron job crashes at 2 AM. The API key expires on a Saturday. Nobody notices until the customer asks "why did the invoices stop processing last Thursday?"

By then you have lost trust. Maybe the customer.

**Your monitoring needs to catch problems before the customer does.** No exceptions.

### The Three Layers

**Layer 1: Heartbeats**

The automation checks in at regular intervals to prove it is alive.

```python
# heartbeat.py
import requests
from datetime import datetime, timezone

def send_heartbeat(webhook_url: str, client_name: str, status: str = "healthy"):
    """Send a heartbeat to Slack. If this stops arriving, something is wrong."""
    requests.post(webhook_url, json={
        "text": f"💓 {client_name} heartbeat: {status} | {datetime.now(timezone.utc).strftime('%H:%M UTC')}"
    }, timeout=10)
```

Add this to the end of every automation run.

**Better approach — dead man's switch:** Monitor for heartbeats that DON'T arrive. Services like Better Stack or Cronitor work, or a simple cron check:

```bash
# check_heartbeats.sh — runs every hour
# Checks that each client's automation ran in the last 2 hours

for client_dir in /state/*/; do
    client=$(basename "$client_dir")
    last_run=$(jq -r '.last_run // "never"' "$client_dir/state.json" 2>/dev/null || echo "error")

    if [ "$last_run" = "never" ] || [ "$last_run" = "error" ]; then
        curl -s -X POST "$SLACK_WEBHOOK" \
            -d "{\"text\": \"🚨 $client: No run data found. Check immediately.\"}"
        continue
    fi

    # Convert to epoch and check if older than 2 hours
    last_epoch=$(date -d "$last_run" +%s 2>/dev/null || echo 0)
    now_epoch=$(date +%s)
    diff=$(( (now_epoch - last_epoch) / 3600 ))

    if [ "$diff" -gt 2 ]; then
        curl -s -X POST "$SLACK_WEBHOOK" \
            -d "{\"text\": \"⚠️ $client: Last run was $diff hours ago. Expected within 2 hours.\"}"
    fi
done
```

**Layer 2: Error Alerts**

Every unhandled exception triggers an immediate notification. Not a log entry. A notification that interrupts you.

```python
# error_handler.py
import traceback
import requests
from datetime import datetime, timezone

def alert_on_error(webhook_url: str, client_name: str, error: Exception,
                    context: str = ""):
    """Send an error alert to Slack with full context."""
    error_msg = {
        "text": f"🚨 *Error in {client_name}*\n"
                f"Context: {context}\n"
                f"Error: {type(error).__name__}: {str(error)}\n"
                f"Time: {datetime.now(timezone.utc).isoformat()}\n"
                f"```{traceback.format_exc()[-500:]}```"
    }
    requests.post(webhook_url, json=error_msg, timeout=10)
```

Wrap your main processing loop:

```python
try:
    process_invoices()
    send_heartbeat(config['slack_webhook'], config['client_name'])
except Exception as e:
    alert_on_error(
        config['slack_webhook'],
        config['client_name'],
        e,
        context="Main invoice processing loop"
    )
    raise  # Re-raise so the error is also logged
```

**Layer 3: Daily Summaries**

Even when nothing breaks, send a daily summary. Confirms the system ran (for you) and provides a paper trail (for the customer).

```python
# daily_summary.py
import json
from datetime import datetime, timedelta, timezone

def generate_daily_summary(client_name: str, run_log_path: str) -> str:
    """Generate a daily operations summary from run logs."""
    today = datetime.now(timezone.utc).date()

    runs = 0
    total_processed = 0
    total_flagged = 0
    total_errors = 0

    with open(run_log_path) as f:
        for line in f:
            entry = json.loads(line)
            entry_date = datetime.fromisoformat(entry['timestamp']).date()
            if entry_date == today:
                runs += 1
                total_processed += entry.get('processed', 0)
                total_flagged += entry.get('flagged', 0)
                total_errors += entry.get('errors', 0)

    status = "✅ Healthy" if total_errors == 0 else f"⚠️ {total_errors} errors"

    return (
        f"📊 Daily Summary — {client_name}\n"
        f"Date: {today.isoformat()}\n"
        f"Status: {status}\n"
        f"Runs completed: {runs}\n"
        f"Items processed: {total_processed}\n"
        f"Items flagged for review: {total_flagged}\n"
        f"Errors: {total_errors}"
    )
```

Schedule at end of business in the client's timezone:

```bash
0 18 * * 1-5 cd /home/deploy && python daily_summary.py >> /dev/null 2>&1
```

### Complete Monitoring Cron

```bash
# /etc/cron.d/automation-monitoring

# Heartbeat checker — every hour during business hours
0 8-18 * * 1-5 deploy /home/deploy/scripts/check_heartbeats.sh

# Daily summaries — end of business (6 PM local)
0 18 * * 1-5 deploy cd /home/deploy && python scripts/send_daily_summaries.py

# Weekly health report — Sunday night
0 20 * * 0 deploy cd /home/deploy && python scripts/weekly_health_report.py

# Monthly ROI reports — 1st of each month
0 9 1 * * deploy cd /home/deploy && python scripts/send_monthly_reports.py
```

---

## 6.2 The Monthly ROI Report

The monthly ROI report is your insurance policy against cancellation. When the customer gets their bill for $1,500 and simultaneously sees a report showing $4,200 in savings, they do not think about canceling. They think about expanding.

That psychology works because it is built on real numbers — not spin.

### The Full Report Generator

```python
# monthly_report.py
import json
import os
from datetime import datetime, timedelta, timezone
from notifications import send_slack_notification

def generate_monthly_report(
    client_name: str,
    run_log_path: str,
    retainer_amount: float,
    avg_minutes_per_item: float = 8.0,
    hourly_labor_cost: float = 25.0,
    item_label: str = "invoices"
) -> str:
    """Generate a comprehensive monthly ROI report."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)

    # This month's data
    current = _aggregate_period(run_log_path, month_start, now)
    # Previous month's data (for comparison)
    previous = _aggregate_period(run_log_path, prev_month_start, month_start)

    total_items = current['processed'] + current['flagged']
    hours_saved = (total_items * avg_minutes_per_item) / 60
    money_saved = hours_saved * hourly_labor_cost
    auto_rate = (current['processed'] / total_items * 100) if total_items > 0 else 0
    error_rate = (current['errors'] / total_items * 100) if total_items > 0 else 0
    roi = money_saved / retainer_amount if retainer_amount > 0 else 0

    # Month-over-month change
    prev_total = previous['processed'] + previous['flagged']
    volume_change = ((total_items - prev_total) / prev_total * 100) if prev_total > 0 else 0

    report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MONTHLY AUTOMATION REPORT
   {client_name}
   {month_start.strftime('%B %Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 ACTIVITY
   {item_label.title()} auto-processed:  {current['processed']:,}
   Flagged for human review:             {current['flagged']:,}
   Total handled:                        {total_items:,}
   vs. last month:                       {volume_change:+.0f}%

⏱️  TIME SAVED
   Manual processing time:    {avg_minutes_per_item} min/{item_label[:-1]}
   Total time saved:          {hours_saved:.1f} hours
   Equivalent labor cost:     ${money_saved:,.0f}

✅ QUALITY
   Automation rate:     {auto_rate:.0f}% (auto-processed without human review)
   Error rate:          {error_rate:.1f}%
   Runs completed:      {current['runs']}
   System uptime:       {_calculate_uptime(run_log_path, month_start, now)}%

💰 ROI
   Your monthly investment:   ${retainer_amount:,.0f}
   Monthly savings delivered: ${money_saved:,.0f}
   Net benefit:               ${money_saved - retainer_amount:,.0f}
   Return on investment:      {roi:.1f}x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return report


def _aggregate_period(run_log_path, start, end):
    """Aggregate run log entries for a time period."""
    result = {'processed': 0, 'flagged': 0, 'errors': 0, 'runs': 0}
    if not os.path.exists(run_log_path):
        return result
    with open(run_log_path) as f:
        for line in f:
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry['timestamp'])
            if start <= ts < end:
                result['processed'] += entry.get('processed', 0)
                result['flagged'] += entry.get('flagged', 0)
                result['errors'] += entry.get('errors', 0)
                result['runs'] += 1
    return result


def _calculate_uptime(run_log_path, start, end):
    """Calculate uptime percentage based on expected vs actual runs."""
    result = _aggregate_period(run_log_path, start, end)
    days = (end - start).days or 1
    # Expect ~20 runs/day (every 30 min, 10 hours/day)
    expected_runs = days * 20
    actual_runs = result['runs']
    uptime = min(100, (actual_runs / expected_runs * 100)) if expected_runs > 0 else 0
    return f"{uptime:.1f}"


def send_monthly_reports():
    """Send monthly reports for all clients."""
    clients_dir = '/state'
    for client_name in os.listdir(clients_dir):
        client_dir = os.path.join(clients_dir, client_name)
        config_path = os.path.join(client_dir, 'config.json')
        run_log_path = os.path.join(client_dir, 'run_log.jsonl')

        if not os.path.exists(config_path):
            continue

        with open(config_path) as f:
            config = json.load(f)

        report = generate_monthly_report(
            client_name=config.get('client_name', client_name),
            run_log_path=run_log_path,
            retainer_amount=config.get('retainer_amount', 1500),
            avg_minutes_per_item=config.get('avg_minutes_per_item', 8.0),
            hourly_labor_cost=config.get('hourly_labor_cost', 25.0),
            item_label=config.get('item_label', 'invoices')
        )

        send_slack_notification(config['slack_webhook'], report)

        # Also save to file for records
        report_path = os.path.join(
            client_dir,
            f"report_{datetime.now(timezone.utc).strftime('%Y_%m')}.txt"
        )
        with open(report_path, 'w') as f:
            f.write(report)


if __name__ == '__main__':
    send_monthly_reports()
```

Schedule on the 1st of every month:

```bash
0 9 1 * * cd /home/deploy && python monthly_report.py
```

The report sends itself. You do not lift a finger. It sells your service every single month.

**Pro tip:** Send the report 1-2 days before the invoice. They see "$4,200 in savings" on Monday, your "$1,500 invoice" on Wednesday. That is not manipulation — it is making the value visible at the right moment.

---

## 6.3 Customer Onboarding

Send this immediately after the customer signs. The first 48 hours determine the tone of the entire relationship.

### Onboarding Doc Template

**Welcome to [Your Service Name] | Prepared for: [Customer Name] | Date: [Date]**

**Week 1:** We request access to your [Gmail/CRM/tools], configure the automation, and begin test runs with your real data. Your time: ~1 hour total.

**Week 2:** Automation runs in "shadow mode" — processing but not taking action. We review every output and tune accuracy. End of week: go/no-go decision.

**Week 3-4:** Automation goes live. Weekly progress emails every Friday. One 30-minute check-in call.

**Month 2 onward:** Runs autonomously. Monthly reports. Support via [Slack/email/LINE], response within 4 business hours.

**What We Need From You (Day 1):** Tool access (OAuth link we send), sample data (20 recent items), chart of accounts / category list, Slack channel for notifications (Day 2), and a point of contact for questions.

**Communication:** Weekly updates in Month 1, then monthly. Urgent issues: 4-hour response. Questions: 1 business day. Monthly 30-min check-in at your convenience.

**Your Contacts:** [Your name] — [Email/Slack/LINE] | Emergency: [Your name or VA] — [Phone/LINE]

Send this on Day 1. Customers who receive a clear onboarding doc are 3x more likely to still be paying after 6 months.

---

## 6.4 Communication Cadence

Consistent communication separates a service from a project. Projects end. Services persist.

I have seen operators lose customers not because the automation stopped working, but because the customer forgot it was working. Silence is the enemy.

**Month 1: Weekly Updates.** Every Friday:

```
📊 Weekly Update — [Client Name]
Week of [Date]

✅ What happened:
- Processed 127 invoices (118 auto, 9 flagged for review)
- Fixed: Thai-language invoices now categorized correctly
- Uptime: 100%

📋 Next week:
- Tuning categorization for [specific vendor type]
- Adding [small improvement discussed with client]

💬 Questions? Reply here or message me on [channel].
```

Ten minutes. Builds trust every week.

**Month 2+:** Switch to the auto-generated monthly ROI report.

**Always communicate proactively about issues.** If something breaks — even if you fix it fast — tell them:

```
⚠️ Quick heads up — our invoice processing had a brief interruption this morning
(6:15-6:45 AM) due to a Gmail API rate limit change. Already fixed.
No invoices were lost — 3 that arrived during the window were processed
once the system recovered. All caught up now.
```

**Quarterly Business Reviews.** For customers paying $2,000+/month, schedule a 30-minute quarterly video call. Present trends, discuss evolving needs, propose expansions.

---

## 6.5 Handling Scope Creep

It will happen. "This is great. Can you also automate [completely different thing]?"

Small things free, big things quoted. Customers respect clear boundaries more than vague accommodation.

| Customer request | Response | Action |
|-----------------|----------|--------|
| Small config change (e.g., add a category) | "Done. Included in your retainer." | Do it same day |
| Medium request (e.g., add a new notification type) | "I can add that. It's covered under your monthly improvement." | Add to next sprint |
| Large request (e.g., automate a completely new workflow) | "Great idea. Let me scope and send a proposal." | Quote setup fee + retainer increase |
| Out-of-domain request (e.g., "can you fix our website?") | "That's outside my specialty. I can recommend someone." | Refer and move on |

---

## 6.6 When Things Break: Incident Response

Things will break. APIs change without warning. PDF formats shift. Rate limits tighten. Not "if" — "when."

We have to be honest about this. As a solo operator, you need a lightweight incident response process. Not a 50-page runbook. A checklist.

### The Solo Operator Incident Checklist

1. **Acknowledge** (2 min): Check Slack. Read the error. Is the customer impacted right now?

2. **Assess severity:**
   - **Critical:** Automation down. Data may be lost.
   - **Warning:** Degraded. Some items failing. Customer has not noticed yet.
   - **Low:** Minor issue. No impact. Fix during business hours.

3. **Communicate** (if Critical or Warning). Do not wait until it is fixed:
   ```
   "We detected an issue with [system] at [time]. Investigating now.
   No data has been lost. Will update within [timeframe]."
   ```

4. **Fix.** Common causes: API key expired (rotate), rate limit hit (add backoff), disk full (clean logs), malformed input (add validation), external API down (retry queue).

5. **Verify:** Run manually. Confirm correct processing. Catch up missed items.

6. **Post-mortem** (5 min): What happened, what was the impact, what you fixed, how you prevent it next time.

7. **Update the customer** (if you communicated in step 3):
   ```
   "Issue resolved at [time]. Root cause: [brief explanation].
   All [items] have been processed. We've added [preventive measure]
   to avoid this in the future."
   ```

---

## 6.7 Liability and Contracts

You are running automated systems that touch other people's business data. At some point, something will go wrong — a misprocessed invoice, a missed reminder, a categorization error that cascades. The question is not just "how do we fix it?" It is "who is responsible?"

A clear contract protects both sides. You do not need a lawyer for your first few customers — but you do need explicit written agreements.

### Essential Contract Terms

**Scope of service.** Exactly what the automation does and does not do. "We automate invoice extraction and categorization" is different from "we guarantee accurate bookkeeping." That distinction matters legally.

**Liability caps.** Cap total liability at fees paid in the previous 12 months. If your $1,500/month automation causes a $500,000 error, you are not personally liable for the full amount. Without this clause, you could be.

**Data handling.** Where client data is processed, stored, who has access, when it is deleted. For personal data, these terms are legally required in many jurisdictions.

**Termination.** Either party, 30 days' notice. Include a transition clause: documentation and reasonable support for moving to another provider.

**Errors and omissions.** Automation provided "as-is" for the defined scope. Human review recommended for high-stakes decisions. The client retains responsibility for decisions made using the output.

### When to Get Legal Review

For your first 3-5 customers, a clear scope document and email agreement is sufficient. Past $10,000/month in recurring revenue, invest in a proper service agreement. Budget $1,000-2,000 — a one-time cost that protects a growing revenue stream.

### Errors and Omissions Insurance

Past $5,000+/month, consider E&O insurance — covers claims that your automation caused financial harm. Typical cost: $500-1,500/year. Small price for peace of mind.

---

## 6.8 Managing Up: Internal Champions

If you are automating internal processes, your "customer" is your leadership chain. Leaders do not want to hear about your architecture. They want outcomes. I have watched brilliant projects die because the builder could not translate technical achievement into business impact.

**Monthly leadership update template:**

```
Subject: AI Automation — Monthly Impact Report

Team,

Quick update on our invoice processing automation (Month [N]):

RESULTS
- 487 invoices processed automatically this month
- 62 hours of manual processing eliminated
- Error rate: 0.4% (down from 3.2% manual baseline)
- Zero missed invoices

BUSINESS IMPACT
- Equivalent of 1.5 FTE reassigned to higher-value work
- $8,400/month in labor cost savings
- Cumulative savings since launch: $38,200

WHAT'S NEXT
- Expanding to vendor onboarding workflow (projected: 30 additional hours/month saved)
- Pilot scheduled for [date] with [department]

Happy to discuss in our next [meeting]. Details in the attached dashboard.
```

**Key principles:** Lead with numbers, not technology. Frame savings as "FTE equivalent." Show cumulative impact. Always have a "what's next." Keep it under 200 words.

The goal remains what we established in Chapter 1 — make the automation invisible. When nobody questions the budget for something that quietly saves them 60 hours a month, you have won.

---

## 6.9 When to Fire a Customer

Not every engagement is worth keeping.

**Disproportionate support.** They take 40% of your time but generate 10% of revenue.

**No respect for boundaries.** Late-night messages, weekend calls, aggressive demands.

**ROI does not hold up.** After 3 months of iteration, the automation still is not delivering clear value.

**They do not pay on time.** One late payment is a mistake. Two is a pattern. Three is a firing.

### How to fire gracefully:

> "After reviewing our engagement, I don't think we're delivering the value you deserve for [specific task]. I'd recommend [alternative suggestion]. I'll ensure a smooth transition over the next 30 days, including documenting everything for your team or next provider."

Professional. No blame. Clean exit.

**Sunsetting internal projects** follows the same logic: the process no longer exists, maintenance exceeds value, or a commercial tool does it better. Sunsetting is not failure — it is good engineering judgment.

---

## 6.10 Checklists

### First Deployment Checklist

Before going live, run through every item.

- [ ] **Error Handling:** Try/catch with retry (3 attempts, exponential backoff) on every API call
- [ ] **Logging:** Timestamp, input, actions, output, errors to append-only JSONL
- [ ] **State Persistence:** Read from disk at start, write at end. Crashes do not lose progress
- [ ] **API Key Security:** No keys in code. Secrets in env vars or `.env` only
- [ ] **Rate Limiting:** Respects provider limits. Delays between batches. Token usage monitored
- [ ] **Graceful Failures:** Low-confidence outputs route to human review
- [ ] **Monitoring:** Error alert within 5 minutes. Heartbeat alert if automation misses window
- [ ] **Backup:** Daily backup. Restorable to any point in last 7 days
- [ ] **Documentation:** README covers deploy, debug, config, escalation
- [ ] **Test Run:** Full day of real data. Every output reviewed. Zero critical errors

### Monthly Health Check

Run on the 1st of every month, for every customer.

- [ ] **Uptime:** Any unplanned downtime? Root cause identified?
- [ ] **Error rate:** Under 2%? If higher, what is causing it?
- [ ] **Volume trends:** Growing, steady, or declining?
- [ ] **API costs:** Within range? Any spikes?
- [ ] **State file size:** Growing unbounded? (Prune processed IDs after 90 days.)
- [ ] **Log rotation:** Logs rotating? Disk usage reasonable?
- [ ] **Security:** API keys rotated in last 90 days?
- [ ] **Customer satisfaction:** Complaints or requests addressed?
- [ ] **ROI report sent:** Generated and sent correctly?
- [ ] **Improvement deployed:** At least one small improvement shipped?

---

## Chapter 6 Summary

**What you should have after this chapter:**

1. **Monitoring is live:** Heartbeats, error alerts, and daily summaries for every customer
2. **ROI report auto-generates:** Monthly report sends on the 1st, showing value delivered
3. **Onboarding doc sent:** Every new customer gets a clear document on Day 1
4. **Communication cadence established:** Weekly in Month 1, monthly ongoing
5. **Incident response defined:** You know what to do when things break
6. **Contracts protect you:** Clear terms on scope, liability, data, and termination
7. **Checklists in use:** First Deployment and Monthly Health Check running consistently

The automation is the product. The operational excellence is the business.

Building something that works is necessary. Building something that keeps working — invisibly, reliably, month after month — that is what makes a real difference.

Now let us systematize everything and grow.
