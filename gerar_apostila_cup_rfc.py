#!/usr/bin/env python3
"""Gera a apostila CUP/RFC/Workflow em PDF."""

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
    s.add(ParagraphStyle("CoverTitle", fontName="Inter-Bold", fontSize=26, leading=32,
                         textColor=white, alignment=TA_LEFT, spaceAfter=10))
    s.add(ParagraphStyle("CoverSub", fontName="Inter", fontSize=12, leading=17,
                         textColor=HexColor("#D7E2EE"), alignment=TA_LEFT))
    s.add(ParagraphStyle("H1", fontName="Inter-Bold", fontSize=14.5, leading=19,
                         textColor=NAVY, spaceBefore=16, spaceAfter=8))
    s.add(ParagraphStyle("H2", fontName="Inter-Semi", fontSize=12, leading=16,
                         textColor=TEAL, spaceBefore=12, spaceAfter=6))
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


def h2(title):
    return P(title, "H2")


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


def simple_table(headers, rows, first_cm=3.8):
    head = [Paragraph(h, STYLES["TableHead"]) for h in headers]
    data = [head] + [[Paragraph(str(c), STYLES["TableCell"]) for c in row] for row in rows]
    if len(headers) == 2:
        widths = [first_cm * cm, CONTENT_W - first_cm * cm]
    else:
        col_w = CONTENT_W / len(headers)
        widths = [col_w] * len(headers)
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
    canvas.drawString(28 * mm, 14 * mm, "Uso interno  ·  Treinamento técnico")
    canvas.drawRightString(PAGE_W - 18 * mm, 14 * mm, "CUP  ·  RFC  ·  Sistur")
    canvas.restoreState()


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 1.4 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Inter", 7.5)
    canvas.drawString(MARGIN_L, PAGE_H - 8 * mm, "Apostila  ·  CUP, RFC e Workflow de Publicação")
    canvas.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 8 * mm, "Treinamento interno")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_L, 12 * mm, PAGE_W - MARGIN_R, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Inter", 8)
    canvas.drawString(MARGIN_L, 7 * mm, "Sem CUP + RFC no fluxo certo, a mudança não chega em produção")
    canvas.drawRightString(PAGE_W - MARGIN_R, 7 * mm, f"{doc.page}")
    canvas.restoreState()


def build_story():
    s = []
    s.append(Spacer(1, 45 * mm))
    s.append(Paragraph("APOSTILA DE TREINAMENTO", STYLES["CoverKicker"]))
    s.append(Paragraph("CUP, RFC e<br/>Workflow de Publicação", STYLES["CoverTitle"]))
    s.append(Spacer(1, 8))
    s.append(CoverBar(42 * mm, 3.2, GOLD))
    s.append(Spacer(1, 14))
    s.append(Paragraph(
        "Ambientes, package, scripts, CCB,<br/>"
        "menu, permissões e boas práticas no Sistur.",
        STYLES["CoverSub"],
    ))
    s.append(NextPageTemplate("body"))
    s.append(PageBreak())

    s.append(P("Sumário", "H1"))
    for item in [
        "1. Visão geral",
        "2. Base de conhecimento e wiki",
        "3. Welcome CVC",
        "4. Janelas e CCB",
        "5. De onde vem a demanda",
        "6. Ferramenta e ambientes de banco",
        "7. Ambientes no Sistur (URL)",
        "8. Por que existe o ambiente TI",
        "9. Hoval",
        "10. Packages no Sistur",
        "11. Como achar a package a partir do menu",
        "12. Bloqueio de package (controle de versão)",
        "13. Sempre partir de produção (merge)",
        "14. CUP — o que é e onde abre",
        "15. Regras da CUP",
        "16. Script antes × script depois",
        "17. Padrão de modelo de dados",
        "18. Owner CUR e execução no SQL*Plus",
        "19. Rollback da CUP",
        "20. Fluxo da CUP (fases)",
        "21. Separar CUP de estrutura e de package",
        "22. RFC — o que é e onde cria",
        "23. Campos principais da RFC",
        "24. Validação na janela (Sim/Não)",
        "25. Evidências",
        "26. Fluxo da RFC",
        "27. Rod Script",
        "28. Desenvolvimento de tela: IE × Chrome",
        "29. Incluir item novo no menu",
        "30. Item de menu em produção",
        "31. Chave de permissão × chave de controle",
        "32. Apontamento de horas",
        "33. Fluxo mental completo",
        "34. Principais caminhos / objetos",
        "35. Contatos / papéis citados",
        "36. O que você precisa guardar",
    ]:
        s.append(P(item, "TOCItem"))
    s.append(PageBreak())

    s.append(h1(1, "Visão geral"))
    s.append(P("A reunião tem duas partes:"))
    s.extend(bullets([
        "<b>Ana Paula</b> (coordenação Backoffice/Finanças/CSC) apresenta a base de conhecimento, wiki e o Welcome CVC;",
        "<b>Sérgio</b> (9 anos de CVC) explica o fluxo técnico do dia a dia: ambientes, package, CUP, RFC, rollback, Rod Script, menu e permissões.",
    ]))
    s.append(callout(
        "Desenvolver em DEV não basta. Sem <b>CUP + RFC</b> no fluxo certo, a mudança não chega em produção.",
        "rule",
    ))

    s.append(h1(2, "Base de conhecimento e wiki"))
    s.append(P("Existe uma base de conhecimento no Backoffice (Teams/arquivos). Vale estudar cedo. Materiais citados:"))
    s.extend(bullets([
        "guia do desenvolvedor (vídeo que reforça o que o Sérgio mostra);",
        "padrão de arquitetura;",
        "jobs em produção;",
        "lançamento de horas;",
        "terminologia do turismo;",
        "Welcome CVC;",
        "wiki com janelas, fluxo RFC, fases CUP/RFC, plantão, férias, links e dicas.",
    ]))
    s.append(callout(
        "A wiki é viva. Dicas preciosas (ex.: Miriam) valem ouro — detalhes bobos como a <b>barra no fim do script</b> derrubam aplicação.",
        "info",
    ))

    s.append(h1(3, "Welcome CVC"))
    s.append(P(
        "O Welcome aterrissa o contexto CVC: onde o time está inserido e como o desenvolvimento atua. "
        "Foi combinado marcar o Welcome com o time."
    ))
    s.append(P("Para quem acompanha (coordenação), ajuda a:"))
    s.extend(bullets([
        "saber em que fase a RFC está;",
        "acompanhar validação técnica, CCB e aprovação de negócio;",
        "cobrar no horário certo.",
    ]))

    s.append(h1(4, "Janelas e CCB"))
    s.append(P("Pontos citados:"))
    s.extend(bullets([
        "avaliação/validações no fluxo;",
        "entre ~12h e 14h entra o <b>CCB</b> (comitê de mudança);",
        "no CCB defende-se a mudança para subir;",
        "precisa alinhamento prévio com o negócio;",
        "às vezes a aprovação de negócio ainda vai por e-mail / depois pelo Gira.",
    ]))

    s.append(h1(5, "De onde vem a demanda"))
    s.append(P("A demanda chega via PO, coordenador, gerência ou às vezes a própria Kátia."))
    s.append(P(
        "Primeiro passo do Dev: identificar qual programa/package mexer. "
        "Se a funcionalidade não trouxer o caminho: cobrar."
    ))

    s.append(h1(6, "Ferramenta e ambientes de banco"))
    s.append(P("Ferramenta principal: <b>PL/SQL Developer</b>."))
    s.append(simple_table(
        ["Ambiente", "Papel"],
        [
            ["DEV", "Único com acesso livre para desenvolver/compilar o que estiver liberado"],
            ["TI", "Primeiro ambiente do caminho de promoção"],
            ["HOMOLOG", "Homologação / evidência com usuário"],
            ["PROD", "Produção"],
        ],
    ))

    s.append(h1(7, "Ambientes no Sistur (URL)"))
    s.append(simple_table(
        ["URL / ambiente", "Significado"],
        [
            ["cur", "Produção"],
            ["cur-hom (ex.)", "Homologação"],
            ["cur-ti", "TI"],
            ["cur-dev", "DEV"],
        ],
        first_cm=4.2,
    ))
    s.append(P("Produção é só <b>cur</b>. Nos outros, depois do cur vêm letras indicando o ambiente. No dia a dia usa-se mais DEV e Homolog."))

    s.append(h1(8, "Por que existe o ambiente TI"))
    s.append(P("TI nasceu porque Homolog quebrava demais quando se ia direto de DEV → Homolog."))
    s.append(diagram("DEV  →  TI  →  Homolog  →  (Hoval)  →  Produção"))
    s.append(P("Se quebrar em TI, corrige, devolve a CUP, ajusta e avança de novo."))

    s.append(h1(9, "Hoval"))
    s.append(P("Antes de produção, o DBA aplica em <b>Hoval</b> — homologação da produção. O time Dev normalmente não tem acesso."))
    s.append(callout(
        "Se der erro em Hoval, tende a dar erro em PROD. Pode passar em Homolog e falhar em Hoval: "
        "Homolog pode ter “sujeira”. Refresh Homolog ← PROD acontece poucas vezes ao ano (~2x).",
        "alert",
    ))

    s.append(h1(10, "Packages no Sistur"))
    s.append(P(
        "A maior parte do sistema é package. Poucas functions/procedures isoladas. "
        "Uma package concentra um assunto (tela, background, suporte, rotinas noturnas). "
        "Jobs noturnos chamam procedures dentro das packages."
    ))

    s.append(h1(11, "Como achar a package a partir do menu"))
    s.append(P("Exemplo: Caixa → Extrato de Comissão."))
    s.append(diagram(
        "Sistemas → Controle de acesso de usuários\n"
        "  → Acesso de usuários → buscar módulos\n"
        "  → Caixa → Extrato de Comissão"
    ))
    s.append(P("No item aparece: descrição do menu, package executada (ex.: PKG_GEN_EXTRATO_COMISSAO) e procedure inicial (ex.: PRC_MENU)."))
    s.append(callout("Anote: <b>Controle de acesso de usuários</b> é caminho importante.", "info"))

    s.append(h1(12, "Bloqueio de package (controle de versão)"))
    s.append(P("Em DEV, só um Dev pode “deter” a package para compilar."))
    s.append(P("Consulta no Sistur de produção: <b>Controle de versão</b> — mostra situação (SPEC/BODY) e com quem está."))
    s.append(P("Se estiver com outro Dev:"))
    s.extend(bullets([
        "falar com ele para liberar;",
        "se não puder, alinhar com analista/coordenador;",
        "opção: trabalhar em cópia.",
    ]))

    s.append(h1(13, "Sempre partir de produção (merge)"))
    s.append(callout(
        "Sempre fazer merge DEV × PROD, ou pegar a versão de PROD, jogar em DEV e mexer nela.",
        "rule",
    ))
    s.append(P("Cuidado crítico ao colar em DEV:"))
    s.extend(bullets([
        "a versão de PROD vem com owner <b>CUR.</b>;",
        "precisa <b>remover o CUR.</b> ao criar/compilar em DEV;",
        "senão cria objeto errado.",
    ]))

    s.append(h1(14, "CUP — o que é e onde abre"))
    s.append(P("CUP = documento/pacote para avançar objetos (package, script etc.) no workflow até produção."))
    s.append(diagram("Sistemas → Gerenciamento → Painel geral → Workflow"))
    s.append(callout(
        "Permissão de workflow de CUP <b>não vem automática</b> com o login. "
        "Coordenador pede por e-mail (ex.: Julian / Jabur), passando o login dos Devs. Pedir cedo.",
        "alert",
    ))

    s.append(h1(15, "Regras da CUP"))
    s.extend(bullets([
        "toda CUP começa como fluxo de <b>Homologação</b>;",
        "campos: motivo, descrição, objetos (SPEC e BODY), scripts;",
        "uma package <b>não pode</b> estar em duas CUPs ao mesmo tempo;",
        "se outro Dev precisa dela: editar a CUP, remover o objeto, gravar.",
    ]))

    s.append(h1(16, "Script antes × script depois"))
    s.append(P("Ordem de aplicação da CUP:"))
    s.append(diagram("1. Script antes  →  2. Package  →  3. Script depois"))
    s.append(P(
        "Exemplo: criar tabela + popular + subir package → script antes = CREATE; "
        "package = SPEC+BODY; script depois = INSERT/popular."
    ))
    s.append(P("Limite citado: ~30.000 caracteres por área. Script grande → dividir. Se inverter a ordem, a CUP volta."))

    s.append(h1(17, "Padrão de modelo de dados"))
    s.append(P("Toda tabela/coluna precisa obedecer o padrão de estrutura de dados (documento no Teams): colunas, índices, FKs, checks, temporárias, nomes."))
    s.append(P("Se estiver fora do padrão, a CUP volta na etapa de modelo de dados."))

    s.append(h1(18, "Owner CUR e execução no SQL*Plus"))
    s.append(P("O DBA extrai o script e aplica. Execução é no SQL*Plus (<font face='JetBrains'>@script.sql</font>), muitas vezes como SYSTEM."))
    s.append(callout(
        "Sempre qualificar com owner (<b>CUR.tabela</b>). Não esquecer <b>COMMIT</b> e a barra <b>/</b> no fim do bloco. "
        "Barra mal posicionada também quebra. Sem commit, executa e não efetiva.",
        "rule",
    ))

    s.append(h1(19, "Rollback da CUP"))
    s.append(P("CUP exige script de rollback. Não colocar só um ponto."))
    s.append(P("Exemplo: subiu INSERT → rollback = DELETE correspondente (+ commit + barra)."))
    s.append(P("Na RFC, o plano de rollback aponta para o rollback da CUP (e recompilar package anterior se houver backup)."))

    s.append(h1(20, "Fluxo da CUP (fases)"))
    s.append(diagram(
        "Solicitação\n"
        "    │\n"
        "    ▼\n"
        "(se tem script) Aprovação de modelo de dados\n"
        "    │\n"
        "    ▼\n"
        "Implantação / Homologação  →  TI, depois Homolog\n"
        "    │\n"
        "    ▼\n"
        "CUP finalizada em Homolog\n"
        "    │\n"
        "    ▼\n"
        "Mudar CUP para Produção + avançar fase\n"
        "    │\n"
        "    ▼\n"
        "Validação DBA / aplicação em PROD"
    ))
    s.append(P("Para reaplicar: voltar CUP para Solicitação → ajustar → avançar de novo. Package pura anda mais rápido (não para em modelo de dados)."))

    s.append(h1(21, "Separar CUP de estrutura e de package"))
    s.append(callout(
        "Boa prática: <b>CUP 1 = só modelo de dados/scripts</b> e <b>CUP 2 = só package</b>. "
        "No vai-e-vem de Homolog, trabalhe só com a de package. Antes de PROD, coloque as duas de novo na RFC.",
        "rule",
    ))
    s.append(P("Controle pessoal: planilha de acompanhamento (Gira, projeto, RFC, CUPs)."))

    s.append(h1(22, "RFC — o que é e onde cria"))
    s.append(P("RFC = Gestão de Mudança (sistêmica), criada no Gira."))
    s.append(P(
        "Na época da reunião: último dia do Gira antigo; na segunda começaria o novo. "
        "Conceito permanece; tela pode mudar."
    ))

    s.append(h1(23, "Campos principais da RFC"))
    s.append(simple_table(
        ["Campo", "Orientação"],
        [
            ["Planejada / Não planejada", "Planejada = padrão. Não planejada = emergência fora da janela"],
            ["Natureza", "Corretiva ou evolutiva"],
            ["Evolutiva", "Precisa autorização do Otero. Sem OK anexado, não passa no CCB"],
            ["Squad / Sistema", "Ex.: Parcerias / Sistur"],
            ["Afeta canal de venda?", "Backoffice normalmente não"],
            ["Coordenador / Gerente / Diretor", "Ex.: Vinícius / Kátia / Otero"],
            ["Plataforma", "PL/SQL / banco Sistur"],
            ["Número da CUP", "Pode ser mais de uma"],
            ["Benefício / risco / rollback", "Para que serve + rollback da CUP"],
            ["Validação na janela", "Sim/Não — ver seção 24"],
        ],
        first_cm=5.5,
    ))

    s.append(h1(24, "Validação na janela (Sim/Não)"))
    s.append(P("Aplicação de RFC costuma ser de madrugada."))
    s.append(P("Se colocar <b>Sim</b>: precisa ficar acordado; alguém liga para validar; se o Dev não atende → coordenador → gerente → diretor."))
    s.append(callout(
        "Se a mudança pode ser validada no dia seguinte: colocar <b>Não</b>. "
        "Só Sim quando realmente precisa validar na hora.",
        "alert",
    ))

    s.append(h1(25, "Evidências"))
    s.append(P("Evidência de Homolog (usuário) é obrigatória no fluxo normal."))
    s.append(P("Evidência boa: print/arquivo com <b>URL</b> e <b>data da máquina</b> visíveis."))
    s.append(P("Sem isso, corre risco de não passar no CCB. Em TI/Homolog, o time de mudança anexa evidência de execução da CUP."))

    s.append(h1(26, "Fluxo da RFC"))
    s.append(diagram(
        "Criar RFC\n"
        "    │\n"
        "    ▼\n"
        "Avançar CUP (Solicitação → Implantação/Homolog)\n"
        "    │\n"
        "    ▼\n"
        "Aplicação TI → evidência TI\n"
        "    │\n"
        "    ▼\n"
        "Aplicação Homolog → evidência Homolog\n"
        "    │\n"
        "    ▼\n"
        "Slack #qualidade (link da RFC)\n"
        "    │\n"
        "    ▼\n"
        "Validação técnica\n"
        "    │\n"
        "    ▼\n"
        "CUP → Produção → DBA → negócio → CCB → janela"
    ))
    s.append(P("Checklist típico antes do CCB:"))
    s.extend(bullets([
        "evidência de Homolog;",
        "OK do Otero (se evolutiva);",
        "OK da área de negócio (clique ou e-mail anexado).",
    ]))
    s.append(callout(
        "O último clique/aprovação precisa ser da <b>área de negócio</b> (não do coordenador Dev), senão o CCB recusa.",
        "alert",
    ))

    s.append(h1(27, "Rod Script"))
    s.append(P("Rod Script = script DML para corrigir algo em produção. Dev não tem DML livre em PROD."))
    s.append(P("Fluxo: montar/testar em Homolog → CUP com script → RFC com a tag <b>Rod Script</b> no título."))
    s.append(callout(
        "No CCB, Rod Script muda o jogo: não precisa aprovação do Otero nem de negócio da mesma forma.",
        "info",
    ))
    s.append(P(
        "Evidência: muitas vezes a informação só existe em PROD. Comentar: "
        "“Não é possível evidenciar em TI/Homolog — informações somente de produção.”"
    ))

    s.append(h1(28, "Desenvolvimento de tela: IE × Chrome"))
    s.append(P("Sistur é antigo. Muita coisa nasceu no Internet Explorer."))
    s.append(callout(
        "Edge não resolve. Precisa <b>IE + modo de compatibilidade</b> (cvc.com.br). "
        "Sem isso, JavaScript “morre” sem aviso claro.",
        "rule",
    ))
    s.append(P("Há telas no padrão antigo (IE) e telas no padrão novo (Chrome). Não misturar CSS/padrão."))
    s.append(P("Bibliotecas: jQuery, Prototype e JavaScript puro. Seguir o que a tela já carrega — não forçar jQuery se só tem Prototype."))

    s.append(h1(29, "Incluir item novo no menu"))
    s.append(P("Em Homolog/DEV (controle de acesso):"))
    s.extend(bullets([
        "Módulos → escolher módulo → criar item/subitem;",
        "se for pasta: sem programa; se for tela: package + procedure inicial;",
        "dar permissão de grupos;",
        "se a package tem várias procedures, liberar todas as necessárias.",
    ]))
    s.append(P("Na package, a procedure de menu valida se o usuário tem permissão; senão: “usuário não tem acesso”."))

    s.append(h1(30, "Item de menu em produção"))
    s.append(P("Em PROD o Dev não “clica e cria” como em Homolog."))
    s.append(diagram(
        "Planilha (caminho, package, procedures, grupos)\n"
        "        │\n"
        "        ▼\n"
        "Chamado → área de segurança cria o item\n"
        "        │\n"
        "        ▼\n"
        "Gerente aprova → acompanhar chamado"
    ))
    s.append(P("Modelo da planilha fica nos arquivos do Teams. Canal de chamado pode ter migrado para o Gira."))

    s.append(h1(31, "Chave de permissão × chave de controle"))
    s.append(simple_table(
        ["Conceito", "Uso"],
        [
            ["Chave de permissão", "Acessa o menu, mas não um pedaço (ícone/aba). Criar primeiro em PROD (gera código), replicar ambientes, usar no programa"],
            ["Chave de controle", "Coisas mais simples (ex.: data de corte / switch)"],
        ],
        first_cm=4.5,
    ))

    s.append(h1(32, "Apontamento de horas"))
    s.append(callout(
        "No Gira, apontar horas é obrigatório. Sem apontamento no fechamento do mês: impacta pagamento "
        "(especialmente terceiros). As horas do Gira é o que vai para faturamento.",
        "alert",
    ))

    s.append(h1(33, "Fluxo mental completo"))
    s.append(diagram(
        "Demanda (PO/coordenação)\n"
        "        │\n"
        "        ▼\n"
        "Achar menu → package\n"
        "        │\n"
        "        ▼\n"
        "Controle de versão → base PROD (sem CUR.)\n"
        "        │\n"
        "        ▼\n"
        "Desenvolver em DEV (padrão IE/Chrome)\n"
        "        │\n"
        "        ▼\n"
        "CUP (Homolog) + rollback\n"
        "   script | package\n"
        "        │\n"
        "        ▼\n"
        "TI → Homolog → evidências → RFC\n"
        "        │\n"
        "        ▼\n"
        "Slack → técnica → DBA → negócio → CCB → PROD"
    ))

    s.append(h1(34, "Principais caminhos / objetos"))
    s.append(simple_table(
        ["Item", "Para que serve"],
        [
            ["Controle de acesso de usuários", "Achar package do menu / criar item em Homolog"],
            ["Controle de versão", "Ver bloqueio e baixar package de PROD"],
            ["Gerenciamento → Workflow", "Abrir/avançar CUP"],
            ["Gira → Gestão de Mudança", "Abrir RFC"],
            ["Slack #qualidade", "Pedir avanço de RFC"],
            ["PL/SQL Developer", "Desenvolvimento"],
            ["Planilha de item de menu", "Subsídio do chamado em PROD"],
            ["Doc padrão de estrutura", "Nomenclatura de tabela/coluna"],
        ],
        first_cm=6.2,
    ))

    s.append(h1(35, "Contatos / papéis citados"))
    s.append(simple_table(
        ["Papel", "Quem (na reunião)"],
        [
            ["Coordenação Dev / Digs", "Vinícius"],
            ["Coordenação Backoffice", "Ana Paula"],
            ["Gerência", "Kátia"],
            ["Diretoria", "Otero"],
            ["Acesso workflow CUP", "Julian / Jabur"],
            ["Squad exemplo", "Parcerias"],
        ],
        first_cm=5.5,
    ))
    s.append(P("Ajustar nomes/squad ao time atual quando for usar."))

    s.append(h1(36, "O que você precisa guardar"))
    concepts = [
        ("1. DEV é o único lugar livre para código",
         "Depois é CUP/RFC."),
        ("2. Package se acha pelo menu no controle de acesso",
         "Descrição + package + PRC inicial."),
        ("3. Package bloqueada = falar com o dono ou copiar",
         "Sempre preferir base de PROD; tirar CUR. em DEV."),
        ("4. CUP sempre começa em fluxo Homolog",
         "Script antes → package → script depois. Rollback obrigatório de verdade."),
        ("5. Owner, commit e barra /",
         "SQL*Plus não perdoa."),
        ("6. Separe CUP de dados e CUP de package",
         "Homolog anda mais rápido."),
        ("7. RFC evolutiva precisa do Otero",
         "Negócio precisa aprovar (clique ou e-mail). Evidência com URL + data."),
        ("8. Validação na janela = Sim só se for acordar",
         "Senão, Não."),
        ("9. Rod Script no título facilita o CCB",
         "É DML de correção, não feature."),
        ("10. Menu/permissão em PROD é chamado + planilha",
         "Chave de permissão nasce em PROD. IE precisa de compatibilidade."),
    ]
    for title, body in concepts:
        s.append(P(title, "ConceptNum"))
        s.append(P(body, "BodyLeft"))

    s.append(Spacer(1, 8))
    s.append(hr())
    s.append(P("A frase que resume a reunião", "H2"))
    s.append(callout(
        "Ache a package pelo menu, desarme o bloqueio com base em produção, suba pela CUP "
        "(com rollback e padrão de dados), amarre na RFC com evidência e aprovações certas, "
        "passe TI → Homolog → DBA → negócio → CCB — "
        "<b>e não esqueça owner, commit e a barra no script.</b>",
        "rule",
    ))
    return s


def main():
    out = "/workspace/Apostila-CUP-RFC-e-Workflow-de-Publicacao.pdf"
    frame_cover = Frame(28 * mm, 40 * mm, PAGE_W - 46 * mm, PAGE_H - 80 * mm, id="cover")
    frame_body = Frame(MARGIN_L, MARGIN_B, CONTENT_W, PAGE_H - MARGIN_T - MARGIN_B, id="body")
    doc = BaseDocTemplate(
        out,
        pagesize=A4,
        title="Apostila — CUP, RFC e Workflow de Publicação",
        author="Treinamento interno",
        subject="Ambientes, package, scripts, CCB e boas práticas no Sistur",
    )
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame_cover], onPage=draw_cover),
        PageTemplate(id="body", frames=[frame_body], onPage=draw_page),
    ])
    doc.build(build_story())
    print(out)


if __name__ == "__main__":
    main()
