# Frieren: Agentic Core

✨ **MAGE FRIEREN: AGENTIC CORE ONLINE** ✨

An AI voice assistant built with Python that serves as your calm, serene study partner and party member. Frieren is not just a conversational bot; she is an agent equipped with "spells" (tools) to help you research, write files, and even generate basic websites, all while keeping her cool, tranquil, and detached demeanor intact.

## Features
* **Agentic Capabilities**: Powered by LangChain and the Groq API (Llama-3.1-8b-instant), allowing her to autonomously decide when and how to use her spells.
* **Voice Interaction**: Frieren speaks with a calm, serene voice using Edge-TTS (`en-US-AvaNeural`).
* **Speech Recognition**: Actively listens to your voice via your microphone and responds intelligently.
* **Spells (Tools)**:
  * **Search**: Uses DuckDuckGo to search the web for real-time information and current events.
  * **Create**: Drafts documents and content in memory based on your topics.
  * **Save**: Inscribes knowledge, research notes, or code to your local machine.
  * **Spidy_Web**: Weaves an HTML construct to generate basic websites and save them locally.

## Setup & Configuration

### Prerequisites
Make sure you have Python installed, along with a working microphone and speakers. You'll need the following libraries:
- `SpeechRecognition`
- `edge-tts`
- `playsound3`
- `python-dotenv`
- `langchain-groq`
- `langchain-core`
- `duckduckgo-search`

### Installation
1. Clone this repository.
2. Install the necessary dependencies (you can use `pip install` for the packages listed above).
3. Create a `.env` file in the root directory of the project.
4. Add your Groq API key to the `.env` file:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage
To start your session with Frieren, simply run the main script:
```bash
python Frieren.py
```

Wait for the prompt:
`⏳ [Frieren is observing... Speak when ready]`

Once you see this, start speaking to her. She will listen, process your request, use her spells if necessary, and reply with audio output.

## Shutdown Commands
To stop the application gracefully, simply say one of the following phrases to her:
* "exit"
* "quit"
* "stop studying"
* "goodbye"
* "go to sleep"
* "sleep frieren"
* "turn off"
* "shut down"
