"""Streamlit Web Workstation for OmniResearch."""

import os
import sys
import tempfile

import streamlit as st

# Ensure src is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omniresearch.config import get_settings
from omniresearch.core.graph import run_research
from omniresearch.exporters.docx import export_docx_file
from omniresearch.exporters.markdown import export_markdown_file, format_markdown
from omniresearch.exporters.pdf import export_pdf_file

st.set_page_config(
    page_title="OmniResearch — Enterprise Intelligence Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #E2E8F0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/search.png", width=64)
    st.markdown("### ⚙️ Engine Settings")

    settings = get_settings()
    llm_provider = st.selectbox(
        "LLM Provider",
        ["gemini", "openai", "anthropic", "ollama"],
        index=["gemini", "openai", "anthropic", "ollama"].index(settings.llm_provider),
    )

    search_provider = st.selectbox(
        "Search Provider",
        ["duckduckgo", "tavily", "exa"],
        index=["duckduckgo", "tavily", "exa"].index(settings.search_provider),
        help="DuckDuckGo is built-in and free without API keys.",
    )

    st.divider()
    st.markdown("### 📂 Enterprise Document Ingestion")
    uploaded_files = st.file_uploader(
        "Upload corporate documents (.pdf, .docx, .csv, .txt)",
        type=["pdf", "docx", "csv", "txt", "md"],
        accept_multiple_files=True,
    )

    st.caption("🔒 All documents are processed locally or in memory.")

# Main Interface
st.markdown('<div class="main-header">🔍 OmniResearch</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Enterprise Autonomous Deep Research & Fact-Checked Intelligence Engine</div>',
    unsafe_allow_html=True,
)

# Example Presets
col_preset1, col_preset2, col_preset3 = st.columns(3)
preset_topic = ""
if col_preset1.button("⚡ AI Chip Competitor Dynamics: Nvidia vs Custom Silicon"):
    preset_topic = "AI Chip Market Dynamics: Nvidia Blackwell vs AMD MI300X vs Google TPU v5e"
if col_preset2.button("🛡️ Enterprise Cyber Insurance & Ransomware 2026"):
    preset_topic = (
        "Enterprise Cyber Insurance Underwriting Trends and Ransomware Claim Volatility 2026"
    )
if col_preset3.button("📱 Small Language Models (SLMs) On-Device"):
    preset_topic = (
        "Small Language Models (SLMs) Benchmarks and On-Device Edge Deployment in Enterprise"
    )

topic_input = st.text_input(
    "Enter Research Topic or Executive Inquiry:",
    value=preset_topic,
    placeholder="e.g. Global Renewable Energy Grid Storage Market Projections 2026-2030",
)

col_run, col_clear = st.columns([1, 5])
start_btn = col_run.button("🚀 Run Deep Research", type="primary", use_container_width=True)

if start_btn and topic_input.strip():
    # Save uploaded files to temp directory
    temp_doc_paths = []
    if uploaded_files:
        temp_dir = tempfile.mkdtemp()
        for uf in uploaded_files:
            target_path = os.path.join(temp_dir, uf.name)
            with open(target_path, "wb") as f:
                f.write(uf.getbuffer())
            temp_doc_paths.append(target_path)

    progress_bar = st.progress(0.0)
    status_text = st.empty()

    def update_progress(msg: str, frac: float):
        progress_bar.progress(frac)
        status_text.info(msg)

    with st.spinner("OmniResearch Multi-Agent State Machine is analyzing..."):
        state = run_research(
            topic=topic_input.strip(),
            uploaded_files=temp_doc_paths,
            progress_callback=update_progress,
        )

    status_text.success("🎉 Research Complete! Executive Dossier is ready.")
    progress_bar.empty()

    if state.report:
        rep = state.report

        # Metrics Row
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Empirical Confidence Score", f"{rep.average_confidence_score}%")
        m_col2.metric("Verified Evidence Sources", len(rep.sources))
        m_col3.metric("Audited Claims", len(rep.fact_check_summary))

        st.divider()

        # Tabs for Deliverables
        tab_dossier, tab_factcheck, tab_sources, tab_download = st.tabs(
            [
                "📋 Executive Dossier",
                "🛡️ Fact-Check Matrix",
                "📚 Primary Sources",
                "⬇️ Export Deliverables",
            ]
        )

        with tab_dossier:
            st.markdown(format_markdown(rep), unsafe_allow_html=True)

        with tab_factcheck:
            st.subheader("Audited Claims & Empirical Verification")
            if rep.fact_check_summary:
                fact_data = [
                    {
                        "Claim / Metric": c.claim_text,
                        "Status": c.status.upper(),
                        "Confidence": f"{c.confidence_score}%",
                        "Source": f"Source {c.source_id}" if c.source_id else "Corroborated",
                        "Rationale": c.verification_rationale,
                    }
                    for c in rep.fact_check_summary
                ]
                st.dataframe(fact_data, use_container_width=True)
            else:
                st.info("No numerical/factual claims were flagged for verification.")

        with tab_sources:
            st.subheader("Retrieved Hybrid Sources & Snippets")
            for s in rep.sources:
                with st.expander(f"[Source {s.id}] {s.title} ({s.source_type.upper()})"):
                    st.write(f"**Path / URL:** {s.url_or_path}")
                    st.write(f"**Excerpt:** {s.snippet}")

        with tab_download:
            st.subheader("Download Formatted Corporate Deliverables")

            # Prepare files in temp
            out_temp = tempfile.mkdtemp()
            clean_name = "omniresearch_dossier"

            # Markdown
            md_path = os.path.join(out_temp, f"{clean_name}.md")
            export_markdown_file(rep, md_path)
            with open(md_path, "r", encoding="utf-8") as f:
                md_bytes = f.read().encode("utf-8")

            # DOCX
            docx_path = os.path.join(out_temp, f"{clean_name}.docx")
            export_docx_file(rep, docx_path)
            with open(docx_path, "rb") as f:
                docx_bytes = f.read()

            # PDF
            pdf_path = os.path.join(out_temp, f"{clean_name}.pdf")
            export_pdf_file(rep, pdf_path)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            d_col1, d_col2, d_col3 = st.columns(3)
            d_col1.download_button(
                "📄 Download Markdown (.md)",
                data=md_bytes,
                file_name=f"{clean_name}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            d_col2.download_button(
                "📘 Download Word (.docx)",
                data=docx_bytes,
                file_name=f"{clean_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
            d_col3.download_button(
                "📕 Download Executive PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"{clean_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
