"""OmniResearch: Enterprise Autonomous Deep Research & Fact-Checked Intelligence Engine."""

__version__ = "0.1.0"
__author__ = "Davin Maritza"

from omniresearch.core.graph import create_research_graph, run_research
from omniresearch.core.state import ResearchReport, ResearchState

__all__ = [
    "ResearchReport",
    "ResearchState",
    "create_research_graph",
    "run_research",
]
