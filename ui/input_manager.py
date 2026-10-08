class InputManager:
    def __init__(self, renderer):
        self.renderer = renderer

    def get_clicked_cell(self, mouse_pos):
        x, y = mouse_pos

        board_x = self.renderer.BOARD_X
        board_y = self.renderer.BOARD_Y
        cell_size = self.renderer.CELL_SIZE
        board_size = self.renderer.game.board.size

        col = (x - board_x) // cell_size
        row = (y - board_y) // cell_size

        if 0 <= row < board_size and 0 <= col < board_size:
            return row, col

        return None