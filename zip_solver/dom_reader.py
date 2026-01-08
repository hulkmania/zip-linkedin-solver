from zip_solver.cell import Cell
from zip_solver.grid import Grid


def read_grid(frame):
    grid = Grid()

    # tutte le celle
    cell_divs = frame.query_selector_all('//div[@data-cell-idx]')
    idxs = [int(c.get_attribute("data-cell-idx")) for c in cell_divs]

    # numero colonne stimato dinamicamente
    cols = infer_columns(idxs)

    for div in cell_divs:
        idx = int(div.get_attribute("data-cell-idx"))
        r, c = idx // cols, idx % cols
        cell = Cell(r, c)
        
        
        # numero nella cella
        content = div.query_selector('.trail-cell-content')
        if content:
            txt = content.inner_text().strip()
            if txt.isdigit():
                cell.number = int(txt)

        # muri da classi trail-cell-wall--down, trail-cell-wall--right, trail-cell-wall--left, trail-cell-wall--up
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
