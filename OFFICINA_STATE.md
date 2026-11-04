# Officina Lab — Project State

_Last updated: 2026-11-03_

## North Star
Build → Understand → Ship → Explain → Repeat.

Officina Lab is a personal AI/software lab evolving into an AI-native Control Tower and, later, an AI Venture Lab.

## Current architecture

Browser
→ JavaScript dashboard
→ FastAPI routes
→ services
→ repositories
→ SQLite

AI execution:
Run
→ executor
→ Context Builder
→ LLM Provider
→ OpenAI Responses API
→ tools
→ approvals for protected writes
→ output / usage / audit
→ SQLite + dashboard

## Implemented
- Task CRUD
- SQLite persistence
- Modular routes / services / repositories
- Dashboard with projects, stats and Next Best Action
- Activity Log
- Agents
- Agent Runs
- Run observability: tokens, cost, duration, model
- Real OpenAI API execution
- Project Context Builder
- Project Memory v1
- Read-only tools
- Protected write tools
- Human-in-the-loop approvals
- Tool Audit
- inspect_project_state
- Efficiency optimization for project inspection
- Automatic memory for approved actions
- Separate Error Log for failed runs
- Agent goal field
- Edit Agent
- Agent goal injected into run context
- Explorer → Builder handoff

## Current agents

### Explorer
Role: Research Agent

Goal:
Analyze the real state of Officina Lab, use available data and tools, find evidence before proposing actions, and suggest the next useful step without modifying anything without approval.

### Builder
Role: Software Engineer

Goal:
Improve Officina Lab through small, testable increments, keeping the code understandable, avoiding unnecessary rewrites, and prioritizing reliability, observability and simplicity.

## Multi-agent workflow v0
Explorer
→ analyzes real project state
→ produces output
→ Handoff to Builder
→ Builder receives original task + Explorer output
→ Builder proposes the next technical intervention

Verified working on 2026-11-03.

## Known limitation discovered
The first Builder handoff can reason from evidence that is already stale.

Example:
Builder proposed implementing Error Log even though Error Log had already been implemented and manually verified.

## Next technical objective
Make Explorer → Builder handoff context-fresh.

Desired flow:

Explorer output
+ current project state snapshot
→ Builder
→ recommendation based on the latest real state

The fresh snapshot should ideally include:
- current tasks
- current agents and goals
- recent runs
- project memories
- recent tool calls
- Error Log / relevant operational state

## Current task-state notes
Implemented in code:
- #9 project context in agent runs
- #8 automatic memory for approved decisions/actions
- #7 separate Error Log
- #6 agent goal field

Some dashboard task statuses may still need to be updated through the approval workflow even though the code already exists.

## Operating rules
- Maximize small, testable increments.
- Do not rewrite working parts without a reason.
- Writes proposed by agents should go through approval.
- Prefer real project evidence over assumptions.
- Keep token/cost/duration observability.
- Keep GitHub as the technical source of truth.
- Maintain this file when an important feature, architecture decision, bug, or next step changes.

## Restart

Terminal 1 — server:

```bash
cd ~/officina-lab
export OPENAI_API_KEY="YOUR_KEY"
python3 -m uvicorn app:app --reload
```

Terminal 2 — commands / Git:

```bash
cd ~/officina-lab
git pull
git status
```

Dashboard:
http://127.0.0.1:8000/

Docs:
http://127.0.0.1:8000/docs

## Next session
1. Pull latest main.
2. Verify Explorer and Builder goals.
3. Implement context-fresh handoff.
4. Run Explorer.
5. Handoff to Builder.
6. Confirm Builder no longer proposes already-completed work.
7. Update this state file.


## Checkpoint 2026-11-04 — Bug Hunter v1

Implemented:
- Bug Hunter specialized role instructions.
- Read-only tool: list_recent_errors.
- Read-only tool: list_project_files.
- Read-only tool: read_project_file.
- Project file inspection excludes secrets, SQLite DB, .git, virtualenvs and path traversal.
- Regression tests added for Bug Hunter behavior.
- Regression tests added for safe project-file inspection.

Current Bug Hunter capability:
- Read recent errors.
- Separate evidence from hypotheses.
- Propose likely cause, confidence, minimal reproduction/test and smallest fix.
- Inspect source/test files to verify whether a fix or regression test is actually implemented.
- No protected writes without approval.

Next verification:
1. Pull latest main.
2. Run:
   python3 -m unittest tests/test_bug_hunter.py tests/test_project_file_tools.py
3. Launch Bug Hunter with:
   "Verifica se il controllo dei placeholder OPENAI_API_KEY è già implementato e coperto da test automatici. Usa list_project_files e read_project_file per ispezionare il codice e i test. Distingui chiaramente: errori storici, implementazione presente, test presenti, verifica end-to-end ancora mancante. Non modificare nulla senza approval."
4. Confirm it cites evidence from services/llm_provider.py and tests/test_api_key_config.py.
