# 🧠 Sane-AI

Your personal Python-based AI assistant (starter project).  
This project wraps your OS with an AI agent that can respond to natural language commands:
- Install apps
- Open websites
- Send emails (mock)
- Chat using LLM
- Remember things

---

## 📦 Project structure

Sane-AI/
├── ai_brain.py # Uses LLM to turn your prompt into an action command
├── task_router.py # Routes the command to the correct module
├── main.py # Entry point: reads user prompt and executes
├── memory.json # Stores installed apps so we don’t ask again
├── modules/
│ ├── install_apps.py # Install or open apps, checks if already installed
│ ├── open_web.py # Open websites
│ ├── send_email.py # Dummy email sender
│ └── llm_chat.py # Fallback chat with LLM
├── .env # (Not committed) Stores your API key
├── requirements.txt # Python dependencies
└── README.md # Project guide (this file)

---

## ⚙️ Setup instructions

✅ **1. Clone the repo**

git clone https://github.com/sane2002/Sane-AI.git
cd Sane-AI

✅ 2. Create and activate virtual environment

macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

Windows
python -m venv .venv
.venv\Scripts\activate


✅ 3. Install requirements
pip install -r requirements.txt

✅ 4. Add your Groq / OpenAI API key
Create a .env file in the root folder:

GROQ_API_KEY=your_key_here


🚀 Run

bash  python main.py
The assistant will ask:

"What do you want me to do?"

You can type things like:

Install vscode

Open youtube

Send email

What is the capital of France?

🧠 How it works
ai_brain.py: converts prompt → short command

task_router.py: dispatches command → correct module

modules/: actual actions (install apps, open web, etc.)

memory.json: remembers already installed apps
