import pyttsx3
import sys
engine = pyttsx3.init()

def speak(text):
    """
    Speak text aloud.
    """
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()



if __name__=="__main__":
    speak("Hello! I am your assistant. How can I help you today?")
    


