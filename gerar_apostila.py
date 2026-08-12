#!/usr/bin/env python3
"""Gera a apostila de treinamento ME/IC em PDF."""

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
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
PAGE_BG = HexColor("#FAFBFC")

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
        self.box_width = width
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
            leftIndent=0,
        )
        # Keep spaces; convert to <br/> and escape
        escaped = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace(" ", "&nbsp;")
            .replace("\n", "<br/>")
        )
        self.p = Paragraph(escaped, style)
        self.box_width = width
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
        "CoverTitle", fontName="Inter-Bold", fontSize=28, leading=34,
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
        "CalloutBold", fontName="Inter-Semi", fontSize=9.5, leading=13.5,
        textColor=NAVY, alignment=TA_LEFT,
    ))
    s.add(ParagraphStyle(
        "Quote", fontName="Inter-Italic", fontSize=10, leading=15,
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
        "Footer", fontName="Inter", fontSize=8, textColor=MUTED,
    ))
    s.add(ParagraphStyle(
        "TOCItem", fontName="Inter", fontSize=9.5, leading=16,
        textColor=SLATE,
    ))
    s.add(ParagraphStyle(
        "ConceptNum", fontName="Inter-Bold", fontSize=11, textColor=TEAL,
        spaceBefore=8, spaceAfter=2,
    ))
    s.add(ParagraphStyle(
        "Caption", fontName="Inter-Med", fontSize=8, leading=11,
        textColor=MUTED, spaceAfter=10, spaceBefore=2,
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
    inner = Paragraph(
        f"<b>{label}.</b> {text}",
        STYLES["Callout"],
    )
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


def simple_table(headers, rows):
    head = [Paragraph(h, STYLES["TableHead"]) for h in headers]
    data = [head]
    for row in rows:
        data.append([Paragraph(str(c), STYLES["TableCell"]) for c in row])
    col_w = CONTENT_W / len(headers)
    # first column narrower for code tables
    if len(headers) == 2:
        widths = [3.4 * cm, CONTENT_W - 3.4 * cm]
    else:
        widths = [col_w] * len(headers)
    t = Table(data, colWidths=widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Inter-Semi"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
        else:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), white))
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
    # bottom band
    canvas.setFillColor(NAVY_MID)
    canvas.rect(0, 0, PAGE_W, 28 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 28 * mm, PAGE_W, 2.2 * mm, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#9BB0C4"))
    canvas.setFont("Inter", 8)
    canvas.drawString(28 * mm, 14 * mm, "Uso interno  ·  Treinamento técnico")
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
    canvas.drawString(MARGIN_L, PAGE_H - 8 * mm, "Apostila  ·  Mecanismo de Eventos e Integrador Contábil")
    canvas.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 8 * mm, "Treinamento interno")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_L, 12 * mm, PAGE_W - MARGIN_R, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Inter", 8)
    canvas.drawString(MARGIN_L, 7 * mm, "ME calcula e processa  ·  IC captura o resultado")
    canvas.drawRightString(PAGE_W - MARGIN_R, 7 * mm, f"{doc.page}")
    canvas.restoreState()


def build_story():
    s = []
    # --- COVER CONTENT (drawn over navy via cover template; we use white text) ---
    s.append(Spacer(1, 55 * mm))
    s.append(Paragraph("APOSTILA DE TREINAMENTO", STYLES["CoverKicker"]))
    s.append(Paragraph("Mecanismo de Eventos<br/>e Integrador Contábil", STYLES["CoverTitle"]))
    s.append(Spacer(1, 8))
    s.append(CoverBar(42 * mm, 3.2, GOLD))
    s.append(Spacer(1, 14))
    s.append(Paragraph(
        "Análise de reservas, fatos geradores, eventos contábeis,<br/>"
        "filas de processamento e investigação de inconsistências.",
        STYLES["CoverSub"],
    ))
    s.append(NextPageTemplate("body"))
    s.append(PageBreak())

    # --- SUMÁRIO ---
    s.append(P("Sumário", "H1"))
    toc = [
        "1. Visão geral",
        "2. Arquitetura conceitual",
        "3. Fato Gerador",
        "4. Ciclo de uma reserva",
        "5. Fechamento de Caixa — Fato Gerador 11",
        "6. Alterações antes e depois do fechamento",
        "7. Fato Gerador 55 — Modificação da Venda",
        "8. Múltiplas modificações",
        "9. Embarque — Fato Gerador 10",
        "10. Diferença entre 11 e 55",
        "11. Ciclo de vida da reserva",
        "12. MGE_EVENTO",
        "13. Evento × Fato Gerador",
        "14. Parametrização dos eventos",
        "15. Quando um evento não aparece",
        "16. MGE_CADASTRO_SQL",
        "17. De onde veio o valor?",
        "18. Sequência identificadora",
        "19. VEM_RESERVA × VEM_RESERVA_STG",
        "20. A fila",
        "21. Status da fila",
        "22. Package",
        "23. Evento relacionado — cadastro SQL = -1",
        "24. Exemplo 13 → 27 → 208",
        "25. Dificuldade na investigação",
        "26–28. Integrador Contábil e contas",
        "29. Onde investigar primeiro",
        "30–33. Reprocessamento",
        "34–36. Ambientes e refresh",
        "37–39. Debug, privilégios e versão",
        "40. Fluxo completo de troubleshooting",
        "41–42. Tabelas e códigos",
        "43. Dez conceitos essenciais",
    ]
    for item in toc:
        s.append(P(item, "TOCItem"))
    s.append(PageBreak())

    # 1
    s.append(h1(1, "Visão geral"))
    s.append(P(
        "O treinamento apresenta o funcionamento do <b>Mecanismo de Eventos (ME)</b> "
        "e do <b>Integrador Contábil (IC)</b>, com foco principalmente na análise de reservas, "
        "geração de fatos geradores, eventos contábeis, filas de processamento e investigação de inconsistências."
    ))
    s.append(P("A ideia central é:"))
    s.append(callout(
        "O Mecanismo de Eventos <b>calcula e processa</b>. O Integrador Contábil <b>captura o resultado</b>. "
        "Essa distinção é fundamental para investigar incidentes.",
        "rule",
    ))

    # 2
    s.append(h1(2, "Arquitetura conceitual"))
    s.append(P("O fluxo simplificado apresentado na reunião é:"))
    s.append(diagram(
        "Reserva → Fato Gerador → Eventos → Fila → Package/Cadastro SQL\n"
        "        → Eventos Contábeis → Integrador Contábil"
    ))
    s.append(P("Cada etapa possui uma responsabilidade diferente."))
    s.append(h2("Mecanismo de Eventos"))
    s.append(P("É responsável por:"))
    s.extend(bullets([
        "processar os fatos geradores;",
        "realizar cálculos;",
        "gerar os eventos;",
        "capturar o ciclo de vida da reserva, bilhete ou fatura;",
        "determinar os valores que serão posteriormente enviados ao contábil.",
    ]))
    s.append(h2("Integrador Contábil"))
    s.append(P("O IC <b>não realiza o cálculo original</b>. Ele recebe/captura aquilo que já foi processado pelo Mecanismo de Eventos."))
    s.append(callout(
        "Se o IC recebeu um valor errado, o primeiro lugar a investigar normalmente é o <b>Mecanismo de Eventos</b>.",
        "alert",
    ))
    s.append(P("Exemplo:"))
    s.append(diagram(
        "Mecanismo de Eventos\n"
        "        │\n"
        "        │  calcula R$ 218,96\n"
        "        ▼\n"
        "Evento contábil\n"
        "        │\n"
        "        ▼\n"
        "Integrador Contábil\n"
        "        │\n"
        "        ▼\n"
        "Débito / Crédito"
    ))
    s.append(P("Se os R$ 218,96 estiverem errados, o problema provavelmente está <b>antes</b> do IC."))

    # 3
    s.append(h1(3, "Fato Gerador"))
    s.append(P(
        "O fato gerador representa algo que aconteceu no ciclo de vida da reserva, bilhete ou fatura. "
        "É o acontecimento que inicia determinado processamento."
    ))
    s.append(P("Exemplos citados no treinamento:"))
    s.append(simple_table(
        ["Código", "Fato Gerador"],
        [
            ["11", "Fechamento de Caixa"],
            ["10", "Embarque"],
            ["55", "Modificação da Venda"],
            ["34", "Reembolso"],
            ["17", "Cancelamento"],
            ["9", "Cancelamento"],
            ["38", "Emissão de Nota Fiscal"],
        ],
    ))
    s.append(P("Existem diversos outros fatos geradores cadastrados no sistema. Eles podem estar relacionados a:"))
    s.extend(bullets([
        "reservas;",
        "bilhetes;",
        "faturas;",
        "cancelamentos;",
        "reembolsos;",
        "alterações;",
        "embarques;",
        "emissão de documentos, etc.",
    ]))

    # 4
    s.append(h1(4, "O exemplo mais importante: ciclo de uma reserva"))
    s.append(P("Um exemplo de caminho feliz apresentado na reunião seria:"))
    s.append(diagram(
        "Reserva\n"
        "   │\n"
        "   ▼\n"
        "Fato Gerador 11  —  Fechamento de Caixa\n"
        "   │\n"
        "   ▼\n"
        "Eventos\n"
        "   │\n"
        "   ▼\n"
        "Fato Gerador 10  —  Embarque\n"
        "   │\n"
        "   ▼\n"
        "Eventos\n"
        "   │\n"
        "   ▼\n"
        "Fato Gerador 38  —  Emissão da NF\n"
        "   │\n"
        "   ▼\n"
        "Eventos\n"
        "   │\n"
        "   ▼\n"
        "Integrador Contábil"
    ))
    s.append(P("Quando não ocorre nenhuma alteração na reserva, o fluxo é relativamente simples."))

    # 5
    s.append(h1(5, "Fechamento de Caixa — Fato Gerador 11"))
    s.append(P(
        "O fato gerador 11 é extremamente importante. Ele representa o Fechamento de Caixa "
        "e funciona como o início do ciclo contábil da reserva."
    ))
    s.append(callout(
        "O fechamento de caixa é o <b>start do ciclo contábil da reserva</b>. "
        "Antes dele, a reserva pode sofrer alterações comerciais sem gerar os fatos geradores "
        "contábeis que serão tratados pelo mecanismo.",
        "rule",
    ))
    s.append(h2("5.1 Uma reserva pode ter mais de um fechamento?"))
    s.append(P("Não. Segundo o treinamento:"))
    s.append(callout(
        "Uma reserva deve possuir <b>apenas um fato gerador 11</b>. "
        "Se existirem dois fechamentos de caixa para a mesma reserva, isso é considerado uma inconsistência.",
        "alert",
    ))

    # 6
    s.append(h1(6, "Alterações antes e depois do fechamento"))
    s.append(P("Essa diferença é muito importante."))
    s.append(h2("Antes do fechamento"))
    s.append(P(
        "A reserva ainda está aberta. O pessoal comercial pode alterar a reserva. "
        "Essas alterações ficam registradas no histórico da reserva, mas ainda não representam "
        "necessariamente uma Modificação da Venda como fato gerador contábil."
    ))
    s.append(h2("Depois do fechamento"))
    s.append(P("A partir do momento em que o caixa foi fechado, uma alteração relevante pode gerar:"))
    s.append(P("<b>Fato Gerador 55 — Modificação da Venda</b>"))
    s.append(diagram(
        "Reserva\n"
        "   │\n"
        "   ├── Cliente altera pacote\n"
        "   ├── Altera data\n"
        "   ├── Inclui serviço\n"
        "   └── Remove serviço"
    ))
    s.append(P("Essas alterações podem provocar impactos financeiros e contábeis."))

    # 7
    s.append(h1(7, "Fato Gerador 55 — Modificação da Venda"))
    s.append(P("Quando ocorre uma modificação depois do fechamento:"))
    s.append(diagram(
        "11 — Fechamento\n"
        "        │\n"
        "        ▼\n"
        "     STORNO\n"
        "        │\n"
        "        ▼\n"
        "55 — Modificação da Venda\n"
        "     NORMAL"
    ))
    s.append(P(
        "O fechamento original deixa de representar o estado atual daquela reserva. "
        "Por isso, o fato gerador 11 é estornado e um novo fato gerador 55 representa a alteração."
    ))

    # 8
    s.append(h1(8, "Múltiplas modificações"))
    s.append(P("Uma reserva pode ser modificada diversas vezes. Exemplo:"))
    s.append(diagram(
        "11 — Fechamento\n"
        "│\n"
        "├── eventos\n"
        "▼\n"
        "55 — Modificação 1\n"
        "│\n"
        "├── eventos\n"
        "▼\n"
        "55 — Modificação 2\n"
        "│\n"
        "├── eventos\n"
        "▼\n"
        "55 — Modificação 3\n"
        "│\n"
        "▼\n"
        "10 — Embarque"
    ))
    s.append(P(
        "Cada modificação representa uma nova etapa no histórico. "
        "Isso explica por que algumas reservas possuem vários fatos geradores."
    ))

    # 9
    s.append(h1(9, "Embarque — Fato Gerador 10"))
    s.append(P("O fato gerador 10 representa o embarque. Existe uma regra importante:"))
    s.append(callout(
        "O embarque deve refletir o <b>estado mais recente da reserva</b> antes do embarque.",
        "rule",
    ))
    s.append(h2("Sem modificações"))
    s.append(diagram(
        "11 — Fechamento\n"
        "       │\n"
        "       ▼\n"
        "10 — Embarque\n"
        "       │\n"
        "       ▼\n"
        "38 — Emissão da NF"
    ))
    s.append(h2("Com modificações"))
    s.append(diagram(
        "11 — Fechamento\n"
        "       │\n"
        "       ▼\n"
        "55 — Modificação\n"
        "       │\n"
        "       ▼\n"
        "55 — Modificação\n"
        "       │\n"
        "       ▼\n"
        "10 — Embarque"
    ))
    s.append(P("O embarque deverá refletir a última modificação ocorrida antes dele."))

    # 10
    s.append(h1(10, "Diferença entre 11 e 55"))
    s.append(P("Uma dúvida levantada durante a reunião foi se o 55 simplesmente substitui o 11. A resposta é:"))
    s.append(P(
        "<b>Sim</b>, conceitualmente o 55 substitui o estado contábil anterior representado pelo 11, "
        "através do estorno do 11. Porém o 10 — embarque — é outro fato gerador."
    ))
    s.append(diagram(
        "11 — Fechamento     NORMAL  →  fica STORNO\n"
        "55 — Modificação    NORMAL  →  permanece NORMAL\n"
        "10 — Embarque       NORMAL  →  permanece NORMAL"
    ))

    # 11
    s.append(h1(11, "Ciclo de vida da reserva"))
    s.append(P("Uma maneira simples de visualizar:"))
    s.append(diagram(
        "                    RESERVA\n"
        "                       │\n"
        "                       ▼\n"
        "             11 — FECHAMENTO\n"
        "                       │\n"
        "              ┌────────┴────────┐\n"
        "              │                 │\n"
        "         Sem alteração       Alteração\n"
        "              │                 │\n"
        "              │                 ▼\n"
        "              │            55 — MODIFICAÇÃO\n"
        "              │                 │\n"
        "              │           (pode ocorrer outra)\n"
        "              │                 │\n"
        "              └────────┬────────┘\n"
        "                       ▼\n"
        "                 10 — EMBARQUE\n"
        "                       │\n"
        "                       ▼\n"
        "               38 — EMISSÃO NF\n"
        "                       │\n"
        "                       ▼\n"
        "                      IC"
    ))

    # 12
    s.append(h1(12, "MGE_EVENTO"))
    s.append(P("Uma das principais tabelas citadas é <b>MGE_EVENTO</b>. Ela contém o cadastro dos eventos existentes no sistema. É possível consultar:"))
    s.extend(bullets([
        "código do evento;",
        "descrição;",
        "cadastro SQL relacionado;",
        "parâmetros;",
        "relacionamentos;",
        "outras informações de configuração.",
    ]))
    s.append(P("Exemplos de eventos:"))
    s.append(simple_table(
        ["Código", "Descrição"],
        [
            ["13", "Repasse líquido de acordo"],
            ["27", "Evento relacionado ao 13"],
            ["208", "Outro evento relacionado ao mesmo processamento"],
            ["155", "Comissão de Recibo Complementar de Serviços"],
        ],
    ))

    # 13
    s.append(h1(13, "Evento × Fato Gerador"))
    s.append(P("Essa é uma das distinções mais importantes da reunião."))
    s.append(h2("Fato gerador"))
    s.append(P("É o que aconteceu. Exemplo: fechamento de caixa."))
    s.append(h2("Evento"))
    s.append(P("É o que foi gerado/processado em consequência daquele fato. Exemplo: repasse líquido, margem, comissão etc."))
    s.append(callout(
        "Analogia do treinamento: <b>nota fiscal = fato gerador</b> e <b>itens da nota = eventos</b>. "
        "Não é uma equivalência técnica perfeita, mas ajuda a entender o conceito.",
        "info",
    ))

    # 14
    s.append(h1(14, "Parametrização dos eventos"))
    s.append(P("Um evento não pode simplesmente aparecer em qualquer fato gerador. Existe uma parametrização determinando <b>quais fatos geradores podem gerar determinado evento</b>."))
    s.append(P("Por exemplo, o evento 155 foi apresentado como estando vinculado aos fatos geradores:"))
    s.extend(bullets([
        "11 — Fechamento de Caixa;",
        "55 — Modificação da Venda;",
        "60 — Lançamento de Recibo Complementar.",
    ]))
    s.append(P("Portanto, ele não deveria aparecer associado arbitrariamente a outro fato gerador que não esteja parametrizado."))

    # 15
    s.append(h1(15, "O que pode causar um evento não aparecer?"))
    s.append(P("Se o evento está corretamente parametrizado, mas não foi gerado, é necessário investigar outras causas. Possibilidades citadas:"))
    s.extend(bullets([
        "problema na fila;",
        "intermitência no processamento;",
        "fila muito antiga;",
        "valor calculado igual a zero;",
        "problema de cadastro;",
        "problema no processamento do fato gerador;",
        "problema na package responsável pelo processamento.",
    ]))
    s.append(callout(
        "Um evento <b>não deveria ser gerado</b> se não estiver parametrizado para aquele fato gerador.",
        "rule",
    ))

    # 16
    s.append(h1(16, "MGE_CADASTRO_SQL"))
    s.append(P("Outro objeto fundamental é o cadastro SQL. O evento aponta para um cadastro SQL. Exemplo apresentado:"))
    s.append(diagram(
        "Evento 13\n"
        "   │\n"
        "   ▼\n"
        "Cadastro SQL 73\n"
        "   │\n"
        "   ▼\n"
        "Consulta SQL\n"
        "   │\n"
        "   ▼\n"
        "Valores e informações do evento"
    ))
    s.append(P("Esse SQL é responsável por buscar/compor as informações utilizadas na geração do evento."))

    # 17
    s.append(h1(17, "Como descobrir de onde veio o valor?"))
    s.append(P("Essa é uma das partes mais importantes para análise de incidentes. Imagine que o sistema mostra: <b>Evento 13 = R$ 218,96</b>."))
    s.append(P("A pergunta é: de onde vieram esses R$ 218,96? O caminho apresentado é:"))
    s.append(diagram(
        "Evento\n"
        "   │\n"
        "   ▼\n"
        "MGE_EVENTO\n"
        "   │\n"
        "   ▼\n"
        "Cadastro SQL\n"
        "   │\n"
        "   ▼\n"
        "SQL\n"
        "   │\n"
        "   ▼\n"
        "Tabelas utilizadas\n"
        "   │\n"
        "   ▼\n"
        "Composição do valor"
    ))
    s.append(P("Assim é possível descobrir como o sistema chegou ao valor."))

    # 18
    s.append(h1(18, "Sequência identificadora"))
    s.append(P(
        "A sequência identificadora é um dos elementos mais importantes para rastreamento. "
        "Ela permite identificar determinada alteração/processamento da reserva. "
        "Com ela é possível chegar à fila correspondente."
    ))
    s.append(diagram(
        "Reserva\n"
        "   │\n"
        "   ▼\n"
        "Sequência Identificadora\n"
        "   │\n"
        "   ▼\n"
        "Fila\n"
        "   │\n"
        "   ▼\n"
        "Processamento\n"
        "   │\n"
        "   ▼\n"
        "Fato Gerador\n"
        "   │\n"
        "   ▼\n"
        "Package"
    ))
    s.append(P("Ela também é utilizada para simular determinados SQLs apresentados durante a análise."))

    # 19
    s.append(h1(19, "VEM_RESERVA × VEM_RESERVA_STG"))
    s.append(h2("VEM_RESERVA"))
    s.append(P("Representa o <b>estado atual</b> da reserva. Em geral, existe uma linha representando o estado atual."))
    s.append(h2("VEM_RESERVA_STG"))
    s.append(P("Funciona como um <b>histórico das alterações</b>. Cada alteração pode gerar uma nova linha."))
    s.append(diagram(
        "VEM_RESERVA\n"
        "     │\n"
        "     └── Estado atual\n"
        "\n"
        "VEM_RESERVA_STG\n"
        "     │\n"
        "     ├── Estado 1\n"
        "     ├── Estado 2\n"
        "     ├── Estado 3\n"
        "     ├── Estado 4\n"
        "     └── ..."
    ))
    s.append(P("A sequência identificadora permite saber a ordem das alterações."))

    # 20
    s.append(h1(20, "A fila"))
    s.append(P("A fila é responsável por armazenar o processamento que precisa ser realizado. Ela contém informações relacionadas ao:"))
    s.extend(bullets([
        "fato gerador;",
        "sequência identificadora;",
        "criação;",
        "processamento;",
        "status.",
    ]))
    s.append(P("Um dos caminhos de investigação apresentados é:"))
    s.append(diagram("Reserva  →  Sequência identificadora  →  Fila  →  Status"))

    # 21
    s.append(h1(21, "Status da fila"))
    s.append(P("Foram apresentados quatro status:"))
    s.append(simple_table(
        ["Status", "Significado"],
        [
            ["1", "Aberto"],
            ["2", "Processando"],
            ["3", "Processado com sucesso"],
            ["4", "Erro"],
        ],
    ))
    s.append(P("Isso é extremamente útil em troubleshooting. Se o fato gerador deveria existir, mas não apareceu:"))
    s.extend(bullets([
        "obtenha a sequência identificadora;",
        "consulte a fila;",
        "verifique o status.",
    ]))
    s.append(P("<b>3</b> → processamento concluído com sucesso. &nbsp; <b>4</b> → existe erro no processamento. &nbsp; <b>1</b> → ainda está aberto. &nbsp; <b>2</b> → está sendo processado."))

    # 22
    s.append(h1(22, "Package"))
    s.append(P("A package tem uma função diferente do cadastro SQL. Durante a reunião foi explicado que:"))
    s.append(callout("Quem gera o fato gerador é a <b>package</b>.", "rule"))
    s.append(P("Portanto, quando o problema é <i>“o fato gerador nem sequer foi criado”</i>, é necessário investigar a package responsável."))
    s.append(P("Já quando o problema é <i>“o fato gerador existe, mas determinado evento está errado”</i>, a investigação tende a passar por:"))
    s.append(diagram("MGE_EVENTO  →  Cadastro SQL  →  SQL  →  dados utilizados"))

    # 23
    s.append(h1(23, "Evento relacionado — cadastro SQL = -1"))
    s.append(P("Um ponto mais avançado apresentado foi o cadastro SQL com valor <b>-1</b>. Exemplo:"))
    s.append(diagram(
        "Evento 13     Cadastro SQL = 73\n"
        "Evento 27     Cadastro SQL = -1"
    ))
    s.append(P("Nesse caso, o evento 27 não é necessariamente gerado de forma independente. Ele pode ser um complemento/relacionado ao evento 13."))
    s.append(callout(
        "Evento com cadastro SQL <b>-1</b> não é gerado sozinho. Ele depende de outro evento.",
        "rule",
    ))

    # 24
    s.append(h1(24, "Exemplo 13 → 27 → 208"))
    s.append(P("Foi mostrado um SQL que pode retornar diferentes eventos dependendo da linha. Conceitualmente:"))
    s.append(diagram(
        "Linha 1  →  Evento 13   (busca custo)\n"
        "Linha 2  →  Evento 27   (calcula diferença / preço − custo)\n"
        "Linha 3  →  Evento 208  (busca determinado valor)"
    ))
    s.append(P(
        "O mesmo cadastro SQL pode produzir mais de um evento. O SQL utiliza condições para alterar o cálculo "
        "dependendo do evento retornado. Isso explica por que simplesmente olhar o código do evento pode não ser suficiente: "
        "é necessário analisar o SQL."
    ))

    # 25
    s.append(h1(25, "Uma dificuldade importante na investigação"))
    s.append(P("Nem sempre eventos relacionados possuem códigos sequenciais. Por exemplo, 90 → 91 pode parecer fácil. Mas 13 → 27 não é óbvio."))
    s.append(callout(
        "Quando existe um evento com <b>CADASTRO_SQL = -1</b>, é necessário entrar no SQL do evento relacionado e analisar como ele determina os eventos.",
        "info",
    ))

    # 26
    s.append(h1(26, "Integrador Contábil"))
    s.append(P("Depois que o Mecanismo de Eventos processa tudo, os resultados chegam ao Integrador Contábil. No IC é possível consultar os fatos geradores e seus respectivos eventos. O exemplo apresentado mostrou:"))
    s.append(diagram(
        "Fato Gerador 11\n"
        "   ├── Evento 90\n"
        "   ├── Débito\n"
        "   └── Crédito\n"
        "\n"
        "Fato Gerador 55\n"
        "   ├── Eventos\n"
        "   ├── Débitos\n"
        "   └── Créditos\n"
        "\n"
        "Fato Gerador 10\n"
        "   ├── Eventos\n"
        "   ├── Débitos\n"
        "   └── Créditos"
    ))

    # 27
    s.append(h1(27, "O papel contábil do IC"))
    s.append(P("O IC trabalha com <b>Débito × Crédito</b>. Cada evento pode estar associado a contas contábeis. Existe uma parametrização determinando:"))
    s.extend(bullets([
        "qual conta será utilizada;",
        "se será débito;",
        "se será crédito;",
        "quais condições determinam a conta.",
    ]))

    # 28
    s.append(h1(28, "Cadastro de contas contábeis"))
    s.append(P("Foi mencionado o conceito de cadastro de contas/ações contábeis. Para determinado fato gerador e evento, existem configurações que determinam como o lançamento será contabilizado. Por exemplo:"))
    s.append(diagram(
        "Evento\n"
        "   │\n"
        "   ├── Conta A  →  Débito\n"
        "   └── Conta B  →  Crédito"
    ))
    s.append(P("Outro evento pode possuir três ou mais contas, dependendo das regras."))

    # 29
    s.append(h1(29, "Onde investigar primeiro?"))
    s.append(P("Essa é provavelmente a parte mais útil da reunião."))
    s.append(h2("Cenário 1 — O fato gerador não existe"))
    s.append(diagram("Reserva  →  Sequência / histórico  →  Fila  →  Package"))
    s.append(P("Porque quem gera o fato gerador é a package."))
    s.append(h2("Cenário 2 — Fato gerador existe, evento não existe"))
    s.append(diagram("Fato Gerador  →  Parametrização  →  MGE_EVENTO  →  Cadastro SQL  →  Fila/processamento"))
    s.append(h2("Cenário 3 — Evento existe, mas valor está errado"))
    s.append(diagram("Evento  →  MGE_EVENTO  →  Cadastro SQL  →  SQL  →  Tabelas  →  Composição do valor"))
    s.append(h2("Cenário 4 — Evento está correto no ME, mas errado no IC"))
    s.append(diagram("Mecanismo de Eventos  →  IC  →  Parametrização contábil  →  Conta / Débito / Crédito"))

    # 30
    s.append(h1(30, "Reprocessamento"))
    s.append(P("O treinamento também explicou uma regra muito importante sobre reprocessamento."))
    s.append(h2("Homologação"))
    s.append(P("É onde normalmente são feitos: testes, investigação, reprocessamentos, validações e comprovação de correções."))
    s.append(h2("Produção"))
    s.append(P("Normalmente <b>não se reprocessa</b> uma reserva em produção simplesmente para corrigir o passado. O procedimento normal é:"))
    s.append(diagram(
        "Problema\n"
        " ↓\n"
        "Investigar em Homologação\n"
        " ↓\n"
        "Corrigir regra/código\n"
        " ↓\n"
        "Testar\n"
        " ↓\n"
        "Versionar\n"
        " ↓\n"
        "Subir para Produção\n"
        " ↓\n"
        "Daí em diante o processamento fica correto"
    ))

    # 31
    s.append(h1(31, "Exceções em produção"))
    s.append(P("Existem situações excepcionais. Se houver grande volume de reservas, impacto financeiro relevante, problema urgente ou necessidade de correção em massa, pode ser necessário criar um script de ajuste em produção."))
    s.append(callout("Isso é tratado como uma situação <b>excepcional</b>.", "alert"))

    # 32
    s.append(h1(32, "Reprocessamento com modificação de venda"))
    s.append(P("Essa é uma regra que merece destaque. Imagine:"))
    s.append(diagram("11 — Fechamento   →   55 — Modificação   →   10 — Embarque"))
    s.append(P("Se for necessário reprocessar essa reserva, <b>não se deve simplesmente apagar tudo</b>. Existe um script específico que preserva o fato gerador 11."))
    s.append(P("Por quê? Porque o fato gerador 55 depende das informações relacionadas ao fechamento original."))
    s.append(callout(
        "Quando existe Modificação da Venda (55), o reprocessamento deve <b>preservar o 11</b>.",
        "rule",
    ))

    # 33
    s.append(h1(33, "Caminho feliz"))
    s.append(P("Quando não existem modificações:"))
    s.append(diagram("11 — Fechamento  →  10 — Embarque  →  38 — Emissão"))
    s.append(P("Nesse caso, o reprocessamento pode excluir e gerar novamente o fluxo porque o embarque refletirá o fechamento."))

    # 34
    s.append(h1(34, "Ambientes"))
    s.append(P("Foram citados três ambientes principais — <b>DEV</b>, <b>HOMOLOG</b> e <b>PROD</b> — além do ambiente TI, utilizado em determinados processos de versionamento/RFC."))
    s.append(h2("DEV"))
    s.append(P("Normalmente utilizado para alteração de código: packages, functions, procedures, triggers, views e alterações estruturais."))
    s.append(h2("HOMOLOG"))
    s.append(P("Principal ambiente de trabalho para testes, scripts, ajustes de cadastro, validações e reprocessamentos."))
    s.append(h2("PROD"))
    s.append(P("Ambiente produtivo. Alterações devem seguir o processo de versionamento/RFC."))

    # 35
    s.append(h1(35, "Código × Configuração"))
    s.append(h2("Alteração de código"))
    s.append(P("Exemplos: package, procedure, function, trigger, view. Normalmente:"))
    s.append(diagram("DEV  →  RFC  →  HOMOLOG  →  PROD"))
    s.append(h2("Alteração / configuração"))
    s.append(P("Exemplos: cadastro SQL e parametrizações. O trabalho pode ocorrer diretamente em homologação conforme o processo da equipe."))

    # 36
    s.append(h1(36, "Refresh dos ambientes"))
    s.append(P(
        "Foi comentado que o refresh entre ambientes não é necessariamente recente. "
        "Na reunião, foi mencionado que o último refresh estava há aproximadamente três meses. "
        "Isso significa que homologação pode não representar exatamente o estado atual de produção."
    ))
    s.append(callout(
        "Se você reproduzir um problema em homologação e não encontrar o mesmo comportamento, "
        "considere a diferença entre as bases.",
        "alert",
    ))

    # 37
    s.append(h1(37, "Debug"))
    s.append(P("O debug é especialmente importante quando o fato gerador <b>não está sendo criado</b>, porque a package é responsável pela geração."))
    s.append(P("Se o fato gerador existe, muitas vezes é possível investigar o evento através do cadastro SQL sem precisar debugar. Mas se a reserva deveria gerar fato gerador e não gerou, pode ser necessário entrar na package e acompanhar a execução."))

    # 38
    s.append(h1(38, "Connect Session"))
    s.append(P(
        "Foi comentado que o debug depende de determinados privilégios, incluindo acesso relacionado a Connect Session. "
        "Após refresh dos ambientes, esses privilégios podem ser perdidos. "
        "Por isso, em determinadas situações, pode ser necessário solicitar novamente o acesso adequado."
    ))

    # 39
    s.append(h1(39, "Controle de versão"))
    s.append(P("O sistema possui controle de versão dos objetos. É possível consultar versão em produção, versão em homologação, histórico, arquivos e alterações. Isso é útil para responder:"))
    s.extend(bullets([
        "O código de produção é igual ao de homologação?",
        "Quando essa package foi alterada?",
    ]))

    # 40
    s.append(h1(40, "Fluxo completo de troubleshooting"))
    s.append(P("Juntando tudo que foi explicado na reunião, o fluxo mental ideal é:"))
    s.append(diagram(
        "                 PROBLEMA\n"
        "                    │\n"
        "                    ▼\n"
        "              Identificar reserva\n"
        "                    │\n"
        "                    ▼\n"
        "             Identificar fato gerador\n"
        "                    │\n"
        "          ┌─────────┴─────────┐\n"
        "          │                   │\n"
        "       EXISTE?              NÃO EXISTE\n"
        "          │                   │\n"
        "          │                   ▼\n"
        "          │              Verificar fila\n"
        "          │                   │\n"
        "          │                   ▼\n"
        "          │                Package\n"
        "          ▼\n"
        "     Verificar eventos\n"
        "          │\n"
        "          ▼\n"
        "   Evento está correto?\n"
        "      │            │\n"
        "     SIM           NÃO\n"
        "      │             │\n"
        "      │             ▼\n"
        "      │       MGE_EVENTO → Cadastro SQL → SQL → Tabelas/valores\n"
        "      ▼\n"
        "Integrador Contábil → Débito/Crédito → Parametrização contábil"
    ))

    # 41
    s.append(h1(41, "Principais tabelas/objetos citados"))
    s.append(simple_table(
        ["Objeto", "Função"],
        [
            ["MGE_EVENTO", "Cadastro dos eventos"],
            ["MGE_FATO_GERADOR", "Cadastro dos fatos geradores"],
            ["MGE_CADASTRO_SQL", "SQL utilizado na geração/consulta dos eventos"],
            ["VEM_RESERVA", "Estado atual da reserva"],
            ["VEM_RESERVA_STG", "Histórico das alterações da reserva"],
            ["Fila", "Controle do processamento dos fatos geradores"],
            ["Package", "Geração/processamento dos fatos geradores"],
            ["IC", "Integração/contabilização dos eventos"],
        ],
    ))

    # 42
    s.append(h1(42, "Códigos que vale decorar inicialmente"))
    s.append(P("Não é necessário decorar todos os códigos agora. Os mais importantes apresentados na reunião são:"))
    s.append(simple_table(
        ["Código", "Significado"],
        [
            ["11", "Fechamento de Caixa"],
            ["10", "Embarque"],
            ["55", "Modificação da Venda"],
            ["38", "Emissão de NF"],
            ["34", "Reembolso"],
            ["17", "Cancelamento"],
            ["9", "Cancelamento"],
            ["13", "Repasse Líquido de Acordo"],
            ["27", "Evento relacionado ao 13"],
            ["208", "Evento relacionado ao mesmo processamento"],
            ["155", "Comissão de Recibo Complementar"],
        ],
    ))

    # 43
    s.append(h1(43, "O que você realmente precisa guardar"))
    s.append(P("Se a reunião fosse reduzida a 10 conceitos essenciais, seriam estes:"))

    concepts = [
        ("1. ME ≠ IC", "ME calcula/processa. IC captura/contabiliza."),
        ("2. Fato gerador ≠ evento", "Fato gerador = o que aconteceu. Evento = consequência/processamento daquele fato."),
        ("3. 11 é extremamente importante", "11 = Fechamento de Caixa. É o início do ciclo contábil."),
        ("4. 55 representa alteração", "55 = Modificação da Venda. Quando ocorre depois do fechamento, o 11 é estornado."),
        ("5. 10 é embarque", "O embarque deve refletir o último estado válido da reserva."),
        ("6. A sequência identificadora é sua trilha", "Ela permite acompanhar: Reserva → alteração → fila → processamento."),
        ("7. Fila é fundamental", "Sempre que algo deveria ter sido processado e não foi, consulte a fila. 1 = aberto · 2 = processando · 3 = sucesso · 4 = erro."),
        ("8. Evento errado → Cadastro SQL", "Se o evento existe mas o valor está errado: MGE_EVENTO → Cadastro SQL → SQL → tabelas."),
        ("9. Fato gerador não criado → Package", "Se nem o fato gerador apareceu, investigue a package."),
        ("10. IC errado não significa necessariamente problema no IC", "Primeiro descubra o que o ME produziu. Se o ME já produziu errado, o problema está antes do IC."),
    ]
    for title, body in concepts:
        s.append(P(title, "ConceptNum"))
        s.append(P(body, "BodyLeft"))

    s.append(Spacer(1, 8))
    s.append(hr())
    s.append(P("A frase que resume praticamente toda a reunião", "H2"))
    s.append(callout(
        "Para descobrir um problema contábil, primeiro entenda o ciclo de vida da reserva, "
        "identifique o fato gerador, veja quais eventos foram produzidos, rastreie a sequência pela fila e, "
        "se necessário, chegue até o cadastro SQL ou package que gerou aquele resultado. "
        "<b>Só depois analise o Integrador Contábil.</b>",
        "rule",
    ))
    return s


def main():
    out = "/workspace/Apostila-Mecanismo-de-Eventos-e-Integrador-Contabil.pdf"
    frame_cover = Frame(28 * mm, 40 * mm, PAGE_W - 46 * mm, PAGE_H - 80 * mm, id="cover")
    frame_body = Frame(MARGIN_L, MARGIN_B, CONTENT_W, PAGE_H - MARGIN_T - MARGIN_B, id="body")
    doc = BaseDocTemplate(
        out,
        pagesize=A4,
        title="Apostila — Treinamento do Mecanismo de Eventos e Integrador Contábil",
        author="Treinamento interno",
        subject="ME e IC — fatos geradores, eventos, filas e troubleshooting",
    )
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame_cover], onPage=draw_cover),
        PageTemplate(id="body", frames=[frame_body], onPage=draw_page),
    ])
    doc.build(build_story())
    print(out)


if __name__ == "__main__":
    main()
