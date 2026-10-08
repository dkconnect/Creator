import json


class JsonTransport:
    @staticmethod
    def encode(message):
        """
        Encode one protocol message as newline-delimited JSON.
        """

        data = json.dumps(
            message,
            separators=(",", ":")
        )

        return (data + "\n").encode("utf-8")

    @staticmethod
    def decode(data):
        """
        Decode one complete JSON message.

        Accepts bytes or string data.
        """

        if isinstance(data, bytes):
            data = data.decode("utf-8")

        data = data.strip()

        if not data:
            return None

        try:
            message = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

        if not isinstance(message, dict):
            return None

        return message