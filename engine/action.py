from dataclasses import dataclass

@dataclass(frozen=True)
class GameAction:
    action_type: str
    pawn_id: int
    row: int
    col: int

    MOVE = "MOVE"

    @classmethod
    def move(cls, pawn_id, row, col):
        return cls(
            action_type=cls.MOVE,
            pawn_id=pawn_id,
            row=row,
            col=col,
        )

    def to_dict(self):
        return {
            "type": self.action_type,
            "pawn_id": self.pawn_id,
            "row": self.row,
            "col": self.col,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            action_type=data["type"],
            pawn_id=data["pawn_id"],
            row=data["row"],
            col=data["col"],
        )