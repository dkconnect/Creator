from pathlib import Path
import json


class MenuState:
    # State constants
    MODE_SELECT = "MODE_SELECT"
    AI_DIFFICULTY = "AI_DIFFICULTY"
    AI_PATTERN = "AI_PATTERN"
    ROOM_CHOICE = "ROOM_CHOICE"
    ROOM_PATTERN = "ROOM_PATTERN"
    ROOM_JOIN = "ROOM_JOIN"
    LOBBY_WAITING = "LOBBY_WAITING"
    IN_GAME = "IN_GAME"

    def __init__(self):
        self.current_state = self.MODE_SELECT
        self.selected_mode = None          # "ONLINE", "AI", "ROOM"
        self.selected_difficulty = None    # "EASY", "LEARNING", "ADVANCED"
        self.selected_pattern = None       # filename string, e.g. "A.json"
        self.room_action = None            # "CREATE", "JOIN"
        self.lobby_data = None
        self.lobby_team = None
        self.room_code_input = ""          # for Join Room
        self.generated_room_code = "849201"  # mock room code for local lobby

        self.available_patterns = self._load_available_patterns()
        if self.available_patterns:
            self.selected_pattern = self.available_patterns[0]

    def _load_available_patterns(self):
        base_dir = Path(__file__).resolve().parent.parent
        pattern_folder = base_dir / "patterns"
        pattern_files = list(pattern_folder.glob("*.json"))
        return [f.name for f in pattern_files] if pattern_files else ["default.json"]

    def reset(self):
        self.current_state = self.MODE_SELECT
        self.selected_mode = None
        self.selected_difficulty = None
        self.room_action = None
        self.lobby_data = None
        self.lobby_team = None
        self.room_code_input = ""