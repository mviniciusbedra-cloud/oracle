(() => {
const { CHALLENGES } = window;

const state = {
  players: [],
  level: "leve",
  round: 1,
  currentPlayerId: null,
  lastPick: null,
  used: {
    faz: new Set(),
    bebe: new Set(),
  },
  spinning: false,
};

const els = {
  screens: [...document.querySelectorAll(".screen")],
  playerForm: document.getElementById("player-form"),
  playerInput: document.getElementById("player-input"),
  playerList: document.getElementById("player-list"),
  btnStart: document.getElementById("btn-start"),
  setupHint: document.getElementById("setup-hint"),
  roundNum: document.getElementById("round-num"),
  spinName: document.getElementById("spin-name"),
  btnSpin: document.getElementById("btn-spin"),
  currentPlayer: document.getElementById("current-player"),
  choiceRow: document.getElementById("choice-row"),
  challengeCard: document.getElementById("challenge-card"),
  challengeType: document.getElementById("challenge-type"),
  challengeText: document.getElementById("challenge-text"),
  challengeMeta: document.getElementById("challenge-meta"),
  btnDidIt: document.getElementById("btn-did-it"),
  btnDrank: document.getElementById("btn-drank"),
  btnReroll: document.getElementById("btn-reroll"),
  btnBackSpin: document.getElementById("btn-back-spin"),
  scoresDialog: document.getElementById("scores-dialog"),
  scoresList: document.getElementById("scores-list"),
  btnResetNight: document.getElementById("btn-reset-night"),
};

function uid() {
  return crypto.randomUUID?.() ?? `p-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function go(screen) {
  els.screens.forEach((s) => {
    const active = s.dataset.screen === screen;
    s.classList.toggle("is-active", active);
    s.hidden = !active;
  });
}

function getLevel() {
  const checked = document.querySelector('input[name="level"]:checked');
  return checked?.value ?? "leve";
}

function normalizeName(name) {
  return name.trim().replace(/\s+/g, " ");
}

function renderPlayers() {
  els.playerList.innerHTML = "";
  state.players.forEach((p) => {
    const li = document.createElement("li");
    li.className = "player-chip";
    li.innerHTML = `<span>${escapeHtml(p.name)}</span>`;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.setAttribute("aria-label", `Remover ${p.name}`);
    remove.textContent = "×";
    remove.addEventListener("click", () => {
      state.players = state.players.filter((x) => x.id !== p.id);
      renderPlayers();
      syncSetup();
    });
    li.appendChild(remove);
    els.playerList.appendChild(li);
  });
  syncSetup();
}

function syncSetup() {
  const ok = state.players.length >= 2;
  els.btnStart.disabled = !ok;
  els.setupHint.textContent = ok
    ? `${state.players.length} na mesa · pronto pra começar`
    : "Adiciona pelo menos 2 pessoas";
}

function escapeHtml(str) {
  return str
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function addPlayer(raw) {
  const name = normalizeName(raw);
  if (!name) return;
  if (state.players.some((p) => p.name.toLowerCase() === name.toLowerCase())) {
    els.playerInput.value = "";
    els.playerInput.placeholder = "Esse nome já tá na mesa";
    return;
  }
  state.players.push({
    id: uid(),
    name,
    did: 0,
    drank: 0,
  });
  els.playerInput.value = "";
  els.playerInput.placeholder = "Ex: Biia, Dudu, Ana…";
  renderPlayers();
}

function startNight() {
  state.level = getLevel();
  state.round = 1;
  state.currentPlayerId = null;
  state.lastPick = null;
  state.used = { faz: new Set(), bebe: new Set() };
  state.players.forEach((p) => {
    p.did = 0;
    p.drank = 0;
  });
  els.roundNum.textContent = String(state.round);
  els.spinName.textContent = "?";
  els.spinName.classList.remove("is-spinning", "is-locked");
  els.btnSpin.disabled = false;
  els.btnSpin.textContent = "Girar a roda";
  go("spin");
}

function currentPlayer() {
  return state.players.find((p) => p.id === state.currentPlayerId) ?? null;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function spinWheel() {
  if (state.spinning || state.players.length < 2) return;
  state.spinning = true;
  els.btnSpin.disabled = true;
  els.spinName.classList.add("is-spinning");
  els.spinName.classList.remove("is-locked");

  const ticks = 18 + Math.floor(Math.random() * 8);
  let delay = 45;
  let pick = state.players[0];

  for (let i = 0; i < ticks; i += 1) {
    pick = state.players[Math.floor(Math.random() * state.players.length)];
    els.spinName.textContent = pick.name;
    await sleep(delay);
    delay += 12;
  }

  // Evita repetir a mesma pessoa duas vezes seguidas quando dá
  if (state.players.length > 1 && pick.id === state.currentPlayerId) {
    const others = state.players.filter((p) => p.id !== state.currentPlayerId);
    pick = others[Math.floor(Math.random() * others.length)];
    els.spinName.textContent = pick.name;
  }

  state.currentPlayerId = pick.id;
  els.spinName.classList.remove("is-spinning");
  els.spinName.classList.add("is-locked");
  await sleep(450);
  state.spinning = false;
  openChallengeScreen();
}

function openChallengeScreen() {
  const player = currentPlayer();
  if (!player) return;
  els.currentPlayer.textContent = player.name;
  els.choiceRow.hidden = false;
  els.challengeCard.hidden = true;
  state.lastPick = null;
  go("challenge");
}

function poolFor(kind) {
  const list = CHALLENGES[kind][state.level] ?? CHALLENGES[kind].leve;
  const used = state.used[kind];
  const fresh = list
    .map((text, index) => ({ text, index }))
    .filter((item) => !used.has(item.index));
  if (fresh.length === 0) {
    used.clear();
    return list.map((text, index) => ({ text, index }));
  }
  return fresh;
}

function drawChallenge(kind, { reroll = false } = {}) {
  const pool = poolFor(kind);
  const item = pool[Math.floor(Math.random() * pool.length)];
  state.used[kind].add(item.index);
  state.lastPick = kind;

  els.choiceRow.hidden = true;
  els.challengeCard.hidden = false;
  els.challengeCard.dataset.kind = kind;
  els.challengeType.textContent = kind === "faz" ? "FAZ" : "BEBE";
  els.challengeText.textContent = item.text;
  const levelLabel = { leve: "Leve", medio: "Médio", pesado: "Pesado" }[state.level];
  els.challengeMeta.textContent = reroll
    ? `Nível ${levelLabel} · desafio trocado`
    : `Nível ${levelLabel} · ${kind === "faz" ? "faz o desafio ou bebe de castigo" : "bora hidratar"}`;
}

function finishTurn(action) {
  const player = currentPlayer();
  if (!player) return;
  if (action === "did") player.did += 1;
  if (action === "drank") player.drank += 1;
  state.round += 1;
  els.roundNum.textContent = String(state.round);
  els.spinName.textContent = "?";
  els.spinName.classList.remove("is-locked", "is-spinning");
  els.btnSpin.disabled = false;
  els.btnSpin.textContent = "Girar a roda";
  go("spin");
}

function renderScores() {
  const ranked = [...state.players].sort((a, b) => b.did + b.drank - (a.did + a.drank));
  els.scoresList.innerHTML = "";
  ranked.forEach((p, i) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span class="rank">${i + 1}</span>
      <span>${escapeHtml(p.name)}</span>
      <span class="stat">${p.did} fez · ${p.drank} bebeu</span>
    `;
    els.scoresList.appendChild(li);
  });
}

function openScores() {
  renderScores();
  els.scoresDialog.showModal();
}

function resetNight() {
  els.scoresDialog.close();
  state.currentPlayerId = null;
  state.round = 1;
  state.used = { faz: new Set(), bebe: new Set() };
  state.players.forEach((p) => {
    p.did = 0;
    p.drank = 0;
  });
  go("setup");
}

// Events
document.querySelectorAll("[data-go]").forEach((btn) => {
  btn.addEventListener("click", () => go(btn.dataset.go));
});

els.playerForm.addEventListener("submit", (e) => {
  e.preventDefault();
  addPlayer(els.playerInput.value);
});

els.btnStart.addEventListener("click", startNight);
els.btnSpin.addEventListener("click", spinWheel);
els.btnBackSpin.addEventListener("click", () => go("spin"));

document.querySelectorAll("[data-pick]").forEach((btn) => {
  btn.addEventListener("click", () => drawChallenge(btn.dataset.pick));
});

els.btnDidIt.addEventListener("click", () => finishTurn("did"));
els.btnDrank.addEventListener("click", () => finishTurn("drank"));
els.btnReroll.addEventListener("click", () => {
  if (!state.lastPick) return;
  drawChallenge(state.lastPick, { reroll: true });
});

document.getElementById("btn-scores").addEventListener("click", openScores);
document.getElementById("btn-scores-2").addEventListener("click", openScores);
els.btnResetNight.addEventListener("click", resetNight);

// boot
renderPlayers();
go("home");
})();
