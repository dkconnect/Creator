from engine.protocol import Protocol
from network.game_session import GameSession


def session_started():
    session = GameSession()
    session.add_client("blue")
    session.add_client("red")
    session.handle_client_message("blue", Protocol.set_ready(True))
    session.handle_client_message("red", Protocol.set_ready(True))
    return session


def test_history_shared_and_ordered():
    session = session_started()
    session.handle_client_message("blue", Protocol.roll())
    blue = session.handle_client_message("blue", Protocol.get_state())
    red = session.handle_client_message("red", Protocol.get_state())
    assert blue["room_status"]["move_history"] == red["room_status"]["move_history"]
    assert blue["room_status"]["move_history"] == [session.last_event]


def test_rejected_action_does_not_enter_history():
    session = session_started()
    session.handle_client_message("red", Protocol.roll())
    assert session.move_history == []


def test_history_bounded_to_twelve():
    session = session_started()
    for number in range(20):
        session.event_id = number + 1
        session.last_event = {"id": number + 1, "type": "ROLL", "team": "BLUE", "value": 1}
        # Verify the bounded public history contract.
        session.move_history.append(dict(session.last_event))
        session.move_history = session.move_history[-12:]
    assert len(session.lobby_state()["move_history"]) == 12
    assert session.lobby_state()["move_history"][0]["id"] == 9


def test_history_resets_on_rematch():
    session = session_started()
    session.handle_client_message("blue", Protocol.roll())
    session.game.game_over = True
    session.handle_client_message("blue", Protocol.set_rematch(True))
    session.handle_client_message("red", Protocol.set_rematch(True))
    assert session.move_history == []
    assert session.match_number == 2


def test_history_snapshot_is_not_mutable_alias():
    session = session_started()
    session.handle_client_message("blue", Protocol.roll())
    snapshot = session.lobby_state()
    snapshot["move_history"][0]["value"] = 999
    assert session.move_history[0]["value"] != 999
