import logging
from aiogram import Bot, Dispatcher, types, F
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
        "🎓 *Welcome to EduBot!*\n\n"
        "I am your AI Tutoring Team.\n"
        "Use `/learn <topic>` to start a lesson.\n"
        "Example: `/learn Quantum Physics`",
        parse_mode="Markdown"
    )

@dp.message(Command("learn"))
async def cmd_learn(message: types.Message):
    topic = message.text.replace("/learn", "").strip() if message.text else ""
    if not topic:
        await message.answer("Please provide a topic. Ex: `/learn History of Rome`", parse_mode="Markdown")
        return

    user_id = message.from_user.id if message.from_user else 0
    config = get_config(user_id)
    
    from src.state import EduState
    initial_state: EduState = {
        "topic": topic,
        "difficulty": "Beginner",
        "explanation": "",
        "quiz_data": [],
        "current_q_index": 0,
        "user_answers": {},
        "score": 0,
        "feedback_msg": "",
        "next_recommendation": "",
        "messages": [],
        "status": "idle"
    }
    
    await message.answer(f"🚀 *Assembling the team for: {topic}*...", parse_mode="Markdown")
    
    # Run Graph until it pauses (at quiz)
    async for event in graph_app.astream(initial_state, config=config):
        for key, value in event.items():
            if key == "explainer":
                await message.answer(f"📘 *Prof. Spark says:*\n\n{value['explanation']}", parse_mode="Markdown")
            elif key == "quiz_gen":
                await message.answer("📝 *QuizMaster Q has prepared a quiz.* Get ready!")

    # Check if we are ready to ask a question
    state = graph_app.get_state(config)
    if hasattr(state, "values") and state.values.get("quiz_data"):
        await send_next_question(message.chat.id, user_id, state.values)

async def send_next_question(chat_id: int, user_id: int, state: dict):
    q_idx = state.get("current_q_index", 0)
    quiz_data = state.get("quiz_data", [])
    
    # If finished
    if not quiz_data or q_idx >= len(quiz_data):
        # Resume graph to get feedback
        config = get_config(user_id)
        # We manually trigger the next step in the graph
        async for event in graph_app.astream(None, config=config):
            if "feedback" in event:
                data = event["feedback"]
                await bot.send_message(
                    chat_id,
                    f"🏆 *Coach Iris Analysis*\n\n{data.get('feedback_msg', '')}\n\n"
                    f"Recommendation: *{data.get('next_recommendation', '')}*",
                    parse_mode="Markdown"
                )
        return

    # Send Question
    q = quiz_data[q_idx]
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(q["options"]):
        # Callback: answer:question_index:option_index
        builder.button(text=opt, callback_data=f"ans:{q_idx}:{i}")
    builder.adjust(1)
    
    await bot.send_message(
        chat_id,
        f"❓ *Question {q_idx + 1}/{len(quiz_data)}*\n\n{q['question']}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("ans:"))
async def process_quiz_answer(callback: types.CallbackQuery):
    if callback.data:
        parts = callback.data.split(":")
        if len(parts) == 3:
            _, q_idx, ans_idx = parts
            q_idx, ans_idx = int(q_idx), int(ans_idx)
        else:
            await callback.answer("Invalid answer format.", show_alert=True)
            return
    else:
        await callback.answer("No answer data.", show_alert=True)
        return
    user_id = callback.from_user.id if callback.from_user else 0
    config = get_config(user_id)
    
    # Get current state
    state = graph_app.get_state(config)
    current_values = getattr(state, "values", {})
    
    # Verify we aren't answering an old question
    if q_idx != current_values.get("current_q_index", -1):
        await callback.answer("Old question.", show_alert=True)
        return

    # Check Answer
    quiz_data = current_values.get("quiz_data", [])
    if not quiz_data or q_idx >= len(quiz_data):
        await callback.answer("Invalid question index.", show_alert=True)
        return
    question = quiz_data[q_idx]
    is_correct = (ans_idx == question.get("correct_index"))
    
    # Update State manually (LangGraph update_state)
    new_score = current_values.get("score", 0) + (1 if is_correct else 0)
    new_index = current_values.get("current_q_index", 0) + 1
    
    # Update logic
    graph_app.update_state(
        config,
        {
            "score": new_score,
            "current_q_index": new_index,
            "user_answers": {**current_values.get("user_answers", {}), q_idx: ans_idx}
        }
    )
    
    # Visual Feedback
    feedback_text = "✅ Correct!" if is_correct else f"❌ Wrong. Explanation: {question.get('explanation', '')}"
    msg_text = getattr(callback.message, "text", "") if callback.message else ""
    options = question.get("options", [])
    answer_text = options[ans_idx] if ans_idx < len(options) else ""
    if callback.message and hasattr(callback.message, "chat") and hasattr(callback.message, "message_id"):
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=f"{msg_text}\n\n**Your Answer:** {answer_text}\n{feedback_text}",
            parse_mode="Markdown"
        )
    
    # Next Step
    updated_state = graph_app.get_state(config)
    if hasattr(updated_state, "values") and callback.message and hasattr(callback.message, "chat"):
        await send_next_question(callback.message.chat.id, user_id, updated_state.values)
    await callback.answer()

async def main():
    await dp.start_polling(bot)