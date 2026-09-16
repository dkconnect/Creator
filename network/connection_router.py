from engine.protocol import Protocol
from network.room_manager import RoomManager


class ConnectionRouter:
    def __init__(self, room_manager=None):
        self.room_manager = (
            room_manager
            if room_manager is not None
            else RoomManager()
        )

        self.client_rooms = {}

    def handle_message(self, client_id, message):
        """
        Route a protocol message from a connected client.
        """

        if not Protocol.is_valid(message):
            return Protocol.error(
                "Invalid protocol message"
            )

        message_type = message["type"]

        if message_type == Protocol.CREATE_ROOM:
            return self._handle_create_room(
                client_id
            )

        if message_type == Protocol.JOIN_ROOM:
            return self._handle_join_room(
                client_id,
                message["data"]
            )

        room_code = self.client_rooms.get(
            client_id
        )

        if room_code is None:
            return Protocol.error(
                "Client is not in a room"
            )

        response = (
            self.room_manager.handle_client_message(
                room_code,
                client_id,
                message
            )
        )

        if response is None:
            return Protocol.error(
                "Room not found"
            )

        return response

    def _handle_create_room(self, client_id):
        if client_id in self.client_rooms:
            return Protocol.error(
                "Client is already in a room"
            )

        room_code, team = (
            self.room_manager.create_room(
                client_id
            )
        )

        self.client_rooms[client_id] = room_code

        return Protocol.room_joined(
            room_code,
            team
        )

    def _handle_join_room(self, client_id, data):
        if client_id in self.client_rooms:
            return Protocol.error(
                "Client is already in a room"
            )

        room_code = data.get(
            "room_code"
        )

        if not isinstance(room_code, str):
            return Protocol.error(
                "Invalid room code"
            )

        room_code = room_code.upper()

        team = self.room_manager.join_room(
            room_code,
            client_id
        )

        if team is None:
            return Protocol.error(
                "Unable to join room"
            )

        self.client_rooms[client_id] = room_code

        return Protocol.room_joined(
            room_code,
            team
        )