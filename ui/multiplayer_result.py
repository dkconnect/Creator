import pygame


class MultiplayerResult:
    """End-of-match overlay, independent of the local/AI victory UI."""

    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.small = pygame.font.SysFont("arial", 17)
        cx = screen.get_width() // 2
        self.rematch_button = pygame.Rect(cx - 230, 525, 215, 62)
        self.menu_button = pygame.Rect(cx + 15, 525, 215, 62)

    def draw(self, multiplayer, game):
        if not game.game_over:
            return
        status = multiplayer.room_status or {}
        votes = status.get('rematch') or {}
        team = multiplayer.team
        winner = getattr(game.winner, 'team', None)
        blue = (82, 166, 245)
        red = (225, 93, 112)
        accent = blue if winner == 'BLUE' else red if winner == 'RED' else (242, 194, 105)
        text_color = (236, 245, 253)
        muted = (149, 175, 196)
        edge = (48, 78, 103)
        panel_color = (20, 33, 49)
        veil = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        veil.fill((5, 12, 21, 235))
        self.screen.blit(veil, (0, 0))
        cx = self.screen.get_width() // 2
        panel = pygame.Rect(cx - 335, 181, 670, 489)
        pygame.draw.rect(self.screen, panel_color, panel, border_radius=20)
        pygame.draw.rect(self.screen, edge, panel, 2, border_radius=20)
        pygame.draw.line(self.screen, accent, (cx - 290, 205), (cx + 290, 205), 3)

        def centered(message, y, font, color=text_color):
            surface = font.render(str(message), True, color)
            self.screen.blit(surface, surface.get_rect(center=(cx, y)))

        centered('CREATOR / MATCH RESULT', 238, self.small, muted)
        centered(f'{winner} VICTORY' if winner else 'MATCH COMPLETE',
                 292, self.title_font, accent)
        outcome = 'YOU WON' if winner == team else 'OPPONENT WON' if winner else 'MATCH FINISHED'
        centered(outcome, 333, self.font)
        centered(f"MATCH #{status.get('match_number', 1)}  /  ROOM {multiplayer.room_code}",
                 371, self.small, muted)
        for side, x, color in (('BLUE', cx - 230, blue), ('RED', cx + 12, red)):
            rect = pygame.Rect(x, 400, 218, 69)
            ready = bool(votes.get(side))
            pygame.draw.rect(self.screen, (26, 45, 64), rect, border_radius=10)
            pygame.draw.rect(self.screen, color if ready else edge,
                             rect, 2 if ready else 1, border_radius=10)
            name = self.font.render(side, True, color)
            state = self.small.render('READY' if ready else 'WAITING', True,
                                      (90, 205, 158) if ready else muted)
            self.screen.blit(name, (rect.x + 15, rect.y + 8))
            self.screen.blit(state, (rect.x + 15, rect.y + 39))
        if status.get('paused'):
            centered('MATCH PAUSED / WAITING FOR RECONNECTION', 496,
                     self.small, (242, 194, 105))
        elif votes.get(team):
            centered('VOTE REGISTERED / WAITING FOR OPPONENT', 496,
                     self.small, (90, 205, 158))
        else:
            centered('BOTH PLAYERS MUST VOTE FOR A REMATCH', 496, self.small, muted)
        for rect, label, fill, disabled in (
            (self.rematch_button, 'CANCEL VOTE' if votes.get(team) else 'REMATCH',
             (38, 100, 153), bool(status.get('paused'))),
            (self.menu_button, 'MAIN MENU', (26, 45, 64), False),
        ):
            hover = rect.collidepoint(pygame.mouse.get_pos()) and not disabled
            if disabled:
                fill = (48, 60, 72)
            elif hover:
                fill = tuple(min(255, value + 18) for value in fill)
            pygame.draw.rect(self.screen, fill, rect, border_radius=11)
            pygame.draw.rect(self.screen, blue if hover else edge,
                             rect, 2 if hover else 1, border_radius=11)
            surface = self.font.render(label, True, muted if disabled else text_color)
            self.screen.blit(surface, surface.get_rect(center=rect.center))
        centered('NEW MATCH / FRESH BOARD / SAME ROOM', 622, self.small, muted)
