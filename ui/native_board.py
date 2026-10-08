"""Native-resolution board pass for Creator.

The rest of the interface stays on the virtual canvas for now. All board
rectangles and circles are rasterized on the physical display surface, with
the same virtual geometry and input hitboxes as Renderer.
"""
import pygame


def draw_native_board(window, viewport, renderer):
    game = renderer.game
    if game.game_over:
        # Keep the original victory overlay unobstructed.
        return
    scale = viewport.scale
    ox, oy = viewport.offset
    if scale <= 0:
        return

    def x(value):
        return round(ox + value * scale)

    def y(value):
        return round(oy + value * scale)

    def rect(left, top, right, bottom):
        return pygame.Rect(x(left), y(top), max(1, x(right)-x(left)),
                           max(1, y(bottom)-y(top)))

    def radius(value):
        return max(1, round(value * scale))

    size = game.board.size
    cell = renderer.CELL_SIZE
    bx, by = renderer.BOARD_X, renderer.BOARD_Y
    board_end_x, board_end_y = bx + size * cell, by + size * cell

    # Restrict native drawing to the board, not the neighboring control panel.
    original_clip = window.get_clip()
    clip = rect(bx - 7, by - 7, board_end_x + 7, board_end_y + 7)
    window.set_clip(clip)
    try:
        border = rect(bx-7, by-7, board_end_x+7, board_end_y+7)
        pygame.draw.rect(window, renderer.PANEL, border,
                         border_radius=radius(10))
        pygame.draw.rect(window, renderer.EDGE, border,
                         max(1, radius(2)), border_radius=radius(10))

        pattern = game.pattern
        offset = (size - pattern.size) // 2 if pattern.size else 0
        target = {(r + offset, c + offset)
                  for r in range(pattern.size)
                  for c in range(pattern.size)
                  if pattern.grid[r][c] == 1}

        for r in range(size):
            for c in range(size):
                left, top = bx + c * cell, by + r * cell
                square = rect(left, top, left + cell, top + cell)
                color = (22, 43, 61) if (r+c) % 2 == 0 else (18, 36, 53)
                pygame.draw.rect(window, color, square)
                pygame.draw.rect(window, (39, 65, 86), square, 1)
                if (r, c) in target:
                    pygame.draw.rect(window, (67, 92, 107), square,
                                     max(1, radius(2)))
                    center = (x(left + cell/2), y(top + cell/2))
                    marker = pygame.Rect(center[0] - radius(4),
                                         center[1] - radius(4),
                                         radius(8), radius(8))
                    pygame.draw.rect(window, (91, 127, 146), marker,
                                     border_radius=radius(2))

        try:
            valid_moves = game.get_valid_moves()
        except (AttributeError, ValueError):
            valid_moves = []
        for r, c in valid_moves:
            center = (x(bx + (c+.5)*cell), y(by + (r+.5)*cell))
            pygame.draw.circle(window, renderer.GREEN, center,
                               radius(9), max(1, radius(2)))
            pygame.draw.circle(window, renderer.GREEN, center, radius(3))

        selected = game.selected_pawn
        for r in range(size):
            for c in range(size):
                pawn = game.board.get_pawn(r, c)
                if pawn is None:
                    continue
                cx = x(bx + (c+.5)*cell)
                cy = y(by + (r+.5)*cell)
                team_color = renderer.BLUE if pawn.team == "BLUE" else renderer.RED
                pygame.draw.circle(window, (7, 15, 25),
                                   (cx + radius(2), cy + radius(3)), radius(19))
                pygame.draw.circle(window, team_color, (cx, cy), radius(17))
                pygame.draw.circle(window, (219, 238, 249),
                                   (cx-radius(4), cy-radius(5)),
                                   radius(5), max(1, radius(1)))
                if selected is pawn or (
                    selected is not None
                    and getattr(selected, "id", None) == getattr(pawn, "id", None)
                    and selected.team == pawn.team
                ):
                    pygame.draw.circle(window, renderer.GOLD, (cx, cy),
                                       radius(22), max(1, radius(3)))
    finally:
        window.set_clip(original_clip)
