import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from engine.game import Game
from engine import victory
from engine.ai.basic_ai import BasicAI
from engine.ai.learning_ai import LearningAI
from engine.ai.advanced_ai import AdvancedAI

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
PATTERNS = ROOT / "patterns"

# Each browser session has its own game and AI instance.
SESSIONS = {}
LOCK = threading.RLock()

AI_CLASSES = {
    "basic": BasicAI,
    "learning": LearningAI,
    "advanced": AdvancedAI,
}


def pattern_catalog():
    items = []

    for path in sorted(PATTERNS.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append({
                "file": path.name,
                "name": data["name"],
                "size": data["size"],
            })
        except (ValueError, KeyError):
            continue

    return items


def snapshot(game, mode="human"):
    ai_turn = (
        mode != "human"
        and game.current_player.team == "RED"
        and not game.game_over
    )

    targets = victory.target_cells(
        game, game.current_player.team
    )

    selected = game.selected_pawn

    return {
        "board": [
            [
                None if pawn is None else {
                    "team": pawn.team,
                    "id": pawn.id,
                }
                for pawn in row
            ]
            for row in game.board.grid
        ],
        "turn": game.current_player.team,
        "mode": mode,
        "ai_turn": ai_turn,
        "turn_count": game.turn_count,
        "phase": game.turn_phase,
        "dice": game.dice.value,
        "pattern": {
            "name": game.pattern.name,
            "size": game.pattern.size,
            "grid": game.pattern.grid,
        },
        "targets": [
            list(cell) for cell in sorted(targets)
        ],
        "selected": (
            None if selected is None
            else [selected.row, selected.col]
        ),
        "valid_moves": [
            list(pos) for pos in game.get_valid_moves()
        ],
        "game_over": game.game_over,
        "winner": (
            None if game.winner is None
            else game.winner.team
        ),
        "blue_captures_suffered":
            game.blue.captures_suffered,
        "red_captures_suffered":
            game.red.captures_suffered,
    }


class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200, cookie=None):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.send_header(
            "X-Content-Type-Options", "nosniff"
        )

        if cookie:
            self.send_header(
                "Set-Cookie",
                f"creator_session={cookie}; "
                "HttpOnly; SameSite=Lax; Path=/"
            )

        self.end_headers()
        self.wfile.write(body)

    def session(self):
        raw = self.headers.get("Cookie", "")

        sid = next(
            (
                part.strip().split("=", 1)[1]
                for part in raw.split(";")
                if part.strip().startswith(
                    "creator_session="
                )
            ),
            None
        )

        return sid, SESSIONS.get(sid)

    def do_GET(self):
        path = urlsplit(self.path).path

        if path == "/api/patterns":
            return self.send_json(pattern_catalog())

        if path == "/api/state":
            with LOCK:
                _, entry = self.session()

                return self.send_json(
                    snapshot(*entry)
                    if entry else {"needs_new_game": True}
                )

        files = {
            "/": (
                "index.html",
                "text/html; charset=utf-8"
            ),
            "/app.js": (
                "app.js",
                "text/javascript; charset=utf-8"
            ),
            "/style.css": (
                "style.css",
                "text/css; charset=utf-8"
            ),
        }

        if path not in files:
            return self.send_json(
                {"error": "Not found"}, 404
            )

        filename, mime = files[path]
        body = (WEB / filename).read_bytes()

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header(
            "X-Content-Type-Options", "nosniff"
        )
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        path = urlsplit(self.path).path

        allowed = (
            "/api/new",
            "/api/roll",
            "/api/select",
            "/api/move",
            "/api/ai",
        )

        if path not in allowed:
            return self.send_json(
                {"error": "Not found"}, 404
            )

        try:
            length = int(
                self.headers.get("Content-Length", "0")
            )

            if length < 0 or length > 4096:
                return self.send_json(
                    {"error": "Request too large"}, 413
                )

            data = json.loads(
                self.rfile.read(length) or b"{}"
            )

            if not isinstance(data, dict):
                raise ValueError("Invalid request")

            with LOCK:

                if path == "/api/new":
                    filename = data.get("pattern")

                    valid_patterns = {
                        p["file"]
                        for p in pattern_catalog()
                    }

                    if (
                        not isinstance(filename, str)
                        or filename not in valid_patterns
                    ):
                        return self.send_json(
                            {"error": "Select a valid pattern"},
                            400
                        )

                    mode = data.get("mode", "human")

                    if (
                        mode != "human"
                        and mode not in AI_CLASSES
                    ):
                        return self.send_json(
                            {"error": "Invalid game mode"},
                            400
                        )

                    pattern = json.loads(
                        (PATTERNS / filename).read_text(
                            encoding="utf-8"
                        )
                    )

                    ai = (
                        AI_CLASSES[mode](team="RED")
                        if mode != "human"
                        else None
                    )

                    game = Game(ai_controller=ai)

                    game.pattern.name = pattern["name"]
                    game.pattern.size = pattern["size"]
                    game.pattern.grid = pattern["grid"]

                    sid = secrets.token_urlsafe(32)
                    SESSIONS[sid] = (game, mode)

                    return self.send_json(
                        snapshot(game, mode),
                        cookie=sid
                    )

                _, entry = self.session()

                if entry is None:
                    return self.send_json(
                        {"error": "Start a new game"},
                        404
                    )

                game, mode = entry

                ai_turn = (
                    mode != "human"
                    and game.current_player.team == "RED"
                    and not game.game_over
                )

                if path == "/api/ai":
                    if not ai_turn:
                        return self.send_json(
                            {"error": "Not an AI turn"},
                            409
                        )

                    # Existing Python engine handles
                    # dice rolling and AI movement.
                    game.step_ai()

                    return self.send_json(
                        snapshot(game, mode)
                    )

                # Never allow browser-controlled moves
                # during the AI's turn.
                if ai_turn:
                    return self.send_json(
                        {"error": "Wait for the AI"},
                        409
                    )

                if path == "/api/roll":
                    ok = game.roll_dice() is not None

                elif path == "/api/select":
                    ok = game.select_pawn(
                        int(data["row"]),
                        int(data["col"])
                    )

                else:
                    ok = game.move_selected_pawn(
                        int(data["row"]),
                        int(data["col"])
                    )

                if not ok:
                    return self.send_json(
                        {
                            "error": "Illegal action",
                            "state": snapshot(game, mode),
                        },
                        409
                    )

                return self.send_json(
                    snapshot(game, mode)
                )

        except (
            ValueError,
            TypeError,
            KeyError,
            IndexError
        ):
            return self.send_json(
                {"error": "Invalid request"},
                400
            )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))

    print(
        f"Creator web: http://localhost:{port}"
    )

    ThreadingHTTPServer(
        ("0.0.0.0", port),
        Handler
    ).serve_forever()
