import socket

from engine.protocol import Protocol
from network.tcp_server import TcpGameServer
from network.transport import JsonTransport


class FakeRouter:
    def __init__(self):
        self.calls = []

    def handle_message(
        self,
        client_id,
        message
    ):
        self.calls.append(
            (client_id, message)
        )

        return Protocol.error(
            "Test response"
        )

    def remove_client(self, client_id):
        pass
        
def test_server_defaults():
    server = TcpGameServer()

    assert server.host == "127.0.0.1"
    assert server.port == 5555
    assert server.running is False
    assert server.server_socket is None


def test_server_accepts_custom_host_and_port():
    server = TcpGameServer(
        host="0.0.0.0",
        port=6000
    )

    assert server.host == "0.0.0.0"
    assert server.port == 6000


def test_server_accepts_custom_router():
    router = FakeRouter()

    server = TcpGameServer(
        router=router
    )

    assert server.router is router


def test_handle_client_routes_message():
    router = FakeRouter()

    server = TcpGameServer(
        router=router
    )

    server.running = True

    server_side, client_side = (
        socket.socketpair()
    )

    try:
        client_side.sendall(
            JsonTransport.encode(
                Protocol.roll()
            )
        )

        client_side.shutdown(
            socket.SHUT_WR
        )

        server._handle_client(
            server_side,
            "client-test"
        )

        assert len(router.calls) == 1

        client_id, message = (
            router.calls[0]
        )

        assert client_id == "client-test"
        assert message == Protocol.roll()

        response_data = client_side.recv(
            4096
        )

        response = JsonTransport.decode(
            response_data
        )

        assert response["type"] == Protocol.ERROR
        assert response["data"]["message"] == (
            "Test response"
        )

    finally:
        client_side.close()


def test_handle_client_rejects_invalid_json():
    router = FakeRouter()

    server = TcpGameServer(
        router=router
    )

    server.running = True

    server_side, client_side = (
        socket.socketpair()
    )

    try:
        client_side.sendall(
            b"not-json\n"
        )

        client_side.shutdown(
            socket.SHUT_WR
        )

        server._handle_client(
            server_side,
            "client-test"
        )

        assert router.calls == []

        response_data = client_side.recv(
            4096
        )

        response = JsonTransport.decode(
            response_data
        )

        assert response["type"] == Protocol.ERROR
        assert response["data"]["message"] == (
            "Invalid JSON message"
        )

    finally:
        client_side.close()


def test_handle_client_processes_multiple_messages():
    router = FakeRouter()

    server = TcpGameServer(
        router=router
    )

    server.running = True

    server_side, client_side = (
        socket.socketpair()
    )

    try:
        client_side.sendall(
            JsonTransport.encode(
                Protocol.roll()
            )
            + JsonTransport.encode(
                Protocol.create_room()
            )
        )

        client_side.shutdown(
            socket.SHUT_WR
        )

        server._handle_client(
            server_side,
            "client-test"
        )

        assert len(router.calls) == 2

        assert (
            router.calls[0][1]
            == Protocol.roll()
        )

        assert (
            router.calls[1][1]
            == Protocol.create_room()
        )

    finally:
        client_side.close()
    
class CleanupRouter(FakeRouter):
    def __init__(self):
        super().__init__()
        self.removed_clients = []

    def remove_client(self, client_id):
        self.removed_clients.append(
            client_id
        )


def test_handle_client_cleans_up_on_disconnect():
    router = CleanupRouter()

    server = TcpGameServer(
        router=router
    )

    server.running = True

    server_side, client_side = (
        socket.socketpair()
    )

    try:
        client_side.shutdown(
            socket.SHUT_WR
        )

        server._handle_client(
            server_side,
            "client-test"
        )

        assert router.removed_clients == [
            "client-test"
        ]

    finally:
        client_side.close()