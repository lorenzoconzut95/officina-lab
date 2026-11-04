# Incident Case Study — openai_api_key

**Incident ID:** 1
**Status:** investigating
**Severity:** high
**Occurrences:** 4

## Problem

Il run #30 termina con un errore di configurazione perché `OPENAI_API_KEY` contiene un valore riconosciuto come placeholder. L’errore è esplicito e impedisce di procedere con l’esecuzione LLM.

## Evidence

Gli errori storici dei run #19–21 riportano 401 `invalid_api_key` e un valore mascherato compatibile con `LA_TUA_CHIAVE`. L’errore più recente, invece, segnala il placeholder prima della chiamata al provider. Nel codice, `services/llm_provider.py` classifica i placeholder e `services/executor.py` fallisce il run senza chiamare `run_llm()`. Sono presenti test in `tests/test_api_key_config.py` e `tests/test_executor_api_key.py`, incluso un test che passa un placeholder attraverso `execute_run()`. L’ispezione non ha eseguito i test.

## Root cause

Per gli errori storici, una chiave placeholder arrivava al provider e veniva rifiutata. Per il run #30, le evidenze indicano che il controllo attuale funziona: la variabile d’ambiente del server contiene ancora un placeholder. La sua configurazione effettiva non è verificabile dai file ispezionati. I test coprono classificazione e comportamento dell’executor, ma non una verifica end-to-end con server e persistenza reali; non serve una chiamata live a OpenAI per testare il rifiuto del placeholder.

## Confidence

Alta sul funzionamento del fail-fast nel codice e sulla presenza dei test; media sulla configurazione runtime, non ispezionata. Il run #30, da solo, non dimostra un nuovo bug nel controllo.

## Minimal test

Eseguire `python -m unittest tests.test_api_key_config tests.test_executor_api_key` per verificare i test presenti. Come verifica end-to-end mancante, eseguire un run tramite il percorso applicativo reale con `OPENAI_API_KEY` impostata a un placeholder e verificare che il run fallisca con il messaggio atteso senza invocare il provider.

## Smallest fix

Non modificare il codice per questo sintomo: sostituire nel terminale/server `OPENAI_API_KEY` con una chiave reale e riavviare il processo affinché rilegga la variabile. Nessuna modifica è stata effettuata.

## Latest error

Run #30 · Agent: Buh Hunter

OpenAI configuration error: OPENAI_API_KEY contains a placeholder value. Set a real API key in the server terminal before executing this run.

## Bug Hunter analysis

Run #48 · completed

Model: gpt-6-luna

SYMPTOM: Il run #30 termina con un errore di configurazione perché `OPENAI_API_KEY` contiene un valore riconosciuto come placeholder. L’errore è esplicito e impedisce di procedere con l’esecuzione LLM.

EVIDENCE: Gli errori storici dei run #19–21 riportano 401 `invalid_api_key` e un valore mascherato compatibile con `LA_TUA_CHIAVE`. L’errore più recente, invece, segnala il placeholder prima della chiamata al provider. Nel codice, `services/llm_provider.py` classifica i placeholder e `services/executor.py` fallisce il run senza chiamare `run_llm()`. Sono presenti test in `tests/test_api_key_config.py` e `tests/test_executor_api_key.py`, incluso un test che passa un placeholder attraverso `execute_run()`. L’ispezione non ha eseguito i test.

ROOT_CAUSE: Per gli errori storici, una chiave placeholder arrivava al provider e veniva rifiutata. Per il run #30, le evidenze indicano che il controllo attuale funziona: la variabile d’ambiente del server contiene ancora un placeholder. La sua configurazione effettiva non è verificabile dai file ispezionati. I test coprono classificazione e comportamento dell’executor, ma non una verifica end-to-end con server e persistenza reali; non serve una chiamata live a OpenAI per testare il rifiuto del placeholder.

CONFIDENCE: Alta sul funzionamento del fail-fast nel codice e sulla presenza dei test; media sulla configurazione runtime, non ispezionata. Il run #30, da solo, non dimostra un nuovo bug nel controllo.

MINIMAL_TEST: Eseguire `python -m unittest tests.test_api_key_config tests.test_executor_api_key` per verificare i test presenti. Come verifica end-to-end mancante, eseguire un run tramite il percorso applicativo reale con `OPENAI_API_KEY` impostata a un placeholder e verificare che il run fallisca con il messaggio atteso senza invocare il provider.

SMALLEST_FIX: Non modificare il codice per questo sintomo: sostituire nel terminale/server `OPENAI_API_KEY` con una chiave reale e riavviare il processo affinché rilegga la variabile. Nessuna modifica è stata effettuata.

## Lifecycle

Created: 2026-11-04 14:25:47
Updated: 2026-11-04 15:13:33
Resolved: not resolved
