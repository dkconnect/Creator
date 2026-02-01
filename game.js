// STILL UNDER DEVELOPMENT

// STABLE RELEASE V.1

//WORKING V.2 - ADDING FIREBASE

const CONFIG = JSON.parse(localStorage.getItem("CREATOR_GAME_CONFIG"));

const firebaseConfig = {
    apiKey: "AIzaSyDZB8Bp3wWEDCMTWK8HRWFS3P4Al5qasu8",
    authDomain: "the-creator-game.firebaseapp.com",
    projectId: "the-creator-game",
    storageBucket: "the-creator-game.firebasestorage.app",
    messagingSenderId: "195933793096",
    appId: "1:195933793096:web:0a9588c723c23a353aa17d"
};

firebase.initializeApp(firebaseConfig);
const db = firebase.database();
const roomRef = db.ref("rooms/" + CONFIG.roomCode);

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

let board = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(null));
let currentPlayer = "C";
let diceRoll = null;
let selectedPawn = null;
let validMoves = [];
let gameOver = false;
let phase = "ROLL";

const pattern = buildPattern8(PATTERNS[CONFIG.patternCategory][CONFIG.patternId]);

// INIT GAME
resetBoard();
updateUI();

if (CONFIG.roomCode !== "LOCAL") {
    if (CONFIG.role === "C") {
        roomRef.set({
            board, currentPlayer, diceRoll, phase, gameOver: false
        });
    }

    roomRef.on("value", (snapshot) => {
        const data = snapshot.val();
        if (!data) return;
        board = data.board;
        currentPlayer = data.currentPlayer;
        diceRoll = data.diceRoll;
        phase = data.phase;
        gameOver = data.gameOver;
        updateUI();
    });
} else {
    startRollPhase();
}

function buildPattern8(raw) {
    const grid = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(false));
    const off = Math.floor((GRID_SIZE - 8) / 2);
    for (let r = 0; r < 8; r++)
        for (let c = 0; c < 8; c++)
            if (raw && raw[r] && raw[r][c]) grid[off + r][off + c] = true;
    return grid;
}

function resetBoard() {
    board.forEach(r => r.fill(null));
    for (let r = 0; r < 2; r++) for (let c = 0; c < GRID_SIZE; c++) board[r][c] = "C";
    for (let r = GRID_SIZE - 2; r < GRID_SIZE; r++) for (let c = 0; c < GRID_SIZE; c++) board[r][c] = "D";
}

function updateUI() {
    document.getElementById("roomDisplay").textContent = CONFIG.roomCode;
    document.getElementById("roleDisplay").textContent = CONFIG.role === "C" ? "ROLE: CREATOR" : "ROLE: DESTROYER";
    
    turnDisplay.textContent = currentPlayer === "C" ? "CREATOR'S TURN" : "DESTROYER'S TURN";
    turnDisplay.style.color = currentPlayer === "C" ? "#4da6ff" : "#ff4d4d";
    diceDisplay.textContent = diceRoll ?? "–";
    phaseLabel.textContent = phase;

    const isMyTurn = (CONFIG.roomCode === "LOCAL") || (currentPlayer === CONFIG.role);
    rollBtn.disabled = !isMyTurn || phase !== "ROLL" || gameOver;
}

rollBtn.onclick = () => {
    diceRoll = Math.floor(Math.random() * 6) + 1;
    phase = "MOVE";
    sync();
};

canvas.onclick = e => {
    if (phase !== "MOVE" || gameOver) return;
    if (CONFIG.roomCode !== "LOCAL" && currentPlayer !== CONFIG.role) return;

    const rect = canvas.getBoundingClientRect();
    const col = Math.floor((e.clientX - rect.left) / CELL);
    const row = Math.floor((e.clientY - rect.top) / CELL);

    if (board[row][col] === currentPlayer) {
        selectedPawn = { row, col };
        validMoves = getValidMoves(row, col);
        return;
    }

    const move = validMoves.find(m => m.row === row && m.col === col);
    if (!move) return;

    if (board[row][col]) sendPawnHome(board[row][col]);

    board[row][col] = currentPlayer;
    board[selectedPawn.row][selectedPawn.col] = null;
    
    if (checkWin(currentPlayer)) {
        alert(`${currentPlayer} WINS!`);
        gameOver = true;
    } else {
        currentPlayer = currentPlayer === "C" ? "D" : "C";
        phase = "ROLL";
        diceRoll = null;
    }
    
    selectedPawn = null;
    validMoves = [];
    sync();
};

function sync() {
    if (CONFIG.roomCode !== "LOCAL") {
        roomRef.update({ board, currentPlayer, diceRoll, phase, gameOver });
    }
    updateUI();
}

function getValidMoves(r, c) {
    const dirs = [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];
    return dirs.map(([dr, dc]) => ({
        row: r + dr * diceRoll,
        col: c + dc * diceRoll
    })).filter(m => 
        m.row >= 0 && m.row < GRID_SIZE && 
        m.col >= 0 && m.col < GRID_SIZE && 
        board[m.row][m.col] !== currentPlayer
    );
}

function sendPawnHome(player) {
    const rows = player === "C" ? [0, 1] : [GRID_SIZE - 2, GRID_SIZE - 1];
    for (let r of rows) for (let c = 0; c < GRID_SIZE; c++) 
        if (!board[r][c]) { board[r][c] = player; return; }
}

function checkWin(p) {
    for (let r = 0; r < GRID_SIZE; r++)
        for (let c = 0; c < GRID_SIZE; c++)
            if (pattern[r][c] && board[r][c] !== p) return false;
    return true;
}

function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.strokeStyle="#b7ff5a22";
    for (let i=0;i<=GRID_SIZE;i++){
        ctx.beginPath(); ctx.moveTo(i*CELL,0); ctx.lineTo(i*CELL,canvas.height); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0,i*CELL); ctx.lineTo(canvas.width,i*CELL); ctx.stroke();
    }
    ctx.fillStyle="rgba(255,255,255,0.15)";
    for (let r=0;r<GRID_SIZE;r++) for (let c=0;c<GRID_SIZE;c++) if (pattern[r][c]) ctx.fillRect(c*CELL,r*CELL,CELL,CELL);
    ctx.fillStyle="rgba(0,255,0,0.2)";
    validMoves.forEach(m => ctx.fillRect(m.col*CELL,m.row*CELL,CELL,CELL));
    for (let r=0;r<GRID_SIZE;r++) for (let c=0;c<GRID_SIZE;c++) if (board[r][c]) {
        ctx.fillStyle = board[r][c]==="C" ? "#4da6ff" : "#ff4d4d";
        ctx.fillRect(c*CELL+CELL*0.2, r*CELL+CELL*0.2, CELL*0.6, CELL*0.6);
    }
    requestAnimationFrame(draw);
}
draw();
