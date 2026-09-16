class Protocol:
    VERSION = 1

    MOVE = "MOVE"
    GAME_STATE = "GAME_STATE"
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
    def game_state(cls, game):
        return {
            "version": cls.VERSION,
            "type": cls.GAME_STATE,
            "data": game.to_dict(),
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
            cls.GAME_STATE,
            cls.ERROR,
        ):
            return False

        if not isinstance(message.get("data"), dict):
            return False

        return True