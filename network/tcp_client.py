import socket

from network.transport import JsonTransport


class TcpGameClient:
    def __init__(
        self,
        host="127.0.0.1",
        port=5555
    ):
        self.host = host
        self.port = port

        self.socket = None
        self.buffer = b""

    def connect(self):
        """
        Connect to the game server.
        """

        if self.socket is not None:
            return False

        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            client_socket.connect(
                (self.host, self.port)
            )
        except OSError:
            client_socket.close()
            return False

        self.socket = client_socket
        self.buffer = b""

        return True

    def disconnect(self):
        """
        Close the server connection.
        """

        if self.socket is None:
            return

        try:
            self.socket.close()
        except OSError:
            pass

        self.socket = None
        self.buffer = b""

    def send_message(self, message):
        """
        Send one protocol message.
        """

        if self.socket is None:
            return False

        try:
            self.socket.sendall(
                JsonTransport.encode(
                    message
                )
            )
        except (
            ConnectionError,
            OSError
        ):
            self.disconnect()
            return False

        return True

    def receive_message(self):
        """
        Wait for and return one complete protocol message.
        """

        if self.socket is None:
            return None

        while b"\n" not in self.buffer:
            try:
                data = self.socket.recv(
                    4096
                )
            except (
                ConnectionError,
                OSError
            ):
                self.disconnect()
                return None

            if not data:
                self.disconnect()
                return None

            self.buffer += data

        line, self.buffer = self.buffer.split(
            b"\n",
            1
        )

        return JsonTransport.decode(
            line
        )

    def request(self, message):
        """
        Send one message and wait for one response.
        """

        if not self.send_message(message):
            return None

        return self.receive_message()