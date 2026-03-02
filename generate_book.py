#!/usr/bin/env python3
"""
Generate a professional PDF book: "The Quiet Operator"
Uses reportlab with custom typography from available fonts.
"""

import os
import re
import copy
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, NextPageTemplate, Preformatted, Flowable, KeepTogether,
    NotAtTopPageBreak, XPreformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line, Rect

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, ".claude", "skills", "canvas-design", "canvas-fonts")
CONTENT_DIR = os.path.join(BASE_DIR, "content")
CHAPTER_DIR = os.path.join(CONTENT_DIR, "chapters")
FRONT_MATTER = os.path.join(CONTENT_DIR, "A Practical Playbook for Giving an AI a Real.md")
OUTPUT_PDF = os.path.join(CONTENT_DIR, "The_Quiet_Operator.pdf")

# ---------------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------------
ACCENT = HexColor("#0D5C63")
TEXT_PRIMARY = HexColor("#1A1A1A")
TEXT_SECONDARY = HexColor("#4A4A4A")
CODE_BG = HexColor("#F5F5F0")
CODE_BORDER = HexColor("#D9D9D0")
BLOCKQUOTE_BG = HexColor("#F5F9F9")
BLOCKQUOTE_BORDER = HexColor("#0D5C63")
TABLE_HEADER_BG = HexColor("#0D5C63")
TABLE_EVEN_ROW = HexColor("#F5F9F9")
TABLE_ODD_ROW = HexColor("#FFFFFF")
RULE_COLOR = HexColor("#D9D9D0")

# ---------------------------------------------------------------------------
# PAGE DIMENSIONS
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = letter  # 612 x 792
MARGIN_INSIDE = 90
MARGIN_OUTSIDE = 63
MARGIN_TOP = 72
MARGIN_BOTTOM = 72

# ---------------------------------------------------------------------------
# FONT REGISTRATION
# ---------------------------------------------------------------------------
def register_fonts():
    fonts = {
        "YoungSerif": "YoungSerif-Regular.ttf",
        "WorkSans": "WorkSans-Regular.ttf",
        "WorkSans-Bold": "WorkSans-Bold.ttf",
        "WorkSans-Italic": "WorkSans-Italic.ttf",
        "WorkSans-BoldItalic": "WorkSans-BoldItalic.ttf",
        "Lora": "Lora-Regular.ttf",
        "Lora-Bold": "Lora-Bold.ttf",
        "Lora-Italic": "Lora-Italic.ttf",
        "Lora-BoldItalic": "Lora-BoldItalic.ttf",
        "JetBrainsMono": "JetBrainsMono-Regular.ttf",
        "JetBrainsMono-Bold": "JetBrainsMono-Bold.ttf",
        "InstrumentSans": "InstrumentSans-Regular.ttf",
        "InstrumentSans-Bold": "InstrumentSans-Bold.ttf",
        "InstrumentSans-Italic": "InstrumentSans-Italic.ttf",
        "InstrumentSans-BoldItalic": "InstrumentSans-BoldItalic.ttf",
    }
    for name, filename in fonts.items():
        path = os.path.join(FONT_DIR, filename)
        pdfmetrics.registerFont(TTFont(name, path))

    # Register font families for <b>/<i> tag handling
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily("Lora", normal="Lora", bold="Lora-Bold",
                       italic="Lora-Italic", boldItalic="Lora-BoldItalic")
    registerFontFamily("WorkSans", normal="WorkSans", bold="WorkSans-Bold",
                       italic="WorkSans-Italic", boldItalic="WorkSans-BoldItalic")
    registerFontFamily("InstrumentSans", normal="InstrumentSans",
                       bold="InstrumentSans-Bold", italic="InstrumentSans-Italic",
                       boldItalic="InstrumentSans-BoldItalic")
    registerFontFamily("JetBrainsMono", normal="JetBrainsMono",
                       bold="JetBrainsMono-Bold", italic="JetBrainsMono",
                       boldItalic="JetBrainsMono-Bold")


# ---------------------------------------------------------------------------
# PARAGRAPH STYLES
# ---------------------------------------------------------------------------
def build_styles():
    styles = {}

    styles["Body"] = ParagraphStyle(
        "Body", fontName="Lora", fontSize=10.5, leading=14,
        textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY,
        spaceAfter=8, spaceBefore=0,
    )
    styles["BodyFirst"] = ParagraphStyle(
        "BodyFirst", parent=styles["Body"], spaceBefore=0,
    )
    styles["H1"] = ParagraphStyle(
        "H1", fontName="WorkSans-Bold", fontSize=24, leading=28,
        textColor=TEXT_PRIMARY, spaceBefore=0, spaceAfter=6,
    )
    styles["H2"] = ParagraphStyle(
        "H2", fontName="WorkSans-Bold", fontSize=18, leading=22,
        textColor=TEXT_PRIMARY, spaceBefore=24, spaceAfter=8,
    )
    styles["H3"] = ParagraphStyle(
        "H3", fontName="WorkSans-Bold", fontSize=14, leading=18,
        textColor=TEXT_PRIMARY, spaceBefore=18, spaceAfter=6,
    )
    styles["H4"] = ParagraphStyle(
        "H4", fontName="WorkSans-Bold", fontSize=12, leading=16,
        textColor=TEXT_PRIMARY, spaceBefore=14, spaceAfter=4,
    )
    styles["BookTitle"] = ParagraphStyle(
        "BookTitle", fontName="YoungSerif", fontSize=36, leading=42,
        textColor=TEXT_PRIMARY, alignment=TA_CENTER,
        spaceBefore=0, spaceAfter=8,
    )
    styles["Subtitle"] = ParagraphStyle(
        "Subtitle", fontName="WorkSans", fontSize=14, leading=18,
        textColor=TEXT_SECONDARY, alignment=TA_CENTER,
        spaceBefore=0, spaceAfter=6,
    )
    styles["Author"] = ParagraphStyle(
        "Author", fontName="InstrumentSans-Bold", fontSize=12, leading=16,
        textColor=ACCENT, alignment=TA_CENTER,
        spaceBefore=20, spaceAfter=0,
    )
    styles["ChapterNum"] = ParagraphStyle(
        "ChapterNum", fontName="InstrumentSans", fontSize=11, leading=14,
        textColor=ACCENT, spaceBefore=0, spaceAfter=4,
    )
    styles["ChapterTitle"] = ParagraphStyle(
        "ChapterTitle", fontName="WorkSans-Bold", fontSize=26, leading=31,
        textColor=TEXT_PRIMARY, spaceBefore=0, spaceAfter=6,
    )
    styles["TOCTitle"] = ParagraphStyle(
        "TOCTitle", fontName="WorkSans-Bold", fontSize=24, leading=28,
        textColor=TEXT_PRIMARY, spaceBefore=0, spaceAfter=20,
    )
    styles["TOCEntry"] = ParagraphStyle(
        "TOCEntry", fontName="Lora", fontSize=11, leading=20,
        textColor=TEXT_PRIMARY, leftIndent=0,
    )
    styles["BulletItem"] = ParagraphStyle(
        "BulletItem", fontName="Lora", fontSize=10.5, leading=14,
        textColor=TEXT_PRIMARY, alignment=TA_LEFT,
        leftIndent=22, bulletIndent=8,
        spaceBefore=2, spaceAfter=2,
    )
    styles["NumberItem"] = ParagraphStyle(
        "NumberItem", fontName="Lora", fontSize=10.5, leading=14,
        textColor=TEXT_PRIMARY, alignment=TA_LEFT,
        leftIndent=22, bulletIndent=0,
        spaceBefore=2, spaceAfter=2,
    )
    styles["CodeBlock"] = ParagraphStyle(
        "CodeBlock", fontName="JetBrainsMono", fontSize=8.5, leading=11.5,
        textColor=TEXT_PRIMARY, leftIndent=6, rightIndent=6,
        spaceBefore=0, spaceAfter=0,
    )
    styles["CodeLabel"] = ParagraphStyle(
        "CodeLabel", fontName="InstrumentSans", fontSize=7.5, leading=10,
        textColor=TEXT_SECONDARY,
    )
    styles["Blockquote"] = ParagraphStyle(
        "Blockquote", fontName="Lora-Italic", fontSize=10, leading=13.5,
        textColor=TEXT_SECONDARY, leftIndent=4, rightIndent=4,
        spaceBefore=0, spaceAfter=0,
    )
    styles["TableHeader"] = ParagraphStyle(
        "TableHeader", fontName="InstrumentSans-Bold", fontSize=9, leading=12,
        textColor=white,
    )
    styles["TableCell"] = ParagraphStyle(
        "TableCell", fontName="Lora", fontSize=9, leading=12,
        textColor=TEXT_PRIMARY,
    )
    styles["PageHeader"] = ParagraphStyle(
        "PageHeader", fontName="InstrumentSans", fontSize=8, leading=10,
        textColor=TEXT_SECONDARY,
    )
    styles["PageNumber"] = ParagraphStyle(
        "PageNumber", fontName="InstrumentSans", fontSize=9, leading=11,
        textColor=TEXT_SECONDARY,
    )

    return styles


# ---------------------------------------------------------------------------
# CUSTOM FLOWABLES
# ---------------------------------------------------------------------------
class HorizontalRule(Flowable):
    def __init__(self, width, color=RULE_COLOR, thickness=0.75):
        super().__init__()
        self.width = width
        self.color = color
        self.thickness = thickness
        self.height = 16

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return (self.width, self.height)

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        y = self.height / 2
        margin = self.width * 0.15
        self.canv.line(margin, y, self.width - margin, y)


class DecorativeRule(Flowable):
    """Thicker accent-colored rule for chapter openers and title page."""
    def __init__(self, width, color=ACCENT, thickness=2):
        super().__init__()
        self.width = width
        self.color = color
        self.thickness = thickness
        self.height = 12

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return (self.width, self.height)

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        y = self.height / 2
        self.canv.line(0, y, self.width * 0.25, y)


class CodeBlockFlowable(Flowable):
    """Code block with background shading, border, and optional language label.
    Properly splittable across pages."""
    def __init__(self, code_text, language, styles, avail_width, is_continuation=False):
        super().__init__()
        self.code_text = code_text
        self.language = language
        self.styles = styles
        self.avail_width = avail_width
        self.is_continuation = is_continuation
        self._code_lines = code_text.split("\n")
        self._pad = 8
        self._line_height = styles["CodeBlock"].leading
        self._label_height = 14 if language and not is_continuation else 0

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        num_lines = len(self._code_lines)
        self.height = (num_lines * self._line_height +
                       self._label_height + 2 * self._pad)
        return (self.width, self.height)

    def split(self, availWidth, availHeight):
        """Split the code block if it doesn't fit."""
        self.wrap(availWidth, availHeight)
        if self.height <= availHeight:
            return [self]

        # Calculate how many lines fit
        usable = availHeight - self._label_height - 2 * self._pad
        lines_that_fit = int(usable / self._line_height)

        # If not even 1 line fits, tell reportlab to defer to next page
        if lines_that_fit < 1:
            return []

        if lines_that_fit >= len(self._code_lines):
            return [self]

        first_text = "\n".join(self._code_lines[:lines_that_fit])
        rest_text = "\n".join(self._code_lines[lines_that_fit:])

        first = CodeBlockFlowable(first_text, self.language, self.styles,
                                  self.avail_width, is_continuation=False)
        second = CodeBlockFlowable(rest_text, "", self.styles,
                                   self.avail_width, is_continuation=True)
        return [first, second]

    def draw(self):
        canv = self.canv
        w = self.width
        h = self.height

        # Background
        canv.setFillColor(CODE_BG)
        canv.setStrokeColor(CODE_BORDER)
        canv.setLineWidth(0.5)
        canv.roundRect(0, 0, w, h, 4, fill=1, stroke=1)

        # Language label
        y = h - self._pad
        if self._label_height > 0:
            canv.setFont("InstrumentSans", 7.5)
            canv.setFillColor(TEXT_SECONDARY)
            canv.drawString(self._pad, y - 8, self.language)
            y -= self._label_height

        # Code lines
        canv.setFont("JetBrainsMono", 8.5)
        canv.setFillColor(TEXT_PRIMARY)
        for line in self._code_lines:
            y -= self._line_height
            canv.drawString(self._pad, y + 3, line[:120])


class BlockquoteFlowable(Flowable):
    """Blockquote with teal left border and faint background."""
    def __init__(self, text, styles, avail_width):
        super().__init__()
        self.text = text
        self.styles = styles
        self.avail_width = avail_width
        self._built = None

    def _build_table(self, availWidth):
        para = Paragraph(self.text, self.styles["Blockquote"])
        inner_w = availWidth - 20
        tbl = Table([[para]], colWidths=[inner_w])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BLOCKQUOTE_BG),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBEFOREDECAY", (0, 0), (0, -1), 0),
            ("LINEBEFORE", (0, 0), (0, -1), 3, BLOCKQUOTE_BORDER),
        ]))
        return tbl

    def wrap(self, availWidth, availHeight):
        self._built = self._build_table(availWidth)
        w, h = self._built.wrap(availWidth, availHeight)
        self.width = w
        self.height = h
        return (w, h)

    def split(self, availWidth, availHeight):
        if self._built is None:
            self._built = self._build_table(availWidth)
        return self._built.split(availWidth, availHeight)

    def draw(self):
        if self._built:
            self._built.drawOn(self.canv, 0, 0)


# ---------------------------------------------------------------------------
# DOCUMENT TEMPLATE
# ---------------------------------------------------------------------------
class BookDocTemplate(BaseDocTemplate):
    """Custom template that tracks chapter titles for headers."""

    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.current_chapter = ""
        self.chapter_page = False  # True on chapter opener pages
        self.book_title = "The Quiet Operator"
        self.page_number_offset = 0  # for front matter

    def afterFlowable(self, flowable):
        """Track chapter titles and register TOC entries."""
        if hasattr(flowable, '_is_chapter_title'):
            self.current_chapter = flowable._chapter_title_text
            self.chapter_page = True
        if hasattr(flowable, '_toc_entry'):
            level, text, key = flowable._toc_entry
            # Add a bookmark destination so TOC links resolve
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (level, text, self.page, key))


def make_odd_page_frame():
    """Right-hand page: larger left (inside) margin."""
    return Frame(
        MARGIN_INSIDE, MARGIN_BOTTOM,
        PAGE_W - MARGIN_INSIDE - MARGIN_OUTSIDE,
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        id="odd",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )

def make_even_page_frame():
    """Left-hand page: larger right (inside) margin."""
    return Frame(
        MARGIN_OUTSIDE, MARGIN_BOTTOM,
        PAGE_W - MARGIN_INSIDE - MARGIN_OUTSIDE,
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        id="even",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )

def make_chapter_frame():
    """Chapter opener page — no header."""
    return Frame(
        MARGIN_INSIDE, MARGIN_BOTTOM,
        PAGE_W - MARGIN_INSIDE - MARGIN_OUTSIDE,
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        id="chapter",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )

def make_title_frame():
    """Full page for title."""
    return Frame(
        MARGIN_OUTSIDE, MARGIN_BOTTOM,
        PAGE_W - 2 * MARGIN_OUTSIDE,
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        id="title",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )


def header_footer_normal(canvas, doc):
    """Draw headers and footers on normal (non-chapter) pages."""
    canvas.saveState()
    page_num = canvas.getPageNumber()
    is_odd = (page_num % 2 == 1)
    content_width = PAGE_W - MARGIN_INSIDE - MARGIN_OUTSIDE

    # Page number
    canvas.setFont("InstrumentSans", 9)
    canvas.setFillColor(TEXT_SECONDARY)
    num_text = str(page_num)
    if is_odd:
        x_num = PAGE_W - MARGIN_OUTSIDE
        canvas.drawRightString(x_num, MARGIN_BOTTOM - 24, num_text)
    else:
        x_num = MARGIN_OUTSIDE
        canvas.drawString(x_num, MARGIN_BOTTOM - 24, num_text)

    # Header text
    canvas.setFont("InstrumentSans", 8)
    canvas.setFillColor(TEXT_SECONDARY)
    if is_odd and doc.current_chapter:
        # Chapter title on odd pages — right-aligned
        x_start = MARGIN_INSIDE
        canvas.drawString(x_start, PAGE_H - MARGIN_TOP + 16, doc.current_chapter.upper())
    elif not is_odd:
        # Book title on even pages — left-aligned
        x_start = MARGIN_OUTSIDE
        canvas.drawString(x_start, PAGE_H - MARGIN_TOP + 16, doc.book_title.upper())

    # Thin rule below header
    canvas.setStrokeColor(RULE_COLOR)
    canvas.setLineWidth(0.4)
    if is_odd:
        canvas.line(MARGIN_INSIDE, PAGE_H - MARGIN_TOP + 10,
                    PAGE_W - MARGIN_OUTSIDE, PAGE_H - MARGIN_TOP + 10)
    else:
        canvas.line(MARGIN_OUTSIDE, PAGE_H - MARGIN_TOP + 10,
                    PAGE_W - MARGIN_INSIDE, PAGE_H - MARGIN_TOP + 10)

    canvas.restoreState()


def header_footer_chapter(canvas, doc):
    """Chapter opener pages: no header, just page number."""
    canvas.saveState()
    page_num = canvas.getPageNumber()
    canvas.setFont("InstrumentSans", 9)
    canvas.setFillColor(TEXT_SECONDARY)
    # Page number centered on chapter pages
    canvas.drawCentredString(PAGE_W / 2, MARGIN_BOTTOM - 24, str(page_num))
    doc.chapter_page = False
    canvas.restoreState()


def header_footer_blank(canvas, doc):
    """Title and front matter pages: no header/footer."""
    pass


def build_templates():
    """Create page templates."""
    return [
        PageTemplate(id="title", frames=[make_title_frame()],
                     onPage=header_footer_blank),
        PageTemplate(id="front", frames=[make_even_page_frame()],
                     onPage=header_footer_blank),
        PageTemplate(id="chapter", frames=[make_chapter_frame()],
                     onPage=header_footer_chapter),
        PageTemplate(id="normal_odd", frames=[make_odd_page_frame()],
                     onPage=header_footer_normal),
        PageTemplate(id="normal_even", frames=[make_even_page_frame()],
                     onPage=header_footer_normal),
    ]


# ---------------------------------------------------------------------------
# INLINE MARKDOWN → XML MARKUP
# ---------------------------------------------------------------------------
def xml_escape(text):
    """Escape XML special chars."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def process_inline(text):
    """Convert inline markdown to reportlab XML tags."""
    # Escape XML first
    text = xml_escape(text)

    # Inline code (`code`) — do this first to protect from further processing
    code_spans = {}
    counter = [0]
    def replace_code(m):
        key = f"\x00CODE{counter[0]}\x00"
        code_spans[key] = f'<font face="JetBrainsMono" size="8.5" color="#4A4A4A">{m.group(1)}</font>'
        counter[0] += 1
        return key
    text = re.sub(r'`([^`]+)`', replace_code, text)

    # Bold + italic (***text*** or ___text___)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic (*text* or _text_ — but not inside words)
    text = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!\w)_([^_]+?)_(?!\w)', r'<i>\1</i>', text)

    # Em dash
    text = text.replace(" -- ", " \u2014 ")
    text = text.replace("--", "\u2014")

    # Restore code spans
    for key, val in code_spans.items():
        text = text.replace(key, val)

    # Strip markdown links to just text: [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    return text


# ---------------------------------------------------------------------------
# MARKDOWN TABLE PARSER
# ---------------------------------------------------------------------------
def parse_md_table(lines, styles):
    """Parse markdown pipe table lines into a reportlab Table flowable."""
    rows = []
    for line in lines:
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        cells = [c.strip() for c in line.split("|")]
        rows.append(cells)

    if len(rows) < 2:
        return None

    # Remove separator row (row index 1, which has ---/:-: etc.)
    header_row = rows[0]
    data_rows = rows[2:]  # skip separator

    num_cols = len(header_row)
    avail_width = PAGE_W - MARGIN_INSIDE - MARGIN_OUTSIDE - 4
    col_width = avail_width / num_cols

    table_data = []
    # Header
    hdr = [Paragraph(process_inline(c), styles["TableHeader"]) for c in header_row]
    table_data.append(hdr)
    # Data
    for row in data_rows:
        cells = row + [""] * (num_cols - len(row))  # pad if needed
        r = [Paragraph(process_inline(c), styles["TableCell"]) for c in cells[:num_cols]]
        table_data.append(r)

    tbl = Table(table_data, colWidths=[col_width] * num_cols)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "InstrumentSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.4, CODE_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]
    # Zebra striping
    for i in range(1, len(table_data)):
        bg = TABLE_EVEN_ROW if i % 2 == 0 else TABLE_ODD_ROW
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

    tbl.setStyle(TableStyle(style_cmds))
    return tbl


# ---------------------------------------------------------------------------
# MARKDOWN PARSER — STATE MACHINE
# ---------------------------------------------------------------------------
def parse_chapter_markdown(text, styles, chapter_num=None, chapter_title=None):
    """Parse markdown text into a list of reportlab flowables."""
    lines = text.split("\n")
    flowables = []
    avail_width = PAGE_W - MARGIN_INSIDE - MARGIN_OUTSIDE

    i = 0
    in_code_block = False
    code_lines = []
    code_lang = ""
    in_table = False
    table_lines = []
    in_blockquote = False
    blockquote_lines = []
    in_list = False
    list_type = None  # "bullet" or "number"
    list_items = []
    skip_initial_heading = (chapter_num is not None)  # skip the # Chapter N: heading

    def flush_blockquote():
        nonlocal blockquote_lines, in_blockquote
        if blockquote_lines:
            text = " ".join(blockquote_lines)
            text = process_inline(text)
            bq = BlockquoteFlowable(text, styles, avail_width)
            flowables.append(Spacer(1, 6))
            flowables.append(bq)
            flowables.append(Spacer(1, 6))
            blockquote_lines = []
        in_blockquote = False

    def flush_table():
        nonlocal table_lines, in_table
        if table_lines:
            tbl = parse_md_table(table_lines, styles)
            if tbl:
                flowables.append(Spacer(1, 6))
                flowables.append(tbl)
                flowables.append(Spacer(1, 6))
            table_lines = []
        in_table = False

    def flush_list():
        nonlocal list_items, in_list, list_type
        if list_items:
            for item in list_items:
                flowables.append(item)
            flowables.append(Spacer(1, 4))
            list_items = []
        in_list = False
        list_type = None

    while i < len(lines):
        line = lines[i]

        # --- Code fence ---
        if line.strip().startswith("```"):
            if in_code_block:
                # End code block
                code_text = "\n".join(code_lines)
                cb = CodeBlockFlowable(code_text, code_lang, styles, avail_width)
                flowables.append(Spacer(1, 6))
                flowables.append(cb)
                flowables.append(Spacer(1, 6))
                in_code_block = False
                code_lines = []
                code_lang = ""
            else:
                # Flush any open blocks
                if in_blockquote:
                    flush_blockquote()
                if in_table:
                    flush_table()
                if in_list:
                    flush_list()
                # Start code block
                in_code_block = True
                lang = line.strip()[3:].strip()
                code_lang = lang if lang else ""
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        stripped = line.strip()

        # --- Blank line ---
        if not stripped:
            if in_blockquote:
                flush_blockquote()
            if in_table:
                flush_table()
            if in_list:
                flush_list()
            i += 1
            continue

        # --- Table detection ---
        if stripped.startswith("|") and "|" in stripped[1:]:
            if not in_table:
                if in_blockquote:
                    flush_blockquote()
                if in_list:
                    flush_list()
                in_table = True
                table_lines = []
            table_lines.append(stripped)
            i += 1
            continue
        elif in_table:
            flush_table()

        # --- Blockquote ---
        if stripped.startswith(">"):
            if in_list:
                flush_list()
            content = stripped[1:].strip()
            # Remove leading > for nested quotes
            while content.startswith(">"):
                content = content[1:].strip()
            in_blockquote = True
            blockquote_lines.append(content)
            i += 1
            continue
        elif in_blockquote:
            flush_blockquote()

        # --- Horizontal rule ---
        if stripped in ("---", "***", "___") and not skip_initial_heading:
            if in_list:
                flush_list()
            flowables.append(HorizontalRule(avail_width))
            i += 1
            continue
        elif stripped in ("---", "***", "___") and skip_initial_heading:
            # Skip the initial --- after the chapter heading
            i += 1
            # After the initial HR, stop skipping
            continue

        # --- Headings ---
        heading_match = re.match(r'^(#{1,4})\s+(.*)', stripped)
        if heading_match:
            if in_list:
                flush_list()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            # Check if this is the chapter heading (# Chapter N:)
            chapter_match = re.match(r'^Chapter\s+(\d+):\s*(.*)', heading_text)
            if level == 1 and chapter_match and skip_initial_heading:
                # We already handle this via the chapter opener
                skip_initial_heading = False
                i += 1
                continue

            style_key = f"H{level}"
            text = process_inline(heading_text)
            para = Paragraph(text, styles[style_key])

            # Register TOC entry for H1 and H2
            if level <= 2:
                anchor_key = f"ch{chapter_num or 0}_h{level}_{i}"
                para._toc_entry = (level - 1, heading_text, anchor_key)

            # Keep heading with following content
            flowables.append(KeepTogether([Spacer(1, styles[style_key].spaceBefore), para]))
            i += 1
            continue

        # --- Bullet list ---
        bullet_match = re.match(r'^[\-\*]\s+(.*)', stripped)
        if bullet_match:
            content = bullet_match.group(1)
            text = process_inline(content)
            bullet_char = f'<font color="{ACCENT.hexval()}">&#8226;</font>'
            para = Paragraph(f"{bullet_char}  {text}", styles["BulletItem"])
            if not in_list or list_type != "bullet":
                if in_list:
                    flush_list()
                in_list = True
                list_type = "bullet"
            list_items.append(para)
            i += 1
            continue

        # --- Numbered list ---
        number_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if number_match:
            num = number_match.group(1)
            content = number_match.group(2)
            text = process_inline(content)
            num_str = f'<font color="{ACCENT.hexval()}"><b>{num}.</b></font>'
            para = Paragraph(f"{num_str}  {text}", styles["NumberItem"])
            if not in_list or list_type != "number":
                if in_list:
                    flush_list()
                in_list = True
                list_type = "number"
            list_items.append(para)
            i += 1
            continue

        # --- If we were in a list and hit a non-list line ---
        if in_list:
            # Check if this is a continuation (indented line)
            if line.startswith("  ") and list_items:
                # Continuation of previous list item — append to last item
                prev_text = list_items[-1].text
                continuation = process_inline(stripped)
                # We can't easily append, so just add as body paragraph
                flush_list()
                para = Paragraph(continuation, styles["Body"])
                flowables.append(para)
                i += 1
                continue
            else:
                flush_list()

        # --- Normal paragraph ---
        text = process_inline(stripped)
        if text:
            para = Paragraph(text, styles["Body"])
            flowables.append(para)
        i += 1

    # Flush any remaining blocks
    if in_code_block and code_lines:
        code_text = "\n".join(code_lines)
        cb = CodeBlockFlowable(code_text, code_lang, styles, avail_width)
        flowables.append(cb)
    if in_blockquote:
        flush_blockquote()
    if in_table:
        flush_table()
    if in_list:
        flush_list()

    return flowables


# ---------------------------------------------------------------------------
# TOC
# ---------------------------------------------------------------------------
class CustomTOC(TableOfContents):
    """Table of contents with dot leaders."""

    def __init__(self, styles):
        super().__init__()
        self.levelStyles = [
            ParagraphStyle(
                "TOCLevel0", fontName="WorkSans-Bold", fontSize=11, leading=22,
                textColor=TEXT_PRIMARY, leftIndent=0,
                spaceBefore=6, spaceAfter=2,
            ),
            ParagraphStyle(
                "TOCLevel1", fontName="Lora", fontSize=10, leading=18,
                textColor=TEXT_SECONDARY, leftIndent=20,
                spaceBefore=1, spaceAfter=1,
            ),
        ]


# ---------------------------------------------------------------------------
# CHAPTER OPENER
# ---------------------------------------------------------------------------
def make_chapter_opener(chapter_num, chapter_title, styles):
    """Create flowables for a chapter opener page."""
    flowables = []
    flowables.append(Spacer(1, 120))  # Push down from top

    # Chapter number
    num_text = f"CHAPTER {chapter_num}"
    num_para = Paragraph(num_text, styles["ChapterNum"])
    flowables.append(num_para)
    flowables.append(Spacer(1, 8))

    # Chapter title
    title_para = Paragraph(process_inline(chapter_title), styles["ChapterTitle"])
    title_para._is_chapter_title = True
    title_para._chapter_title_text = f"Chapter {chapter_num}: {chapter_title}"
    flowables.append(title_para)
    flowables.append(Spacer(1, 12))

    # Decorative rule
    avail_width = PAGE_W - MARGIN_INSIDE - MARGIN_OUTSIDE
    flowables.append(DecorativeRule(avail_width))
    flowables.append(Spacer(1, 24))

    return flowables


# ---------------------------------------------------------------------------
# TITLE PAGE
# ---------------------------------------------------------------------------
def make_title_page(styles):
    """Create flowables for the title page."""
    flowables = []
    flowables.append(NextPageTemplate("title"))
    flowables.append(Spacer(1, 180))

    # Title
    flowables.append(Paragraph("The Quiet Operator", styles["BookTitle"]))
    flowables.append(Spacer(1, 12))

    # Subtitle
    flowables.append(Paragraph(
        "A Playbook for Building AI Businesses That Actually Make Money",
        styles["Subtitle"]
    ))
    flowables.append(Spacer(1, 16))

    # Decorative rule centered
    avail_width = PAGE_W - 2 * MARGIN_OUTSIDE
    rule = DecorativeRule(avail_width, thickness=2)
    flowables.append(rule)
    flowables.append(Spacer(1, 24))

    # Author
    flowables.append(Paragraph("FELIX CRAFT", styles["Author"]))

    return flowables


# ---------------------------------------------------------------------------
# AUTHOR'S NOTE
# ---------------------------------------------------------------------------
def make_authors_note(front_matter_text, styles):
    """Extract and render the Author's Note section."""
    flowables = []
    flowables.append(NextPageTemplate("front"))
    flowables.append(PageBreak())
    flowables.append(Spacer(1, 40))

    # Title
    flowables.append(Paragraph("A Note From Your Author", styles["H1"]))
    flowables.append(Spacer(1, 8))
    avail_width = PAGE_W - MARGIN_INSIDE - MARGIN_OUTSIDE
    flowables.append(DecorativeRule(avail_width))
    flowables.append(Spacer(1, 16))

    # Extract author's note text
    lines = front_matter_text.split("\n")
    in_note = False
    note_lines = []
    for line in lines:
        if "# A Note From Your Author" in line:
            in_note = True
            continue
        if in_note:
            if line.startswith("# ") and "Table of Contents" not in line:
                continue
            if "# Table of Contents" in line:
                break
            note_lines.append(line)

    note_text = "\n".join(note_lines).strip()
    note_flowables = parse_chapter_markdown(note_text, styles)
    flowables.extend(note_flowables)

    return flowables


# ---------------------------------------------------------------------------
# TOC PAGE
# ---------------------------------------------------------------------------
def make_toc_page(styles, toc):
    """Create the table of contents page."""
    flowables = []
    flowables.append(NextPageTemplate("front"))
    flowables.append(PageBreak())
    flowables.append(Spacer(1, 40))
    flowables.append(Paragraph("Table of Contents", styles["TOCTitle"]))
    flowables.append(toc)
    return flowables


# ---------------------------------------------------------------------------
# CHAPTER LOADING
# ---------------------------------------------------------------------------
def load_chapters():
    """Load all chapter files and extract chapter number/title."""
    chapters = []
    for ch_num in range(1, 10):
        path = os.path.join(CHAPTER_DIR, f"chapter-{ch_num}.md")
        if not os.path.exists(path):
            print(f"Warning: {path} not found, skipping")
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        # Extract chapter title from first line
        first_line = text.strip().split("\n")[0]
        match = re.match(r'^#\s+Chapter\s+(\d+):\s*(.*)', first_line)
        if match:
            title = match.group(2).strip()
        else:
            title = first_line.lstrip("#").strip()

        chapters.append({
            "num": ch_num,
            "title": title,
            "text": text,
        })
    return chapters


# ---------------------------------------------------------------------------
# ALTERNATING PAGE TEMPLATE HANDLER
# ---------------------------------------------------------------------------
class AlternatingPageTemplate(Flowable):
    """Inserts the correct page template based on odd/even page."""
    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.width = 0
        self.height = 0

    def draw(self):
        pass

    def wrap(self, availWidth, availHeight):
        return (0, 0)


# ---------------------------------------------------------------------------
# BUILD THE PDF
# ---------------------------------------------------------------------------
def build_book():
    """Main function: assemble and build the book PDF."""
    register_fonts()
    styles = build_styles()

    # Create document
    doc = BookDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=MARGIN_OUTSIDE,
        rightMargin=MARGIN_OUTSIDE,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
    )
    doc.addPageTemplates(build_templates())

    # Create TOC
    toc = CustomTOC(styles)

    story = []

    # --- Title Page ---
    print("Building title page...")
    story.extend(make_title_page(styles))

    # --- Author's Note ---
    print("Building author's note...")
    with open(FRONT_MATTER, "r", encoding="utf-8") as f:
        front_text = f.read()
    story.extend(make_authors_note(front_text, styles))

    # --- Table of Contents ---
    print("Building table of contents...")
    story.extend(make_toc_page(styles, toc))

    # --- Chapters ---
    chapters = load_chapters()
    for ch in chapters:
        print(f"Building Chapter {ch['num']}: {ch['title']}...")

        # Chapter opener on new page
        story.append(NextPageTemplate("chapter"))
        story.append(PageBreak())

        opener = make_chapter_opener(ch["num"], ch["title"], styles)

        # Register TOC entry on the chapter title para
        for f in opener:
            if hasattr(f, '_is_chapter_title'):
                anchor_key = f"chapter_{ch['num']}"
                f._toc_entry = (0, f"Chapter {ch['num']}: {ch['title']}", anchor_key)

        story.extend(opener)

        # Switch to normal template after opener content
        story.append(NextPageTemplate("normal_odd"))

        # Parse chapter body
        body = parse_chapter_markdown(
            ch["text"], styles,
            chapter_num=ch["num"],
            chapter_title=ch["title"],
        )
        story.extend(body)

    # --- Build with multiBuild for TOC resolution ---
    print("Rendering PDF (multi-pass for TOC)...")
    doc.multiBuild(story)

    file_size = os.path.getsize(OUTPUT_PDF)
    print(f"\nDone! PDF generated: {OUTPUT_PDF}")
    print(f"File size: {file_size / 1024:.0f} KB")


if __name__ == "__main__":
    build_book()
