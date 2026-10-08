import pygame


class MultiplayerHUD:

    BLUE = (75, 150, 255)
    RED = (245, 100, 110)
    WHITE = (245, 245, 250)
    MUTED = (175, 185, 205)
    GREEN = (75, 215, 145)
    AMBER = (255, 195, 90)
    PANEL = (20, 25, 38)
    BORDER = (60, 72, 95)

    def __init__(self, screen):
        self.screen = screen

        self.font = pygame.font.SysFont(
            "arial", 19, bold=True
        )

        self.small_font = pygame.font.SysFont(
            "arial", 15
        )

    def _text(self, value, x, y, color=None, font=None):
        font = font or self.font
        color = color or self.WHITE

        surface = font.render(
            str(value),
            True,
            color
        )

        self.screen.blit(surface, (x, y))

    def draw(self, multiplayer, game, sync):
        width = self.screen.get_width()

        panel = pygame.Rect(
            12,
            10,
            width - 24,
            58
        )

        pygame.draw.rect(
            self.screen,
            self.PANEL,
            panel,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            self.BORDER,
            panel,
            1,
            border_radius=10
        )

        your_team = multiplayer.team or "UNKNOWN"

        current_team = (
            game.current_player.team
            if game.current_player is not None
            else "UNKNOWN"
        )

        team_color = (
            self.BLUE
            if your_team == "BLUE"
            else self.RED
        )

        current_color = (
            self.BLUE
            if current_team == "BLUE"
            else self.RED
        )

        is_your_turn = (
            current_team == your_team
            and not game.game_over
        )

        self._text(
            f"YOU: {your_team}",
            28,
            18,
            team_color
        )

        room = multiplayer.room_code or "------"

        self._text(
            f"ROOM {room}",
            28,
            43,
            self.MUTED,
            self.small_font
        )

        turn_label = (
            "YOUR TURN"
            if is_your_turn
            else f"{current_team}'S TURN"
        )

        self._text(
            turn_label,
            width // 2 - 100,
            18,
            self.GREEN if is_your_turn else current_color
        )

        phase = multiplayer.game_state.turn_phase

        phase_names = {
            "WAITING_FOR_ROLL": "Roll the dice",
            "WAITING_FOR_SELECTION": "Select a pawn",
            "WAITING_FOR_MOVE": "Choose a destination",
        }

        phase_text = phase_names.get(
            phase,
            str(phase).replace("_", " ").title()
        )

        if paused := (multiplayer.room_status or {}).get("paused", False):
            phase_text = "Waiting for player to reconnect"
        elif not is_your_turn and not game.game_over:
            phase_text = "Waiting for opponent"

        if game.game_over:
            winner = (
                game.winner.team
                if game.winner is not None
                else "UNKNOWN"
            )
            phase_text = f"Winner: {winner}"

        self._text(
            phase_text,
            width // 2 - 100,
            43,
            self.MUTED,
            self.small_font
        )

        paused = (multiplayer.room_status or {}).get("paused", False)
        status = (
            "PAUSED" if paused and sync.connected else
            "LIVE"
            if sync.connected
            else "CONNECTION LOST"
        )

        status_color = (
            self.GREEN
            if sync.connected and not paused
            else self.AMBER
        )

        status_surface = self.font.render(
            status,
            True,
            status_color
        )

        self.screen.blit(
            status_surface,
            (
                width - status_surface.get_width() - 28,
                18
            )
        )

        self._text(
            "Waiting for player" if paused else "R: Refresh",
            width - 115,
            43,
            self.MUTED,
            self.small_font
        )
        event = (multiplayer.room_status or {}).get("last_event")
        if event and not game.game_over:
            if event.get("type") == "ROLL":
                detail = f"{event.get('team')} rolled {event.get('value')}"
            elif event.get("type") == "MOVE":
                detail = (f"{event.get('team')} pawn {event.get('pawn_id')} "
                          f"to ({event.get('row')}, {event.get('col')})")
                if event.get("captures", 0):
                    detail += f"  |  CAPTURE x{event['captures']}"
            else:
                detail = ""
            if detail:
                notice = self.small_font.render(detail, True, self.AMBER)
                box = pygame.Rect(12, 73, min(width - 24, notice.get_width() + 28), 29)
                pygame.draw.rect(self.screen, self.PANEL, box, border_radius=7)
                self.screen.blit(notice, (box.x + 12, box.y + 6))
