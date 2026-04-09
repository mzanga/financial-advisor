from agents import Agent, Runner
from dotenv import load_dotenv
import gradio as gr

import re

from triage_agent import triage_agent
from credit_card_agent import cc_search_agent

load_dotenv(override=True)

# --- SUB-FUNCTION 1: TRIAGE ---
async def run_triage(messages):
    """
    Refines the user's need. Returns the agent's text or a 'READY' query.
    """
    result = await Runner.run(triage_agent, input=messages)
    return result.final_output

# --- SUB-FUNCTION 2: SEARCH ---
async def run_search(refined_query):
    """
    Executes the specialized search based on the refined criteria.
    """
    search_prompt = (
        f"Act as a Financial Expert. Search for the best credit cards for this profile: {refined_query}. "
        "Provide a comparison table of the top 3 matches and cite your sources."
    )
    result = await Runner.run(cc_search_agent, input=search_prompt)
    return result.final_output

async def run_agents(message, history, refined_query_state):
    global refined_query
    # Step 1: triage conversation
    clean_history = [{"role": m["role"], "content": m["content"]} for m in history]
    messages = clean_history + [{"role": "user", "content": message}]
    triage_reply = await run_triage(messages)

    # Step 2: check if triage is done
    match = re.search(r"READY:\s*(.+)", triage_reply, re.IGNORECASE)
    if not match:
        return triage_reply, refined_query_state # still asking clarifying questions

    # Step 3: pass refined query to planner
    refined_query = match.group(1).strip()

    search_results = await run_search(refined_query)
    # return f"Got it! I look for the following card for you:\n\n_{refined_query}_", refined_query
    final_response = (
        f"### ✅ Profile Confirmed\n"
        f"**Searching for:** {refined_query}\n\n"
        f"---\n"
        f"{search_results}"
    )

    return final_response, refined_query

refined_query_state = gr.State(None)

if __name__ == "__main__":
    gr.ChatInterface(
        fn=run_agents,
        type="messages",
        title="💳 Credit Card Advisor",
        additional_inputs=[refined_query_state],
        additional_outputs=[refined_query_state]
    ).launch()

