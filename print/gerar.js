/**
 * FAZ OU BEBE — folhas A4 pra impressão
 * Carta: 63 × 88 mm (padrão pôquer)
 * 9 cartas por folha (3×3) com linhas de corte
 */
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const desafios = JSON.parse(fs.readFileSync(path.join(ROOT, "desafios.json"), "utf8"));
const PER_PAGE = 9;
const COLS = 3;

const CATS = {
  beba: { label: "BEBA", icon: "🍺", color: "#F0A500", ink: "#1a1000" },
  todos: { label: "TODOS", icon: "👥", color: "#3DB8A8", ink: "#041512" },
  desafio: { label: "DESAFIO", icon: "🎯", color: "#D6FF3F", ink: "#121800" },
  escolha: { label: "ESCOLHA", icon: "🤝", color: "#FF6B45", ink: "#1a0800" },
  historia: { label: "HISTÓRIA", icon: "🧠", color: "#7EB6FF", ink: "#041018" },
  coringa: { label: "CORINGA", icon: "⭐", color: "#FFD166", ink: "#1a1400" },
  fim: { label: "FINAL", icon: "🏆", color: "#F3EEE4", ink: "#111" },
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
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Manrope:wght@600;700;800&display=swap');

  :root {
    --black: #0a0a0a;
    --ink: #f6f2ea;
    --card-w: 63mm;
    --card-h: 88mm;
    --gap: 2mm;
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
    padding: 14.5mm 9.5mm;
    display: grid;
    grid-template-columns: repeat(3, var(--card-w));
    grid-template-rows: repeat(3, var(--card-h));
    gap: var(--gap);
    justify-content: center;
    align-content: center;
    page-break-after: always;
    break-after: page;
    position: relative;
  }
  .sheet:last-child { page-break-after: auto; break-after: auto; }

  .card {
    width: var(--card-w);
    height: var(--card-h);
    background: var(--black);
    color: var(--ink);
    position: relative;
    overflow: hidden;
    border: 0.3mm solid #222;
  }
  .card.empty {
    visibility: hidden;
    border-color: transparent;
  }

  /* cut marks */
  .sheet::before {
    content: "";
    position: absolute;
    inset: 10mm 6mm;
    border: 0.15mm dashed #bbb;
    pointer-events: none;
  }

  /* —— VERSO —— */
  .card-back {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 5mm;
    background:
      radial-gradient(90% 70% at 50% 100%, #1c1c1c 0%, transparent 60%),
      var(--black);
  }
  .card-back .frame {
    position: absolute;
    inset: 3mm;
    border: 0.4mm solid #2e2e2e;
    pointer-events: none;
  }
  .card-back .brand {
    font-family: "Bebas Neue", Impact, sans-serif;
    font-size: 14mm;
    line-height: 0.86;
    letter-spacing: 0.03em;
    margin: 0;
    color: #fff;
  }
  .card-back .brand span { display: block; }
  .card-back .ou {
    color: #FF6B45;
    font-size: 5.5mm;
    letter-spacing: 0.32em;
    margin: 1.5mm 0 1mm;
  }
  .card-back .hint {
    margin-top: 5mm;
    font-size: 2.6mm;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #888;
    font-weight: 700;
  }
  .card-back .cats {
    margin-top: 6mm;
    display: flex;
    gap: 1.5mm;
    font-size: 3.2mm;
  }

  /* —— FRENTE —— */
  .card-front {
    display: flex;
    flex-direction: column;
    background: var(--black);
  }
  .head {
    display: flex;
    align-items: center;
    gap: 2mm;
    padding: 3.2mm 3.5mm;
    font-family: "Bebas Neue", Impact, sans-serif;
    font-size: 6.5mm;
    letter-spacing: 0.06em;
    line-height: 1;
    font-weight: 400;
  }
  .head .icon { font-size: 5.5mm; line-height: 1; }
  .body {
    flex: 1;
    display: flex;
    align-items: center;
    padding: 4mm 3.8mm 3mm;
  }
  .texto {
    margin: 0;
    width: 100%;
    font-size: 5.2mm;
    line-height: 1.22;
    font-weight: 800;
    color: #fff;
  }
  .texto.long { font-size: 4.4mm; }
  .texto.xl { font-size: 3.8mm; }
  .foot {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2.4mm 3.5mm 3mm;
    border-top: 0.3mm solid #222;
    font-size: 2.3mm;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #666;
    font-weight: 700;
  }
  .foot .num { color: #999; letter-spacing: 0.08em; }

  @page { size: A4; margin: 0; }

  @media screen {
    body { background: #c8c8c8; padding: 12px; }
    .sheet {
      background: #fff;
      margin: 0 auto 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,.2);
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
      <div class="cats" aria-hidden="true">🍺👥🎯🤝🧠⭐</div>
    </article>`;
}

function frontCard(d) {
  if (!d) return `<article class="card empty"></article>`;
  const meta = CATS[d.cat] || CATS.desafio;
  const len = d.texto.length;
  const size = len > 110 ? " xl" : len > 80 ? " long" : "";
  return `
    <article class="card card-front">
      <div class="head" style="background:${meta.color};color:${meta.ink}">
        <span class="icon">${meta.icon}</span>
        <span>${meta.label}</span>
      </div>
      <div class="body">
        <p class="texto${size}">${escapeHtml(d.texto)}</p>
      </div>
      <div class="foot">
        <span>faz ou bebe</span>
        <span class="num">#${String(d.n).padStart(3, "0")}</span>
      </div>
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

const counts = {};
sorted.forEach((c) => {
  counts[c.cat] = (counts[c.cat] || 0) + 1;
});

const preview = documentHtml(
  "FAZ OU BEBE — Preview",
  `
  <div style="max-width:210mm;margin:0 auto 16px;padding:14px;background:#fff;color:#111;font-family:Manrope,sans-serif">
    <h1 style="margin:0;font-family:Bebas Neue,sans-serif;font-size:48px;letter-spacing:.03em">FAZ OU BEBE</h1>
    <p style="margin:8px 0 0;line-height:1.45"><strong>${sorted.length} cartas</strong> · 63×88 mm (pôquer) · 9 por folha A4 · ${pagesNeeded} folhas</p>
    <p style="margin:6px 0 0;font-size:14px;color:#444">${Object.entries(counts)
      .map(([k, v]) => `${(CATS[k] || {}).icon || ""} ${v}`)
      .join(" · ")}</p>
  </div>
  ${frentePages.slice(0, 2).join("\n")}
  `
);
fs.writeFileSync(path.join(ROOT, "preview.html"), preview);

console.log(`OK: ${sorted.length} cartas, ${pagesNeeded} folhas`);
console.log(counts);
