from dataclasses import dataclass, field
from engine.pawn import Pawn


@dataclass
class Player:
    team: str
    pawns: list[Pawn] = field(default_factory=list)
    captures_suffered: int = 0
    respawns: int = 0
