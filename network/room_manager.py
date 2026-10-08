import random
import string

from network.game_session import GameSession


class RoomManager:
    ROOM_CODE_LENGTH = 6

    def __init__(self):
        self.rooms = {}

    def _generate_room_code(self):
        """
        Generate a unique 6-character room code.
        """

        while True:
            code = "".join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=self.ROOM_CODE_LENGTH,
                )
            )

            if code not in self.rooms:
                return code

    def create_room(self, client_id):
        """
        Create a new room and assign the creator to BLUE.

        Returns:
            (room_code, team)
        """

        room_code = self._generate_room_code()

        session = GameSession()

        team = session.add_client(
            client_id
        )

        self.rooms[room_code] = session

        return room_code, team

    def join_room(self, room_code, client_id):
        """
        Join an existing room.

        Returns:
            assigned team on success.
            None if the room does not exist or is full.
        """

        room_code = room_code.upper()

        session = self.rooms.get(
            room_code
        )

        if session is None:
            return None

        return session.add_client(
            client_id
        )

    def get_room(self, room_code):
        return self.rooms.get(
            room_code.upper()
        )
        
    def handle_client_message(
        self,
        room_code,
        client_id,
        message
    ):
        """
        Route a client message to the correct room session.
        """

        session = self.get_room(
            room_code
        )

        if session is None:
            return None

        return session.handle_client_message(
            client_id,
            message
        )

    def remove_client(self, room_code, client_id):
        session = self.get_room(
            room_code
        )

        if session is None:
            return None

        return session.remove_client(
            client_id
        )

    def delete_room(self, room_code):
        room_code = room_code.upper()

        if room_code not in self.rooms:
            return False

        del self.rooms[room_code]

        return True