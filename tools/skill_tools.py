from langchain_core.tools import tool
from state.skill_engine import SkillEngine

skill_engine = SkillEngine()

@tool("AddSkill")
def AddSkill(skill_name: str, category: str = "General", level: str = "Beginner", progress: int = 0) -> str:
    """Useful for tracking a new skill the user wants to learn."""
    skill_engine.add_skill(skill_name, category, level, progress)
    return f"Skill '{skill_name}' added successfully to tracking."

@tool("UpdateSkillProgress")
def UpdateSkillProgress(skill_name: str, progress_increment: int) -> str:
    """Useful for increasing the progress of a specific skill. Progress is a number from 1 to 100. Pass the amount to INCREASE it by (e.g., 5 or 10)."""
    skill_engine.update_skill_progress(skill_name, progress_increment)
    return f"Progress for skill '{skill_name}' has been increased by {progress_increment}%."

def get_skill_tools():
    return [AddSkill, UpdateSkillProgress]
