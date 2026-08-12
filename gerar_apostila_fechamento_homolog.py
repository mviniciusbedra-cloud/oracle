#!/usr/bin/env python3
"""Gera a mini-apostila de fechamento sob demanda em Homolog."""

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
        self.content.wrap(width - 2 * pad, 10000)
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
            "diag", fontName="JetBrains", fontSize=8, leading=11.5, textColor=NAVY,
        )
        escaped = (
            text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace(" ", "&nbsp;").replace("\n", "<br/>")
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
    s.add(ParagraphStyle("CoverKicker", fontName="Inter-Med", fontSize=10, textColor=GOLD,
                         tracking=1.4, alignment=TA_LEFT, spaceAfter=8))
    s.add(ParagraphStyle("CoverTitle", fontName="Inter-Bold", fontSize=24, leading=30,
                         textColor=white, alignment=TA_LEFT, spaceAfter=10))
    s.add(ParagraphStyle("CoverSub", fontName="Inter", fontSize=12, leading=17,
                         textColor=HexColor("#D7E2EE"), alignment=TA_LEFT))
    s.add(ParagraphStyle("H1", fontName="Inter-Bold", fontSize=14.5, leading=19,
                         textColor=NAVY, spaceBefore=14, spaceAfter=7))
    s.add(ParagraphStyle("H2", fontName="Inter-Semi", fontSize=12, leading=16,
                         textColor=TEAL, spaceBefore=10, spaceAfter=5))
    s.add(ParagraphStyle("Body", fontName="Inter", fontSize=9.5, leading=13.5,
                         textColor=SLATE, alignment=TA_JUSTIFY, spaceAfter=7))
    s.add(ParagraphStyle("BodyLeft", fontName="Inter", fontSize=9.5, leading=13.5,
                         textColor=SLATE, alignment=TA_LEFT, spaceAfter=7))
    s.add(ParagraphStyle("BulletBody", fontName="Inter", fontSize=9.5, leading=13.5,
                         textColor=SLATE, leftIndent=12, spaceAfter=2))
    s.add(ParagraphStyle("Callout", fontName="Inter", fontSize=9.5, leading=13.5,
                         textColor=NAVY, alignment=TA_LEFT))
    s.add(ParagraphStyle("TableHead", fontName="Inter-Semi", fontSize=8.5, leading=11,
                         textColor=white, alignment=TA_LEFT))
    s.add(ParagraphStyle("TableCell", fontName="Inter", fontSize=8.5, leading=11.5,
                         textColor=SLATE, alignment=TA_LEFT))
    s.add(ParagraphStyle("TOCItem", fontName="Inter", fontSize=9.5, leading=15,
                         textColor=SLATE))
    s.add(ParagraphStyle("ConceptNum", fontName="Inter-Bold", fontSize=11, textColor=TEAL,
                         spaceBefore=8, spaceAfter=2))
    return s


STYLES = make_styles()
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


def P(text, style="Body"):
    return Paragraph(text, STYLES[style])


def h1(n, title):
    return P(f"{n}. {title}", "H1")


def callout(text, kind="info"):
    if kind == "rule":
        bg, border, label = GOLD_BG, GOLD, "Regra"
    elif kind == "alert":
        bg, border, label = RED_SOFT, RED, "Atenção"
    else:
        bg, border, label = TEAL_LIGHT, TEAL, "Ponto-chave"
    inner = Paragraph(f"<b>{label}.</b> {text}", STYLES["Callout"])
    return KeepTogether([ColoredBox(inner, bg, border, CONTENT_W), Spacer(1, 8)])


def bullets(items):
    flow = [Paragraph(f"•  {item}", STYLES["BulletBody"]) for item in items]
    flow.append(Spacer(1, 6))
    return flow


def simple_table(headers, rows, first_cm=4.0):
    head = [Paragraph(h, STYLES["TableHead"]) for h in headers]
    data = [head] + [[Paragraph(str(c), STYLES["TableCell"]) for c in row] for row in rows]
    widths = [first_cm * cm, CONTENT_W - first_cm * cm] if len(headers) == 2 else [CONTENT_W / len(headers)] * len(headers)
    t = Table(data, colWidths=widths, repeatRows=1)
    cmds = [
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
        cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT if i % 2 == 0 else white))
    t.setStyle(TableStyle(cmds))
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
    canvas.drawString(28 * mm, 14 * mm, "Uso interno  ·  Mini-apostila operacional")
    canvas.drawRightString(PAGE_W - 18 * mm, 14 * mm, "Extrato  ·  Homologação")
    canvas.restoreState()


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 1.4 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Inter", 7.5)
    canvas.drawString(MARGIN_L, PAGE_H - 8 * mm, "Mini-apostila  ·  Fechamento sob demanda em Homolog")
    canvas.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 8 * mm, "Treinamento interno")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_L, 12 * mm, PAGE_W - MARGIN_R, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Inter", 8)
    canvas.drawString(MARGIN_L, 7 * mm, "Fecha filial sob demanda sem bagunçar o extrato dos outros")
    canvas.drawRightString(PAGE_W - MARGIN_R, 7 * mm, f"{doc.page}")
    canvas.restoreState()


def build_story():
    s = []
    s.append(Spacer(1, 50 * mm))
    s.append(Paragraph("MINI-APOSTILA OPERACIONAL", STYLES["CoverKicker"]))
    s.append(Paragraph("Fechamento sob demanda<br/>em Homologação", STYLES["CoverTitle"]))
    s.append(Spacer(1, 8))
    s.append(CoverBar(42 * mm, 3.2, GOLD))
    s.append(Spacer(1, 14))
    s.append(Paragraph(
        "Dois scripts: parametrizar filial(is) e rodar o fechamento<br/>"
        "sem impactar cenários de segunda a sexta.",
        STYLES["CoverSub"],
    ))
    s.append(NextPageTemplate("body"))
    s.append(PageBreak())

    s.append(P("Sumário", "H1"))
    for item in [
        "1. Visão geral",
        "2. Por que personalizado + domingo",
        "3. Fluxo sob demanda",
        "4. Script 1 — configurar filial(is)",
        "5. Script 2 — roda fechamento 2",
        "6. Controle: não fechar duas vezes no mesmo dia",
        "7. Relação com retenção",
        "8. O que guardar",
    ]:
        s.append(P(item, "TOCItem"))
    s.append(Spacer(1, 8))

    s.append(h1(1, "Visão geral"))
    s.append(P(
        "Em homologação, às vezes o solicitante pede para <b>fechar o extrato de uma filial específica</b> "
        "no mesmo dia (testar retenção, SP, boleto, EBS etc.)."
    ))
    s.append(callout(
        "A solução prática: dois scripts — um configura a(s) filial(is) para o dia de hoje; "
        "o outro executa o <b>roda fechamento 2</b>.",
        "rule",
    ))
    s.append(P(
        "Isso evita depender do job semanal “de verdade” e reduz impacto nos cenários "
        "que o time monta de segunda a sexta."
    ))

    s.append(h1(2, "Por que personalizado + domingo"))
    s.append(P(
        "O script base altera a parametrização das filiais para <b>personalizado</b> "
        "e joga a execução padrão para <b>domingo</b>."
    ))
    s.append(P("Motivo:"))
    s.extend(bullets([
        "o fechamento “normal” de segunda a sexta deixa de pegar essas filiais;",
        "outros testes/cenários do time não são impactados no meio da semana;",
        "só a filial que você marcar para SYSDATE entra no fechamento sob demanda.",
    ]))
    s.append(callout(
        "Domingo = “estacionamento”. SYSDATE = “fecha hoje”.",
        "info",
    ))

    s.append(h1(3, "Fluxo sob demanda"))
    s.append(diagram(
        "Solicitante informa a filial (ex.: 102)\n"
        "        │\n"
        "        ▼\n"
        "Script 1 — parametrização personalizada\n"
        "        │  coloca execução no SYSDATE\n"
        "        ▼\n"
        "Script 2 — roda fechamento 2\n"
        "        │\n"
        "        ├── emissão de boleto\n"
        "        ├── geração de SP\n"
        "        ├── envio ao EBS\n"
        "        └── demais rotinas do fechamento\n"
        "        │\n"
        "        ▼\n"
        "Conferir extrato / retenção / títulos"
    ))

    s.append(h1(4, "Script 1 — configurar filial(is)"))
    s.append(P("O que o script faz, em essência:"))
    s.extend(bullets([
        "altera a parametrização das filiais para <b>personalizado</b>;",
        "define o dia padrão de execução (ex.: domingo) para não conflitar com Mon–Sex;",
        "para a(s) filial(is) solicitada(s), grava a execução para <b>SYSDATE</b> (dia da semana de hoje).",
    ]))
    s.append(P("Exemplo da reunião: filial <b>102</b> configurada para execução de quinta-feira (número do dia da semana)."))
    s.append(callout(
        "Dá para informar <b>N filiais</b> de uma vez (lista no script). Configure todas para SYSDATE e depois rode o fechamento.",
        "info",
    ))

    s.append(h1(5, "Script 2 — roda fechamento 2"))
    s.append(P(
        "Rotina citada: <b>roda fechamento 2</b> (passada pelo Elso). "
        "Há trechos comentados que não precisam rodar; o importante é executar o conjunto necessário do fechamento."
    ))
    s.append(P("O fechamento não é só “fechar extrato”. Ele dispara várias funcionalidades:"))
    s.extend(bullets([
        "emissão de boleto;",
        "geração de SP;",
        "envio / integração com EBS;",
        "demais passos do fechamento do extrato.",
    ]))
    s.append(P("Ordem prática:"))
    s.append(diagram(
        "1. Script de configuração (filial → SYSDATE)\n"
        "2. Script / rotina roda fechamento 2"
    ))

    s.append(h1(6, "Controle: não fechar duas vezes no mesmo dia"))
    s.append(callout(
        "Se pedirem de novo a mesma filial no mesmo dia, <b>não execute de novo sem checar</b>. "
        "Fechar duas vezes bagunça o extrato.",
        "alert",
    ))
    s.append(P("Como controlar:"))
    s.append(diagram(
        "Consultar GEN_COTA_EXTRATO\n"
        "        │\n"
        "        ▼\n"
        "A filial tem data inicial = SYSDATE?\n"
        "   │                    │\n"
        "  SIM                  NÃO\n"
        "   │                    │\n"
        "   ▼                    ▼\n"
        "Não executar         Pode configurar\n"
        "de novo              e fechar"
    ))
    s.append(P(
        "Sugestão da reunião: antes do UPDATE, conferir o estado (select) — "
        "não sair alterando sem validar."
    ))
    s.append(simple_table(
        ["Situação", "Ação"],
        [
            ["Filial ainda no domingo / sem SYSDATE", "Configurar para hoje e fechar"],
            ["Filial já com data inicial = SYSDATE", "Não fechar de novo; só analisar"],
            ["Várias filiais no pedido", "Configurar a lista e fechar uma vez"],
            ["Pedido repetido no mesmo dia", "Checar GEN_COTA_EXTRATO antes"],
        ],
        first_cm=7.2,
    ))

    s.append(h1(7, "Relação com retenção"))
    s.append(P(
        "Esse procedimento é o mesmo tipo de preparação usada quando o time precisa "
        "testar retenção / fechamento em Homolog sem esperar o job da madrugada."
    ))
    s.append(P(
        "Complementa a apostila de <b>Retenção de Taxas</b>: lá está a regra de negócio; "
        "aqui está o “como forçar o fechamento de uma filial hoje”."
    ))

    s.append(h1(8, "O que guardar"))
    concepts = [
        ("1. Dois scripts", "Configurar filial(is) + roda fechamento 2."),
        ("2. Personalizado + domingo", "Tira as filiais do caminho Mon–Sex dos outros."),
        ("3. SYSDATE = fecha hoje", "Só a filial pedida entra no fechamento sob demanda."),
        ("4. Fechamento faz mais que fechar", "Boleto, SP, EBS e outras rotinas."),
        ("5. GEN_COTA_EXTRATO manda no controle", "Data inicial = SYSDATE → não executar de novo."),
    ]
    for title, body in concepts:
        s.append(P(title, "ConceptNum"))
        s.append(P(body, "BodyLeft"))

    s.append(Spacer(1, 8))
    s.append(hr())
    s.append(P("A frase que resume", "H2"))
    s.append(callout(
        "Para fechar uma filial sob demanda em Homolog: parametrize personalizado (as demais no domingo), "
        "marque a filial no SYSDATE, rode o <b>roda fechamento 2</b> e "
        "<b>nunca feche de novo no mesmo dia sem olhar a GEN_COTA_EXTRATO</b>.",
        "rule",
    ))
    return s


def main():
    out = "/workspace/Apostila-Fechamento-Sob-Demanda-Homolog.pdf"
    frame_cover = Frame(28 * mm, 40 * mm, PAGE_W - 46 * mm, PAGE_H - 80 * mm, id="cover")
    frame_body = Frame(MARGIN_L, MARGIN_B, CONTENT_W, PAGE_H - MARGIN_T - MARGIN_B, id="body")
    doc = BaseDocTemplate(
        out,
        pagesize=A4,
        title="Mini-apostila — Fechamento sob demanda em Homologação",
        author="Treinamento interno",
        subject="Scripts para parametrizar filial e rodar fechamento sem impactar Mon–Sex",
    )
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame_cover], onPage=draw_cover),
        PageTemplate(id="body", frames=[frame_body], onPage=draw_page),
    ])
    doc.build(build_story())
    print(out)


if __name__ == "__main__":
    main()
