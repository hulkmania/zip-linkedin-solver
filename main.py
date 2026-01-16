from playwright.sync_api import sync_playwright
from zip_solver.dom_reader import read_grid
from zip_solver.solver import solve
from zip_solver.bot import click_path

# Importa i moduli per il Sudoku
from sudoku_solver.dom_reader import read_sudoku_grid
from sudoku_solver.solver import solve_sudoku
from sudoku_solver.bot import click_sudoku_path
import os
import time


ZIP_URL = "https://www.linkedin.com/games/zip/"
SUDOKU_URL = "https://www.linkedin.com/games/mini-sudoku/"
BROWSER_PROFILE_DIR = "./browser_profile"  # Salva la sessione qui


def show_menu():
    """Mostra il menu interattivo per scegliere il gioco"""
    print("\n" + "="*50)
    print("🎮 LINKEDIN GAMES SOLVER")
    print("="*50)
    print("1. 🔗 ZIP - Gioco del percorso")
    print("2. 🔢 SUDOKU - Gioco dei numeri")
    print("3. ❌ Esci")
    print("="*50)

    while True:
        try:
            choice = input("Scegli un'opzione (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return choice
            else:
                print("❌ Opzione non valida. Scegli 1, 2 o 3.")
        except KeyboardInterrupt:
            print("\n👋 Arrivederci!")
            return '3'


def ask_close_confirmation(game_name=""):
    """Chiede conferma prima di chiudere il browser"""
    print(f"\n{'='*50}")
    print("✅ PUZZLE COMPLETATO!")
    print(f"{'='*50}")
    print(f"🎉 Il {game_name} è stato risolto con successo!")
    print("📱 Il browser rimarrà aperto per permetterti di verificare la soluzione.")
    print(f"{'='*50}")

    while True:
        try:
            response = input("🔐 Vuoi chiudere il browser ora? (s/n): ").strip().lower()
            if response in ['s', 'si', 'sì', 'y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("❌ Rispondi 's' (sì) o 'n' (no).")
        except KeyboardInterrupt:
            print("\n👋 Chiudendo il browser...")
            return True


def main():
    # Crea la directory del profilo se non esiste
    os.makedirs(BROWSER_PROFILE_DIR, exist_ok=True)

    # Menu interattivo
    choice = show_menu()

    if choice == '3':
        print("👋 Arrivederci!")
        return

    # Determina l'URL del gioco scelto
    game_url = ""
    game_name = ""
    game_emoji = ""
    if choice == '1':
        game_url = ZIP_URL
        game_name = "ZIP"
        game_emoji = "🔗"
    elif choice == '2':
        game_url = SUDOKU_URL
        game_name = "SUDOKU"
        game_emoji = "🔢"
    
    with sync_playwright() as p:
        # Usa un profilo persistente - primo avvio salva i cookies, avvii successivi li ricarica
        # Aggiungi parametri per nascondere che è un browser automatizzato
        browser = p.chromium.launch_persistent_context(
            BROWSER_PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],  # Nasconde che è automatizzato
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"  # User agent realistico
        )
        page = browser.new_page()
        
        # Naviga a LinkedIn.com prima - se non loggato, chiede il login
        print("📱 Navigando a LinkedIn...")
        page.goto("https://www.linkedin.com/")
        page.wait_for_load_state("domcontentloaded")
        
        # Attendi che l'utente faccia il login
        input("👉 Fai il login a LinkedIn, poi premi INVIO per continuare...")
        
        print(f"{game_emoji} Navigando al gioco {game_name}...")
        page.goto(game_url)
        page.wait_for_load_state("domcontentloaded")

        # Alcune versioni del gioco usavano un iframe dedicato, ora la griglia è spesso
        # direttamente nella pagina principale.
        # Per ZIP, proviamo prima a prendere il frame, altrimenti ripieghiamo sulla pagina.
        # Per Sudoku, interagiamo direttamente con la pagina.
        target = page # Default a page per tutti i giochi

        # Logica specifica per il gioco scelto
        if choice == '1': # ZIP
            # Per ZIP, tenta di trovare un frame specifico
            frame = page.frame(url="https://www.linkedin.com/games/view/zip/desktop")
            target = frame or page

            # attende il contenitore principale del gioco
            target.wait_for_selector('//div[@data-cell-idx]', state="visible", timeout=30000)

            # Leggi la griglia PRIMA di chiudere la pagina
            print("📊 Leggendo la griglia del puzzle...")
            grid, cols = read_grid(target)
            print("✓ Griglia letta con successo")

            # Chiudi la pagina del gioco per fermare il timer
            print("🔄 Chiudendo la pagina del gioco per fermare il timer...")
            current_game_url = page.url  # Salva l'URL del gioco
            page.close()
            print("✓ Pagina del gioco chiusa - timer fermato!")

            path = solve(grid)

            if path is None:
                print("❌ Nessuna soluzione trovata! Il solver non è riuscito a risolvere il puzzle.")
                print("📋 Controlla il file 'solver.log' per i dettagli dei percorsi scartati.")
                browser.close()
                return

            # Riapri LinkedIn e il gioco per completare il puzzle
            print("🔄 Riaprendo LinkedIn e il gioco per completare il puzzle...")
            page = browser.new_page()
            page.goto("https://www.linkedin.com/")
            page.wait_for_load_state("domcontentloaded")

            # Attendi che l'utente faccia il login se necessario
            input("👉 Se devi fare login a LinkedIn, falla ora. Premi INVIO quando sei pronto...")

            # Vai al gioco ZIP
            print("🎮 Navigando al gioco ZIP...")
            page.goto(current_game_url)
            
            page.wait_for_load_state("domcontentloaded")

            # Attendi che la pagina carichi completamente e sia stabile
            print("⏳ Caricamento pagina del gioco...")
            frame = page.frame(url="https://www.linkedin.com/games/view/zip/desktop")
            target = frame or page

            # Aspetta che la griglia sia visibile e stabile
            target.wait_for_load_state("domcontentloaded")

            # Aspetta un po' per assicurarsi che tutto sia stabile
            time.sleep(2)

            print("✓ Pagina del gioco pronta - completando il puzzle")

            print(f"✓ Soluzione trovata! Eseguo {len(path)} mosse...")
            try:
                click_path(target, path, cols)
                print("✓ Puzzle completato!")
            except Exception as e:
                print(f"❌ Errore durante il completamento del puzzle: {e}")
                print("💡 Possibili cause:")
                print("   - La pagina si è chiusa o ricaricata")
                print("   - Elementi del gioco che bloccano i click")
                print("   - LinkedIn ha cambiato l'interfaccia")

            # Chiedi conferma prima di chiudere il browser
            if ask_close_confirmation("ZIP"):
                browser.close()
            else:
                print("📱 Browser lasciato aperto per la verifica. Chiudilo manualmente quando vuoi.")
                input("👉 Premi INVIO per continuare...")
                browser.close()

        elif choice == '2': # SUDOKU
            # Per Sudoku, interagiamo direttamente con la pagina principale
            target = page
            
            # Aspetta che la griglia del Sudoku sia visibile
            target.wait_for_selector('//div[@data-cell-idx]', state="visible", timeout=30000)

            print("📊 Leggendo la griglia del Sudoku...")
            initial_grid = read_sudoku_grid(target)
            print("✓ Griglia Sudoku letta con successo")
            
            # Chiudi la pagina del gioco per fermare il timer
            print("🔄 Chiudendo la pagina del gioco per fermare il timer...")
            current_game_url = page.url  # Salva l'URL del gioco
            page.close()
            print("✓ Pagina del gioco chiusa - timer fermato!")

            print("🧠 Risolvendo il Sudoku...")
            solved_grid = solve_sudoku(initial_grid)

            if solved_grid is None:
                print("❌ Nessuna soluzione trovata per il Sudoku!")
                browser.close()
                return
            
            print("✓ Sudoku risolto!")

            # Riapri LinkedIn e il gioco per completare il puzzle
            print("🔄 Riaprendo LinkedIn e il gioco per completare il puzzle...")
            page = browser.new_page()
            page.goto("https://www.linkedin.com/")
            page.wait_for_load_state("domcontentloaded")

            input("👉 Se devi fare login a LinkedIn, falla ora. Premi INVIO quando sei pronto...")

            print("🎮 Navigando al gioco SUDOKU...")
            page.goto(current_game_url)
            page.wait_for_load_state("domcontentloaded")

            print("⏳ Caricamento pagina del gioco...")
            target = page # Per Sudoku, interagiamo direttamente con la pagina principale
            target.wait_for_selector('//div[@data-cell-idx]', state="visible", timeout=30000)
            
            #time.sleep(2) # Attendi per stabilità
            print("✓ Pagina del gioco pronta - completando il puzzle")
            
            print("✏️ Inserendo la soluzione nel Sudoku...")
            try:
                # Per il Sudoku 6x6, le colonne sono fisse a 6
                click_sudoku_path(target, solved_grid, initial_grid, cols=6)
                print("✓ Sudoku completato!")
            except Exception as e:
                print(f"❌ Errore durante il completamento del Sudoku: {e}")
                print("💡 Possibili cause:")
                print("   - La pagina si è chiusa o ricaricata")
                print("   - Elementi del gioco che bloccano i click")
                print("   - LinkedIn ha cambiato l'interfaccia")

            # Chiedi conferma prima di chiudere il browser
            if ask_close_confirmation("Sudoku"):
                browser.close()
            else:
                print("📱 Browser lasciato aperto per la verifica. Chiudilo manualmente quando vuoi.")
                input("👉 Premi INVIO per continuare...")
                browser.close()


if __name__ == "__main__":
    main()