SET DEFINE ON
SET SERVEROUTPUT ON
SET LINESIZE 240
SET PAGESIZE 200
SET TRIMSPOOL ON

PROMPT FISCO-4926 - Diagnostico NF entrada complemento ICMS fornecedor > Scania
PROMPT Ajuste a chave abaixo se for investigar outra NF.

DEFINE chave_nfe = '35251117160282000359550100000134471365751556'

PROMPT
PROMPT 1) Capa da NF no Fisco
PROMPT

SELECT *
  FROM tfc_nf_entrada n
 WHERE n.chave = '&&chave_nfe';

PROMPT
PROMPT 2) Itens da NF no Fisco
PROMPT    Confirmar classe 3408 e CFOP x902.
PROMPT

SELECT i.*
  FROM tfc_item_nf_entrada i
 WHERE EXISTS (
           SELECT 1
             FROM tfc_nf_entrada n
            WHERE n.id_nf = i.id_nf
              AND n.chave = '&&chave_nfe'
       )
 ORDER BY i.id_nf;

PROMPT
PROMPT 3) Resumo de classe/CFOP da NF exemplo
PROMPT

SELECT i.id_nf,
       i.classe_nf,
       i.nat_operacao,
       COUNT(*) AS qtd_itens
  FROM tfc_item_nf_entrada i
 WHERE EXISTS (
           SELECT 1
             FROM tfc_nf_entrada n
            WHERE n.id_nf = i.id_nf
              AND n.chave = '&&chave_nfe'
       )
 GROUP BY i.id_nf,
          i.classe_nf,
          i.nat_operacao
 ORDER BY i.id_nf,
          i.classe_nf,
          i.nat_operacao;

PROMPT
PROMPT 4) Outras NFs candidatas com classe 3408 e CFOP x902
PROMPT    Use para comparar casos contabilizados e nao contabilizados.
PROMPT

SELECT n.id_nf,
       n.chave,
       n.data_nf,
       n.data_entrada,
       i.classe_nf,
       i.nat_operacao,
       COUNT(*) AS qtd_itens
  FROM tfc_nf_entrada n
  JOIN tfc_item_nf_entrada i
    ON i.id_nf = n.id_nf
 WHERE i.classe_nf = '3408'
   AND SUBSTR(i.nat_operacao, 2, 3) = '902'
 GROUP BY n.id_nf,
          n.chave,
          n.data_nf,
          n.data_entrada,
          i.classe_nf,
          i.nat_operacao
 ORDER BY n.data_entrada DESC NULLS LAST,
          n.id_nf DESC
 FETCH FIRST 100 ROWS ONLY;

PROMPT
PROMPT 5) Comparativo: NFs classe 3400 com CFOP x949
PROMPT

SELECT n.id_nf,
       n.chave,
       n.data_nf,
       n.data_entrada,
       i.classe_nf,
       i.nat_operacao,
       COUNT(*) AS qtd_itens
  FROM tfc_nf_entrada n
  JOIN tfc_item_nf_entrada i
    ON i.id_nf = n.id_nf
 WHERE i.classe_nf = '3400'
   AND SUBSTR(i.nat_operacao, 2, 3) = '949'
 GROUP BY n.id_nf,
          n.chave,
          n.data_nf,
          n.data_entrada,
          i.classe_nf,
          i.nat_operacao
 ORDER BY n.data_entrada DESC NULLS LAST,
          n.id_nf DESC
 FETCH FIRST 100 ROWS ONLY;

PROMPT
PROMPT 6) Localizar tabelas de setup com colunas relacionadas a classe/parametro/conta
PROMPT

SELECT owner,
       table_name,
       column_name
  FROM all_tab_columns
 WHERE owner NOT IN ('SYS', 'SYSTEM')
   AND (
           UPPER(column_name) LIKE '%CLASSE%'
        OR UPPER(column_name) LIKE '%NAT_OPER%'
        OR UPPER(column_name) LIKE '%CFOP%'
        OR UPPER(column_name) LIKE '%PARAM%'
        OR UPPER(column_name) LIKE '%CONTA%'
        OR UPPER(column_name) LIKE '%FINALIDADE%'
       )
 ORDER BY owner,
          table_name,
          column_id;

PROMPT
PROMPT 7) Localizar fontes que citam a classe 3408, parametro 0158 ou CFOP 902
PROMPT

SELECT owner,
       name,
       type,
       line,
       text
  FROM all_source
 WHERE UPPER(text) LIKE '%3408%'
    OR UPPER(text) LIKE '%0158%'
    OR UPPER(text) LIKE '%X902%'
    OR UPPER(text) LIKE '%''902''%'
 ORDER BY owner,
          name,
          type,
          line;

PROMPT
PROMPT 8) Localizar fontes provaveis de contabilizacao Fisco/FINE
PROMPT

SELECT owner,
       name,
       type,
       line,
       text
  FROM all_source
 WHERE (
           UPPER(text) LIKE '%CONTABIL%'
        OR UPPER(text) LIKE '%FINE%'
        OR UPPER(text) LIKE '%PARAMETRO%'
        OR UPPER(text) LIKE '%TFC_NF_ENTRADA%'
       )
   AND (
           UPPER(text) LIKE '%CLASSE_NF%'
        OR UPPER(text) LIKE '%NAT_OPERACAO%'
        OR UPPER(text) LIKE '%DATA_ENTRADA%'
        OR UPPER(text) LIKE '%ID_NF%'
       )
 ORDER BY owner,
          name,
          type,
          line;

PROMPT
PROMPT 9) Localizar jobs que possam disparar contabilizacao/interface
PROMPT

SELECT owner,
       job_name,
       enabled,
       state,
       repeat_interval,
       job_action
  FROM all_scheduler_jobs
 WHERE UPPER(job_action) LIKE '%CONTABIL%'
    OR UPPER(job_action) LIKE '%FINE%'
    OR UPPER(job_action) LIKE '%FISCO%'
    OR UPPER(job_action) LIKE '%TFC_NF_ENTRADA%'
 ORDER BY owner,
          job_name;

PROMPT
PROMPT 10) Localizar triggers sobre TFC_NF_ENTRADA e TFC_ITEM_NF_ENTRADA
PROMPT

SELECT owner,
       trigger_name,
       table_owner,
       table_name,
       status,
       triggering_event
  FROM all_triggers
 WHERE table_name IN ('TFC_NF_ENTRADA', 'TFC_ITEM_NF_ENTRADA')
 ORDER BY owner,
          table_name,
          trigger_name;

PROMPT
PROMPT Fim do diagnostico FISCO-4926.
