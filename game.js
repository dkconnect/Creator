
// Copyright - 2026
// The Creator Game
// Dibyanshu & Lucifer

const CONFIG = JSON.parse(
  localStorage.getItem("CREATOR_GAME_CONFIG")
);

// canvas not screen lol finally
const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const GRID_SIZE = 16;
const CELL = canvas.width / GRID_SIZE;

const rollBtn = document.getElementById("rollBtn");
const diceDisplay = document.getElementById("diceDisplay");
const turnDisplay = document.getElementById("turnDisplay");

// freeze

let board = Array.from({ length: GRID_SIZE }, () =>
  Array(GRID_SIZE).fill(null)
);

let currentPlayer = "C";
let diceRoll = null;
let selectedPawn = null;
let validMoves = [];
let gameOver = false;

// pattern

const category = CONFIG.patternCategory;
const patternId = CONFIG.patternId;

if (!window.PATTERNS?.[category]?.[patternId]) {
  throw new Error(`Pattern not found: ${category}:${patternId}`);
}

const pattern = buildPattern8(
  PATTERNS[category][patternId]
);

resetBoard();
updateUI();

function buildPattern8(raw8) {
  const grid = Array.from({ length: GRID_SIZE }, () =>
    Array(GRID_SIZE).fill(false)
  );

  const offset = Math.floor((GRID_SIZE - 8) / 2);

  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      if (raw8[r][c]) {
        grid[offset + r][offset + c] = true;
      }
    }
  }
  return grid;
}

function resetBoard() {
  for (let r = 0; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      board[r][c] = null;

  for (let r = 0; r < 2; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      board[r][c] = "C";

  for (let r = GRID_SIZE - 2; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      board[r][c] = "D";
}

function rollDice() {
  diceRoll = Math.floor(Math.random() * 6) + 1;
  diceDisplay.textContent = diceRoll;
  rollBtn.disabled = true;
}

function getValidMoves(r, c) {
  if (!diceRoll) return [];
  const dirs = [
    [1,0],[-1,0],[0,1],[0,-1],
    [1,1],[1,-1],[-1,1],[-1,-1]
  ];

  return dirs
    .map(([dr, dc]) => ({
      row: r + dr * diceRoll,
      col: c + dc * diceRoll
    }))
    .filter(m =>
      m.row >= 0 && m.row < GRID_SIZE &&
      m.col >= 0 && m.col < GRID_SIZE &&
      board[m.row][m.col] !== currentPlayer
    );
}

function sendPawnHome(player) {
  const rows = player === "C"
    ? [0, 1]
    : [GRID_SIZE - 2, GRID_SIZE - 1];

  for (let r of rows)
    for (let c = 0; c < GRID_SIZE; c++)
      if (!board[r][c]) {
        board[r][c] = player;
        return;
      }
}

function checkWin(p) {
  for (let r = 0; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      if (pattern[r][c] && board[r][c] !== p)
        return false;
  return true;
}

function switchTurn() {
  currentPlayer = currentPlayer === "C" ? "D" : "C";
  diceRoll = null;
  selectedPawn = null;
  validMoves = [];

  rollBtn.disabled =
    CONFIG.mode === "AI" && currentPlayer !== CONFIG.role;

  updateUI();

  if (
    CONFIG.mode === "AI" &&
    currentPlayer !== CONFIG.role &&
    typeof window.aiMove === "function"
  ) {
    setTimeout(aiMove, 500);
  }
}

function updateUI() {
  turnDisplay.textContent =
    currentPlayer === "C"
      ? "CREATOR'S TURN"
      : "DESTROYER'S TURN";

  diceDisplay.textContent = diceRoll ?? "–";
}

rollBtn.onclick = () => {
  if (!diceRoll && !gameOver) rollDice();
};

canvas.onclick = e => {
  if (!diceRoll || gameOver) return;

  if (
    CONFIG.mode === "AI" &&
    currentPlayer !== CONFIG.role
  ) return;

  const rect = canvas.getBoundingClientRect();
  const col = Math.floor((e.clientX - rect.left) / CELL);
  const row = Math.floor((e.clientY - rect.top) / CELL);

  // reworking on pawns logic bitch is doing drama ughhhhh
  if (board[row][col] === currentPlayer) {
    selectedPawn = { row, col };
    validMoves = getValidMoves(row, col);
    return;
  }

  const move = validMoves.find(
    m => m.row === row && m.col === col
  );
  if (!move) return;

  if (board[row][col])
    sendPawnHome(board[row][col]);

  board[row][col] = currentPlayer;
  board[selectedPawn.row][selectedPawn.col] = null;

  selectedPawn = null;
  validMoves = [];

  if (checkWin(currentPlayer)) {
    alert(`${currentPlayer} WINS`);
    gameOver = true;
    return;
  }

  switchTurn();
};

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // GRID
  ctx.strokeStyle = "#b7ff5a";
  for (let i = 0; i <= GRID_SIZE; i++) {
    ctx.beginPath();
    ctx.moveTo(i * CELL, 0);
    ctx.lineTo(i * CELL, canvas.height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, i * CELL);
    ctx.lineTo(canvas.width, i * CELL);
    ctx.stroke();
  }

  // FILLING PATTERN CELLS
  ctx.fillStyle = "rgba(200,200,200,0.4)";
  for (let r = 0; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      if (pattern[r][c])
        ctx.fillRect(
          c * CELL,
          r * CELL,
          CELL,
          CELL
        );

  ctx.fillStyle = "rgba(0,255,0,0.3)";
  validMoves.forEach(m =>
    ctx.fillRect(
      m.col * CELL,
      m.row * CELL,
      CELL,
      CELL
    )
  );

  for (let r = 0; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      if (board[r][c]) {
        ctx.fillStyle =
          board[r][c] === "C"
            ? "#4da6ff"
            : "#ff4d4d";

        ctx.fillRect(
          c * CELL + CELL * 0.2,
          r * CELL + CELL * 0.2,
          CELL * 0.6,
          CELL * 0.6
        );
      }

  requestAnimationFrame(draw);
}

draw();
