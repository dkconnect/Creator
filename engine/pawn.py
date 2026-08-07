from dataclasses import dataclass


@dataclass
class Pawn:
    id: int
    team: str
    row: int
    col: int
    active: bool = True
