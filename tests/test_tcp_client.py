import socket

from engine.protocol import Protocol
from network.tcp_client import TcpGameClient
from network.transport import JsonTransport


def test_client_defaults():
    client = TcpGameClient()

    assert client.host == "127.0.0.1"
    assert client.port == 5555
    assert client.socket is None
    assert client.buffer == b""


def test_client_accepts_custom_host_and_port():
    client = TcpGameClient(
        host="192.168.1.10",
        port=6000
    )

    assert client.host == "192.168.1.10"
    assert client.port == 6000


def test_send_message_without_connection_fails():
    client = TcpGameClient()

    assert not client.send_message(
        Protocol.roll()
    )


def test_receive_without_connection_returns_none():
    client = TcpGameClient()

    assert client.receive_message() is None


def test_send_message_uses_transport():
    client = TcpGameClient()

    client_side, server_side = (
        socket.socketpair()
    )

    try:
        client.socket = client_side

        assert client.send_message(
            Protocol.roll()
        )

        data = server_side.recv(
            4096
        )

        message = JsonTransport.decode(
            data
        )

        assert message == Protocol.roll()

    finally:
        client.disconnect()
        server_side.close()


def test_receive_message_decodes_response():
    client = TcpGameClient()

    client_side, server_side = (
        socket.socketpair()
    )

    try:
        client.socket = client_side

        response = Protocol.error(
            "Test response"
        )

        server_side.sendall(
            JsonTransport.encode(
                response
            )
        )

        received = client.receive_message()

        assert received == response

    finally:
        client.disconnect()
        server_side.close()


def test_receive_preserves_extra_message_in_buffer():
    client = TcpGameClient()

    client_side, server_side = (
        socket.socketpair()
    )

    try:
        client.socket = client_side

        first = Protocol.error(
            "First"
        )

        second = Protocol.error(
            "Second"
        )

        server_side.sendall(
            JsonTransport.encode(first)
            + JsonTransport.encode(second)
        )

        first_received = (
            client.receive_message()
        )

        second_received = (
            client.receive_message()
        )

        assert first_received == first
        assert second_received == second

    finally:
        client.disconnect()
        server_side.close()


def test_disconnect_clears_socket_and_buffer():
    client = TcpGameClient()

    client_side, server_side = (
        socket.socketpair()
    )

    try:
        client.socket = client_side
        client.buffer = b"test"

        client.disconnect()

        assert client.socket is None
        assert client.buffer == b""

    finally:
        server_side.close()