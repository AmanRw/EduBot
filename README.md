🎓 **EduBot: Adaptive AI Tutoring Team**

EduBot is a Telegram-based multi-agent tutoring system powered by Google Gemini and LangGraph. It simulates a team of three distinct AI agents working together to teach you any topic, test your knowledge, and adapt the difficulty based on your performance.

🚀 *Key Features*

Multi-Agent Architecture:

📘 Prof. Spark (Explainer): Breaks down complex topics with analogies and clear formatting.

📝 QuizMaster Q (Examiner): Generates interactive multiple-choice quizzes.

🏆 Coach Iris (Mentor): Analyzes your scores and dynamically adjusts difficulty (Advance/Demote/Retry).

Adaptive Learning: The difficulty level shifts automatically based on your quiz performance.

State Management: Uses LangGraph to maintain lesson context and score history across the conversation.

Telegram Integration: Interactive buttons for quizzes and clean Markdown responses.

🛠️ *Tech Stack*

Language: Python 3.10+

LLM: Google Gemini 1.5 Flash (via langchain-google-genai)

Orchestration: LangGraph (State machines for AI)

Frontend: Aiogram 3.x (Telegram Bot API)

Validation: Pylance/MyPy compliant strict typing.

📂 **Project Structure**

EduBot/
├── .env                  # API Keys (Create this file)
├── requirements.txt      # Python dependencies
├── run.py                # Application entry point
├── auto_fix.py           # Utility to find valid Gemini models
└── src/
    ├── __init__.py
    ├── config.py         # Configuration loader
    ├── state.py          # LangGraph TypedDict definitions
    ├── agents.py         # Gemini prompts & logic (Explainer, Quiz, Feedback)
    ├── graph.py          # Workflow definition (Nodes & Edges)
    └── bot.py            # Telegram message handlers & UI


⚡ **Quick Start Guide**

1. Prerequisites

Python 3.10 or higher installed.

A Telegram Bot Token (Get it from @BotFather).

A Google AI Studio API Key (Get it here).

2. Installation

Clone the repository (or create the folder) and navigate into it:

cd EduBot


Create and activate a virtual environment:

Windows:

python -m venv .venv
.venv\Scripts\activate


Mac/Linux:

python3 -m venv .venv
source .venv/bin/activate


Install dependencies:

pip install -r requirements.txt


3. Configuration

Create a file named .env in the root directory and add your keys:

GOOGLE_API_KEY=AIzaSy...
TELEGRAM_BOT_TOKEN=123456:ABC...


4. Run the Bot

Execute the runner script from the root folder:

python run.py


You should see: INFO:root:Bot is polling...

🎮 How to Use

Open your bot in Telegram.

Send /start to see the welcome message.

Start a lesson:

/learn Quantum Physics

/learn The History of Pizza

/learn Python Programming

The Flow:

Read: Prof. Spark explains the concept.

Quiz: QuizMaster Q sends questions. Click the buttons to answer.

Feedback: Coach Iris grades you and decides if you move to the next level.

🔧 Troubleshooting

Error: ModuleNotFoundError: No module named 'src'

Fix: Ensure you run python run.py from the root EduBot/ folder, not inside the src/ folder.

Error: 404 models/gemini-1.5-flash is not found

Fix: Your API key might not support the specific model name alias.

Solution: Run the auto-fix script included in the repo:

python auto_fix.py


Copy the recommended model name into src/config.py.

Error: Import "dotenv" could not be resolved

Fix: You may have installed the wrong package. Run:

pip uninstall dotenv
pip install python-dotenv


VS Code Pylance Errors

If you see red squiggles despite the code running fine, ensure your VS Code is using the virtual environment.

Press Ctrl+Shift+P -> Python: Select Interpreter -> Select the one marked ('.venv': venv).

📜 *License*

This project is open-source and available for educational purposes.