"""State Machine Graph Orchestration for OmniResearch."""

from omniresearch.agents.planner import plan_research_step
from omniresearch.agents.researcher import research_step
from omniresearch.agents.verifier import verify_facts_step
from omniresearch.agents.writer import write_report_step
from omniresearch.core.state import ResearchState


def run_research(
    topic: str,
    uploaded_files: list[str] | None = None,
    max_iterations: int = 1,
    progress_callback=None,
) -> ResearchState:
    """Execute the end-to-end multi-agent research pipeline."""
    state = ResearchState(
        topic=topic,
        uploaded_files=uploaded_files or [],
        max_iterations=max_iterations,
    )

    # 1. Planning Phase
    if progress_callback:
        progress_callback("🧠 Planner Agent: Decomposing inquiry into research tracks...", 0.15)
    state = plan_research_step(state)

    # 2. Research & Hybrid Retrieval Phase
    if progress_callback:
        progress_callback(
            "🌐 Researcher Agent: Collecting public web & internal document evidence...", 0.45
        )
    state = research_step(state)

    # 3. Fact-Checking & Verification Phase
    if progress_callback:
        progress_callback(
            "🛡️ Verifier Agent: Cross-referencing claims & confidence scoring...", 0.75
        )
    state = verify_facts_step(state)

    # 4. Executive Dossier Synthesis Phase
    if progress_callback:
        progress_callback(
            "✍️ Executive Writer: Compiling verified dossier & recommendations...", 0.95
        )
    state = write_report_step(state)

    if progress_callback:
        progress_callback("✅ Complete! Dossier generated.", 1.0)

    return state


def create_research_graph():
    """Return LangGraph StateGraph instance if available."""
    try:
        from langgraph.graph import END, START, StateGraph

        builder = StateGraph(ResearchState)
        builder.add_node("planner", plan_research_step)
        builder.add_node("researcher", research_step)
        builder.add_node("verifier", verify_facts_step)
        builder.add_node("writer", write_report_step)

        builder.add_edge(START, "planner")
        builder.add_edge("planner", "researcher")
        builder.add_edge("researcher", "verifier")
        builder.add_edge("verifier", "writer")
        builder.add_edge("writer", END)

        return builder.compile()
    except Exception as exc:
        print(f"[OmniResearch Graph Info] Using direct state pipeline: {exc}")
        return None
