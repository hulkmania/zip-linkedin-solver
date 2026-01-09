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

        # muri da classi trail-cell-wall--down, trail-cell-wall--right, trail-cell-wall--left, trail-cell-wall--up
        # Se LinkedIn ha cambiato sistema per i muri, queste query semplicemente non troveranno nulla
        # e la griglia verrà considerata senza muri (comunque risolvibile in molti casi).
        wall_bottom = div.query_selector('.trail-cell-wall--down')
        if wall_bottom:
            cell.walls.add('BOTTOM')

        wall_top = div.query_selector('.trail-cell-wall--up')
        if wall_top:
            cell.walls.add('TOP')

        wall_right = div.query_selector('.trail-cell-wall--right')
        if wall_right:
            cell.walls.add('RIGHT')

        wall_left = div.query_selector('.trail-cell-wall--left')
        if wall_left:
            cell.walls.add('LEFT')

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
