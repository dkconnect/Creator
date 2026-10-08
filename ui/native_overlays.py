"""DPI-aware Creator multiplayer HUD and result panels.

Draw directly on the physical display. Coordinates match the 1200x900
virtual input rectangles; no changes to the network protocol or game rules.
"""
from functools import lru_cache
import pygame

BG = (8, 16, 26)
PANEL = (20, 33, 49)
PANEL2 = (26, 45, 64)
EDGE = (48, 78, 103)
WHITE = (236, 245, 253)
MUTED = (149, 175, 196)
BLUE = (82, 166, 245)
RED = (225, 93, 112)
GREEN = (90, 205, 158)
GOLD = (242, 194, 105)


@lru_cache(maxsize=128)
def font(size, bold=False):
    return pygame.font.SysFont("arial", size, bold=bold)


class Painter:
    def __init__(self, surface, viewport):
        self.surface = surface
        self.scale = viewport.scale
        self.ox, self.oy = viewport.offset
        self.mouse = viewport.mouse_pos()

    def x(self, value):
        return round(self.ox + value * self.scale)

    def y(self, value):
        return round(self.oy + value * self.scale)

    def s(self, value):
        return max(1, round(value * self.scale))

    def rect(self, x, y, w, h):
        return pygame.Rect(self.x(x), self.y(y), self.s(w), self.s(h))

    def box(self, x, y, w, h, color=PANEL, border=EDGE, radius=12):
        r = self.rect(x, y, w, h)
        pygame.draw.rect(self.surface, color, r, border_radius=self.s(radius))
        if border:
            pygame.draw.rect(self.surface, border, r, self.s(1),
                             border_radius=self.s(radius))
        return r

    def text(self, value, x, y, size=17, color=WHITE, bold=False, center=False,
             right=False, max_width=None):
        text = str(value)
        f = font(max(9, round(size * self.scale)), bold)
        if max_width is not None:
            while len(text) > 3 and f.size(text)[0] > self.s(max_width):
                text = text[:-2].rstrip('…') + '…'
        img = f.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = (self.x(x), self.y(y))
        elif right:
            rect.topright = (self.x(x), self.y(y))
        else:
            rect.topleft = (self.x(x), self.y(y))
        self.surface.blit(img, rect)

    def button(self, virtual_rect, label, primary=False, disabled=False):
        x, y, w, h = virtual_rect
        hover = pygame.Rect(x, y, w, h).collidepoint(self.mouse) and not disabled
        fill = (38, 100, 153) if primary else PANEL2
        if disabled:
            fill = (48, 60, 72)
        elif hover:
            fill = tuple(min(255, c + 19) for c in fill)
        self.box(x, y, w, h, fill, BLUE if hover else EDGE, 11)
        self.text(label, x+w/2, y+h/2, 20, MUTED if disabled else WHITE,
                  True, center=True)


def draw_multiplayer_hud(surface, viewport, multiplayer, game, sync):
    """Room status, phase, activity feed and last ten history entries."""
    p = Painter(surface, viewport)
    status = multiplayer.room_status or {}
    team = multiplayer.team or "UNKNOWN"
    current = getattr(game.current_player, "team", "UNKNOWN")
    paused = bool(status.get("paused"))
    connected = bool(getattr(sync, "connected", False))
    turn = current == team and not paused
    phase = getattr(multiplayer.game_state, "turn_phase", "")
    phase_names = {
        "WAITING_FOR_ROLL": "Roll the dice",
        "WAITING_FOR_SELECTION": "Select a pawn",
        "WAITING_FOR_MOVE": "Choose a destination",
    }
    phase_text = ("Waiting for reconnection" if paused else
                  "Waiting for opponent" if not turn else
                  phase_names.get(phase, phase.replace("_", " ").title()))
    # The gameplay HUD already owns the right rail. Use its top slot for
    # room-specific information without covering the board.
    p.box(829, 10, 355, 65)
    p.text("YOU: " + team, 841, 15, 18, BLUE if team == "BLUE" else RED, True)
    p.text("ROOM " + str(multiplayer.room_code or "------"),
           841, 42, 14, MUTED)
    p.text("YOUR TURN" if turn else current + "'S TURN",
           977, 15, 18, GREEN if turn else MUTED, True, max_width=188)
    p.text(phase_text, 977, 42, 14, MUTED, max_width=196)
    state_label = "PAUSED" if paused else "LIVE" if connected else "OFFLINE"
    p.text(state_label, 1170, 82, 13, GREEN if connected and not paused else GOLD,
           True, right=True)

    event = status.get("last_event") or {}
    if event:
        if event.get("type") == "ROLL":
            detail = f"{event.get('team')} rolled {event.get('value')}"
        elif event.get("type") == "MOVE":
            detail = (f"{event.get('team')} pawn {event.get('pawn_id')} "
                      f"to ({event.get('row')}, {event.get('col')})")
            if event.get("captures", 0):
                detail += "  /  CAPTURE"
        else:
            detail = ""
        if detail:
            p.box(33, 53, 760, 27, PANEL2, None, 6)
            p.text(detail, 46, 58, 14, GOLD, max_width=728)

    history = status.get("move_history") or []
    if history:
        visible = history[-10:]
        p.box(829, 567, 355, min(290, 46 + len(visible) * 23))
        p.text("MATCH HISTORY", 841, 578, 14, WHITE, True)
        for i, entry in enumerate(reversed(visible)):
            kind = entry.get("type")
            if kind == "ROLL":
                line = f"#{entry.get('id')}  {entry.get('team')} rolled {entry.get('value')}"
            elif kind == "MOVE":
                line = (f"#{entry.get('id')}  {entry.get('team')} pawn "
                        f"{entry.get('pawn_id')} -> ({entry.get('row')},{entry.get('col')})")
                if entry.get("captures", 0):
                    line += "  CAPTURE"
            else:
                continue
            p.text(line, 841, 608 + i*23, 14,
                   GOLD if entry.get("captures", 0) else MUTED,
                   max_width=329)


def draw_match_result(surface, viewport, game, renderer, multiplayer=None):
    """Native text and panels, preserving the existing virtual click rectangles."""
    p = Painter(surface, viewport)
    winner = getattr(getattr(game, "winner", None), "team", None)
    accent = BLUE if winner == "BLUE" else RED if winner == "RED" else GOLD
    p.box(263, 175, 674, 500, PANEL, EDGE, 22)
    pygame.draw.line(surface, accent, (p.x(306), p.y(204)),
                     (p.x(894), p.y(204)), p.s(3))
    p.text("CREATOR  /  MATCH COMPLETE", 600, 240, 15, MUTED, True, center=True)
    p.text(f"{winner} VICTORY" if winner else "MATCH COMPLETE",
           600, 290, 38, accent, True, center=True)

    if multiplayer is None:
        p.text("THE BOARD HAS BEEN DECIDED", 600, 347, 20, WHITE, center=True)
        p.text("VICTORY PATTERN  /  " + str(getattr(game.pattern, "name", "—")),
               600, 398, 17, MUTED, center=True)
        p.button(renderer.rematch_button, "PLAY AGAIN", primary=True)
        p.button(renderer.menu_button, "MAIN MENU")
        p.text("NEW MATCH  /  SAME RULES", 600, 637, 15, MUTED, center=True)
        return

    status = multiplayer.room_status or {}
    votes = status.get("rematch") or {}
    team = multiplayer.team
    verdict = "YOU WON" if winner == team else "OPPONENT WON" if winner else "MATCH FINISHED"
    p.text(verdict, 600, 333, 21, WHITE, True, center=True)
    p.text(f"MATCH #{status.get('match_number', 1)}  /  ROOM {multiplayer.room_code}",
           600, 371, 16, MUTED, center=True)
    for side, x, color in (("BLUE", 370, BLUE), ("RED", 612, RED)):
        ready = bool(votes.get(side))
        p.box(x, 400, 218, 69, PANEL2, color if ready else EDGE, 10)
        p.text(side, x+15, 407, 21, color, True)
        p.text("READY" if ready else "WAITING", x+15, 440, 15,
               GREEN if ready else MUTED)
    message = ("MATCH PAUSED  /  WAITING FOR RECONNECTION" if status.get("paused")
               else "VOTE REGISTERED  /  WAITING FOR OPPONENT" if votes.get(team)
               else "BOTH PLAYERS MUST VOTE FOR A REMATCH")
    p.text(message, 600, 495, 16, GOLD if status.get("paused") else MUTED,
           center=True)
    cx = 600
    p.button((cx-230, 525, 215, 62),
             "CANCEL VOTE" if votes.get(team) else "REMATCH",
             primary=True, disabled=bool(status.get("paused")))
    p.button((cx+15, 525, 215, 62), "MAIN MENU")
    p.text("NEW MATCH  /  FRESH BOARD  /  SAME ROOM",
           600, 623, 15, MUTED, center=True)
