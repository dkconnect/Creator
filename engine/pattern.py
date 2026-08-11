import json
import random
from pathlib import Path


class Pattern:
    def __init__(self):
        self.name = ""
        self.size = 7
        self.grid = []

    def load_random(self):
        pattern_folder = Path("patterns")

        files = list(pattern_folder.glob("*.json"))

        if not files:
            raise Exception("No pattern files found.")

        file = random.choice(files)

        with open(file, "r") as f:
            data = json.load(f)

        self.name = data["name"]
        self.size = data["size"]
        self.grid = data["grid"]
