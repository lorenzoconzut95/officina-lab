# Pilota follow up preventivi

**Stato: progettato, da implementare e validare.** Nessun cliente interessato, pagamento o risultato commerciale confermato.

Prima offerta da testare: aiutare un serramentista di Torino e provincia a seguire i preventivi già inviati, con scadenze, testi da approvare, invio manuale e misurazione degli esiti.

## Materiali

- [Proposta commerciale](proposta.md): 30 giorni, massimo 30 preventivi, 690 € da verificare.
- [Decisione e specifica essenziale](spec.md): confronto con servizi B2B, ipotesi economiche, codice riutilizzabile, workflow, dati e collaudo.

## Che cosa esiste oggi

Nel repository sono presenti CRUD dei task, persistenza SQLite, approvazioni di alcune azioni interne e UI di laboratorio. Mancano il modello preventivo, le scadenze, l’approvazione del testo, la conferma dell’invio, il report commerciale e l’accesso protetto per il cliente.

Le approvazioni esistenti non inviano messaggi. Il pilota proposto usa testi fissi personalizzabili e invio umano; non richiede un modello AI nella prima versione.

## Prima prova da costruire

Un preventivo sintetico genera un richiamo, il referente approva il testo, dichiara l’invio manuale e registra una risposta. La risposta ferma i richiami residui e il report ricostruisce gli eventi senza contare approvazioni come invii.

Completare questa sola funzionalità prima di aggiungere integrazioni, agenti, WhatsApp automatico o agenda sopralluoghi.

## Base tecnica

La specifica è fondata sulla lettura del codice al commit `fe6bea5c75f44b35d2832f0b3b28a44ce2216628`. La pubblicazione di questi documenti non aggiunge funzionalità applicative e non sostituisce il collaudo.
