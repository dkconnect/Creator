from math import ceil

VICTORY_FRACTION = .75
TURN_LIMIT = 400

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
                cells.append((board_r if team == "BLUE" else game.board.size - 1 - board_r, c + offset))
    return cells

def progress(game, team):
    targets = target_cells(game, team)
    held = sum((p := game.board.get_pawn(r, c)) is not None and p.team == team for r, c in targets)
    return held, len(targets)

def required_count(game):
    return ceil(len(target_cells(game, "BLUE")) * VICTORY_FRACTION)

def check_victory(game, player):
    held, total = progress(game, player.team)
    return total > 0 and held >= ceil(total * VICTORY_FRACTION)

def endgame_result(game):
    blue, bt = progress(game, "BLUE")
    red, rt = progress(game, "RED")
    if not bt or not rt or blue * rt == red * bt:
        return None
    return game.blue if blue * rt > red * bt else game.red
