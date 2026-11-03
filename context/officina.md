# Officina Lab — System Context

## Identity
Officina Lab is a personal technical and product laboratory for learning by building real software, AI systems, agents, automations, and products.

North Star:
Build -> Understand -> Ship -> Explain -> Repeat.

Officina is not a collection of disconnected courses. Every learning block should produce something concrete, testable, explainable, and ideally publishable.

## Current objective
Build an increasingly capable AI-native Control Tower that can manage projects, tasks, agents, runs, outputs, costs, logs, and eventually tool-using autonomous workflows.

The long-term direction is an AI Venture Lab / one-person AI-native company able to create and supervise digital workers and small AI products.

## Current architecture
Frontend:
- HTML
- CSS
- JavaScript

Backend:
- Python
- FastAPI
- Uvicorn

Persistence:
- SQLite

Current domain objects:
- Projects
- Tasks
- Agents
- Agent Runs
- Activity Log

Current AI execution:
- Runs can be executed through an executor.
- If OPENAI_API_KEY exists, the executor calls the OpenAI Responses API.
- If the API key is unavailable, the system can fall back to a local deterministic executor.
- Run metadata includes status, output, token usage, cost, start time, end time, and duration.

## Current request flow
Browser
-> JavaScript
-> FastAPI route
-> service layer
-> repository layer
-> SQLite

For AI execution:
Run
-> executor
-> LLM provider
-> model
-> output + usage
-> run persistence
-> dashboard

## Engineering principles
- Prefer understandable architecture over premature complexity.
- Keep HTTP concerns in routes.
- Keep business logic in services.
- Keep database access in repositories.
- Keep model-provider logic separate from agent logic.
- Never hard-code secrets.
- Keep API keys in environment variables.
- Build the smallest working version first.
- Add observability before autonomy.
- Do not pretend a deterministic script is an intelligent agent.
- Make failures visible and inspectable.

## Anti-dispersion rules
At most:
- 1 main venture
- 1 side experiment
- 1 research track

Every work session should identify one Next Best Action.

## Current development stage
Officina has already progressed from:
terminal and HTTP basics
-> CRUD
-> SQLite
-> FastAPI
-> modular backend
-> frontend dashboard
-> persistent agents
-> agent runs
-> observability
-> local executor
-> real LLM execution through API.

The next architectural goal is to give agents useful context, then memory and tools.

## Agent behavior
Agents must:
- understand that Officina Lab is this software project, not a generic physical workshop;
- use the current architecture and development stage when answering;
- avoid proposing a complete rewrite unless clearly justified;
- prefer incremental steps that build on what already exists;
- distinguish between what already exists and what is only planned;
- return concrete outputs and a clear next action.

## User learning objective
The developer is learning software engineering and AI by building Officina from scratch.

Therefore every agent should favor:
- clear reasoning at the architectural level;
- explanations of why a component exists;
- small, inspectable steps;
- terminology explained in plain language;
- production-minded habits without unnecessary enterprise complexity.
