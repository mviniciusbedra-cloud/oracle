# FAZ OU BEBE — cartas pra imprimir

Baralho em formato **cartão de visita** (90×50 mm), fundo preto:

- **Verso:** marca FAZ OU BEBE (igual em todas) — pra embaralhar
- **Frente:** desafio FAZ (verde) ou BEBE (vermelho)

60 cartas · 6 folhas A4 · 10 cartas por folha

## Arquivos prontos

| Arquivo | Pra quê |
|---|---|
| [`print/verso.pdf`](print/verso.pdf) | Costas das cartas (imprime primeiro) |
| [`print/frente.pdf`](print/frente.pdf) | Desafios (imprime no verso da mesma folha) |
| [`print/desafios.json`](print/desafios.json) | Textos — edite e regenere se quiser |

## Como imprimir

1. Papel A4 (180–250 g/m² fica melhor pra recortar; sulfite também rola).
2. Imprima **`verso.pdf`**.
3. Coloque as folhas de volta na impressora (frente e verso / duplex).
4. Imprima **`frente.pdf`** nas **mesmas folhas**, na mesma ordem.
5. Na impressora, use **virar na borda longa** (flip on long edge).
6. Recorte nas bordas pretas das cartas.

### Dica de alinhamento
Faça um teste com 1 folha antes do pacote inteiro. Se o texto não bater com o verso, inverta a orientação ao recolocar o papel.

## Como jogar

1. Embaralhe o baralho (verso pra cima).
2. A pessoa da vez tira uma carta.
3. **FAZ** = faz o desafio (ou bebe de castigo).
4. **BEBE** = bebe o que a carta mandar.
5. Níveis: leve · médio · pesado.

## Regenerar as folhas

Se editar `print/desafios.json`:

```bash
cd print
node gerar.js
```

Depois abra `frente.html` / `verso.html` no Chrome e imprima em PDF  
(ou use os PDFs já gerados nesta pasta).

## Modelo da sua namorada

Não achei o arquivo de referência no repositório.  
Se você mandar o modelo (foto, PDF, Canva, etc.), eu adapto o layout pra ficar igual — mantendo o formato de impressão.
