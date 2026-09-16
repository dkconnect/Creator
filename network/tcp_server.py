import socket
import threading
import uuid

from engine.protocol import Protocol
from network.connection_router import ConnectionRouter
from network.transport import JsonTransport


class TcpGameServer:
    def __init__(
        self,
        host="127.0.0.1",
        port=5555,
        router=None
    ):
        self.host = host
        self.port = port

        self.router = (
            router
            if router is not None
            else ConnectionRouter()
        )

        self.server_socket = None
        self.running = False

    def start(self):
        """
        Start accepting TCP connections.
        """

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server_socket.bind(
            (self.host, self.port)
        )

        self.server_socket.listen()

        self.running = True

        while self.running:
            try:
                client_socket, _ = (
                    self.server_socket.accept()
                )
            except OSError:
                break

            client_id = uuid.uuid4().hex

            thread = threading.Thread(
                target=self._handle_client,
                args=(
                    client_socket,
                    client_id,
                ),
                daemon=True
            )

            thread.start()

    def stop(self):
        """
        Stop accepting new connections.
        """

        self.running = False

        if self.server_socket is not None:
            try:
                self.server_socket.close()
            except OSError:
                pass

            self.server_socket = None

    def _handle_client(
        self,
        client_socket,
        client_id
    ):
        """
        Receive newline-delimited JSON messages from
        one connected client.
        """

        buffer = b""

        try:
            while self.running:
                data = client_socket.recv(
                    4096
                )

                if not data:
                    break

                buffer += data

                while b"\n" in buffer:
                    line, buffer = buffer.split(
                        b"\n",
                        1
                    )

                    message = JsonTransport.decode(
                        line
                    )

                    if message is None:
                        response = Protocol.error(
                            "Invalid JSON message"
                        )
                    else:
                        response = (
                            self.router.handle_message(
                                client_id,
                                message
                            )
                        )

                    client_socket.sendall(
                        JsonTransport.encode(
                            response
                        )
                    )

        except (
            ConnectionError,
            OSError
        ):
            pass

        finally:
            try:
                client_socket.close()
            except OSError:
                pass