// STILL UNDER DEVELOPMENT

// STABLE RELEASE V.1
const CONFIG = JSON.parse(
  localStorage.getItem("CREATOR_GAME_CONFIG")
);

const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const GRID_SIZE = 16;
const CELL = canvas.width / GRID_SIZE;

const rollBtn = document.getElementById("rollBtn");
const diceDisplay = document.getElementById("diceDisplay");
const turnDisplay = document.getElementById("turnDisplay");
const timerDisplay = document.getElementById("timerDisplay");
const timerCircle = document.getElementById("timerCircle");
const phaseLabel = document.getElementById("phaseLabel");
const timerBlock = document.querySelector(".timer-block");

let board = Array.from({ length: GRID_SIZE }, () =>
  Array(GRID_SIZE).fill(null)
);

let currentPlayer = "C";
let diceRoll = null;
let selectedPawn = null;
let validMoves = [];
let gameOver = false;

let turnTimer = null;
let timeLeft = 0;
let phase = "ROLL";

const pattern = buildPattern8(
  PATTERNS[CONFIG.patternCategory][CONFIG.patternId]
);

resetBoard();
updateUI();
startRollPhase();

function buildPattern8(raw) {
  const grid = Array.from({ length: GRID_SIZE }, () =>
    Array(GRID_SIZE).fill(false)
  );
  const off = Math.floor((GRID_SIZE - 8) / 2);
  for (let r = 0; r < 8; r++)
    for (let c = 0; c < 8; c++)
      if (raw[r][c]) grid[off + r][off + c] = true;
  return grid;
}

function resetBoard() {
  board.forEach(r => r.fill(null));

  for (let r = 0; r < 2; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      board[r][c] = "C";

  for (let r = GRID_SIZE - 2; r < GRID_SIZE; r++)
    for (let c = 0; c < GRID_SIZE; c++)
      board[r][c] = "D";
}

function startTimer(seconds, onExpire) {
  clearInterval(turnTimer);
  timeLeft = seconds;
  updateTimerVisual(seconds);

  turnTimer = setInterval(() => {
    timeLeft--;
    updateTimerVisual(seconds);

    if (timeLeft <= 0) {
      clearInterval(turnTimer);
      onExpire();
    }
  }, 1000);
}

function updateTimerVisual(max) {
  timerDisplay.textContent = timeLeft;
  const pct = timeLeft / max;
  timerCircle.style.strokeDashoffset = 339.29 * (1 - pct);

  timerBlock.classList.remove("timer-warning", "timer-danger");
  if (timeLeft <= 3) timerBlock.classList.add("timer-danger");
  else if (timeLeft <= 7) timerBlock.classList.add("timer-warning");
}

function startRollPhase() {
  phase = "ROLL";
  phaseLabel.textContent = "ROLL";

  if (CONFIG.mode === "AI" && currentPlayer !== CONFIG.role) {
    setTimeout(aiMove, 500);
    return;
  }

  rollBtn.disabled = false;

  startTimer(10, () => {
    if (!diceRoll) {
      rollDice();
      startMovePhase();
    }
  });
}

function startMovePhase() {
  phase = "MOVE";
  phaseLabel.textContent = "MOVE";

  startTimer(20, () => {
    selectedPawn = null;
    validMoves = [];
    switchTurn();
  });
}

function rollDice() {
  diceRoll = Math.floor(Math.random() * 6) + 1;
  diceDisplay.textContent = diceRoll;
  rollBtn.disabled = true;
}

function switchTurn() {
  clearInterval(turnTimer);

  currentPlayer = currentPlayer === "C" ? "D" : "C";
  diceRoll = null;
  selectedPawn = null;
  validMoves = [];

  updateUI();
  startRollPhase();
}

function updateUI() {
  turnDisplay.textContent =
    currentPlayer === "C"
      ? "CREATOR'S TURN"
      : "DESTROYER'S TURN";

  diceDisplay.textContent = diceRoll ?? "–";
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

rollBtn.onclick = () => {
  if (phase === "ROLL" && !diceRoll && !gameOver) {
    rollDice();
    startMovePhase();
  }
};

canvas.onclick = e => {
  if (phase !== "MOVE" || gameOver) return;

  const rect = canvas.getBoundingClientRect();
  const col = Math.floor((e.clientX - rect.left) / CELL);
  const row = Math.floor((e.clientY - rect.top) / CELL);

  if (board[row][col] === currentPlayer) {
    selectedPawn = { row, col };
    validMoves = getValidMoves(row, col);
    return;
  }

  const move = validMoves.find(
    m => m.row === row && m.col === col
  );
  if (!move) return;

  clearInterval(turnTimer);

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
  ctx.clearRect(0,0,canvas.width,canvas.height);

  ctx.strokeStyle="#b7ff5a";
  for (let i=0;i<=GRID_SIZE;i++){
    ctx.beginPath();
    ctx.moveTo(i*CELL,0);
    ctx.lineTo(i*CELL,canvas.height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0,i*CELL);
    ctx.lineTo(canvas.width,i*CELL);
    ctx.stroke();
  }

  ctx.fillStyle="rgba(255,255,255,0.25)";
  for (let r=0;r<GRID_SIZE;r++)
    for (let c=0;c<GRID_SIZE;c++)
      if (pattern[r][c])
        ctx.fillRect(c*CELL,r*CELL,CELL,CELL);

  ctx.fillStyle="rgba(0,255,0,0.3)";
  validMoves.forEach(m =>
    ctx.fillRect(m.col*CELL,m.row*CELL,CELL,CELL)
  );

  for (let r=0;r<GRID_SIZE;r++)
    for (let c=0;c<GRID_SIZE;c++)
      if (board[r][c]) {
        ctx.fillStyle =
          board[r][c]==="C" ? "#4da6ff" : "#ff4d4d";
        ctx.fillRect(
          c*CELL+CELL*0.2,
          r*CELL+CELL*0.2,
          CELL*0.6,
          CELL*0.6
        );
      }

  requestAnimationFrame(draw);
}
draw();


