from engine.protocol import Protocol
from network.game_session import GameSession


def started_session():
    session = GameSession()
    assert session.add_client('blue') == 'BLUE'
    assert session.add_client('red') == 'RED'
    session.handle_client_message('blue', Protocol.set_ready(True))
    session.handle_client_message('red', Protocol.set_ready(True))
    return session


def test_roll_event_shared_by_both_players():
    session = started_session()
    result = session.handle_client_message('blue', Protocol.roll())
    assert result['type'] == Protocol.GAME_STATE
    event = result['room_status']['last_event']
    assert event['type'] == 'ROLL'
    assert event['team'] == 'BLUE'
    assert event['value'] == session.game.dice.value
    other = session.handle_client_message('red', Protocol.get_state())
    assert other['room_status']['last_event'] == event


def test_invalid_action_does_not_publish_event():
    session = started_session()
    response = session.handle_client_message('red', Protocol.roll())
    assert response['type'] == Protocol.ERROR
    assert session.event_id == 0
    assert session.last_event is None


def test_move_event_only_after_accepted_move():
    session = started_session()
    session.handle_client_message('blue', Protocol.roll())
    old_id = session.event_id
    response = session.handle_client_message('blue', Protocol.move(-999, 5, 5))
    assert response['type'] == Protocol.ERROR
    assert session.event_id == old_id


def test_feedback_clears_on_rematch():
    session = started_session()
    session.handle_client_message('blue', Protocol.roll())
    session.game.game_over = True
    session.handle_client_message('blue', Protocol.set_rematch(True))
    session.handle_client_message('red', Protocol.set_rematch(True))
    assert session.event_id == 0
    assert session.last_event is None
    assert session.match_number == 2
