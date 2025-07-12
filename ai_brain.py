# ai_brain.py
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

client = Groq()


def prompt_to_action(prompt):
    """
    Summarize a lengthy user instruction into a clear, short command like 'send email', 'install vs code', or 'open web'.
    If no command is detected, default to 'chat <prompt>'.
    """
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant that translates user prompts into specific actions. Your name is 'SANE'\n"
                    "You must ONLY answer with one of these formats:\n"
                    "- install <app>\n"
                    "- open <app>\n"
                    "- send email\n"
                    "- remember <info>\n"
                    "- recall <info>\n"
                    "- play music\n"
                    "If none fit, reply exactly as: chat <original prompt>\n"
                    "NEVER add anything else."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        stream=False,
    )
    action = response.choices[0].message.content.strip().lower()
    # print(f"AI decided: {action}")

    # Recognized commands
    known_commands = [
        "install",
        "open",
        "send email",
        "remember",
        "recall",
        "play music",
    ]

    # Check if action starts with known command
    if any(action.startswith(cmd) for cmd in known_commands):
        return action
    else:
        # Otherwise fallback: treat as chat
        return f"chat {prompt.strip()}"


if __name__ == "__main__":
    # Example usage
    user_input = "What is the capital of india?"
    action = prompt_to_action(user_input)
    print(f"Action: {action}")

    # You can then route this action to the appropriate module
    # from task_router import route_task
    # response = route_task(action)
    # print(response)
