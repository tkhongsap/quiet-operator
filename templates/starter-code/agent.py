"""
Quiet Operator — Single Agent Example
======================================
A simple, production-oriented AI agent that:
1. Reads state from a JSON file
2. Processes tasks using the OpenAI API with tool use
3. Updates state after each run
4. Runs on a schedule (cron loop)

This is your starting point. One agent, one workflow, one client.
"""

import json
import os
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import yaml
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# ---------------------------------------------------------------------------
# State Management (the most important pattern in this file)
# ---------------------------------------------------------------------------
# State lives in files, NOT in memory. This means:
# - You can debug by reading a JSON file
# - You can version-control state with git
# - Crashes don't lose state
# - You can run the agent locally with production state

def load_state(state_path: str = "state.json") -> dict:
    """Load the current state from disk."""
    if not Path(state_path).exists():
        return {
            "client": "example_client",
            "last_run": None,
            "status": "initialized",
            "metrics": {"items_processed": 0, "errors": 0},
            "pending_tasks": [],
            "completed_tasks": [],
        }
    with open(state_path, "r") as f:
        return json.load(f)


def save_state(state: dict, state_path: str = "state.json") -> None:
    """Write state back to disk. Always do this at the end of a run."""
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2, default=str)


def append_log(entry: dict, log_path: str = "run_log.jsonl") -> None:
    """Append a run log entry. JSONL = one JSON object per line, append-only."""
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(log_path, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")

# ---------------------------------------------------------------------------
# Tools — Define what the agent can do
# ---------------------------------------------------------------------------
# Tools are functions the AI can call. Keep them simple and focused.
# Each tool should do ONE thing well.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "process_item",
            "description": "Process a single item (invoice, lead, appointment, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "string",
                        "description": "The unique identifier of the item to process",
                    },
                    "action": {
                        "type": "string",
                        "enum": ["classify", "extract", "summarize", "route"],
                        "description": "What to do with the item",
                    },
                    "details": {
                        "type": "string",
                        "description": "Additional details or extracted data",
                    },
                },
                "required": ["item_id", "action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_notification",
            "description": "Send a notification (email, Slack, SMS) about a result",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "enum": ["email", "slack", "sms"],
                    },
                    "recipient": {"type": "string"},
                    "message": {"type": "string"},
                },
                "required": ["channel", "message"],
            },
        },
    },
]


def handle_tool_call(name: str, args: dict) -> str:
    """
    Execute a tool call from the AI. In production, these would connect
    to real APIs (SendGrid, Twilio, Slack webhooks, CRMs, etc.).
    """
    if name == "process_item":
        # --- Replace with real processing logic ---
        logging.info(f"Processing item {args['item_id']}: {args['action']}")
        return json.dumps({
            "status": "success",
            "item_id": args["item_id"],
            "action": args["action"],
            "result": f"Item {args['item_id']} {args['action']}d successfully",
        })

    elif name == "send_notification":
        # --- Replace with real notification logic ---
        logging.info(f"Notification via {args['channel']}: {args['message'][:80]}...")
        return json.dumps({"status": "sent", "channel": args["channel"]})

    else:
        return json.dumps({"error": f"Unknown tool: {name}"})

# ---------------------------------------------------------------------------
# Agent Core — The main processing loop
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an AI automation agent for a business client.

Your job:
1. Review pending tasks from the state
2. Process each task using the available tools
3. Report results clearly

Rules:
- Process items one at a time
- If you're unsure about a classification, flag it for human review
- Always send a summary notification when you're done
- Be concise and precise in all outputs

Current client: {client_name}
"""


def run_agent(config: dict, state: dict) -> dict:
    """
    Run one cycle of the agent. This is called on each scheduled run.
    
    Returns the updated state.
    """
    client = OpenAI(api_key=config["api"]["openai_key"])
    
    # Build the context from current state
    system = SYSTEM_PROMPT.format(client_name=state.get("client", "unknown"))
    user_message = (
        f"Current state:\n"
        f"- Pending tasks: {len(state.get('pending_tasks', []))}\n"
        f"- Items processed so far: {state['metrics']['items_processed']}\n\n"
        f"Pending tasks:\n{json.dumps(state.get('pending_tasks', []), indent=2)}\n\n"
        f"Process all pending tasks and send a summary."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]

    # --- Agent loop: call the model, handle tool calls, repeat ---
    max_iterations = 10  # Safety limit to prevent infinite loops
    for _ in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model=config["api"].get("model", "gpt-4o"),
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            logging.error(f"API call failed: {e}")
            state["metrics"]["errors"] += 1
            append_log({"event": "api_error", "error": str(e)})
            break

        choice = response.choices[0]

        # If the model wants to call tools, execute them
        if choice.finish_reason == "tool_calls" or choice.message.tool_calls:
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = handle_tool_call(tool_call.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
                state["metrics"]["items_processed"] += 1
        else:
            # Model is done — log the final response
            final_message = choice.message.content or ""
            logging.info(f"Agent completed: {final_message[:200]}")
            append_log({
                "event": "run_complete",
                "tasks_processed": len(state.get("pending_tasks", [])),
                "summary": final_message[:500],
            })
            break

    # Mark all pending tasks as completed
    state["completed_tasks"].extend(state.get("pending_tasks", []))
    state["pending_tasks"] = []
    state["status"] = "healthy"

    return state

# ---------------------------------------------------------------------------
# Cron Loop — Run the agent on a schedule
# ---------------------------------------------------------------------------

def main():
    """Main entry point. Loads config, runs the agent once or on a schedule."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    config = load_config()
    state = load_state()

    logging.info(f"Starting agent for client: {state.get('client', 'unknown')}")

    # --- Option 1: Run once (good for cron-based scheduling) ---
    # Use this if you run the agent via system cron: `*/30 * * * * python agent.py`
    if config.get("schedule", {}).get("mode") == "cron":
        state = run_agent(config, state)
        save_state(state)
        logging.info("Single run complete. State saved.")
        return

    # --- Option 2: Built-in schedule loop ---
    # Use this if you want the script to run continuously
    import schedule

    interval_minutes = config.get("schedule", {}).get("interval_minutes", 30)

    def scheduled_run():
        nonlocal state
        logging.info("Scheduled run starting...")
        try:
            state = run_agent(config, state)
            save_state(state)
            logging.info("Scheduled run complete.")
        except Exception as e:
            logging.error(f"Run failed: {e}")
            state["metrics"]["errors"] += 1
            save_state(state)

    # Run immediately on startup, then on schedule
    scheduled_run()
    schedule.every(interval_minutes).minutes.do(scheduled_run)

    logging.info(f"Agent running every {interval_minutes} minutes. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
