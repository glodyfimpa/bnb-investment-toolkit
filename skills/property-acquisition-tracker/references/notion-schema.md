# Notion binding — database "(DB) Appartamenti BNB"

Mapping dei campi generici di Step 6 sul database Notion reale di Glody (data source
`collection://57b0527a-512f-42b5-afa3-74f982afc1db`, verificato 2026-09-29). Usare questi nomi
esatti quando il connettore ~~project tracker è Notion.

| Campo generico (Step 6) | Proprietà Notion | Tipo / opzioni |
|---|---|---|
| Name | `Name` | title |
| URL | `URL` | url |
| Price | `Prezzo` | number (euro) |
| Size | `Mq` | number |
| Zone | `Zona` | text |
| Rooms | `Locali` | number |
| Floor | `Piano` | text (es. "3°", "Terra") |
| Condo fees | `Spese Condo` | number (euro) |
| Score | `Score` | number |
| Investment Status | `Status Investimento` | select: Hot, Review, Watch, Skip |
| Source | `Fonte` | select: Immobiliare, Idealista, Casa.it |
| Contract type | `Tipo Contratto` | select: 4+4, 3+2, Transitorio, Uso Foresteria |
| Scan Date | `Data Scansione` | date |
| Notes | `Notes` | text (mini-report) |

**Alla creazione imposta sempre `Aggiunto su BNB` = false** (checkbox non spuntata): è il trigger
dell'automazione Make che elabora l'annuncio a valle.

**Non scrivere** `Revisionato` e `Processed Date`: sono gestiti a valle (revisione manuale / Make).

Se una proprietà manca nel database, creala prima di salvare (stessi nomi e tipi della tabella).
Se la scrittura fallisce: logga l'annuncio in locale, continua e riporta i fallimenti nel riepilogo.

## Formato Notes (mini-report)

```
Rent: 1,200€ + Condo: 150€ = Total: 1,350€
Size: 55 m² | Floor: 3° | Energy: C
Zone avg rate: 125€/night
Quick Score: 28.5 (Review)
```

## Esempio di riepilogo scan

```
Scan completed:
- Immobiliare.it: 47 listings scanned
- Idealista: 52 listings scanned
- Duplicates skipped: 12
- Saved to Notion: 18 (Hot: 5, Review: 13)
- Skipped: 69 (low score: 41, wrong zone: 18, price: 10, wrong contract: 8, no elevator: 5, no subletting: 3)
```
