def find_empty(grid):
    """
    Trova la prossima cella vuota nella griglia del Sudoku.
    Restituisce (riga, colonna) della cella vuota o None se la griglia è piena.
    """
    for r in range(6):
        for c in range(6):
            if grid[r][c] is None:
                return (r, c)
    return None

def is_valid(grid, num, pos):
    """
    Controlla se posizionare 'num' nella 'pos' (riga, colonna) è valido.
    """
    row, col = pos

    # Controlla riga
    for c in range(6):
        if grid[row][c] == num and col != c:
            return False

    # Controlla colonna
    for r in range(6):
        if grid[r][col] == num and row != r:
            return False

    # Controlla sotto-griglia 3x2 (box)
    box_x = col // 3  # Indice della sotto-griglia per la colonna
    box_y = row // 2  # Indice della sotto-griglia per la riga

    for r_offset in range(2):
        for c_offset in range(3):
            check_row = box_y * 2 + r_offset
            check_col = box_x * 3 + c_offset
            if grid[check_row][check_col] == num and (check_row, check_col) != pos:
                return False
    return True

def solve_sudoku(grid):
    """
    Risolve un Sudoku 6x6 usando il backtracking.
    Restituisce la griglia risolta o None se non c'è soluzione.
    """
    # Lavora su una copia della griglia per non modificare l'originale
    solved_grid_copy = [row[:] for row in grid] # Crea una copia superficiale di righe, ma profonda degli elementi

    find = find_empty(solved_grid_copy)
    if not find:
        print("DEBUG: Griglia completamente risolta.")
        return solved_grid_copy  # Griglia risolta
    else:
        row, col = find
        print(f"DEBUG: Trovata cella vuota in ({row},{col})")

    for num in range(1, 7):  # Numeri da 1 a 6
        print(f"DEBUG: Tentativo {num} per cella ({row},{col})")
        if is_valid(solved_grid_copy, num, (row, col)):
            print(f"DEBUG: {num} è valido per ({row},{col})")
            solved_grid_copy[row][col] = num

            result = solve_sudoku(solved_grid_copy)
            if result:
                return result # PASSALA SU! Non la solved_grid_copy di questo livello.

            print(f"DEBUG: Backtrack da ({row},{col}) con numero {num}")
            solved_grid_copy[row][col] = None  # Backtrack

    print(f"DEBUG: Nessuna soluzione trovata da ({row},{col}). Ritorno None.")
    return None