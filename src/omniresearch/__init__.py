"""OmniResearch: Enterprise Autonomous Deep Research & Fact-Checked Intelligence Engine."""

__version__ = "0.1.0"
__author__ = "Davin Maritza"

from omniresearch.core.state import ResearchState, ResearchReport
from omniresearch.core.graph import create_research_graph, run_research

__all__ = [
    "ResearchState",
    "ResearchReport",
    "create_research_graph",
    "run_research",
]
