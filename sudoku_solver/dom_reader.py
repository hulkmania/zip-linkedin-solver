from playwright.sync_api import Page, FrameLocator

def read_sudoku_grid(target: Page | FrameLocator):
    """
    Legge la griglia del Sudoku 6x6 dal DOM di LinkedIn.
    Restituisce una griglia 6x6 con None per le celle vuote e numeri 1-6 per quelle riempite.
    """
    grid = [[None for _ in range(6)] for _ in range(6)]

    cells = target.query_selector_all('//div[@data-cell-idx]')

    for cell in cells:
        try:
            idx = int(cell.get_attribute('data-cell-idx'))
            if 0 <= idx < 36:  # Sudoku 6x6 ha 36 celle
                row = idx // 6
                col = idx % 6

                # Controlla se la cella è pre-riempita o vuota
                content_div = cell.query_selector('.sudoku-cell-content')
                if content_div:
                    text = content_div.text_content().strip()
                    if text and text.isdigit() and 1 <= int(text) <= 6:
                        grid[row][col] = int(text)
                    else:
                        grid[row][col] = None
        except Exception as e:
            print(f"⚠️ Errore nella lettura della cella con idx {cell.get_attribute('data-cell-idx')}: {e}")
            continue

    return grid