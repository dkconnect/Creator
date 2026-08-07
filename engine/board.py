class Board:
    def __init__(self, size: int = 16):
        self.size = size
        self.grid = [
            [None for _ in range(size)]
            for _ in range(size)
        ]

    def place_pawn(self, pawn):
        self.grid[pawn.row][pawn.col] = pawn

    def get_pawn(self, row, col):
        return self.grid[row][col]
