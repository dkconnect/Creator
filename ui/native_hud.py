"""Physical-pixel Creator match HUD.

Draws the main match rail directly on the display after the virtual-canvas
pass. Leaves the multiplayer history area and victory overlays untouched.
No input hitboxes, game state, or network behavior are changed.
"""
from functools import lru_cache
import pygame


@lru_cache(maxsize=128)
def _font(size, bold):
    return pygame.font.SysFont("arial", size, bold=bold)


def draw_native_hud(window, viewport, renderer):
    game = renderer.game
    if game.game_over:
        return  # Preserve both existing result overlays.

    scale = viewport.scale
    if scale <= 0:
        return
    ox, oy = viewport.offset

    def X(value):
        return round(ox + value * scale)

    def Y(value):
        return round(oy + value * scale)

    def S(value):
        return max(1, round(value * scale))

    def R(x, y, w, h):
        return pygame.Rect(X(x), Y(y), max(1, S(w)), max(1, S(h)))

    def label(message, x, y, size=17, color=None, bold=False, center=None):
        font = _font(max(9, round(size * scale)), bold)
        surface = font.render(str(message), True, color or renderer.TEXT)
        dest = surface.get_rect(center=(X(center[0]), Y(center[1]))) if center else (X(x), Y(y))
        window.blit(surface, dest)

    def panel(x, y, w, h, radius=12):
        rect = R(x, y, w, h)
        pygame.draw.rect(window, renderer.PANEL, rect, border_radius=S(radius))
        pygame.draw.rect(window, renderer.EDGE, rect, max(1, S(1)),
                         border_radius=S(radius))

    # Redraw all typography on the title bar, avoiding scaled-font ghosts.
    pygame.draw.rect(window, renderer.BG, R(23, 13, 792, 57))
    label("CREATOR   /   TACTICAL BOARD", 33, 31, 23, bold=True)
    label("COMPLETE THE PATTERN TO WIN", 470, 38, 14,
          renderer.MUTED, True)

    panel(829, 86, 355, 344, 14)
    label("MATCH CONTROL", 850, 106, 14, renderer.MUTED, True)
    current = getattr(game.current_player, "team", "—")
    current_color = renderer.BLUE if current == "BLUE" else renderer.RED
    label(f"{current} TO PLAY", 850, 130, 32, current_color, True)
    pygame.draw.line(window, renderer.EDGE,
                     (X(849), Y(182)), (X(1162), Y(182)), S(1))

    label("DICE RESULT", 862, 199, 14, renderer.MUTED, True)
    dice = game.dice.value
    label("—" if dice is None else str(dice), 862, 223,
          23, renderer.GOLD, True)
    label("VICTORY PATTERN", 862, 267, 14, renderer.MUTED, True)
    label(str(game.pattern.name or "—"), 862, 291, 23, bold=True)

    button = renderer.dice_button
    hover = button.collidepoint(viewport.mouse_pos())
    rect = R(button.x, button.y, button.width, button.height)
    pygame.draw.rect(window,
                     (49, 125, 182) if hover else (38, 100, 153),
                     rect, border_radius=S(10))
    pygame.draw.rect(window, renderer.BLUE, rect, S(2),
                     border_radius=S(10))
    label("ROLL DICE", 0, 0, 23, bold=True, center=button.center)

    panel(829, 442, 355, 109)
    label("PAWN LOSSES", 849, 458, 14, renderer.MUTED, True)
    label(f"BLUE   {getattr(game.blue, 'respawns', 0)}",
          849, 491, 23, renderer.BLUE, True)
    label(f"RED   {getattr(game.red, 'respawns', 0)}",
          1010, 491, 23, renderer.RED, True)

    # Repaint the footer line, which would otherwise remain scaled.
    pygame.draw.rect(window, renderer.BG, R(824, 851, 376, 35))
    label("SELECT A PAWN  /  CHOOSE A HIGHLIGHTED SQUARE",
          830, 864, 14, renderer.MUTED, True)
