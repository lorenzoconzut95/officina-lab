# Officina Lab

Laboratorio di software e agenti AI di Lorenzo Conzut: task, approvazioni umane, esecuzione di agenti e tracce verificabili delle operazioni. Stack: Python, FastAPI, SQLite e JavaScript.

**Stato al 9 novembre 2026:** codice di laboratorio presente; nessuna applicazione commerciale per serramentisti o servizi B2B dichiarata pronta. La ricognizione documentale di oggi non ha eseguito la suite né verificato una demo pubblica.

## Esplora il portfolio

| Progetto o componente | Stato documentato | Prova consultabile |
| --- | --- | --- |
| Task e approvazioni | Implementati nel sorgente | [Task API](routes/tasks.py), [servizio approvazioni](services/approvals.py), [SQLite](database.py) |
| Esecuzione agenti e audit | Implementati nel sorgente | [Executor](services/executor.py), [provider](services/llm_provider.py), [registro richieste](repositories/model_requests.py) |
| Bug Hunter e incidenti | Codice, test e casi storici presenti | [Caso API key](docs/case-studies/bug-hunter-001-api-key.md), [test](tests/) |
| Follow up preventivi | Progettato, da validare e implementare | [Pilota commerciale](docs/pilots/preventivi-followup/README.md) |

L’[indice portfolio](docs/PORTFOLIO.md) distingue codice disponibile, esperimenti e idee. I test presenti sono verifiche riproducibili, non una certificazione di produzione. I risultati storici vanno letti con la loro data.

## Avvio locale

Da una copia del repository, con Python e un ambiente virtuale:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1
```

Aprire `http://127.0.0.1:8000/` per il cruscotto e `http://127.0.0.1:8000/docs` per le API. `GET /health` espone il controllo di salute. SQLite usa il file locale `tasks.db`.

Senza `OPENAI_API_KEY`, l’executor produce un piano locale predefinito: non è una risposta di un modello AI. L’esecuzione AI richiede configurazione nel proprio ambiente e può generare costi. Non inserire chiavi nel repository.

Il codice di laboratorio non include un livello di autenticazione per le API esaminate: mantenere l’avvio locale. L’accesso protetto è un requisito aperto del pilota commerciale.

## Test

Comando per eseguire i test presenti in un ambiente isolato:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Il comando non è stato eseguito durante l’aggiornamento documentale del 9 novembre. I test si concentrano su provider, executor, incidenti, budget delle richieste e strumenti di lettura. Il futuro flusso preventivi richiede test propri.

## Struttura

- `routes/`: API HTTP.
- `services/`: logica applicativa, executor e strumenti degli agenti.
- `repositories/` e `database.py`: persistenza SQLite.
- `static/`: interfaccia web.
- `tests/`: suite automatizzata.
- `docs/case-studies/`: problemi affrontati ed evidenze storiche.
- `docs/pilots/`: specifiche e criteri di validazione dei servizi.

## Come rendiamo verificabile ogni progetto

Per ogni incremento: problema, stato, codice o specifica, istruzioni di prova, risultato osservato, limiti e commit. Una demo sintetica, un test locale e un risultato ottenuto da un cliente sono evidenze diverse.

Seguire il [protocollo di pubblicazione](docs/PORTFOLIO_WORKFLOW.md). Per il contesto storico consultare [OFFICINA_STATE.md](OFFICINA_STATE.md), che contiene checkpoint con date diverse.
