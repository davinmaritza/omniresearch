# OmniResearch Architecture Specification

## 1. Design Overview

OmniResearch uses a modular state-machine pattern to run multi-stage autonomous research. Rather than piping a user query directly into an LLM context window with arbitrary web search results, OmniResearch isolates responsibilities across specialized agents connected by a shared state container (`ResearchState`).

## 2. Agent Node Lifecycle

1. **Planner Agent**
   - Inputs: `topic`, `uploaded_files`.
   - Output: List of `ResearchHypothesis` objects (3-5 targeted investigative angles).
   - Invariants: Queries must be mutually exclusive and cover market size, technical architecture, and risk factors.

2. **Researcher Agent**
   - Inputs: Uncompleted `ResearchHypothesis` items, `uploaded_files`.
   - Output: List of `SourceDocument` instances added to `state.sources`.
   - Seam: `search_hybrid` handles routing between DuckDuckGo and Tavily/Exa. Local files are chunked by page or paragraph via `parse_document`.

3. **Verifier Agent**
   - Inputs: Top retrieved `SourceDocument` chunks.
   - Output: List of `FactCheckClaim` instances with confidence scores (0-100%) and verification rationale.
   - Ground truth matching: Claims without direct evidence are labeled unverified rather than discarded, ensuring analysts can inspect gaps.

4. **Writer Agent**
   - Inputs: Verified claims, sources, and original inquiry.
   - Output: Structured `ResearchReport` containing executive summary, key findings, analytical sections with inline citation IDs (`[Source N]`), and strategic recommendations.

## 3. Data Flow and Invariants

```
User Query + Docs
       │
       ▼
[ResearchState] ──► Planner ──► Researcher ──► Verifier ──► Writer
       ▲                                                       │
       └────────────────── State Updates ──────────────────────┘
                                                               │
                                                               ▼
                                                      Exporters (MD, PDF, DOCX)
```

- **Idempotency**: Agents do not re-run queries that have already been marked `completed = True`.
- **Zero-Key Guarantee**: If external LLM or Search API credentials are absent, the system falls back to DuckDuckGo search and local heuristic synthesis to ensure pipeline continuity during offline evaluations.
