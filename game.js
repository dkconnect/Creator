// Copyright - 2026
// Creator 
// Dibyanshu | Luci

// Let's Initialize Canvas Here
const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const GRID_SIZE = 16;
const CELL_SIZE = canvas.width / GRID_SIZE;

// Basic UI
const turnEl = document.getElementById("turn");
const diceEl = document.getElementById("dice");
const rollBtn = document.getElementById("rollBtn");
const startBtn = document.getElementById("startBtn");
const patternSelectEl = document.getElementById("pattern");
const modeSelectEl = document.getElementById("mode");
const sideSelectEl = document.getElementById("side");

// Init
let gameMode = "HUMAN";
let humanPlayer = "C";
let currentPlayer = "C";

let diceRoll = null;
let selectedPawn = null;
let validMoves = [];

let gameStarted = false;
let gameOver = false;

// Board Design
const board = Array.from({ length: GRID_SIZE }, () =>
  Array(GRID_SIZE).fill(null)
);

// patterns  - kinda list (will complete it in a moment)
const RAW_PATTERNS = {
  X: [
    [1,0,0,0,1],
    [0,1,0,1,0],
    [0,0,1,0,0],
    [0,1,0,1,0],
    [1,0,0,0,1]
  ],
  
  "0": [
    [1,1,1],
    [1,0,1],
    [1,0,1],
    [1,0,1],
    [1,1,1]
  ],
  
  "1": [
    [0,1,0],
    [1,1,0],
    [0,1,0],
    [0,1,0],
    [1,1,1]
  ]
};

let pattern = Array.from({ length: GRID_SIZE }, () =>
  Array(GRID_SIZE).fill(false)
);

function buildPattern(raw) {
  const h = raw.length;
  const w = raw[0].length;
  const ro = Math.floor((GRID_SIZE - h) / 2);
  const co = Math.floor((GRID_SIZE - w) / 2);
  const g = Array.from({ length: GRID_SIZE }, () =>
    Array(GRID_SIZE).fill(false)
  );
  for (let r = 0; r < h; r++)
    for (let c = 0; c < w; c++)
      if (raw[r][c]) g[ro + r][co + c] = true;
  return g;
}

// //
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

// pawn capture logic
function sendPawnHome(player) {
  const rows = player === "C" ? [0, 1] : [GRID_SIZE - 2, GRID_SIZE - 1];
  for (let r of rows)
    for (let c = 0; c < GRID_SIZE; c++)
      if (!board[r][c]) {
        board[r][c] = player;
        return;
      }
}

// dicr logic
function rollDice() {
  diceRoll = Math.floor(Math.random() * 6) + 1;
  diceEl.textContent = `Dice: ${diceRoll}`;
  rollBtn.disabled = true;
}

// turn system
function switchTurn() {
  currentPlayer = currentPlayer === "C" ? "D" : "C";
  diceRoll = null;
  selectedPawn = null;
  validMoves = [];

  turnEl.textContent =
    currentPlayer === "C" ? "Turn: Creator" : "Turn: Destroyer";
  diceEl.textContent = "Dice: -";

  rollBtn.disabled =
    gameMode === "AI" && currentPlayer !== humanPlayer;

  if (gameMode === "AI" && currentPlayer !== humanPlayer) {
    setTimeout(aiMove, 600);
  }
}

// //
function getValidMoves(r, c) {
  if (!diceRoll) return [];
  const dirs = [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];
  return dirs
    .map(([dr, dc]) => ({ row: r + dr * diceRoll, col: c + dc * diceRoll }))
    .filter(m =>
      m.row >= 0 && m.row < GRID_SIZE &&
      m.col >= 0 && m.col < GRID_SIZE &&
      board[m.row][m.col] !== currentPlayer
    );
}

// win logic
function checkWin(p) {
  for (let r = 0; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      if (pattern[r][c] && board[r][c] !== p) return false;
  return true;
}

// comp ago
function aiMove() {
  rollDice();

  setTimeout(() => {
    let moves = [];

    for (let r = 0; r < GRID_SIZE; r++)
      for (let c = 0; c < GRID_SIZE; c++)
        if (board[r][c] === currentPlayer)
          getValidMoves(r, c).forEach(m =>
            moves.push({ from: { r, c }, to: m })
          );

    if (!moves.length) return switchTurn();

    function score(m) {
      let s = 0;
      if (pattern[m.to.row][m.to.col]) s += 100;
      if (board[m.to.row][m.to.col]) s += 50;

      board[m.from.r][m.from.c] = null;
      const prev = board[m.to.row][m.to.col];
      board[m.to.row][m.to.col] = currentPlayer;
      if (checkWin(currentPlayer)) s += 1000;
      board[m.from.r][m.from.c] = currentPlayer;
      board[m.to.row][m.to.col] = prev;

      return s;
    }

    moves.sort((a, b) => score(b) - score(a));
    const move = moves[0];

    if (board[move.to.row][move.to.col])
      sendPawnHome(board[move.to.row][move.to.col]);

    board[move.to.row][move.to.col] = currentPlayer;
    board[move.from.r][move.from.c] = null;

    if (checkWin(currentPlayer)) {
      alert(`${currentPlayer} WINS`);
      gameOver = true;
      return;
    }

    switchTurn();
  }, 300);
}

// --------------------------------------------------------------------------------------------------------------

rollBtn.onclick = () => {
  if (!diceRoll && gameStarted && !gameOver) rollDice();
};

canvas.onclick = e => {
  if (!gameStarted || gameOver || !diceRoll) return;
  if (gameMode === "AI" && currentPlayer !== humanPlayer) return;

  const rect = canvas.getBoundingClientRect();
  const col = Math.floor((e.clientX - rect.left) / CELL_SIZE);
  const row = Math.floor((e.clientY - rect.top) / CELL_SIZE);

  if (!selectedPawn && board[row][col] === currentPlayer) {
    selectedPawn = { row, col };
    validMoves = getValidMoves(row, col);
    return;
  }

  const m = validMoves.find(v => v.row === row && v.col === col);
  if (!m) return (selectedPawn = validMoves = null);

  if (board[row][col]) sendPawnHome(board[row][col]);
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

// --------------------------------------------------------------------------------------------------------------
function draw() {
  ctx.clearRect(0,0,canvas.width,canvas.height);

  ctx.fillStyle = "rgba(255,255,255,0.15)";
  for (let r=0;r<GRID_SIZE;r++)
    for (let c=0;c<GRID_SIZE;c++)
      if (pattern[r][c])
        ctx.fillRect(c*CELL_SIZE,r*CELL_SIZE,CELL_SIZE,CELL_SIZE);

  ctx.fillStyle = "rgba(0,255,0,0.3)";
  validMoves.forEach(m =>
    ctx.fillRect(m.col*CELL_SIZE,m.row*CELL_SIZE,CELL_SIZE,CELL_SIZE)
  );

  ctx.strokeStyle="#444";
  for (let i=0;i<=GRID_SIZE;i++){
    ctx.beginPath();
    ctx.moveTo(i*CELL_SIZE,0);
    ctx.lineTo(i*CELL_SIZE,canvas.height);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0,i*CELL_SIZE);
    ctx.lineTo(canvas.width,i*CELL_SIZE);
    ctx.stroke();
  }

  for (let r=0;r<GRID_SIZE;r++)
    for (let c=0;c<GRID_SIZE;c++)
      if (board[r][c]){
        ctx.beginPath();
        ctx.arc(c*CELL_SIZE+CELL_SIZE/2,r*CELL_SIZE+CELL_SIZE/2,CELL_SIZE*0.35,0,Math.PI*2);
        ctx.fillStyle=board[r][c]==="C"?"#4da6ff":"#ff4d4d";
        ctx.fill();
      }

  requestAnimationFrame(draw);
}
draw();

// fcking start
startBtn.onclick = () => {
  pattern = buildPattern(RAW_PATTERNS[patternSelectEl.value]);
  gameMode = modeSelectEl.value;
  humanPlayer = sideSelectEl.value;

  resetBoard();
  gameStarted = true;
  gameOver = false;
  currentPlayer = "C";

  rollBtn.disabled = gameMode === "AI" && humanPlayer !== "C";
};
