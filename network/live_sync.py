import pygame


class LiveSync:
    """
    Synchronizes the client-side game adapter with the
    authoritative server without clearing local selection
    when the server state has not changed.
    """

    def __init__(self, multiplayer, game_adapter, interval_ms=500):
        self.multiplayer = multiplayer
        self.game_adapter = game_adapter
        self.interval_ms = interval_ms

        self.last_check = pygame.time.get_ticks()
        self.last_success = self.last_check

        self.connected = True
        self.last_error = None
        self.update_count = 0

        self._signature = self._make_signature()
        self.reconnect_attempt_ms = 2000
        self.last_reconnect_attempt = 0

    def _make_signature(self):
        state = self.multiplayer.game_state

        pawn_data = []

        for team in ("BLUE", "RED"):
            player = (state.players or {}).get(team, {})

            for pawn in player.get("pawns", []):
                pawn_data.append(
                    (
                        team,
                        pawn.get("id"),
                        pawn.get("row"),
                        pawn.get("col"),
                        pawn.get("active"),
                    )
                )

        return (
            state.current_player,
            state.turn_phase,
            state.dice,
            state.game_over,
            state.winner,
            state.selected_pawn_id,
            (self.multiplayer.room_status or {}).get("match_number", 1),
            (self.multiplayer.room_status or {}).get("event_id", 0),
            tuple(sorted(pawn_data, key=str)),
        )

    def poll(self, force=False):
        now = pygame.time.get_ticks()

        if (
            not force
            and now - self.last_check < self.interval_ms
        ):
            return False

        self.last_check = now

        if self.multiplayer.client.socket is None:
            if now - self.last_reconnect_attempt < self.reconnect_attempt_ms:
                return False
            self.last_reconnect_attempt = now
            if not self.multiplayer.reconnect():
                self.connected = False
                self.last_error = "Reconnecting..."
                return False

        try:
            response = self.multiplayer.get_state()

            if (
                response is None
                or response.get("type") != "GAME_STATE"
            ):
                self.connected = False
                self.last_error = "State request failed"
                return False

            self.connected = True
            self.last_error = None
            self.last_success = now

            new_signature = self._make_signature()

            if new_signature == self._signature:
                return False

            self._signature = new_signature
            self.game_adapter.refresh()
            self.update_count += 1

            return True

        except (ConnectionError, OSError, TimeoutError) as exc:
            self.connected = False
            self.last_error = str(exc)
            return False

    def acknowledge_local_update(self):
        """
        Called after a successful local roll or move.
        Prevents the next poll from needlessly rebuilding
        the same board.
        """
        self._signature = self._make_signature()
        self.last_success = pygame.time.get_ticks()
        self.connected = True
        self.last_error = None

    def reset(self):
        self._signature = self._make_signature()
        self.last_check = pygame.time.get_ticks()