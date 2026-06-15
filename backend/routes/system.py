import os
import json
from fastapi import APIRouter, Depends
from backend.auth.security import get_api_key

router = APIRouter(prefix="/api/v1/system", dependencies=[Depends(get_api_key)])

STATUS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "db", "system_status.json"))

def read_status() -> str:
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f:
                data = json.load(f)
                return data.get("state", "AWAKE")
    except Exception as e:
        print(f"[!] Warning: Failed to read system status: {e}")
    return "AWAKE"

def write_status(state: str):
    try:
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, "w") as f:
            json.dump({"state": state}, f)
    except Exception as e:
        print(f"[!] Warning: Failed to write system status: {e}")

@router.get("/status")
async def get_system_status():
    return {"status": read_status()}

@router.post("/sleep")
async def set_system_sleep():
    write_status("SLEEPING")
    return {"status": "SLEEPING"}

@router.post("/wake")
async def set_system_wake():
    write_status("AWAKE")
    return {"status": "AWAKE"}
