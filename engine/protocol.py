class Protocol:
    VERSION = 1

    MOVE = "MOVE"
    ROLL = "ROLL"
    CREATE_ROOM = "CREATE_ROOM"
    JOIN_ROOM = "JOIN_ROOM"
    ROOM_JOINED = "ROOM_JOINED"
    GAME_STATE = "GAME_STATE"
    GET_STATE = "GET_STATE"
    GET_LOBBY = "GET_LOBBY"
    SET_READY = "SET_READY"
    REJOIN_ROOM = "REJOIN_ROOM"
    LOBBY_STATE = "LOBBY_STATE"
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
    def rejoin_room(cls, room_code, reconnect_token):
        return {"version": cls.VERSION, "type": cls.REJOIN_ROOM,
                "data": {"room_code": room_code, "reconnect_token": reconnect_token}}

    @classmethod
    def room_joined(cls, room_code, team, reconnect_token=None):
        return {
            "version": cls.VERSION,
            "type": cls.ROOM_JOINED,
            "data": {
                "room_code": room_code,
                "team": team,
                **({"reconnect_token": reconnect_token} if reconnect_token else {}),
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
    def get_lobby(cls):
        return {"version": cls.VERSION, "type": cls.GET_LOBBY, "data": {}}

    @classmethod
    def set_ready(cls, ready):
        return {"version": cls.VERSION, "type": cls.SET_READY, "data": {"ready": ready}}

    @classmethod
    def lobby_state(cls, state):
        return {"version": cls.VERSION, "type": cls.LOBBY_STATE, "data": state}

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
            cls.GET_LOBBY,
            cls.SET_READY,
            cls.REJOIN_ROOM,
            cls.LOBBY_STATE,
            cls.ERROR,
        ):
            return False

        if not isinstance(message.get("data"), dict):
            return False

        return True