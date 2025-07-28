import json
from datetime import datetime

def handle(action):
    """
    Handles remembering and recalling information.
    """
    try:
        with open("memory.json", "r") as f:
            memories = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memories = []

    action_parts = action.strip().split(maxsplit=1)
    command = action_parts[0].lower()
    argument = action_parts[1] if len(action_parts) > 1 else ""

    if command == "remember":
        if not argument:
            return "What should I remember?"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memories.append({"timestamp": timestamp, "data": argument})
        
        with open("memory.json", "w") as f:
            json.dump(memories, f, indent=4)
        return f"I will remember that: '{argument}'"

    elif command == "recall":
        if not argument:
            if memories:
                return "Here are all my memories:\n" + "\n".join([f"- {item['data']}" for item in memories])
            else:
                return "I don't have any memories yet."

        relevant_memories = [item['data'] for item in memories if argument.lower() in item['data'].lower()]
        
        if relevant_memories:
            return "Here's what I found:\n" + "\n".join([f"- {memory}" for memory in relevant_memories])
        else:
            return f"I couldn't find any memories related to '{argument}'."
    
    return "I'm not sure how to handle that."
