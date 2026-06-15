from memory.long_term_memory import LongTermMemory
from memory.retrieval_evaluator import RetrievalEvaluator
from state.user_profile import UserProfileEngine
from state.goal_management import GoalManagementSystem
from state.project_engine import ProjectEngine
from state.skill_engine import SkillEngine
from state.personalization import PersonalizationLayer

class ContextBuilderService:
    def __init__(self):
        self.long_term_memory = LongTermMemory()
        self.retrieval_evaluator = RetrievalEvaluator()
        self.user_profile = UserProfileEngine()
        self.goal_system = GoalManagementSystem()
        self.project_engine = ProjectEngine()
        self.skill_engine = SkillEngine()
        self.personalization = PersonalizationLayer()

    def get_raw_state(self) -> dict:
        """Returns the raw dictionaries of the cognitive state."""
        return {
            "profile": self.user_profile.get_profile(),
            "goals": self.goal_system.get_active_goals(),
            "projects": self.project_engine.get_active_projects(),
            "skills": self.skill_engine.get_all_skills()
        }

    def assemble_context_string(self, user_input: str) -> str:
        """Builds the formatted string block to be injected into the Reasoning prompt."""
        # 1. Memories
        episodic_memories = self.long_term_memory.retrieve_episodic(user_input)
        semantic_memories = self.long_term_memory.retrieve_semantic(user_input)
        all_raw_memories = episodic_memories + semantic_memories
        evaluated_memories = self.retrieval_evaluator.evaluate(user_input, all_raw_memories)
        memory_str = "\n".join([f"- {m['memory']} (Relevance: {m['relevance']}, Confidence: {m['confidence']})" for m in evaluated_memories]) if evaluated_memories else "No relevant past memories."
        
        # 2. State
        state = self.get_raw_state()
        
        profile = state['profile']
        profile_str = f"Name: {profile.get('name', 'User')}\nPreferences: {profile.get('speaking_style_preference', 'calm')}"
        
        goals_str = "\n".join([f"- {g['title']}: {g['description']}" for g in state['goals']]) if state['goals'] else "No active goals."
        projects_str = "\n".join([f"- {p['name']}: {p['description']}" for p in state['projects']]) if state['projects'] else "No active projects."
        skills_str = "\n".join([f"- {s['skill_name']} ({s['category']}): Level {s['level']} | Progress: {s['progress']}%" for s in state['skills']]) if state['skills'] else "No skills tracked yet."
        
        # 3. Personalization
        personalization_str = self.personalization.format_prompt_modifier(profile)
        
        context_package = f"""
[Relevant Memories]
{memory_str}

[User Profile]
{profile_str}

[Active Goals]
{goals_str}

[Active Projects]
{projects_str}

[Active Skills / Learning Progression]
{skills_str}

[Personalization Instructions]
{personalization_str}
"""
        return context_package
