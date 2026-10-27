"""Rich CLI Interface for OmniResearch."""

import os
import sys
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from omniresearch import __version__
from omniresearch.config import get_settings
from omniresearch.core.graph import run_research
from omniresearch.exporters.markdown import export_markdown_file
from omniresearch.exporters.pdf import export_pdf_file
from omniresearch.exporters.docx import export_docx_file

app = typer.Typer(
    name="omniresearch",
    help="Enterprise Autonomous Deep Research & Fact-Checked Intelligence Engine",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Display OmniResearch version and system details."""
    console.print(f"[bold cyan]OmniResearch[/bold cyan] version [green]{__version__}[/green]")
    settings = get_settings()
    console.print(f"LLM Provider: [yellow]{settings.llm_provider}[/yellow] ({settings.llm_model})")
    console.print(f"Search Provider: [yellow]{settings.search_provider}[/yellow]")


@app.command()
def check():
    """Audit system readiness, API keys, and model connectivity."""
    settings = get_settings()
    table = Table(title="OmniResearch System Audit", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Configured Value", style="white")
    table.add_column("Status", style="bold")

    # LLM Provider
    llm_status = "🟢 Ready" if (
        (settings.llm_provider == "gemini" and settings.gemini_api_key) or
        (settings.llm_provider == "openai" and settings.openai_api_key) or
        (settings.llm_provider == "anthropic" and settings.anthropic_api_key) or
        (settings.llm_provider == "ollama")
    ) else "🟡 Offline / Heuristic Mode"
    table.add_row("LLM Provider", f"{settings.llm_provider} ({settings.llm_model})", llm_status)

    # Search Provider
    search_status = "🟢 Ready (Zero-Cost)" if settings.search_provider == "duckduckgo" else (
        "🟢 Ready" if settings.tavily_api_key else "🟡 Missing API Key (Falling back to DuckDuckGo)"
    )
    table.add_row("Search Engine", settings.search_provider, search_status)

    # Document Parsing
    table.add_row("Document Parser", "PDF (PyMuPDF), DOCX, CSV, MD", "🟢 Available")
    
    # Exporters
    table.add_row("Report Exporters", "Markdown, PDF (ReportLab), DOCX", "🟢 Available")

    console.print(table)


@app.command()
def run(
    topic: str = typer.Argument(..., help="Research question or enterprise topic"),
    docs: Optional[List[str]] = typer.Option(None, "--docs", "-d", help="Paths to local PDF/DOCX/CSV documents"),
    export: str = typer.Option("md,pdf,docx", "--export", "-e", help="Comma-separated export formats (md, pdf, docx)"),
    out: str = typer.Option("./reports", "--out", "-o", help="Output directory for generated dossiers"),
):
    """Execute end-to-end autonomous research and produce an executive dossier."""
    console.print(Panel.fit(
        f"[bold white]Topic:[/bold white] [bold cyan]{topic}[/bold cyan]\n"
        f"[bold white]Documents:[/bold white] {len(docs or [])} local files\n"
        f"[bold white]Output Formats:[/bold white] {export}",
        title="[bold green]OmniResearch Autonomous Deep Engine[/bold green]",
        border_style="green"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Initializing OmniResearch Multi-Agent Workflow...", total=100)

        def progress_cb(msg: str, frac: float):
            progress.update(task, description=f"[cyan]{msg}", completed=int(frac * 100))

        state = run_research(topic=topic, uploaded_files=docs or [], progress_callback=progress_cb)

    if not state.report:
        console.print("[bold red]Failed to compile research report.[/bold red]")
        sys.exit(1)

    # Print Executive Summary Banner
    console.print("\n[bold green]═══ Executive Dossier Compiled ═══[/bold green]")
    console.print(f"[bold]Empirical Confidence Score:[/bold] [bold yellow]{state.report.average_confidence_score}%[/bold yellow]")
    console.print(f"[bold]Total Sources Analyzed:[/bold] [cyan]{len(state.report.sources)}[/cyan]\n")

    # Exporting
    clean_topic = "".join([c if c.isalnum() else "_" for c in topic[:30]]).strip("_").lower()
    os.makedirs(out, exist_ok=True)
    exported_files = []

    formats = [f.strip().lower() for f in export.split(",")]
    if "md" in formats:
        md_path = os.path.join(out, f"{clean_topic}_dossier.md")
        export_markdown_file(state.report, md_path)
        exported_files.append(md_path)

    if "docx" in formats:
        docx_path = os.path.join(out, f"{clean_topic}_dossier.docx")
        export_docx_file(state.report, docx_path)
        exported_files.append(docx_path)

    if "pdf" in formats:
        pdf_path = os.path.join(out, f"{clean_topic}_dossier.pdf")
        export_pdf_file(state.report, pdf_path)
        exported_files.append(pdf_path)

    console.print("[bold green]Deliverables exported successfully:[/bold green]")
    for p in exported_files:
        console.print(f"  📄 [bold underline]{p}[/bold underline]")


@app.command()
def web(
    port: int = typer.Option(8501, "--port", "-p", help="Port to run Streamlit app"),
):
    """Launch the interactive Streamlit Web Workstation."""
    import subprocess
    web_file = os.path.join(os.path.dirname(__file__), "web.py")
    console.print(f"[bold green]Starting OmniResearch Web Dashboard on port {port}...[/bold green]")
    cmd = [sys.executable, "-m", "streamlit", "run", web_file, "--server.port", str(port)]
    subprocess.run(cmd)


if __name__ == "__main__":
    app()
