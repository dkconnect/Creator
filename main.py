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

from network.multiplayer_client import MultiplayerClient
from network.client_game_adapter import ClientGameAdapter
from network.live_sync import LiveSync

from ui.multiplayer_hud import MultiplayerHUD


pygame.init()

WIDTH, HEIGHT = 1200, 900

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Creator")

menu_state = MenuState()
menu_renderer = MenuRenderer(screen, menu_state)

game = None
renderer = None
input_manager = None

multiplayer = None
network_game = None
network_renderer = None
network_input_manager = None
network_selected_pawn_id = None
network_sync = None

multiplayer_hud = MultiplayerHUD(screen)

clock = pygame.time.Clock()
running = True

ai_turn_delay_ms = 1500
last_ai_step_time = 0
last_lobby_poll = 0
lobby_poll_interval_ms = 500


def start_game():
    global game, renderer, input_manager, last_ai_step_time
    global network_game, network_renderer
    global network_input_manager, network_selected_pawn_id
    global network_sync

    network_game = None
    network_renderer = None
    network_input_manager = None
    network_selected_pawn_id = None
    network_sync = None

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


def start_network_game():
    global game, renderer, input_manager
    global network_game, network_renderer
    global network_input_manager, network_selected_pawn_id
    global network_sync

    if multiplayer is None:
        return False

    response = multiplayer.get_state()

    if (
        response is None
        or response.get("type") != "GAME_STATE"
    ):
        return False

    game = None
    renderer = None
    input_manager = None

    network_game = ClientGameAdapter(
        multiplayer.game_state
    )

    network_renderer = Renderer(
        screen,
        network_game
    )

    network_input_manager = InputManager(
        network_renderer
    )

    network_selected_pawn_id = None

    network_sync = LiveSync(
        multiplayer,
        network_game,
        interval_ms=500
    )

    menu_state.current_state = MenuState.IN_GAME

    return True


def refresh_network_game():
    global network_selected_pawn_id

    if network_game is None:
        return

    network_game.refresh()
    network_selected_pawn_id = None

    if network_sync is not None:
        network_sync.acknowledge_local_update()


def network_roll():

    if multiplayer is None or network_game is None:
        return False

    if network_game.game_over or (multiplayer.room_status or {}).get("paused"):
        return False

    if network_game.current_player is None:
        return False

    if network_game.current_player.team != multiplayer.team:
        return False

    if (
        multiplayer.game_state.turn_phase
        != "WAITING_FOR_ROLL"
    ):
        return False

    response = multiplayer.roll()

    if (
        response is None
        or response.get("type") != "GAME_STATE"
    ):
        return False

    refresh_network_game()

    return True


while running:

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif menu_state.current_state != MenuState.IN_GAME:

            if event.type == pygame.MOUSEBUTTONDOWN:

                pos = event.pos

                for btn_key, rect in menu_renderer.buttons.items():

                    if not rect.collidepoint(pos):
                        continue

                    if btn_key == "BACK":

                        if menu_state.current_state in (
                            MenuState.AI_DIFFICULTY,
                            MenuState.ROOM_CHOICE,
                            MenuState.LOBBY_WAITING,
                        ):

                            if multiplayer is not None:
                                multiplayer.disconnect()
                                multiplayer = None

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

                    elif btn_key.startswith("DIFF_"):

                        menu_state.selected_difficulty = (
                            btn_key.replace("DIFF_", "")
                        )

                        menu_state.current_state = (
                            MenuState.AI_PATTERN
                        )

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

                    elif btn_key.startswith("PATTERN_"):

                        menu_state.selected_pattern = (
                            btn_key.replace("PATTERN_", "")
                        )

                    elif btn_key == "CONFIRM_START":

                        if menu_state.selected_mode == "AI":

                            start_game()

                        elif (
                            menu_state.selected_mode == "ROOM"
                            and menu_state.room_action == "CREATE"
                        ):

                            multiplayer = MultiplayerClient()

                            if multiplayer.connect():

                                response = multiplayer.create_room()

                                if (
                                    response is not None
                                    and response.get("type")
                                    == "ROOM_JOINED"
                                ):

                                    menu_state.room_code_input = (
                                        multiplayer.room_code
                                    )

                                    menu_state.current_state = (
                                        MenuState.LOBBY_WAITING
                                    )

                                else:
                                    multiplayer.disconnect()
                                    multiplayer = None

                        else:
                            menu_state.current_state = (
                                MenuState.LOBBY_WAITING
                            )

                    elif btn_key == "SUBMIT_JOIN":

                        if len(menu_state.room_code_input) == 6:

                            multiplayer = MultiplayerClient()

                            if multiplayer.connect():

                                response = multiplayer.join_room(
                                    menu_state.room_code_input
                                )

                                if (
                                    response is not None
                                    and response.get("type")
                                    == "ROOM_JOINED"
                                ):

                                    menu_state.room_code_input = (
                                        multiplayer.room_code
                                    )

                                    menu_state.current_state = (
                                        MenuState.LOBBY_WAITING
                                    )

                                else:
                                    multiplayer.disconnect()
                                    multiplayer = None

                    elif btn_key == "TOGGLE_READY":
                        if multiplayer is not None and multiplayer.lobby_state:
                            team_info = multiplayer.lobby_state["players"][multiplayer.team]
                            response = multiplayer.set_ready(not team_info["ready"])
                            if response and response.get("type") == "LOBBY_STATE":
                                menu_state.lobby_data = multiplayer.lobby_state

                    elif btn_key == "LAUNCH_GAME":

                        if (
                            menu_state.selected_mode == "ROOM"
                            and multiplayer is not None
                        ):
                            start_network_game()

                        else:
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

        else:

            # -----------------------------------------
            # NETWORK GAMEPLAY
            # -----------------------------------------

            if network_game is not None:

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if network_game.game_over or (multiplayer.room_status or {}).get("paused"):
                        continue

                    if (
                        network_game.current_player is None
                        or network_game.current_player.team
                        != multiplayer.team
                    ):
                        continue

                    phase = multiplayer.game_state.turn_phase

                    if (
                        phase == "WAITING_FOR_ROLL"
                        and network_renderer.dice_button.collidepoint(
                            event.pos
                        )
                    ):
                        network_roll()
                        continue

                    cell = network_input_manager.get_clicked_cell(
                        event.pos
                    )

                    if cell is None:
                        continue

                    row, col = cell

                    if phase not in (
                        "WAITING_FOR_SELECTION",
                        "WAITING_FOR_MOVE",
                    ):
                        continue

                    clicked_pawn = network_game.board.get_pawn(
                        row,
                        col
                    )

                    if (
                        clicked_pawn is not None
                        and clicked_pawn.team == multiplayer.team
                        and clicked_pawn.active
                    ):

                        network_selected_pawn_id = clicked_pawn.id
                        network_game.selected_pawn = clicked_pawn

                        continue

                    if network_selected_pawn_id is not None:

                        if (
                            row,
                            col
                        ) in network_game.get_valid_moves():

                            response = multiplayer.move(
                                pawn_id=network_selected_pawn_id,
                                row=row,
                                col=col
                            )

                            if (
                                response is not None
                                and response.get("type")
                                == "GAME_STATE"
                            ):
                                refresh_network_game()

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:
                        network_roll()

                    elif event.key == pygame.K_r:

                        if network_sync.poll(force=True):
                            network_selected_pawn_id = None

                continue

            # -----------------------------------------
            # LOCAL / AI GAMEPLAY
            # -----------------------------------------

            if event.type == pygame.MOUSEBUTTONDOWN:

                if game.game_over:

                    if renderer.rematch_button.collidepoint(
                        event.pos
                    ):
                        start_game()
                        continue

                    if renderer.menu_button.collidepoint(
                        event.pos
                    ):

                        game = None
                        renderer = None
                        input_manager = None

                        menu_state.reset()
                        continue

                    continue

                ai_turn = (
                    game.ai_controller is not None
                    and game.current_player.team
                    == game.ai_controller.team
                )

                if ai_turn:
                    continue

                if renderer.dice_button.collidepoint(
                    event.pos
                ):

                    game.roll_dice()
                    continue

                cell = input_manager.get_clicked_cell(
                    event.pos
                )

                if cell is not None:

                    row, col = cell
                    game.handle_click(row, col)

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    ai_turn = (
                        game.ai_controller is not None
                        and game.current_player.team
                        == game.ai_controller.team
                    )

                    if not game.game_over and not ai_turn:
                        game.roll_dice()

                elif event.key == pygame.K_ESCAPE:

                    game = None
                    renderer = None
                    input_manager = None

                    menu_state.reset()

    # -----------------------------------------
    # RENDERING
    # -----------------------------------------

    if (
        menu_state.current_state == MenuState.LOBBY_WAITING
        and menu_state.selected_mode == "ROOM"
        and multiplayer is not None
        and current_time - last_lobby_poll >= lobby_poll_interval_ms
    ):
        last_lobby_poll = current_time
        try:
            response = multiplayer.get_lobby()
            if response and response.get("type") == "LOBBY_STATE":
                menu_state.lobby_data = multiplayer.lobby_state
                menu_state.lobby_team = multiplayer.team
                if multiplayer.lobby_state.get("started"):
                    start_network_game()
        except (OSError, ConnectionError, TimeoutError):
            pass

    if menu_state.current_state != MenuState.IN_GAME:

        menu_renderer.draw()

    else:

        if network_game is not None:

            if network_sync is not None:

                changed = network_sync.poll()

                if changed:
                    network_selected_pawn_id = None

            network_renderer.draw()

            multiplayer_hud.draw(
                multiplayer,
                network_game,
                network_sync
            )

        else:

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

            renderer.draw()

    pygame.display.flip()
    clock.tick(60)


if multiplayer is not None:
    multiplayer.disconnect()

pygame.quit()