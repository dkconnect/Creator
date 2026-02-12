//REVERT

const CONFIG = JSON.parse(localStorage.getItem("CREATOR_GAME_CONFIG") || "{}");

const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const GRID_SIZE = 16;
const CELL = canvas.width / GRID_SIZE;
const PATTERN_SIZE = 7;
const OFFSET = Math.floor((GRID_SIZE - PATTERN_SIZE) / 2);

const rollBtn = document.getElementById("rollBtn");
const diceDisplay = document.getElementById("diceDisplay");
const turnDisplay = document.getElementById("turnDisplay");

let board = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(null));
let pattern = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(false));

let currentPlayer = "C";           
let myRole = CONFIG.role || "C";   
let diceRoll = null;
let selectedPawn = null;
let validMoves = [];

function loadPattern() {
  try {
    const cat = CONFIG.patternCategory;
    const id  = CONFIG.patternId;

    if (!cat || !id || typeof PATTERNS === 'undefined') {
      console.warn("No pattern data - using fallback X pattern");
     
      for (let i = 0; i < PATTERN_SIZE; i++) {
        pattern[OFFSET + i][OFFSET + i] = true;
        pattern[OFFSET + i][OFFSET + PATTERN_SIZE - 1 - i] = true;
      }
      return;
    }

    const raw = PATTERNS[cat]?.[id];
    if (!raw || !Array.isArray(raw) || raw.length !== 7) {
      console.warn("Invalid pattern - using fallback");
 
      for (let i = 0; i < PATTERN_SIZE; i++) {
        pattern[OFFSET + i][OFFSET + i] = true;
        pattern[OFFSET + i][OFFSET + PATTERN_SIZE - 1 - i] = true;
      }
      return;
    }

    for (let r = 0; r < 7; r++) {
      for (let c = 0; c < 7; c++) {
        if (raw[r][c]) {
          pattern[OFFSET + r][OFFSET + c] = true;
        }
      }
    }

    console.log("Pattern loaded:", cat, id);
  } catch (e) {
    console.error("Pattern error:", e);
  }
}

function resetBoard() {
  board.forEach(row => row.fill(null));


  for (let r = 0; r < 2; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      board[r][c] = "C";
    }
  }


  for (let r = GRID_SIZE - 2; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      board[r][c] = "D";
    }
  }
}

function updateUI() {
  turnDisplay.textContent = currentPlayer === "C" ? "CREATOR'S TURN" : "DESTROYER'S TURN";
  diceDisplay.textContent = diceRoll || "–";
  rollBtn.disabled = !!diceRoll;  
}

function rollDice() {
  diceRoll = Math.floor(Math.random() * 6) + 1;
  diceDisplay.textContent = diceRoll;
  rollBtn.disabled = true;
}

function getValidMoves(r, c) {
  if (!diceRoll) return [];

  const dirs = [
    [-1,0], [1,0], [0,-1], [0,1],
    [-1,-1], [-1,1], [1,-1], [1,1]
  ];

  const moves = [];

  for (const [dr, dc] of dirs) {
    const nr = r + dr * diceRoll;
    const nc = c + dc * diceRoll;
    if (nr >= 0 && nr < GRID_SIZE && nc >= 0 && nc < GRID_SIZE) {
     
      if (board[nr][nc] !== currentPlayer) {
        moves.push({ row: nr, col: nc });
      }
    }
  }

  return moves;
}

function returnPawnHome(player) {
  const homeRows = player === "C" ? [0, 1] : [GRID_SIZE - 2, GRID_SIZE - 1];

  for (const row of homeRows) {
    for (let col = 0; col < GRID_SIZE; col++) {
      if (!board[row][col]) {
        board[row][col] = player;
        return true;
      }
    }
  }
  
  return false;
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  
  ctx.strokeStyle = "#b7ff5a";
  ctx.lineWidth = 1;
  for (let i = 0; i <= GRID_SIZE; i++) {
    ctx.beginPath();
    ctx.moveTo(i * CELL, 0);
    ctx.lineTo(i * CELL, canvas.height);
    ctx.moveTo(0, i * CELL);
    ctx.lineTo(canvas.width, i * CELL);
    ctx.stroke();
  }

  ctx.fillStyle = "rgba(180, 255, 120, 0.10)";
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      if (pattern[r][c]) {
        ctx.fillRect(c * CELL, r * CELL, CELL, CELL);
      }
    }
  }


  if (selectedPawn && validMoves.length > 0) {
    ctx.fillStyle = "rgba(100, 180, 255, 0.35)";
    validMoves.forEach(m => {
      ctx.fillRect(m.col * CELL, m.row * CELL, CELL, CELL);
    });
  }

  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      const p = board[r][c];
      if (p) {
        ctx.fillStyle = p === "C" ? "#4da6ff" : "#ff4d4d";
        ctx.beginPath();
        ctx.arc(c * CELL + CELL/2, r * CELL + CELL/2, CELL * 0.38, 0, Math.PI * 2);
        ctx.fill();

 
        ctx.strokeStyle = "rgba(255,255,255,0.7)";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }
  }
}



rollBtn.onclick = () => {
  if (!diceRoll) {
    rollDice();
    updateUI();
  }
};

canvas.onclick = (e) => {
  const rect = canvas.getBoundingClientRect();
  const col = Math.floor((e.clientX - rect.left) / CELL);
  const row = Math.floor((e.clientY - rect.top) / CELL);

 
  if (board[row][col] === currentPlayer && !selectedPawn) {
    selectedPawn = { row, col };
    validMoves = getValidMoves(row, col);
    draw();
    return;
  }

  if (selectedPawn) {
    const isValidMove = validMoves.some(m => m.row === row && m.col === col);
    if (isValidMove) {
      const targetPawn = board[row][col];

      // Cut opponent if present
      if (targetPawn && targetPawn !== currentPlayer) {
        returnPawnHome(targetPawn);
      }

      // Move pawn
      board[row][col] = currentPlayer;
      board[selectedPawn.row][selectedPawn.col] = null;

      selectedPawn = null;
      validMoves = [];
      diceRoll = null;

      // Switch turn
      currentPlayer = currentPlayer === "C" ? "D" : "C";
      updateUI();
      draw();
    }
  }
}


loadPattern();
resetBoard();
updateUI();
draw();

setInterval(draw, 60);
