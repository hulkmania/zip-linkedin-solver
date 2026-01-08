class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.number = None
        self.walls = set()  # TOP, RIGHT, BOTTOM, LEFT
