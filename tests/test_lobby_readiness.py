from engine.protocol import Protocol
from network.connection_router import ConnectionRouter


def setup_room():
    router = ConnectionRouter()
    code = router.handle_message("blue", Protocol.create_room())["data"]["room_code"]
    router.handle_message("red", Protocol.join_room(code))
    return router, code


def test_lobby_presence_and_readiness():
    router, _ = setup_room()
    state = router.handle_message("blue", Protocol.get_lobby())["data"]
    assert state["players"]["BLUE"]["connected"]
    assert state["players"]["RED"]["connected"]
    assert not state["started"]
    state = router.handle_message("blue", Protocol.set_ready(True))["data"]
    assert state["players"]["BLUE"]["ready"]
    assert not state["started"]
    state = router.handle_message("red", Protocol.set_ready(True))["data"]
    assert state["started"]
    assert router.handle_message("blue", Protocol.roll())["type"] == Protocol.GAME_STATE


def test_roll_blocked_until_both_ready():
    router, _ = setup_room()
    assert router.handle_message("blue", Protocol.roll())["type"] == Protocol.ERROR
    router.handle_message("blue", Protocol.set_ready(True))
    assert router.handle_message("blue", Protocol.roll())["type"] == Protocol.ERROR


def test_disconnect_updates_presence():
    router, _ = setup_room()
    router.remove_client("red")
    state = router.handle_message("blue", Protocol.get_lobby())["data"]
    assert not state["players"]["RED"]["connected"]
    assert not state["players"]["RED"]["ready"]


def test_bad_ready_value_rejected():
    router, _ = setup_room()
    assert router.handle_message("blue", Protocol.set_ready("yes"))["type"] == Protocol.ERROR
