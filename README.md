# FAZ OU BEBE

## Jogar agora (jeito fácil)

O GitHub **mostra o código** quando você clica no `.html` — isso é normal.  
Pra abrir o **jogo de verdade**, faça assim:

### Opção 1 — baixar e abrir (recomendado)

1. Clique neste link pra **baixar** o jogo:  
   **[⬇️ Baixar jogar.html](https://github.com/mviniciusbedra-cloud/oracle/raw/cursor/faz-ou-bebe-game-d814/jogar.html)**
2. Abra o arquivo baixado no celular ou no computador (toque / clique duas vezes).
3. O navegador abre o jogo. Pode passar o aparelho na roda.

> Dica: se o navegador mostrar texto em vez do jogo, salve o arquivo na pasta Downloads e abra de lá.

### Opção 2 — pelo terminal

Na pasta do projeto:

```bash
npx --yes serve .
```

Abra o link que aparecer (ex.: `http://localhost:3000`).

---

## Como funciona

1. Adicione pelo menos 2 jogadores.
2. Escolha o nível: **Leve**, **Médio** ou **Pesado**.
3. Gire a roda → a pessoa escolhe **FAZ** (desafio) ou **BEBE** (gole).
4. Marque **Fez!** ou **Bebeu**.
5. O placar (★) mostra quem mais fez e quem mais bebeu.

Os desafios ficam em `js/challenges.js` (e também embutidos no `jogar.html`).

Jogue com consentimento, hidratação e bom senso.
