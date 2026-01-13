import logging
from collections import deque

# Configura logging
logger = logging.getLogger("solver")
logger.setLevel(logging.DEBUG)

# Crea handler solo se non esiste già
if not logger.handlers:
    handler = logging.FileHandler("solver.log", encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

_path_counter = 0


def visualize_grid(grid):
    """
    Crea una rappresentazione ASCII della griglia con numeri e muri.
    """
    if not grid.cells:
        return "Griglia vuota"

    # Trova dimensioni
    max_r = max(r for r, c in grid.cells.keys())
    max_c = max(c for r, c in grid.cells.keys())

    lines = []
    for r in range(max_r + 1):
        line = ""
        for c in range(max_c + 1):
            if (r, c) in grid.cells:
                cell = grid.cells[(r, c)]
                if cell.number is not None:
                    line += f"[{cell.number:2d}]"
                else:
                    line += "[ .]"
            else:
                line += "    "
            
            # Aggiungi muro a destra
            if c < max_c:
                if (r, c) in grid.cells and "RIGHT" in grid.cells[(r, c)].walls:
                    line += "|"
                else:
                    line += " "
        
        lines.append(line)
        
        # Aggiungi linea di muri inferiori
        if r < max_r:
            wall_line = ""
            for c in range(max_c + 1):
                if (r, c) in grid.cells and "BOTTOM" in grid.cells[(r, c)].walls:
                    wall_line += "----"
                else:
                    wall_line += "    "
                wall_line += " "
            lines.append(wall_line)

    return "\n".join(lines)


def is_connected(grid, visited):
    """
    Controlla se le celle non visitate rimangono connesse tra loro.
    Se si dividono in isole separate, è impossibile visitarle tutte.
    """
    unvisited = grid.all_cells - visited
    if len(unvisited) <= 1:
        return True

    start = next(iter(unvisited))
    visited_unvisited = {start}
    queue = deque([start])

    while queue:
        r, c = queue.popleft()
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) in unvisited and (nr, nc) not in visited_unvisited:
                if grid.can_move(r, c, nr, nc):
                    visited_unvisited.add((nr, nc))
                    queue.append((nr, nc))

    return len(visited_unvisited) == len(unvisited)


def should_cutoff(grid, visited, current_pos, next_num_pos):
    """
    Controlla se il percorso attuale può essere abbandonato.
    Usa: Manhattan distance, celle isolate, e connettività.
    """
    r1, c1 = current_pos
    r2, c2 = next_num_pos
    manhattan_distance = abs(r1 - r2) + abs(c1 - c2)

    remaining_cells = grid.total_cells - len(visited)
    if manhattan_distance > remaining_cells:
        return True

    # Controlla se le celle non visitate rimangono connesse
    if not is_connected(grid, visited):
        return True

    return False


def dfs(grid, current_cell, path, visited, next_num, depth=0):
    """
    DFS ricorsivo per ZIP con backtracking e cutoff.
    """
    global _path_counter

    # caso base: tutti i numeri visitati in ordine E tutte le celle visitate
    if next_num - 1 == max(grid.numbers):
        logger.info(f"DEBUG: Raggiunto ultimo numero {max(grid.numbers)}, visited={len(visited)}/{grid.total_cells}")
        if len(visited) == grid.total_cells:
            solution_path = path + [current_cell]
            logger.info(f"SOLUZIONE COMPLETA TROVATA! Percorso finale: {solution_path}")
            logger.info(f"SUCCESSO: Tutti i numeri (1-{max(grid.numbers)}) e tutte le celle ({grid.total_cells}/{grid.total_cells}) visitate.")
            return solution_path
        else:
            logger.info(f"DEBUG: Ultimo numero raggiunto ma non tutte le celle visitate ({len(visited)}/{grid.total_cells})")
            return None

    r, c = current_cell
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        next_cell = (nr, nc)

        if next_cell in visited:
            continue
        if not grid.can_move(r, c, nr, nc):
            continue

        # aggiornamento numero successivo se raggiungo il numero corretto
        new_next_num = next_num
        if next_num in grid.numbers:
            if next_cell == grid.numbers[next_num]:
                new_next_num += 1
            elif next_cell in grid.numbers.values():
                continue  # salto numero sbagliato

        new_visited = visited | {next_cell}

        # cutoff Manhattan
        if new_next_num in grid.numbers:
            tr, tc = grid.numbers[new_next_num]
            dist = abs(tr - nr) + abs(tc - nc)
            remaining = grid.total_cells - len(new_visited)
            if dist > remaining:
                continue

        # cutoff regioni isolate e connettività
        if should_cutoff(grid, new_visited, next_cell, grid.numbers.get(new_next_num, next_cell)):
            _path_counter += 1
            visited_order = (path + [current_cell]) if path else [current_cell]
            logger.debug(
                f"[Percorso #{_path_counter} scartato] Ordine visita: {visited_order + [next_cell]}, "
                f"Totale: {len(new_visited)}/{grid.total_cells}, "
                f"Prossimo numero: {new_next_num}"
            )
            continue

        result = dfs(
            grid,
            next_cell,
            path + [current_cell],
            new_visited,
            new_next_num,
            depth + 1
        )
        if result:
            return result

    return None


def solve(grid):
    """
    Funzione principale per risolvere ZIP.
    """
    logger.info("="*80)
    logger.info("INIZIO RISOLUZIONE")
    logger.info(f"Griglia: {grid.total_cells} celle, numeri: {sorted(grid.numbers.keys())}")
    logger.info(f"Numero massimo presente: {max(grid.numbers) if grid.numbers else 'N/A'}")
    logger.info(f"Numeri consecutivi da 1 a {max(grid.numbers) if grid.numbers else 'N/A'}: {list(range(1, max(grid.numbers)+1)) if grid.numbers else 'N/A'}")
    logger.info("="*80)
    logger.info("\nRappresentazione griglia:")
    logger.info("\n" + visualize_grid(grid))
    logger.info("="*80 + "\n")

    global _path_counter
    _path_counter = 0

    start = grid.numbers[1]
    result = dfs(
        grid,
        current_cell=start,
        path=[],
        visited={start},
        next_num=2
    )

    if result:
        # Evita simboli Unicode (✓, ✗) che possono dare problemi su alcune console Windows
        logger.info(f"SOLUZIONE TROVATA! Percorsi testati: {_path_counter}")
    else:
        logger.info(f"NESSUNA SOLUZIONE TROVATA. Percorsi scartati: {_path_counter}")

    logger.info("="*80)
    return result
