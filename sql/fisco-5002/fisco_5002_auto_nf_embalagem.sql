SET DEFINE OFF;
SET SERVEROUTPUT ON;

PROMPT FISCO 5002 - Automatizacao da escrituracao de NF de embalagens
PROMPT Criando procedimento PRC_FISCO_5002_AUTO_NF_EMBALAGEM

CREATE OR REPLACE PROCEDURE prc_fisco_5002_auto_nf_embalagem (
    p_dias_emissao IN NUMBER DEFAULT 60,
    p_retorno      OUT VARCHAR2
) IS
    l_chaves  owa_util.vc_arr;
    l_cont    PLS_INTEGER := 0;
    l_retorno VARCHAR2(1000);
BEGIN
    IF p_dias_emissao IS NULL OR p_dias_emissao < 0 THEN
        raise_application_error(
            -20002,
            'O parametro p_dias_emissao deve ser maior ou igual a zero.'
        );
    END IF;

    FOR reg IN (
        SELECT DISTINCT
               n.chave
          FROM tfc_nf_entrada n
         WHERE n.data_entrada IS NULL
           AND n.chave IS NOT NULL
           AND TRUNC(n.data_nf) <= TRUNC(SYSDATE) - p_dias_emissao
           AND EXISTS (
               SELECT 1
                 FROM tfc_item_nf_entrada i
                WHERE i.id_nf = n.id_nf
                  AND i.classe_nf IN ('0709', '0472')
                  AND i.nat_operacao IN ('5920', '5921', '6920', '6921')
           )
         ORDER BY n.chave
    ) LOOP
        l_cont := l_cont + 1;
        l_chaves(l_cont) := reg.chave;
    END LOOP;

    IF l_cont = 0 THEN
        p_retorno := 'Nenhuma NF de embalagem pendente para escrituracao automatica.';
        DBMS_OUTPUT.PUT_LINE(p_retorno);
        RETURN;
    END IF;

    PFC_XML_AUTO.PRC_LIBERA_ENTRADA(
        NULL,
        NULL,
        l_chaves,
        l_retorno
    );

    p_retorno := 'Chaves processadas: ' || l_cont || '. Retorno: ' || l_retorno;
    DBMS_OUTPUT.PUT_LINE(p_retorno);
EXCEPTION
    WHEN OTHERS THEN
        p_retorno := 'Erro FISCO 5002 - escrituracao automatica de NF de embalagem: '
                     || SUBSTR(SQLERRM, 1, 900);
        DBMS_OUTPUT.PUT_LINE(p_retorno);
        RAISE;
END prc_fisco_5002_auto_nf_embalagem;
/

SHOW ERRORS PROCEDURE prc_fisco_5002_auto_nf_embalagem;

PROMPT Criando/agendando job JOB_FISCO_5002_AUTO_NF_EMBALAGEM

DECLARE
    l_job_name CONSTANT VARCHAR2(128) := 'JOB_FISCO_5002_AUTO_NF_EMBALAGEM';
    l_exists   NUMBER;
    l_enabled  VARCHAR2(5);
BEGIN
    SELECT COUNT(*),
           MAX(enabled)
      INTO l_exists,
           l_enabled
      FROM user_scheduler_jobs
     WHERE job_name = l_job_name;

    IF l_exists = 0 THEN
        DBMS_SCHEDULER.CREATE_JOB(
            job_name        => l_job_name,
            job_type        => 'PLSQL_BLOCK',
            job_action      => q'[
DECLARE
    l_retorno VARCHAR2(1000);
BEGIN
    prc_fisco_5002_auto_nf_embalagem(p_retorno => l_retorno);
END;
]',
            start_date      => SYSTIMESTAMP,
            repeat_interval => 'FREQ=DAILY;BYHOUR=2;BYMINUTE=0;BYSECOND=0',
            enabled         => TRUE,
            comments        => 'FISCO 5002 - escritura automaticamente NFs de embalagens apos 60 dias da emissao.'
        );
    ELSE
        IF l_enabled = 'TRUE' THEN
            DBMS_SCHEDULER.DISABLE(
                name  => l_job_name,
                force => TRUE
            );
        END IF;

        DBMS_SCHEDULER.SET_ATTRIBUTE(
            name      => l_job_name,
            attribute => 'job_action',
            value     => q'[
DECLARE
    l_retorno VARCHAR2(1000);
BEGIN
    prc_fisco_5002_auto_nf_embalagem(p_retorno => l_retorno);
END;
]'
        );

        DBMS_SCHEDULER.SET_ATTRIBUTE(
            name      => l_job_name,
            attribute => 'repeat_interval',
            value     => 'FREQ=DAILY;BYHOUR=2;BYMINUTE=0;BYSECOND=0'
        );

        DBMS_SCHEDULER.SET_ATTRIBUTE(
            name      => l_job_name,
            attribute => 'comments',
            value     => 'FISCO 5002 - escritura automaticamente NFs de embalagens apos 60 dias da emissao.'
        );

        DBMS_SCHEDULER.ENABLE(l_job_name);
    END IF;
END;
/
