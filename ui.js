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

function generateRoomCode() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

startBtn.addEventListener("click", () => {
  const mode = document.getElementById("modeSelect").value;
  let roomCode = "LOCAL";
  let role = document.getElementById("roleSelect").value;

  if (mode === "HUMAN") {
    const isHosting = confirm("OK to HOST (Code will be generated) | Cancel to JOIN (Enter a code)");
    if (isHosting) {
      roomCode = generateRoomCode();
      role = "C"; 
      alert("ROOM CODE: " + roomCode + "\nShare this with Player 2!");
    } else {
      roomCode = prompt("Enter 6-digit Room Code:");
      role = "D";
      if (!roomCode) return;
    }
  }

  const config = {
    role: role,
    mode: mode,
    difficulty: document.getElementById("difficultySelect").value,
    patternCategory: selectedCategory,
    patternId: selectedPattern,
    roomCode: roomCode.trim().toUpperCase()
  };

  localStorage.setItem("CREATOR_GAME_CONFIG", JSON.stringify(config));
  window.location.href = "game.html";
});
