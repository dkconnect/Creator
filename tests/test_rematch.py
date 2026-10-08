from engine.protocol import Protocol
from network.connection_router import ConnectionRouter


def completed_room():
    router = ConnectionRouter()
    code = router.handle_message("blue", Protocol.create_room())["data"]["room_code"]
    router.handle_message("red", Protocol.join_room(code))
    router.handle_message("blue", Protocol.set_ready(True))
    router.handle_message("red", Protocol.set_ready(True))
    session = router.room_manager.get_room(code)
    session.game.game_over = True
    session.game.winner = session.game.blue
    return router, code, session


def test_rematch_requires_completed_game():
    router, code, session = completed_room()
    session.game.game_over = False
    assert router.handle_message("blue", Protocol.set_rematch(True))["type"] == Protocol.ERROR


def test_one_vote_preserves_completed_match():
    router, code, session = completed_room()
    original = session.game
    response = router.handle_message("blue", Protocol.set_rematch(True))
    assert response["data"]["rematch"] == {"BLUE": True, "RED": False}
    assert session.game is original


def test_two_votes_start_fresh_game():
    router, code, session = completed_room()
    original = session.game
    router.handle_message("blue", Protocol.set_rematch(True))
    response = router.handle_message("red", Protocol.set_rematch(True))
    assert session.game is not original
    assert not session.game.game_over
    assert session.game.turn_phase == "WAITING_FOR_ROLL"
    assert session.match_number == 2
    assert response["data"]["rematch"] == {"BLUE": False, "RED": False}
    assert router.handle_message("blue", Protocol.get_state())["data"]["game_over"] is False


def test_vote_can_be_cancelled():
    router, code, session = completed_room()
    router.handle_message("blue", Protocol.set_rematch(True))
    response = router.handle_message("blue", Protocol.set_rematch(False))
    assert response["data"]["rematch"]["BLUE"] is False


def test_rematch_rejects_invalid_vote():
    router, code, session = completed_room()
    assert router.handle_message("blue", Protocol.set_rematch("yes"))["type"] == Protocol.ERROR


def test_rematch_paused_until_reconnect():
    router, code, session = completed_room()
    router.remove_client("red")
    assert router.handle_message("blue", Protocol.set_rematch(True))["type"] == Protocol.ERROR
