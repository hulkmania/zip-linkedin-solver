# ZIP LinkedIn Solver

Solver automatico per il gioco ZIP di LinkedIn.

## Funzionalità
- Parsing DOM reale
- Rilevamento muri TOP / RIGHT / BOTTOM / LEFT
- DFS con backtracking ottimizzato
- Cutoff intelligenti (Manhattan distance, connettività)
- Click automatico delle celle
- Logging dettagliato in `solver.log`
- Profilo browser persistente (salva sessione LinkedIn)

## Installazione

### 1. Clonare/aprire il progetto
```bash
cd c:\Users\Daniele\Progetti\Python\zip-linkedin-solver
```

### 2. Creare ambiente virtuale (se non esiste)
```bash
python -m venv .venv
.venv\Scripts\Activate
```

### 3. Installare dipendenze
```bash
pip install -r requirements.txt
```

### 4. Installare Chromium per Playwright (solo prima volta)
```bash
python -m playwright install chromium
```

## Come usare

### Primo avvio
1. Apri PowerShell nella cartella del progetto
2. Esegui:
```bash
.venv\Scripts\python.exe main.py
```
3. Quando si apre il browser su LinkedIn:
   - Fai il login con il tuo account
   - Premi INVIO sulla console
4. Il programma naviga al gioco ZIP
5. Osserva il puzzle, poi premi INVIO
6. Il solver risolve automaticamente il gioco! 🎮

### Avvii successivi
- Sei già loggato da ieri, premi subito INVIO quando te lo chiede
- Il profilo browser ricorda la tua sessione
- Ogni volta che il puzzle si aggiorna (24 ore), il solver lo risolve automaticamente

## Output

- **Console**: Messaggi di progresso (`✓ Soluzione trovata!`, ecc.)
- **solver.log**: Log dettagliato di ogni percorso scartato, utile per debug
- **browser_profile/**: Profilo browser con sessione LinkedIn salvata

## Struttura del progetto

```
.
├── main.py                 # Entry point principale
├── requirements.txt        # Dipendenze Python
├── README.md              # Questo file
├── solver.log             # Log dettagliato dell'algoritmo
└── zip_solver/
    ├── __init__.py
    ├── bot.py            # Automazione click delle celle
    ├── cell.py           # Classe cella (numero, muri)
    ├── dom_reader.py     # Estrae griglia dal DOM di LinkedIn
    ├── grid.py           # Classe griglia
    └── solver.py         # DFS con backtracking + cutoff
```

## Algoritmo

Il solver usa **DFS ricorsivo con backtracking** per trovare il percorso:

1. Parte dalla cella con numero 1
2. Visita le celle in ordine crescente dei numeri
3. Applica cutoff intelligenti:
   - **Manhattan distance**: Se la distanza al prossimo numero è > celle rimanenti, scarta il percorso
   - **Connettività**: Se le celle non visitate si dividono in isole separate, scarta
4. Se trova un vicolo cieco, backtrack e prova un'altra strada
5. Registra tutto nel log per debugging

## Troubleshooting

**Errore: "playwright install chromium"**
- Esegui il comando di installazione di Playwright (vedi sopra)

**Errore: "timeout waiting for selector"**
- LinkedIn potrebbe aver cambiato il layout
- Controlla il DOM del sito e aggiorna i selettori in `main.py` e `dom_reader.py`

**Il gioco non viene risolto (solver.log mostra 0 percorsi)**
- Controlla `solver.log` per capire quale regola lo ha bloccato
- Potrebbe essere un puzzle particolarmente difficile
- Report il problema!

**Vuoi resettare la sessione LinkedIn**
- Elimina la cartella `browser_profile/`
- Al prossimo avvio, dovrai fare login di nuovo
