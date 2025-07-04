from voice_input import listen
from speak import speak
from ai_brain import prompt_to_action
from task_router import route_task
from dotenv import load_dotenv
import os




def main():
    speak("Hello! I am your assistant. How can I help you today?")

    while True:
        # Listen to the user (you can replace with input() if you want text mode)
        # prompt = listen()
        prompt=input()

        if prompt.lower() in ['exit', 'quit', 'bye']:
            speak("Goodbye!")
            break

        # Ask AI what action to take (like 'install chrome')
        action = prompt_to_action(prompt)
        print(f"AI decided: {action}")

        # Route the action to the right module (install, open website, etc.)
        result = route_task(action)

        # Speak and show the result
        speak(result)

if __name__ == "__main__":
    main()
