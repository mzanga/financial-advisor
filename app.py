from agents import Agent, Runner
from dotenv import load_dotenv
import gradio as gr

import re

from triage_agent import triage_agent

load_dotenv(override=True)

async def run_triage(message, history, refined_query_state):
    global refined_query
    # Step 1: triage conversation
    clean_history = [{"role": m["role"], "content": m["content"]} for m in history]
    messages = clean_history + [{"role": "user", "content": message}]
    triage_result = await Runner.run(triage_agent, input=messages)
    triage_reply = triage_result.final_output

    # Step 2: check if triage is done
    match = re.search(r"READY:\s*(.+)", triage_reply, re.IGNORECASE)
    if not match:
        return triage_reply, refined_query_state # still asking clarifying questions

    # Step 3: pass refined query to planner
    refined_query = match.group(1).strip()
    return f"Got it! I look for the following card for you:\n\n_{refined_query}_", refined_query


refined_query_state = gr.State(None)

if __name__ == "__main__":
    gr.ChatInterface(
        fn=run_triage,
        type="messages",
        title="💳 Credit Card Advisor",
        additional_inputs=[refined_query_state],
        additional_outputs=[refined_query_state],
    ).launch()

