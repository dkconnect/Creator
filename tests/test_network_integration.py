import threading
import time

from engine.protocol import Protocol
from network.tcp_client import TcpGameClient
from network.tcp_server import TcpGameServer


def start_test_server():
    server = TcpGameServer(
        host="127.0.0.1",
        port=0
    )

    thread = threading.Thread(
        target=server.start,
        daemon=True
    )

    thread.start()

    timeout = time.time() + 2

    while (
        server.server_socket is None
        or not server.running
    ):
        if time.time() > timeout:
            raise AssertionError(
                "Server failed to start"
            )

        time.sleep(0.01)

    port = server.server_socket.getsockname()[1]

    return server, thread, port


def test_real_client_can_create_room():
    server, thread, port = start_test_server()

    client = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    try:
        assert client.connect()

        response = client.request(
            Protocol.create_room()
        )

        assert response["type"] == Protocol.ROOM_JOINED
        assert response["data"]["team"] == "BLUE"
        assert len(response["data"]["room_code"]) == 6

    finally:
        client.disconnect()
        server.stop()

        thread.join(timeout=1)


def test_two_real_clients_can_join_same_room():
    server, thread, port = start_test_server()

    blue = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    red = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    try:
        assert blue.connect()
        assert red.connect()

        create_response = blue.request(
            Protocol.create_room()
        )

        room_code = (
            create_response["data"]["room_code"]
        )

        join_response = red.request(
            Protocol.join_room(room_code)
        )

        assert create_response["data"]["team"] == "BLUE"

        assert join_response["type"] == Protocol.ROOM_JOINED
        assert join_response["data"]["room_code"] == room_code
        assert join_response["data"]["team"] == "RED"

    finally:
        blue.disconnect()
        red.disconnect()

        server.stop()

        thread.join(timeout=1)


def test_blue_can_roll_over_real_tcp():
    server, thread, port = start_test_server()

    blue = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    red = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    try:
        assert blue.connect()
        assert red.connect()

        create_response = blue.request(
            Protocol.create_room()
        )

        room_code = (
            create_response["data"]["room_code"]
        )

        red.request(
            Protocol.join_room(room_code)
        )

        response = blue.request(
            Protocol.roll()
        )

        assert response["type"] == Protocol.GAME_STATE
        assert response["data"]["dice"] is not None

    finally:
        blue.disconnect()
        red.disconnect()

        server.stop()

        thread.join(timeout=1)


def test_red_cannot_roll_during_blue_turn_over_tcp():
    server, thread, port = start_test_server()

    blue = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    red = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    try:
        assert blue.connect()
        assert red.connect()

        create_response = blue.request(
            Protocol.create_room()
        )

        room_code = (
            create_response["data"]["room_code"]
        )

        red.request(
            Protocol.join_room(room_code)
        )

        response = red.request(
            Protocol.roll()
        )

        assert response["type"] == Protocol.ERROR
        assert response["data"]["message"] == (
            "Not your turn"
        )

    finally:
        blue.disconnect()
        red.disconnect()

        server.stop()

        thread.join(timeout=1)

def test_new_client_can_replace_disconnected_red_player():
    server, thread, port = start_test_server()

    blue = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    red = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    replacement = TcpGameClient(
        host="127.0.0.1",
        port=port
    )

    try:
        assert blue.connect()
        assert red.connect()

        create_response = blue.request(
            Protocol.create_room()
        )

        room_code = (
            create_response["data"]["room_code"]
        )

        join_response = red.request(
            Protocol.join_room(room_code)
        )

        assert join_response["data"]["team"] == "RED"

        # Disconnect RED.
        red.disconnect()

        # Give the server thread a moment to process
        # the closed connection and release the slot.
        timeout = time.time() + 2

        while time.time() < timeout:
            session = (
                server.router.room_manager.get_room(
                    room_code
                )
            )

            if session.red_client is None:
                break

            time.sleep(0.01)

        session = (
            server.router.room_manager.get_room(
                room_code
            )
        )

        assert session.red_client is None

        # A new connection should now be able
        # to take the released RED slot.
        assert replacement.connect()

        replacement_response = (
            replacement.request(
                Protocol.join_room(room_code)
            )
        )

        assert (
            replacement_response["type"]
            == Protocol.ROOM_JOINED
        )

        assert (
            replacement_response["data"]["room_code"]
            == room_code
        )

        assert (
            replacement_response["data"]["team"]
            == "RED"
        )

    finally:
        blue.disconnect()
        red.disconnect()
        replacement.disconnect()

        server.stop()

        thread.join(timeout=1)