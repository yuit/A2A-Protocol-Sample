import asyncio
import os
from typing import Final

from dotenv import load_dotenv
from a2a.types import Message
from a2a.utils.message import get_message_text
from agentstack_sdk.server import Server
from agentstack_sdk.a2a.types import AgentMessage
from beeai_framework.adapters.a2a.agents import A2AAgent
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory

load_dotenv()

research_port: Final[str | None] = os.getenv("RESEARCH_AGENT_PORT")
research_server_agent_name: Final[str] = "Research Agent"

if not research_port:
    raise ValueError("RESEARCH_AGENT_PORT is not set")

research_a2a_client_agent = A2AAgent(
    url=f"http://localhost:{research_port}",
    memory=UnconstrainedMemory(),
)
print("[ResearchA2AAgent] Research A2A client created")
asyncio.run(research_a2a_client_agent.check_agent_exists())
print("[ResearchA2AAgent] Completed checking A2A agent card")

server = Server()


@server.agent(
    name=research_server_agent_name,
)
async def research_agent_wrapper(
    input: Message,
):
    """Proxy to the remote research A2A agent; exposed on Agent Stack for handoff."""
    prompt = get_message_text(input)
    response = await research_a2a_client_agent.run(prompt)
    response_text = getattr(response, "last_message", response).text
    yield AgentMessage(text=response_text)


def run() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("RESEARCH_AGENTSTACK_PORT"))
    server.run(host=host, port=port)


if __name__ == "__main__":
    run()
