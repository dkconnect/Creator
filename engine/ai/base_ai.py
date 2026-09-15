from abc import ABC, abstractmethod
from typing import Optional, Tuple
from engine.pawn import Pawn


class BaseAI(ABC):
    """
    Abstract Base Class for all AI controllers.
    """
    def __init__(self, team: str = "RED"):
        self.team = team

    @abstractmethod
    def select_move(self, game) -> Optional[Tuple[Pawn, int, int]]:
        """
        Analyzes the current board state and dice roll.
        
        Returns:
            A tuple of (selected_pawn, target_row, target_col) to execute,
            or None if no legal moves are available.
        """
        pass