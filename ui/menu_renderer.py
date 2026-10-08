from ui.viewport import active_mouse_pos
import pygame
import json
from pathlib import Path
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
        self._render_scale = 1.0
        self._font_cache = {}

    def set_display_surface(self, surface, scale):
        """Use physical-resolution menu surface, keeping virtual click rects."""
        self.screen = surface
        self._render_scale = scale
        sizes = (("title_font", 48, True), ("header_font", 32, True),
                 ("font", 24, False), ("small_font", 18, False))
        for attr, points, bold in sizes:
            px = max(9, round(points * scale))
            key = (px, bold)
            if key not in self._font_cache:
                self._font_cache[key] = pygame.font.SysFont("arial", px, bold=bold)
            setattr(self, attr, self._font_cache[key])

    def _mouse_on_surface(self):
        vx, vy = active_mouse_pos()
        return (round(vx * self.screen.get_width() / 1200),
                round(vy * self.screen.get_height() / 900))

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
        self.screen.fill((12, 22, 34))
        self.buttons.clear()

        # The launch screen owns its brand placement; submenus keep their existing header.
        if self.state.current_state != MenuState.MODE_SELECT:
            self._draw_submenu_shell()

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

        self._draw_status_and_help()
        # Event coordinates are virtual; convert display-space hitboxes back.
        sx = self.screen.get_width() / 1200
        sy = self.screen.get_height() / 900
        for key, rect in list(self.buttons.items()):
            self.buttons[key] = pygame.Rect(
                round(rect.x / sx), round(rect.y / sy),
                max(1, round(rect.width / sx)), max(1, round(rect.height / sy)))

    def _draw_mode_select(self):
        """Premium launch screen; preserve the original MODE_* hit targets."""
        w, h = self.screen.get_size()
        sx, sy = w / 1200, h / 900
        def R(x, y, width, height):
            return pygame.Rect(round(x*sx), round(y*sy), round(width*sx), round(height*sy))
        def label(text, x, y, font, color, center=False):
            surface = font.render(text, True, color)
            target = surface.get_rect(center=(round(x*sx), round(y*sy))) if center else (round(x*sx), round(y*sy))
            self.screen.blit(surface, target)

        # Quiet geometric board motif on the left; no external assets.
        motif = R(68, 250, 470, 470)
        tile = motif.width / 8
        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(round(motif.x + col*tile), round(motif.y + row*tile),
                                   round(tile)+1, round(tile)+1)
                shade = (19, 35, 51) if (row+col)%2 == 0 else (15, 28, 42)
                pygame.draw.rect(self.screen, shade, rect)
                pygame.draw.rect(self.screen, (29, 48, 65), rect, 1)
        # Distinctive abstract pieces, rather than misleading actual game positions.
        for row, col, color in ((1,1,(59,145,229)),(2,4,(59,145,229)),
                                (5,2,(213,91,107)),(6,6,(213,91,107))):
            cx = round(motif.x+(col+.5)*tile)
            cy = round(motif.y+(row+.5)*tile)
            pygame.draw.circle(self.screen, (9, 17, 27), (cx+3,cy+4), max(8,round(tile*.27)))
            pygame.draw.circle(self.screen, color, (cx,cy), max(8,round(tile*.27)))
            pygame.draw.circle(self.screen, (228,239,252), (cx,cy), max(3,round(tile*.12)), 1)
        pygame.draw.rect(self.screen, (55, 83, 108), motif, 2, border_radius=4)

        label('TACTICS  /  TERRITORY  /  PATTERNS', 70, 116, self.small_font, (96, 167, 218))
        label('CREATOR', 65, 146, self.title_font, (238, 246, 255))
        label('OWN THE BOARD.', 70, 206, self.header_font, (183, 204, 223))
        label('Think ahead. Take space. Complete the pattern.', 70, 746,
              self.small_font, (147, 166, 186))

        # Right-side launch panel, with card-based actions.
        panel = R(618, 122, 518, 650)
        pygame.draw.rect(self.screen, (20, 32, 47), panel, border_radius=20)
        pygame.draw.rect(self.screen, (47, 73, 98), panel, 1, border_radius=20)
        label('CHOOSE GAME MODE', 650, 155, self.header_font, (236, 245, 254))
        label('Every match has exactly two players', 650, 201, self.small_font, (142, 165, 187))

        modes = (
            ('AI', 'SOLO  /  AI OPPONENT', 'Train against three AI difficulty levels', True),
            ('FRIEND ROOM', 'MULTIPLAYER  /  PRIVATE ROOM', 'Create a room or join with a code', True),
            ('ONLINE', 'GLOBAL  /  MATCHMAKING', 'Coming in a future update', False),
        )
        mouse = self._mouse_on_surface()
        for index, (key, title, desc, active) in enumerate(modes):
            rect = R(650, 252+index*142, 452, 116)
            self.buttons[f'MODE_{key}'] = rect
            hover = active and rect.collidepoint(mouse)
            bg = (31, 65, 91) if hover else ((27, 46, 65) if active else (24, 35, 47))
            outline = (88, 174, 236) if hover else ((52, 86, 113) if active else (42, 57, 71))
            pygame.draw.rect(self.screen, bg, rect, border_radius=12)
            pygame.draw.rect(self.screen, outline, rect, 2 if hover else 1, border_radius=12)
            accent = (92, 184, 245) if index == 0 else ((89, 197, 167) if index == 1 else (99, 112, 129))
            pygame.draw.rect(self.screen, accent, R(650, 269+index*142, 4, 81), border_radius=2)
            label(title, 675, 270+index*142, self.font, (241,247,253) if active else (130,144,159))
            label(desc, 675, 310+index*142, self.small_font, (154,178,199) if active else (102,116,131))
            label('>' if active else 'SOON', 1055 if active else 1025,
                  290+index*142, self.small_font, accent)

        label('H  HELP', 650, 723, self.small_font, (142, 165, 187))

    # All coordinates below are authored on the same 1200 x 900 canvas as 47A.
    # Scaling preserves mouse hit targets on other window sizes.
    def _r(self, x, y, w, h):
        sw, sh = self.screen.get_size()
        return pygame.Rect(round(x * sw / 1200), round(y * sh / 900),
                           round(w * sw / 1200), round(h * sh / 900))

    def _text(self, value, x, y, font=None, color=(233, 243, 252), center=False):
        surf = (font or self.font).render(str(value), True, color)
        sw, sh = self.screen.get_size()
        px, py = round(x * sw / 1200), round(y * sh / 900)
        self.screen.blit(surf, surf.get_rect(center=(px, py)) if center else (px, py))

    def _panel(self, x, y, w, h):
        rect = self._r(x, y, w, h)
        pygame.draw.rect(self.screen, (20, 32, 47), rect, border_radius=18)
        pygame.draw.rect(self.screen, (47, 73, 98), rect, 1, border_radius=18)
        return rect

    def _draw_submenu_shell(self):
        self._text('CREATOR', 66, 52, self.header_font)
        self._text('TACTICS  /  TERRITORY  /  PATTERNS', 68, 102,
                   self.small_font, (103, 163, 207))
        pygame.draw.line(self.screen, (42, 66, 87),
                         self._r(66, 136, 0, 0).topleft,
                         self._r(1134, 136, 0, 0).topleft, 1)
        self._back_button()

    def _back_button(self):
        rect = self._r(68, 779, 180, 57)
        self.buttons['BACK'] = rect
        self._card(rect, 'BACK', 'ESC  /  RETURN', (133, 156, 179))

    def _card(self, rect, heading, subtitle, accent=(92, 184, 245),
              selected=False, enabled=True):
        hovered = enabled and rect.collidepoint(self._mouse_on_surface())
        fill = (31, 65, 91) if hovered else ((31, 59, 76) if selected else (27, 46, 65))
        if not enabled:
            fill = (24, 35, 47)
        edge = accent if (hovered or selected) else (52, 86, 113)
        pygame.draw.rect(self.screen, fill, rect, border_radius=12)
        pygame.draw.rect(self.screen, edge, rect, 2 if hovered or selected else 1, border_radius=12)
        pygame.draw.rect(self.screen, accent if enabled else (78, 92, 106),
                         pygame.Rect(rect.x, rect.y + 12, max(3, rect.width // 110),
                                     max(4, rect.height - 24)), border_radius=2)
        title_color = (240, 247, 253) if enabled else (130, 144, 159)
        self.screen.blit(self.font.render(heading, True, title_color),
                         (rect.x + 25, rect.y + max(12, rect.height // 5)))
        if subtitle:
            self.screen.blit(self.small_font.render(subtitle, True, (150, 176, 198)),
                             (rect.x + 25, rect.y + max(43, rect.height // 2 + 5)))

    def _page_header(self, eyebrow, heading, description):
        self._text(eyebrow, 330, 180, self.small_font, (95, 176, 232))
        self._text(heading, 330, 219, self.header_font)
        self._text(description, 330, 273, self.small_font, (151, 177, 198))

    def _draw_ai_difficulty(self):
        self._panel(302, 157, 830, 620)
        self._page_header('SOLO CAMPAIGN  /  01', 'CHOOSE YOUR OPPONENT',
                          'Select the intelligence level for your match.')
        entries = (
            ('EASY', 'A straightforward tactical opponent', (89, 197, 167)),
            ('LEARNING', 'Adapts to your playing style', (92, 184, 245)),
            ('ADVANCED', 'Deeper search and stronger planning', (216, 151, 104)),
        )
        for i, (key, description, accent) in enumerate(entries):
            rect = self._r(332, 330 + i * 132, 768, 104)
            self.buttons[f'DIFF_{key}'] = rect
            self._card(rect, key, description, accent)

    def _draw_pattern_select(self, confirm_label):
        self._panel(302, 157, 830, 620)
        self._page_header('MATCH SETUP  /  PATTERN LIBRARY', 'CHOOSE YOUR FORMATION',
                          '53 formations  /  One victory condition')
        tabs = [('LETTERS', 'A-Z'), ('NUMBERS', '1-9'),
                ('SYMBOLS', 'SYMBOLS'), ('SHAPES', 'SHAPES')]
        for i, (key, title) in enumerate(tabs):
            rect = self._r(328 + i * 195, 286, 181, 43)
            self.buttons['CATEGORY_' + key] = rect
            selected = self.state.pattern_category == key
            pygame.draw.rect(self.screen, (35, 92, 130) if selected else (28, 47, 65),
                             rect, border_radius=8)
            pygame.draw.rect(self.screen, (99, 182, 241) if selected else (54, 82, 104),
                             rect, 2 if selected else 1, border_radius=8)
            text = self.small_font.render(title, True, (236, 246, 253))
            self.screen.blit(text, text.get_rect(center=rect.center))

        candidates = [filename for filename in self.state.available_patterns
                      if self.state.pattern_category_for(filename) == self.state.pattern_category]
        page_size = 20
        pages = max(1, (len(candidates) + page_size - 1) // page_size)
        self.state.pattern_page = min(self.state.pattern_page, pages - 1)
        page_items = candidates[self.state.pattern_page * page_size:
                                (self.state.pattern_page + 1) * page_size]
        for i, filename in enumerate(page_items):
            col, row = i % 5, i // 5
            rect = self._r(329 + col * 98, 352 + row * 75, 88, 64)
            selected = self.state.selected_pattern == filename
            pygame.draw.rect(self.screen, (37, 86, 122) if selected else (25, 45, 63),
                             rect, border_radius=9)
            pygame.draw.rect(self.screen, (105, 188, 250) if selected else (51, 79, 104),
                             rect, 2 if selected else 1, border_radius=9)
            self.buttons['PATTERN_' + filename] = rect
            label = self.state.pattern_label(filename)
            font = self.small_font if len(label) > 3 else self.font
            text = font.render(label[:10], True, (237, 246, 253))
            self.screen.blit(text, text.get_rect(center=rect.center))

        if pages > 1:
            for key, x, label in [('PREV', 333, '<'), ('NEXT', 717, '>')]:
                rect = self._r(x, 662, 55, 38)
                self.buttons['PAGE_' + key] = rect
                self._draw_button(rect, label)
            self._text(f'{self.state.pattern_page + 1} / {pages}', 569, 673,
                       self.small_font, center=True)

        preview = self._r(832, 351, 270, 309)
        pygame.draw.rect(self.screen, (15, 29, 43), preview, border_radius=12)
        pygame.draw.rect(self.screen, (50, 83, 110), preview, 1, border_radius=12)
        filename = self.state.selected_pattern
        if filename:
            try:
                source = Path(__file__).resolve().parent.parent / 'patterns' / filename
                data = json.loads(source.read_text(encoding='utf-8'))
                grid = data['grid']
                count = sum(bool(cell) for row in grid for cell in row)
                self._text(str(data.get('name', filename[:-5]))[:17], 852, 368,
                           self.font, (232, 245, 255))
                self._text(f'{count} PAWNS REQUIRED', 852, 414,
                           self.small_font, (148, 185, 210))
                n = len(grid)
                cell = min(27, 190 // max(1, n))
                origin_x = preview.centerx - n * cell // 2
                origin_y = preview.y + 86
                for y, row in enumerate(grid):
                    for x, active in enumerate(row):
                        r = pygame.Rect(origin_x + x * cell, origin_y + y * cell,
                                        cell - 3, cell - 3)
                        pygame.draw.rect(self.screen, (100, 184, 247) if active else
                                         (37, 60, 79), r, border_radius=3)
            except (OSError, ValueError, KeyError, TypeError):
                self._text('PREVIEW UNAVAILABLE', 843, 445, self.small_font)
        rect = self._r(833, 681, 268, 64)
        self.buttons['CONFIRM_START'] = rect
        self._card(rect, confirm_label, '', (89, 197, 167), selected=True)

    def _draw_room_choice(self):
        self._panel(302, 157, 830, 620)
        self._page_header('MULTIPLAYER  /  PRIVATE ROOM', 'PLAY WITH A FRIEND',
                          'Create a private room or enter an existing room code.')
        for i, (key, title, desc, accent) in enumerate((
            ('ROOM_CREATE', 'CREATE ROOM', 'Host a private match and share your code', (92, 184, 245)),
            ('ROOM_JOIN', 'JOIN ROOM', 'Enter the six-character code from a friend', (89, 197, 167)),
        )):
            rect = self._r(332, 345 + i * 164, 768, 125)
            self.buttons[key] = rect
            self._card(rect, title, desc, accent)
        self._text('Both players must be ready before the match starts.',
                   332, 693, self.small_font, (145, 170, 190))

    def _draw_room_join(self):
        self._panel(302, 157, 830, 620)
        self._page_header('MULTIPLAYER  /  JOIN', 'ENTER ROOM CODE',
                          'Type the six-character code shared by the host.')
        code_rect = self._r(332, 344, 768, 136)
        pygame.draw.rect(self.screen, (14, 26, 39), code_rect, border_radius=12)
        pygame.draw.rect(self.screen, (70, 115, 150), code_rect, 2, border_radius=12)
        code = self.state.room_code_input or '_ _ _ _ _ _'
        self._text(code, 716, 411, self.title_font, (237, 247, 255), center=True)
        self._text('Room codes are case-insensitive.', 332, 508,
                   self.small_font, (145, 170, 190))
        enabled = len(self.state.room_code_input) == 6
        rect = self._r(332, 576, 768, 84)
        self.buttons['SUBMIT_JOIN'] = rect
        self._card(rect, 'JOIN MATCH', 'Connect to the private room',
                   (89, 197, 167), selected=enabled, enabled=enabled)

    def _draw_friend_lobby(self):
        info = getattr(self.state, 'lobby_data', None) or {}
        players = info.get('players', {})
        self._panel(302, 157, 830, 620)
        self._page_header('MULTIPLAYER  /  LOBBY', 'PRIVATE MATCH LOBBY',
                          'Share the code, then both players select READY.')
        code = self.state.room_code_input or getattr(self.state, 'generated_room_code', '') or '------'
        self._text('ROOM CODE', 332, 318, self.small_font, (151, 177, 198))
        self._text(code, 332, 346, self.title_font, (110, 190, 255))
        for i, team in enumerate(('BLUE', 'RED')):
            member = players.get(team, {})
            connected = member.get('connected', False)
            ready = member.get('ready', False)
            status = 'READY' if ready else ('NOT READY' if connected else 'WAITING FOR PLAYER')
            accent = (92, 184, 245) if team == 'BLUE' else (229, 105, 121)
            rect = self._r(332 + i * 390, 430, 378, 124)
            self._card(rect, team, status, accent, selected=ready)
        own = players.get(getattr(self.state, 'lobby_team', None), {})
        ready = own.get('ready', False)
        rect = self._r(332, 594, 768, 82)
        self.buttons['TOGGLE_READY'] = rect
        self._card(rect, 'CANCEL READY' if ready else "I'M READY",
                   'Waiting for both players to confirm',
                   (89, 197, 167), selected=ready)
        if info.get('started'):
            self._text('Both players ready - starting match...', 332, 709,
                       self.small_font, (89, 197, 167))

    def _draw_lobby_waiting(self):
        if self.state.selected_mode == "ROOM":
            self._draw_friend_lobby()
            return

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
    def _draw_status_and_help(self):
        width, height = self.screen.get_size()
        hint = self.small_font.render("H: Help    ESC: Back", True, (165, 175, 195))
        self.screen.blit(hint, (24, height - 36))
        if self.state.status_message:
            message = self.state.status_message[:100]
            surface = self.small_font.render(message, True, (255, 190, 125))
            self.screen.blit(surface, surface.get_rect(center=(width // 2, height - 75)))
        if not self.state.show_help:
            return
        panel = pygame.Rect(width // 2 - 340, height // 2 - 235, 680, 470)
        pygame.draw.rect(self.screen, (29, 36, 50), panel, border_radius=14)
        pygame.draw.rect(self.screen, (115, 150, 195), panel, 2, border_radius=14)
        lines = [
            "HOW TO PLAY CREATOR",
            "Roll: click the dice or press SPACE.",
            "Select one of your pawns, then a highlighted square.",
            "Capture opposing pawns and complete your target pattern.",
            "AI: play against the computer locally.",
            "Friend Room: start the TCP server, create or join a code.",
            "Both players must select READY to begin.",
            "During multiplayer: R refreshes the match.",
            "Global matchmaking is not available in v1.",
            "Press H or ESC to close this guide.",
        ]
        for i, line in enumerate(lines):
            font = self.header_font if i == 0 else self.small_font
            surface = font.render(line, True, (235, 240, 250))
            self.screen.blit(surface, (panel.x + 32, panel.y + 27 + i * 43))
