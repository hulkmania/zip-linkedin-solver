from playwright.sync_api import sync_playwright
from zip_solver.dom_reader import read_grid
from zip_solver.solver import solve
from zip_solver.bot import click_path
import requests
from bs4 import BeautifulSoup
import os


ZIP_URL = "https://www.linkedin.com/games/zip/"
BROWSER_PROFILE_DIR = "./browser_profile"  # Salva la sessione qui


def main():
    # Crea la directory del profilo se non esiste
    os.makedirs(BROWSER_PROFILE_DIR, exist_ok=True)
    
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
        
        # Ora vai al gioco ZIP
        print("🎮 Navigando al gioco ZIP...")
        page.goto(ZIP_URL)
        
        # Attendi che la pagina carichi
        print("⏳ Caricamento pagina del gioco...")
        input("👉 Osserva la pagina che si è aperta, poi premi INVIO per continuare...")

        frame = page.frame(url="https://www.linkedin.com/games/view/zip/desktop")
        
        # Prova a cliccare il pulsante di avvio se esiste (potrebbero averlo rimosso per utenti loggati)
        try:
            frame.wait_for_selector('#launch-footer-start-button', state="visible", timeout=30000)
            frame.click('#launch-footer-start-button')
            print("✓ Pulsante di avvio cliccato")
        except:
            print("ℹ️ Pulsante di avvio non trovato, potrebbe essere già in gioco...")

        # attende il contenitore principale del gioco
        print("⏳ Attendendo il caricamento della griglia...")
        frame.wait_for_selector('//div[@data-cell-idx]', state="visible", timeout=30000)

        grid, cols = read_grid(frame)
        path = solve(grid)
        
        if path is None:
            print("❌ Nessuna soluzione trovata! Il solver non è riuscito a risolvere il puzzle.")
            print("📋 Controlla il file 'solver.log' per i dettagli dei percorsi scartati.")
        else:
            print(f"✓ Soluzione trovata! Eseguo {len(path)} mosse...")
            click_path(frame, path, cols)
            print("✓ Puzzle completato!")

        browser.close()


if __name__ == "__main__":
    main()
