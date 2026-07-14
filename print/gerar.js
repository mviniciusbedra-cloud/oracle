/**
 * Gera folhas A4 prontas pra impressão frente e verso.
 * Cartão: 90×50 mm (estilo cartão de visita).
 * 10 cartas por folha (2 colunas × 5 linhas).
 */
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const desafios = JSON.parse(fs.readFileSync(path.join(ROOT, "desafios.json"), "utf8"));
const PER_PAGE = 10;
const COLS = 2;

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

/** Espelha colunas pra alinhar no verso (virar na borda longa). */
function mirrorPage(cards) {
  const rows = chunk(cards, COLS);
  return rows.flatMap((row) => {
    const padded = [...row];
    while (padded.length < COLS) padded.push(null);
    return padded.reverse();
  });
}

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Manrope:wght@500;700;800&display=swap');

  :root {
    --black: #050505;
    --ink: #f3eee4;
    --faz: #d6ff3f;
    --bebe: #ff5a3c;
    --mute: #8a8a8a;
    --card-w: 90mm;
    --card-h: 50mm;
  }

  * { box-sizing: border-box; }
  html, body {
    margin: 0;
    padding: 0;
    background: #fff;
    color: var(--ink);
    font-family: "Manrope", system-ui, sans-serif;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .sheet {
    width: 210mm;
    height: 297mm;
    padding: 18.5mm 15mm;
    display: grid;
    grid-template-columns: repeat(2, var(--card-w));
    grid-template-rows: repeat(5, var(--card-h));
    gap: 0;
    justify-content: space-between;
    align-content: space-between;
    page-break-after: always;
    break-after: page;
  }
  .sheet:last-child {
    page-break-after: auto;
    break-after: auto;
  }

  .card {
    width: var(--card-w);
    height: var(--card-h);
    background: var(--black);
    color: var(--ink);
    position: relative;
    overflow: hidden;
    border: 0.2mm solid #1a1a1a;
  }
  .card.empty { visibility: hidden; }

  /* —— VERSO (costas / embaralhar) —— */
  .card-back {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 4mm;
    background:
      radial-gradient(120% 80% at 50% 120%, #1a1a1a 0%, transparent 55%),
      var(--black);
  }
  .card-back .brand {
    font-family: "Bebas Neue", Impact, sans-serif;
    font-size: 15mm;
    line-height: 0.85;
    letter-spacing: 0.04em;
    margin: 0;
  }
  .card-back .brand span { display: block; }
  .card-back .ou {
    color: var(--bebe);
    font-size: 5.5mm;
    letter-spacing: 0.35em;
    margin: 1.2mm 0 0.8mm;
  }
  .card-back .hint {
    margin-top: 3mm;
    font-size: 2.4mm;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--mute);
    font-weight: 700;
  }
  .card-back .frame {
    position: absolute;
    inset: 2.2mm;
    border: 0.35mm solid #2a2a2a;
    pointer-events: none;
  }

  /* —— FRENTE (desafio) —— */
  .card-front {
    display: flex;
    flex-direction: column;
    padding: 3mm 3.8mm 2.8mm;
    background: var(--black);
  }
  .card-front .top {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 1.2mm;
  }
  .badge {
    font-family: "Bebas Neue", Impact, sans-serif;
    font-size: 11mm;
    letter-spacing: 0.06em;
    line-height: 0.9;
  }
  .badge.faz { color: var(--faz); }
  .badge.bebe { color: var(--bebe); }
  .nivel {
    font-size: 2.8mm;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--mute);
    font-weight: 700;
  }
  .texto {
    margin: 0;
    flex: 1;
    font-size: 5mm;
    line-height: 1.22;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
  }
  .texto.long { font-size: 4.2mm; }
  .texto.xl { font-size: 3.7mm; }
  .foot {
    margin-top: auto;
    padding-top: 1.2mm;
    border-top: 0.25mm solid #222;
    font-size: 2.2mm;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #666;
    font-weight: 700;
  }

  @page {
    size: A4;
    margin: 0;
  }

  @media screen {
    body {
      background: #cfcfcf;
      padding: 12px;
    }
    .sheet {
      background: #fff;
      margin: 0 auto 16px;
      box-shadow: 0 8px 28px rgba(0,0,0,.18);
    }
  }
`;

function backCard() {
  return `
    <article class="card card-back">
      <div class="frame" aria-hidden="true"></div>
      <h2 class="brand">
        <span>FAZ</span>
        <span class="ou">OU</span>
        <span>BEBE</span>
      </h2>
      <p class="hint">embaralhe · tire uma</p>
    </article>`;
}

function frontCard(d) {
  if (!d) return `<article class="card empty"></article>`;
  const len = d.texto.length;
  const sizeClass = len > 95 ? " xl" : len > 70 ? " long" : "";
  const nivelLabel = { leve: "leve", medio: "médio", pesado: "pesado" }[d.nivel] || d.nivel;
  return `
    <article class="card card-front">
      <div class="top">
        <span class="badge ${d.tipo.toLowerCase()}">${escapeHtml(d.tipo)}</span>
        <span class="nivel">${escapeHtml(nivelLabel)}</span>
      </div>
      <p class="texto${sizeClass}">${escapeHtml(d.texto)}</p>
      <p class="foot">faz ou bebe</p>
    </article>`;
}

function page(cardsHtml) {
  return `<section class="sheet">${cardsHtml.join("")}</section>`;
}

function documentHtml(title, body) {
  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>${escapeHtml(title)}</title>
  <style>${css}</style>
</head>
<body>
${body}
</body>
</html>`;
}

// —— VERSO: mesmas costas, espelhadas por página pra duplex ——
const pagesNeeded = Math.ceil(desafios.length / PER_PAGE);
const versoPages = [];
for (let i = 0; i < pagesNeeded; i += 1) {
  const slots = Array.from({ length: PER_PAGE }, () => "x");
  const mirrored = mirrorPage(slots);
  versoPages.push(page(mirrored.map((s) => (s ? backCard() : `<article class="card empty"></article>`))));
}

// —— FRENTE: desafios; última página completa com vazios ——
const frentePages = [];
const challengePages = chunk(desafios, PER_PAGE);
challengePages.forEach((group) => {
  const slots = [...group];
  while (slots.length < PER_PAGE) slots.push(null);
  // Frente NÃO espelha — o verso é que espelha no duplex
  frentePages.push(page(slots.map(frontCard)));
});

fs.writeFileSync(path.join(ROOT, "verso.html"), documentHtml("FAZ OU BEBE — Verso", versoPages.join("\n")));
fs.writeFileSync(path.join(ROOT, "frente.html"), documentHtml("FAZ OU BEBE — Frente", frentePages.join("\n")));

// Preview combinado (só tela / referência)
const preview = documentHtml(
  "FAZ OU BEBE — Preview",
  `
  <div style="max-width:210mm;margin:0 auto 20px;padding:12px;font-family:Manrope,sans-serif;color:#111;background:#fff">
    <h1 style="margin:0 0 8px;font-family:Bebas Neue,sans-serif;font-size:42px;letter-spacing:.04em">FAZ OU BEBE</h1>
    <p style="margin:0;line-height:1.45"><strong>${desafios.length} cartas</strong> · 90×50 mm · 10 por folha A4.<br/>
    Imprima <em>verso.pdf</em> e <em>frente.pdf</em> frente e verso (virar na borda longa), depois recorte.</p>
  </div>
  ${frentePages.join("\n")}
  `
);
fs.writeFileSync(path.join(ROOT, "preview.html"), preview);

console.log(`OK: ${desafios.length} cartas, ${pagesNeeded} folhas`);
