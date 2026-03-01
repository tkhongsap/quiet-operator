"""
Quiet Operator — Multi-Agent Orchestrator
==========================================
Manages multiple specialized sub-agents, each handling one phase of a workflow.

Pattern:
1. Orchestrator reads state.json to determine what needs doing
2. Dispatches the right sub-agent for the current phase
3. Sub-agent does its work and returns results
4. Orchestrator updates state, applies quality gates, moves to next phase

Use this when a single agent's prompt gets too long or you need parallel processing.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------------------------------------------------------------------------
# Configuration & State
# ---------------------------------------------------------------------------

def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_state(path: str = "state.json") -> dict:
    if not Path(path).exists():
        return {
            "project": "example_project",
            "phase": "research",
            "phases_completed": [],
            "quality_scores": {},
            "results": {},
            "errors": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    with open(path) as f:
        return json.load(f)


def save_state(state: dict, path: str = "state.json") -> None:
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(path, "w") as f:
        json.dump(state, f, indent=2, default=str)

# ---------------------------------------------------------------------------
# Sub-Agent Definitions
# ---------------------------------------------------------------------------
# Each sub-agent has a focused system prompt and a specific job.
# The orchestrator picks which sub-agent to run based on the current phase.

SUB_AGENTS = {
    "research": {
        "name": "Research Agent",
        "system_prompt": (
            "You are a research agent. Your job is to analyze the given data "
            "and produce a structured research summary. Be thorough but concise. "
            "Output valid JSON with keys: findings (list of strings), "
            "confidence (0-100), and recommendations (list of strings)."
        ),
        "next_phase": "processing",
    },
    "processing": {
        "name": "Processing Agent",
        "system_prompt": (
            "You are a data processing agent. Take the research findings and "
            "process them into actionable items. Categorize, prioritize, and "
            "structure the data. Output valid JSON with keys: items (list of "
            "objects with id, category, priority, action), and summary (string)."
        ),
        "next_phase": "quality_check",
    },
    "quality_check": {
        "name": "Quality Check Agent",
        "system_prompt": (
            "You are a quality assurance agent. Review the processed items for "
            "accuracy, completeness, and consistency. Score the overall quality "
            "from 0-100. Output valid JSON with keys: score (int), issues "
            "(list of strings), approved (boolean — true if score >= 70)."
        ),
        "next_phase": "reporting",
    },
    "reporting": {
        "name": "Reporting Agent",
        "system_prompt": (
            "You are a reporting agent. Generate a clear, client-ready summary "
            "of the work done. Include: what was processed, key results, any "
            "issues found, and recommended next steps. Write in plain language "
            "suitable for a non-technical business owner. Output as markdown."
        ),
        "next_phase": None,  # Final phase
    },
}

# ---------------------------------------------------------------------------
# Quality Gate
# ---------------------------------------------------------------------------

def quality_gate(phase: str, result: dict, state: dict) -> bool:
    """
    Quality gates ensure each phase meets minimum standards before proceeding.
    If a phase fails the quality gate, the orchestrator can retry or escalate.
    """
    if phase == "quality_check":
        score = result.get("score", 0)
        state["quality_scores"][phase] = score
        if not result.get("approved", False):
            logging.warning(f"Quality gate FAILED: score={score}, issues={result.get('issues', [])}")
            return False
        logging.info(f"Quality gate PASSED: score={score}")
        return True

    # Default: pass (not all phases need quality gates)
    return True

# ---------------------------------------------------------------------------
# Sub-Agent Execution
# ---------------------------------------------------------------------------

def run_sub_agent(config: dict, agent_def: dict, context: str) -> dict:
    """
    Run a single sub-agent with the given context.
    Returns parsed JSON result from the agent.
    """
    client = OpenAI(api_key=config["api"]["openai_key"])
    model = config["api"].get("model", "gpt-4o")

    logging.info(f"Running sub-agent: {agent_def['name']}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": agent_def["system_prompt"]},
                {"role": "user", "content": context},
            ],
            response_format={"type": "json_object"} if "JSON" in agent_def["system_prompt"] else None,
        )

        content = response.choices[0].message.content or ""

        # Try to parse as JSON; if it fails, wrap in a result dict
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_output": content}

    except Exception as e:
        logging.error(f"Sub-agent {agent_def['name']} failed: {e}")
        return {"error": str(e)}

# ---------------------------------------------------------------------------
# Orchestrator Core
# ---------------------------------------------------------------------------

def run_orchestrator(config: dict, state: dict, max_retries: int = 2) -> dict:
    """
    Main orchestration loop.
    
    Reads the current phase from state, runs the appropriate sub-agent,
    applies quality gates, and advances to the next phase.
    """
    current_phase = state.get("phase", "research")

    if current_phase is None:
        logging.info("All phases complete. Nothing to do.")
        return state

    agent_def = SUB_AGENTS.get(current_phase)
    if not agent_def:
        logging.error(f"Unknown phase: {current_phase}")
        state["errors"].append(f"Unknown phase: {current_phase}")
        return state

    # Build context from previous results
    context_parts = [f"Project: {state.get('project', 'unknown')}"]
    if state.get("results"):
        context_parts.append(f"Previous results:\n{json.dumps(state['results'], indent=2)}")
    context = "\n\n".join(context_parts)

    # Run the sub-agent (with retries)
    result = None
    for attempt in range(max_retries + 1):
        result = run_sub_agent(config, agent_def, context)

        if "error" not in result:
            break

        if attempt < max_retries:
            logging.warning(f"Retry {attempt + 1}/{max_retries} for {agent_def['name']}")

    if result is None or "error" in result:
        state["errors"].append({
            "phase": current_phase,
            "error": result.get("error", "Unknown error") if result else "No result",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        state["status"] = "error"
        return state

    # Store results
    state["results"][current_phase] = result

    # Apply quality gate
    if quality_gate(current_phase, result, state):
        state["phases_completed"].append(current_phase)
        state["phase"] = agent_def["next_phase"]
        state["status"] = "healthy" if agent_def["next_phase"] else "complete"
        logging.info(f"Phase '{current_phase}' complete. Next: {agent_def['next_phase'] or 'DONE'}")
    else:
        # Quality gate failed — keep the same phase for retry on next run
        state["status"] = "quality_gate_failed"
        logging.warning(f"Phase '{current_phase}' failed quality gate. Will retry next run.")

    return state

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    config = load_config()
    state = load_state()

    logging.info(f"Orchestrator starting — project: {state.get('project')}, phase: {state.get('phase')}")

    # Run through all phases in one execution
    # (In production, you might run one phase per cron cycle instead)
    max_cycles = len(SUB_AGENTS) + 1  # Safety limit
    for _ in range(max_cycles):
        if state.get("phase") is None or state.get("status") in ("complete", "error", "quality_gate_failed"):
            break
        state = run_orchestrator(config, state)
        save_state(state)

    # Final status
    if state.get("status") == "complete":
        logging.info("All phases complete!")
        # The reporting phase result contains the client-ready summary
        report = state.get("results", {}).get("reporting", {})
        if report:
            logging.info(f"Final report:\n{report.get('raw_output', json.dumps(report, indent=2))}")
    else:
        logging.info(f"Orchestrator stopped at phase: {state.get('phase')}, status: {state.get('status')}")

    save_state(state)
    logging.info("State saved.")


if __name__ == "__main__":
    main()
