from typing import TypedDict, List, Dict, Any, Optional
import operator
from langchain_core.messages import BaseMessage

class QuizQuestion(TypedDict):
    id: int
    question: str
    options: List[str]
    correct_index: int
    explanation: str

class EduState(TypedDict):
    # User Context
    topic: str
    difficulty: str  # Beginner, Intermediate, Advanced
    
    # Agent Outputs
    explanation: str
    quiz_data: List[QuizQuestion]
    
    # Quiz State
    current_q_index: int
    user_answers: Dict[int, int] # Map question index to option index
    score: int
    
    # Feedback State
    feedback_msg: str
    next_recommendation: str # ADVANCE, RETRY, DEMOTE
    
    # Flow Control
    messages: List[BaseMessage]
    status: str # "idle", "explaining", "quizzing", "feedback"