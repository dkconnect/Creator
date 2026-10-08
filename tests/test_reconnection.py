from engine.protocol import Protocol
from network.connection_router import ConnectionRouter


def started_room():
    router = ConnectionRouter()
    created = router.handle_message('blue-old', Protocol.create_room())
    code = created['data']['room_code']
    blue_token = created['data']['reconnect_token']
    joined = router.handle_message('red-old', Protocol.join_room(code))
    red_token = joined['data']['reconnect_token']
    assert blue_token != red_token
    router.handle_message('blue-old', Protocol.set_ready(True))
    router.handle_message('red-old', Protocol.set_ready(True))
    return router, code, blue_token, red_token


def test_disconnect_pauses_and_reconnect_resumes_same_game():
    router, code, blue_token, _ = started_room()
    session = router.room_manager.get_room(code)
    original_game = session.game
    assert router.remove_client('blue-old') == 'BLUE'
    status = router.handle_message('red-old', Protocol.get_state())
    assert status['room_status']['paused'] is True
    assert not status['room_status']['players']['BLUE']['connected']
    assert router.handle_message('red-old', Protocol.roll())['type'] == Protocol.ERROR
    restored = router.handle_message('blue-new', Protocol.rejoin_room(code, blue_token))
    assert restored['type'] == Protocol.ROOM_JOINED
    assert restored['data']['team'] == 'BLUE'
    assert session.game is original_game
    assert router.handle_message('red-old', Protocol.get_state())['room_status']['paused'] is False
    assert router.handle_message('blue-new', Protocol.roll())['type'] == Protocol.GAME_STATE


def test_wrong_token_cannot_steal_team():
    router, code, _, _ = started_room()
    router.remove_client('red-old')
    assert router.handle_message('attacker', Protocol.rejoin_room(code, 'invalid'))['type'] == Protocol.ERROR
    assert router.handle_message('attacker', Protocol.join_room(code))['type'] == Protocol.ERROR
    assert router.room_manager.get_room(code).paused


def test_rejoin_token_cannot_replace_connected_player():
    router, code, token, _ = started_room()
    assert router.handle_message('other', Protocol.rejoin_room(code, token))['type'] == Protocol.ERROR


def test_lobby_disconnect_still_releases_slot():
    router = ConnectionRouter()
    code = router.handle_message('blue', Protocol.create_room())['data']['room_code']
    router.remove_client('blue')
    joined = router.handle_message('new', Protocol.join_room(code))
    assert joined['data']['team'] == 'BLUE'


def test_reconnect_token_not_in_public_lobby_or_game_state():
    router, code, token, _ = started_room()
    lobby = router.handle_message('blue-old', Protocol.get_lobby())
    game = router.handle_message('blue-old', Protocol.get_state())
    assert token not in str(lobby)
    assert token not in str(game)
