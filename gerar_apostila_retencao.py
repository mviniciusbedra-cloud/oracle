#!/usr/bin/env python3
"""Gera a apostila de Retenção de Taxas em PDF."""

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
    canvas.drawString(28 * mm, 14 * mm, "Uso interno  ·  Treinamento técnico")
    canvas.drawRightString(PAGE_W - 18 * mm, 14 * mm, "Extrato de Comissão  ·  Retenção")
    canvas.restoreState()


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 1.4 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Inter", 7.5)
    canvas.drawString(MARGIN_L, PAGE_H - 8 * mm, "Apostila  ·  Processo de Retenção de Taxas")
    canvas.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 8 * mm, "Treinamento interno")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_L, 12 * mm, PAGE_W - MARGIN_R, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Inter", 8)
    canvas.drawString(MARGIN_L, 7 * mm, "Abate dívida com a comissão antes de pagar a loja")
    canvas.drawRightString(PAGE_W - MARGIN_R, 7 * mm, f"{doc.page}")
    canvas.restoreState()


def build_story():
    s = []
    s.append(Spacer(1, 48 * mm))
    s.append(Paragraph("APOSTILA DE TREINAMENTO", STYLES["CoverKicker"]))
    s.append(Paragraph("Processo de<br/>Retenção de Taxas", STYLES["CoverTitle"]))
    s.append(Spacer(1, 8))
    s.append(CoverBar(42 * mm, 3.2, GOLD))
    s.append(Spacer(1, 14))
    s.append(Paragraph(
        "Parametrização, extrato de comissão, abatimentos,<br/>"
        "integração EBS e arquivo KAB.",
        STYLES["CoverSub"],
    ))
    s.append(NextPageTemplate("body"))
    s.append(PageBreak())

    s.append(P("Sumário", "H1"))
    toc = [
        "1. Visão geral",
        "2. O que é o processo de retenção",
        "3. Onde começa a parametrização no CUR",
        "4. Tipos de fechamento do extrato",
        "5. Parametrização por filial (para testes)",
        "6. Liberação de programas — ligar / desligar",
        "7. Extrato: crédito, débito, SP e boleto",
        "8. Onde a retenção entra no extrato",
        "9. Exemplo de resultado no extrato",
        "10. OPF / OP Fax também entra",
        "11. Percentual 30% × 100% — onde está",
        "12. Tipos de movimento que forçam 100%",
        "13. Parametrização por tipo de pendência",
        "14. Objeto principal e job",
        "15. Versão antiga × versão nova",
        "16. Cursor de filiais elegíveis",
        "17. Configuração de juros",
        "18. Função de fechamento geral × personalizado",
        "19. Coração do processo: cursor de títulos",
        "20. Dois tipos de título no EBS",
        "21. Pré-cadastros obrigatórios no Sistur",
        "22. Um título, duas pendências, dois abatimentos",
        "23. Ordem de prioridade dos títulos",
        "24. Tabela de abatimentos e saldo do dia",
        "25. Quando a comissão não cobre nem os juros",
        "26. Vários abatimentos ao longo do tempo",
        "27. Integração com o EBS",
        "28. Arquivo KAB (comunicação com o banco)",
        "29. Confirmação do banco",
        "30. Consolidação antes de mandar ao banco",
        "31. Fluxo completo",
        "32. Principais objetos citados",
        "33. O que você precisa guardar",
    ]
    for item in toc:
        s.append(P(item, "TOCItem"))
    s.append(PageBreak())

    s.append(h1(1, "Visão geral"))
    s.append(P(
        "A reunião apresenta o novo processo de <b>retenção de taxas</b>: como parametrizar, "
        "ligar/desligar a funcionalidade, como o abatimento acontece no extrato da loja e quais "
        "objetos estão envolvidos (package, jobs, tabelas do Sistur/EBS e arquivo KAB)."
    ))
    s.append(P("A ideia central é:"))
    s.append(callout(
        "No fechamento do extrato da loja, se existir título em atraso, a CVC abate parte "
        "(ou toda) a comissão <b>antes</b> de pagar a loja.",
        "rule",
    ))
    s.append(P(
        "Sem retenção, a loja poderia receber comissão mesmo devendo boletos. "
        "Com retenção, a dívida é quitada (total ou parcial) usando a comissão."
    ))

    s.append(h1(2, "O que é o processo de retenção"))
    s.append(P("No momento do fechamento de uma loja, o processo:"))
    s.extend(bullets([
        "verifica títulos em atraso;",
        "verifica o valor da comissão disponível;",
        "verifica o que a loja está pendente;",
        "abate esses títulos antes do fechamento.",
    ]))
    s.append(P("Exemplo reforçado na reunião:"))
    s.extend(bullets([
        "extrato fecha e a loja teria R$ 1.000 a receber;",
        "a mesma loja deve R$ 5.000, R$ 6.000 ou R$ 15.000 em boletos;",
        "em vez de pagar a comissão “cheia”, o sistema retém e abate a dívida.",
    ]))

    s.append(h1(3, "Onde começa a parametrização no CUR"))
    s.append(P("Caminho apresentado:"))
    s.append(diagram("Caixa  →  Extrato de Comissão"))
    s.append(P("Existem dois níveis de parametrização de fechamento:"))
    s.extend(bullets([
        "<b>Parametrização geral</b> — vale para todas as filiais sem configuração personalizada;",
        "<b>Parametrização por filial</b> — personalizada para uma filial específica.",
    ]))

    s.append(h1(4, "Tipos de fechamento do extrato"))
    s.append(P("Hoje há três tipos:"))
    s.append(simple_table(
        ["Tipo", "Uso"],
        [
            ["Mensal", "Fechamento mensal"],
            ["Semanal", "Fechamento semanal"],
            ["Valor máximo", "Fecha quando atinge valor"],
        ],
    ))
    s.append(P("A configuração fica na tabela <b>GEN_COTA_EXTRATO</b>."))
    s.append(P("Na prática, a maioria (e o que o time vê em produção) é <b>semanal</b>."))
    s.append(callout(
        "Rotina típica: toda segunda-feira, <b>01:30</b> — processo de retenção; "
        "às <b>03:00</b> — rotina de fechamento.",
        "info",
    ))

    s.append(h1(5, "Parametrização por filial (para testes)"))
    s.append(P("Em homologação, para testar mais rápido, usa-se parametrização por filial."))
    s.append(P("Ao criar personalizada:"))
    s.extend(bullets([
        "indicar o tipo (ex.: semanal);",
        "indicar o dia de execução.",
    ]))
    s.append(P("Exemplo: filial 1275. Se o teste for na terça, a parametrização precisa estar como semanal + terça."))
    s.append(callout(
        "Se a filial não estiver no dia/tipo certo: não entra no processo de retenção e "
        "não entra no fechamento do extrato.",
        "alert",
    ))
    s.append(P("Essa parte já existia há bastante tempo e não mudou com a retenção nova."))

    s.append(h1(6, "Liberação de programas — ligar / desligar"))
    s.append(P("Além da cota/extrato, o processo de retenção depende da <b>liberação de programas</b>."))
    s.append(P("Foram criados dois programas:"))
    s.append(simple_table(
        ["Código", "Função"],
        [
            ["179", "Inclusão no processo de retenção"],
            ["181", "Exclusão do processo de retenção"],
        ],
    ))
    s.append(P("Regras:"))
    s.extend(bullets([
        "obrigatoriamente um desses precisa estar ligado (liberação automática) para a funcionalidade rodar;",
        "também é preciso cadastrar quais filiais participam;",
        "se a filial estiver só no <b>179</b> (inclusão) → executa;",
        "se estiver no <b>181</b> (exclusão) → não executa;",
        "se estiver nos <b>dois</b> → não executa.",
    ]))
    s.append(callout(
        "Mesmo com filial parametrizada na cota, se a liberação não estiver ligada, <b>nada funciona</b>.",
        "rule",
    ))

    s.append(h1(7, "Extrato: crédito, débito, SP e boleto"))
    s.append(P("Tela citada para consulta: Extrato → consulta por filial."))
    s.append(P("Há parametrização geral, parametrização por filial e o extrato em si."))
    s.append(P("O extrato aberto funciona como extrato de banco:"))
    s.extend(bullets([
        "qualquer venda gera crédito da loja naquele extrato;",
        "qualquer débito (fraude, pendência etc.) entra no mesmo extrato;",
        "no fechamento, soma crédito − débito.",
    ]))
    s.append(diagram(
        "Saldo a crédito  →  gera SP e paga a filial\n"
        "Saldo a débito   →  gera boleto, integra no EBS e cobra a loja"
    ))

    s.append(h1(8, "Onde a retenção entra no extrato"))
    s.append(diagram(
        "Loja vende / gera comissão\n"
        "        │\n"
        "        ▼\n"
        "Extrato aberto (créditos e débitos)\n"
        "        │\n"
        "        ▼\n"
        "Existe boleto em atraso no EBS?\n"
        "        │\n"
        "        ▼\n"
        "Processo de retenção\n"
        "        │\n"
        "        ├── usa 100% ou 30% da comissão\n"
        "        ├── abate título (+ juros, se couber)\n"
        "        └── sobra crédito? → SP no fechamento"
    ))
    s.append(callout(
        "A grande alteração recente: percentual de retenção <b>por tipo de pendência</b> "
        "(não mais só regra antiga por data de corte).",
        "info",
    ))

    s.append(h1(9, "Exemplo de resultado no extrato"))
    s.append(P("No exemplo apresentado, após rodar retenção na filial:"))
    s.extend(bullets([
        "aparecem linhas de títulos em aberto (título do EBS);",
        "título com emissão 01/03, vencimento 05/03, em atraso;",
        "valor original ≈ R$ 6.686,80;",
        "com parametrização de 100% da comissão, o débito foi quitado;",
        "já integrado no EBS, saldo a pagar zerado;",
        "juros calculados ≈ R$ 238,50 (107 dias de atraso, de 05/03 até 26/06);",
        "ainda sobrou crédito ≈ R$ 292,00 para a loja.",
    ]))
    s.append(P("Quando rodar o job de fechamento (diário às 03:00), esse crédito sobrante gera SP."))

    s.append(h1(10, "OPF / OP Fax também entra"))
    s.append(P("Dúvida da reunião: OPF entra? <b>Sim.</b>"))
    s.append(P("No caso de OPF/OP Fax, usa-se <b>100%</b> da comissão."))
    s.append(P("Exemplo: dívida R$ 300; comissão R$ 500 → usa até R$ 500 para quitar; se der, quita total; senão, parcial."))
    s.append(P("OPF entra como tipo de pendência na parametrização."))

    s.append(h1(11, "Percentual 30% × 100% — onde está"))
    s.append(P("O percentual por tipo de pendência está parametrizado em <b>tabela</b>."))
    s.append(P("Não há tela para alterar (pelo menos na apresentação): altera-se na tabela."))
    s.append(callout(
        "A parametrização é <b>global por tipo de pendência</b>, não por filial. "
        "Se a filial tem aquele tipo de pendência, segue o percentual cadastrado para o tipo.",
        "rule",
    ))

    s.append(h1(12, "Tipos de movimento que forçam 100%"))
    s.append(P(
        "Além da tabela por tipo de pendência, há IDs de movimento do extrato que levam a usar "
        "100% da comissão quando existem no extrato."
    ))
    s.append(simple_table(
        ["ID movimento", "Significado"],
        [
            ["1", "Baixa de recibo"],
            ["3", "OP Fax / OPF"],
            ["11", "Ajuste"],
            ["34", "(também citado na lista de movimentos)"],
        ],
        first_cm=3.8,
    ))
    s.append(P("Esses IDs estão ligados a Caixa Extrato Identificação / Caixa Extrato Diária."))

    s.append(h1(13, "Parametrização por tipo de pendência"))
    s.append(P("Tabela/conceito: retenção por tipo de pendência. Exemplos citados:"))
    s.extend(bullets([
        "faturamento aéreo;",
        "fraude;",
        "utilização de saldo de ficha para terceiros;",
        "demais pendências possíveis no dashboard de pendências.",
    ]))
    s.append(P("Para cada tipo dá para configurar: <b>100%</b> ou <b>30%</b> da comissão."))
    s.append(P(
        "Pendências da filial ficam em <b>FIM_DEBITO</b> / <b>FIM_DEBITO_FILIAL</b> "
        "(débito por filial + tipo de pendência + percentual aplicável)."
    ))

    s.append(h1(14, "Objeto principal e job"))
    s.append(P("Package citada: <b>PKG_FIM_DEBITO_UTIL</b>."))
    s.append(P("Job noturno: <b>PRC_PROCESSO_NOTURNO</b> — ~01:30."))
    s.append(P("Pode rodar para uma filial específica, mas em produção está agendado para todas."))
    s.append(P("Dentro do processo, conforme liberação 179/181:"))
    s.extend(bullets([
        "verifica se 179 ou 181 está habilitado;",
        "se sim, invoca <b>PRC_TITULOS_EM_ATRASO_PEND</b>.",
    ]))

    s.append(h1(15, "Versão antiga × versão nova"))
    s.append(P("A mudança foi grande. A versão antiga ficou inalterada."))
    s.append(h2("Regra antiga (data de corte)"))
    s.extend(bullets([
        "acima da data de corte → 100%;",
        "abaixo → 30%.",
    ]))
    s.append(h2("Nova procedure"))
    s.append(simple_table(
        ["Procedure", "Função"],
        [
            ["PRC_TITULOS_EM_ATRASO", "Versão antiga (data de corte)"],
            ["PRC_TITULOS_EM_ATRASO_PEND", "Versão nova (por pendência)"],
        ],
        first_cm=6.2,
    ))

    s.append(h1(16, "Cursor de filiais elegíveis"))
    s.append(P("O processo abre cursor das filiais elegíveis à retenção. Usa <b>GEN_COTA_EXTRATO</b>:"))
    s.extend(bullets([
        "CD_COTA / tipo de extrato;",
        "extrato de agência × extrato de filial.",
    ]))
    s.append(P("Diferença resumida:"))
    s.append(simple_table(
        ["Tipo", "Comissão"],
        [
            ["Filial CVC", "Comissão única direto para a filial"],
            ["Agência", "Sempre debaixo de uma filial; comissão dividida (agência + filial atendente)"],
        ],
    ))
    s.append(P("O cursor valida as parametrizações já vistas: liberação de programas, cota, tipo de fechamento etc."))

    s.append(h1(17, "Configuração de juros"))
    s.append(P("Há tabelas de configuração com o percentual/taxa de juros."))
    s.append(P("Função de cálculo de juros:"))
    s.extend(bullets([
        "recebe valor do boleto;",
        "data de vencimento;",
        "taxa;",
        "calcula o juros do atraso.",
    ]))

    s.append(h1(18, "Função de fechamento geral × personalizado"))
    s.append(P("Existe função pronta (sem manutenção frequente) que resolve:"))
    s.extend(bullets([
        "fechamento default ou personalizado;",
        "tipo: diário, semanal, mensal, por valor;",
        "se não houver personalização, cai na geral.",
    ]))

    s.append(h1(19, "Coração do processo: cursor de títulos"))
    s.append(P(
        "O cursor de títulos busca títulos em atraso no <b>EBS</b>, com regras/características específicas. "
        "Dúvidas de modelo EBS → Michael. Há log para todo o processo."
    ))

    s.append(h1(20, "Dois tipos de título no EBS"))
    s.append(simple_table(
        ["Tipo", "Regra de %"],
        [
            ["Títulos antigos nascidos direto no EBS (sem param. no Sistur)", "Sempre 30%"],
            ["Títulos novos / com origem Sistur", "Segue tipo de pendência / movimentos (30% ou 100%)"],
        ],
        first_cm=8.5,
    ))
    s.append(P("Títulos “só EBS” são legado: não nascem mais assim."))
    s.append(P(
        "No cursor há UNION para esses casos, com tipos de transação fixos e "
        "PC_UTIL_COMISSAO = 30%. Para os demais:"
    ))
    s.extend(bullets([
        "consulta tabelas do extrato;",
        "verifica se existe débito / ID movimento 1, 3, 11, 34;",
        "se existir, usa 100%;",
        "também identifica o extrato de origem do título (pode estar pagando no extrato B um título nascido no extrato A).",
    ]))

    s.append(h1(21, "Pré-cadastros obrigatórios no Sistur"))
    s.append(P("Para a retenção funcionar, precisam estar parametrizados no Sistur:"))
    s.append(h2("Operação / código de transação"))
    s.append(P("Tabela citada: <b>FIM_MOD_EBS_OPERACAO</b>."))
    s.append(P("Títulos que nascem no CUR usam código de transação <b>5710</b>."))
    s.append(h2("Método de recebimento"))
    s.append(P("Pré-cadastro também necessário. Na prática do time: quase nunca inclui/remove esses cadastros; já estável."))

    s.append(h1(22, "Um título, duas pendências, dois abatimentos"))
    s.append(callout(
        "Um mesmo título pode ter mais de um tipo de pendência e sofrer <b>dois abatimentos</b>.",
        "rule",
    ))
    s.append(simple_table(
        ["Pendência", "%"],
        [
            ["Faturamento aéreo / venda não processada", "30%"],
            ["Fraude", "100%"],
            ["Uso de saldo de ficha para terceiros", "100%"],
        ],
        first_cm=8.5,
    ))
    s.append(P(
        "Hoje só existem dois percentuais (100 e 30), então no máximo dois abatimentos por título: "
        "primeiro usa 100% da fatia correspondente; depois, se sobrar comissão, usa 30% da outra fatia."
    ))
    s.append(P(
        "Antes: um título sofria só um abatimento (limitação do arquivo KAB). "
        "Agora: pode quebrar e abater em duas regras."
    ))

    s.append(h1(23, "Ordem de prioridade dos títulos"))
    s.append(P("Mudou também. Ordem:"))
    s.append(diagram(
        "1. Títulos classificados com 100%\n"
        "        │\n"
        "        ▼\n"
        "2. Dentro disso, o mais antigo\n"
        "        │\n"
        "        ▼\n"
        "3. Depois os de 30% (também pelo mais antigo)"
    ))
    s.append(P("Exemplo:"))
    s.extend(bullets([
        "comissão R$ 1.000; título R$ 1.200 com 100% → usa R$ 1.000, deixa R$ 200 para o próximo fechamento;",
        "quebra no mesmo título: R$ 700 (100%) + R$ 300 (30%); comissão R$ 1.000 → paga R$ 700; sobram R$ 300; desses só pode usar 30% (= R$ 90).",
    ]))

    s.append(h1(24, "Tabela de abatimentos e saldo do dia"))
    s.append(P("Cada abatimento grava:"))
    s.extend(bullets([
        "valor abatido;",
        "juros calculados;",
        "valor pendente a abater;",
        "saldo em aberto no EBS;",
        "comissão disponível no momento;",
        "percentual utilizado;",
        "se quitou total ou parcial;",
        "valor disponível para o próximo abatimento (quando há quebra).",
    ]))
    s.append(callout(
        "A busca de percentual/saldo disponível considera o <b>dia do abatimento</b>. "
        "No dia seguinte o EBS já está atualizado.",
        "info",
    ))

    s.append(h1(25, "Quando a comissão não cobre nem os juros"))
    s.append(P("Cenário: comissão menor que o juros calculado."))
    s.append(callout(
        "Não cobra juros (“CVC é mãe”). Zera o juros naquele abatimento e usa a comissão só no principal da dívida.",
        "rule",
    ))
    s.append(P("No extrato: aparece título em aberto / débito do título; <b>não</b> aparece linha de juros; também não envia juros efetivos ao EBS nesse caso."))

    s.append(h1(26, "Vários abatimentos ao longo do tempo"))
    s.append(P("Um título pode ser fatiado em vários fechamentos (ex.: R$ 100 por semana)."))
    s.append(P("A cada novo abatimento, o processo verifica no EBS se já houve aplicação/ajuste anterior."))
    s.extend(bullets([
        "se houve → a data de vencimento efetiva muda; usa a data da última aplicação como nova base para juros;",
        "se não localizar → usa a data de vencimento original do título.",
    ]))
    s.append(P("Isso impacta direto o cálculo de juros."))

    s.append(h1(27, "Integração com o EBS"))
    s.append(P("Há tabela(s) de integração alimentadas a cada ajuste. No envio:"))
    s.extend(bullets([
        "abatimento do título → ajuste <b>negativo</b> no EBS (reduz saldo);",
        "juros → envia lançamento positivo e negativo (zera efeito no saldo; fica só demonstrativo);",
        "o que realmente reduz saldo no EBS é o valor de fato abatido do boleto (encontro de franquias).",
    ]))
    s.append(P("Job de integração (homolog e produção citados): periodicidade ~ a cada <b>2 horas</b>."))
    s.append(P(
        "Como a retenção roda 1x/dia (ou 1x/semana no ciclo do extrato), o controle de saldo não costuma conflitar. "
        "Na próxima execução, o saldo do EBS já está atualizado."
    ))

    s.append(h1(28, "Arquivo KAB (comunicação com o banco)"))
    s.append(P("Depois dos abatimentos, o processo consolida e gera instruções no arquivo KAB."))
    s.append(simple_table(
        ["Instrução", "Significado"],
        [
            ["02", "Pedido de baixa — pagamento integral"],
            ["04", "Concessão de abatimento — parcial"],
            ["06", "Alteração de vencimento"],
        ],
    ))
    s.append(P("Regras:"))
    s.extend(bullets([
        "pagamento integral → instrução 02;",
        "abatimento parcial → 04;",
        "sempre que envia 04, <b>obrigatoriamente</b> envia 06 (nova data de vencimento).",
    ]))
    s.append(P("O arquivo vai para FTP → banco → retorno de aceitação por instrução."))

    s.append(h1(29, "Confirmação do banco"))
    s.append(P("Tabela de retorno / confirmação (ST_CONFIRMACAO_BANCO etc.). Quando o banco aceita:"))
    s.extend(bullets([
        "pagamento integral → boleto zerado na consulta;",
        "parcial → desconto aplicado + nova data de vencimento.",
    ]))
    s.append(P(
        "Em homologação muitas vezes não há retorno real do banco; em produção o ODI "
        "(João Paulo citado) carimba a confirmação."
    ))
    s.append(P(
        "Limitação: por tabela, envia-se tipicamente 02 e 04; a 06 (vencimento) foi para tabela separada "
        "<b>FIM_SANTANDER_VENCIMENTO</b>."
    ))

    s.append(h1(30, "Consolidação antes de mandar ao banco"))
    s.append(P("Como um título pode ter vários abatimentos no mesmo ciclo, ao final:"))
    s.extend(bullets([
        "soma todos os abatimentos daquele boleto/parcela;",
        "envia um único registro consolidado ao KAB.",
    ]))
    s.append(P(
        "Se o boleto/parcela já existe na tabela de envio: cai em exception de índice único; "
        "aí atualiza somando o valor do novo abatimento."
    ))

    s.append(h1(31, "Fluxo completo"))
    s.append(diagram(
        "                 FECHAMENTO / JOB 01:30\n"
        "                         │\n"
        "                         ▼\n"
        "              Liberação 179/181 ligada?\n"
        "                         │\n"
        "            ┌────────────┴────────────┐\n"
        "            NÃO                      SIM\n"
        "            │                         │\n"
        "            ▼                         ▼\n"
        "         Não executa         Filial elegível (cota/dia)\n"
        "                                      │\n"
        "                                      ▼\n"
        "                            Cursor títulos EBS\n"
        "                                      │\n"
        "                    ┌─────────────────┴─────────────────┐\n"
        "                    │                                   │\n"
        "              Título legado EBS                   Título Sistur\n"
        "                    │                                   │\n"
        "                    ▼                                   ▼\n"
        "                  30%                         % por pendência\n"
        "                                      │\n"
        "                                      ▼\n"
        "                         Prioridade: 100% → depois 30%\n"
        "                                      │\n"
        "                                      ▼\n"
        "                         Calcula juros / abate\n"
        "                         (comissão < juros → sem juros)\n"
        "                                      │\n"
        "                                      ▼\n"
        "                         Grava abatimento + integração EBS\n"
        "                                      │\n"
        "                                      ▼\n"
        "                         Consolida e gera KAB (02 / 04+06)\n"
        "                                      │\n"
        "                                      ▼\n"
        "                         Fechamento 03:00 → SP do crédito"
    ))

    s.append(h1(32, "Principais objetos citados"))
    s.append(simple_table(
        ["Objeto", "Função"],
        [
            ["GEN_COTA_EXTRATO", "Tipo de fechamento geral ou por filial"],
            ["Liberação 179 / 181", "Inclusão / exclusão da retenção"],
            ["PKG_FIM_DEBITO_UTIL", "Package principal"],
            ["PRC_PROCESSO_NOTURNO", "Job ~01:30"],
            ["PRC_TITULOS_EM_ATRASO", "Versão antiga (data de corte)"],
            ["PRC_TITULOS_EM_ATRASO_PEND", "Versão nova (por pendência)"],
            ["FIM_DEBITO / FIM_DEBITO_FILIAL", "Débitos/pendências da filial"],
            ["Tabela % por tipo de pendência", "30% ou 100% (global por tipo)"],
            ["Caixa Extrato Identificação", "Movimentos 1, 3, 11, 34 etc."],
            ["FIM_MOD_EBS_OPERACAO", "Operações/transações EBS (ex.: 5710)"],
            ["Método de recebimento", "Pré-cadastro Sistur"],
            ["Tabelas de log / abatimento", "Histórico do que foi retido"],
            ["Tabelas de integração EBS", "Ajustes e juros enviados"],
            ["Arquivo KAB + FTP", "Instruções 02/04/06 ao banco"],
            ["FIM_SANTANDER_VENCIMENTO", "Instrução 06 (nova data)"],
        ],
        first_cm=6.8,
    ))

    s.append(h1(33, "O que você precisa guardar"))
    concepts = [
        ("1. Retenção = abater dívida com a comissão no fechamento",
         "Evita pagar loja que está em atraso."),
        ("2. Duas camadas de parametrização de execução",
         "Cota/extrato (geral ou filial + dia) e liberação 179/181."),
        ("3. 179 executa, 181 não; nos dois, não executa",
         "E a liberação automática precisa estar ligada."),
        ("4. % agora é por tipo de pendência",
         "Tabela global; OPF/fraude etc. podem ser 100%; outras 30%."),
        ("5. Movimentos 1, 3, 11 (e 34) no extrato puxam 100%",
         "Baixa recibo, OPF, ajuste etc."),
        ("6. Package + job 01:30; fechamento 03:00",
         "PRC_TITULOS_EM_ATRASO_PEND é a nova."),
        ("7. Título pode virar dois abatimentos",
         "Fatias 100% e 30% no mesmo boleto."),
        ("8. Ordem: 100% primeiro, depois mais antigo",
         "Depois os de 30%."),
        ("9. Comissão < juros → não cobra juros",
         "Abate só o principal possível."),
        ("10. EBS recebe ajuste; banco recebe KAB",
         "Integral = 02; parcial = 04 + 06. Integração ~2/2h; confirmação do banco atualiza o boleto."),
    ]
    for title, body in concepts:
        s.append(P(title, "ConceptNum"))
        s.append(P(body, "BodyLeft"))

    s.append(Spacer(1, 8))
    s.append(hr())
    s.append(P("A frase que resume a reunião", "H2"))
    s.append(callout(
        "Retenção de taxas é parametrizar quem participa (cota + 179/181), achar título em atraso no EBS, "
        "aplicar 100% ou 30% conforme o tipo de pendência, abater na comissão do extrato (com juros quando couber), "
        "integrar no EBS e avisar o banco via KAB — "
        "<b>para a loja não receber comissão em cima de dívida aberta.</b>",
        "rule",
    ))
    return s


def main():
    out = "/workspace/Apostila-Processo-de-Retencao-de-Taxas.pdf"
    frame_cover = Frame(28 * mm, 40 * mm, PAGE_W - 46 * mm, PAGE_H - 80 * mm, id="cover")
    frame_body = Frame(MARGIN_L, MARGIN_B, CONTENT_W, PAGE_H - MARGIN_T - MARGIN_B, id="body")
    doc = BaseDocTemplate(
        out,
        pagesize=A4,
        title="Apostila — Processo de Retenção de Taxas",
        author="Treinamento interno",
        subject="Parametrização, extrato, abatimentos, EBS e arquivo KAB",
    )
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame_cover], onPage=draw_cover),
        PageTemplate(id="body", frames=[frame_body], onPage=draw_page),
    ])
    doc.build(build_story())
    print(out)


if __name__ == "__main__":
    main()
