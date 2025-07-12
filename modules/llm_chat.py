from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()


def handle(action):
    prompt = action.replace("chat", "", 1).replace("ask", "", 1).strip()
    if not prompt:
        return "Please provide something to chat about."
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        stream=True,
    )
    content = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content += chunk.choices[0].delta.content
    return content.strip()
