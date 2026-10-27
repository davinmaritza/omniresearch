"""PDF Exporter for OmniResearch Executive Dossiers using ReportLab."""

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from omniresearch.core.state import ResearchReport


def export_pdf_file(report: ResearchReport, output_path: str) -> str:
    """Generate high-impact executive PDF dossier."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom Corporate Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=14,
    )
    h1_style = ParagraphStyle(
        "DocH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
    )

    story = []

    # Title & Metadata
    story.append(Paragraph(f"Executive Dossier: {report.topic}", title_style))
    story.append(
        Paragraph(
            f"OmniResearch Engine | {report.generated_at} | Confidence Score: {report.average_confidence_score}%",
            meta_style,
        )
    )
    story.append(Spacer(1, 10))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(report.executive_summary, body_style))
    story.append(Spacer(1, 8))

    # 2. Key Findings
    if report.key_findings:
        story.append(Paragraph("2. Key Strategic Findings", h1_style))
        for kf in report.key_findings:
            story.append(Paragraph(f"• {kf}", body_style))
        story.append(Spacer(1, 8))

    # 3. Analytical Sections
    story.append(Paragraph("3. In-Depth Analysis", h1_style))
    for idx, sec in enumerate(report.sections, start=1):
        story.append(Paragraph(f"3.{idx}. {sec.heading}", h1_style))
        story.append(Paragraph(sec.content, body_style))

    # 4. Strategic Recommendations
    if report.strategic_recommendations:
        story.append(Paragraph("4. Strategic Recommendations", h1_style))
        for idx, rec in enumerate(report.strategic_recommendations, start=1):
            story.append(Paragraph(f"{idx}. {rec}", body_style))
        story.append(Spacer(1, 8))

    # 5. Fact Check Matrix Table
    if report.fact_check_summary:
        story.append(Paragraph("5. Fact-Check & Verification Matrix", h1_style))
        table_data = [["Claim / Metric", "Status", "Confidence", "Source"]]
        for c in report.fact_check_summary[:8]:
            short_claim = c.claim_text[:50] + "..." if len(c.claim_text) > 50 else c.claim_text
            table_data.append(
                [
                    short_claim,
                    c.status.upper(),
                    f"{c.confidence_score}%",
                    f"Source {c.source_id}" if c.source_id else "Corroborated",
                ]
            )

        t = Table(table_data, colWidths=[240, 80, 80, 100])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)
    return output_path
