
let state = null;
let aiTimer = null;
let busy = false;
let generation = 0;

const board = document.getElementById('board');
const status = document.getElementById('status');
const setupStatus = document.getElementById('setup-status');
const home = document.getElementById('home');
const gameScreen = document.getElementById('game');

async function api(path, data) {
  const options = data === undefined
    ? {}
    : {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      };

  const response = await fetch('/api/' + path, options);
  const result = await response.json();

  if (!response.ok) {
    throw Error(result.error || 'Request failed');
  }

  return result;
}

function showGame() {
  home.hidden = true;
  gameScreen.hidden = false;
}

function showHome() {
  clearTimeout(aiTimer);
  generation++;

  gameScreen.hidden = true;
  home.hidden = false;

  setupStatus.textContent =
    'Choose your settings and start a match.';
}

function scheduleAI(g) {
  clearTimeout(aiTimer);

  if (!g?.ai_turn || g.game_over) {
    return;
  }

  const current = generation;

  aiTimer = setTimeout(async () => {
    if (
      current !== generation ||
      gameScreen.hidden
    ) {
      return;
    }

    if (busy) {
      scheduleAI(g);
      return;
    }

    busy = true;

    try {
      const next = await api('ai', {});

      if (current === generation) {
        render(next);
      }
    } catch (error) {
      if (current === generation) {
        status.textContent =
          'AI error: ' + error.message;
      }
    } finally {
      busy = false;
    }
  }, g.phase === 'WAITING_FOR_ROLL' ? 550 : 850);
}

function render(g) {
  state = g;
  showGame();
  board.replaceChildren();

  if (!g?.board) {
    return;
  }

  const legal = new Set(
    (g.valid_moves || []).map(
      p => p.join(',')
    )
  );

  const targets = new Set(
    (g.targets || []).map(
      p => p.join(',')
    )
  );

  for (let row = 0; row < g.board.length; row++) {
    for (
      let col = 0;
      col < g.board[row].length;
      col++
    ) {
      const cell = document.createElement('button');

      cell.type = 'button';
      cell.className =
        'cell' + ((row + col) % 2 ? ' dark' : '');

      const key = row + ',' + col;

      if (targets.has(key)) {
        cell.classList.add('target');
      }

      if (legal.has(key)) {
        cell.classList.add('valid');
      }

      if (
        g.selected &&
        g.selected[0] === row &&
        g.selected[1] === col
      ) {
        cell.classList.add('selected');
      }

      const pawn = g.board[row][col];

      if (pawn) {
        const piece = document.createElement('span');

        piece.className = 'pawn ' + pawn.team;
        cell.appendChild(piece);
      }

      cell.setAttribute(
        'aria-label',
        `Row ${row + 1}, column ${col + 1}${
          pawn ? ', ' + pawn.team + ' pawn' : ''
        }`
      );

      cell.onclick = () => clickCell(row, col);

      board.appendChild(cell);
    }
  }

  document.getElementById('roll').disabled =
    g.phase !== 'WAITING_FOR_ROLL' ||
    g.game_over ||
    g.ai_turn;

  const turn = document.getElementById('turn');

  turn.className = g.turn.toLowerCase();

  turn.textContent = g.game_over
    ? `${g.winner} WINS`
    : `${g.turn} TO PLAY`;

  document.getElementById('dice').textContent =
    g.dice ?? '—';

  document.getElementById('pattern').textContent =
    g.pattern?.name || '—';

  const captures = document.getElementById('captures');
  captures.replaceChildren();

  for (const [team, count] of [
    ['BLUE', g.blue_captures_suffered],
    ['RED', g.red_captures_suffered]
  ]) {
    const span = document.createElement('span');

    span.className = team.toLowerCase();
    span.textContent = `${team} ${count}`;

    captures.appendChild(span);
  }

  status.textContent = g.game_over
    ? `${g.winner} wins — choose NEW MATCH to play again.`
    : g.ai_turn
      ? `${g.mode.toUpperCase()} AI is thinking…`
      : g.phase === 'WAITING_FOR_ROLL'
        ? `${g.turn}: roll the dice · Turn ${g.turn_count + 1}`
        : g.phase === 'WAITING_FOR_SELECTION'
          ? `${g.turn}: select a pawn`
          : `${g.turn}: choose a highlighted destination`;

  scheduleAI(g);
}

async function clickCell(row, col) {
  if (
    busy ||
    !state ||
    state.game_over ||
    state.phase === 'WAITING_FOR_ROLL' ||
    state.ai_turn
  ) {
    return;
  }

  const pawn = state.board[row][col];

  const action =
    pawn && pawn.team === state.turn
      ? 'select'
      : 'move';

  busy = true;

  try {
    render(await api(action, { row, col }));
  } catch (error) {
    status.textContent = error.message;
  } finally {
    busy = false;
  }
}

document.getElementById('new').onclick = async () => {
  if (busy) {
    return;
  }

  clearTimeout(aiTimer);
  generation++;
  busy = true;

  try {
    const pattern =
      document.getElementById('patterns').value;

    const mode =
      document.getElementById('mode').value;

    if (!pattern) {
      throw Error('Choose a victory pattern.');
    }

    render(await api('new', { pattern, mode }));
  } catch (error) {
    setupStatus.textContent = error.message;
  } finally {
    busy = false;
  }
};

document.getElementById('back').onclick = () => {
  if (
    state &&
    !state.game_over &&
    !confirm(
      'Leave this match and return to setup? ' +
      'Your current match will remain until you start another.'
    )
  ) {
    return;
  }

  showHome();
};

document.getElementById('roll').onclick = async () => {
  if (busy || state?.ai_turn) {
    return;
  }

  busy = true;

  try {
    render(await api('roll', {}));
  } catch (error) {
    status.textContent = error.message;
  } finally {
    busy = false;
  }
};

async function initialize() {
  try {
    const patterns = await api('patterns');

    const select =
      document.getElementById('patterns');

    select.replaceChildren();

    for (const pattern of patterns) {
      const option = document.createElement('option');

      option.value = pattern.file;
      option.textContent = pattern.name;

      select.appendChild(option);
    }

    const saved = await api('state');

    if (saved.board) {
      if (saved.mode) {
        document.getElementById('mode').value =
          saved.mode;
      }

      const matchPattern = patterns.find(
        p => p.name === saved.pattern?.name
      );

      if (matchPattern) {
        select.value = matchPattern.file;
      }

      render(saved);
    } else {
      setupStatus.textContent =
        'Select a mode and pattern to begin.';
    }
  } catch (error) {
    setupStatus.textContent = error.message;
  }
}

initialize();
