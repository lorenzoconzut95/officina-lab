# Scelta commerciale e specifica del primo MVP

Officina • Decisione proposta al 9 novembre 2026 • Lettura del codice senza esecuzione

Validare per primo il follow up dei preventivi già inviati per serramentisti di Torino e provincia. È un segmento ristretto dell’ipotesi installatori: il risultato è osservabile e si evita di costruire contemporaneamente acquisizione richieste, agenda, preventivazione e gestione interventi. È una raccomandazione da verificare, non domanda commerciale dimostrata.

## Confronto delle opportunità

| Criterio | Installatori e serramentisti | Piccoli servizi B2B |
| --- | --- | --- |
| Problema concreto | Richieste e preventivi da seguire mentre il titolare lavora fuori sede. Primo taglio: preventivi già inviati. | Opportunità senza prossima azione e passaggi commerciali non tracciati. Occorre scegliere un sottosettore. |
| Primi clienti | Aziende e recapiti pubblici facilmente identificabili. Accesso al titolare e interesse ancora da dimostrare. | L’esperienza commerciale B2B del fondatore aiuta il dialogo. Non risultano contatti disponibili o introduzioni confermate. |
| Valore economico | Margine su ordini recuperati e tempo risparmiato; dipende da volume, capacità produttiva e marginalità reale. | Potenziale valore ricorrente dei contratti; durata, costi di erogazione e ciclo di vendita possono ritardare la prova. |
| Complessità | Bassa o media sul solo richiamo. Alta aggiungendo misure, listini, sopralluoghi, urgenze e squadre. | Simile per il solo richiamo. Cresce con CRM, processi operativi diversi, ruoli e integrazioni. |
| Tempo del piccolo MVP | 32–48 ore tecniche; 50–80 ore prudenziali per sviluppo guidato. | Stessa stima se il perimetro è identico. La formula generica non consente una stima affidabile. |

## Cosa sappiamo e cosa manca

Evidenze: il codice contiene task, approvazioni e SQLite. I siti di SE.CO e Poma mostrano richieste di preventivo; Poma descrive anche sopralluoghi. ML Service, nei servizi B2B, descrive sopralluogo, capitolato e attività ricorrenti. Questi esempi confermano i processi, non un problema di follow up o una disponibilità a pagare. [1–4]

Ipotesi decisive: almeno 10 preventivi aperti; richiami oggi saltati; margine sufficiente a giustificare il servizio; referente disposto a usarlo ogni giorno. Nessuna di queste condizioni è già confermata.

Cambiare priorità se emerge prima un’impresa B2B con problema documentato, dati disponibili e impegno economico concreto. Il vantaggio del primo target è la chiarezza dell’offerta, non un vantaggio tecnico esclusivo. Un CRM gratuito è già un’alternativa: il valore da vendere è l’avvio e la gestione del processo. [5]

## Pilota e criteri di validazione

Perimetro: 30 giorni dall’attivazione; una sola azienda, un referente cliente e Lorenzo; massimo 30 preventivi e due richiami ciascuno. Inserimento manuale guidato, testi predefiniti, scadenze nel cruscotto, approvazione e invio manuale dal cliente. Nessun modello AI è necessario nel pilota.

Misurazione: registrare prima dell’avvio 10 casi recenti e i minuti impiegati nel processo corrente. Durante il pilota misurare il tempo su almeno 10 casi comparabili. Non presentare il confronto prima/dopo come prova causale di vendite aggiuntive.

| Indicatore | Definizione e soglia proposta |
| --- | --- |
| Puntualità primaria | Invii dichiarati entro 1 giorno lavorativo / richiami dovuti. Obiettivo ≥90%; riportare i conteggi. Escludere solo stop registrati prima della scadenza; rinvii tardivi restano ritardi. Se zero dovuti, test inconcludente. |
| Risultato commerciale | Numero di risposte utili, appuntamenti, preventivi vinti e margine relativo. Fonte: conferma del cliente; non conteggiare il valore totale dei preventivi come ricavo recuperato. |
| Uso e tempo | Minuti complessivi, incluse approvazioni e registrazione. Obiettivo secondario: riduzione ≥30% rispetto ai casi iniziali, da concordare; evitare di trasferire semplicemente lavoro al cliente. |

## Prezzo e sostenibilità da testare

Prezzo pilota: 690 €, oltre IVA se dovuta; 50% alla conferma, 50% all’attivazione verificata. Eventuale seguito: 249 €/mese, massimo 30 nuovi preventivi e 3 ore di assistenza. Sono prezzi di esperimento, non tariffe validate dal mercato.

| Voce | Ipotesi interna |
| --- | --- |
| Spese vive per mese | 20–40 € di budget per hosting con disco persistente, backup e accesso protetto. Stima di pianificazione, non preventivo di un fornitore. Email cliente già disponibile; AI e API messaggi: 0 €. |
| Primo sviluppo | 32–48 h × 30 €/h = 960–1.440 € di tempo valorizzato. Per 50–80 h guidate: 1.500–2.400 €. Non è un esborso se sviluppi tu. |
| Erogazione primo pilota | 6–8 h × 30 €/h = 180–240 €, oltre allo sviluppo. Contributo prima dello sviluppo: 410–490 €; dopo lo sviluppo minimo: perdita 470–1.030 €. |
| Mese successivo | 249 € meno 20–40 € e 3 h × 30 € = 119–139 €, prima di acquisizione, imposte e spese generali. Ore extra riducono il margine. |

Esempio puramente ipotetico: 690 € si coprono con un ordine realmente aggiuntivo da 900 € di margine di contribuzione, oppure con 27,6 ore risparmiate valutate 25 €/h. Il solo risparmio di tempo su pochi preventivi potrebbe non bastare. Misurare margine, non fatturato.

Prima di costruire tutto: selezionare 15 aziende, svolgere 5 conversazioni effettive e far esaminare il flusso a 2 titolari. Procedere con almeno 2 problemi documentati e 1 pilota accettato al prezzo proposto, con dati e referente disponibili. Cortesia e interesse verbale non valgono come vendita. Dopo 10 conversazioni qualificate senza un impegno pagante, rivedere problema, target o offerta. Attività ancora da eseguire; nessun contatto è stato avviato.

## Codice verificato e riuso possibile

Snapshot remoto: main al commit fe6bea5c75f44b35d2832f0b3b28a44ce2216628, del 6 novembre 2026. Verifica del 9 novembre: lettura di sorgenti e albero file, senza test, avvio del server o ispezione di modifiche su computer locali. “Implementato” qui significa presente nel sorgente, non collaudato per un cliente.

| Componente verificato | Stato e impiego nel pilota |
| --- | --- |
| app.py e routes/tasks.py | Implementati FastAPI, /health, file statici e CRUD /api/tasks. Riutilizzabili come struttura e gestione delle attività. |
| models.py e repositories/tasks.py | Implementati titolo, stato, priorità, progetto e creazione. Mancano cliente, scadenza, responsabile e collegamento al preventivo. |
| database.py | SQLite e inizializzazione schema già presenti. Riutilizzabili per una singola istanza; servono migrazione, volume persistente e prova di ripristino. |
| routes/approvals.py e servizi | Implementati elenco, approve e reject. Il servizio gestisce create_task, update_task_status e incident_builder_proposal. Nessuna approvazione di invio messaggi. |
| repositories/approvals.py | Payload JSON, stato e timestamp già persistiti. Riutilizzabili con validazione, versione del testo e transazioni coerenti per il nuovo flusso. |
| static/app.js e index.html | Esistono viste task e approvazioni. È riutilizzabile la struttura; serve una schermata cliente semplice per preventivi, scadenze e testi. |
| Activity e sistema run AI | Esistono log di attività e infrastruttura di esecuzione AI. Il log attuale non prova invii e non identifica l’operatore; il motore AI resta fuori dal pilota. |

## Sviluppo necessario prima di usare dati reali

Nuovi dati di preventivo e follow up; scadenze; testi compilati da modello fisso; azione di approvazione dedicata; conferma manuale di esecuzione; registrazione risposte e stop; report con metriche; schermata mobile; accessi, backup ed esportazione dei dati.

Nel codice letto non è presente un livello di autenticazione per le rotte. Il campo project non isola i clienti. Per il pilota usare una sola istanza e database dedicati, identità distinte per cliente e operatore, accesso autenticato su tutte le API e HTTPS; non esporre le altre funzioni di laboratorio.

Dettaglio da correggere: approve() può segnare “approved” anche un’azione sconosciuta; lettura, effetto e risoluzione usano passaggi separati. Non basta aggiungere una voce alla UI. Servono elenco esplicito delle azioni ammesse e transazione atomica per evitare effetti duplicati o stati incoerenti.

I test presenti nell’albero riguardano soprattutto executor, incidenti e provider. Non costituiscono prova del pilota commerciale; non sono stati eseguiti in questa verifica. [1]

## Workflow e contratto minimo dei dati

1. Registrazione. Il cliente o Lorenzo inserisce un preventivo già inviato: riferimento univoco, contatto, canale, data di invio, responsabile e importo facoltativo. Si conferma che il contatto riguarda una richiesta già ricevuta. Niente PDF, foto o estrazione automatica nella prima versione.

2. Pianificazione. Il servizio genera due attività con scadenza, inizialmente a +3 e +10 giorni di calendario dall’invio; sabato e domenica slittano a lunedì. Orario Europe/Rome; festivi e date particolari si correggono a mano. Un arretrato genera un solo richiamo immediato, poi uno dopo almeno 7 giorni.

3. Revisione. Il cruscotto mostra i richiami dovuti al momento dell’apertura o aggiornamento. Il testo usa solo campi confermati. Il cliente può modificare, rinviare, rifiutare o approvare. L’approvazione memorizza la versione esatta del testo e abilita “Copia testo”; non invia niente.

4. Esecuzione. Il cliente invia dal proprio account e seleziona “Confermo inviato”, con data, ora e canale. Un testo approvato o copiato non viene contato come inviato. Il sistema non può verificare autonomamente la consegna: il report esplicita che il dato è dichiarato dal cliente.

5. Esito. La risposta, il rifiuto, la vittoria o una richiesta di non essere ricontattati fermano gli altri richiami. Dopo due tentativi senza risposta il caso resta “senza risposta”, non “perso”. Una trattativa riaperta richiede una nuova scadenza manuale. Se cambia il testo, occorre una nuova approvazione.

| Dati da aggiungere | Campi essenziali |
| --- | --- |
| quotes | id, external_ref UNIQUE, contact_name, contact_channel, contact_value, sent_at, owner, status, amount_cents opzionale, do_not_contact, created_at, updated_at. |
| followups e tasks | quote_id, task_id, sequence_no, due_at, draft_text, draft_version, approval_id, status, sent_at, sent_by. Vincolo UNIQUE(quote_id, sequence_no); tasks mantiene il lavoro operativo. |
| quote_events | quote_id, followup_id opzionale, event_type, actor_id, occurred_at, dettaglio minimo. Esiti e timestamp per ricostruire i conteggi; niente contenuti completi delle email. |

Stati del follow up: scheduled → pending_approval → ready → sent; alternative rejected, postponed e cancelled. Stati preventivo: open, responded, won, lost, no_response, do_not_contact. Un task done non prova un invio. Regole e transizioni vanno validate sul server.

API proposte, tutte da sviluppare: POST/GET/PATCH /api/quotes; GET /api/followups?due_before=…; POST /api/followups/{id}/request-approval; POST /api/followups/{id}/mark-sent; POST /api/quotes/{id}/events; GET /api/pilot-report. Riusare approve/reject aggiungendo l’azione release_followup con payload tipizzato e versione.

Transazione unica per approvazione e passaggio a ready; controllo versione e vincoli per doppio clic. mark-sent è idempotente. Stop, risposta e chiusura cancellano i richiami non eseguiti e invalidano le approvazioni pendenti. Nessun cron o integrazione di posta è richiesto: l’uso quotidiano del cruscotto è parte esplicita del pilota.

## Consegna e verifiche prima del pilota

| Passo sequenziale | Ore e contenuto |
| --- | --- |
| Modello dati e migrazione | 6–8 h: dati sintetici, riferimenti, scadenze, vincoli e collegamento ai task. |
| Interfaccia e workflow | 10–16 h: registro preventivi, filtri dovuti, testi, approve/reject, invio dichiarato, stop. |
| Accessi e continuità | 8–12 h: accesso protetto, istanza dedicata, backup, ripristino ed esportazione. |
| Misure e collaudo | 8–12 h: report, casi di prova e verifica con il titolare. Totale 32–48 h. |

Stima a bassa confidenza, prima del collaudo: 8–12 giorni a 4 ore/giorno per sviluppo già familiare con lo stack; per sviluppo guidato prevedere 50–80 ore, cioè 13–20 giorni lavorativi. Una demo locale sintetica può richiedere 8–12 ore, incluse nel totale, ma non è un sistema pronto per dati reali. I tempi per acquisire un cliente restano separati e non prevedibili.

## Criteri di accettazione

Su 10 preventivi sintetici verificare: rifiuto di riferimenti duplicati; scadenze e rinvio corretto del weekend; due richiami massimi; nessuna duplicazione dopo doppio clic o riavvio; approvazione legata alla versione del testo; stop immediato su risposta o chiusura; nessun messaggio inviato dal sistema; metriche coerenti con gli eventi, anche con zero richiami dovuti.

Verificare anche: accesso negato senza autenticazione; un operatore non può confermare per errore con l’identità del cliente; nessuna perdita dei dati dopo riavvio; backup ripristinato su database separato; export leggibile. Prima dell’attivazione il titolare completa da telefono un caso registrazione → approvazione → invio manuale → esito.

Dati e responsabilità: raccogliere il minimo, concordare accessi, trattamento e tempi di conservazione; separare database e backup dall’ambiente di studio; esportare i dati al termine e concordare la cancellazione. Nessun invio a modelli AI o accesso automatico alle caselle nel perimetro iniziale.

Sequenza di lavoro: validare il problema, ottenere un impegno pagante, completare un solo flusso e collaudarlo, poi avviare i 30 giorni. Prima funzionalità da chiudere: preventivo registrato → richiamo approvato → esecuzione dichiarata → report coerente. Principio operativo: un solo flusso alla volta, con esito verificabile.

## Fonti consultate e limiti

[[1] Officina Lab — commit verificato e sorgenti](https://github.com/lorenzoconzut95/officina-lab/tree/fe6bea5c75f44b35d2832f0b3b28a44ce2216628)

[[1a] Task API](https://github.com/lorenzoconzut95/officina-lab/blob/fe6bea5c75f44b35d2832f0b3b28a44ce2216628/routes/tasks.py)

[[1b] Logica effettiva delle approvazioni](https://github.com/lorenzoconzut95/officina-lab/blob/fe6bea5c75f44b35d2832f0b3b28a44ce2216628/services/approvals.py)

[[2] SE.CO — richiesta di preventivo](https://www.secoserramenti.it/corsaro-serramenti-chiama-subito/)

[[3] Poma — preventivi e sopralluoghi](https://www.pomaserramenti.it/servizi/)

[[4] ML Service — sopralluogo e servizi B2B ricorrenti](https://www.mlservicetorino.it/servizi/pulizie-uffici-torino/)

[[5] HubSpot — alternativa CRM gratuita](https://www.hubspot.com/products/crm)

Le aziende citate sono esempi pubblici di processo, non clienti o prospect qualificati. Per Poma è disponibile il risultato indicizzato; l’apertura diretta è scaduta. Non sono disponibili interviste, margini aziendali, adesioni o disponibilità a pagare. Prezzi, soglie, costi e ore sono ipotesi da validare. La verifica non ha modificato codice applicativo né eseguito invii commerciali.
