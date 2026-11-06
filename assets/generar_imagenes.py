"""Genera las imágenes del README (assets/*.svg y, con --capturas, assets/*.png).

Uso (desde la raíz del repo, con Orange3 y PyQt5 instalados):

    python assets/generar_imagenes.py              # esquemas SVG
    python assets/generar_imagenes.py --capturas   # + capturas de los widgets

Los SVG son autocontenidos: los iconos de Orange se incrustan como data
URI, porque GitHub y PyPI muestran las imágenes como <img> y no cargan
recursos externos.
"""
import base64
import math
import os
import sys

ASSETS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ASSETS)
OUR_ICONS = os.path.join(ROOT, "orangecontrib", "orange_gualbe_fs", "widgets", "icons")

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
TEXT = "#24292F"
MUTED = "#57606A"
FAINT = "#A0A7AF"
BORDER = "#D8DEE4"
ORANGE = "#FFA85C"
ORANGE_RING = "#E08A35"
ORANGE_DARK = "#9A5313"
NEUTRAL_BG = "#F2F4F6"
# (fondo, trazo/texto) de cada familia de métodos
FILTRO = ("#E3EEFB", "#1F5F9E")
WRAPPER = ("#EFE8FA", "#5B3A99")
EMBEB = ("#DFF3E8", "#1E7A4A")
KEEP_BG, KEEP_FG = "#CFEFDB", "#1E7A4A"
DROP_BG, DROP_FG = "#F2F4F6", "#98A0A9"

OUR = lambda name: os.path.join(OUR_ICONS, name)


def orange_icon(module, name):
    mod = __import__(module, fromlist=["__file__"])
    return os.path.join(os.path.dirname(mod.__file__), "icons", name)


def data_uri(path):
    with open(path, "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


def icon(path, cx, cy, size):
    uri = data_uri(path)
    x, y = cx - size / 2, cy - size / 2
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" '
            f'href="{uri}" xlink:href="{uri}"/>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=14, fill=TEXT, weight=400, anchor="middle", style=""):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'dominant-baseline="central"{style}>{esc(s)}</text>')


def tw(s, size, weight=400):
    """Anchura aproximada de un texto, para centrar y ajustar líneas."""
    return len(s) * size * (0.53 if weight >= 600 else 0.50)


def paragraph(x, y, s, max_px, size=13, fill=MUTED, weight=400, anchor="start", lh=None):
    lh = lh or size * 1.5
    lines, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if tw(t, size, weight) <= max_px:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    out = "".join(text(x, y + i * lh, ln, size, fill, weight, anchor)
                  for i, ln in enumerate(lines))
    return out, len(lines)


def rect(x, y, w, h, fill, stroke="none", rx=6, sw=1, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')


def line(x1, y1, x2, y2, color=BORDER, width=1.5, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{width}"{d}/>')


def arrow(x1, y1, x2, y2, color=MUTED, width=2, dash="", head=9):
    """Línea con punta de flecha dibujada como polígono (los marcadores con
    context-stroke no se muestran igual en todos los navegadores)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    ca, sa = math.cos(ang), math.sin(ang)
    bx, by = x2 - head * ca, y2 - head * sa          # base de la punta
    p2 = (bx + head * 0.5 * sa, by - head * 0.5 * ca)
    p3 = (bx - head * 0.5 * sa, by + head * 0.5 * ca)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{bx + ca}" y2="{by + sa}" stroke="{color}" '
            f'stroke-width="{width}"{d}/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}" '
            f'fill="{color}"/>')


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{esc(title)}</title>'
            + rect(0.5, 0.5, w - 1, h - 1, "#FFFFFF", BORDER, rx=16)
            + body + "</svg>\n")


def save(name, content):
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("escrito", name, f"({len(content) // 1024} KB)")


def bars(x0, base, heights, colors, bw=24, gap=10, labels=None, lsize=11):
    """Barras verticales con la base en y=base. colors: un color de relleno por barra."""
    out = []
    for i, (hh, col) in enumerate(zip(heights, colors)):
        x = x0 + i * (bw + gap)
        out.append(rect(x, base - hh, bw, hh, col[0], col[1], rx=3, sw=1.2))
        if labels:
            out.append(text(x + bw / 2, base + 13, labels[i], lsize, MUTED))
    return "".join(out)


def pill_tag(x, y, label, fg, bg):
    """Pastilla pequeña centrada en (x, y)."""
    wdt = tw(label, 11, 700) + 14
    return (rect(x - wdt / 2, y - 9, wdt, 18, bg, "none", rx=9)
            + text(x, y, label, 11, fg, 700))


# ---------------------------------------------------------------- banner
def banner():
    w, h = 1000, 240
    b = []
    b.append(f'<circle cx="140" cy="120" r="78" fill="#FFCFA0" stroke="{ORANGE_RING}" stroke-width="3"/>')
    b.append(icon(OUR("category.svg"), 140, 120, 104))
    b.append(text(260, 92, "orange_gualbe_fs", 46, TEXT, 700, "start"))
    b.append(text(262, 140, "Selección de atributos para Orange Data Mining", 21, MUTED, 400, "start"))
    chips = [("owunivariateselection.svg", "Filtro Univariante", FILTRO),
             ("owwrapperselection.svg", "Selección Wrapper", WRAPPER),
             ("owembeddedselection.svg", "Selección Embebida", EMBEB)]
    x = 260
    for fname, label, (bg, fg) in chips:
        cw = int(tw(label, 16, 600)) + 64
        b.append(rect(x, 172, cw, 42, bg, fg, rx=21, sw=1.5))
        b.append(f'<circle cx="{x + 21}" cy="193" r="16" fill="#FFCFA0"/>')
        b.append(icon(OUR(fname), x + 21, 193, 24))
        b.append(text(x + 44, 193, label, 16, fg, 600, "start"))
        x += cw + 14
    save("banner.svg", svg(w, h, "".join(b),
                           "orange_gualbe_fs: selección de atributos para Orange Data Mining"))


# ---------------------------------------------------------------- familias
def familias():
    w, h = 960, 428
    CW, GAP, X0 = 293, 16, 24
    cards = [
        dict(family=FILTRO, icon="owunivariateselection.svg", title="Filtro",
             widget="widget Filtro Univariante",
             texto="Puntúa cada atributo por separado frente al objetivo y se queda con los mejores.",
             filas=["Sin modelo predictivo", "Muy rápido", "Mira cada atributo por separado"]),
        dict(family=WRAPPER, icon="owwrapperselection.svg", title="Wrapper",
             widget="widget Selección Wrapper",
             texto="Prueba subconjuntos de atributos entrenando un modelo y se queda con el que mejor rinde.",
             filas=["Entrena el modelo muchas veces", "El más lento", "Tiene en cuenta combinaciones"]),
        dict(family=EMBEB, icon="owembeddedselection.svg", title="Embebida",
             widget="widget Selección Embebida",
             texto="Entrena un modelo una vez y usa la importancia que él mismo asigna a cada atributo.",
             filas=["Entrena el modelo una sola vez", "Rápido", "Usa la importancia del propio modelo"]),
    ]
    b = []
    for i, c in enumerate(cards):
        x0 = X0 + i * (CW + GAP)
        cx = x0 + CW / 2
        bg, fg = c["family"]
        b.append(rect(x0, 20, CW, h - 40, "#FAFBFC", BORDER, rx=14))
        b.append(f'<path d="M{x0 + 16} 21.5 H{x0 + CW - 16}" stroke="{fg}" stroke-width="4" stroke-linecap="round"/>')
        # cabecera
        b.append(f'<circle cx="{x0 + 40}" cy="64" r="23" fill="#FFCFA0" stroke="{ORANGE_RING}" stroke-width="1.5"/>')
        b.append(icon(OUR(c["icon"]), x0 + 40, 64, 30))
        b.append(text(x0 + 74, 56, c["title"], 21, fg, 700, "start"))
        b.append(text(x0 + 74, 78, c["widget"], 12.5, MUTED, 400, "start"))
        p, _ = paragraph(x0 + 22, 114, c["texto"], CW - 44, 13.5, TEXT)
        b.append(p)
        # esquema
        if i == 0:      # filtro: barras con umbral
            heights = [86, 34, 100, 20, 68, 48, 14]
            base = 276
            x_start = x0 + (CW - (7 * 24 + 6 * 10)) / 2
            cols = [(bg, fg) if hh > 55 else (DROP_BG, DROP_FG) for hh in heights]
            b.append(text(x0 + 24, 178, "puntuación", 11.5, MUTED, 400, "start"))
            b.append(line(x0 + 20, base, x0 + CW - 20, base, BORDER))
            b.append(bars(x_start, base, heights, cols, labels=list("ABCDEFG")))
            b.append(line(x0 + 20, base - 55, x0 + CW - 20, base - 55, fg, 1.8, "5 4"))
            b.append(text(x0 + CW - 24, base - 66, "umbral", 11.5, fg, 700, "end"))
        elif i == 1:    # wrapper: ciclo
            boxes = [(cx, 192, "Elegir atributos"), (cx + 78, 262, "Entrenar modelo"),
                     (cx - 78, 262, "Evaluar")]
            for bx, by, lab in boxes:
                bw_ = max(84, tw(lab, 12.5, 700) + 26)
                b.append(rect(bx - bw_ / 2, by - 17, bw_, 34, bg, fg, rx=9, sw=1.5))
                b.append(text(bx, by, lab, 12.5, fg, 700))
            b.append(arrow(cx + 30, 211, cx + 70, 243, fg, 2))
            b.append(arrow(cx + 20, 262, cx - 34, 262, fg, 2))
            b.append(arrow(cx - 70, 243, cx - 30, 211, fg, 2))
            b.append(text(cx, 294, "se repite hasta hallar el mejor subconjunto", 11.5, MUTED))
        else:           # embebida: modelo -> importancias con umbral
            b.append(rect(x0 + 20, 196, 96, 64, bg, fg, rx=10, sw=1.5))
            b.append(text(x0 + 68, 219, "Modelo", 14, fg, 700))
            b.append(text(x0 + 68, 240, "1 solo ajuste", 11.5, fg))
            b.append(arrow(x0 + 120, 228, x0 + 146, 228, fg, 2))
            heights = [72, 30, 56, 14]
            base = 276
            cols = [(bg, fg) if hh > 40 else (DROP_BG, DROP_FG) for hh in heights]
            b.append(text(x0 + 150, 178, "importancia", 11.5, MUTED, 400, "start"))
            b.append(line(x0 + 146, base, x0 + CW - 12, base, BORDER))
            b.append(bars(x0 + 154, base, heights, cols, bw=20, gap=8, labels=list("ABCD")))
            b.append(line(x0 + 146, base - 40, x0 + CW - 12, base - 40, fg, 1.8, "5 4"))
            b.append(text(x0 + CW - 14, base - 52, "umbral", 11.5, fg, 700, "end"))
        # filas de características
        for k, fila in enumerate(c["filas"]):
            yy = 330 + k * 28
            b.append(f'<circle cx="{x0 + 30}" cy="{yy}" r="5" fill="{fg}"/>')
            b.append(text(x0 + 46, yy, fila, 13.5, TEXT, 400, "start"))
    save("familias.svg", svg(w, h, "".join(b),
                             "Las tres familias de selección de atributos: filtro, wrapper y embebida"))


# ---------------------------------------------------------------- flujo
def flujo():
    w, h = 960, 470
    R = 30
    data_c = ("#FFD39F", "#D99A4E")
    trans_c = ("#FF9D5E", "#D9702A")
    ours_c = (ORANGE, ORANGE_RING)
    model_c = ("#FAC1D9", "#D9799F")
    eval_c = ("#C3F3F3", "#5BBFBF")
    nodes = {
        "file": (80, 195, "File", data_c, orange_icon("Orange.widgets.data", "File.svg")),
        "impute": (235, 195, "Impute", trans_c, orange_icon("Orange.widgets.data", "Impute.svg")),
        "table": (780, 105, "Data Table", data_c, orange_icon("Orange.widgets.data", "Table.svg")),
        "test": (780, 285, "Test and Score", eval_c,
                 orange_icon("Orange.widgets.evaluate", "TestLearners1.svg")),
        "logreg": (560, 385, "Regresión Logística", model_c,
                   orange_icon("Orange.widgets.model", "LogisticRegression.svg")),
    }
    SX, SY = 480, 195                      # centro del bloque de selección
    HALF = 96                              # semianchura de la pastilla

    def right(n):
        return nodes[n][0] + R + 3, nodes[n][1]

    def left(n):
        return nodes[n][0] - R - 3, nodes[n][1]

    def link(p1, p2, label=None):
        (x1, y1), (x2, y2) = p1, p2
        dx = (x2 - x1) / 2
        out = (f'<path d="M{x1} {y1} C{x1 + dx} {y1} {x2 - dx} {y2} {x2} {y2}" '
               f'fill="none" stroke="#9AA3AD" stroke-width="2.5"/>'
               f'<circle cx="{x1}" cy="{y1}" r="3.5" fill="#9AA3AD"/>'
               f'<circle cx="{x2}" cy="{y2}" r="3.5" fill="#9AA3AD"/>')
        if label:
            out += text(label[0], label[1], label[2], 12, MUTED, 400, "middle")
        return out

    sel_left, sel_right = (SX - HALF - 11, SY), (SX + HALF + 11, SY)
    b = [link(right("file"), left("impute")),
         link(right("impute"), sel_left),
         link(sel_right, left("table")),
         link(sel_right, left("test")),
         link(right("logreg"), left("test"), label=(690, 392, "Learner"))]

    # bloque de selección: los tres widgets intercambiables
    b.append(f'<rect x="{SX - HALF - 8}" y="{SY - 48}" width="{2 * HALF + 16}" height="96" rx="48" '
             f'fill="none" stroke="{ORANGE_RING}" stroke-width="2" stroke-dasharray="5 4"/>')
    b.append(rect(SX - HALF, SY - 40, 2 * HALF, 80, "#FFF4E8", ORANGE_RING, rx=40, sw=1.5))
    for k, fname in enumerate(["owunivariateselection.svg", "owwrapperselection.svg",
                               "owembeddedselection.svg"]):
        cx = SX + (k - 1) * 64
        b.append(f'<circle cx="{cx}" cy="{SY}" r="26" fill="{ORANGE}" stroke="{ORANGE_RING}" stroke-width="2"/>')
        b.append(icon(OUR(fname), cx, SY, 34))
    b.append(text(SX, SY + 76, "Uno de los tres widgets de selección", 14, TEXT, 600))
    b.append(text(SX, SY + 96, "Filtro Univariante · Selección Wrapper · Selección Embebida", 11.5, FAINT))

    for key, (x, y, label, (fill, stroke), path) in nodes.items():
        b.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        b.append(icon(path, x, y, 40))
        b.append(text(x, y + R + 22, label, 14, TEXT, 400))
    b.append(text(235, 195 + R + 41, "sin valores ausentes", 11.5, FAINT))
    b.append(text(780, 105 + R + 41, "columnas conservadas", 11.5, FAINT))
    b.append(text(780, 285 + R + 41, "con el modelo y los datos reducidos", 11.5, FAINT))
    b.append(f'<circle cx="60" cy="440" r="11" fill="none" stroke="{ORANGE_RING}" '
             'stroke-width="2" stroke-dasharray="4 3"/>')
    b.append(text(78, 440, "widgets de orange_gualbe_fs", 13, MUTED, 400, "start"))
    save("flujo.svg", svg(w, h, "".join(b), "Flujo de trabajo típico en Orange"))


# ---------------------------------------------------------------- univariante
def univariante():
    import warnings
    warnings.filterwarnings("ignore")
    import numpy as np
    from Orange.data import Table
    from sklearn.feature_selection import f_regression

    w, h = 960, 540
    # puntuaciones reales (f_regression) de los 7 mejores atributos de housing
    t = Table("housing")
    f, _ = f_regression(t.X, t.Y)
    order = np.argsort(-f)[:7]
    names = [t.domain.attributes[i].name for i in order]
    scores = f[order] / f[order].max() * 150

    b = []
    b.append(rect(20, 20, 560, h - 40, "#FAFBFC", BORDER, rx=12))
    b.append(rect(600, 20, 340, h - 40, "#FAFBFC", BORDER, rx=12))
    bg, fg = FILTRO
    b.append(text(44, 48, "1 · Cada atributo recibe una puntuación", 17, TEXT, 700, "start"))
    b.append(text(44, 72, "Ejemplo con el conjunto housing y la función Regresión F", 12.5, MUTED, 400, "start"))

    # gráfico de barras
    base, bw, gap = 260, 52, 14
    x0 = 44 + (512 - (7 * bw + 6 * gap)) / 2
    keep = 3
    cols = [(bg, fg) if i < keep else (DROP_BG, DROP_FG) for i in range(7)]
    b.append(text(44, 100, "puntuación", 11.5, MUTED, 400, "start"))
    b.append(line(40, base, 560, base, BORDER))
    b.append(bars(x0, base, list(scores), cols, bw=bw, gap=gap, labels=names, lsize=11.5))
    cut = x0 + keep * (bw + gap) - gap / 2
    b.append(line(cut, 96, cut, base + 30, fg, 1.8, "5 4"))
    b.append(text(cut - 8, 112, "se quedan", 12, fg, 700, "end"))
    b.append(text(cut + 8, 112, "se descartan", 12, DROP_FG, 700, "start"))

    # cómo corta cada método
    b.append(text(44, 322, "Cómo decide cuántos conservar", 14, TEXT, 700, "start"))
    cards = [("K mejores", "SelectKBest", "los k de mayor puntuación", 3),
             ("Percentil", "SelectPercentile", "el % de mejor puntuación", 4),
             ("Alpha", "Fpr · Fdr · Fwe", "los de p-valor menor que α", 5)]
    cw = 164
    for k, (nm, sub, desc, n) in enumerate(cards):
        cx0 = 44 + k * (cw + 10)
        b.append(rect(cx0, 338, cw, 154, "#FFFFFF", BORDER, rx=10))
        b.append(text(cx0 + 14, 358, nm, 14, fg, 700, "start"))
        b.append(text(cx0 + 14, 376, sub, 11.5, MUTED, 400, "start"))
        for j in range(7):
            on = j < n
            b.append(rect(cx0 + 14 + j * 20, 392, 16, 16, bg if on else DROP_BG,
                          fg if on else BORDER, rx=3, sw=1.2))
        p, _ = paragraph(cx0 + 14, 428, desc, cw - 28, 12, TEXT)
        b.append(p)
        b.append(text(cx0 + 14, 474, {3: "k = 3  →  3 atributos", 4: "60 %  →  4 atributos",
                                       5: "α = 0,05  →  5 atributos"}[n],
                      12, fg, 700, "start"))
    b.append(text(44, 508, "Fpr, Fdr y Fwe controlan el error con distinto rigor (de menos a más estricto).",
                  11.5, MUTED, 400, "start"))

    # matriz de compatibilidad
    b.append(text(624, 48, "2 · La función de puntuación", 17, TEXT, 700, "start"))
    b.append(text(624, 68, "depende del tipo de objetivo", 17, TEXT, 700, "start"))
    colx = [800, 888]
    heads = [("Objetivo", "categórico"), ("Objetivo", "numérico")]
    for cxh, (a, c) in zip(colx, heads):
        b.append(text(cxh, 106, a, 12, MUTED))
        b.append(text(cxh, 122, c, 13, TEXT, 700))
    b.append(text(800, 140, "(clasificación)", 11, FAINT))
    b.append(text(888, 140, "(regresión)", 11, FAINT))
    rows = [("chi2", "atributos ≥ 0", (True, False)),
            ("f_classif", "ANOVA F", (True, False)),
            ("f_regression", "Regresión F", (False, True)),
            ("r_regression", "Pearson r", (False, True))]
    for k, (nm, sub, ok) in enumerate(rows):
        yy = 186 + k * 56
        b.append(rect(612, yy - 26, 316, 50, "#FFFFFF", BORDER, rx=8))
        b.append(text(626, yy - 8, nm, 14, TEXT, 700, "start"))
        b.append(text(626, yy + 10, sub, 11.5, MUTED, 400, "start"))
        for cxh, good in zip(colx, ok):
            if good:
                b.append(f'<circle cx="{cxh}" cy="{yy}" r="14" fill="{KEEP_BG}" stroke="{KEEP_FG}" stroke-width="1.5"/>')
                b.append(f'<path d="M{cxh - 6} {yy} l4 4 l8 -9" fill="none" stroke="{KEEP_FG}" '
                         'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
            else:
                b.append(f'<circle cx="{cxh}" cy="{yy}" r="14" fill="{DROP_BG}" stroke="{BORDER}" stroke-width="1.5"/>')
                b.append(f'<path d="M{cxh - 5} {yy - 5} l10 10 M{cxh + 5} {yy - 5} l-10 10" '
                         f'stroke="{DROP_FG}" stroke-width="2.2" stroke-linecap="round"/>')
    p, n = paragraph(624, 428, "El widget detecta el tipo de objetivo y solo activa las funciones válidas.",
                     296, 12.5, TEXT)
    b.append(p)
    p, _ = paragraph(624, 428 + n * 18.75 + 8,
                     "r_regression no calcula p-valores: solo vale con K mejores y Percentil.",
                     296, 12.5, ORANGE_DARK)
    b.append(p)
    save("univariante.svg", svg(w, h, "".join(b), "Cómo funciona el widget Filtro Univariante"))


# ---------------------------------------------------------------- wrapper
def wrapper():
    w, h = 960, 510
    bg, fg = WRAPPER
    PW, PX = 296, [20, 332, 644]
    titles = [("RFE", "Eliminación Recursiva de Atributos"),
              ("RFECV", "RFE con validación cruzada"),
              ("SFS", "Selección Secuencial")]
    captions = ["Entrena el modelo, elimina el atributo menos importante y repite hasta quedar con n. El paso indica cuántos se eliminan por iteración.",
                "Igual que RFE, pero la validación cruzada elige sola cuántos atributos conservar: el nº con mejor puntuación.",
                "Añade (hacia adelante) o quita (hacia atrás) un atributo cada vez, eligiendo el mejor paso por validación cruzada."]
    b = []
    for i in range(3):
        x = PX[i]
        b.append(rect(x, 20, PW, 392, "#FAFBFC", BORDER, rx=12))
        b.append(text(x + 22, 44, titles[i][0], 20, fg, 700, "start"))
        b.append(text(x + 22, 66, titles[i][1], 12.5, MUTED, 400, "start"))
        p, _ = paragraph(x + 22, 340, captions[i], PW - 44, 12.5, TEXT)
        b.append(p)

    # --- RFE: filas de cuadrados donde se van tachando
    x = PX[0]
    removed_order = [5, 2, 7, 0]           # atributo eliminado en cada iteración
    gone = set()
    sq, sg = 22, 6
    sx = x + 56
    b.append(text(x + 22, 92, "nº de atributos", 11.5, MUTED, 400, "start"))
    for r in range(5):
        yy = 112 + r * 44
        n_left = 8 - len(gone)
        b.append(text(x + 30, yy + sq / 2, str(n_left), 14, TEXT, 700))
        final = r == 4
        for j in range(8):
            xx = sx + j * (sq + sg)
            if j in gone:
                b.append(rect(xx, yy, sq, sq, "#FFFFFF", BORDER, rx=4, sw=1.2, extra=' stroke-dasharray="3 3"'))
                b.append(f'<path d="M{xx + 6} {yy + 6} l10 10 M{xx + 16} {yy + 6} l-10 10" stroke="{FAINT}" stroke-width="1.6" stroke-linecap="round"/>')
            else:
                col = (KEEP_BG, KEEP_FG) if final else (bg, fg)
                b.append(rect(xx, yy, sq, sq, col[0], col[1], rx=4, sw=1.5))
        if r < 4:
            gone.add(removed_order[r])
            b.append(arrow(sx + 4 * (sq + sg) - 3, yy + sq + 3, sx + 4 * (sq + sg) - 3, yy + 40, FAINT, 1.4))
    b.append(text(sx + 8 * (sq + sg) - sg + 2, 112 + 4 * 44 + sq / 2, "", 11))
    b.append(text(x + PW / 2, 318, "los que quedan (verde) forman el resultado", 11.5, KEEP_FG))

    # --- RFECV: curva de puntuación
    x = PX[1]
    ax0, ay0, aw, ah = x + 52, 270, 214, 140
    scores = [0.50, 0.67, 0.80, 0.86, 0.90, 0.885, 0.865, 0.845]
    sx_ = lambda k: ax0 + 10 + k * (aw - 20) / 7
    sy_ = lambda v: ay0 - (v - 0.45) / 0.50 * ah
    b.append(line(ax0, ay0, ax0 + aw, ay0, MUTED, 1.5))
    b.append(line(ax0, ay0, ax0, ay0 - ah - 6, MUTED, 1.5))
    b.append(text(x + 22, 92, "puntuación (validación cruzada)", 11.5, MUTED, 400, "start"))
    b.append(text(ax0 + aw / 2, ay0 + 26, "nº de atributos", 11.5, MUTED))
    for k in range(8):
        b.append(text(sx_(k), ay0 + 12, str(k + 1), 11, MUTED))
    pts = " ".join(f"{sx_(k)},{sy_(v)}" for k, v in enumerate(scores))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{fg}" stroke-width="2.6"/>')
    for k, v in enumerate(scores):
        best = k == 4
        b.append(f'<circle cx="{sx_(k)}" cy="{sy_(v)}" r="{7 if best else 4}" fill="{KEEP_BG if best else "#FFFFFF"}" '
                 f'stroke="{KEEP_FG if best else fg}" stroke-width="2.4"/>')
    b.append(line(sx_(4), sy_(scores[4]) + 8, sx_(4), ay0, KEEP_FG, 1.6, "4 4"))
    b.append(text(sx_(4), sy_(scores[4]) - 20, "óptimo: 5 atributos", 12, KEEP_FG, 700))

    # --- SFS: adelante y atrás
    x = PX[2]
    sq, sg = 18, 6
    sx = x + (PW - (6 * sq + 5 * sg)) / 2 + 22
    def block(y0, title, steps):
        out = [text(x + 22, y0, title, 12.5, fg, 700, "start")]
        for r, filled in enumerate(steps):
            yy = y0 + 14 + r * 24
            out.append(text(x + 22, yy + sq / 2, f"paso {r}", 11, FAINT, 400, "start"))
            for j in range(6):
                xx = sx + j * (sq + sg)
                on = j in filled
                out.append(rect(xx, yy, sq, sq, bg if on else "#FFFFFF", fg if on else BORDER, rx=4, sw=1.5))
        return "".join(out)
    b.append(block(96, "hacia adelante: empieza vacío y añade",
                   [set(), {2}, {2, 4}, {0, 2, 4}]))
    b.append(block(214, "hacia atrás: empieza completo y quita",
                   [{0, 1, 2, 3, 4, 5}, {0, 1, 2, 4, 5}, {0, 2, 4, 5}, {0, 2, 4}]))

    # pie
    b.append(rect(20, 428, 920, 56, "#FFFFFF", BORDER, rx=12))
    b.append(text(44, 448, "Modelo base: Regresión Logística o Bosque Aleatorio (clasificación) · Regresión Lineal o Bosque Aleatorio (regresión).",
                  13, TEXT, 400, "start"))
    b.append(text(44, 468, "Al ser más lentos, este widget no aplica los cambios solo: pulsa Apply (los datos nuevos sí se procesan al llegar).",
                  13, MUTED, 400, "start"))
    save("wrapper.svg", svg(w, h, "".join(b), "Cómo funciona el widget Selección Wrapper"))


# ---------------------------------------------------------------- embebida
def embebida():
    w, h = 960, 510
    bg, fg = EMBEB
    MID = ("#EAF7EF", "#7DBF98")
    b = []
    b.append(rect(20, 20, 480, h - 40, "#FAFBFC", BORDER, rx=12))
    b.append(rect(520, 20, 420, h - 40, "#FAFBFC", BORDER, rx=12))
    b.append(text(44, 48, "1 · El modelo se entrena una vez", 17, TEXT, 700, "start"))
    b.append(text(44, 72, "y sus propias importancias deciden qué atributos se quedan", 12.5, MUTED, 400, "start"))

    # datos -> modelo -> importancias
    b.append(rect(44, 100, 70, 56, "#FFFFFF", BORDER, rx=10))
    b.append(text(79, 128, "Datos", 14, TEXT, 700))
    b.append(arrow(118, 128, 146, 128, MUTED, 2))
    b.append(rect(150, 94, 150, 68, bg, fg, rx=12, sw=1.8))
    b.append(text(225, 118, "Modelo (estimador)", 13.5, fg, 700))
    b.append(text(225, 140, "entrenado una sola vez", 11.5, fg))
    b.append(arrow(304, 128, 332, 128, MUTED, 2))
    b.append(rect(336, 106, 148, 44, "#FFFFFF", fg, rx=10, sw=1.5))
    b.append(text(410, 122, "coef_ o", 12, fg, 700))
    b.append(text(410, 138, "feature_importances_", 11, fg))

    # importancias con umbrales
    heights = [100, 24, 120, 12, 80, 30, 10, 18]
    sc = 1.45
    base, bw, gap = 396, 34, 10
    x0 = 44 + (400 - (8 * bw + 7 * gap)) / 2
    mean = sum(heights) / len(heights)
    srt = sorted(heights)
    median = srt[3] / 2 + srt[4] / 2
    cols = []
    for hh in heights:
        if hh > mean:
            cols.append((bg, fg))
        elif hh > median:
            cols.append(MID)
        else:
            cols.append((DROP_BG, DROP_FG))
    b.append(text(44, 184, "importancia de cada atributo", 11.5, MUTED, 400, "start"))
    b.append(line(40, base, 480, base, BORDER))
    b.append(bars(x0, base, [hh * sc for hh in heights], cols, bw=bw, gap=gap,
                  labels=list("ABCDEFGH"), lsize=12))
    xe = x0 + 8 * (bw + gap) - gap + 6
    b.append(line(40, base - mean * sc, xe, base - mean * sc, fg, 2, "6 4"))
    b.append(text(xe + 4, base - mean * sc, "media", 11.5, fg, 700, "start"))
    b.append(line(40, base - median * sc, xe, base - median * sc, MID[1], 2, "2 4"))
    b.append(text(xe + 4, base - median * sc, "mediana", 11.5, "#4F9A70", 700, "start"))
    b.append(text(44, 430, "Umbral: la media, la mediana o un valor propio.", 12.5, TEXT, 400, "start"))
    b.append(text(44, 452, "Opcional: como máximo N atributos (los de mayor importancia).", 12.5, TEXT, 400, "start"))
    for k, (col, lab) in enumerate([((bg, fg), "con la media"), (MID, "y con la mediana"),
                                    ((DROP_BG, DROP_FG), "descartado")]):
        lx = 44 + [0, 122, 262][k]
        b.append(rect(lx, 468, 16, 16, col[0], col[1], rx=3, sw=1.2))
        b.append(text(lx + 24, 476, lab, 12, MUTED, 400, "start"))

    # estimadores
    b.append(text(544, 48, "2 · 12 algoritmos para elegir", 17, TEXT, 700, "start"))
    b.append(text(544, 72, "el widget ofrece los válidos para el tipo de objetivo", 12.5, MUTED, 400, "start"))
    CT, RT = ("#1F5F9E", "#DCEBFA"), ("#9A5313", "#FFE9D2")

    def chips(y0, items):
        out, x, y = [], 544, y0
        for label, tags in items:
            wdt = tw(label, 12.5, 600) + 30 + 22 * len(tags)
            if x + wdt > 924:
                x, y = 544, y + 38
            out.append(rect(x, y, wdt, 30, "#FFFFFF", fg, rx=15, sw=1.4))
            out.append(text(x + 12, y + 15, label, 12.5, TEXT, 600, "start"))
            tx = x + 12 + tw(label, 12.5, 600) + 18
            for tag in tags:
                col = CT if tag == "C" else RT
                out.append(f'<circle cx="{tx}" cy="{y + 15}" r="9" fill="{col[1]}"/>')
                out.append(text(tx, y + 15, tag, 11, col[0], 700))
                tx += 22
            x += wdt + 8
        return "".join(out), y + 30

    b.append(text(544, 108, "Modelos lineales", 14, fg, 700, "start"))
    b.append(text(544, 128, "valoran el coeficiente de cada atributo (coef_)", 12, MUTED, 400, "start"))
    lin, yend = chips(144, [("Regresión Logística", ["C"]), ("SVM Lineal", ["C"]),
                            ("Regresión Lineal", ["R"]), ("Ridge", ["R"]), ("Lasso", ["R"]),
                            ("ElasticNet", ["R"]), ("SGD", ["C", "R"])])
    b.append(lin)
    y1 = yend + 30
    b.append(text(544, y1, "Árboles y ensambles", 14, fg, 700, "start"))
    b.append(text(544, y1 + 20, "valoran la importancia acumulada (feature_importances_)", 12, MUTED, 400, "start"))
    tre, yend = chips(y1 + 36, [("Árbol de Decisión", ["C", "R"]), ("Bosque Aleatorio", ["C", "R"]),
                                ("Extra Trees", ["C", "R"]), ("Gradient Boosting", ["C", "R"]),
                                ("AdaBoost", ["C", "R"])])
    b.append(tre)
    ly = 466
    b.append(f'<circle cx="548" cy="{ly}" r="9" fill="{CT[1]}"/>')
    b.append(text(548, ly, "C", 11, CT[0], 700))
    b.append(text(564, ly, "clasificación: 8 algoritmos", 12, MUTED, 400, "start"))
    b.append(f'<circle cx="744" cy="{ly}" r="9" fill="{RT[1]}"/>')
    b.append(text(744, ly, "R", 11, RT[0], 700))
    b.append(text(760, ly, "regresión: 10 algoritmos", 12, MUTED, 400, "start"))
    save("embebida.svg", svg(w, h, "".join(b), "Cómo funciona el widget Selección Embebida"))


# ---------------------------------------------------------------- capturas
def capturas():
    import warnings
    warnings.filterwarnings("ignore")
    from AnyQt.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from Orange.data import Table
    from Orange.preprocess import Impute
    from orangecontrib.orange_gualbe_fs.widgets.owunivariateselection import OWUnivariateSelection
    from orangecontrib.orange_gualbe_fs.widgets.owwrapperselection import OWWrapperSelection, SFS_METHOD
    from orangecontrib.orange_gualbe_fs.widgets.owembeddedselection import OWEmbeddedSelection, MEDIAN

    def grab(widget, name):
        widget.show()
        app.processEvents()
        widget.adjustSize()
        app.processEvents()
        widget.grab().save(os.path.join(ASSETS, name))
        print("escrita", name)

    housing = Table("housing")
    heart = Impute()(Table("heart_disease"))      # sin valores ausentes

    w = OWUnivariateSelection()
    w.set_data(housing)
    w.method_index, w.k = 0, 5
    w.commit.now()
    grab(w, "captura_univariante.png")

    w2 = OWWrapperSelection()
    w2.set_data(heart)
    w2.method_index, w2.n_features, w2.cv = SFS_METHOD, 5, 5
    w2.direction_index, w2.scoring_index = 0, 1
    w2.scoring_combo.setCurrentIndex(1)
    w2._update_param_visibility()
    w2.commit.now()
    grab(w2, "captura_wrapper.png")

    w3 = OWEmbeddedSelection()
    w3.set_data(housing)
    w3.estimator_index = 6                      # Bosque Aleatorio
    w3.estimator_combo.setCurrentIndex(6)
    w3.threshold_mode = MEDIAN
    w3._update_threshold_visibility()
    w3.limit_max_features, w3.max_features = True, 5
    w3.max_features_spin.setEnabled(True)
    w3.commit.now()
    grab(w3, "captura_embebida.png")


if __name__ == "__main__":
    banner()
    familias()
    flujo()
    univariante()
    wrapper()
    embebida()
    if "--capturas" in sys.argv:
        capturas()
