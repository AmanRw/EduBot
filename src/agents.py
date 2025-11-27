import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.config import Config
from src.state import EduState

# Configure Logging
logger = logging.getLogger(__name__)

# Pylance Fix: Ensure API Key is present
if not Config.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in environment variables")

from pydantic import SecretStr

llm = ChatGoogleGenerativeAI(
    model=Config.MODEL_NAME, 
    temperature=0.7,
    api_key=SecretStr(Config.GOOGLE_API_KEY)
)

# --- Helper: JSON Cleaner ---
def clean_and_parse_json(content: str):
    """Robustly extracts JSON from LLM response."""
    try:
        # Remove code blocks if present
        clean_text = content.replace("```json", "").replace("```", "").strip()
        
        # Determine start/end of JSON structure if extra text exists
        if clean_text.startswith("[") and "]" in clean_text:
            end_idx = clean_text.rfind("]") + 1
            clean_text = clean_text[:end_idx]
        elif clean_text.startswith("{") and "}" in clean_text:
            end_idx = clean_text.rfind("}") + 1
            clean_text = clean_text[:end_idx]
            
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON Parse Error: {e}. Content: {content}")
        return None

# --- 1. The Professor (Explainer) ---
async def explainer_agent(state: EduState):
    prompt = ChatPromptTemplate.from_template(
        """You are Prof. Spark, an expert tutor.
        Explain the topic "{topic}" to a student at a {difficulty} level.
        Use clear headings, bullet points, and an analogy.
        Keep it under 300 words.
        """
    )
    chain = prompt | llm
    response = await chain.ainvoke({"topic": state["topic"], "difficulty": state["difficulty"]})
    return {"explanation": response.content, "status": "explaining"}

# --- 2. The Examiner (Quiz Generator) ---
async def quiz_generator_agent(state: EduState):
    prompt = ChatPromptTemplate.from_template(
        """You are QuizMaster Q. 
        Generate 3 multiple-choice questions for the topic "{topic}" at {difficulty} level.
        
        RETURN ONLY RAW JSON. No Markdown. No ```json``` tags.
        Format:
        [
            {{
                "id": 0,
                "question": "Question text?",
                "options": ["A", "B", "C", "D"],
                "correct_index": 0,
                "explanation": "Why A is correct."
            }}
        ]
        """
    )
    chain = prompt | llm
    response = await chain.ainvoke({"topic": state["topic"], "difficulty": state["difficulty"]})
    
    quiz_data = clean_and_parse_json(str(response.content))
    
    if not quiz_data:
        # Fallback if generation fails
        quiz_data = []
        
    return {
        "quiz_data": quiz_data, 
        "current_q_index": 0, 
        "score": 0, 
        "user_answers": {},
        "status": "quizzing"
    }

# --- 3. The Mentor (Feedback) ---
async def feedback_agent(state: EduState):
    prompt = ChatPromptTemplate.from_template(
        """You are Coach Iris. The student scored {score} out of {total} on "{topic}" ({difficulty}).
        
        Analyze their performance.
        1. Give constructive feedback.
        2. Recommend: "ADVANCE" (next level), "RETRY" (same level), or "DEMOTE" (easier).
        
        RETURN ONLY RAW JSON. Format:
        {{
            "feedback": "Your text here...",
            "recommendation": "ADVANCE"
        }}
        """
    )
    chain = prompt | llm
    response = await chain.ainvoke({
        "score": state["score"], 
        "total": len(state["quiz_data"]),
        "topic": state["topic"],
        "difficulty": state["difficulty"]
    })
    
    data = clean_and_parse_json(str(response.content))
    
    if not data:
        data = {"feedback": "Good effort! (Error generating detailed feedback)", "recommendation": "RETRY"}
        
    return {
        "feedback_msg": data.get("feedback", "No feedback provided."),
        "next_recommendation": data.get("recommendation", "RETRY"),
        "status": "feedback"
    }