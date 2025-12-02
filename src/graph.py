from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import EduState
from src.agents import explainer_agent, quiz_generator_agent, feedback_agent

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
    # If we have questions left to ask, go to human_input
    # Because we add 'interrupt_before', the graph will PAUSE here.
    if state["current_q_index"] < len(state["quiz_data"]):
        return "human_input" 
    return "feedback"

# --- Edges ---
workflow.set_entry_point("explainer")
workflow.add_edge("explainer", "quiz_gen")
workflow.add_conditional_edges("quiz_gen", route_quiz_loop)
workflow.add_edge("human_input", "feedback") 

# Setup Checkpointer for sessions
checkpointer = MemorySaver()

# !!! CRITICAL FIX: Add interrupt_before !!!
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_input"]
)