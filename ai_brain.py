from openai import OpenAI
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv() 

client = Groq()

def prompt_to_action(prompt):
    """
    Call OpenAI to convert user text into a clear command like 'install chrome'.
    """
    response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
      
        {"role": "system", "content": "You are an assistant. Reply ONLY with a short command like 'install chrome', 'open youtube', etc."},
        {"role": "user", "content": prompt}
      
    ],
    temperature=0.6,
    stream=True
)
    content = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content += chunk.choices[0].delta.content
    
    return content.strip()