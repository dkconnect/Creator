// STABLE UI FOR NOW

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
const joinSection = document.getElementById("joinSection");
const roomCodeInput = document.getElementById("roomCodeInput");
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

modeSelect.addEventListener("change", () => {
  if (modeSelect.value === "HUMAN") {
    joinSection.classList.remove("hidden");
  } else {
    joinSection.classList.add("hidden");
    roomCodeInput.value = ""; 
  }
});

function validate() {
  startBtn.disabled = !(selectedCategory && selectedPattern);
}

function generateRoomCode() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

startBtn.addEventListener("click", () => {
  const mode = modeSelect.value;
  let role = roleSelect.value;
  let roomCode = roomCodeInput.value.trim().toUpperCase();


  if (mode === "HUMAN") {
    if (!roomCode) {
      roomCode = generateRoomCode();
      role = "C"; 
      alert(`ROOM CREATED!\nCode: ${roomCode}\n\nGive this code to your friend. They must enter it in their 'Room Code' box to join.`);
    } else {
      role = "D"; 
    }
  } else {
    roomCode = "LOCAL";
  }

  const config = {
    role: role,
    mode: mode,
    difficulty: document.getElementById("difficultySelect").value,
    patternCategory: selectedCategory,
    patternId: selectedPattern,
    roomCode: roomCode
  };

  localStorage.setItem("CREATOR_GAME_CONFIG", JSON.stringify(config));
  
  // START
  window.location.href = "game.html";
});
