import sys
import io
import os
import asyncio
from dotenv import load_dotenv

# Force UTF-8 output to prevent UnicodeEncodeError on Windows terminals
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', write_through=True)
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', write_through=True)

# Load env before importing engines that require keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("\n[!] ERROR: GROQ_API_KEY not found in your .env file!")
    exit()

from core.perception import listen_for_voice
from core.output import speak_async
import requests

async def main_engine():
    print("=" * 50)
    print("✨ MAGE FRIEREN: WINDOWS CLIENT ONLINE ✨")
    print("=" * 50)
    
    API_URL = "http://localhost:8000/api/v1"
    HEADERS = {"X-API-Key": os.getenv("FRIEREN_API_KEY")}
    
    # Check if backend is alive
    try:
        health = requests.get(f"{API_URL}/health")
        if health.status_code == 200:
            print("[Backend Connected]")
    except Exception:
        print("[!] Cannot connect to Frieren Backend. Please run 'python backend/app.py' first.")
        return

    greeting = "It is good to see you again. My cognitive pathways are connected to the central backend. What projects or studies shall we focus on today?"
    print(f"\n🦋 Frieren: {greeting}")
    await speak_async(greeting)
    
    while True:
        user_input = listen_for_voice()
        
        if user_input:
            print(f"👤 You: {user_input}")
            
            user_text_lower = user_input.lower()
            shutdown_phrases = ["exit", "quit", "stop studying", "goodbye", "go to sleep", "sleep frieren", "turn off", "shut down"]
            if any(phrase in user_text_lower for phrase in shutdown_phrases):
                farewell = "I understand. Take a good rest. We can continue our work later."
                print(f"\n🦋 Frieren: {farewell}")
                await speak_async(farewell)
                break
            
            # 1. Cognitive Reasoning via Backend HTTP Request
            payload = {
                "user_id": "vikash", # Single user default
                "device_id": "windows",
                "message": user_input
            }
            try:
                res = requests.post(f"{API_URL}/chat", json=payload, headers=HEADERS)
                if res.status_code == 200:
                    data = res.json()
                    frieren_response = data["response"]
                else:
                    frieren_response = f"Backend error: {res.status_code} {res.text}"
            except Exception as e:
                frieren_response = f"Network error connecting to brain: {e}"

            print(f"\n🦋 Frieren: {frieren_response}")
            
            # 2. Speak (TTS Output)
            await speak_async(frieren_response)

if __name__ == "__main__":
    asyncio.run(main_engine())