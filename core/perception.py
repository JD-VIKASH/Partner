import speech_recognition as sr

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
