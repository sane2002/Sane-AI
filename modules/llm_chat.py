from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Initialize chat history
chat_history = [
    {"role": "system", "content": "You are a helpful AI assistant."},
]


def handle(action):
    global chat_history
    prompt = action.replace("chat", "", 1).replace("ask", "", 1).strip()
    if not prompt:
        return "Please provide something to chat about."

    # Add user message to history
    chat_history.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=chat_history,
            temperature=0.2,
            stream=True,
        )
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content += chunk.choices[0].delta.content

        # Add assistant response to history
        chat_history.append({"role": "assistant", "content": content})
        return content.strip()

    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = handle(f"chat {user_input}")
        print(f"AI: {response}")
