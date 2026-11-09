# Portfolio Officina

Indice delle prove disponibili al 9 novembre 2026. L’elenco non certifica che tutti i prodotti siano pronti o che abbiano clienti.

| Progetto | Stato | Evidenze | Prossima prova utile |
| --- | --- | --- | --- |
| Officina Lab | Codice di laboratorio | [Sorgenti](../), [test](../tests/), [checkpoint storici](../OFFICINA_STATE.md) | Avvio riproducibile e report di test aggiornato |
| Bug Hunter | Componente AI di Officina Lab | [Caso API key](case-studies/bug-hunter-001-api-key.md), [test ruolo](../tests/test_bug_hunter.py), [incidenti](../services/incidents.py) | Dimostrazione riproducibile con dati sintetici e limiti espliciti |
| Follow up preventivi | Specificato; implementazione commerciale assente | [Offerta, specifica e accettazione](pilots/preventivi-followup/README.md) | Un caso completo su dati sintetici; poi pilota pagante |
| Officina Academy | Repository pubblico con index.html presente | [Repository](https://github.com/lorenzoconzut95/officina-academy) | Verificare avvio e funzionalità; in questa ricognizione è stato letto solo l’inventario |
| SurfOps | Idea in backlog | Obiettivo: operazioni di surfhouse e scuole surf; codice dedicato non verificato qui | Definire un singolo caso e produrre una prova prima di presentarlo come prodotto |
| GTM Agent | Idea in backlog | Obiettivo: supporto al lavoro commerciale; codice dedicato non verificato qui | Definire perimetro, dati e verifica |

Paperclip resta un riferimento esterno: non viene presentato come software originale di Officina. Nessun materiale di clienti, credenziale o dato operativo reale è incluso in questi nuovi documenti.

## Lettura corretta delle evidenze

- **Progettato:** esistono problema, specifica e criteri di accettazione.
- **Implementato:** esiste codice collegato a un commit; non implica test superati.
- **Verificato localmente:** esistono comando, ambiente, data e risultato della prova.
- **Dimostrabile:** un’altra persona può riprodurre il caso con dati sintetici.
- **Validato con un cliente:** esistono dati osservati e un impegno economico; eventuale pubblicazione del caso richiede il permesso del cliente.

Ogni scheda mantiene separati stato tecnico e stato commerciale. Le prove mancanti restano esplicite.
