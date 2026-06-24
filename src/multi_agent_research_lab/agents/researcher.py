"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.services.llm_client import LLMClient

class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self):
        self.search_client = SearchClient()
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        
        # 1. Search
        sources = self.search_client.search(state.request.query)
        state.sources.extend(sources)
        
        # 2. Summarize sources into notes
        sources_text = "\n\n".join([f"Source: {s.title}\nContent: {s.snippet}" for s in sources])
        
        system_prompt = (
            "You are a researcher. Your task is to review search results and summarize them "
            "into concise research notes. Focus on facts, numbers, and key information."
        )
        user_prompt = f"Query: {state.request.query}\n\nSearch Results:\n{sources_text}"
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.research_notes = response.content
        
        return state
