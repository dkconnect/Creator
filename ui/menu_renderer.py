import pygame
from ui.menu_state import MenuState


class MenuRenderer:
    def __init__(self, screen, menu_state: MenuState):
        self.screen = screen
        self.state = menu_state
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.header_font = pygame.font.SysFont("arial", 32, bold=True)
        self.font = pygame.font.SysFont("arial", 24)
        self.small_font = pygame.font.SysFont("arial", 18)

        # Dynamic interactive button rects
        self.buttons = {}

    def _draw_button(self, rect, text, is_selected=False, is_active=True, color=(50, 50, 60), active_color=(70, 130, 240)):
        bg_color = active_color if is_selected else color
        if not is_active:
            bg_color = (35, 35, 40)

        pygame.draw.rect(self.screen, bg_color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 120), rect, width=2, border_radius=10)

        text_color = (255, 255, 255) if is_active else (120, 120, 130)
        btn_txt = self.font.render(text, True, text_color)
        btn_rect = btn_txt.get_rect(center=rect.center)
        self.screen.blit(btn_txt, btn_rect)

    def draw(self):
        self.screen.fill((20, 22, 28))
        self.buttons.clear()

        # Title
        title_surf = self.title_font.render("CREATOR", True, (240, 240, 245))
        self.screen.blit(title_surf, (self.screen.get_width() // 2 - title_surf.get_width() // 2, 60))

        if self.state.current_state == MenuState.MODE_SELECT:
            self._draw_mode_select()
        elif self.state.current_state == MenuState.AI_DIFFICULTY:
            self._draw_ai_difficulty()
        elif self.state.current_state == MenuState.AI_PATTERN:
            self._draw_pattern_select("START GAME")
        elif self.state.current_state == MenuState.ROOM_CHOICE:
            self._draw_room_choice()
        elif self.state.current_state == MenuState.ROOM_PATTERN:
            self._draw_pattern_select("CREATE & WAIT")
        elif self.state.current_state == MenuState.ROOM_JOIN:
            self._draw_room_join()
        elif self.state.current_state == MenuState.LOBBY_WAITING:
            self._draw_lobby_waiting()

    def _draw_mode_select(self):
        sub_text = self.header_font.render("SELECT MODE", True, (180, 180, 190))
        self.screen.blit(sub_text, (self.screen.get_width() // 2 - sub_text.get_width() // 2, 170))

        modes = [
            ("ONLINE", "Matchmaking against remote players"),
            ("AI", "Play against local intelligent bots"),
            ("FRIEND ROOM", "Play with friends via Room Code"),
        ]

        start_y = 260
        for i, (mode_key, desc) in enumerate(modes):
            rect = pygame.Rect(self.screen.get_width() // 2 - 220, start_y + i * 110, 440, 65)
            self.buttons[f"MODE_{mode_key}"] = rect
            self._draw_button(rect, mode_key)

            desc_surf = self.small_font.render(desc, True, (140, 140, 150))
            self.screen.blit(desc_surf, (self.screen.get_width() // 2 - desc_surf.get_width() // 2, start_y + i * 110 + 72))

    def _draw_ai_difficulty(self):
        sub_text = self.header_font.render("SELECT AI DIFFICULTY", True, (180, 180, 190))
        self.screen.blit(sub_text, (self.screen.get_width() // 2 - sub_text.get_width() // 2, 170))

        diffs = [
            ("EASY", "Basic 1-ply greedy decision-making"),
            ("LEARNING", "Adaptive AI that counters your playstyle"),
            ("ADVANCED", "Expectiminimax search with lookahead"),
        ]

        start_y = 260
        for i, (diff_key, desc) in enumerate(diffs):
            rect = pygame.Rect(self.screen.get_width() // 2 - 220, start_y + i * 110, 440, 65)
            self.buttons[f"DIFF_{diff_key}"] = rect
            self._draw_button(rect, diff_key)

            desc_surf = self.small_font.render(desc, True, (140, 140, 150))
            self.screen.blit(desc_surf, (self.screen.get_width() // 2 - desc_surf.get_width() // 2, start_y + i * 110 + 72))

        # Back Button
        back_rect = pygame.Rect(40, 40, 110, 45)
        self.buttons["BACK"] = back_rect
        self._draw_button(back_rect, "BACK", color=(60, 60, 70))

    def _draw_pattern_select(self, confirm_label):
        sub_text = self.header_font.render("CHOOSE PATTERN", True, (180, 180, 190))
        self.screen.blit(sub_text, (self.screen.get_width() // 2 - sub_text.get_width() // 2, 170))

        patterns = self.state.available_patterns
        start_y = 260
        for i, pat in enumerate(patterns):
            rect = pygame.Rect(self.screen.get_width() // 2 - 180, start_y + i * 70, 360, 50)
            is_selected = (self.state.selected_pattern == pat)
            self.buttons[f"PATTERN_{pat}"] = rect
            self._draw_button(rect, pat.replace(".json", ""), is_selected=is_selected)

        # Start / Action Button
        confirm_rect = pygame.Rect(self.screen.get_width() // 2 - 160, start_y + len(patterns) * 70 + 40, 320, 60)
        self.buttons["CONFIRM_START"] = confirm_rect
        self._draw_button(confirm_rect, confirm_label, is_selected=True, active_color=(40, 180, 80))

        # Back Button
        back_rect = pygame.Rect(40, 40, 110, 45)
        self.buttons["BACK"] = back_rect
        self._draw_button(back_rect, "BACK", color=(60, 60, 70))

    def _draw_room_choice(self):
        sub_text = self.header_font.render("FRIEND ROOM", True, (180, 180, 190))
        self.screen.blit(sub_text, (self.screen.get_width() // 2 - sub_text.get_width() // 2, 170))

        create_rect = pygame.Rect(self.screen.get_width() // 2 - 200, 280, 400, 70)
        join_rect = pygame.Rect(self.screen.get_width() // 2 - 200, 380, 400, 70)

        self.buttons["ROOM_CREATE"] = create_rect
        self.buttons["ROOM_JOIN"] = join_rect

        self._draw_button(create_rect, "CREATE ROOM")
        self._draw_button(join_rect, "JOIN ROOM")

        back_rect = pygame.Rect(40, 40, 110, 45)
        self.buttons["BACK"] = back_rect
        self._draw_button(back_rect, "BACK", color=(60, 60, 70))

    def _draw_room_join(self):
        sub_text = self.header_font.render("ENTER 6-DIGIT ROOM CODE", True, (180, 180, 190))
        self.screen.blit(sub_text, (self.screen.get_width() // 2 - sub_text.get_width() // 2, 170))

        # Code display box
        code_box = pygame.Rect(self.screen.get_width() // 2 - 160, 270, 320, 70)
        pygame.draw.rect(self.screen, (30, 30, 40), code_box, border_radius=8)
        pygame.draw.rect(self.screen, (120, 120, 150), code_box, 2, border_radius=8)

        display_code = self.state.room_code_input if self.state.room_code_input else "______"
        code_surf = self.header_font.render(display_code, True, (255, 255, 255))
        self.screen.blit(code_surf, code_surf.get_rect(center=code_box.center))

        # Join button
        can_join = len(self.state.room_code_input) == 6
        join_btn = pygame.Rect(self.screen.get_width() // 2 - 160, 370, 320, 60)
        self.buttons["SUBMIT_JOIN"] = join_btn
        self._draw_button(join_btn, "JOIN MATCH", is_selected=can_join, is_active=can_join, active_color=(40, 180, 80))

        back_rect = pygame.Rect(40, 40, 110, 45)
        self.buttons["BACK"] = back_rect
        self._draw_button(back_rect, "BACK", color=(60, 60, 70))

    def _draw_lobby_waiting(self):
        if self.state.selected_mode == "ONLINE":
            title = "MATCHMAKING"
            status = "Finding opponent in lobby..."
        else:
            title = "WAITING FOR FRIEND"
            status = f"Share Code: {self.state.generated_room_code}"

        sub_text = self.header_font.render(title, True, (180, 180, 190))
        self.screen.blit(sub_text, (self.screen.get_width() // 2 - sub_text.get_width() // 2, 200))

        status_surf = self.font.render(status, True, (100, 200, 255))
        self.screen.blit(status_surf, (self.screen.get_width() // 2 - status_surf.get_width() // 2, 300))

        # Start game trigger button for demo/local testing
        launch_btn = pygame.Rect(self.screen.get_width() // 2 - 160, 420, 320, 60)
        self.buttons["LAUNCH_GAME"] = launch_btn
        self._draw_button(launch_btn, "ENTER BOARD", is_selected=True, active_color=(40, 180, 80))

        back_rect = pygame.Rect(40, 40, 110, 45)
        self.buttons["BACK"] = back_rect
        self._draw_button(back_rect, "CANCEL", color=(60, 60, 70))