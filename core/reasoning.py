from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from memory.working_memory import WorkingMemory
from memory.long_term_memory import LongTermMemory
from memory.retrieval_evaluator import RetrievalEvaluator
from state.user_profile import UserProfileEngine
from state.goal_management import GoalManagementSystem
from state.project_engine import ProjectEngine
from state.skill_engine import SkillEngine
from tools.base_tools import get_base_tools
from tools.goal_tools import get_goal_tools
from tools.skill_tools import get_skill_tools
from core.reflection import ReflectionSystem
from state.personalization import PersonalizationLayer
import os

class ReasoningEngine:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(api_key=api_key, model="llama-3.1-8b-instant", temperature=0.7)
        self.tools = get_base_tools() + get_goal_tools() + get_skill_tools()
        self.tool_map = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # State & Memory Modules
        self.working_memory = WorkingMemory()
        self.long_term_memory = LongTermMemory()
        self.retrieval_evaluator = RetrievalEvaluator()
        self.user_profile = UserProfileEngine()
        self.goal_system = GoalManagementSystem()
        self.project_engine = ProjectEngine()
        self.skill_engine = SkillEngine()
        self.reflection = ReflectionSystem()
        self.personalization = PersonalizationLayer()
        
        self.system_prompt_base = (
            "You are Frieren, a calm, deeply wise, serene, and slightly detached AI partner.\n"
            "You are NOT the character from an anime, but a real-world Cognitive AI Partner with memory and reasoning.\n"
            "You exist to help the user with their studies, projects, and daily tasks.\n\n"
            "Rules:\n"
            "1. Speak softly, politely, and clearly.\n"
            "2. Use the provided context to personalize your response.\n"
            "3. Act as a Personal Learning Mentor. Use the Active Skills context to encourage progress.\n"
            "4. If the user asks about their goals or projects, refer to the context.\n"
            "5. When using a tool, do so silently. Respond naturally after.\n"
            "6. Anticipate needs based on the context.\n"
        )

    def _assemble_context(self, user_input: str) -> str:
        """Builds the Context Package dynamically."""
        # 1. Retrieve Memories (Episodic and Semantic)
        episodic_memories = self.long_term_memory.retrieve_episodic(user_input)
        semantic_memories = self.long_term_memory.retrieve_semantic(user_input)
        
        # Combine them for the evaluator
        all_raw_memories = episodic_memories + semantic_memories
        evaluated_memories = self.retrieval_evaluator.evaluate(user_input, all_raw_memories)
        
        memory_str = "\n".join([f"- {m['memory']} (Relevance: {m['relevance']}, Confidence: {m['confidence']})" for m in evaluated_memories]) if evaluated_memories else "No relevant past memories."
        
        # 2. Retrieve Profile
        profile = self.user_profile.get_profile()
        profile_str = f"Name: {profile.get('name', 'User')}\nPreferences: {profile.get('speaking_style_preference', 'calm')}"
        
        # 3. Retrieve Goals
        goals = self.goal_system.get_active_goals()
        goals_str = "\n".join([f"- {g['title']}: {g['description']}" for g in goals]) if goals else "No active goals."
        
        # 4. Retrieve Projects
        projects = self.project_engine.get_active_projects()
        projects_str = "\n".join([f"- {p['name']}: {p['description']}" for p in projects]) if projects else "No active projects."
        
        # 5. Retrieve Skills
        skills = self.skill_engine.get_all_skills()
        skills_str = "\n".join([f"- {s['skill_name']} ({s['category']}): Level {s['level']} | Progress: {s['progress']}%" for s in skills]) if skills else "No skills tracked yet."
        
        # 6. Retrieve Personalization
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

    def generate_response(self, user_input: str) -> str:
        """Main entry point for generating a response."""
        context = self._assemble_context(user_input)
        
        history = self.working_memory.get_messages()
        
        system_msg = SystemMessage(content=(
            self.system_prompt_base +
            "\n=== COGNITIVE CONTEXT PACKAGE ===\n" + context + "\n================================\n"
        ))
        
        messages = [system_msg] + list(history) + [HumanMessage(content=user_input)]
        
        # Agentic tool-call loop (up to 5 iterations)
        output = ""
        for _ in range(5):
            response = self.llm_with_tools.invoke(messages)
            messages.append(response)
            
            # No tool calls — final text answer
            if not getattr(response, 'tool_calls', None):
                output = response.content
                break
            
            # Execute each requested tool
            for tc in response.tool_calls:
                tool_name = tc['name']
                tool_args = tc.get('args', {})
                tool_result = self.tool_map[tool_name].invoke(tool_args) if tool_name in self.tool_map else f"Unknown tool: {tool_name}"
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tc['id']))
        
        if not output:
            output = response.content or "I seem to be having trouble responding right now."
        
        # Update working memory
        self.working_memory.add_messages([HumanMessage(content=user_input), AIMessage(content=output)])
        
        # Trigger Reflection
        self.reflection.trigger_reflection(user_input, output)
        
        return output
