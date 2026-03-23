
import asyncio
import os
from typing import Final

from dotenv import load_dotenv
from a2a.types import Message
from a2a.utils.message import get_message_text
from agentstack_sdk.server import Server
from agentstack_sdk.server.context import RunContext
from agentstack_sdk.a2a.types import AgentMessage
from beeai_framework.adapters.a2a.agents import A2AAgent
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from logger import get_logger

load_dotenv()
logger = get_logger(name="PolicyA2AAgent")

policy_port: Final[str] = os.getenv("POLICY_AGENT_PORT")
policy_server_agent_name: Final[str] =os.getenv("POLICY_AGENTSTACK_NAME")

if not policy_port:
  raise ValueError("POLICY_AGENT_PORT is not set")

policy_a2a_client_agent = A2AAgent(
  url=f"http://localhost:{policy_port}",
  memory=UnconstrainedMemory()
)
logger.info("Policy A2A agent created")
asyncio.run(policy_a2a_client_agent.check_agent_exists())
logger.info("Completed checking A2A agent card")

server = Server()
# Provide the server with an Agent name so it can be discovered on the Agent Stack Platform by name and called by the Healthcare agent as a handoff tool
@server.agent(
    name=policy_server_agent_name,
)
async def policy_agent_wraper(
  input: Message,
):
  # Pull the raw user message text
  prompt = get_message_text(input)
  llm_config = None

  # Delegate to the policy agent and stream the answer
  response = await policy_a2a_client_agent.run(prompt)
  response_text = getattr(response, "last_message", response).text
  yield AgentMessage(text=response_text)

# Run the server with 
def run() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("POLICY_AGENTSTACK_PORT"))
    server.run(host=host, port=port)

if __name__ == "__main__":
    run()