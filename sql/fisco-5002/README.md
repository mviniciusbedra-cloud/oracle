# FISCO 5002 - Automatizacao da escrituracao de NF de embalagens

## Objetivo

Automatizar a escrituracao/liberacao das notas fiscais de embalagens capturadas no painel de recepcao quando nao houver entrada manual dentro do prazo definido.

## Regra implementada

O script `fisco_5002_auto_nf_embalagem.sql` cria o procedimento `PRC_FISCO_5002_AUTO_NF_EMBALAGEM` e agenda o job `JOB_FISCO_5002_AUTO_NF_EMBALAGEM`.

Uma nota fiscal sera selecionada quando atender todos os criterios:

- Existir em `TFC_NF_ENTRADA`;
- Estar pendente de entrada (`DATA_ENTRADA IS NULL`);
- Possuir chave de NF preenchida;
- Ter data de emissao com 60 dias ou mais (`TRUNC(DATA_NF) <= TRUNC(SYSDATE) - 60`);
- Possuir item em `TFC_ITEM_NF_ENTRADA` com:
  - `CLASSE_NF` em `0709` ou `0472`;
  - `NAT_OPERACAO` em `5920`, `5921`, `6920` ou `6921`.

As chaves encontradas sao enviadas para `PFC_XML_AUTO.PRC_LIBERA_ENTRADA`, que executa a liberacao automatica da entrada/capa de lote conforme comportamento ja existente no sistema.

## Diferenca em relacao ao esboco inicial

O filtro de data foi ajustado para considerar NFs emitidas ha 60 dias ou mais.

No esboco, a condicao `DATA_NF >= SYSDATE - 60` selecionaria NFs dos ultimos 60 dias, que ainda estariam dentro do prazo operacional. A regra da area pede o processamento automatico apos 60 dias da emissao.

## Agendamento

O job e criado habilitado e executa diariamente as 02:00:

```sql
FREQ=DAILY;BYHOUR=2;BYMINUTE=0;BYSECOND=0
```

Caso seja necessario alterar a janela de execucao, ajuste o atributo `repeat_interval` no script antes da implantacao.

## Execucao manual

Para executar manualmente:

```sql
SET SERVEROUTPUT ON;

DECLARE
    l_retorno VARCHAR2(1000);
BEGIN
    prc_fisco_5002_auto_nf_embalagem(
        p_dias_emissao => 60,
        p_retorno      => l_retorno
    );

    DBMS_OUTPUT.PUT_LINE(l_retorno);
END;
/
```

## Dependencias esperadas

- Permissao de leitura em `TFC_NF_ENTRADA`;
- Permissao de leitura em `TFC_ITEM_NF_ENTRADA`;
- Permissao de execucao em `PFC_XML_AUTO.PRC_LIBERA_ENTRADA`;
- Permissao de uso do `DBMS_SCHEDULER` para criacao/alteracao do job.
