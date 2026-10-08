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
        self.status_message = ""
        self.show_help = False
        self.selected_mode = None          # "ONLINE", "AI", "ROOM"
        self.selected_difficulty = None    # "EASY", "LEARNING", "ADVANCED"
        self.selected_pattern = None       # filename string, e.g. "A.json"
        self.room_action = None            # "CREATE", "JOIN"
        self.lobby_data = None
        self.lobby_team = None
        self.room_code_input = ""          # for Join Room
        self.generated_room_code = "849201"  # mock room code for local lobby

        self.pattern_category = "LETTERS"
        self.pattern_page = 0
        self.available_patterns = self._load_available_patterns()
        if self.available_patterns:
            self.selected_pattern = self.available_patterns[0]

    def _load_available_patterns(self):
        base_dir = Path(__file__).resolve().parent.parent
        pattern_folder = base_dir / "patterns"
        pattern_files = list(pattern_folder.glob("*.json"))
        return sorted((f.name for f in pattern_files), key=self._pattern_sort_key) if pattern_files else ["default.json"]

    @staticmethod
    def pattern_category_for(filename):
        prefix = filename.split("_", 1)[0].lower()
        return {"letter": "LETTERS", "number": "NUMBERS",
                "symbol": "SYMBOLS", "shape": "SHAPES"}.get(prefix, "SHAPES")

    @staticmethod
    def pattern_label(filename):
        name = filename.removesuffix(".json")
        return name.split("_", 1)[-1].replace("_", " ")

    @classmethod
    def _pattern_sort_key(cls, filename):
        order = {"LETTERS": 0, "NUMBERS": 1, "SYMBOLS": 2, "SHAPES": 3}
        return (order[cls.pattern_category_for(filename)], filename)

    def reset(self):
        self.current_state = self.MODE_SELECT
        self.status_message = ""
        self.show_help = False
        self.selected_mode = None
        self.selected_difficulty = None
        self.room_action = None
        self.lobby_data = None
        self.lobby_team = None
        self.room_code_input = ""