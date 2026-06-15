import os
import edge_tts
from playsound3 import playsound

VOICE = "en-US-AvaNeural"
PITCH = "+0Hz"
RATE = "-5%"

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
