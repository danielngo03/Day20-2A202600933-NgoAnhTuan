"""Supervisor / router skeleton."""

import json
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self):
        self.llm = LLMClient()
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        
        if state.iteration >= self.settings.max_iterations:
            state.errors.append("Max iterations reached. Force ending.")
            state.record_route("END")
            return state

        system_prompt = (
            "You are a supervisor managing a research team. "
            "The team consists of 'researcher', 'analyst', 'writer', and 'critic'.\n"
            "Your job is to read the current state of the request and decide the next step.\n"
            "Return ONLY a JSON object with a single key 'next_agent' and its value as the name of the next agent or 'END'.\n"
            "Rules:\n"
            "1. If 'research_notes' is empty, route to 'researcher'.\n"
            "2. If 'research_notes' has content but 'analysis_notes' is empty, route to 'analyst'.\n"
            "3. If both notes exist but 'final_answer' is empty, route to 'writer'.\n"
            "4. If 'final_answer' is populated and 'Is Reviewed By Critic' is False, route to 'critic'.\n"
            "5. If 'Is Reviewed By Critic' is True, route to 'END'.\n"
        )
        
        user_prompt = (
            f"Query: {state.request.query}\n"
            f"Iteration: {state.iteration}\n"
            f"Route History: {state.route_history}\n"
            f"Research Notes Exists: {bool(state.research_notes)}\n"
            f"Analysis Notes Exists: {bool(state.analysis_notes)}\n"
            f"Final Answer Exists: {bool(state.final_answer)}\n"
            f"Is Reviewed By Critic: {'--- Critic Review ---' in (state.final_answer or '')}\n"
        )
        
        response = self.llm.complete(system_prompt, user_prompt)
        
        # Parse JSON
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            decision = json.loads(content)
            next_agent = decision.get("next_agent", "END")
            
            # Simple validation
            if next_agent not in ["researcher", "analyst", "writer", "critic", "END"]:
                next_agent = "END"
                
            state.record_route(next_agent)
        except Exception as e:
            state.errors.append(f"Supervisor routing error: {e}")
            # Fallback logic
            if not state.research_notes:
                state.record_route("researcher")
            elif not state.analysis_notes:
                state.record_route("analyst")
            elif not state.final_answer:
                state.record_route("writer")
            else:
                state.record_route("END")
                
        return state
