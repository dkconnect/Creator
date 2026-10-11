VICTORY_FRACTION = 1.0
TURN_LIMIT = None  # Kept for compatibility; no automatic match cutoff.

def target_cells(game, team):
    if team not in ("BLUE", "RED"):
        raise ValueError("Unknown team")

    pattern = game.pattern
    offset = (game.board.size - pattern.size) // 2

    cells = []

    for r, row in enumerate(pattern.grid):
        for c, active in enumerate(row):
            if active == 1:
                board_r = r + offset
                board_c = c + offset

                if team == "RED":
                    target_row = game.board.size - 1 - board_r
                else:
                    target_row = board_r

                cells.append((target_row, board_c))

    return cells

def progress(game, team):
    targets = target_cells(game, team)
    held = sum((pawn := game.board.get_pawn(r, c)) is not None and pawn.team == team
               for r, c in targets)
    return held, len(targets)


def required_count(game):
    return len(target_cells(game, "BLUE"))


def check_victory(game, player):
    held, total = progress(game, player.team)
    return total > 0 and held == total


def endgame_result(game):
    """No occupancy-based winner in classic mode."""
    return None
