"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

class WriterAgent(BaseAgent):
    """Drafts the final response based on the analysis."""

    name = "writer"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer` based on `state.analysis_notes`."""
        
        system_prompt = (
            "You are an expert writer. Your task is to draft a comprehensive and engaging final "
            "response based on the provided analysis notes. Ensure the answer directly addresses the original query."
        )
        
        user_prompt = (
            f"Original Query: {state.request.query}\n\n"
            f"Analysis Notes:\n{state.analysis_notes}\n\n"
            f"Please write the final response now."
        )
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        
        return state
