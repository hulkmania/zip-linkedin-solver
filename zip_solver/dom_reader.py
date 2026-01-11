from zip_solver.cell import Cell
from zip_solver.grid import Grid


def read_grid(page_or_frame):
    grid = Grid()

    # tutte le celle (sia da Frame che da Page, a seconda di dove vive la griglia)
    cell_divs = page_or_frame.query_selector_all('//div[@data-cell-idx]')
    idxs = [int(c.get_attribute("data-cell-idx")) for c in cell_divs]

    # numero colonne stimato dinamicamente
    cols = infer_columns(idxs)

    for div in cell_divs:
        idx = int(div.get_attribute("data-cell-idx"))
        r, c = idx // cols, idx % cols
        cell = Cell(r, c)
        
        # numero nella cella
        # Versione vecchia: contenuto in .trail-cell-content
        content = div.query_selector('.trail-cell-content')
        # Versione nuova di LinkedIn ZIP: div con data-cell-content="true"
        if not content:
            content = div.query_selector('[data-cell-content="true"]')

        if content:
            txt = content.inner_text().strip()
            if txt.isdigit():
                cell.number = int(txt)

        # NUOVO SISTEMA LinkedIn ZIP: muri rappresentati da classi con ::after border-width: 12px
        # Cerchiamo tutte le classi note e anche dinamicamente quelle con border-width negli stili

        # Classi note identificate:
        # _2dafef0f -> RIGHT (border-right-width: 12px)
        # ed9cc1f4 -> LEFT (border-left-width: 12px)

        wall_right = div.query_selector('._2dafef0f')
        if wall_right:
            cell.walls.add('RIGHT')

        wall_left = div.query_selector('.ed9cc1f4')
        if wall_left:
            cell.walls.add('LEFT')

        # Per TOP e BOTTOM, cerchiamo dinamicamente classi con ::after border-top/bottom-width: 12px
        # Eseguiamo JavaScript per controllare tutti gli elementi della cella
        wall_check_script = """
        (cellDiv) => {
            const results = { top: false, bottom: false };

            // Cerca tutti gli elementi nella cella
            const elements = cellDiv.querySelectorAll('*');

            for (const el of elements) {
                const computedStyle = window.getComputedStyle(el, '::after');
                const borderTop = computedStyle.getPropertyValue('border-top-width');
                const borderBottom = computedStyle.getPropertyValue('border-bottom-width');

                if (borderTop === '12px') results.top = true;
                if (borderBottom === '12px') results.bottom = true;

                if (results.top && results.bottom) break;
            }

            return results;
        }
        """

        try:
            wall_results = div.evaluate(wall_check_script)
            if wall_results['top']:
                cell.walls.add('TOP')
            if wall_results['bottom']:
                cell.walls.add('BOTTOM')
        except Exception as e:
            # Se fallisce lo script JS, procediamo senza muri TOP/BOTTOM (fallback sicuro)
            print(f"⚠️ Impossibile verificare muri TOP/BOTTOM per cella {idx}: {e}")

        grid.add_cell(cell)

    # normalizzazione muri
    grid.normalize_walls()
    return grid, cols


def infer_columns(idxs):
    """
    Deduce il numero di colonne dalla sequenza di data-cell-idx.
    """
    idxs = sorted(idxs)
    for i in range(1, len(idxs)):
        diff = idxs[i] - idxs[i - 1]
        if diff > 1:
            return diff
    return int(len(idxs) ** 0.5)
