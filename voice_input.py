import speech_recognition as sr

def listen():
    """
    Listen to user's voice and convert to text.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except Exception:
        print("Sorry, couldn't understand.")
        return ""
