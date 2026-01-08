class Grid:
    def __init__(self):
        self.cells = {}
        self.numbers = {}
        self.total_cells = 0

    @property
    def all_cells(self):
        return set(self.cells.keys())
    
    def add_cell(self, cell):
        self.cells[(cell.r, cell.c)] = cell
        self.total_cells = len(self.cells)

        if cell.number is not None:
            self.numbers[cell.number] = (cell.r, cell.c)

    def normalize_walls(self):
        for (r, c), cell in self.cells.items():
            for w in list(cell.walls):
                if w == "LEFT" and (r, c - 1) in self.cells:
                    self.cells[(r, c - 1)].walls.add("RIGHT")
                if w == "RIGHT" and (r, c + 1) in self.cells:
                    self.cells[(r, c + 1)].walls.add("LEFT")
                if w == "TOP" and (r - 1, c) in self.cells:
                    self.cells[(r - 1, c)].walls.add("BOTTOM")
                if w == "BOTTOM" and (r + 1, c) in self.cells:
                    self.cells[(r + 1, c)].walls.add("TOP")

    def is_valid(self, r, c):
        return (r, c) in self.cells
    
    def can_move(self, r1, c1, r2, c2):
        if (r2, c2) not in self.cells:
            return False

        if r2 == r1 and c2 == c1 + 1:
            return "RIGHT" not in self.cells[(r1, c1)].walls
        if r2 == r1 and c2 == c1 - 1:
            return "LEFT" not in self.cells[(r1, c1)].walls
        if r2 == r1 + 1 and c2 == c1:
            return "BOTTOM" not in self.cells[(r1, c1)].walls
        if r2 == r1 - 1 and c2 == c1:
            return "TOP" not in self.cells[(r1, c1)].walls

        return False
