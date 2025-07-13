from voice_input import listen
from speak import speak
from ai_brain import prompt_to_action
from task_router import route_task
# from dotenv import load_dotenv
# import os


def main():
    speak("Hello! I am your assistant. How can I help you today?")

    while True:
        # Listen to the user (you can replace with input() if you want text mode)
        # prompt = listen()
        print("Waiting for your input...")
        prompt = input()

        if prompt.lower() in ["exit", "quit", "bye"]:
            speak("Goodbye!")
            break
        try:
            # Ask AI what action to take (like 'install chrome')
            action = prompt_to_action(prompt)
            # print(f"AI decided: {action}")

            # # Route the action to the right module (install, open website, etc.)
            # result = route_task(action)
            # # print(f"Result: {result}")
            # speak(result)

            # ...existing code...
            result = route_task(action)
            print(f"[DEBUG] result: {result}")
            speak(str(result))
        except Exception as e:
            print(f"[ERROR] {e}")
            speak("Sorry, something went wrong.")


if __name__ == "__main__":
    # main()
    from gui import *
