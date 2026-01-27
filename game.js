// Copyright - 2026
// Dibyanshu - Luci

// Initial Canvas
const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const GRID_SIZE = 16;
const CELL_SIZE = canvas.width / GRID_SIZE;

// Board: null | "C" | "D"
const board = Array.from({ length: GRID_SIZE }, () =>
  Array(GRID_SIZE).fill(null)
);

// X shape
const pattern = Array.from({ length: GRID_SIZE }, (_, row) =>
  Array.from({ length: GRID_SIZE }, (_, col) =>
    row === col || row + col === GRID_SIZE - 1
  )
);

let currentPlayer = "C"; 
let diceRoll = null;
let selectedPawn = null; 
let validMoves = [];

// Adding Pawns
function setupPawns() {
  // Creator (for the top 2 blocks)
  for (let row = 0; row < 2; row++) {
    for (let col = 0; col < GRID_SIZE; col++) {
      board[row][col] = "C";
    }
  }

  // Destroyerbottom 2 row
  for (let row = GRID_SIZE - 2; row < GRID_SIZE; row++) {
    for (let col = 0; col < GRID_SIZE; col++) {
      board[row][col] = "D";
    }
  }
}

setupPawns();

// Adding Dice
function rollDice() {
  diceRoll = Math.floor(Math.random() * 6) + 1;
  selectedPawn = null;
  validMoves = [];
  console.log(`${currentPlayer} rolled ${diceRoll}`);
}

rollDice();

// Moving
function getValidMoves(row, col) {
  const moves = [];
  const directions = [
    [1, 0], [-1, 0], [0, 1], [0, -1],    // straight coordinates
    [1, 1], [1, -1], [-1, 1], [-1, -1]  // diagonal coordinates
  ];

  for (const [dr, dc] of directions) {
    const r = row + dr * diceRoll;
    const c = col + dc * diceRoll;

    if (r < 0 || r >= GRID_SIZE || c < 0 || c >= GRID_SIZE) continue;

    const target = board[r][c];

    if (target === null || target !== currentPlayer) {
      moves.push({ row: r, col: c });
    }
  }

  return moves;
}

canvas.addEventListener("click", (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const col = Math.floor(x / CELL_SIZE);
  const row = Math.floor(y / CELL_SIZE);

  // Adding Pawn Selection
  if (!selectedPawn) {
    if (board[row][col] === currentPlayer) {
      selectedPawn = { row, col };
      validMoves = getValidMoves(row, col);
    }
    return;
  }

  // Pwn Movement
  const isValid = validMoves.some(
    (m) => m.row === row && m.col === col
  );

  if (isValid) {
    board[row][col] = currentPlayer;
    board[selectedPawn.row][selectedPawn.col] = null;
    currentPlayer = currentPlayer === "C" ? "D" : "C";
    rollDice();
  }

  selectedPawn = null;
  validMoves = [];
});


function drawPattern() {
  ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
  for (let row = 0; row < GRID_SIZE; row++) {
    for (let col = 0; col < GRID_SIZE; col++) {
      if (pattern[row][col]) {
        ctx.fillRect(
          col * CELL_SIZE,
          row * CELL_SIZE,
          CELL_SIZE,
          CELL_SIZE
        );
      }
    }
  }
}

function drawGrid() {
  ctx.strokeStyle = "#444";
  for (let i = 0; i <= GRID_SIZE; i++) {
    ctx.beginPath();
    ctx.moveTo(i * CELL_SIZE, 0);
    ctx.lineTo(i * CELL_SIZE, canvas.height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, i * CELL_SIZE);
    ctx.lineTo(canvas.width, i * CELL_SIZE);
    ctx.stroke();
  }
}

function drawPawns() {
  for (let row = 0; row < GRID_SIZE; row++) {
    for (let col = 0; col < GRID_SIZE; col++) {
      const pawn = board[row][col];
      if (!pawn) continue;

      ctx.beginPath();
      ctx.arc(
        col * CELL_SIZE + CELL_SIZE / 2,
        row * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE * 0.35,
        0,
        Math.PI * 2
      );

      ctx.fillStyle = pawn === "C" ? "#4da6ff" : "#ff4d4d";
      ctx.fill();
    }
  }
}

function drawValidMoves() {
  ctx.fillStyle = "rgba(0, 255, 0, 0.3)";
  validMoves.forEach(({ row, col }) => {
    ctx.fillRect(
      col * CELL_SIZE,
      row * CELL_SIZE,
      CELL_SIZE,
      CELL_SIZE
    );
  });
}

function drawSelection() {
  if (!selectedPawn) return;

  ctx.strokeStyle = "#ffff00";
  ctx.lineWidth = 3;
  ctx.strokeRect(
    selectedPawn.col * CELL_SIZE,
    selectedPawn.row * CELL_SIZE,
    CELL_SIZE,
    CELL_SIZE
  );
  ctx.lineWidth = 1;
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawPattern();
  drawGrid();
  drawValidMoves();
  drawPawns();
  drawSelection();
}

// Game Loop 
function gameLoop() {
  draw();
  requestAnimationFrame(gameLoop);
}

gameLoop();
