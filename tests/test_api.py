"""
Frieren API Test Suite
Tests all /api/v1/ endpoints.

Usage:
  1. Start backend:  uvicorn backend.app:app --reload
  2. Run tests:      python tests/test_api.py
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = os.getenv("FRIEREN_API_KEY", "frieren-dev-key-123")
HEADERS = {"X-API-Key": API_KEY}
USER_ID = "vikash"
DEVICE_ID = "test_runner"

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

def test(name: str, fn):
    try:
        fn()
        print(f"{PASS} {name}")
    except AssertionError as e:
        print(f"{FAIL} {name} — {e}")
    except Exception as e:
        print(f"{FAIL} {name} — Unexpected error: {e}")


# ─── Health ─────────────────────────────────────────────────────────────────
def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "status" in data, "Missing 'status' key"
    assert data["status"] == "healthy", f"Status was '{data['status']}'"
    assert "sqlite" in data, "Missing 'sqlite' key"
    print(f"  {INFO} Health payload: {data}")

# ─── State Routes ─────────────────────────────────────────────────────────
def test_get_profile():
    r = requests.get(f"{BASE_URL}/profile", headers=HEADERS)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

def test_get_goals():
    r = requests.get(f"{BASE_URL}/goals", headers=HEADERS)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert isinstance(r.json(), list), "Expected a list response"

def test_get_projects():
    r = requests.get(f"{BASE_URL}/projects", headers=HEADERS)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert isinstance(r.json(), list), "Expected a list response"

def test_get_skills():
    r = requests.get(f"{BASE_URL}/skills", headers=HEADERS)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    result = r.json()
    assert isinstance(result, list), "Expected a list response"
    print(f"  {INFO} {len(result)} skill(s) tracked.")

def test_get_context():
    r = requests.get(f"{BASE_URL}/context", headers=HEADERS)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    for key in ("profile", "goals", "projects", "skills"):
        assert key in data, f"Missing key '{key}' in context response"

# ─── Auth Guard ─────────────────────────────────────────────────────────
def test_auth_rejection():
    r = requests.get(f"{BASE_URL}/profile", headers={"X-API-Key": "wrong-key"})
    assert r.status_code == 403, f"Expected 403 for bad key, got {r.status_code}"

# ─── Memory ─────────────────────────────────────────────────────────────
def test_add_memory():
    payload = {
        "user_id": USER_ID,
        "device_id": DEVICE_ID,
        "content": "Test memory: Frieren backend test suite ran successfully.",
        "category": "event",
        "importance_score": 6.0
    }
    r = requests.post(f"{BASE_URL}/memory", json=payload, headers=HEADERS)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["status"] == "success"
    assert "memory_id" in data
    print(f"  {INFO} Memory stored to: {data['collection']} (ID: {data['memory_id']})")

# ─── Chat ─────────────────────────────────────────────────────────────────
def test_chat():
    payload = {
        "user_id": USER_ID,
        "device_id": DEVICE_ID,
        "message": "Hello Frieren. What skills am I currently learning?"
    }
    r = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "response" in data, "Missing 'response' key"
    assert "session_id" in data, "Missing 'session_id' key"
    assert len(data["response"]) > 0, "Response was empty"
    print(f"  {INFO} Session: {data['session_id']}")
    print(f"  {INFO} Response: {data['response'][:120]}...")


# ─── Runner ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  FRIEREN BACKEND — API VERIFICATION SUITE")
    print("=" * 55 + "\n")

    test("Health Check",           test_health)
    test("Auth Rejection (403)",   test_auth_rejection)
    test("GET /profile",           test_get_profile)
    test("GET /goals",             test_get_goals)
    test("GET /projects",          test_get_projects)
    test("GET /skills",            test_get_skills)
    test("GET /context",           test_get_context)
    test("POST /memory",           test_add_memory)
    test("POST /chat",             test_chat)

    print("\n" + "=" * 55)
    print("  TEST RUN COMPLETE")
    print("=" * 55 + "\n")
