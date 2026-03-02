# Chapter 6: Deliver & Keep Them

> *All dollar amounts in this playbook are in USD unless otherwise noted.*

---

Getting the customer is the beginning, not the end. But here is what I have seen too many operators get wrong: they treat delivery as an afterthought. Chapter 4 gave you a working prototype. Chapter 5 showed you how to land the deal. This chapter is about what happens after the handshake — because how you deliver determines whether they stay for 12 months or cancel after 3.

The difference between a one-time project and a retained service is operational excellence: monitoring, reporting, communication, and the discipline to make your automation invisible. The best system is the one they forget exists — because it just works. That is not a metaphor. It is literally the goal.

Powerful enough to deliver real value; invisible enough that nobody worries about it.

---

## 6.1 Monitoring That Works

Most automations fail silently. The cron job crashes at 2 AM. The API key expires on a Saturday. The email provider changes their rate limits. Nobody notices until the customer asks "why did the invoices stop processing last Thursday?"

By then you have lost trust. Maybe the customer. Definitely sleep.

**Your monitoring needs to catch problems before the customer does.** Always. No exceptions.

### The Three Layers of Monitoring

**Layer 1: Heartbeats**

A heartbeat is the simplest form of monitoring: the automation checks in at regular intervals to prove it is alive.

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

Add this to the end of every automation run. If you stop seeing heartbeats in your Slack channel, investigate immediately.

**Better approach — dead man's switch:** Instead of monitoring for heartbeats that arrive, monitor for heartbeats that DON'T arrive. Services like Better Stack, Cronitor, or even a simple cron plus Slack check:

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

Run this via cron every hour. If any client's automation is late, you know before they do.

**Layer 2: Error Alerts**

Every unhandled exception should trigger an immediate notification. Not a log entry you will read someday. A notification that interrupts you.

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

Even when nothing breaks, send a daily summary. This serves two purposes: it confirms the system ran (for you) and it provides a paper trail (for the customer, if they ever ask).

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

Schedule this to run at 6 PM (or end of business in the client's timezone):

```bash
0 18 * * 1-5 cd /home/deploy && python daily_summary.py >> /dev/null 2>&1
```

### Monitoring Setup: Complete Cron Script

Here is the complete monitoring cron that covers all three layers for all clients:

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

I want to be direct about this: the monthly ROI report is your insurance policy against cancellation. When the customer gets their bill for $1,500 and simultaneously sees a report showing $4,200 in savings, they do not think about canceling. They think about expanding.

That is the psychology, and it works because it is built on real numbers — not spin.

### What the Report Contains

Every monthly report needs these sections:

1. **Activity Summary:** What the automation did (items processed, tasks completed)
2. **Time Saved:** Hours of manual work eliminated
3. **Money Saved:** Dollar value of those hours
4. **Quality Metrics:** Error rate, accuracy, items flagged for review
5. **ROI Calculation:** Their investment vs. their savings — plain math
6. **Issues & Improvements:** What you fixed, what you are improving next month

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

### Making the Report Auto-Generate

Schedule it to run on the 1st of every month:

```bash
0 9 1 * * cd /home/deploy && python monthly_report.py
```

The customer receives their report automatically. You do not lift a finger. The report sells your service for you every single month.

**Pro tip:** Send the report 1-2 days before the invoice. They see "$4,200 in savings" on Monday. They see your "$1,500 invoice" on Wednesday. The invoice feels small. That is not manipulation — it is making the value visible at the right moment.

---

## 6.3 Customer Onboarding Document

Send this immediately after the customer signs. It sets expectations upfront so there are no surprises. I cannot stress this enough — the first 48 hours after a customer signs determine the tone of the entire relationship.

### Onboarding Doc Template

---

**Welcome to [Your Service Name]**
**Prepared for: [Customer Name / Company]**
**Date: [Date]**

---

**What Happens Next**

**This Week (Week 1):**
- We will request access to your [Gmail/CRM/tools] — you will receive a secure access request via [method]
- We configure the automation using your existing data and processes
- Initial test runs begin with your real data
- Your time commitment: ~1 hour total (granting access + answering a few questions)

**Next Week (Week 2):**
- Automation runs in "shadow mode" — processing your data but not taking action yet
- We review every output manually and tune accuracy
- You will receive a summary of what the automation would have done
- End of week: go/no-go decision for live deployment

**Week 3-4 (Month 1):**
- Automation goes live
- You will receive **weekly progress emails** every Friday
- One 30-minute check-in call to review performance and address any questions
- We handle all issues and edge cases as they emerge

**Month 2 Onward:**
- Automation runs autonomously
- Reports shift from weekly to **monthly** (1st of each month)
- Support available via [Slack/email/LINE] — response within 4 business hours
- Monthly check-in call (optional — schedule as needed)

---

**What We Need From You**

| Item | How to provide | When |
|------|---------------|------|
| Gmail access (or relevant tool access) | OAuth authorization link we'll send | Day 1 |
| Sample data (20 recent invoices/items) | Email to [your email] | Day 1 |
| Chart of accounts / category list | Spreadsheet or list | Day 1 |
| Slack channel for notifications | Invite us to your workspace, or we'll use a webhook | Day 2 |
| Point of contact for questions | Name + preferred channel | Day 1 |

---

**What's Included in Your Retainer**

- Continuous automation processing (24/7 during configured hours)
- Monitoring and error alerts (we catch issues before you do)
- Monthly ROI report with detailed metrics
- Up to 2 hours of support and configuration changes per month
- One small improvement or optimization per month
- Bug fixes and maintenance

**Not included (available as add-ons):**
- New workflows or automations (quoted separately)
- Major configuration overhauls
- Integration with new tools not in original scope

---

**Communication**

- **Routine updates:** Weekly (Month 1), then Monthly
- **Urgent issues (system down, data error):** We respond within 4 business hours
- **Questions and requests:** Slack/email, response within 1 business day
- **Monthly check-in:** 30-min call, scheduled at your convenience

---

**Your Contacts**

| Role | Name | Channel |
|------|------|---------|
| Your automation specialist | [Your name] | [Email/Slack/LINE] |
| Emergency support | [Your name or VA] | [Phone/LINE for urgent] |

---

Send this on Day 1. It eliminates the "what do I do now?" confusion and signals professionalism. Customers who receive a clear onboarding doc are 3x more likely to still be paying after 6 months compared to those who get a vague "we'll be in touch."

That number should tell you everything about how much first impressions matter.

---

## 6.4 Communication Cadence

Consistent communication is what separates a service from a project. Projects end. Services persist. The difference is whether the customer hears from you regularly.

I have seen operators lose customers not because the automation stopped working, but because the customer forgot it was working. Silence is the enemy.

### The Cadence

**Month 1: Weekly Updates**

Every Friday, send a short email or Slack message:

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

This takes 10 minutes to write. It builds trust every single week.

**Month 2+: Monthly Reports**

Switch to the auto-generated monthly ROI report. The customer knows the system is running, they see the numbers, and they do not need weekly reassurance.

**Exception: always communicate proactively about issues.** If something breaks — even if you fix it within an hour — tell the customer:

```
⚠️ Quick heads up — our invoice processing had a brief interruption this morning
(6:15-6:45 AM) due to a Gmail API rate limit change. Already fixed.
No invoices were lost — 3 that arrived during the window were processed
once the system recovered. All caught up now.
```

This message takes 2 minutes. It demonstrates three things: you are monitoring, you fixed it fast, and no data was lost. That is trust in a text message.

### Quarterly Business Reviews (For Premium Customers)

For customers paying $2,000+/month or those you want to expand:

- 30-minute video call
- Present quarterly metrics (trends, not just snapshots)
- Discuss their evolving needs
- Propose expansions: "Based on what I have seen, automating [X] could save you another [Y] hours/month. Want me to scope it?"

Quarterly reviews are your expansion mechanism. They are not sales calls — they are value reviews that naturally surface new opportunities. The best growth comes from serving the people you already serve, not from endlessly chasing new ones.

---

## 6.5 Handling Scope Creep

It will happen. The customer will say: "This is great. Can you also automate [completely different thing]?"

**The wrong response:** "Sure, I'll add that." (You just committed to free work.)

**The also wrong response:** "No, that's out of scope." (You just shut down a revenue opportunity.)

**The right response:**

> "That's a great idea — I can see how it would save your team time. Let me scope it out. Based on the complexity, it would be [a small addition to your current retainer / a separate project with its own setup fee]. I'll send you a quick proposal by [day]."

This does three things:
1. **Validates their idea** — they feel heard
2. **Protects your time** — it is not free
3. **Creates revenue** — more work from existing customers is the most efficient way to grow

### The Scope Creep Response Framework

| Customer request | Response | Action |
|-----------------|----------|--------|
| Small config change (e.g., add a category) | "Done. Included in your retainer." | Do it same day |
| Medium request (e.g., add a new notification type) | "I can add that. It's covered under your monthly improvement." | Add to next sprint |
| Large request (e.g., automate a completely new workflow) | "Great idea. Let me scope and send a proposal." | Quote setup fee + retainer increase |
| Out-of-domain request (e.g., "can you fix our website?") | "That's outside my specialty. I can recommend someone." | Refer and move on |

The key principle: **small things are free, big things are quoted.** This creates goodwill on the small stuff and revenue on the big stuff. Customers respect clear boundaries more than vague accommodation.

---

## 6.6 When Things Break: Incident Response for Solo Operators

Things will break. APIs change without warning. PDF formats shift. Rate limits tighten. A server runs out of disk space at 4 AM. This is not a matter of "if" — it is "when."

We have to be honest about this. As a solo operator (or small team), you need a lightweight incident response process. Not a 50-page runbook. A checklist.

### The Solo Operator Incident Checklist

**When you get an alert:**

1. **Acknowledge** (2 min): Check Slack. Read the error. Is this affecting the customer right now?

2. **Assess severity:**
   - **Critical:** Automation is down. Data may be lost. Customer is impacted.
   - **Warning:** Automation is degraded. Some items failing. Customer has not noticed yet.
   - **Low:** Minor issue. No customer impact. Can fix during business hours.

3. **Communicate** (if Critical or Warning):
   Send the customer a brief status update. Do not wait until it is fixed.
   ```
   "We detected an issue with [system] at [time]. Investigating now.
   No data has been lost. Will update within [timeframe]."
   ```

4. **Fix:** Resolve the issue. For common causes:
   - API key expired — rotate key, update config
   - Rate limit hit — add backoff, reduce frequency
   - Disk full — clean logs, add log rotation
   - Malformed input — add input validation, skip bad item, alert
   - External API down — wait and retry, alert if extended

5. **Verify:** Run the automation manually. Confirm it processes correctly. Check that any missed items are caught up.

6. **Post-mortem** (5 min): Write a quick note:
   - What happened?
   - When did you notice?
   - What was the impact?
   - What did you fix?
   - How do you prevent it next time?

7. **Update the customer** (if you communicated in step 3):
   ```
   "Issue resolved at [time]. Root cause: [brief explanation].
   All [items] have been processed. We've added [preventive measure]
   to avoid this in the future."
   ```

### Preventing Common Failures

| Failure | Prevention | Cost |
|---------|-----------|------|
| API key expiration | Calendar reminder 2 weeks before expiry | Free |
| Disk full | Log rotation + weekly disk check script | Free |
| Rate limiting | Exponential backoff + daily volume monitoring | Free |
| Silent cron failure | Dead man's switch (heartbeat monitoring) | Free |
| Malformed input | Input validation + graceful skip + alert | Free |
| External API outage | Retry queue + manual processing fallback | Free |

Notice: every prevention measure is free. Reliability is not expensive. It is a discipline.

---

## 6.7 Managing Up: Internal Champions and Leadership

Not every operator serves external customers. If you are a corporate employee automating internal processes, your "customer" is your leadership chain — and keeping them engaged requires different skills.

### How to Report to Leadership

Leaders do not want to hear about your architecture. They want to hear about outcomes. I have watched brilliant internal projects die because the builder could not translate technical achievement into business impact.

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

**Key principles for reporting internally:**
- Lead with numbers, not technology
- Frame savings as "FTE equivalent" — leaders understand headcount
- Show cumulative impact — it gets more impressive every month
- Always have a "what's next" — this positions you for expanded scope and budget
- Keep it under 200 words — executives skim

### Scaling from Pilot to Department to Company-Wide

This is the internal equivalent of growing from 3 customers to 30:

**Phase 1: Pilot (1-2 months)**
- Automate one workflow for one team
- Document everything: process, results, edge cases
- Build your internal case study

**Phase 2: Department (months 3-6)**
- Present pilot results to department leadership
- Identify 2-3 similar workflows in the same department
- Replicate with minimal customization (you have productized internally)

**Phase 3: Cross-department (months 6-12)**
- Present department results to executive leadership
- Other departments see the results and request similar automation
- You become the internal "automation team" (even if it is just you)

**Phase 4: Company-wide (year 2+)**
- Formal automation practice with budget
- Hire a VA or junior developer to handle deployment
- You shift to strategy: identifying opportunities, prioritizing projects, measuring ROI

**The "invisible automation" principle:** At every phase, the goal is the same — make the automation invisible. The best automation is the one people forget exists because it just works. They do not think about it the same way they do not think about the electricity powering the office. It is infrastructure. It runs. Results appear.

When your automation becomes invisible, you have won. Nobody questions the budget for something that quietly saves them 60 hours a month. That is the kind of technology I believe in — technology that serves people so well they stop noticing it.

---

## 6.8 When to Fire a Customer (or Sunset a Project)

Not every engagement is worth keeping. This is a hard truth, but an important one.

### Fire a customer when:

**They require disproportionate support.** One customer takes 40% of your support time but generates 10% of your revenue. The math does not work.

**They do not respect boundaries.** Late-night messages, weekend calls, aggressive demands. This erodes your quality of life — the entire point of being a quiet operator.

**The ROI does not hold up.** If the automation is not delivering clear value after 3 months of iteration, it is honest to say "this is not the right fit."

**They do not pay on time.** One late payment is a mistake. Two is a pattern. Three is a firing.

### How to fire gracefully:

> "After reviewing our engagement, I don't think we're delivering the value you deserve for [specific task]. I'd recommend [alternative suggestion]. I'll ensure a smooth transition over the next 30 days, including documenting everything for your team or next provider."

Professional. No blame. Clean exit. Your reputation matters more than one month's retainer.

### When to sunset an internal project:

- The process it automates no longer exists (reorg, product change)
- Maintenance cost exceeds value (the API it depends on is deprecated and the replacement would require a full rebuild)
- A commercial tool now does it better and cheaper (rare, but it happens — be honest about it)

Sunsetting is not failure. It is good engineering judgment. Document what you learned, archive the code, and move the resources to something that delivers more value. Knowing when to stop is just as important as knowing when to start.

---

## 6.9 Checklists

### First Deployment Checklist

Before going live with any customer automation, run through this. Every item.

- [ ] **Error Handling:** Every API call has try/catch with retry logic (3 attempts, exponential backoff). No unhandled exceptions.
- [ ] **Logging:** Every run logs timestamp, input summary, actions taken, output summary, and errors to an append-only JSONL file.
- [ ] **State Persistence:** Agent reads state from disk at start, writes updated state at end. Crashes do not lose progress.
- [ ] **API Key Security:** No API keys in code. All secrets in environment variables or `.env` (excluded from version control).
- [ ] **Rate Limiting:** API calls respect provider rate limits. Delays between batch operations. Token usage monitored.
- [ ] **Graceful Failures:** When the AI is uncertain (confidence < threshold), route to human review. Never take irreversible action on low-confidence output.
- [ ] **Monitoring:** Slack/email alert fires within 5 minutes of any unhandled error. Heartbeat alert if automation does not complete within expected window.
- [ ] **Backup:** Customer data and state files backed up daily. Restorable to any point in the last 7 days.
- [ ] **Documentation:** README exists: how to deploy, debug, update config, and escalate.
- [ ] **Test Run:** Full day of real customer data processed. Every output reviewed manually. Zero critical errors before go-live.

### Monthly Health Check

Run this on the 1st of every month, for every customer.

- [ ] **Uptime:** Was there any unplanned downtime? Root cause identified?
- [ ] **Error rate:** Under 2%? If higher, what is causing it?
- [ ] **Volume trends:** Is processing volume growing, steady, or declining? (Declining might mean the customer's business is shrinking — or that they have stopped sending data.)
- [ ] **API costs:** Within expected range? Any spikes?
- [ ] **State file size:** Growing unbounded? (Old processed IDs should be pruned after 90 days.)
- [ ] **Log rotation:** Are logs being rotated? Is disk usage reasonable?
- [ ] **Security:** API keys rotated in the last 90 days? No leaked credentials?
- [ ] **Customer satisfaction:** Any complaints or requests? Have they been addressed?
- [ ] **ROI report sent:** Did the monthly report generate and send correctly?
- [ ] **Improvement deployed:** Did you ship at least one small improvement this month?

---

## Chapter 6 Summary

**What you should have after this chapter:**

1. **Monitoring is live:** Heartbeats, error alerts, and daily summaries running for every customer
2. **ROI report auto-generates:** Monthly report sends itself on the 1st, showing value delivered
3. **Onboarding doc sent:** Every new customer gets a clear, professional onboarding document on Day 1
4. **Communication cadence established:** Weekly updates in Month 1, monthly reports ongoing
5. **Incident response process defined:** You know exactly what to do when things break
6. **Checklists in use:** First Deployment and Monthly Health Check running consistently

This is what separates a quiet operator making $3,000/month (who eventually burns out and loses customers) from one making $30,000/month (who retains customers for years and grows through referrals).

The automation is the product. The operational excellence is the business.

Building something that works is necessary. Building something that keeps working — invisibly, reliably, month after month — that is what makes a real difference in people's lives.

Now let us systematize everything and grow.
