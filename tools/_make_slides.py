# -*- coding: utf-8 -*-
import openpyxl
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SRC = r'C:\Users\think\Project_v2\chatbot\asset\PERTANYAAN TERKAIT STR DAN UKOM RESERTIFIKASI (Responses).xlsx'
OUT = r'C:\Users\think\Project_v2\chatbot\asset\Pertanyaan_STR_UKOM_Slides.pptx'

wb = openpyxl.load_workbook(SRC)
ws = wb.active
data = []
for r in range(2, ws.max_row + 1):
    nama = str(ws.cell(r, 3).value or '').strip()
    tanya = str(ws.cell(r, 5).value or '').strip()
    if nama or tanya:
        data.append((nama, tanya))

print('ROWS:', len(data))

# --- Design ---
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
NAVY = RGBColor(0x0B, 0x2A, 0x4A)   # dark professional blue
ACCENT = RGBColor(0xE8, 0x9B, 0x2C) # warm accent (name + index)
LIGHT = RGBColor(0x5B, 0x6B, 0x7B)  # muted grey-blue for question
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
blank = prs.slide_layouts[6]

for i, (nama, tanya) in enumerate(data, 1):
    slide = prs.slides.add_slide(blank)

    # Background: solid white via a full-bleed rectangle
    bg = slide.shapes.add_shape(1, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background()
    bg.shadow.inherit = False

    # Top accent bar (thin) for visual anchor
    bar = slide.shapes.add_shape(1, 0, 0, SLIDE_W, Inches(0.18))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False

    # --- Name in top-left corner ---
    name_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.45), Inches(9.0), Inches(0.8))
    nf = name_box.text_frame
    nf.word_wrap = True
    np_ = nf.paragraphs[0]
    nrun = np_.add_run()
    nrun.text = nama if nama else 'Sejawat'
    nrun.font.size = Pt(28)
    nrun.font.bold = True
    nrun.font.color.rgb = ACCENT
    nrun.font.name = 'Calibri'

    # --- Question index chip top-right ---
    idx_box = slide.shapes.add_textbox(Inches(11.0), Inches(0.45), Inches(1.8), Inches(0.7))
    idxf = idx_box.text_frame
    idp = idxf.paragraphs[0]
    idp.alignment = PP_ALIGN.RIGHT
    irun = idp.add_run()
    irun.text = f'{i} / {len(data)}'
    irun.font.size = Pt(20)
    irun.font.bold = True
    irun.font.color.rgb = NAVY
    irun.font.name = 'Calibri'

    # --- Question centered, dominant, large ---
    q_box = slide.shapes.add_textbox(Inches(0.9), Inches(1.7), Inches(11.53), Inches(5.2))
    qf = q_box.text_frame
    qf.word_wrap = True
    qf.vertical_anchor = MSO_ANCHOR.MIDDLE
    qpara = qf.paragraphs[0]
    qpara.alignment = PP_ALIGN.CENTER
    qpara.line_spacing = 1.0
    qrun = qpara.add_run()
    qrun.text = tanya if tanya else '—'
    qrun.font.size = Pt(40)
    qrun.font.color.rgb = NAVY
    qrun.font.name = 'Calibri'

    # Shrink-to-fit if question is long: estimate overflow and scale font
    qchars = len(tanya)
    if qchars > 180:
        qrun.font.size = Pt(30)
    elif qchars > 120:
        qrun.font.size = Pt(34)
    elif qchars > 80:
        qrun.font.size = Pt(38)

    # Bottom accent rule
    brule = slide.shapes.add_shape(1, Inches(0.6), Inches(7.1), Inches(12.13), Inches(0.04))
    brule.fill.solid()
    brule.fill.fore_color.rgb = LIGHT
    brule.line.fill.background()
    brule.shadow.inherit = False

prs.save(OUT)
print('SAVED:', OUT)
print('SLIDES:', len(prs.slides._sldIdLst))
