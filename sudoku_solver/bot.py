from playwright.sync_api import Page, FrameLocator
import time

def click_sudoku_path(target: Page | FrameLocator, solved_grid, initial_grid, cols=6, delay=0.5):
    """
    Clicca automaticamente le celle del Sudoku per inserire la soluzione.
    """
    print("✏️ Inizio inserimento soluzione Sudoku...")
    for r in range(6):
        for c in range(6):
            if initial_grid[r][c] is None:  # Inserisce solo le celle che non erano pre-riempite
                idx = r * cols + c
                num_to_enter = solved_grid[r][c]
                
                if num_to_enter is None:
                    print(f"⚠️ Salto cella ({r},{c}) perché il numero risolto è None.")
                    continue # Salta se per qualche motivo non c'è un numero risolto

                cell_selector = f"//div[@data-cell-idx='{idx}']"
                num_selector = f"//button[@data-number='{num_to_enter}']"

                print(f"Attempting to set cell ({r},{c}) with number {num_to_enter}...")
                try:
                    # Clicca la cella per attivarla
                    target.click(cell_selector, timeout=10000) # Aumenta il timeout
                    # Clicca il numero sul keypad virtuale
                    target.click(num_selector, timeout=10000) # Aumenta il timeout
                    print(f"✓ Inserito {num_to_enter} nella cella ({r},{c})")
                except Exception as e:
                    print(f"❌ Errore nell'inserire {num_to_enter} nella cella ({r},{c}) (Tentativo 1): {e}")
                    # Prova con force click se il click normale fallisce
                    try:
                        target.locator(cell_selector).click(force=True, timeout=10000)
                        target.locator(num_selector).click(force=True, timeout=10000)
                        print(f"✓ Inserito {num_to_enter} nella cella ({r},{c}) con force click")
                    except Exception as e2:
                        print(f"❌ Anche force click fallito su cella ({r},{c}) per numero {num_to_enter} (Tentativo 2): {e2}")
                        continue
                
                time.sleep(delay)
    print("✅ Inserimento soluzione Sudoku completato.")