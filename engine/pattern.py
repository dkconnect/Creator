import json
import random
from pathlib import Path


class Pattern:
    def __init__(self):
        self.name = ""
        self.size = 7
        self.grid = []

    def load_random(self):

        base_dir = Path(__file__).resolve().parent.parent
        pattern_folder = base_dir / "patterns"

        files = list(pattern_folder.glob("*.json"))

        if not files:
            raise FileNotFoundError(f"No pattern files found in {pattern_folder}.")

        file = random.choice(files)

        with open(file, "r") as f:
            data = json.load(f)

        self.name = data["name"]
        self.size = data["size"]
        self.grid = data["grid"]
