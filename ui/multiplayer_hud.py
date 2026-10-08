import pygame


class MultiplayerHUD:

    BLUE = (75, 150, 255)
    RED = (245, 100, 110)
    WHITE = (245, 245, 250)
    MUTED = (175, 185, 205)
    GREEN = (75, 215, 145)
    AMBER = (255, 195, 90)
    PANEL = (20, 33, 49)
    BORDER = (48, 78, 103)

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
            829,
            10,
            max(0, width - 845),
            65
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
            841,
            15,
            team_color
        )

        room = multiplayer.room_code or "------"

        self._text(
            f"ROOM {room}",
            841,
            42,
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
            975,
            15,
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
            975,
            42,
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
                width - status_surface.get_width() - 20,
                18
            )
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
                box = pygame.Rect(33, 53, min(766, notice.get_width() + 28), 27)
                pygame.draw.rect(self.screen, self.PANEL, box, border_radius=7)
                self.screen.blit(notice, (box.x + 12, box.y + 6))

        history = (multiplayer.room_status or {}).get("move_history", [])
        if history and not game.game_over:
            panel_x = 829
            panel_w = max(0, width - panel_x - 14)
            if panel_w >= 160:
                visible = history[-10:]
                panel_h = 46 + 23 * len(visible)
                panel = pygame.Rect(panel_x, 567, panel_w, min(panel_h, 290))
                pygame.draw.rect(self.screen, self.PANEL, panel, border_radius=9)
                pygame.draw.rect(self.screen, self.BORDER, panel, 1, border_radius=9)
                self._text("MATCH HISTORY", panel_x + 12, 579, self.WHITE, self.small_font)
                for i, entry in enumerate(reversed(visible)):
                    if entry.get("type") == "ROLL":
                        line = f"#{entry.get('id')} {entry.get('team')} rolled {entry.get('value')}"
                    elif entry.get("type") == "MOVE":
                        line = (f"#{entry.get('id')} {entry.get('team')} pawn {entry.get('pawn_id')} "
                                f"-> ({entry.get('row')},{entry.get('col')})")
                        if entry.get("captures", 0):
                            line += f" x{entry['captures']}"
                    else:
                        continue
                    label = self.small_font.render(line, True, self.AMBER if entry.get("captures", 0) else self.MUTED)
                    available = panel_w - 24
                    if label.get_width() > available:
                        # Fit long pawn identifiers without spilling outside the panel.
                        while len(line) > 3 and label.get_width() > available:
                            line = line[:-2] + "…"
                            label = self.small_font.render(line, True, self.MUTED)
                    self.screen.blit(label, (panel_x + 12, 608 + i * 23))
