//GOING BACK TO STABLE RELEASE VERSION
  
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

// Game start
startBtn.addEventListener("click", () => {
  const config = {
    role: document.getElementById("roleSelect").value,
    mode: document.getElementById("modeSelect").value,
    difficulty: document.getElementById("difficultySelect").value,
    patternCategory: selectedCategory,
    patternId: selectedPattern
  };

  localStorage.setItem(
    "CREATOR_GAME_CONFIG",
    JSON.stringify(config)
  );

  window.location.href = "game.html";
});
