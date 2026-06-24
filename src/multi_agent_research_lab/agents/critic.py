"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""
        
        if not state.final_answer:
            return state

        system_prompt = (
            "You are a strict critic. Review the final answer against the research and analysis notes. "
            "Identify any hallucinations, lack of citations, or logic gaps. Provide a short critique. "
            "If it is perfect, just say 'Critique: PASS'."
        )
        
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes}\n\n"
            f"Analysis Notes:\n{state.analysis_notes}\n\n"
            f"Final Answer to Review:\n{state.final_answer}\n"
        )
        
        response = self.llm.complete(system_prompt, user_prompt)
        
        critique = response.content.strip()
        state.final_answer += f"\n\n--- Critic Review ---\n{critique}"
        
        return state
