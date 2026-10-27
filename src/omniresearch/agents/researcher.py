"""Researcher Agent: Orchestrates hybrid retrieval from web searches and local files."""

import os

from omniresearch.core.state import ResearchState, SourceDocument
from omniresearch.tools.document import parse_document
from omniresearch.tools.search import search_hybrid


def research_step(state: ResearchState) -> ResearchState:
    """Execute the Researcher Agent step."""
    start_id = len(state.sources) + 1
    new_sources: list[SourceDocument] = []

    # 1. First, process any uploaded enterprise documents if not yet indexed
    if state.uploaded_files and state.iteration == 0:
        state.activity_log.append(
            f"📂 [Researcher] Parsing {len(state.uploaded_files)} local enterprise documents..."
        )
        for file_path in state.uploaded_files:
            if os.path.exists(file_path):
                docs = parse_document(file_path, start_id=start_id)
                new_sources.extend(docs)
                start_id += len(docs)
                state.activity_log.append(
                    f"  └─ Extracted {len(docs)} sections from: {os.path.basename(file_path)}"
                )

    # 2. Next, execute web search for each uncompleted hypothesis in the plan
    state.activity_log.append(
        "🌐 [Researcher] Executing multi-track search for planned hypotheses..."
    )
    for idx, hyp in enumerate(state.plan):
        if not hyp.completed:
            state.activity_log.append(f"  🔍 Querying: '{hyp.sub_query}'")
            results = search_hybrid(hyp.sub_query, max_results=3, start_id=start_id)
            new_sources.extend(results)
            start_id += len(results)
            hyp.completed = True

    # Combine into state
    state.sources.extend(new_sources)
    state.iteration += 1
    state.activity_log.append(
        f"✅ [Researcher] Collected total {len(state.sources)} source documents/evidence chunks."
    )
    return state
