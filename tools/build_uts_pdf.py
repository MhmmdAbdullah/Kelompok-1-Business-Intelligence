"""Build the single readable UTS PDF snapshot for Kelompok 1."""

from __future__ import annotations

import html
import re
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "UTS_Kelompok_1_Desain_BI.pdf"

NAVY = colors.HexColor("#12355B")
BLUE = colors.HexColor("#2B6F97")
SKY = colors.HexColor("#E8F2F8")
INK = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#52606D")
LINE = colors.HexColor("#CBD5E1")
PAPER = colors.HexColor("#F7FAFC")


def register_fonts() -> None:
    base = Path("/System/Library/Fonts/Supplemental")
    pdfmetrics.registerFont(TTFont("Arial", str(base / "Arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(base / "Arial Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Italic", str(base / "Arial Italic.ttf")))


register_fonts()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    "DocTitle", fontName="Arial-Bold", fontSize=26, leading=31, textColor=NAVY,
    alignment=TA_CENTER, spaceAfter=14,
))
styles.add(ParagraphStyle(
    "DocSubtitle", fontName="Arial", fontSize=12, leading=17, textColor=BLUE,
    alignment=TA_CENTER, spaceAfter=8,
))
styles.add(ParagraphStyle(
    "H1x", fontName="Arial-Bold", fontSize=17, leading=21, textColor=NAVY,
    spaceBefore=10, spaceAfter=8, keepWithNext=True,
))
styles.add(ParagraphStyle(
    "H2x", fontName="Arial-Bold", fontSize=13, leading=16, textColor=BLUE,
    spaceBefore=8, spaceAfter=5, keepWithNext=True,
))
styles.add(ParagraphStyle(
    "H3x", fontName="Arial-Bold", fontSize=10.5, leading=13, textColor=INK,
    spaceBefore=6, spaceAfter=4, keepWithNext=True,
))
styles.add(ParagraphStyle(
    "Bodyx", fontName="Arial", fontSize=8.6, leading=12.2, textColor=INK,
    spaceAfter=5,
))
styles.add(ParagraphStyle(
    "Smallx", fontName="Arial", fontSize=7.4, leading=10, textColor=MUTED,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    "Bulletx", parent=styles["Bodyx"], leftIndent=13, firstLineIndent=-7,
    bulletIndent=3, spaceAfter=3,
))
styles.add(ParagraphStyle(
    "Codex", fontName="Courier", fontSize=6.25, leading=8.2, textColor=INK,
    backColor=PAPER, borderColor=LINE, borderWidth=0.5, borderPadding=6,
    spaceBefore=3, spaceAfter=7,
))
styles.add(ParagraphStyle(
    "FileLabel", fontName="Arial-Bold", fontSize=8, leading=10, textColor=colors.white,
    backColor=BLUE, borderPadding=5, spaceBefore=8, spaceAfter=5,
))


def inline_markup(text: str) -> str:
    out = html.escape(text.strip())
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', out)
    return out


def wrapped_code(text: str, width: int = 104) -> str:
    lines: list[str] = []
    for raw in text.expandtabs(4).splitlines():
        if not raw:
            lines.append("")
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        prefix = " " * indent
        chunks = textwrap.wrap(
            raw.strip(), width=max(30, width - indent), replace_whitespace=False,
            drop_whitespace=False, subsequent_indent="    ",
        ) or [""]
        lines.extend(prefix + chunk for chunk in chunks)
    return "\n".join(lines)


def column_widths(headers: list[str], available: float) -> list[float]:
    n = len(headers)
    if n == 2:
        return [available * 0.28, available * 0.72]
    if n == 3:
        return [available * 0.08, available * 0.25, available * 0.67]
    if n == 4:
        return [available * 0.06, available * 0.25, available * 0.49, available * 0.20]
    if n == 5:
        return [available * 0.18, available * 0.17, available * 0.21,
                available * 0.14, available * 0.30]
    if n == 6:
        return [available / n] * n
    if n == 7:
        return [available * x for x in (0.035, 0.12, 0.11, 0.16, 0.16, 0.12, 0.295)]
    return [available / n] * n


def make_table(rows: list[list[str]], available: float):
    headers = rows[0]
    font_size = 6.4 if len(headers) <= 5 else 5.5
    cell_style = ParagraphStyle(
        "CellDynamic", fontName="Arial", fontSize=font_size, leading=font_size + 2,
        textColor=INK,
    )
    head_style = ParagraphStyle(
        "HeadDynamic", fontName="Arial-Bold", fontSize=font_size, leading=font_size + 2,
        textColor=colors.white,
    )
    data = []
    for ridx, row in enumerate(rows):
        style = head_style if ridx == 0 else cell_style
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = LongTable(data, colWidths=column_widths(headers, available), repeatRows=1, splitByRow=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def parse_markdown(path: Path, story: list, available: float, include_title: bool = True) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if include_title:
        story.append(Paragraph(f"Sumber: {path.relative_to(ROOT)}", styles["FileLabel"]))

    i = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(x.strip() for x in paragraph)
            story.append(Paragraph(inline_markup(text), styles["Bodyx"]))
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            i += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            story.append(Preformatted(wrapped_code("\n".join(code)), styles["Codex"]))
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+", lines[i + 1]):
            flush_paragraph()
            table_lines = [line]
            i += 2  # skip separator row
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = [[c.strip() for c in row.strip().strip("|").split("|")] for row in table_lines]
            story.append(make_table(rows, available))
            story.append(Spacer(1, 6))
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[4:]), styles["H3x"]))
        elif stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[3:]), styles["H2x"]))
        elif stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), styles["H1x"]))
        elif re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            story.append(Paragraph(inline_markup(re.sub(r"^[-*]\s+", "", stripped)),
                                   styles["Bulletx"], bulletText="•"))
        elif re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            number, content = stripped.split(".", 1)
            story.append(Paragraph(inline_markup(content.strip()), styles["Bulletx"],
                                   bulletText=f"{number}."))
        elif stripped.startswith(">"):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped.lstrip("> ")), styles["Smallx"]))
        else:
            paragraph.append(line)
        i += 1
    flush_paragraph()


def add_code(path: Path, story: list) -> None:
    story.append(Paragraph(f"Berkas: {path.relative_to(ROOT)}", styles["FileLabel"]))
    story.append(Preformatted(wrapped_code(path.read_text(encoding="utf-8")), styles["Codex"]))


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(1.7 * cm, h - 1.25 * cm, w - 1.7 * cm, h - 1.25 * cm)
    canvas.setFont("Arial", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.7 * cm, h - 1.0 * cm, "UTS BI - Kelompok 1 | T3 Kota Bogor")
    canvas.drawRightString(w - 1.7 * cm, 0.85 * cm, f"Halaman {doc.page}")
    canvas.restoreState()


def build() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    left = right = 1.7 * cm
    top = 1.65 * cm
    bottom = 1.4 * cm
    available = page_w - left - right
    doc = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=left, rightMargin=right,
        topMargin=top, bottomMargin=bottom,
        title="Dokumen Desain UTS BI - Kelompok 1",
        author="Kelompok 1",
        subject="T3 Cuaca Ekstrem per Desa - K1 Kota Bogor",
    )
    frame = Frame(left, bottom, available, page_h - top - bottom, id="normal")
    doc.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=header_footer))

    story: list = []
    story.extend([
        Spacer(1, 3.0 * cm),
        Paragraph("DOKUMEN DESAIN UTS", styles["DocTitle"]),
        Paragraph("Business Intelligence Systems", styles["DocSubtitle"]),
        Spacer(1, 0.5 * cm),
        Table([["KELOMPOK", "1"],
               ["TOPIK", "T3 - Cuaca Ekstrem per Desa (BMKG)"],
               ["SLICE", "K1 - Kota Bogor, Jawa Barat (32.71)"],
               ["SNAPSHOT", "19 September 2026"],
               ["DOKUMEN", "30 September 2026"]],
              colWidths=[3.3 * cm, 10.2 * cm],
              style=TableStyle([
                  ("FONTNAME", (0, 0), (0, -1), "Arial-Bold"),
                  ("FONTNAME", (1, 0), (1, -1), "Arial"),
                  ("FONTSIZE", (0, 0), (-1, -1), 9),
                  ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
                  ("BACKGROUND", (0, 0), (0, -1), SKY),
                  ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                  ("TOPPADDING", (0, 0), (-1, -1), 8),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
              ])),
        Spacer(1, 1.0 * cm),
        Paragraph("Desain - bukan implementasi", styles["DocSubtitle"]),
        Paragraph(
            "Dokumen ini adalah snapshot terbaca dari tujuh deliverable UTS. "
            "Pipeline load dan test runner tidak dijalankan selama penyusunan.",
            ParagraphStyle("CoverNote", parent=styles["Bodyx"], alignment=TA_CENTER,
                           textColor=MUTED, leftIndent=1.2 * cm, rightIndent=1.2 * cm),
        ),
        PageBreak(),
    ])

    parse_markdown(ROOT / "docs/UTS_design_brief.md", story, available, include_title=False)

    appendices = [
        ("Lampiran A - Bukti sumber dan profiling", [
            ("md", ROOT / "data/raw/t3_publik/k1/SOURCE.md"),
            ("md", ROOT / "docs/profile_t3_k1.md"),
        ]),
        ("Lampiran B - DDL star schema", [
            ("code", ROOT / "sql/10_dim_date.sql"),
            ("code", ROOT / "sql/20_dim_wilayah.sql"),
            ("code", ROOT / "sql/20_dim_slot.sql"),
            ("code", ROOT / "sql/20_dim_cuaca.sql"),
            ("code", ROOT / "sql/30_fact_prakiraan_cuaca.sql"),
        ]),
        ("Lampiran C - Desain load", [("md", ROOT / "pipeline/DESIGN_load.md")]),
        ("Lampiran D - Enam test kualitas", [("code", ROOT / "tests/test_definitions.yml")]),
        ("Lampiran E - Tiga kueri analitik", [
            ("code", ROOT / "sql/40_analytics/q01.sql"),
            ("code", ROOT / "sql/40_analytics/q02.sql"),
            ("code", ROOT / "sql/40_analytics/q03.sql"),
        ]),
        ("Lampiran F - Kamus dan SQL metrik", [
            ("md", ROOT / "docs/kamus_metrik.md"),
            ("code", ROOT / "sql/50_metrics/persentase_slot_hujan.sql"),
        ]),
        ("Lampiran G - Batas desain", [("md", ROOT / "docs/batas_desain.md")]),
        ("Lampiran H - Form D7 scope cut", [("md", ROOT / "docs/D7_scope_cut.md")]),
    ]
    for title, files in appendices:
        story.append(PageBreak())
        story.append(Paragraph(title, styles["H1x"]))
        for kind, path in files:
            if kind == "md":
                parse_markdown(path, story, available)
            else:
                add_code(path, story)

    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    print(build())
