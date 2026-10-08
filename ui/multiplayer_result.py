import pygame


class MultiplayerResult:
    """End-of-match overlay, independent of the local/AI victory UI."""

    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.small = pygame.font.SysFont("arial", 20)
        cx = screen.get_width() // 2
        self.rematch_button = pygame.Rect(cx - 230, 525, 215, 62)
        self.menu_button = pygame.Rect(cx + 15, 525, 215, 62)

    def draw(self, multiplayer, game):
        if not game.game_over:
            return
        status = multiplayer.room_status or {}
        votes = status.get("rematch", {})
        team = multiplayer.team
        winner = game.winner.team if game.winner else "NONE"
        veil = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        veil.fill((9, 13, 25, 225))
        self.screen.blit(veil, (0, 0))
        cx = self.screen.get_width() // 2

        def centered(message, y, font, color=(245, 245, 250)):
            surf = font.render(message, True, color)
            self.screen.blit(surf, surf.get_rect(center=(cx, y)))

        centered("VICTORY" if winner == team else "MATCH COMPLETE", 260,
                 self.title_font, (110, 210, 160) if winner == team else (245, 245, 250))
        centered(f"{winner} WINS", 333, self.title_font)
        centered(f"Match #{status.get('match_number', 1)}  |  Room {multiplayer.room_code}",
                 391, self.small, (180, 190, 210))
        blue = "READY" if votes.get("BLUE") else "WAITING"
        red = "READY" if votes.get("RED") else "WAITING"
        centered(f"Rematch votes:  BLUE {blue}  /  RED {red}", 453, self.small)
        if status.get("paused"):
            centered("Waiting for player to reconnect", 488, self.small, (255, 190, 95))
        for rect, label, color in (
            (self.rematch_button, "CANCEL VOTE" if votes.get(team) else "REMATCH", (45, 115, 210)),
            (self.menu_button, "MAIN MENU", (70, 76, 91)),
        ):
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            surf = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(surf, surf.get_rect(center=rect.center))
