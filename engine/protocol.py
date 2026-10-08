class Protocol:
    VERSION = 1

    MOVE = "MOVE"
    ROLL = "ROLL"
    CREATE_ROOM = "CREATE_ROOM"
    JOIN_ROOM = "JOIN_ROOM"
    ROOM_JOINED = "ROOM_JOINED"
    GAME_STATE = "GAME_STATE"
    GET_STATE = "GET_STATE"
    ERROR = "ERROR"

    @classmethod
    def move(cls, pawn_id, row, col):
        return {
            "version": cls.VERSION,
            "type": cls.MOVE,
            "data": {
                "pawn_id": pawn_id,
                "row": row,
                "col": col,
            },
        }

    @classmethod
    def roll(cls):
        return {
            "version": cls.VERSION,
            "type": cls.ROLL,
            "data": {},
        }

    @classmethod
    def create_room(cls):
        return {
            "version": cls.VERSION,
            "type": cls.CREATE_ROOM,
            "data": {},
        }

    @classmethod
    def join_room(cls, room_code):
        return {
            "version": cls.VERSION,
            "type": cls.JOIN_ROOM,
            "data": {
                "room_code": room_code,
            },
        }

    @classmethod
    def room_joined(cls, room_code, team):
        return {
            "version": cls.VERSION,
            "type": cls.ROOM_JOINED,
            "data": {
                "room_code": room_code,
                "team": team,
            },
        }

    @classmethod
    def game_state(cls, game):
        return {
            "version": cls.VERSION,
            "type": cls.GAME_STATE,
            "data": game.to_dict(),
        }

    @classmethod
    def get_state(cls):
        return {
            "version": cls.VERSION,
            "type": cls.GET_STATE,
            "data": {},
        }

    @classmethod
    def error(cls, message):
        return {
            "version": cls.VERSION,
            "type": cls.ERROR,
            "data": {
                "message": message,
            },
        }

    @classmethod
    def is_valid(cls, message):
        if not isinstance(message, dict):
            return False

        if message.get("version") != cls.VERSION:
            return False

        if message.get("type") not in (
            cls.MOVE,
            cls.ROLL,
            cls.CREATE_ROOM,
            cls.JOIN_ROOM,
            cls.ROOM_JOINED,
            cls.GAME_STATE,
            cls.GET_STATE,
            cls.ERROR,
        ):
            return False

        if not isinstance(message.get("data"), dict):
            return False

        return True