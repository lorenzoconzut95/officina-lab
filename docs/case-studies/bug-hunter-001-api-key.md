# Bug Hunter v1 — Case Study 001
## Detecting and closing an OpenAI API key configuration failure

**Date:** 2026-11-04  
**Project:** Officina Lab  
**Agent:** Bug Hunter  
**Status:** Verified

## Problem

Several historical agent runs failed with OpenAI HTTP 401 `invalid_api_key`.

The Error Log showed a masked value compatible with a placeholder configuration:

```text
LA_TUA_C*IAVE
```

The initial question was not only:

> Why did the run fail?

It became:

> Is the failure already fixed in the current codebase, is it covered by tests, and what evidence is still missing?

## Bug Hunter role

Bug Hunter is a specialized Officina agent for debugging.

Its operating rules are:

- read real error evidence;
- separate observations from hypotheses;
- estimate confidence;
- inspect source and test files in read-only mode;
- propose the smallest reproducible test;
- propose the smallest fix;
- never perform protected writes without approval.

## Evidence sources

Bug Hunter used:

- `list_recent_errors`
- `list_project_files`
- `read_project_file`

Relevant files inspected:

- `services/llm_provider.py`
- `services/executor.py`
- `tests/test_api_key_config.py`
- `tests/test_executor_api_key.py`

## Diagnosis

Historical runs failed because an invalid API key reached the OpenAI provider.

The current code now distinguishes three API-key states:

```text
missing
placeholder
ok
```

Known placeholder markers include:

```text
la_tua_chiave
your_key
incolla_qui
paste_here
sk-your
sk-xxx
```

## Fix

The executor now performs fail-fast validation.

Desired behavior:

```text
OPENAI_API_KEY
↓
get_api_key_status()
↓
placeholder detected
↓
execute_run() fails clearly
↓
run_llm() is NOT called
```

This prevents a known bad configuration from reaching the provider.

## Regression coverage

### Unit classification tests

`tests/test_api_key_config.py` checks:

1. missing API key → not configured;
2. placeholder API key → rejected;
3. realistic-looking key → accepted.

### Executor regression test

`tests/test_executor_api_key.py` verifies that a placeholder:

- causes the run to fail;
- returns a clear configuration message;
- does not call `run_llm()`.

### Integration-style environment test

The test suite also injects:

```text
OPENAI_API_KEY=" LA_TUA_CHIAVE "
```

into an isolated environment and exercises the real key-classification path through `execute_run()`.

## Security constraint

Bug Hunter's source inspection is read-only.

It cannot read:

- `.env`
- SQLite database files;
- `.git`;
- virtual environments;
- files outside the project via path traversal.

## Result

The incident moved through this lifecycle:

```text
historical failure
↓
error evidence
↓
Bug Hunter diagnosis
↓
source inspection
↓
test-gap discovery
↓
regression test added
↓
integration-style test added
↓
suite green
↓
Bug Hunter verifies closure
```

## What this demonstrates

Bug Hunter is not just a chatbot that comments on an error message.

It can connect:

- runtime evidence;
- current source code;
- regression tests;
- implementation status.

That makes it a first concrete vertical agent inside Officina Lab.

## Next evolution

Possible next capabilities:

- group duplicate errors into incidents;
- rank failures by severity and recurrence;
- link an error to the commit or task that fixed it;
- propose a regression test as a protected write;
- generate a compact incident report for GitHub.
