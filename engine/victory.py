def check_victory(game, player):
    pattern = game.pattern

    offset = (game.board.size - pattern.size) 

    for row in range(pattern.size):
        for col in range(pattern.size):

            if pattern.grid[row][col] == 0:
                continue

            board_row = row + offset
            board_col = col + offset

            pawn = game.board.get_pawn(board_row, board_col)

            if pawn is None:
                return False

            if pawn.team != player.team:
                return False

    return True
