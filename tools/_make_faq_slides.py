# -*- coding: utf-8 -*-
import openpyxl
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SRC = r'C:\Users\think\Project_v2\chatbot\asset\PERTANYAAN TERKAIT STR DAN UKOM RESERTIFIKASI (Responses)(1).xlsx'
OUT = r'C:\Users\think\Project_v2\chatbot\asset\FAQ_STR_UKOM_Slides.pptx'

wb = openpyxl.load_workbook(SRC)
ws = wb.active

# Data starts at row 5; header at row 4. Col D (4)=Pertanyaan, Col E (5)=Jawaban (Draf)
data = []
for r in range(5, ws.max_row + 1):
    kode = str(ws.cell(r, 1).value or '').strip()
    q = str(ws.cell(r, 4).value or '').strip()
    a = str(ws.cell(r, 5).value or '').strip()
    status = str(ws.cell(r, 7).value or '').strip()
    if q:
        data.append((kode, q, a, status))

print('FAQ ROWS:', len(data))

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
NAVY = RGBColor(0x0B, 0x2A, 0x4A)
ACCENT = RGBColor(0xE8, 0x9B, 0x2C)
LIGHT = RGBColor(0x4A, 0x5A, 0x6A)
QGREY = RGBColor(0x33, 0x3A, 0x42)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
blank = prs.slide_layouts[6]

for i, (kode, q, a, status) in enumerate(data, 1):
    slide = prs.slides.add_slide(blank)

    # Background
    bg = slide.shapes.add_shape(1, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background()
    bg.shadow.inherit = False

    # Top navy bar
    bar = slide.shapes.add_shape(1, 0, 0, SLIDE_W, Inches(0.18))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False

    # --- Top-left: FAQ code (pojok) ---
    tag_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.42), Inches(6.0), Inches(0.5))
    tf = tag_box.text_frame
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = kode
    r1.font.size = Pt(22); r1.font.bold = True; r1.font.color.rgb = NAVY; r1.font.name = 'Calibri'

    # --- Index top-right ---
    idx_box = slide.shapes.add_textbox(Inches(11.0), Inches(0.42), Inches(1.8), Inches(0.55))
    idp = idx_box.text_frame.paragraphs[0]
    idp.alignment = PP_ALIGN.RIGHT
    ir = idp.add_run(); ir.text = f'{i} / {len(data)}'
    ir.font.size = Pt(18); ir.font.bold = True; ir.font.color.rgb = LIGHT; ir.font.name = 'Calibri'

    # --- Pertanyaan: centered, dominant, large (middle of slide) ---
    q_box = slide.shapes.add_textbox(Inches(0.9), Inches(1.4), Inches(11.53), Inches(4.6))
    qf = q_box.text_frame
    qf.word_wrap = True
    qf.vertical_anchor = MSO_ANCHOR.MIDDLE
    qp = qf.paragraphs[0]
    qp.alignment = PP_ALIGN.CENTER
    qp.line_spacing = 1.1
    qr = qp.add_run(); qr.text = q
    qsize = 30 if len(q) > 140 else 40
    qr.font.size = Pt(qsize); qr.font.bold = True; qr.font.color.rgb = QGREY; qr.font.name = 'Calibri'

    # Divider line
    div = slide.shapes.add_shape(1, Inches(2.6), Inches(4.1), Inches(8.1), Inches(0.03))
    div.fill.solid(); div.fill.fore_color.rgb = ACCENT; div.line.fill.background(); div.shadow.inherit = False

    # --- (Jawaban dihapus) — hanya Pertanyaan yang dominan di tengah ---

    # Bottom rule
    brule = slide.shapes.add_shape(1, Inches(0.6), Inches(7.1), Inches(12.13), Inches(0.04))
    brule.fill.solid(); brule.fill.fore_color.rgb = LIGHT; brule.line.fill.background(); brule.shadow.inherit = False

prs.save(OUT)
print('SAVED:', OUT)
print('SLIDES:', len(prs.slides._sldIdLst))
