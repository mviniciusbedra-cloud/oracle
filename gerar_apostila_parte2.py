#!/usr/bin/env python3
"""Gera a apostila ME/IC — Parte 2 em PDF."""

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    Flowable,
)

pdfmetrics.registerFont(TTFont("Inter", "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Med", "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Semi", "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Bold", "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Italic", "/usr/share/fonts/truetype/macos/Inter-Italic.ttf"))
pdfmetrics.registerFont(TTFont("JetBrains", "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"))

NAVY = HexColor("#0F2744")
NAVY_MID = HexColor("#1A3A5C")
TEAL = HexColor("#0D7377")
TEAL_LIGHT = HexColor("#E6F4F4")
GOLD = HexColor("#C9A227")
GOLD_BG = HexColor("#FBF6E8")
SLATE = HexColor("#334155")
MUTED = HexColor("#64748B")
LINE = HexColor("#D6DEE8")
ROW_ALT = HexColor("#F4F7FA")
RED_SOFT = HexColor("#FDECEC")
RED = HexColor("#9B2C2C")

PAGE_W, PAGE_H = A4
MARGIN_L = 1.8 * cm
MARGIN_R = 1.8 * cm
MARGIN_T = 2.2 * cm
MARGIN_B = 1.8 * cm


class ColoredBox(Flowable):
    def __init__(self, content, bg, border, width, pad=8):
        super().__init__()
        self.content = content
        self.bg = bg
        self.border = border
        self.pad = pad
        self._inner_w = width - 2 * pad
        self.content.wrap(self._inner_w, 10000)
        self.width = width
        self.height = content.height + 2 * pad

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        self.canv.setFillColor(self.bg)
        self.canv.setStrokeColor(self.border)
        self.canv.setLineWidth(1.2)
        self.canv.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=1)
        self.canv.setStrokeColor(self.border)
        self.canv.setLineWidth(4)
        self.canv.line(2, 4, 2, self.height - 4)
        self.content.drawOn(self.canv, self.pad, self.pad)


class DiagramBox(Flowable):
    def __init__(self, text, width):
        super().__init__()
        style = ParagraphStyle(
            "diag",
            fontName="JetBrains",
            fontSize=8,
            leading=11.5,
            textColor=NAVY,
        )
        escaped = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace(" ", "&nbsp;")
            .replace("\n", "<br/>")
        )
        self.p = Paragraph(escaped, style)
        self.pad = 10
        w, h = self.p.wrap(width - 2 * self.pad, 10000)
        self.width = width
        self.height = h + 2 * self.pad

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        self.canv.setFillColor(HexColor("#F7F9FC"))
        self.canv.setStrokeColor(HexColor("#C5D0DC"))
        self.canv.setLineWidth(0.8)
        self.canv.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=1)
        self.p.drawOn(self.canv, self.pad, self.pad)


class CoverBar(Flowable):
    def __init__(self, width, height, color):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


def make_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(
        "CoverKicker", fontName="Inter-Med", fontSize=10, textColor=GOLD,
        tracking=1.4, alignment=TA_LEFT, spaceAfter=8,
    ))
    s.add(ParagraphStyle(
        "CoverTitle", fontName="Inter-Bold", fontSize=26, leading=32,
        textColor=white, alignment=TA_LEFT, spaceAfter=10,
    ))
    s.add(ParagraphStyle(
        "CoverSub", fontName="Inter", fontSize=12, leading=17,
        textColor=HexColor("#D7E2EE"), alignment=TA_LEFT,
    ))
    s.add(ParagraphStyle(
        "H1", fontName="Inter-Bold", fontSize=14.5, leading=19,
        textColor=NAVY, spaceBefore=16, spaceAfter=8,
    ))
    s.add(ParagraphStyle(
        "H2", fontName="Inter-Semi", fontSize=12, leading=16,
        textColor=TEAL, spaceBefore=12, spaceAfter=6,
    ))
    s.add(ParagraphStyle(
        "Body", fontName="Inter", fontSize=9.5, leading=13.5,
        textColor=SLATE, alignment=TA_JUSTIFY, spaceAfter=7,
    ))
    s.add(ParagraphStyle(
        "BodyLeft", fontName="Inter", fontSize=9.5, leading=13.5,
        textColor=SLATE, alignment=TA_LEFT, spaceAfter=7,
    ))
    s.add(ParagraphStyle(
        "BulletBody", fontName="Inter", fontSize=9.5, leading=13.5,
        textColor=SLATE, leftIndent=12, spaceAfter=2,
    ))
    s.add(ParagraphStyle(
        "Callout", fontName="Inter", fontSize=9.5, leading=13.5,
        textColor=NAVY, alignment=TA_LEFT,
    ))
    s.add(ParagraphStyle(
        "TableHead", fontName="Inter-Semi", fontSize=8.5, leading=11,
        textColor=white, alignment=TA_LEFT,
    ))
    s.add(ParagraphStyle(
        "TableCell", fontName="Inter", fontSize=8.5, leading=11.5,
        textColor=SLATE, alignment=TA_LEFT,
    ))
    s.add(ParagraphStyle(
        "TOCItem", fontName="Inter", fontSize=9.5, leading=15.5,
        textColor=SLATE,
    ))
    s.add(ParagraphStyle(
        "ConceptNum", fontName="Inter-Bold", fontSize=11, textColor=TEAL,
        spaceBefore=8, spaceAfter=2,
    ))
    return s


STYLES = make_styles()
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


def P(text, style="Body"):
    return Paragraph(text, STYLES[style])


def h1(n, title):
    return P(f"{n}. {title}", "H1")


def h2(title):
    return P(title, "H2")


def callout(text, kind="info"):
    if kind == "rule":
        bg, border = GOLD_BG, GOLD
        label = "Regra"
    elif kind == "alert":
        bg, border = RED_SOFT, RED
        label = "Atenção"
    else:
        bg, border = TEAL_LIGHT, TEAL
        label = "Ponto-chave"
    inner = Paragraph(f"<b>{label}.</b> {text}", STYLES["Callout"])
    return KeepTogether([
        ColoredBox(inner, bg, border, CONTENT_W),
        Spacer(1, 8),
    ])


def bullets(items):
    flow = []
    for item in items:
        flow.append(Paragraph(f"•  {item}", STYLES["BulletBody"]))
    flow.append(Spacer(1, 6))
    return flow


def simple_table(headers, rows, first_cm=3.4):
    head = [Paragraph(h, STYLES["TableHead"]) for h in headers]
    data = [head]
    for row in rows:
        data.append([Paragraph(str(c), STYLES["TableCell"]) for c in row])
    if len(headers) == 2:
        widths = [first_cm * cm, CONTENT_W - first_cm * cm]
    else:
        col_w = CONTENT_W / len(headers)
        widths = [col_w] * len(headers)
    t = Table(data, colWidths=widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
    ]
    for i in range(1, len(data)):
        bg = ROW_ALT if i % 2 == 0 else white
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(style_cmds))
    return KeepTogether([t, Spacer(1, 10)])


def diagram(text):
    return KeepTogether([DiagramBox(text, CONTENT_W), Spacer(1, 10)])


def hr():
    return HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=4, spaceAfter=8)


def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, 14 * mm, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(14 * mm, 0, 3 * mm, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(NAVY_MID)
    canvas.rect(0, 0, PAGE_W, 28 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 28 * mm, PAGE_W, 2.2 * mm, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#9BB0C4"))
    canvas.setFont("Inter", 8)
    canvas.drawString(28 * mm, 14 * mm, "Uso interno  ·  Treinamento técnico  ·  Parte 2")
    canvas.drawRightString(PAGE_W - 18 * mm, 14 * mm, "Mecanismo de Eventos  ·  Integrador Contábil")
    canvas.restoreState()


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 1.4 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Inter", 7.5)
    canvas.drawString(MARGIN_L, PAGE_H - 8 * mm, "Apostila  ·  ME e IC  ·  Parte 2")
    canvas.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 8 * mm, "Treinamento interno")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_L, 12 * mm, PAGE_W - MARGIN_R, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Inter", 8)
    canvas.drawString(MARGIN_L, 7 * mm, "Tela, package, triggers, STG e parametrização")
    canvas.drawRightString(PAGE_W - MARGIN_R, 7 * mm, f"{doc.page}")
    canvas.restoreState()


def build_story():
    s = []
    s.append(Spacer(1, 48 * mm))
    s.append(Paragraph("APOSTILA DE TREINAMENTO  ·  PARTE 2", STYLES["CoverKicker"]))
    s.append(Paragraph("Mecanismo de Eventos<br/>e Integrador Contábil", STYLES["CoverTitle"]))
    s.append(Spacer(1, 8))
    s.append(CoverBar(42 * mm, 3.2, GOLD))
    s.append(Spacer(1, 14))
    s.append(Paragraph(
        "Tela do CUR, package orquestradora, fila, cadastro SQL,<br/>"
        "triggers, STGs e o caminho até o IC, ODI e EBS.",
        STYLES["CoverSub"],
    ))
    s.append(NextPageTemplate("body"))
    s.append(PageBreak())

    s.append(P("Sumário", "H1"))
    toc = [
        "1. Visão geral",
        "2. Onde fica no CUR",
        "3. A tela do Mecanismo de Eventos",
        "4. Fato gerador",
        "5. Fechamento de caixa starta o processo",
        "6. Trigger → Fila",
        "7. A package orquestradora",
        "8. Um fato gerador tem N eventos",
        "9. Nem todo evento é gerado sempre",
        "10. Tabelas intermediárias (STG)",
        "11. Sequência identificadora",
        "12. Exemplo: três filas na mesma reserva",
        "13. Datas da fila",
        "14. Eventos só existem depois do processamento",
        "15. Como a package gera os eventos",
        "16. MGE_CADASTRO_SQL",
        "17. Por que a regra fica na query",
        "18. Exceções dentro da package",
        "19. Fato gerador 39",
        "20. Fotos do Sistur",
        "21. Nem sempre é VEM_RESERVA_STG",
        "22. Fatos geradores sem tela",
        "23. Depois do ME: IC, ODI e EBS",
        "24. Fato gerador 55 — exemplo de pagamento",
        "25. Fato gerador 10 — embarque é cópia",
        "26. Evento 101",
        "27. Parametrização fato gerador × evento",
        "28. Status ligado / desligado",
        "29. Mesmo evento em mais de um fato gerador",
        "30. Evento 13",
        "31. Evento 35 e cancelamentos 9 e 17",
        "32. Valores absolutos e sinal no IC",
        "33. Onde está o trabalho do dia a dia",
        "34. Triggers",
        "35. SIS_MGE × Sistur",
        "36. Como nasce um fato gerador novo",
        "37. MGE_TRG_02",
        "38. Trigger mutante",
        "39. Fato gerador 34",
        "40. Cadastro Trigger × Fato Gerador",
        "41. O perigo de gerar fila demais",
        "42. Fato gerador 13 e o projeto de otimização",
        "43. O que o ME realmente faz",
        "44. Atlas → Sistur → ME → IC",
        "45. ME e IC não calculam",
        "46. Quando o problema não é do ME",
        "47. Fluxo completo de troubleshooting",
        "48. Principais tabelas / objetos",
        "49. Códigos desta reunião",
        "50. O que guardar desta reunião",
    ]
    for item in toc:
        s.append(P(item, "TOCItem"))
    s.append(PageBreak())

    s.append(h1(1, "Visão geral"))
    s.append(P(
        "Esta reunião entra no CUR/Sistur e mostra, na prática, como o "
        "<b>Mecanismo de Eventos (ME)</b> funciona: tela, fato gerador, fila, "
        "package, cadastro SQL, STGs, triggers e o caminho até o "
        "<b>Integrador Contábil (IC)</b>."
    ))
    s.append(P("O foco continua o mesmo:"))
    s.append(callout(
        "O Mecanismo de Eventos <b>separa e processa</b>. "
        "O Integrador Contábil <b>captura e abre as contas</b>.",
        "rule",
    ))
    s.append(P(
        "O CUR tem muitos menus. Nem tudo ali é do ME/IC. "
        "O recorte desta reunião é a parte do mecanismo de eventos e da integração contábil."
    ))

    s.append(h1(2, "Onde fica no CUR"))
    s.append(P("Caminho apresentado:"))
    s.append(diagram("Financeiro  →  Consultas  →  Mecanismo de Eventos"))
    s.append(P("Essa tela é o ponto de partida da análise."))

    s.append(h1(3, "A tela do Mecanismo de Eventos"))
    s.append(P("A consulta começa por uma reserva."))
    s.append(P(
        "Na tela aparecem os <b>eventos contábeis</b> daquela reserva: "
        "tudo que já aconteceu de evento contábil nela."
    ))
    s.append(P("Exemplo da reunião:"))
    s.extend(bullets([
        "a reserva já passou por etapas da venda;",
        "chegou no mecanismo de eventos / integração contábil;",
        "foram gerados vários eventos (na tela apareciam vários códigos, inclusive 13).",
    ]))
    s.append(P("A pergunta central da tela é: de onde vieram esses eventos?"))
    s.append(callout("A resposta é: do <b>fato gerador</b>.", "info"))

    s.append(h1(4, "Fato gerador"))
    s.append(P("O fato gerador é o que fez o evento contábil surgir. É o motivo da geração."))
    s.append(P("No Sistur, isso geralmente acontece por <b>trigger</b>."))
    s.append(callout(
        "Fato gerador = o que aconteceu. Evento = o que foi gerado em consequência daquilo.",
        "rule",
    ))
    s.append(P("Existem eventos específicos para cada fato gerador. Isso é parametrizável."))

    s.append(h1(5, "Fechamento de caixa starta o processo"))
    s.append(P("O fechamento do caixa é um fato gerador. Toda vez que o caixa fecha:"))
    s.extend(bullets([
        "existe uma data numa tabela relacionada ao caixa, indicando que o caixa foi fechado;",
        "uma trigger percebe essa alteração;",
        "essa trigger popula uma tabela do lado do Mecanismo de Eventos.",
    ]))
    s.append(P("Essa tabela é uma <b>fila</b>."))

    s.append(h1(6, "Trigger → Fila"))
    s.append(P("Fluxo apresentado:"))
    s.append(diagram(
        "Fechamento do caixa\n"
        "        │\n"
        "        ▼\n"
        "Trigger (alteração da data de fechamento)\n"
        "        │\n"
        "        ▼\n"
        "MGE_FILA\n"
        "        │\n"
        "        ▼\n"
        "Fato Gerador 11"
    ))
    s.append(P("A trigger cria uma fila do fato gerador 11 para processar."))
    s.append(callout(
        "O 11 é o início da contabilização da reserva. Tudo nasce com o fechamento do caixa.",
        "rule",
    ))

    s.append(h1(7, "A package orquestradora"))
    s.append(P("Quem orquestra o processamento é a <b>package principal</b> do Mecanismo de Eventos. Ela:"))
    s.extend(bullets([
        "lê tudo que está pendente na fila;",
        "usa um cursor da fila;",
        "processa o que foi gerado pelo gatilho do fato gerador.",
    ]))
    s.append(P("A tabela citada é <b>MGE_FILA</b>."))

    s.append(h1(8, "Um fato gerador tem N eventos"))
    s.append(P("Dúvida consolidada na reunião: um fato gerador tem vários eventos?"))
    s.append(callout(
        "Sim. Cada fato gerador tem <b>N eventos</b>. Existe parametrização dizendo quais eventos "
        "fazem parte daquele fato gerador. Isso inclui geração normal e estorno.",
        "info",
    ))

    s.append(h1(9, "Nem todo evento é gerado sempre"))
    s.append(P(
        "Clicar no fato gerador 11 mostra os eventos gerados. "
        "Esses eventos estão parametrizados para aquele fato gerador."
    ))
    s.append(P(
        "Mas a package <b>não gera todos automaticamente, sempre</b>. "
        "Ela também olha as características da reserva para decidir o que gera e o que não gera."
    ))
    s.append(P("Quem faz isso é a package principal."))

    s.append(h1(10, "Tabelas intermediárias (STG)"))
    s.append(P(
        "No momento em que a fila do fato gerador é criada, também é criado um registro "
        "nas tabelas intermediárias. O time chama essas tabelas de <b>STGs</b>."
    ))
    s.append(diagram(
        "VEM_RESERVA\n"
        "     │\n"
        "     └── tabela origem (Sistur)\n"
        "\n"
        "VEM_RESERVA_STG\n"
        "     │\n"
        "     └── tabela intermediária / integração (SIS_MGE)"
    ))
    s.append(P(
        "A reserva precisa estar nas duas. VEM_RESERVA tem os dados originais: data, filial, "
        "vendedor, valores, cancelamento, roteiro, data de saída, data de embarque, "
        "data de confirmação etc. A data de confirmação é bastante utilizada."
    ))

    s.append(h1(11, "Sequência identificadora"))
    s.append(P("Na STG podem existir várias linhas da mesma reserva. Cada uma tem um ID exclusivo:"))
    s.append(P("<b>CD_SEQUENCIA_IDENTIFICADORA</b>"))
    s.append(P("Essa sequência liga:"))
    s.append(diagram("STG  ↔  Fila  ↔  processamento"))
    s.append(P("Se existem 3 STGs, em geral existem 3 filas."))

    s.append(h1(12, "Exemplo: três filas na mesma reserva"))
    s.append(P("No exemplo da reunião, a reserva tinha três filas:"))
    s.append(simple_table(
        ["Código", "Fato gerador"],
        [
            ["11", "Fechamento de Caixa"],
            ["55", "Modificação da Venda"],
            ["17", "Cancelamento"],
        ],
    ))
    s.append(P(
        "O 34 (reembolso) apareceu junto com o 17, porque o cancelamento gerou reembolsos. "
        "O que realmente gerou processamento foram as três filas: 11, 55 e 17."
    ))

    s.append(h1(13, "Datas da fila"))
    s.append(P("A fila guarda datas importantes para atendimento de chamado:"))
    s.extend(bullets([
        "data de criação da fila;",
        "data de processamento.",
    ]))
    s.append(P(
        "Exemplo citado: fato gerador 11 criado em 31/08, por volta de 12:46; processado em 03/09. "
        "Essas datas mostram quando a coisa aconteceu e quando o mecanismo processou."
    ))

    s.append(h1(14, "Eventos só existem depois do processamento"))
    s.append(P("No momento da criação:"))
    s.extend(bullets([
        "é gerada a VEM_RESERVA_STG;",
        "é gerada a MGE_FILA.",
    ]))
    s.append(P("Os eventos contábeis ainda não existem."))
    s.append(callout(
        "Quem gera os eventos é a package, <b>depois</b> de processar a fila. "
        "Se a fila do 11 ainda não foi processada, a tela de eventos processados não terá nada daquele fato gerador.",
        "rule",
    ))

    s.append(h1(15, "Como a package gera os eventos"))
    s.append(P("A package principal:"))
    s.extend(bullets([
        "pega o que está pendente na fila;",
        "identifica o fato gerador que está chegando;",
        "busca quais eventos estão vinculados àquele fato gerador;",
        "varre esses eventos;",
        "executa a query de cada um;",
        "analisa o retorno para decidir se gera ou não o evento para aquela reserva.",
    ]))
    s.append(P("Quem diz se gera ou não é a própria query: se retornou ou não."))

    s.append(h1(16, "MGE_CADASTRO_SQL"))
    s.append(P("As queries ficam armazenadas em tabela: <b>MGE_CADASTRO_SQL</b>."))
    s.append(P(
        "Exemplo da reunião: cadastro SQL 68 vinculado a um evento; "
        "evento 92, query de repasse / margem bruta."
    ))
    s.append(P("A query fica armazenada na tabela, como SQL mesmo."))
    s.append(callout(
        "A inteligência do Mecanismo de Eventos, no geral, está nessa tabela. "
        "A package orquestra. A regra de geração do evento está na query.",
        "rule",
    ))

    s.append(h1(17, "Por que a regra fica na query"))
    s.append(P("A maior parte dos chamados e projetos envolve alteração dessas queries. Às vezes é manutenção. Às vezes é SQL novo e evento novo."))
    s.append(P("Vantagem:"))
    s.extend(bullets([
        "altera a regra com UPDATE no cadastro SQL;",
        "não precisa compilar objeto;",
        "não gera indisponibilidade.",
    ]))
    s.append(P("A package, em geral, faz EXECUTE IMMEDIATE, passa parâmetros e insere/atualiza nas tabelas de destino."))

    s.append(h1(18, "Exceções dentro da package"))
    s.append(P("O geral é: regra na query. Mas existem exceções. Há regras de negócio ainda dentro da package."))
    s.append(P("Exemplo citado: fato gerador 13 tinha lógica dentro da package, não encapsulada no SQL."))
    s.append(callout(
        "Isso é <b>exceção</b>, não o caminho padrão. O ideal é parametrizar fora, porque a manutenção fica mais simples.",
        "alert",
    ))

    s.append(h1(19, "Fato gerador 39"))
    s.append(P("Foi consolidado que:"))
    s.extend(bullets([
        "o único fato gerador que não busca as queries da tabela é o <b>39</b>;",
        "o restante é em cima da query cadastrada.",
    ]))
    s.append(P("O 13, apesar de ter particularidades, também usa query de evento."))
    s.append(P(
        "O 39 ficou fixo na package. Tem validações de custo e tipo de fornecedor. "
        "Na prática, isso já obrigou subir objeto com pressa. Daria para ter sido query."
    ))

    s.append(h1(20, "Fotos do Sistur"))
    s.append(P("A STG é uma <b>foto</b> do Sistur. A ideia é:"))
    s.append(diagram(
        "Tirar uma foto no Sistur\n"
        "        │\n"
        "        ▼\n"
        "Trazer para o mecanismo\n"
        "        │\n"
        "        ▼\n"
        "Trabalhar só em cima dessa foto\n"
        "        │\n"
        "        ▼\n"
        "Não pesar no Sistur"
    ))
    s.append(P(
        "A maioria dos fatos geradores usa a foto da VEM_RESERVA, portanto tem "
        "VEM_RESERVA_STG no owner <b>SIS_MGE</b>. Mas nem sempre."
    ))

    s.append(h1(21, "Nem sempre é VEM_RESERVA_STG"))
    s.append(P("Depende do tipo de gatilho / fato gerador."))
    s.append(simple_table(
        ["Fato gerador", "STG / origem"],
        [
            ["Maioria (reserva)", "VEM_RESERVA_STG"],
            ["59 — Baixa de recibo sem reserva", "STG de CXA_LANCAMENTO"],
            ["68 — Fatura", "AIM_FATURA_STG (sem reserva)"],
            ["Reembolso", "STG de processo de reembolso"],
            ["Bilhete", "AIR_BILHETE_EMITIDO_STG / AIR_BILHETE_P_STG"],
        ],
        first_cm=6.2,
    ))
    s.append(P("Nesses casos de fatura, recibo, reembolso ou bilhete, pode não existir VEM_RESERVA_STG."))

    s.append(h1(22, "Fatos geradores sem tela"))
    s.append(P(
        "No menu inicial do ME existem opções de consulta. Mas há situações em que o trâmite roda, "
        "o dado vai para o IC, e <b>não há consulta na tela</b>."
    ))
    s.append(P(
        "O processamento no ME continua sendo o passo inicial. Depois rodam interfaces para "
        "integrar os eventos no IC e, mais à frente, no EBS."
    ))

    s.append(h1(23, "Depois do ME: IC, ODI e EBS"))
    s.append(P("Fluxo apresentado:"))
    s.append(diagram(
        "Sistur\n"
        "  │\n"
        "  ▼\n"
        "Mecanismo de Eventos\n"
        "  │  separa custo, margem, comissão, recibo, recadastro etc.\n"
        "  ▼\n"
        "Integrador Contábil\n"
        "  │  abre as contas (custo → conta X, margem → conta Y...)\n"
        "  ▼\n"
        "ODI\n"
        "  │  checagem prévia das aberturas\n"
        "  ▼\n"
        "GL / EBS\n"
        "  │\n"
        "  ▼\n"
        "Contabilização"
    ))
    s.append(P("No EBS não chegam “evento 13, evento 27, evento 87”. Chega a <b>conta</b> de cada valor."))
    s.append(callout(
        "O IC é o complemento do ME: faz a abertura contábil dos valores para o EBS. "
        "O pessoal fala “IC”, mas isso engloba também o SIS_MGE. "
        "O evento nasce no Mecanismo de Eventos, com base nas informações do CUR/Sistur. "
        "O IC recebe o que o ME passou.",
        "info",
    ))

    s.append(h1(24, "Fato gerador 55 — exemplo de pagamento"))
    s.append(P("O 55 é modificação da venda. Quando entra o 55, o 11 deixa de valer. As informações que valem passam a ser as do 55."))
    s.append(P("Exemplo da reunião:"))
    s.extend(bullets([
        "cliente comprou na loja para pagar no cartão;",
        "a loja baixou a reserva no cartão, mas não passou o cartão;",
        "depois o cliente voltou para pagar em dinheiro;",
        "a loja exclui a operação de cartão e lança pagamento em dinheiro.",
    ]))
    s.append(P("Isso é uma modificação da venda. Contabilmente:"))
    s.append(diagram(
        "Sobe R$ 1.000 de pagamento em cartão\n"
        "        │\n"
        "        ▼\n"
        "Estorno de R$ 1.000 do cartão\n"
        "        │\n"
        "        ▼\n"
        "Pagamento em dinheiro de R$ 1.000  →  Fato Gerador 55"
    ))
    s.append(P("Foi citado o GAP 105, que trata cenário parecido."))

    s.append(h1(25, "Fato gerador 10 — embarque é cópia"))
    s.append(P("O fato gerador 10 é o embarque."))
    s.append(callout(
        "O 10 praticamente <b>não gera fila</b>. Ele é uma cópia do último fato gerador válido: 11 ou 55.",
        "rule",
    ))
    s.append(P(
        "O 11 é uma previsão para a contabilidade, da venda até o embarque. "
        "Até o embarque pode haver modificação, cancelamento ou qualquer alteração."
    ))
    s.append(P("O embarque confirma a venda: a contabilidade fecha e considera que aquela reserva foi recebida."))

    s.append(h1(26, "Evento 101"))
    s.append(P("No processo do mecanismo existe um evento específico, citado como <b>evento 101</b>."))
    s.append(P("Quando a rotina bate no 101:"))
    s.append(diagram(
        "Evento 101\n"
        "     │\n"
        "     ▼\n"
        "Procura fato gerador 11 ou 55\n"
        "     │\n"
        "     ▼\n"
        "Copia para o fato gerador 10"
    ))
    s.append(P("Copia igual. O último fato gerador válido, seja 11 ou 55, vira 10."))

    s.append(h1(27, "Parametrização fato gerador × evento"))
    s.append(P("Existe tabela de relacionamento entre tipo de fato gerador e eventos. Nomes citados:"))
    s.extend(bullets([
        "MGE_PARAM_FATO_GERADOR;",
        "parametrização de evento (MGE_EVENTO / param evento).",
    ]))
    s.append(P("Essa amarração indica ao mecanismo quais eventos precisam ser testados. Exemplo conceitual:"))
    s.extend(bullets([
        "fato gerador 11 → cerca de 20 eventos para testar;",
        "fato gerador 55 → cerca de 15 eventos para testar.",
    ]))
    s.append(P(
        "A rotina executa as queries desses eventos, se estiverem habilitadas / em vigência. "
        "O retorno, de acordo com os dados da reserva, define o que será gerado. "
        "Por isso duas reservas podem gerar eventos contábeis diferentes."
    ))

    s.append(h1(28, "Status ligado / desligado"))
    s.append(P("A parametrização tem status de ligado/desligado. Na reunião houve correção sobre 0 e 1. O ponto prático é:"))
    s.extend(bullets([
        "o evento pode estar parametrizado para um fato gerador e mesmo assim estar desligado;",
        "fato gerador 36 e 41 foram citados como parametrizados um dia, mas hoje não usados.",
    ]))
    s.append(callout("Confirmar no cadastro qual valor significa ligado.", "alert"))

    s.append(h1(29, "Mesmo evento em mais de um fato gerador"))
    s.append(P("Um evento pode aparecer em mais de um fato gerador. Isso não significa que o tratamento seja igual."))

    s.append(h1(30, "Evento 13"))
    s.append(P(
        "O evento 13 é de custo / acordo. Exemplos: acordo de ingresso, seguro viagem etc. "
        "Ele aparece no fato gerador 11 e no 55. Para esses dois, o tratamento é o mesmo."
    ))

    s.append(h1(31, "Evento 35 e cancelamentos 9 e 17"))
    s.append(P("O evento 35 aparece em fatos geradores de cancelamento:"))
    s.append(simple_table(
        ["Código", "Significado"],
        [
            ["9", "Cancelamento para reembolso"],
            ["17", "Cancelamento para recadastro"],
        ],
    ))
    s.append(h2("Cancelamento para recadastro (17)"))
    s.extend(bullets([
        "o cliente cancela, mas não quer o dinheiro de volta;",
        "quer remarcar e ainda não sabe para onde/quando;",
        "fica um crédito na CVC.",
    ]))
    s.append(P(
        "Exemplo: reserva de R$ 1.000 → crédito de R$ 1.000. Depois usa esse crédito em outra reserva. "
        "Foi citado prazo de cerca de 18 meses, com possibilidade de reavaliação / pegar o dinheiro ou remarcar."
    ))
    s.append(P(
        "O evento 35 é <b>cancelamento da comissão da loja</b>. "
        "A loja tinha comissão da venda. Como cancelou, a loja não recebe."
    ))
    s.append(callout(
        "Apesar de ser o mesmo evento 35, o comportamento no 9 e no 17 é <b>diferente</b>: validações diferentes. "
        "Também existem eventos de crédito e de débito, porque o cancelamento pode gerar multa.",
        "info",
    ))

    s.append(h1(32, "Valores absolutos e sinal no IC"))
    s.append(P("A maioria dos eventos trabalha com valor absoluto. Alguns valores podem chegar negativos."))
    s.append(P("O tratamento de sinal, nesse desenho, fica no IC:"))
    s.append(diagram(
        "Valor negativo  →  uma conta\n"
        "Valor positivo  →  outra conta"
    ))
    s.append(P("O ME trabalha com os dois tipos de valor, mas a abertura por sinal é no IC."))

    s.append(h1(33, "Onde está o trabalho do dia a dia"))
    s.append(P("Foi dito que cerca de 60% a 70% das demandas estão em:"))
    s.extend(bullets([
        "cadastro SQL;",
        "evento;",
        "fato gerador;",
        "param fato gerador;",
        "param evento.",
    ]))
    s.append(P("A maioria dos chamados é manutenção de query já cadastrada, para o evento gerar certo."))

    s.append(h1(34, "Triggers"))
    s.append(callout(
        "Cerca de <b>90%</b> dos fatos geradores nascem por trigger. A maioria das triggers do time é AFTER. Também existem BEFORE.",
        "info",
    ))
    s.append(P("A trigger é o gatilho. Em geral está relacionada a um faturador / tabela origem. Quem popula a STG, na maior parte dos casos, é a trigger."))

    s.append(h1(35, "SIS_MGE × Sistur"))
    s.append(P("O Mecanismo de Eventos fica num schema: <b>SIS_MGE</b>."))
    s.append(P("Lá ficam as tabelas STG, fila e cadastros do ME."))
    s.append(P("<b>VEM_RESERVA</b> é tabela do Sistur, não do SIS_MGE."))
    s.append(P("A trigger na tabela origem popula a STG do SIS_MGE e cria a fila."))

    s.append(h1(36, "Como nasce um fato gerador novo"))
    s.append(P("Para criar um fato gerador novo, a primeira coisa é criar o gatilho. Pergunta:"))
    s.append(P("<i>Esse fato gerador vai ser gerado quando? Em que momento starta?</i>"))
    s.append(P("Em geral: trigger na tabela origem."))

    s.append(h1(37, "MGE_TRG_02"))
    s.append(P("Trigger bastante usada e crítica, na VEM_RESERVA. Trata cancelamento de reserva."))
    s.append(P("Gera fato gerador de acordo com o tipo de devolução da tela: <b>9 ou 17</b>."))
    s.append(callout(
        "Se cancelar a reserva e não gerar o fato gerador, a contabilidade não contabiliza. Já houve bastante problema com ela.",
        "alert",
    ))
    s.append(P(
        "O fato gerador 43 (cancelamento automático) chegou a ficar dentro dessa trigger. "
        "Em produção ocorreu trigger mutante, que em homologação não foi pego."
    ))
    s.append(P(
        "Parece código simples. O que envolve ela — toda a parte de cancelamento — é complexo. "
        "Qualquer update na VEM_RESERVA (data etc.) pode startar essa trigger."
    ))

    s.append(h1(38, "Trigger mutante"))
    s.append(P("Exemplo da reunião:"))
    s.append(diagram(
        "Cancelamento altera DT_CANCELAMENTO na VEM_RESERVA\n"
        "        │\n"
        "        ▼\n"
        "Dispara trigger de cancelamento\n"
        "        │\n"
        "        ▼\n"
        "Chama outra trigger da VEM_RESERVA\n"
        "        │\n"
        "        ▼\n"
        "Package de estorno de comissão (grande/complexa)\n"
        "        │\n"
        "        ▼\n"
        "Rotina de exclusão tenta gravar novo movimento no extrato\n"
        "        │\n"
        "        ▼\n"
        "Consulta de novo a VEM_RESERVA\n"
        "        │\n"
        "        ▼\n"
        "ERRO DE TRIGGER MUTANTE"
    ))
    s.append(P("Lição:"))
    s.extend(bullets([
        "trigger chamando objeto complexo é perigoso;",
        "uma query “pequena” num objeto chamado por trigger pode impactar produção;",
        "sempre olhar as triggers da tabela antes de alterar.",
    ]))

    s.append(h1(39, "Fato gerador 34"))
    s.append(callout(
        "O 34 (reembolso) <b>não é trigger</b>. É disparado na tela de reembolso, na confirmação. "
        "Foi citado como possivelmente o único que não é trigger. O restante, em geral, é trigger.",
        "rule",
    ))

    s.append(h1(40, "Cadastro Trigger × Fato Gerador"))
    s.append(P("Existe cadastro para amarrar a trigger ao fato gerador, evitando hard code. Objetos citados:"))
    s.extend(bullets([
        "MGE_TABELA;",
        "MGE_COLUNA.",
    ]))
    s.append(P("A trigger:"))
    s.extend(bullets([
        "identifica a tabela (ex.: VEM_RESERVA);",
        "busca o ID no cadastro de tabelas;",
        "recebe a ação (inclusão/alteração);",
        "abre um cursor com os campos a comparar;",
        "compara NEW / OLD;",
        "só executa o fato gerador se as condições baterem.",
    ]))
    s.append(P(
        "Exemplo: fato gerador 13 só executa quando o status da fatura for baixa efetiva (<b>E</b>). "
        "Se a regra mudar para baixa parcial, não precisa recompilar trigger: dá UPDATE no parâmetro."
    ))
    s.append(P("Também dá para amarrar valor maior que zero, data NOT NULL etc."))
    s.append(callout(
        "Objetivo: só inserir na tabela do ME / só startar o processo quando realmente deve.",
        "info",
    ))

    s.append(h1(41, "O perigo de gerar fila demais"))
    s.append(P("Trigger mal feita pode gerar centenas de milhares de registros desnecessários. Isso já aconteceu."))
    s.append(P("Exemplo atual citado: fato gerador 13 em produção."))
    s.extend(bullets([
        "o gatilho está em outra tabela, não na que deveria;",
        "não tem as validações de campo;",
        "qualquer alteração dispara FG 13;",
        "está gerando fila de qualquer jeito.",
    ]))
    s.append(P(
        "Por isso o 13 foi desligado há cerca de 5 anos: contabilizava errado. "
        "Exemplo: chegava R$ 5.000 para uma fatura de R$ 2.000. A contabilidade fazia lançamento manual de −R$ 3.000."
    ))

    s.append(h1(42, "Fato gerador 13 e o projeto de otimização"))
    s.append(P("Existe o projeto de otimização do fechamento contábil. Objetivo:"))
    s.extend(bullets([
        "eliminar lançamentos manuais;",
        "diminuir relatórios;",
        "reduzir erro humano.",
    ]))
    s.append(P(
        "Foi dito que a contabilidade emite cerca de <b>96 relatórios</b> para bater o mês. "
        "A meta seria reduzir uns 40% a 50%."
    ))
    s.append(P(
        "O ME trabalha só com o Sistur. Ele separa os valores de cada momento do documento: "
        "reserva, fatura, reembolso. Uma fatura pode ter custo, margem, comissão, valor do recibo "
        "e valor de recadastro da reserva anterior."
    ))
    s.append(P("Se o ME lança errado, chega errado na contabilidade."))
    s.append(P("O projeto mexe em:"))
    s.extend(bullets([
        "fato gerador 13;",
        "fatos geradores 52 e 53 (reembolso de bilhete / faturamento aéreo).",
    ]))
    s.append(P("Mexe no ME (Sistur) e no IC (outro banco)."))

    s.append(h1(43, "O que o ME realmente faz"))
    s.append(P("O ME destrincha os valores de cada momento do documento e manda para o IC."))
    s.append(P("O IC separa em contas e disponibiliza para o ODI."))
    s.append(P("O ODI checa e manda para o GL/EBS."))

    s.append(h1(44, "Atlas → Sistur → ME → IC"))
    s.append(P("Atlas = sistema novo de vendas das lojas."))
    s.append(diagram(
        "Atlas\n"
        "  │\n"
        "  ▼\n"
        "tabelas do Sistur\n"
        "  │\n"
        "  ▼\n"
        "Mecanismo de Eventos\n"
        "  │\n"
        "  ▼\n"
        "IC\n"
        "  │\n"
        "  ▼\n"
        "abertura contábil / EBS"
    ))
    s.append(P("Muita coisa que “estoura” no IC nasceu errada no CUR/Sistur."))

    s.append(h1(45, "ME e IC não calculam"))
    s.append(callout(
        "O cálculo deve ser feito no <b>Sistur</b>. ME e IC não devem calcular.",
        "rule",
    ))
    s.append(P("O trabalho deles é:"))
    s.extend(bullets([
        "separar os valores em eventos contábeis;",
        "fazer a abertura contábil desses eventos.",
    ]))
    s.append(P(
        "Se gerou errado, analisa, documenta e devolve para vendas/caixa, quando a origem for lá. "
        "Frase usada na reunião: <i>“o mecanismo está inocente”</i>. Ele pega o que está no Sistur e passa para frente."
    ))

    s.append(h1(46, "Quando o problema não é do ME"))
    s.append(P("Exemplos:"))
    s.extend(bullets([
        "<b>Custo de bilhete duplicado:</b> o valor estava duplicado nas tabelas de acordo do Sistur (custo no dia 22 e no dia 25). O ME somou e gerou R$ 200 num recibo de R$ 100;",
        "<b>Assist Card:</b> câmbio/valor errado no Sistur; o ME só encaminhou;",
        "<b>OPF / venda fiada:</b> loja vende fiado com vencimento depois do embarque; o cliente viaja e não paga; o sistema cobra a loja. Contabilidade pediu ajuste no ME/IC, mas o processo errado é da venda.",
    ]))
    s.append(P("O IC e o ME às vezes só estão passando adiante o peixe que receberam."))

    s.append(h1(47, "Fluxo completo de troubleshooting desta reunião"))
    s.append(diagram(
        "                 PROBLEMA\n"
        "                    │\n"
        "                    ▼\n"
        "              Identificar reserva\n"
        "                    │\n"
        "                    ▼\n"
        "           Tela do ME / fato gerador\n"
        "                    │\n"
        "          ┌─────────┴─────────┐\n"
        "          │                   │\n"
        "       EXISTE?              NÃO EXISTE\n"
        "          │                   │\n"
        "          │                   ▼\n"
        "          │         Sequência identificadora\n"
        "          │                   │\n"
        "          │                   ▼\n"
        "          │              MGE_FILA\n"
        "          │                   │\n"
        "          │                   ▼\n"
        "          │         Trigger / package\n"
        "          ▼\n"
        "     Eventos gerados?\n"
        "          │\n"
        "          ▼\n"
        "   Query do evento (MGE_CADASTRO_SQL)\n"
        "          │\n"
        "          ▼\n"
        "   Dados da STG / Sistur\n"
        "          │\n"
        "          ▼\n"
        "          IC\n"
        "          │\n"
        "          ▼\n"
        "   Conta / débito / crédito\n"
        "          │\n"
        "          ▼\n"
        "        ODI / EBS"
    ))

    s.append(h1(48, "Principais tabelas / objetos citados"))
    s.append(simple_table(
        ["Objeto", "Função"],
        [
            ["MGE_FILA", "Fila de processamento dos fatos geradores"],
            ["Package do ME", "Orquestra leitura da fila e geração dos eventos"],
            ["MGE_CADASTRO_SQL", "Queries / regras dos eventos"],
            ["MGE_EVENTO", "Cadastro dos eventos"],
            ["Param FG / param evento", "Amarração fato gerador × evento"],
            ["VEM_RESERVA", "Estado/origem da reserva no Sistur"],
            ["VEM_RESERVA_STG", "Foto/histórico intermediário no SIS_MGE"],
            ["CD_SEQUENCIA_IDENTIFICADORA", "Trilha STG ↔ fila"],
            ["MGE_TRG_02", "Trigger crítica de cancelamento na VEM_RESERVA"],
            ["MGE_TABELA / MGE_COLUNA", "Cadastro que amarra trigger × fato gerador"],
            ["SIS_MGE", "Schema do mecanismo"],
            ["IC", "Abertura contábil"],
            ["ODI / GL / EBS", "Integração e contabilização final"],
        ],
        first_cm=6.4,
    ))

    s.append(h1(49, "Códigos que vale guardar desta reunião"))
    s.append(simple_table(
        ["Código", "Significado"],
        [
            ["11", "Fechamento de Caixa — início"],
            ["55", "Modificação da Venda"],
            ["10", "Embarque — cópia do 11 ou 55"],
            ["101", "Evento que dispara a cópia para o 10"],
            ["9", "Cancelamento para reembolso"],
            ["17", "Cancelamento para recadastro"],
            ["34", "Reembolso — disparado na tela, não por trigger"],
            ["35", "Cancelamento da comissão da loja"],
            ["13", "Custo / acordo"],
            ["39", "Fato gerador fixo na package, sem query"],
            ["43", "Cancelamento automático"],
            ["59", "Baixa de recibo sem reserva"],
            ["68", "Fatura"],
            ["52 / 53", "Reembolso de bilhete / faturamento aéreo"],
        ],
    ))

    s.append(h1(50, "O que guardar desta reunião"))
    concepts = [
        ("1. A tela do ME começa pela reserva",
         "Financeiro → Consultas → Mecanismo de Eventos."),
        ("2. Fato gerador cria fila; package cria evento",
         "Trigger/tela → MGE_FILA → package → eventos."),
        ("3. 11 starta o ciclo",
         "Fechamento de caixa."),
        ("4. Sequência identificadora é a trilha",
         "STG, fila e processamento se encontram nela."),
        ("5. A regra do evento está no cadastro SQL",
         "A package orquestra. A query decide se gera."),
        ("6. STG é foto",
         "Trabalha no SIS_MGE para não pesar no Sistur. Nem sempre é VEM_RESERVA_STG."),
        ("7. 10 não é fila nova",
         "É cópia do último 11 ou 55, via evento 101."),
        ("8. 90% é trigger",
         "34 é exceção (tela). 39 é exceção (hard code na package)."),
        ("9. Trigger é delicada",
         "Pode mutar, disparar à toa e gerar fila errada. Olhar trigger da tabela antes de mexer."),
        ("10. ME/IC não calculam",
         "Se o valor nasceu errado no Sistur/Atlas, o ME só empurra. O evento nasce no ME; o IC só abre conta."),
    ]
    for title, body in concepts:
        s.append(P(title, "ConceptNum"))
        s.append(P(body, "BodyLeft"))

    s.append(Spacer(1, 8))
    s.append(hr())
    s.append(P("A frase que resume a reunião", "H2"))
    s.append(callout(
        "Na tela do CUR, comece pela reserva, identifique o fato gerador, pegue a sequência identificadora, "
        "veja a fila e só então os eventos. A package orquestra; a query do cadastro SQL decide o que gera. "
        "A STG é a foto. O embarque copia o último 11 ou 55. Trigger starta quase tudo — e é o ponto mais perigoso. "
        "O evento nasce no Mecanismo de Eventos; o IC só faz a abertura contábil. "
        "<b>Se o valor já veio errado do Sistur, o problema não é do IC.</b>",
        "rule",
    ))
    return s


def main():
    out = "/workspace/Apostila-ME-IC-Parte-2-Tela-Package-Triggers-STG.pdf"
    frame_cover = Frame(28 * mm, 40 * mm, PAGE_W - 46 * mm, PAGE_H - 80 * mm, id="cover")
    frame_body = Frame(MARGIN_L, MARGIN_B, CONTENT_W, PAGE_H - MARGIN_T - MARGIN_B, id="body")
    doc = BaseDocTemplate(
        out,
        pagesize=A4,
        title="Apostila — ME e IC Parte 2: tela, package, triggers e STG",
        author="Treinamento interno",
        subject="Tela do CUR, package, fila, cadastro SQL, triggers e caminho até o IC",
    )
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame_cover], onPage=draw_cover),
        PageTemplate(id="body", frames=[frame_body], onPage=draw_page),
    ])
    doc.build(build_story())
    print(out)


if __name__ == "__main__":
    main()
