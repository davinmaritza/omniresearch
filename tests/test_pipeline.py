"""Comprehensive test suite for OmniResearch."""

import os
import tempfile

from omniresearch.core.graph import run_research
from omniresearch.core.state import (
    FactCheckClaim,
    ReportSection,
    ResearchReport,
    ResearchState,
    SourceDocument,
)
from omniresearch.exporters.docx import export_docx_file
from omniresearch.exporters.markdown import export_markdown_file
from omniresearch.exporters.pdf import export_pdf_file


def test_research_state_initialization():
    """Verify that ResearchState initializes with proper defaults."""
    state = ResearchState(topic="Quantum Computing Cryptography Threats")
    assert state.topic == "Quantum Computing Cryptography Threats"
    assert state.iteration == 0
    assert len(state.sources) == 0
    assert len(state.plan) == 0
    assert state.is_completed is False


def test_end_to_end_research_pipeline():
    """Test full multi-agent pipeline from topic to executive report."""
    topic = "Next-Gen Solid State Battery Commercialization 2026"
    state = run_research(topic=topic, max_iterations=1)

    assert state.is_completed is True
    assert state.report is not None
    assert state.report.topic == topic
    assert len(state.report.sections) > 0
    assert state.report.average_confidence_score > 0
    assert len(state.activity_log) >= 4


def test_exporters():
    """Verify Markdown, DOCX, and PDF exporters generate non-empty valid files."""
    report = ResearchReport(
        topic="Enterprise Generative AI Adoption 2026",
        executive_summary="Executive briefing on enterprise LLM deployment patterns.",
        sections=[
            ReportSection(
                heading="ROI and Operational Metrics",
                content="Companies report 32% efficiency gains in customer engineering [Source 1].",
                citations=[1],
            )
        ],
        key_findings=[
            "32% measured productivity uplift",
            "Strict data privacy requirements observed",
        ],
        strategic_recommendations=["Standardize on model-agnostic gateways"],
        fact_check_summary=[
            FactCheckClaim(
                claim_text="Companies report 32% efficiency gains",
                source_id=1,
                status="verified",
                confidence_score=94.0,
                verification_rationale="Verified by case study excerpts",
            )
        ],
        sources=[
            SourceDocument(
                id=1,
                title="Enterprise AI Report 2026",
                url_or_path="https://example.com/ai-report",
                snippet="In a survey of 500 enterprises, measured efficiency gains reached 32% in engineering.",
                source_type="web",
            )
        ],
        average_confidence_score=94.0,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        # Markdown
        md_file = os.path.join(tmpdir, "report.md")
        export_markdown_file(report, md_file)
        assert os.path.exists(md_file)
        with open(md_file, "r", encoding="utf-8") as f:
            md_text = f.read()
        assert "Executive Dossier: Enterprise Generative AI Adoption 2026" in md_text
        assert "94.0%" in md_text

        # DOCX
        docx_file = os.path.join(tmpdir, "report.docx")
        export_docx_file(report, docx_file)
        assert os.path.exists(docx_file)
        assert os.path.getsize(docx_file) > 1000

        # PDF
        pdf_file = os.path.join(tmpdir, "report.pdf")
        export_pdf_file(report, pdf_file)
        assert os.path.exists(pdf_file)
        assert os.path.getsize(pdf_file) > 1000
