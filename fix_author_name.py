"""Replace 'FELIX CRAFT' with 'AVA CRAFT' on page 1 of both PDFs."""

import io
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

# Register fonts
pdfmetrics.registerFont(TTFont('InstrumentSans-Bold',
    '.claude/skills/canvas-design/canvas-fonts/InstrumentSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Prompt-Bold',
    'content/fonts/th/Prompt-Bold.ttf'))

PAGE_W, PAGE_H = letter  # 612 x 792
TEXT_COLOR = HexColor('#0D5C63')
FONT_SIZE = 12
NEW_NAME = "AVA CRAFT"

pdfs = [
    {
        'path': 'landing-page/The_Quiet_Operator.pdf',
        'font': 'InstrumentSans-Bold',
    },
    {
        'path': 'landing-page/The_Quiet_Operator_TH.pdf',
        'font': 'Prompt-Bold',
    },
]

for info in pdfs:
    path = info['path']
    font_name = info['font']
    print(f"Processing {path} ...")

    # Create overlay
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    # White rectangle to cover old text (centered, around y=207)
    rect_w = 200
    rect_h = 20
    rect_x = (PAGE_W - rect_w) / 2
    rect_y = 207 - 5  # a bit below baseline
    c.setFillColor(white)
    c.setStrokeColor(white)
    c.rect(rect_x, rect_y, rect_w, rect_h, fill=1, stroke=1)

    # Draw new text centered
    c.setFont(font_name, FONT_SIZE)
    c.setFillColor(TEXT_COLOR)
    text_w = pdfmetrics.stringWidth(NEW_NAME, font_name, FONT_SIZE)
    text_x = (PAGE_W - text_w) / 2
    text_y = 207
    c.drawString(text_x, text_y, NEW_NAME)

    c.save()
    buf.seek(0)

    # Merge overlay onto page 1
    overlay_pdf = PdfReader(buf)
    overlay_page = overlay_pdf.pages[0]

    reader = PdfReader(path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if i == 0:
            page.merge_page(overlay_page)
        writer.add_page(page)

    with open(path, 'wb') as f:
        writer.write(f)

    print(f"  Done: {path}")

print("\nAll PDFs updated.")
