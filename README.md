     1|# LinkedIn Games Solver
     2|
     3|Risolve automaticamente i giochi ZIP e Sudoku di LinkedIn.
     4|
     5|## Funzionalità
     6|- **Menu Interattivo**: Scegli quale gioco risolvere (ZIP o Sudoku).
     7|- **Blocco Timer Ottimizzato**: Mette in pausa il timer del gioco chiudendo temporaneamente la pagina durante la risoluzione, riaprendola per completare.
     8|- **Solver ZIP**: Parsing DOM, rilevamento muri, DFS con backtracking ottimizzato, cutoff intelligenti, click automatico delle celle.
     9|- **Solver Sudoku**: Parsing DOM per griglie 6x6 (numeri 1-6, sotto-griglie 3x2), algoritmo di backtracking per la risoluzione, interazione con keypad virtuale per l'inserimento dei numeri.
    10|- **Logging Dettagliato**: `solver.log` registra i percorsi ZIP scartati e la soluzione finale, oltre a debug per il Sudoku.
    11|- **Profilo Browser Persistente**: Salva la sessione LinkedIn per evitare login ripetuti.
    12|- **Gestione Errori Robusta**: Include fallback (es. force click) e messaggi informativi per il debug.
    13|
    14|## Installazione
    15|
    16|### 1. Clonare/aprire il progetto
    17|```bash
    18|cd c:\Users\Daniele\Progetti\Python\zip-linkedin-solver
    19|```
    20|
    21|### 2. Creare ambiente virtuale (se non esiste)
    22|```bash
    23|python -m venv .venv
    24|.venv\Scripts\Activate
    25|```
    26|
    27|### 3. Installare dipendenze
    28|```bash
    29|pip install -r requirements.txt
    30|```
    31|
    32|### 4. Installare Chromium per Playwright (solo prima volta)
    33|```bash
    34|python -m playwright install chromium
    35|```
    36|
    37|## Come usare
    38|
    39|### Primo avvio
    40|1. Apri PowerShell nella cartella del progetto
    41|2. Esegui:
    42|```bash
    43|.venv\Scripts\python.exe main.py
    44|```
    45|3. Il programma ti presenterà un menu. Scegli il gioco da risolvere.
    46|4. Quando si apre il browser su LinkedIn:
    47|   - Fai il login con il tuo account
    48|   - Premi INVIO sulla console
    49|5. Il programma navigherà al gioco scelto.
    50|6. Una volta risolto, il programma completerà il gioco automaticamente.
    51|
    52|### Avvii successivi
    53|- Sei già loggato da ieri, premi subito INVIO quando te lo chiede.
    54|- Il profilo browser ricorda la tua sessione.
    55|- Ogni volta che il puzzle si aggiorna (es. 24 ore), il solver lo risolverà automaticamente.
    56|
    57|## Output
    58|
    59|- **Console**: Messaggi di progresso e stato.
    60|- **solver.log**: Log dettagliato dei percorsi scartati (ZIP) e del processo di risoluzione (Sudoku).
    61|- **browser_profile/**: Profilo browser con sessione LinkedIn salvata.
    62|
    63|## Struttura del progetto
    64|
    65|```
    66|.
    67|├── main.py                 # Entry point principale, menu, e logica di alto livello
    68|├── requirements.txt        # Dipendenze Python
    69|├── README.md              # Questo file
    70|├── solver.log             # Log dettagliato degli algoritmi
    71|├── zip_solver/
    72|│   ├── __init__.py
    73|│   ├── bot.py            # Automazione click delle celle ZIP
    74|│   ├── cell.py           # Classe cella ZIP (numero, muri)
    75|│   ├── dom_reader.py     # Estrae griglia ZIP dal DOM di LinkedIn
    76|│   ├── grid.py           # Classe griglia ZIP
    77|│   └── solver.py         # DFS con backtracking + cutoff per ZIP
    78|└── sudoku_solver/
    79|    ├── __init__.py
    80|    ├── bot.py            # Automazione click delle celle Sudoku
    81|    ├── dom_reader.py     # Estrae griglia Sudoku dal DOM di LinkedIn
    82|    └── solver.py         # Algoritmo di backtracking per Sudoku
    83|```
    84|
    85|## Algoritmi
    86|
    87|### ZIP Solver
    88|Il solver usa **DFS ricorsivo con backtracking** per trovare il percorso:
    89|
    90|1. Parte dalla cella con numero 1.
    91|2. Visita le celle in ordine crescente dei numeri.
    92|3. Applica cutoff intelligenti (Manhattan distance, connettività).
    93|4. Se trova un vicolo cieco, backtrack e prova un'altra strada.
    94|5. Registra tutto nel log per debugging.
    95|
    96|### Sudoku Solver
    97|Il solver usa un algoritmo di **backtracking ricorsivo** per trovare la soluzione:
    98|
    99|1. Trova la prossima cella vuota.
   100|2. Per ogni numero da 1 a 6, controlla se è valido per quella cella (riga, colonna, sotto-griglia 3x2).
   101|3. Se il numero è valido, lo inserisce e richiama ricorsivamente il solver.
   102|4. Se la chiamata ricorsiva risolve la griglia, la soluzione viene propagata.
   103|5. Se il numero non porta a soluzione, fa backtracking (rimuove il numero e prova il successivo).
   104|
   105|## Troubleshooting
   106|
   107|**Errore: "playwright install chromium"**
   108|- Esegui il comando di installazione di Playwright (vedi sopra).
   109|
   110|**Errore: "timeout waiting for selector"**
   111|- LinkedIn potrebbe aver cambiato il layout.
   112|- Controlla il DOM del sito e aggiorna i selettori in `dom_reader.py` o `bot.py` del gioco corrispondente.
   113|
   114|**Il gioco non viene risolto (solver.log mostra 0 percorsi o `None` per Sudoku)**
   115|- Controlla `solver.log` per capire quale regola lo ha bloccato (ZIP) o dove il backtracking fallisce (Sudoku).
   116|- Potrebbe essere un puzzle particolarmente difficile o un errore nella logica `is_valid` (Sudoku).
   117|- Report il problema!
   118|
   119|**Vuoi resettare la sessione LinkedIn**
   120|- Elimina la cartella `browser_profile/`.
   121|- Al prossimo avvio, dovrai fare login di nuovo.
