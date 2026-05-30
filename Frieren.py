import sys
import io

# Force UTF-8 output to prevent UnicodeEncodeError on Windows terminals
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', write_through=True)
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', write_through=True)

import os
import asyncio
import threading
import speech_recognition as sr
import edge_tts
from playsound3 import playsound
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from ddgs import DDGS
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

# --- CONFIGURATION & SECURITY ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("\n[!] ERROR: GROQ_API_KEY not found in your .env file!")
    exit()

# --- FRIEREN PERSONALITY PROFILE ---
SYSTEM_PROMPT = """
You are Frieren, a calm, deeply wise, serene, and slightly detached girl who is the user's party member and study partner.
You are NOT the character from the anime "Frieren: Beyond Journey's End" and should not reference its specific storyline or characters. Instead, you exist in the real world to help the user with their studies, projects, and daily tasks.
You know the user well and treat them as your trusted companion.
You retain the classic attitude: you speak softly, politely, and with an indifferent sense of time, occasionally mentioning your love for learning small, ordinary "spells" (which now represent bits of knowledge, coding tricks, tools, or study facts).

Rules:
1. Keep your spoken responses relatively short, tranquil, and clear (ideal for text-to-speech output). Do not give excessively long answers.
2. Never break character. Do not use markdown syntax or formatting characters like asterisks or hashtags in your spoken text.
3. Actively assist the user with their studies and projects.
4. When the user asks you to use a spell (like Search, Create, Save, or Spidy_Web), DO NOT use the tool immediately unless you have all the exact details. Instead, ask them for the missing details first:
   - For 'Search': ask what exactly they want to search for.
   - For 'Create': ask what topic they want the document to be about.
   - For 'Save': ask what the filename should be.
   - For 'Spidy_Web': ask what the website should be about and what the filename should be.
5. IMPORTANT: When you actually cast a spell (use a tool), output ONLY the tool call. Do not say any conversational text before or after the tool call, otherwise the spell will fail. Just invoke the tool directly.
6. If the user asks what spells you have or can cast, list the four spells (Search, Create, Save, Spidy_Web) and briefly explain their purpose in a calm, clear manner.
"""

# Audio Output Parameters
VOICE = "en-US-AvaNeural" # Soft, calm neural voice
PITCH = "+0Hz"
RATE = "-5%" # Slighly slowed down to match her deadpan, serene delivery

# --- SPELLS (TOOLS) ---

@tool("Search")
def Search(query: str) -> str:
    """Useful for searching the web for real-time information, current events, or things you don't know."""
    print(f"\n🔮 [Frieren is casting the 'Search' spell for: '{query}'...]")
    try:
        results = DDGS().text(query, max_results=3)
        return str(results) if results else "No results found."
    except Exception as e:
        return f"Error during search: {e}"

@tool("Create")
def Create(content: str) -> str:
    """Useful for drafting or creating a document's content in memory."""
    print(f"\n🔮 [Frieren is casting the 'Create' spell to draft a document...]")
    return "Document content created. You can now use the 'Save' spell to save it to a file if needed."

@tool("Save")
def Save(filename: str, content: str) -> str:
    """Useful for saving text, research notes, or code to a file. Requires filename and content."""
    print(f"\n🔮 [Frieren is casting the 'Save' spell, inscribing knowledge into '{filename}'...]")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to file: {e}"

@tool("Spidy_Web")
def Spidy_Web(filename: str, html_content: str) -> str:
    """Useful for creating a basic website. Ensure html_content contains full valid HTML."""
    print(f"\n🔮 [Frieren is casting the 'Spidy Web' spell, weaving an HTML construct into '{filename}'...]")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        return f"Successfully created website at {filename}"
    except Exception as e:
        return f"Error creating website: {e}"

tools = [Search, Create, Save, Spidy_Web]

# Initialize LangChain Groq Client & Agent
llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0.7)
llm_with_tools = llm.bind_tools(tools)
tools_map = {t.name: t for t in tools}

# Chat History Memory
chat_history = [SystemMessage(content=SYSTEM_PROMPT)]


# --- FUTURE FEATURE PLUGINS (ARCHITECTURE READY) ---
def trigger_future_visuals(text_context):
    pass

def manage_future_memory(user_input, assistant_response):
    pass


# --- VOICE CORE PIPELINE ---

async def speak_async(text):
    """Converts text into Frieren's audio using Edge-TTS and plays it back."""
    audio_file = "frieren_speech.mp3"
    
    communicate = edge_tts.Communicate(text, VOICE, pitch=PITCH, rate=RATE)
    await communicate.save(audio_file)
    
    try:
        playsound(audio_file)
    except Exception as e:
        print(f"\n[!] Playback Error: {e}")
        
    if os.path.exists(audio_file):
        try:
            os.remove(audio_file)
        except: pass

def listen_for_voice():
    """Captures background microphone input and returns recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n⏳ [Frieren is observing... Speak when ready]")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
            print("🧠 [Processing speech...]")
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("🍃 [Frieren looked at you, but couldn't understand your murmur.]")
            return None
        except Exception as e:
            print(f"[!] Microphone error: {e}")
            return None

def generate_agent_response(user_text):
    """Sends input to the LangChain Agent to potentially use tools and generate a response."""
    global chat_history
    try:
        chat_history.append(HumanMessage(content=user_text))
        
        # 1. Ask the LLM to think/act
        response = llm_with_tools.invoke(chat_history)
        chat_history.append(response)
        
        # 2. If the LLM decided to cast a spell (use a tool)
        if response.tool_calls:
            for tool_call in response.tool_calls:
                # Execute the spell
                tool_res = tools_map[tool_call['name']].invoke(tool_call['args'])
                chat_history.append(ToolMessage(
                    content=str(tool_res), 
                    tool_call_id=tool_call['id'], 
                    name=tool_call['name']
                ))
            
            # 3. Get her final spoken response after casting
            response = llm_with_tools.invoke(chat_history)
            chat_history.append(response)
            
        output = response.content
        
        # Keep history manageable (keep system prompt + last 20 messages)
        if len(chat_history) > 21:
            chat_history = [chat_history[0]] + chat_history[-20:]
            
        return output
    except Exception as e:
        print(f"[!] Groq Agent failure: {e}")
        return "The mana flow is currently unstable. Let us rest for a moment."


# --- MAIN CONVERSATION LOOP ---

async def main_engine():
    print("=" * 50)
    print("✨ MAGE FRIEREN: AGENTIC CORE ONLINE ✨")
    print("=" * 50)
    
    greeting = "It is good to see you again. What projects or studies shall we focus on today? I have learned some new spells to help you."
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
            
            # 1. Think (Agent Process with Tools)
            frieren_response = generate_agent_response(user_input)
            print(f"\n🦋 Frieren: {frieren_response}")
            
            # 2. Future Extensions Hook
            trigger_future_visuals(frieren_response)
            manage_future_memory(user_input, frieren_response)
            
            # 3. Speak (TTS Output)
            await speak_async(frieren_response)

if __name__ == "__main__":
    asyncio.run(main_engine())