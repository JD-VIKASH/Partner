from langchain_core.tools import tool
from state.goal_management import GoalManagementSystem
from state.project_engine import ProjectEngine

goal_system = GoalManagementSystem()
project_engine = ProjectEngine()

@tool("AddGoal")
def AddGoal(title: str, description: str, goal_type: str) -> str:
    """Useful for adding a new goal to the user's long-term or short-term tracking."""
    goal_system.add_goal(title, description, goal_type)
    return f"Goal '{title}' added successfully."

@tool("CompleteGoal")
def CompleteGoal(goal_id: int) -> str:
    """Marks a goal as completed."""
    goal_system.complete_goal(goal_id)
    return f"Goal {goal_id} marked as complete."

@tool("AddProject")
def AddProject(name: str, description: str) -> str:
    """Useful for tracking a new project."""
    project_engine.add_project(name, description)
    return f"Project '{name}' created."

def get_goal_tools():
    return [AddGoal, CompleteGoal, AddProject]
