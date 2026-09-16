import pygame
import json

from pathlib import Path

from engine.game import Game
from engine.ai.basic_ai import BasicAI
from engine.ai.learning_ai import LearningAI
from engine.ai.advanced_ai import AdvancedAI

from ui.renderer import Renderer
from ui.input_manager import InputManager
from ui.menu_state import MenuState
from ui.menu_renderer import MenuRenderer


pygame.init()

WIDTH, HEIGHT = 1200, 900

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Creator")

menu_state = MenuState()
menu_renderer = MenuRenderer(screen, menu_state)

game = None
renderer = None
input_manager = None

clock = pygame.time.Clock()
running = True

# AI turn pacing timer
ai_turn_delay_ms = 1500
last_ai_step_time = 0


def start_game():
    global game, renderer, input_manager, last_ai_step_time

    # Reset AI pacing for every new game/rematch
    last_ai_step_time = pygame.time.get_ticks()

    ai_controller = None

    if menu_state.selected_mode == "AI":

        if menu_state.selected_difficulty == "EASY":
            ai_controller = BasicAI(team="RED")

        elif menu_state.selected_difficulty == "LEARNING":
            ai_controller = LearningAI(team="RED")

        elif menu_state.selected_difficulty == "ADVANCED":
            ai_controller = AdvancedAI(team="RED")

    game = Game(ai_controller=ai_controller)

    # Load custom chosen pattern if selected
    if menu_state.selected_pattern:

        pattern_file = (
            Path(__file__).resolve().parent
            / "patterns"
            / menu_state.selected_pattern
        )

        if pattern_file.exists():
            with open(pattern_file, "r") as f:
                data = json.load(f)

                game.pattern.name = data["name"]
                game.pattern.size = data["size"]
                game.pattern.grid = data["grid"]

    renderer = Renderer(screen, game)
    input_manager = InputManager(renderer)

    menu_state.current_state = MenuState.IN_GAME


while running:

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # --------------------------------------------------
        # MENU EVENT HANDLING
        # --------------------------------------------------

        elif menu_state.current_state != MenuState.IN_GAME:

            if event.type == pygame.MOUSEBUTTONDOWN:

                pos = event.pos

                for btn_key, rect in menu_renderer.buttons.items():

                    if rect.collidepoint(pos):

                        # -------------------------
                        # Navigation & Back
                        # -------------------------

                        if btn_key == "BACK":

                            if menu_state.current_state in (
                                MenuState.AI_DIFFICULTY,
                                MenuState.ROOM_CHOICE,
                                MenuState.LOBBY_WAITING,
                            ):
                                menu_state.reset()

                            elif (
                                menu_state.current_state
                                == MenuState.AI_PATTERN
                            ):
                                menu_state.current_state = (
                                    MenuState.AI_DIFFICULTY
                                )

                            elif menu_state.current_state in (
                                MenuState.ROOM_PATTERN,
                                MenuState.ROOM_JOIN,
                            ):
                                menu_state.current_state = (
                                    MenuState.ROOM_CHOICE
                                )

                            break

                        # -------------------------
                        # Mode Select
                        # -------------------------

                        if btn_key == "MODE_ONLINE":

                            menu_state.selected_mode = "ONLINE"
                            menu_state.current_state = (
                                MenuState.LOBBY_WAITING
                            )

                        elif btn_key == "MODE_AI":

                            menu_state.selected_mode = "AI"
                            menu_state.current_state = (
                                MenuState.AI_DIFFICULTY
                            )

                        elif btn_key == "MODE_FRIEND ROOM":

                            menu_state.selected_mode = "ROOM"
                            menu_state.current_state = (
                                MenuState.ROOM_CHOICE
                            )

                        # -------------------------
                        # AI Difficulty
                        # -------------------------

                        elif btn_key.startswith("DIFF_"):

                            diff = btn_key.replace("DIFF_", "")

                            menu_state.selected_difficulty = diff
                            menu_state.current_state = (
                                MenuState.AI_PATTERN
                            )

                        # -------------------------
                        # Room Choice
                        # -------------------------

                        elif btn_key == "ROOM_CREATE":

                            menu_state.room_action = "CREATE"
                            menu_state.current_state = (
                                MenuState.ROOM_PATTERN
                            )

                        elif btn_key == "ROOM_JOIN":

                            menu_state.room_action = "JOIN"
                            menu_state.current_state = (
                                MenuState.ROOM_JOIN
                            )

                        # -------------------------
                        # Pattern Pick
                        # -------------------------

                        elif btn_key.startswith("PATTERN_"):

                            pat = btn_key.replace("PATTERN_", "")
                            menu_state.selected_pattern = pat

                        # -------------------------
                        # Confirmations
                        # -------------------------

                        elif btn_key == "CONFIRM_START":

                            if menu_state.selected_mode == "AI":
                                start_game()

                            else:
                                menu_state.current_state = (
                                    MenuState.LOBBY_WAITING
                                )

                        elif btn_key == "SUBMIT_JOIN":

                            if len(menu_state.room_code_input) == 6:
                                menu_state.current_state = (
                                    MenuState.LOBBY_WAITING
                                )

                        elif btn_key == "LAUNCH_GAME":

                            start_game()

                        break

            elif (
                event.type == pygame.KEYDOWN
                and menu_state.current_state == MenuState.ROOM_JOIN
            ):

                if event.key == pygame.K_BACKSPACE:

                    menu_state.room_code_input = (
                        menu_state.room_code_input[:-1]
                    )

                elif (
                    len(menu_state.room_code_input) < 6
                    and event.unicode.isalnum()
                ):

                    menu_state.room_code_input += (
                        event.unicode.upper()
                    )

        # --------------------------------------------------
        # IN-GAME EVENT HANDLING
        # --------------------------------------------------

        else:

            if event.type == pygame.MOUSEBUTTONDOWN:

                # -------------------------
                # GAME OVER BUTTONS
                # -------------------------

                if game.game_over:

                    if renderer.rematch_button.collidepoint(event.pos):

                        start_game()
                        continue

                    if renderer.menu_button.collidepoint(event.pos):

                        game = None
                        renderer = None
                        input_manager = None

                        menu_state.reset()

                        continue

                    # Ignore every other mouse click
                    # while the victory screen is active.
                    continue

                # -------------------------
                # NORMAL GAMEPLAY
                # -------------------------

                # Ignore human gameplay input while the AI controls the turn.
                ai_turn = (
                    game.ai_controller is not None
                    and game.current_player.team == game.ai_controller.team
                )

                if ai_turn:
                    continue

                if renderer.dice_button.collidepoint(event.pos):
                    game.roll_dice()
                    continue

                cell = input_manager.get_clicked_cell(event.pos)

                if cell is not None:
                    row, col = cell
                    game.handle_click(row, col)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:

                    ai_turn = (
                        game.ai_controller is not None
                        and game.current_player.team == game.ai_controller.team
                    )

                    if not game.game_over and not ai_turn:
                        game.roll_dice()

                elif event.key == pygame.K_ESCAPE:

                    game = None
                    renderer = None
                    input_manager = None

                    menu_state.reset()


    # --------------------------------------------------
    # UPDATE & RENDER
    # --------------------------------------------------

    if menu_state.current_state != MenuState.IN_GAME:

        menu_renderer.draw()

    else:

        # -------------------------
        # AI TURN
        # -------------------------

        if (
            game.ai_controller is not None
            and not game.game_over
            and game.current_player.team
            == game.ai_controller.team
        ):

            if (
                current_time - last_ai_step_time
                >= ai_turn_delay_ms
            ):

                game.step_ai()
                last_ai_step_time = current_time

        # -------------------------
        # DRAW GAME
        # -------------------------

        renderer.draw()


    pygame.display.flip()
    clock.tick(60)


pygame.quit()