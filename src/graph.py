from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import EduState
from .agents import explainer_agent, quiz_generator_agent, feedback_agent

# Define the nodes
workflow = StateGraph(EduState)

workflow.add_node("explainer", explainer_agent)
workflow.add_node("quiz_gen", quiz_generator_agent)
workflow.add_node("feedback", feedback_agent)

# Node to simply hold state while waiting for user input (Human-in-the-loop)
def wait_for_user(state: EduState):
    return state

workflow.add_node("human_input", wait_for_user)

# --- Routing Logic ---

def route_after_explanation(state):
    return "quiz_gen"

def route_quiz_loop(state):
    # If we have questions left to ask
    if state["current_q_index"] < len(state["quiz_data"]):
        return "human_input" # Pause for user to answer via Telegram
    return "feedback"

# --- Edges ---
workflow.set_entry_point("explainer")
workflow.add_edge("explainer", "quiz_gen")
workflow.add_conditional_edges("quiz_gen", route_quiz_loop)
workflow.add_edge("human_input", "feedback") # Logic handled in bot to re-route manually

# Setup Checkpointer for sessions
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)