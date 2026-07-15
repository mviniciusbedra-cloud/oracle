/**
 * FAZ OU BEBE — cartas 63×88 mm (pôquer), cantos arredondados
 * Layout: categoria grande no topo · ícone no meio · comando embaixo
 */
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const desafios = JSON.parse(fs.readFileSync(path.join(ROOT, "desafios.json"), "utf8"));
const PER_PAGE = 9;
const COLS = 3;

const CATS = {
  beba: {
    label: "BEBA",
    icon: `<svg viewBox="0 0 80 90" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M18 28h36l-3 48c-.4 5-4.5 9-9.5 9H30.5c-5 0-9.1-4-9.5-9L18 28z" fill="#F5C542"/>
      <path d="M20 28h32v10H20z" fill="#FFE9A0"/>
      <path d="M18 28c0-8 8-14 18-14s18 6 18 14" fill="#FFF8E8"/>
      <ellipse cx="36" cy="16" rx="16" ry="7" fill="#FFF"/>
      <path d="M54 34h10c5 0 9 4 9 9v10c0 5-4 9-9 9H51" fill="none" stroke="#F5C542" stroke-width="5" stroke-linecap="round"/>
      <path d="M26 48c6 3 14 3 20 0" fill="none" stroke="#E8A820" stroke-width="2" opacity=".5"/>
    </svg>`,
  },
  todos: {
    label: "TODOS",
    icon: `<svg viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <rect x="8" y="8" width="74" height="74" rx="10" fill="none" stroke="#9B6BFF" stroke-width="4"/>
      <circle cx="30" cy="34" r="9" fill="#C4A8FF"/>
      <circle cx="45" cy="28" r="11" fill="#E8DCFF"/>
      <circle cx="60" cy="34" r="9" fill="#C4A8FF"/>
      <path d="M16 68c2-12 10-18 21-18h6c11 0 19 6 21 18" fill="#C4A8FF"/>
      <path d="M28 62c2-10 8-14 17-14s15 4 17 14" fill="#E8DCFF"/>
    </svg>`,
  },
  desafio: {
    label: "DESAFIO",
    icon: `<svg viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="45" cy="45" r="32" fill="none" stroke="#D6FF3F" stroke-width="5"/>
      <circle cx="45" cy="45" r="20" fill="none" stroke="#D6FF3F" stroke-width="4"/>
      <circle cx="45" cy="45" r="8" fill="#D6FF3F"/>
      <path d="M45 8v10M45 72v10M8 45h10M72 45h10" stroke="#D6FF3F" stroke-width="4" stroke-linecap="round"/>
    </svg>`,
  },
  escolha: {
    label: "ESCOLHA",
    icon: `<svg viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M18 48c0-8 6-14 14-14h8l6 8 6-8h8c8 0 14 6 14 14v6c0 10-8 18-18 18H36c-10 0-18-8-18-18v-6z" fill="#FF6B45"/>
      <path d="M32 38c-4-10 2-18 12-18 6 0 10 3 12 8 2-5 6-8 12-8 10 0 16 8 12 18" fill="none" stroke="#FF8F70" stroke-width="4" stroke-linecap="round"/>
      <circle cx="38" cy="52" r="3" fill="#FFD2C4"/>
      <circle cx="52" cy="52" r="3" fill="#FFD2C4"/>
    </svg>`,
  },
  historia: {
    label: "HISTÓRIA",
    icon: `<svg viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M28 22c-10 4-16 14-16 26 0 16 12 28 28 30 16-2 28-14 28-30 0-12-6-22-16-26-4 10-12 14-24 14s-20-4-24-14z" fill="#7EB6FF"/>
      <path d="M36 30c-2 8-8 12-16 14 4 8 12 14 25 15 13-1 21-7 25-15-8-2-14-6-16-14-4 4-10 6-18 6z" fill="#B7D8FF"/>
      <circle cx="38" cy="48" r="3.5" fill="#041018"/>
      <circle cx="52" cy="48" r="3.5" fill="#041018"/>
      <path d="M40 70v10M50 70v10" stroke="#7EB6FF" stroke-width="4" stroke-linecap="round"/>
      <path d="M34 82h22" stroke="#7EB6FF" stroke-width="4" stroke-linecap="round"/>
    </svg>`,
  },
  coringa: {
    label: "CORINGA",
    icon: `<svg viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M45 10l8 22h23l-18 14 7 23-20-14-20 14 7-23-18-14h23z" fill="#FFD166"/>
      <path d="M45 22l5 14h15l-12 9 4 15-12-9-12 9 4-15-12-9h15z" fill="#FFE9A8"/>
    </svg>`,
  },
  fim: {
    label: "FINAL",
    icon: `<svg viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M28 20h34v8c0 12-8 22-17 26v8h10v6H35v-6h10v-8c-9-4-17-14-17-26V20z" fill="#F3EEE4"/>
      <rect x="30" y="68" width="30" height="6" rx="2" fill="#F3EEE4"/>
      <rect x="24" y="76" width="42" height="8" rx="2" fill="#F3EEE4"/>
      <circle cx="45" cy="34" r="6" fill="#FFD166"/>
    </svg>`,
  },
};

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

function mirrorPage(cards) {
  const rows = chunk(cards, COLS);
  return rows.flatMap((row) => {
    const padded = [...row];
    while (padded.length < COLS) padded.push(null);
    return padded.reverse();
  });
}

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@700&family=Manrope:wght@600;700;800&display=swap');

  :root {
    --black: #000;
    --red: #C62828;
    --ink: #ffffff;
    --muted: #8a8a8a;
    --card-w: 63mm;
    --card-h: 88mm;
    --gap: 2.5mm;
    --radius: 4.5mm;
  }

  * { box-sizing: border-box; }
  html, body {
    margin: 0;
    padding: 0;
    background: #fff;
    font-family: "Manrope", system-ui, sans-serif;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .sheet {
    width: 210mm;
    height: 297mm;
    padding: 14mm 8.5mm;
    display: grid;
    grid-template-columns: repeat(3, var(--card-w));
    grid-template-rows: repeat(3, var(--card-h));
    gap: var(--gap);
    justify-content: center;
    align-content: center;
    page-break-after: always;
    break-after: page;
  }
  .sheet:last-child { page-break-after: auto; break-after: auto; }

  .card {
    width: var(--card-w);
    height: var(--card-h);
    background: var(--black);
    color: var(--ink);
    border-radius: var(--radius);
    position: relative;
    overflow: hidden;
  }
  .card.empty { visibility: hidden; }

  /* —— VERSO —— */
  .card-back {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 6mm;
    background:
      radial-gradient(80% 60% at 50% 110%, #1a1a1a 0%, transparent 55%),
      #000;
  }
  .card-back .frame {
    position: absolute;
    inset: 3.5mm;
    border: 0.45mm solid #2a2a2a;
    border-radius: 3mm;
    pointer-events: none;
  }
  .card-back .brand {
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 9.5mm;
    line-height: 0.95;
    margin: 0;
    color: #fff;
    font-weight: 700;
  }
  .card-back .brand span { display: block; }
  .card-back .ou {
    color: var(--red);
    font-size: 5mm;
    letter-spacing: 0.2em;
    margin: 1.8mm 0 1.2mm;
  }
  .card-back .hint {
    margin-top: 6mm;
    font-size: 2.5mm;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 700;
    font-family: "Manrope", sans-serif;
  }

  /* —— FRENTE —— */
  .card-front {
    display: grid;
    grid-template-rows: auto 1fr auto auto;
    padding: 5.5mm 4.5mm 4mm;
    text-align: center;
  }
  .cat {
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 9mm;
    line-height: 1;
    color: var(--red);
    font-weight: 700;
    letter-spacing: 0.02em;
    margin: 0;
  }
  .icon-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 28mm;
    padding: 2mm 0;
  }
  .icon-wrap svg {
    width: 22mm;
    height: 22mm;
    display: block;
  }
  .texto {
    margin: 0;
    font-size: 4.6mm;
    line-height: 1.25;
    font-weight: 800;
    color: #fff;
    padding: 0 1mm 2mm;
  }
  .texto.long { font-size: 3.9mm; }
  .texto.xl { font-size: 3.4mm; }
  .num {
    position: absolute;
    right: 4mm;
    bottom: 3.2mm;
    font-size: 2.4mm;
    color: var(--muted);
    font-weight: 700;
    letter-spacing: 0.04em;
  }

  @page { size: A4; margin: 0; }

  @media screen {
    body { background: #d0d0d0; padding: 14px; }
    .sheet {
      background: #fff;
      margin: 0 auto 18px;
      box-shadow: 0 12px 32px rgba(0,0,0,.2);
    }
  }
`;

function backCard() {
  return `
    <article class="card card-back">
      <div class="frame"></div>
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
  const meta = CATS[d.cat] || CATS.desafio;
  const len = d.texto.length;
  const size = len > 100 ? " xl" : len > 70 ? " long" : "";
  return `
    <article class="card card-front">
      <h2 class="cat">${escapeHtml(meta.label)}</h2>
      <div class="icon-wrap">${meta.icon}</div>
      <p class="texto${size}">${escapeHtml(d.texto)}</p>
      <span class="num">#${String(d.n).padStart(3, "0")}</span>
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

const sorted = [...desafios].sort((a, b) => a.n - b.n);
const pagesNeeded = Math.ceil(sorted.length / PER_PAGE);

const versoPages = [];
for (let i = 0; i < pagesNeeded; i += 1) {
  const slots = Array.from({ length: PER_PAGE }, () => "x");
  const mirrored = mirrorPage(slots);
  versoPages.push(
    page(mirrored.map((s) => (s ? backCard() : `<article class="card empty"></article>`)))
  );
}

const frentePages = [];
chunk(sorted, PER_PAGE).forEach((group) => {
  const slots = [...group];
  while (slots.length < PER_PAGE) slots.push(null);
  frentePages.push(page(slots.map(frontCard)));
});

fs.writeFileSync(path.join(ROOT, "verso.html"), documentHtml("FAZ OU BEBE — Verso", versoPages.join("\n")));
fs.writeFileSync(path.join(ROOT, "frente.html"), documentHtml("FAZ OU BEBE — Frente", frentePages.join("\n")));

const sample = documentHtml(
  "FAZ OU BEBE — Sample",
  page(sorted.slice(0, 9).map(frontCard))
);
fs.writeFileSync(path.join(ROOT, "sample.html"), sample);

console.log(`OK: ${sorted.length} cartas · ${pagesNeeded} folhas · estilo referência`);
