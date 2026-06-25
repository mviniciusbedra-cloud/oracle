# FISCO-4926 - Contabilizacao automatica de NF entrada complemento ICMS

## Objetivo

Automatizar a contabilizacao das notas fiscais de entrada de complemento de
ICMS emitidas por fornecedores de industrializacao quando registradas no Fisco.

Exemplo informado pela area:

- Chave NF-e: `35251117160282000359550100000134471365751556`
- CNPJ emitente na chave: `17160282000359`
- Modelo: `55`
- Serie: `010`
- Numero NF: `000013447`
- Tipo emissao: `1`
- Codigo numerico: `36575155`
- Digito verificador: `6`

## Evidencias do PDF anexado

### Cenario funcional

As notas de complemento de ICMS de entrada, emitidas pelo fornecedor para a
Scania, nao estao contabilizando automaticamente apos o registro no Fisco.

Foi criada uma nova classe `3408` para isolar o fluxo de complemento de ICMS
com CFOP `x902` e finalidade `2`. A classe `3400` ja suportava NFs
complementares de ICMS com CFOP `x949`, mas o fluxo desejado deve ficar
separado porque as NFs de origem de remessa de industrializacao usam CFOP
`x901`.

Tambem foi criado setup contabil no FINE, mencionado como parametro `02/0158`,
com linhas adicionais para cobrir o retorno do ICMS. Mesmo assim, a
contabilizacao automatica nao funcionou.

### Lancamentos esperados

Para NF de saida de complemento de ICMS emitida pela Scania para fornecedor:

1. `D-1656.0000/V001`
2. `C-1651.SMXX`
3. `D-6998.CCusto`
4. `C-1656.0000/V001`

Para NF de entrada de complemento de ICMS emitida pelo fornecedor para a
Scania:

1. `D-1651.EMXX`
2. `C-1656.0000`
3. `D-1656.0000`
4. `C-6998.CCusto`

No fluxo atual da entrada, o email indica que ja ocorrem os dois primeiros
lancamentos e faltam:

1. `D-1656.0000`
2. `C-6998.CCusto`

### Parametros/contas citados

Email posterior da Tatiana informa substituicoes de parametros:

- Debito ICMS: parametro `9313` substituido por `0302`
- Credito ICMS: parametro `9323` substituido por `0303`

Mapeamento citado para NF entrada complemento ICMS fornecedor > Scania:

| Linha | Lancamento | Parametro antigo | Parametro atual | Conta atual |
| --- | --- | --- | --- | --- |
| 1 | `D-1651.EMXX` | `9313` | - | `040100062` |
| 2 | `C-1656.0000` | `9323` | - | `044200003` |
| 3 | `D-1656.0000` | - | `0302` | `044200003` |
| 4 | `C-6998.CCusto` | - | `0303` | `156100000` |

## Hipotese tecnica inicial

A criacao da classe `3408` e do setup contabil pode nao ser suficiente se o
motor de contabilizacao automatica:

- nao selecionar a classe `3408` para gerar contabilizacao;
- nao considerar finalidade NF-e `2` junto com CFOP `x902`;
- nao vincular o parametro FINE `02/0158` ao evento gerado pelo Fisco;
- gerar apenas as linhas antigas `9313`/`9323`, sem acionar as novas linhas
  `0302`/`0303`;
- depender de alguma interface/evento intermediario que nao esta sendo gravado
  para esta classe.

Antes de alterar codigo, a investigacao deve confirmar se a falha esta em
setup de regra contabil, no roteamento Fisco -> FINE, ou na rotina que monta as
linhas contabeis.

## Roteiro tecnico recomendado

1. Localizar a NF da chave exemplo em `TFC_NF_ENTRADA`.
2. Confirmar nos itens da NF:
   - classe `3408`;
   - CFOP `x902`;
   - finalidade NF-e `2`;
   - fornecedor/industrializacao.
3. Comparar com uma NF complementar que contabiliza corretamente pela classe
   `3400`/CFOP `x949`.
4. Identificar a rotina, trigger ou job que gera a contabilizacao automatica
   apos o registro no Fisco.
5. Verificar se essa rotina consulta classe, CFOP, finalidade, parametro FINE
   ou algum evento contabil intermediario.
6. Validar se o setup `02/0158` esta ativo e se suas quatro linhas foram
   consideradas para classe `3408`.
7. Se a regra for data-driven, ajustar somente o setup.
8. Se houver filtro codificado, alterar a rotina para incluir o fluxo
   `classe 3408 + CFOP x902 + finalidade 2`, preservando idempotencia para nao
   duplicar contabilizacoes.

## Criterios de aceite sugeridos

- Ao registrar no Fisco uma NF-e de entrada de complemento de ICMS de
  fornecedor de industrializacao, classe `3408`, CFOP `x902` e finalidade `2`,
  o sistema gera automaticamente as quatro linhas contabeis esperadas.
- A NF exemplo `35251117160282000359550100000134471365751556` deixa de ficar
  apenas com os lancamentos `D-1651`/`C-1656` e passa a gerar tambem
  `D-1656`/`C-6998`.
- O ajuste nao afeta NFs de remessa `x901`, NFs complementares `x949` ja
  suportadas pela classe `3400`, nem outros tipos de complemento.
- Reprocessamento da mesma NF nao duplica linhas contabeis.

## Observacao sobre este repositorio

Nesta branch, o repositorio contem apenas artefatos de documentacao. Os fontes
PL/SQL/FISCO/FINE necessarios para implementar a regra nao estao versionados
aqui. O arquivo `diagnostico.sql` traz consultas para executar no ambiente
Oracle e fechar o ponto exato de alteracao.
