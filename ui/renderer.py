"""Creator gameplay renderer: modern dark strategy UI.

Retains the public board constants and button rectangles used by InputManager
and main.py. Works with Game and ClientGameAdapter.
"""
import pygame


class Renderer:
    CELL_SIZE = 48
    BOARD_X = 32
    BOARD_Y = 86

    BG = (12, 22, 34)
    PANEL = (20, 33, 49)
    PANEL_ALT = (26, 45, 64)
    EDGE = (48, 78, 103)
    TEXT = (236, 245, 253)
    MUTED = (149, 175, 196)
    BLUE = (82, 166, 245)
    RED = (225, 93, 112)
    GREEN = (90, 205, 158)
    GOLD = (242, 194, 105)

    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.SysFont('arial', 23, bold=True)
        self.small = pygame.font.SysFont('arial', 17)
        self.tiny = pygame.font.SysFont('arial', 14, bold=True)
        self.heading = pygame.font.SysFont('arial', 32, bold=True)
        self.dice_button = pygame.Rect(844, 338, 326, 64)
        self.rematch_button = pygame.Rect(390, 500, 200, 60)
        self.menu_button = pygame.Rect(610, 500, 200, 60)

    def _label(self, text, x, y, font=None, color=None):
        surf = (font or self.small).render(str(text), True, color or self.TEXT)
        self.screen.blit(surf, (x, y))
        return surf

    def _panel(self, rect):
        pygame.draw.rect(self.screen, self.PANEL, rect, border_radius=14)
        pygame.draw.rect(self.screen, self.EDGE, rect, 1, border_radius=14)

    def _stat(self, title, value, y, color=None):
        self._label(title, 862, y, self.tiny, self.MUTED)
        self._label(value, 862, y + 24, self.font, color or self.TEXT)

    def draw(self):
        self.screen.fill(self.BG)
        size = self.game.board.size
        board_w = size * self.CELL_SIZE
        board_rect = pygame.Rect(self.BOARD_X - 7, self.BOARD_Y - 7,
                                 board_w + 14, board_w + 14)
        pygame.draw.rect(self.screen, self.PANEL, board_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.EDGE, board_rect, 2, border_radius=10)
        self._label('CREATOR   /   TACTICAL BOARD', 33, 31, self.font)
        self._label('COMPLETE THE PATTERN TO WIN', 470, 38, self.tiny, self.MUTED)

        # Board cells and center victory-pattern target.
        pattern = self.game.pattern
        offset = (size - pattern.size) // 2 if pattern.size else 0
        target = set()
        for r in range(pattern.size):
            for c in range(pattern.size):
                if pattern.grid[r][c] == 1:
                    target.add((r + offset, c + offset))
        for r in range(size):
            for c in range(size):
                rect = pygame.Rect(self.BOARD_X + c * self.CELL_SIZE,
                                   self.BOARD_Y + r * self.CELL_SIZE,
                                   self.CELL_SIZE, self.CELL_SIZE)
                color = (22, 43, 61) if (r + c) % 2 == 0 else (18, 36, 53)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (39, 65, 86), rect, 1)
                if (r, c) in target:
                    pygame.draw.rect(self.screen, (67, 92, 107), rect, 2)
                    marker = pygame.Rect(rect.centerx - 4, rect.centery - 4, 8, 8)
                    pygame.draw.rect(self.screen, (91, 127, 146), marker, border_radius=2)

        try:
            valid_moves = self.game.get_valid_moves()
        except (AttributeError, ValueError):
            valid_moves = []
        for r, c in valid_moves:
            cx = self.BOARD_X + c * self.CELL_SIZE + self.CELL_SIZE // 2
            cy = self.BOARD_Y + r * self.CELL_SIZE + self.CELL_SIZE // 2
            pygame.draw.circle(self.screen, self.GREEN, (cx, cy), 9, 2)
            pygame.draw.circle(self.screen, self.GREEN, (cx, cy), 3)

        selected = self.game.selected_pawn
        for r in range(size):
            for c in range(size):
                pawn = self.game.board.get_pawn(r, c)
                if pawn is None:
                    continue
                cx = self.BOARD_X + c * self.CELL_SIZE + self.CELL_SIZE // 2
                cy = self.BOARD_Y + r * self.CELL_SIZE + self.CELL_SIZE // 2
                team_color = self.BLUE if pawn.team == 'BLUE' else self.RED
                pygame.draw.circle(self.screen, (7, 15, 25), (cx + 2, cy + 3), 19)
                pygame.draw.circle(self.screen, team_color, (cx, cy), 17)
                pygame.draw.circle(self.screen, (219, 238, 249), (cx - 4, cy - 5), 5, 1)
                if selected is pawn or (selected is not None and
                                        getattr(selected, 'id', None) == getattr(pawn, 'id', None)
                                        and selected.team == pawn.team):
                    pygame.draw.circle(self.screen, self.GOLD, (cx, cy), 22, 3)

        # The right rail reserves its lower half for multiplayer history.
        self._panel(pygame.Rect(829, 86, 355, 344))
        self._label('MATCH CONTROL', 850, 106, self.tiny, self.MUTED)
        current = getattr(self.game.current_player, 'team', '—')
        current_color = self.BLUE if current == 'BLUE' else self.RED
        self._label(f'{current} TO PLAY', 850, 130, self.heading, current_color)
        pygame.draw.line(self.screen, self.EDGE, (849, 182), (1162, 182), 1)
        dice = self.game.dice.value
        self._stat('DICE RESULT', '—' if dice is None else str(dice), 199, self.GOLD)
        self._stat('VICTORY PATTERN', str(pattern.name or '—'), 267)

        hover = self.dice_button.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, (49, 125, 182) if hover else (38, 100, 153),
                         self.dice_button, border_radius=10)
        pygame.draw.rect(self.screen, self.BLUE, self.dice_button, 2, border_radius=10)
        button_text = self.font.render('ROLL DICE', True, self.TEXT)
        self.screen.blit(button_text, button_text.get_rect(center=self.dice_button.center))

        self._panel(pygame.Rect(829, 442, 355, 109))
        self._label('PAWN LOSSES', 849, 458, self.tiny, self.MUTED)
        blue = getattr(self.game.blue, 'respawns', 0)
        red = getattr(self.game.red, 'respawns', 0)
        self._label(f'BLUE   {blue}', 849, 491, self.font, self.BLUE)
        self._label(f'RED   {red}', 1010, 491, self.font, self.RED)
        self._label('SELECT A PAWN  /  CHOOSE A HIGHLIGHTED SQUARE',
                    830, 864, self.tiny, self.MUTED)

        if self.game.game_over:
            self._draw_victory()

    def _draw_victory(self):
        veil = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        veil.fill((5, 12, 21, 228))
        self.screen.blit(veil, (0, 0))
        panel = pygame.Rect(286, 230, 628, 420)
        pygame.draw.rect(self.screen, self.PANEL, panel, border_radius=20)
        pygame.draw.rect(self.screen, self.EDGE, panel, 2, border_radius=20)
        pygame.draw.line(self.screen, self.BLUE, (330, 254), (870, 254), 3)
        winner = getattr(self.game.winner, 'team', None)
        accent = self.BLUE if winner == 'BLUE' else self.RED if winner == 'RED' else self.GOLD

        def centered(label, y, font, color):
            surface = font.render(label, True, color)
            self.screen.blit(surface, surface.get_rect(center=(600, y)))

        centered('CREATOR / MATCH COMPLETE', 300, self.tiny, self.MUTED)
        centered(f'{winner} VICTORY' if winner else 'MATCH COMPLETE',
                 360, self.heading, accent)
        centered('THE BOARD HAS BEEN DECIDED', 411, self.small, self.TEXT)
        pattern = getattr(getattr(self.game, 'pattern', None), 'name', None)
        if pattern:
            centered(f'VICTORY PATTERN / {pattern}', 454, self.small, self.MUTED)
        for rect, label, fill in (
            (self.rematch_button, 'PLAY AGAIN', (38, 100, 153)),
            (self.menu_button, 'MAIN MENU', self.PANEL_ALT),
        ):
            hover = rect.collidepoint(pygame.mouse.get_pos())
            if hover:
                fill = tuple(min(255, v + 18) for v in fill)
            pygame.draw.rect(self.screen, fill, rect, border_radius=11)
            pygame.draw.rect(self.screen, self.BLUE if hover else self.EDGE,
                             rect, 2 if hover else 1, border_radius=11)
            text = self.font.render(label, True, self.TEXT)
            self.screen.blit(text, text.get_rect(center=rect.center))
        centered('NEW MATCH / SAME RULES', 610, self.tiny, self.MUTED)
