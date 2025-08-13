from .orchestration import pattern
from .agent import BaseAgent

@pattern
def notify(agent: BaseAgent, msg: str, source="User"):
    notify_text = f"A message from {source}:\n{msg}"
    agent.add_user_message(notify_text)

@pattern
def tell(speaker: BaseAgent, listener: BaseAgent, instruction="Your current status.", model="glm-4.5"):
    instruction_prompt = f"Your task now is to send a message to agent {listener.get_id()}. The purpose is communication and information exchange. Explain honestly in detail what you know about <{instruction}>. Your full response will be sent directly. So begin directly with the message's content."
    message = speaker.run(instruction_prompt, cli="no-tools", model=model).content
    message_prompt = f"Your inbox: message from agent {speaker.get_id()}:\n{message}"
    listener.add_user_message(message_prompt)

@pattern
def get_status(agent: BaseAgent, n_exchanges: int = 3, model: str = "glm-4.5"):
    """
    Generate a status report of the agent's recent work.
    
    Args:
        n_exchanges: Number of recent user interactions to summarize.
        model: Model to use for generating the report.
    
    Returns:
        A structured status report.
    """
    prompt = f"""Analyze and summarize your work on the last {n_exchanges} user interactions (<5 sentences).

Structure your response as:
Analysis: [What types of tasks were worked on, any patterns or challenges encountered]
Key Outcomes: [What was accomplished, created, fixed, or discovered]
Current Status: [Any pending items, next steps, or relevant context]"""
    
    return agent.run(prompt, model=model, ephemeral=True).content

