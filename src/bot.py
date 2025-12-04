import logging
from typing import Any
from aiogram import Bot, Dispatcher, types, F, html
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from langchain_core.runnables import RunnableConfig

from src.config import Config
from src.graph import app as graph_app

# Validation
if not Config.TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- Helpers ---
def get_config(user_id: int) -> RunnableConfig:
    return {"configurable": {"thread_id": str(user_id)}}

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🎓 <b>Welcome to EduBot!</b>\n\n"
        "I am your AI Tutoring Team.\n"
        "Use <code>/learn &lt;topic&gt;</code> to start a lesson.\n"
        "Example: <code>/learn Quantum Physics</code>",
        parse_mode="HTML"
    )

@dp.message(Command("learn"))
async def cmd_learn(message: types.Message):
    if not message.text or not message.from_user:
        return

    topic = message.text.replace("/learn", "").strip()
    if not topic:
        await message.answer("Please provide a topic. Ex: <code>/learn History of Rome</code>", parse_mode="HTML")
        return

    user_id = message.from_user.id
    config = get_config(user_id)
    
    # Initialize State
    initial_state: Any = {
        "topic": topic,
        "difficulty": "Beginner",
        "current_q_index": 0,
        "score": 0,
        "user_answers": {}
    }
    
    await message.answer(f"🚀 <b>Assembling the team for: {html.quote(topic)}</b>...", parse_mode="HTML")
    
    # Run Graph
    async for event in graph_app.astream(initial_state, config=config):
        for key, value in event.items():
            if key == "explainer":
                # Sanitize content just in case, but keep basic structure if possible
                # For simplicity, we assume LLM outputs clean text, but HTML mode handles _ and * safely.
                # If LLM outputs markdown like **bold**, it will just show as asterisks in HTML mode, which is safe.
                explanation = html.quote(value['explanation'])
                await message.answer(f"📘 <b>Prof. Spark says:</b>\n\n{explanation}", parse_mode="HTML")
            elif key == "quiz_gen":
                await message.answer("📝 <b>QuizMaster Q has prepared a quiz.</b> Get ready!", parse_mode="HTML")

    # Check for questions
    state = graph_app.get_state(config)
    if state.values.get("quiz_data"):
        await send_next_question(message.chat.id, user_id, state.values)

async def send_next_question(chat_id: int, user_id: int, state: dict):
    q_idx = state["current_q_index"]
    quiz_data = state["quiz_data"]
    
    # If finished
    if q_idx >= len(quiz_data):
        config = get_config(user_id)
        async for event in graph_app.astream(None, config=config):
            if "feedback" in event:
                data = event["feedback"]
                fb_msg = html.quote(data['feedback_msg'])
                rec = html.quote(data['next_recommendation'])
                await bot.send_message(
                    chat_id,
                    f"🏆 <b>Coach Iris Analysis</b>\n\n{fb_msg}\n\n"
                    f"Recommendation: <b>{rec}</b>",
                    parse_mode="HTML"
                )
        return

    # Send Question
    q = quiz_data[q_idx]
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(q["options"]):
        builder.button(text=opt, callback_data=f"ans:{q_idx}:{i}")
    builder.adjust(1)
    
    question_text = html.quote(q['question'])
    await bot.send_message(
        chat_id,
        f"❓ <b>Question {q_idx + 1}/{len(quiz_data)}</b>\n\n{question_text}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("ans:"))
async def process_quiz_answer(callback: types.CallbackQuery):
    if not callback.data or not callback.from_user or not isinstance(callback.message, types.Message):
        return

    _, q_idx, ans_idx = callback.data.split(":")
    q_idx, ans_idx = int(q_idx), int(ans_idx)
    user_id = callback.from_user.id
    config = get_config(user_id)
    
    state = graph_app.get_state(config)
    current_values = state.values
    
    if q_idx != current_values["current_q_index"]:
        await callback.answer("Old question.", show_alert=True)
        return

    question = current_values["quiz_data"][q_idx]
    is_correct = (ans_idx == question["correct_index"])
    
    # Update State
    new_score = current_values["score"] + (1 if is_correct else 0)
    new_index = current_values["current_q_index"] + 1
    
    graph_app.update_state(
        config,
        {
            "score": new_score,
            "current_q_index": new_index,
            "user_answers": {**current_values["user_answers"], q_idx: ans_idx}
        }
    )
    
    feedback_text = "✅ <b>Correct!</b>" if is_correct else f"❌ <b>Wrong.</b> Explanation: {html.quote(question['explanation'])}"
    
    # Edit the message with HTML mode (safe from underscores)
    # Note: We cannot easily access the 'original text' perfectly if it had formatting, 
    # but for quiz questions, we reconstruct it.
    original_q = html.quote(question['question'])
    selected_opt = html.quote(question['options'][ans_idx])
    
    await callback.message.edit_text(
        f"❓ <b>Question {q_idx + 1}</b>\n\n{original_q}\n\n"
        f"👉 <b>Your Answer:</b> {selected_opt}\n"
        f"{feedback_text}",
        parse_mode="HTML"
    )
    
    updated_state = graph_app.get_state(config)
    await send_next_question(callback.message.chat.id, user_id, updated_state.values)
    await callback.answer()

async def main():
    print("Bot is polling...")
    # This forces Telegram to forget any previous connections/webhooks
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)