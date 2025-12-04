# EduBot: Adaptive AI Tutoring Team

**EduBot** is a Telegram-based, multi-agent tutoring system powered by **Google Gemini** and **LangGraph**. It simulates a team of three distinct AI agents working together to teach you any topic, test your knowledge, and adapt the difficulty based on your performance.

## 🚀 Key Features

  * **📘 The Professor (Explainer Agent)**: Breaks down complex topics into clear, digestible lessons with analogies.
  * **📝 The Examiner (Quiz Agent)**: Generates interactive 3-question quizzes to test your understanding.
  * **🏆 The Mentor (Feedback Agent)**: Analyzes your quiz score and dynamically adjusts the difficulty (Advance, Retry, or Demote).
  * **🔄 Adaptive Loop**: The system uses a state machine to ensure you master a topic before moving on.
  * **💬 Telegram Interface**: clean UI with interactive buttons and rich text formatting.

## 🛠️ Tech Stack

  * **Language**: Python 3.10+
  * **Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) (Stateful multi-agent workflows)
  * **LLM**: Google Gemini 1.5 Flash (via langchain-google-genai)
  * **Frontend**: Aiogram 3.x (Asynchronous Telegram Bot API)
  * **Deployment**: Ready for Railway, Render, or Docker.

## 📂 Project Structure

``` 
EduBot/
├── .env                  # API Keys (Not committed to Git)
├── requirements.txt      # Python dependencies
├── Procfile              # Deployment command for Cloud platforms
├── run.py                # Entry point (includes dummy server for health checks)
├── auto_fix.py           # Utility script to find valid Gemini models
└── src/
    ├── __init__.py
    ├── config.py         # Configuration loader
    ├── state.py          # State definitions (TypedDict)
    ├── agents.py         # Gemini prompts & logic
    ├── graph.py          # Workflow definition (Nodes & Edges)
    └── bot.py            # Telegram handlers & UI

```

## ⚡ Local Setup Guide

### 1\. Prerequisites

  * Python 3.10 or higher.
  * **Telegram Bot Token**: Get it from [@BotFather](https://t.me/BotFather) on Telegram.
  * **Google API Key**: Get it from [Google AI Studio](https://aistudio.google.com/).

### 2\. Installation

1.  **Clone the repository:**
    ``` bash
    git clone https://github.com/yourusername/edubot.git
    cd EduBot
    
    ```
2.  **Create a Virtual Environment:**
    ``` bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    
    # Mac/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    
    ```
3.  **Install Dependencies:**
    ``` bash
    pip install -r requirements.txt
    
    ```

### 3\. Configuration

Create a file named `.env` in the root directory and paste your keys:

``` 
GOOGLE_API_KEY=AIzaSy...
TELEGRAM_BOT_TOKEN=123456:ABC...

```

### 4\. Run the Bot

``` bash
python run.py

```

You should see: `🚀 Starting Bot Polling...`

## ☁️ Deployment

### Option 1: Railway (Recommended)

1.  Push your code to GitHub.
2.  Go to [Railway.app](https://railway.app/) -\> "New Project" -\> "Deploy from GitHub".
3.  Add your variables (`GOOGLE_API_KEY`, `TELEGRAM_BOT_TOKEN`) in the **Variables** tab.
4.  Railway should automatically detect `python run.py` as the start command.

### Option 2: Render

1.  Create a new **Background Worker** (Recommended) or **Web Service**.
2.  Connect your GitHub repo.
3.  **Build Command:** `pip install -r requirements.txt`
4.  **Start Command:** `python run.py`
5.  Add your Environment Variables.
6.  *Note:* If using a "Web Service", the included `run.py` has a dummy server to prevent timeout errors.

## 🔧 Troubleshooting

| Error                                           | Cause                                          | Fix                                                                                                   |
| :---------------------------------------------: | :--------------------------------------------: | :---------------------------------------------------------------------------------------------------: |
| **ValueError: TELEGRAM\_BOT\_TOKEN is not set** | The `.env` file is missing or not read.        | Ensure `.env` is in the **root** folder, not `src/`.                                                  |
| **404 models/gemini-1.5-flash is not found**    | Your API key doesn't support this model alias. | Run `python auto_fix.py` to find the correct model name for your key.                                 |
| **Port scan timeout (Render)**                  | App didn't open a port.                        | Use a **Background Worker** on Render, or use the updated `run.py` which includes a dummy web server. |
| **ModuleNotFoundError: No module named 'src'**  | Running script from wrong folder.              | Always run `python run.py` from the root `EduBot/` folder.                                            |

## 🎮 How to Use

1.  Open your bot in Telegram.
2.  Send `/start`.
3.  Type `/learn <topic>` (e.g., `/learn Photosynthesis`).
4.  Read the lesson, answer the quiz via buttons, and get your feedback\!

## 📜 License

This project is open-source. Feel free to fork and improve\!
