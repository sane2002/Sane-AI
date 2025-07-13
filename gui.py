import customtkinter as ctk
from ai_brain import prompt_to_action
from task_router import route_task


def ask_ai():
    user_input = entry.get()
    if not user_input.strip():
        return
    text_area.insert(ctk.END, f"You: {user_input}\n")
    action = prompt_to_action(user_input)
    response = route_task(action)
    text_area.insert(ctk.END, f"Jarvis: {response}\n\n")
    entry.delete(0, ctk.END)


ctk.set_appearance_mode("System")  # Light, Dark, or System
ctk.set_default_color_theme("blue")  # Can be blue, green, dark-blue etc.

root = ctk.CTk()
root.title("🧠 Sane-AI Assistant")
root.geometry("700x500")

frame = ctk.CTkFrame(root)
frame.pack(padx=10, pady=10, fill=ctk.X)

entry = ctk.CTkEntry(frame, placeholder_text="Type your question here...", width=450)
entry.pack(side=ctk.LEFT, padx=(0, 10), pady=10)
entry.focus()

button = ctk.CTkButton(frame, text="Ask AI", command=ask_ai)
button.pack(side=ctk.LEFT)

text_area = ctk.CTkTextbox(root, wrap="word", width=680, height=400)
text_area.pack(padx=10, pady=(0, 10), fill=ctk.BOTH, expand=True)

root.mainloop()
