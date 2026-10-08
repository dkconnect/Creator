import socket

from engine.protocol import Protocol
from network.connection_router import ConnectionRouter
from network.tcp_client import TcpGameClient
from network.transport import JsonTransport


def test_invalid_utf8_returns_none():
    assert JsonTransport.decode(b'\xff\xfe') is None


def test_router_rejects_non_dictionary_payload():
    result = ConnectionRouter().handle_message('guest', {
        'version': Protocol.VERSION, 'type': Protocol.JOIN_ROOM, 'data': []
    })
    assert result['type'] == Protocol.ERROR


def test_client_timeout_disconnects_without_hanging():
    left, right = socket.socketpair()
    client = TcpGameClient(timeout=0.01)
    client.socket = left
    left.settimeout(0.01)
    try:
        assert client.receive_message() is None
        assert client.socket is None
    finally:
        right.close()


def test_client_rejects_oversized_response():
    left, right = socket.socketpair()
    client = TcpGameClient(max_message_bytes=16)
    client.socket = left
    right.sendall(b'{"long":"' + b'x' * 40 + b'"}\n')
    try:
        assert client.receive_message() is None
        assert client.socket is None
    finally:
        right.close()
