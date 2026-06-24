"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

class AnalystAgent(BaseAgent):
    """Synthesizes and structures the research notes."""

    name = "analyst"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes` based on `state.research_notes`."""
        
        system_prompt = (
            "You are an expert analyst. Your job is to take raw research notes and "
            "synthesize them into structured analysis notes. Extract key themes, identify patterns, "
            "and highlight the most important insights."
        )
        
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}"
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.analysis_notes = response.content
        
        return state
