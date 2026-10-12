import json
import logging
import os
import secrets
import threading
import time

from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from engine.game import Game
from engine import victory
from engine.ai.basic_ai import BasicAI
from engine.ai.learning_ai import LearningAI
from engine.ai.advanced_ai import AdvancedAI


ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
PATTERNS = ROOT / "patterns"

AI_CLASSES = {
    "basic": BasicAI,
    "learning": LearningAI,
    "advanced": AdvancedAI,
}

# Inactive matches expire after 2 hours.
SESSION_TTL = 2 * 60 * 60

# Protect the free server from unlimited stored games.
MAX_SESSIONS = 100

# Limit JSON request size.
MAX_BODY = 4096

SESSIONS = {}
SESSIONS_LOCK = threading.RLock()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("creator")


@dataclass
class Session:
    game: object
    mode: str
    last_active: float = field(default_factory=time.monotonic)
    lock: object = field(
        default_factory=threading.RLock
    )


def pattern_catalog():
    items = []

    for path in sorted(PATTERNS.glob("*.json")):
        try:
            data = json.loads(
                path.read_text(encoding="utf-8")
            )

            items.append({
                "file": path.name,
                "name": data["name"],
                "size": data["size"],
            })
        except (OSError, ValueError, KeyError, TypeError):
            logger.warning(
                "Skipping invalid pattern: %s",
                path.name
            )

    return items


def snapshot(game, mode="human"):
    ai_turn = (
        mode != "human"
        and game.current_player.team == "RED"
        and not game.game_over
    )

    targets = victory.target_cells(
        game,
        game.current_player.team
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


def clean_sessions():
    """Remove expired sessions without affecting active games."""
    now = time.monotonic()

    with SESSIONS_LOCK:
        expired = [
            sid
            for sid, session in SESSIONS.items()
            if now - session.last_active > SESSION_TTL
        ]

        for sid in expired:
            del SESSIONS[sid]


def new_session(game, mode):
    clean_sessions()

    with SESSIONS_LOCK:
        if len(SESSIONS) >= MAX_SESSIONS:
            return None

        sid = secrets.token_urlsafe(32)
        SESSIONS[sid] = Session(
            game=game,
            mode=mode
        )

        return sid


class Handler(BaseHTTPRequestHandler):
    server_version = "CreatorWeb/1.0"
    sys_version = ""

    def log_message(self, fmt, *args):
        logger.info(
            "%s - %s",
            self.client_address[0],
            fmt % args
        )

    def send_json(self, data, status=200, cookie=None):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.send_header(
            "Cache-Control",
            "no-store"
        )
        self.send_header(
            "X-Content-Type-Options",
            "nosniff"
        )
        self.send_header(
            "Referrer-Policy",
            "same-origin"
        )

        if cookie:
            # Render terminates HTTPS at its proxy.
            forwarded_proto = self.headers.get(
                "X-Forwarded-Proto", ""
            ).lower()

            secure = (
                "Secure; "
                if forwarded_proto == "https"
                else ""
            )

            self.send_header(
                "Set-Cookie",
                "creator_session="
                + cookie
                + "; Path=/; HttpOnly; "
                + secure
                + "SameSite=Lax"
            )

        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, status):
        self.send_json(
            {"error": message},
            status
        )

    def session(self):
        raw = self.headers.get("Cookie", "")

        sid = None

        for part in raw.split(";"):
            part = part.strip()

            if part.startswith("creator_session="):
                sid = part.split("=", 1)[1]
                break

        if not sid:
            return None

        with SESSIONS_LOCK:
            entry = SESSIONS.get(sid)

            if entry is None:
                return None

            now = time.monotonic()

            if now - entry.last_active > SESSION_TTL:
                del SESSIONS[sid]
                return None

            entry.last_active = now
            return entry

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)

        if path == "/health":
            return self.send_json({
                "status": "ok",
                "service": "creator"
            })

        if path == "/api/patterns":
            return self.send_json(pattern_catalog())

        if path == "/api/state":
            entry = self.session()

            if entry is None:
                return self.send_json({
                    "needs_new_game": True
                })

            with entry.lock:
                return self.send_json(
                    snapshot(entry.game, entry.mode)
                )

        files = {
            "/": (
                WEB / "index.html",
                "text/html; charset=utf-8"
            ),
            "/app.js": (
                WEB / "app.js",
                "text/javascript; charset=utf-8"
            ),
            "/style.css": (
                WEB / "style.css",
                "text/css; charset=utf-8"
            ),
            "/logo/logo.png": (
                ROOT / "logo" / "logo.png",
                "image/png"
            ),
            "/Creator - Official - Rulebook.pdf": (
                WEB / "Creator - Official - Rulebook.pdf",
                "application/pdf"
            ),
        }

        if path not in files:
            return self.send_error_json(
                "Not found",
                HTTPStatus.NOT_FOUND
            )

        filename, mime = files[path]

        try:
            body = filename.read_bytes()
        except OSError:
            logger.exception(
                "Unable to read web file: %s",
                filename
            )
            return self.send_error_json(
                "Server file unavailable",
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.send_header(
            "X-Content-Type-Options",
            "nosniff"
        )
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        path = urlsplit(self.path).path

        allowed = {
            "/api/new",
            "/api/roll",
            "/api/select",
            "/api/move",
            "/api/ai",
        }

        if path not in allowed:
            return self.send_error_json(
                "Not found",
                HTTPStatus.NOT_FOUND
            )

        # Browser requests must originate from this website.
        origin = self.headers.get("Origin")

        if origin:
            expected_host = self.headers.get("Host", "")
            actual = urlsplit(origin)

            if (
                actual.hostname is None
                or actual.netloc.lower()
                != expected_host.lower()
                or actual.scheme not in ("http", "https")
            ):
                return self.send_error_json(
                    "Cross-site request blocked",
                    HTTPStatus.FORBIDDEN
                )

        try:
            length = int(
                self.headers.get("Content-Length", "0")
            )

            if length < 0 or length > MAX_BODY:
                return self.send_error_json(
                    "Invalid request size",
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE
                )

            raw = self.rfile.read(length)

            data = json.loads(raw or b"{}")

            if not isinstance(data, dict):
                raise ValueError("Expected JSON object")

        except (
            ValueError,
            TypeError,
            UnicodeDecodeError,
            json.JSONDecodeError
        ):
            return self.send_error_json(
                "Invalid JSON request",
                HTTPStatus.BAD_REQUEST
            )

        if path == "/api/new":
            return self.start_game(data)

        entry = self.session()

        if entry is None:
            return self.send_error_json(
                "Session expired. Start a new match.",
                HTTPStatus.NOT_FOUND
            )

        with entry.lock:
            try:
                return self.game_action(
                    entry,
                    path,
                    data
                )
            except (ValueError, TypeError, KeyError):
                return self.send_error_json(
                    "Invalid game action",
                    HTTPStatus.BAD_REQUEST
                )
            except Exception:
                logger.exception(
                    "Game action failed: %s",
                    path
                )
                return self.send_error_json(
                    "Game engine error",
                    HTTPStatus.INTERNAL_SERVER_ERROR
                )

    def start_game(self, data):
        filename = data.get("pattern")
        mode = data.get("mode", "human")

        valid_patterns = {
            item["file"]
            for item in pattern_catalog()
        }

        if (
            not isinstance(filename, str)
            or filename not in valid_patterns
        ):
            return self.send_error_json(
                "Select a valid pattern",
                HTTPStatus.BAD_REQUEST
            )

        if mode != "human" and mode not in AI_CLASSES:
            return self.send_error_json(
                "Invalid game mode",
                HTTPStatus.BAD_REQUEST
            )

        try:
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

            state = snapshot(game, mode)

        except Exception:
            logger.exception(
                "Failed to start game"
            )
            return self.send_error_json(
                "Unable to start match",
                HTTPStatus.INTERNAL_SERVER_ERROR
            )

        # Release the previous session when a visitor
        # explicitly starts a replacement match.
        old_sid = None

        for part in self.headers.get("Cookie", "").split(";"):
            part = part.strip()

            if part.startswith("creator_session="):
                old_sid = part.split("=", 1)[1]
                break

        if old_sid:
            with SESSIONS_LOCK:
                SESSIONS.pop(old_sid, None)

        sid = new_session(game, mode)

        if sid is None:
            return self.send_error_json(
                "Server is busy. Try again later.",
                HTTPStatus.SERVICE_UNAVAILABLE
            )

        return self.send_json(
            state,
            cookie=sid
        )

    def game_action(self, entry, path, data):
        game = entry.game
        mode = entry.mode

        ai_turn = (
            mode != "human"
            and game.current_player.team == "RED"
            and not game.game_over
        )

        if path == "/api/ai":
            if not ai_turn:
                return self.send_error_json(
                    "Not an AI turn",
                    HTTPStatus.CONFLICT
                )

            # Dice generation stays inside the Python
            # engine, independent of AI move selection.
            game.step_ai()

            return self.send_json(
                snapshot(game, mode)
            )

        if ai_turn:
            return self.send_error_json(
                "Wait for the AI",
                HTTPStatus.CONFLICT
            )

        if game.game_over:
            return self.send_error_json(
                "Match is already finished",
                HTTPStatus.CONFLICT
            )

        if path == "/api/roll":
            ok = game.roll_dice() is not None

        else:
            row = data.get("row")
            col = data.get("col")

            # Reject booleans, strings, floats, negative
            # coordinates and out-of-board positions.
            if (
                type(row) is not int
                or type(col) is not int
                or not 0 <= row < 16
                or not 0 <= col < 16
            ):
                return self.send_error_json(
                    "Invalid board position",
                    HTTPStatus.BAD_REQUEST
                )

            if path == "/api/select":
                ok = game.select_pawn(row, col)
            else:
                ok = game.move_selected_pawn(
                    row, col
                )

        if not ok:
            return self.send_json(
                {
                    "error": "Illegal action",
                    "state": snapshot(game, mode),
                },
                HTTPStatus.CONFLICT
            )

        return self.send_json(
            snapshot(game, mode)
        )


class CreatorServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))

    logger.info(
        "Creator starting on port %s",
        port
    )

    CreatorServer(
        ("0.0.0.0", port),
        Handler
    ).serve_forever()
