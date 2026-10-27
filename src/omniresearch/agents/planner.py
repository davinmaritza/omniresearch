"""Planner Agent: Decomposes research topics into structured investigative hypotheses."""

from omniresearch.core.llm import extract_json_payload, get_llm_client
from omniresearch.core.state import ResearchHypothesis, ResearchState

PLANNER_SYSTEM_PROMPT = """You are an elite corporate research strategist.
Your role is to decompose a complex business, technological, or market inquiry into 3 to 5 high-impact, mutually exclusive investigative sub-topics.
Ensure each sub-query targets factual metrics, competitive dynamics, architecture/methodology, or regulatory/risk profiles.
Output strictly valid JSON with this format:
{
  "sub_queries": [
    {
      "query": "Specific targeted search query",
      "rationale": "Why this specific aspect is vital for executive decision making"
    }
  ]
}"""


def plan_research_step(state: ResearchState) -> ResearchState:
    """Execute the Planner Agent step."""
    llm = get_llm_client()

    prompt = f"Research Topic: {state.topic}\n"
    if state.uploaded_files:
        prompt += f"Context: User also provided {len(state.uploaded_files)} internal documents.\n"
    prompt += "Decompose this topic into 3-4 structured investigative sub-queries."

    state.activity_log.append(
        f"🧠 [Planner] Generating research hypothesis and sub-queries for: '{state.topic}'"
    )

    response_text = llm.generate(prompt=prompt, system_prompt=PLANNER_SYSTEM_PROMPT, json_mode=True)

    hypotheses: list[ResearchHypothesis] = []
    try:
        data = extract_json_payload(response_text)
        for item in data.get("sub_queries", []):
            hypotheses.append(
                ResearchHypothesis(
                    sub_query=item.get("query", state.topic),
                    rationale=item.get("rationale", "Strategic relevance"),
                    priority=1,
                    completed=False,
                )
            )
    except Exception as exc:
        state.activity_log.append(f"⚠️ [Planner] Parser fallback: {exc}")
        # Fallback default queries
        hypotheses = [
            ResearchHypothesis(
                sub_query=f"{state.topic} market size and industry competitors",
                rationale="Market positioning",
            ),
            ResearchHypothesis(
                sub_query=f"{state.topic} technical architecture and implementation",
                rationale="Technical assessment",
            ),
            ResearchHypothesis(
                sub_query=f"{state.topic} corporate risks challenges and trends",
                rationale="Risk management",
            ),
        ]

    state.plan = hypotheses
    state.activity_log.append(f"✅ [Planner] Created {len(hypotheses)} targeted research tracks.")
    return state
