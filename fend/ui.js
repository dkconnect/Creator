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

startBtn.addEventListener("click", () => {
  const config = {
    role: roleSelect.value,         
    mode: "LOCAL",
    patternCategory: selectedCategory,
    patternId: selectedPattern
  };

  localStorage.setItem("CREATOR_GAME_CONFIG", JSON.stringify(config));
  window.location.href = "game%20screen/game.html";
});
