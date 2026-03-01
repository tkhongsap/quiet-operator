# Quiet Operator — Starter Code

Production-oriented starter code for building AI automation services. Simple, readable, and educational.

## Architecture Overview

```
┌─────────────────┐
│   config.yaml   │  ← API keys, agent definitions, schedules
└────────┬────────┘
         │
┌────────▼────────┐
│    agent.py     │  ← Single-agent pattern (start here)
│  orchestrator.py│  ← Multi-agent pattern (grow into this)
└────────┬────────┘
         │
┌────────▼────────┐
│   state.json    │  ← Persistent state per client
└─────────────────┘
```

## Files

| File | What It Does |
|------|-------------|
| `agent.py` | Single-agent example: system prompt, tool use, state-in-files, cron loop |
| `orchestrator.py` | Multi-agent orchestrator: spawns sub-agents, quality gates, state management |
| `state.json` | Example state file for a client project |
| `config.yaml` | Configuration template: API keys, agent definitions, schedules |

## Prerequisites

- Python 3.10+
- `openai` package: `pip install openai`
- `pyyaml` package: `pip install pyyaml`
- `schedule` package: `pip install schedule` (for cron loop in agent.py)

```bash
pip install openai pyyaml schedule
```

## Quick Start

1. Copy `config.yaml` and fill in your API key
2. Run the single agent: `python agent.py`
3. When you need multi-agent, use `orchestrator.py` as your starting point

## Design Principles

- **State lives in files, not memory.** JSON files are the source of truth. Debuggable, version-controllable, portable.
- **No heavy frameworks.** Plain Python + OpenAI SDK. Add frameworks when you feel the pain of not having them.
- **Production-oriented.** Error handling, logging, and retry logic included from the start.
- **One client = one folder.** Scale by adding folders, not refactoring architecture.

## Folder Structure (In Production)

```
/clients/
  /acme_dental/
    config.yaml      # Client-specific config
    state.json        # Current automation state
    run_log.jsonl     # Append-only log of every run
    errors.jsonl      # Error log
  /baker_law/
    config.yaml
    state.json
    run_log.jsonl
    errors.jsonl
```

## When to Use What

- **Start with `agent.py`** for your first 1-3 clients. Single agent handles most automation workflows.
- **Move to `orchestrator.py`** when your single agent's prompt exceeds ~2,000 words or you need parallel processing.
- **Don't optimize prematurely.** The single agent pattern at $2K/month per client with 95%+ margins is a great business.
