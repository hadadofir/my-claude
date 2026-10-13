from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---------------------------------------------------------------- palette --
SURFACE       = RGBColor(0xfc, 0xfc, 0xfb)
CARD          = RGBColor(0xf3, 0xf2, 0xec)
DARK          = RGBColor(0x0b, 0x0b, 0x0b)
DARK_CARD     = RGBColor(0x17, 0x17, 0x16)
INK_PRIMARY   = RGBColor(0x0b, 0x0b, 0x0b)
INK_SECONDARY = RGBColor(0x52, 0x51, 0x4e)
INK_MUTED     = RGBColor(0x89, 0x87, 0x81)
GRIDLINE      = RGBColor(0xe1, 0xe0, 0xd9)
BASELINE      = RGBColor(0xc3, 0xc2, 0xb7)
BLUE          = RGBColor(0x2a, 0x78, 0xd6)
ORANGE        = RGBColor(0xeb, 0x68, 0x34)
VIOLET        = RGBColor(0x4a, 0x3a, 0xa7)
VIOLET_LIGHT  = RGBColor(0xb2, 0xa4, 0xea)
WHITE         = RGBColor(0xff, 0xff, 0xff)
CREAM         = RGBColor(0xf2, 0xf1, 0xec)

FONT = "Arial"
ASSETS = "/home/ofir-hadad/ofir/sandbox/pitch/assets"
OUT = "/home/ofir-hadad/ofir/sandbox/pitch/neuromorphic_vio_pitch.pptx"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]

TOTAL_SLIDES = 12

# ------------------------------------------------------------- primitives --
def no_shadow(shp):
    shp.shadow.inherit = False

def add_bg(slide, color):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    r.fill.solid(); r.fill.fore_color.rgb = color
    r.line.fill.background()
    no_shadow(r)
    return r

def add_rect(slide, l, t, w, h, color, line_color=None, line_w=None, rounded=False, radius=0.06):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, l, t, w, h)
    if rounded:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    shp.fill.solid(); shp.fill.fore_color.rgb = color
    if line_color is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line_color
        shp.line.width = line_w or Pt(1)
    no_shadow(shp)
    return shp

def add_text(slide, l, t, w, h, text, size=18, color=INK_PRIMARY, bold=False,
             italic=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             line_spacing=1.0, letter_spaced=False, font=FONT):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font
    r.font.color.rgb = color
    if letter_spaced:
        _set_letter_spacing(r, 150)
    return tb

def _set_letter_spacing(run, val):
    rPr = run._r.get_or_add_rPr()
    rPr.set('spc', str(val))

def add_kicker(slide, text, color=VIOLET, on_dark=False):
    tick = add_rect(slide, Inches(0.7), Inches(0.62), Inches(0.28), Inches(0.05), color)
    add_text(slide, Inches(1.06), Inches(0.48), Inches(8), Inches(0.35), text,
              size=12.5, color=(VIOLET_LIGHT if on_dark else INK_MUTED), bold=True, letter_spaced=True)

def add_title(slide, text, size=29, color=None, top=Inches(0.92), width=Inches(11.9), on_dark=False):
    color = color or (WHITE if on_dark else INK_PRIMARY)
    add_text(slide, Inches(0.7), top, width, Inches(1.15), text, size=size, color=color,
              bold=True, line_spacing=1.05)

def add_footer(slide, page, on_dark=False):
    line_color = RGBColor(0x2a,0x2a,0x28) if on_dark else GRIDLINE
    add_rect(slide, Inches(0.7), Inches(7.05), Inches(11.93), Pt(1), line_color)
    add_text(slide, Inches(0.7), Inches(7.12), Inches(6), Inches(0.3),
              "NEUROMORPHIC VIO  —  CONFIDENTIAL", size=9,
              color=(INK_MUTED if not on_dark else RGBColor(0x77,0x76,0x70)), letter_spaced=True)
    add_text(slide, Inches(12.0), Inches(7.12), Inches(0.63), Inches(0.3),
              f"{page:02d} / {TOTAL_SLIDES:02d}", size=9,
              color=(INK_MUTED if not on_dark else RGBColor(0x77,0x76,0x70)), align=PP_ALIGN.RIGHT)

def add_source(slide, text, top=Inches(6.62)):
    add_text(slide, Inches(0.7), top, Inches(11.9), Inches(0.35), text, size=9.5,
              color=INK_MUTED, italic=True)

def add_bullets(slide, l, t, w, h, items, size=15.5, color=INK_SECONDARY,
                 lead_color=INK_PRIMARY, marker_color=VIOLET, gap=Pt(12), line_spacing=1.14):
    """items: list of (lead_or_None, rest_text)"""
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    first = True
    for lead, rest in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.line_spacing = line_spacing
        p.space_after = gap
        r0 = p.add_run(); r0.text = "—  "
        r0.font.size = Pt(size); r0.font.bold = True
        r0.font.color.rgb = marker_color; r0.font.name = FONT
        if lead:
            r1 = p.add_run(); r1.text = lead
            r1.font.size = Pt(size); r1.font.bold = True
            r1.font.color.rgb = lead_color; r1.font.name = FONT
        r2 = p.add_run(); r2.text = rest
        r2.font.size = Pt(size); r2.font.bold = False
        r2.font.color.rgb = color; r2.font.name = FONT
    return tb

def add_pic(slide, path, l, t, w=None, h=None):
    return slide.shapes.add_picture(path, l, t, width=w, height=h)

def add_stat_card(slide, l, t, w, h, number, label, number_color=VIOLET, dark=False):
    fill = DARK_CARD if dark else CARD
    add_rect(slide, l, t, w, h, fill, rounded=True, radius=0.10)
    num_top = t + Inches(0.14)
    num_h = Inches(0.5)
    add_text(slide, l + Inches(0.22), num_top, w - Inches(0.44), num_h, number,
              size=26, bold=True, color=number_color, anchor=MSO_ANCHOR.BOTTOM)
    label_top = num_top + num_h + Inches(0.1)
    label_h = (t + h) - label_top - Inches(0.12)
    add_text(slide, l + Inches(0.22), label_top, w - Inches(0.44), label_h, label,
              size=11, color=(CREAM if dark else INK_SECONDARY), anchor=MSO_ANCHOR.TOP, line_spacing=1.1)

def new_slide(dark=False):
    s = prs.slides.add_slide(BLANK)
    add_bg(s, DARK if dark else SURFACE)
    return s

def add_arrow_between(slide, x1, x2, y, color=BASELINE):
    ln = slide.shapes.add_connector(2, x1, y, x2, y)  # 2 = STRAIGHT
    ln.line.color.rgb = color
    ln.line.width = Pt(1.75)
    return ln

# ========================================================================
# SLIDE 1 — TITLE
# ========================================================================
s = new_slide(dark=True)

# abstract spike-train motif, right side (kept clear of the subtitle text block)
spike_x0 = Inches(9.65)
spike_base_y = Inches(5.6)
spikes = [
    (0.00, 0.30, VIOLET), (0.27, 0.75, BLUE), (0.48, 0.25, ORANGE),
    (0.75, 0.95, VIOLET), (0.95, 0.20, BLUE), (1.22, 0.55, ORANGE),
    (1.46, 1.05, VIOLET), (1.68, 0.30, BLUE), (1.93, 0.65, ORANGE),
    (2.20, 0.22, VIOLET), (2.46, 0.85, BLUE), (2.70, 0.35, ORANGE),
    (2.96, 1.0, VIOLET), (3.20, 0.28, BLUE),
]
add_rect(s, spike_x0, spike_base_y, Inches(3.4), Pt(1.5), RGBColor(0x33,0x32,0x30))
for x_off, height, col in spikes:
    bar = add_rect(s, spike_x0 + Inches(x_off), spike_base_y - Inches(height),
                    Inches(0.09), Inches(height), col)

add_kicker(s, "TECHNICAL PARTNERSHIP PITCH", on_dark=True)
add_text(s, Inches(0.7), Inches(2.55), Inches(9.5), Inches(1.6), "NEUROMORPHIC VIO",
          size=54, bold=True, color=WHITE)
add_rect(s, Inches(0.72), Inches(3.55), Inches(1.1), Pt(3.5), VIOLET)
add_text(s, Inches(0.7), Inches(3.85), Inches(9.6), Inches(1.0),
          "Drones that see where GPS can't reach — at a fraction of the power.",
          size=20, color=CREAM, line_spacing=1.2)

add_text(s, Inches(0.7), Inches(6.85), Inches(7), Inches(0.4),
          "Prepared for a potential technical co-founder", size=11.5, color=RGBColor(0x9a,0x98,0x92))
add_text(s, Inches(10.5), Inches(6.85), Inches(2.13), Inches(0.4),
          "July 2026", size=11.5, color=RGBColor(0x9a,0x98,0x92), align=PP_ALIGN.RIGHT)

# ========================================================================
# SLIDE 2 — THE PROBLEM
# ========================================================================
s = new_slide()
add_kicker(s, "01  —  THE PROBLEM")
add_title(s, "GPS-denied navigation is the hard problem\nautonomy hasn't solved", top=Inches(0.95))

add_bullets(s, Inches(0.7), Inches(2.55), Inches(7.55), Inches(3.6), [
    ("Any jammer or tunnel blinds a GPS-only drone: ", "no signal means no position, and no position means no mission."),
    ("Two existing fixes, both wrong for small drones: ", "classical vision is cheap but breaks on low light, motion blur, and texture-less scenes; GPU-class learned vision is robust but needs 5–15W a small airframe can't spare."),
    ("This isn't hypothetical: ", "in April 2026 the U.S. Army paid AeroVironment $17.6M for Red Dragon, a 400km strike drone whose GPS-denied navigation runs on onboard vision and digital scene matching."),
], size=16.5)

add_stat_card(s, Inches(8.65), Inches(2.55), Inches(3.95), Inches(1.7), "400 km",
              "flown GPS-denied — Red Dragon, U.S. Army contract, Apr 2026", number_color=VIOLET)
add_stat_card(s, Inches(8.65), Inches(4.45), Inches(3.95), Inches(1.7), "$3.1B",
              "Pentagon counter-drone budget — the money is already moving", number_color=ORANGE)

add_footer(s, 2)

# ========================================================================
# SLIDE 3 — MARKET PULL
# ========================================================================
s = new_slide()
add_kicker(s, "02  —  WHY THE MARKET IS READY")
add_title(s, "This isn't speculative demand — it's already being funded")

add_pic(s, f"{ASSETS}/market_growth.png", Inches(0.55), Inches(2.35), w=Inches(6.55))

add_bullets(s, Inches(7.55), Inches(2.55), Inches(5.1), Inches(3.9), [
    ("GPS-denied navigation market: ", "$163.1M (2026) → $334.2M (2033), a 9.4% CAGR."),
    ("Defense tech VC funding: ", "$17.9B in 2025 — more than double 2024's $7.3B."),
    ("DARPA OPTIMA program: ", "$78M committed specifically to compute-in-memory accelerators."),
    ("Pentagon counter-drone budget: ", "$3.1B allocated and growing."),
], size=15.5)

add_source(s, "Sources: defense-tech funding reports and GPS-denied navigation market sizing, 2025–2026.")
add_footer(s, 3)

# ========================================================================
# SLIDE 4 — THE GAP
# ========================================================================
s = new_slide()
add_kicker(s, "03  —  THE OPEN GAP")
add_title(s, "Nothing efficient sits between ‘cheap but brittle’\nand ‘accurate but power-hungry’", size=27)

add_pic(s, f"{ASSETS}/power_accuracy_gap.png", Inches(0.45), Inches(2.35), w=Inches(7.15))

add_bullets(s, Inches(7.95), Inches(2.55), Inches(4.7), Inches(3.9), [
    ("Classical VIO ", "(ORB-SLAM3, MIT Navion): milliwatt-class power, but fails on low light, motion blur, texture-less scenes."),
    ("Learned VIO ", "(DPVO, DROID-SLAM): handles the hard cases, but needs 5–15W of GPU — 100–1000x a small drone's budget."),
    ("We scanned every neuromorphic and edge-AI chip on the market ", "— Qualcomm, NVIDIA, Hailo, BrainChip, SynSense, Intel Loihi — none closes this gap for VIO."),
], size=14.5)

add_footer(s, 4)

# ========================================================================
# SLIDE 5 — OUR APPROACH (pipeline diagram)
# ========================================================================
s = new_slide()
add_kicker(s, "04  —  OUR APPROACH")
add_title(s, "Sparse sensing, sparse compute — a spiking front-end,\na classical back-end", size=26)

add_bullets(s, Inches(0.7), Inches(2.15), Inches(11.9), Inches(1.55), [
    ("Event cameras report only pixel changes ", "— 100–1000x less data than a frame camera."),
    ("SNNs compute only when a spike arrives ", "— no wasted cycles on static pixels, the same sparsity all the way through."),
    ("We pair that with a classical EKF back-end ", "— learned flexibility where it helps, guaranteed correctness where it must."),
], size=14.5, gap=Pt(6))

# pipeline boxes
labels = ["Event\nCamera", "SNN Front-End\n(feature / motion\nextraction)",
          "Sparse Feature /\nMotion\nRepresentation", "Classical EKF\nBack-End\n(sensor fusion)",
          "Pose Output\n200Hz+, <5ms"]
colors = [BLUE, VIOLET, INK_SECONDARY, ORANGE, VIOLET]
n = len(labels)
box_w = Inches(2.05); box_h = Inches(1.15)
gap_w = Inches(0.28)
total_w = box_w * n + gap_w * (n - 1)
start_x = int((SW - total_w) / 2)
y = Inches(4.05)
xs = []
for i in range(n):
    x = start_x + i * (box_w + gap_w)
    xs.append(x)
    add_rect(s, x, y, box_w, box_h, CARD, rounded=True, radius=0.12)
    add_rect(s, x, y, Inches(0.07), box_h, colors[i], rounded=False)
    tb = s.shapes.add_textbox(x + Inches(0.16), y, box_w - Inches(0.26), box_h)
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left=0; tf.margin_right=0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT; p.line_spacing = 1.05
    r = p.add_run(); r.text = labels[i]
    r.font.size = Pt(12.5); r.font.bold = True; r.font.color.rgb = INK_PRIMARY; r.font.name = FONT

for i in range(n - 1):
    x1 = xs[i] + box_w
    x2 = xs[i+1]
    add_arrow_between(s, x1, x2, y + box_h/2)

# stat strip
stats = [("<200 mW", "power budget"), ("<5 ms", "pose latency"),
         ("200 Hz+", "output rate"), ("1280×720", "event resolution")]
sc_w = Inches(2.85); sc_h = Inches(0.95); sc_gap = Inches(0.15)
sc_total = sc_w * 4 + sc_gap * 3
sc_x0 = int((SW - sc_total) / 2)
for i, (num, lab) in enumerate(stats):
    x = sc_x0 + i * (sc_w + sc_gap)
    add_stat_card(s, x, Inches(5.55), sc_w, sc_h, num, lab, number_color=[BLUE, VIOLET, ORANGE, VIOLET][i])

add_footer(s, 5)

# ========================================================================
# SLIDE 6 — WHY NOW (3-column)
# ========================================================================
s = new_slide()
add_kicker(s, "05  —  WHY NOW")
add_title(s, "Three things just became true at the same time")

col_w = Inches(3.75); col_gap = Inches(0.25)
col_x0 = Inches(0.7)
cards = [
    ("01", BLUE, "Event cameras shipped", "Prophesee and iniVation sensors are commercially available now — not lab prototypes."),
    ("02", VIOLET, "SNN tooling matured", "snnTorch and SpikingJelly train on commodity GPUs and export to INT8/ONNX — the missing PyTorch-equivalent finally exists."),
    ("03", ORANGE, "A power proof point landed", "TinyDEVO (CVPR 2026) just showed a learned event-VO pipeline running at 86mW on a RISC-V MCU — the sub-500mW gap is closing, right now."),
]
for i, (num, col, head, body) in enumerate(cards):
    x = col_x0 + i * (col_w + col_gap)
    add_rect(s, x, Inches(2.15), col_w, Inches(3.6), CARD, rounded=True, radius=0.06)
    add_text(s, x + Inches(0.28), Inches(2.4), col_w - Inches(0.56), Inches(0.8), num,
              size=38, bold=True, color=col)
    add_text(s, x + Inches(0.28), Inches(3.2), col_w - Inches(0.56), Inches(0.85), head,
              size=17, bold=True, color=INK_PRIMARY, line_spacing=1.05)
    add_text(s, x + Inches(0.28), Inches(4.05), col_w - Inches(0.56), Inches(1.55), body,
              size=13, color=INK_SECONDARY, line_spacing=1.2)

add_rect(s, Inches(0.7), Inches(6.0), Inches(11.93), Pt(1), GRIDLINE)
add_text(s, Inches(0.7), Inches(6.12), Inches(11.9), Inches(0.5),
          "And defense demand is accelerating under all three — this is a closing window, not an open-ended one.",
          size=14, bold=True, color=VIOLET, italic=True)

add_footer(s, 6)

# ========================================================================
# SLIDE 7 — COMPETITIVE LANDSCAPE (table)
# ========================================================================
s = new_slide()
add_kicker(s, "06  —  COMPETITIVE LANDSCAPE")
add_title(s, "We checked every neuromorphic and edge-AI player.\nZero target this gap.", size=25)

rows_data = [
    ("Player", "Power", "Can do full VIO?", "Threat"),
    ("SynSense Speck", "<5 mW", "No — 128×128 resolution ceiling", "Low"),
    ("BrainChip AKD1500", "<300 mW", "No — wrong architecture (counter-drone)", "Low"),
    ("Intel Loihi 3", "~1.2 W", "Research only, targets healthcare/AV", "None"),
    ("Hailo-8 / 15", "1.5–2.5 W", "Partial — CNN only", "Medium"),
    ("Qualcomm RB5 / NVIDIA Orin", "5–15 W", "Yes, full — but that's the power gap", "High — the wedge"),
    ("MIT Navion (academic)", "2 mW", "Yes — proved feasibility, never shipped", "Validates market"),
    ("HYFIX (new, 2026)", "—", "No — RTK/GNSS correction, not vision", "Adjacent"),
]
n_rows = len(rows_data); n_cols = 4
tbl_w = Inches(11.93); tbl_h = Inches(3.55)
graphic_frame = s.shapes.add_table(n_rows, n_cols, Inches(0.7), Inches(2.35), tbl_w, tbl_h)
table = graphic_frame.table
col_widths = [Inches(4.1), Inches(1.7), Inches(4.53), Inches(1.6)]
for i, w in enumerate(col_widths):
    table.columns[i].width = w

for ci in range(n_cols):
    cell = table.cell(0, ci)
    cell.fill.solid(); cell.fill.fore_color.rgb = DARK
    tf = cell.text_frame; tf.margin_left=Inches(0.12); tf.margin_top=Inches(0.06); tf.margin_bottom=Inches(0.06)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT if ci != 3 else PP_ALIGN.CENTER
    r = p.add_run(); r.text = rows_data[0][ci]
    r.font.size = Pt(12.5); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT

threat_colors = {"Low": INK_MUTED, "None": INK_MUTED, "Medium": ORANGE,
                  "High — the wedge": VIOLET, "Validates market": BLUE, "Adjacent": INK_MUTED}
for ri in range(1, n_rows):
    zebra = SURFACE if ri % 2 == 1 else CARD
    for ci in range(n_cols):
        cell = table.cell(ri, ci)
        cell.fill.solid(); cell.fill.fore_color.rgb = zebra
        tf = cell.text_frame; tf.margin_left = Inches(0.12); tf.margin_top = Inches(0.05); tf.margin_bottom = Inches(0.05)
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci != 3 else PP_ALIGN.CENTER
        r = p.add_run(); r.text = rows_data[ri][ci]
        r.font.size = Pt(11.5); r.font.name = FONT
        if ci == 0:
            r.font.bold = True; r.font.color.rgb = INK_PRIMARY
        elif ci == 3:
            r.font.bold = True; r.font.color.rgb = threat_colors.get(rows_data[ri][ci], INK_SECONDARY)
        else:
            r.font.color.rgb = INK_SECONDARY

add_text(s, Inches(0.7), Inches(6.15), Inches(11.9), Inches(0.5),
          "Zero new VIO-accelerator competitors emerged across six months of tracking (Jan→Jul 2026). The gap is wide, and it isn't closing on its own.",
          size=13, bold=True, color=VIOLET, italic=True)

add_footer(s, 7)

# ========================================================================
# SLIDE 8 — TRACTION
# ========================================================================
s = new_slide()
add_kicker(s, "07  —  TRACTION")
add_title(s, "Already in motion — not just a slide deck")

items = [
    ("25+ sources synthesized ", "into technical architecture, competitive landscape, and risk-assessment research."),
    ("Working SNN demos built and running ", "(N-MNIST, DVS Gesture) on snnTorch."),
    ("Classical VIO feature tracker implemented, ", "with an EuRoC benchmark dataset pipeline wired up."),
    ("Hardware path selected and priced: ", "AMD Kria KV260 + Prophesee CCAM5 + BMI088 IMU — ~$800 prototype BOM."),
    ("Architecture grounded in a literature maturity assessment: ", "classical VIO 10/10 proven, SNN ego-motion 4/10, full end-to-end SNN VIO 2/10 — hence a hybrid, not a moonshot."),
]
add_bullets(s, Inches(0.7), Inches(2.45), Inches(11.9), Inches(4.2), items, size=16.5, gap=Pt(16))

add_footer(s, 8)

# ========================================================================
# SLIDE 9 — ROADMAP (timeline)
# ========================================================================
s = new_slide()
add_kicker(s, "08  —  ROADMAP")
add_title(s, "A staged path that de-risks the hardest part last")

phases = [
    ("PHASE 1", "Months 0–3", "Software SNN demos +\nalgorithm development", "status: demos running", BLUE),
    ("PHASE 2", "Months 3–9", "Classical VIO front-end\non FPGA (Kria KV260)", "proven techniques first", VIOLET),
    ("PHASE 3", "Months 9–12", "Event camera integration\n(Prophesee CCAM5, MIPI)", "sensor + hardware fusion", ORANGE),
    ("PHASE 4", "Months 12–30", "SNN front-end replaces\nclassical feature tracking", "full neuromorphic pipeline", VIOLET),
]
n = len(phases)
box_w = Inches(2.7); box_h = Inches(2.55); gap = Inches(0.35)
total_w = box_w * n + gap * (n - 1)
x0 = int((SW - total_w) / 2)
y = Inches(2.65)
xs = []
for i, (tag, months, desc, status, col) in enumerate(phases):
    x = x0 + i * (box_w + gap)
    xs.append(x)
    add_rect(s, x, y, box_w, box_h, CARD, rounded=True, radius=0.08)
    add_rect(s, x, y, box_w, Inches(0.09), col, rounded=False)
    add_text(s, x + Inches(0.22), y + Inches(0.28), box_w - Inches(0.44), Inches(0.35), tag,
              size=12.5, bold=True, color=col, letter_spaced=True)
    add_text(s, x + Inches(0.22), y + Inches(0.62), box_w - Inches(0.44), Inches(0.35), months,
              size=12.5, color=INK_MUTED)
    add_text(s, x + Inches(0.22), y + Inches(1.05), box_w - Inches(0.44), Inches(1.05), desc,
              size=13.5, bold=True, color=INK_PRIMARY, line_spacing=1.15)
    add_text(s, x + Inches(0.22), y + Inches(2.1), box_w - Inches(0.44), Inches(0.4), status,
              size=10.5, italic=True, color=INK_SECONDARY)

for i in range(n - 1):
    add_arrow_between(s, xs[i] + box_w, xs[i+1], y + box_h/2, color=BASELINE)

add_footer(s, 9)

# ========================================================================
# SLIDE 10 — WHY WE NEED A TECHNICAL CO-FOUNDER
# ========================================================================
s = new_slide()
add_kicker(s, "09  —  WHY A TECHNICAL CO-FOUNDER")
add_title(s, "I can design the silicon. I need a partner\nto build the system around it.", size=26)

mid_x = Inches(6.65)
add_rect(s, mid_x, Inches(2.3), Pt(1.5), Inches(4.2), GRIDLINE)

add_text(s, Inches(0.7), Inches(2.35), Inches(5.6), Inches(0.4), "WHAT I BRING", size=13,
          bold=True, color=VIOLET, letter_spaced=True)
add_bullets(s, Inches(0.7), Inches(2.85), Inches(5.6), Inches(3.5), [
    (None, "Logic-design background — FPGA/ASIC architecture, RTL, hardware roadmap."),
    (None, "Deep technical research already done — 25+ sources, architecture decisions grounded in literature."),
    (None, "The compute model for the accelerator and the priced hardware BOM."),
], size=14.5, marker_color=VIOLET, gap=Pt(14))

add_text(s, Inches(7.0), Inches(2.35), Inches(5.6), Inches(0.4), "WHAT'S MISSING", size=13,
          bold=True, color=ORANGE, letter_spaced=True)
add_bullets(s, Inches(7.0), Inches(2.85), Inches(5.6), Inches(3.5), [
    (None, "Production ML engineering — SNN training methodology, dataset pipelines."),
    (None, "Real-time embedded software — MIPI/driver integration, event-stream processing."),
    (None, "The software architecture that turns a chip into a usable product."),
], size=14.5, marker_color=ORANGE, gap=Pt(14))

add_rect(s, Inches(0.7), Inches(6.0), Inches(11.93), Pt(1), GRIDLINE)
add_text(s, Inches(0.7), Inches(6.15), Inches(11.9), Inches(0.6),
          "This isn't “write some scripts.” It's owning half the technical direction of a company\nat its earliest, most malleable point.",
          size=14, bold=True, color=INK_PRIMARY, italic=True, line_spacing=1.2)

add_footer(s, 10)

# ========================================================================
# SLIDE 11 — THE OFFER
# ========================================================================
s = new_slide()
add_kicker(s, "10  —  THE OFFER")
add_title(s, "Technical co-founder — equal footing, from here")

add_bullets(s, Inches(0.7), Inches(2.6), Inches(11.5), Inches(3.8), [
    ("Equity co-founder role, ", "not a contractor and not a later hire."),
    ("Shared ownership of technical direction: ", "the training framework, the software architecture, and the build-vs-buy calls are joint decisions from day one."),
    ("Ground floor on a validated gap ", "in an accelerating market — $163M → $334M by 2033, with defense demand already funding it."),
    ("Specific equity split and terms: ", "open — that's exactly what the next conversation is for."),
], size=17, gap=Pt(18))

add_footer(s, 11)

# ========================================================================
# SLIDE 12 — CLOSING / ASK
# ========================================================================
s = new_slide(dark=True)
add_kicker(s, "LET'S TALK", on_dark=True)
add_title(s, "Let's build the thing that doesn't exist yet", size=32, on_dark=True, top=Inches(1.0))

recap = [("Gap", "proven and wide open"), ("Demand", "funded and accelerating"),
         ("Progress", "real demos, not just research"), ("Roadmap", "staged and de-risked")]
rc_w = Inches(2.85); rc_gap = Inches(0.15)
rc_total = rc_w*4 + rc_gap*3
rc_x0 = int((SW - rc_total)/2)
for i, (head, body) in enumerate(recap):
    x = rc_x0 + i*(rc_w+rc_gap)
    add_stat_card(s, x, Inches(2.35), rc_w, Inches(1.35), head, body, number_color=[BLUE,ORANGE,VIOLET,BLUE][i], dark=True)

add_text(s, Inches(0.7), Inches(4.15), Inches(11.9), Inches(1.3),
          "Next step: let's spend a few sessions scoping the software architecture together — "
          "no commitment, just seeing if this is a problem you want to spend the next few years solving with me.",
          size=17, color=CREAM, line_spacing=1.3)

add_rect(s, Inches(0.7), Inches(5.7), Inches(1.1), Pt(3.5), VIOLET)
add_text(s, Inches(0.7), Inches(5.9), Inches(8), Inches(0.4), "Ofir Hadad", size=15, bold=True, color=WHITE)
add_text(s, Inches(0.7), Inches(6.25), Inches(8), Inches(0.4), "ofir.hadad3@gmail.com", size=13, color=RGBColor(0x9a,0x98,0x92))

add_footer(s, 12, on_dark=True)

prs.save(OUT)
print("Saved:", OUT)
