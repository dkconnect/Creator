//ADDING FIREBASE AND THEN WILL WORK ON STABILIZING THE ALGO

import { db, ref, set } from "./firebase.js";

const PATTERNS = {
  alphabets: [..."ABCDEFGHIJKLMNOPQRSTUVWXYZ"],
  numbers: ["0","1","2","3","4","5","6","7","8","9"],
  symbols: ["@","#","$","%","&","+","-","*","/","?"],
  shapes: ["X","Square","Diamond","Cross"]
};

let selectedCategory = null;
let selectedPattern = null;

const patternButtons = document.querySelectorAll(".pattern-cat-btn");
const patternPicker = document.getElementById("patternPicker");
const patternSelect = document.getElementById("patternSelect");
const startBtn = document.getElementById("startBtn");

const modeSelect = document.getElementById("modeSelect");
const multiplayerBox = document.getElementById("multiplayerBox");
const createGameBtn = document.getElementById("createGameBtn");
const joinGameBtn = document.getElementById("joinGameBtn");
const joinCodeInput = document.getElementById("joinCodeInput");
const roleSelect = document.getElementById("roleSelect");

patternButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    patternButtons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    selectedCategory = btn.dataset.category;
    patternSelect.innerHTML = "";

    PATTERNS[selectedCategory].forEach(p => {
      const opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      patternSelect.appendChild(opt);
    });

    selectedPattern = PATTERNS[selectedCategory][0];
    patternPicker.classList.remove("hidden");
    validate();
  });
});

patternSelect.addEventListener("change", e => {
  selectedPattern = e.target.value;
  validate();
});

function validate() {
  startBtn.disabled = !(selectedCategory && selectedPattern);
}

modeSelect.addEventListener("change", () => {
  if (modeSelect.value === "HUMAN") {
    multiplayerBox.classList.remove("hidden");
    startBtn.classList.add("hidden");
  } else {
    multiplayerBox.classList.add("hidden");
    startBtn.classList.remove("hidden");
  }
});

function generateGameCode() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

createGameBtn.onclick = async () => {
  if (!selectedCategory || !selectedPattern) {
    alert("Select pattern first");
    return;
  }

  const gameCode = generateGameCode();
  const creatorRole = roleSelect.value;
  const otherRole = creatorRole === "C" ? "D" : "C";

  const gameData = {
    players: {
      [creatorRole]: "connected",
      [otherRole]: null
    },
    currentTurn: "C",
    board: null,
    diceRoll: null,
    phase: "ROLL",
    patternCategory: selectedCategory,
    patternId: selectedPattern,
    createdAt: Date.now()
  };

  await set(ref(db, `games/${gameCode}`), gameData);

  const config = {
    mode: "HUMAN",
    multiplayer: true,
    role: creatorRole,
    gameCode,
    patternCategory: selectedCategory,
    patternId: selectedPattern
  };

  localStorage.setItem("CREATOR_GAME_CONFIG", JSON.stringify(config));

  alert(`Game Created!\nShare this code: ${gameCode}`);

  window.location.href = "game.html";
};

joinGameBtn.onclick = () => {
  alert("Join Game — next step");
};

startBtn.addEventListener("click", () => {
  const config = {
    role: roleSelect.value,
    mode: modeSelect.value,
    difficulty: document.getElementById("difficultySelect").value,
    patternCategory: selectedCategory,
    patternId: selectedPattern
  };

  localStorage.setItem("CREATOR_GAME_CONFIG", JSON.stringify(config));
  window.location.href = "game.html";
});
