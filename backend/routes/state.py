from fastapi import APIRouter, Depends
from backend.services.orchestration import OrchestrationService
from backend.auth.security import get_api_key

router = APIRouter(prefix="/api/v1", dependencies=[Depends(get_api_key)])
orchestrator = OrchestrationService()

@router.get("/profile")
async def get_profile():
    return orchestrator.get_context()["profile"]

@router.get("/goals")
async def get_goals():
    return orchestrator.get_context()["goals"]

@router.get("/projects")
async def get_projects():
    return orchestrator.get_context()["projects"]

@router.get("/skills")
async def get_skills():
    return orchestrator.get_context()["skills"]

@router.get("/context")
async def get_context():
    return orchestrator.get_context()
