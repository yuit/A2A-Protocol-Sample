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

provider_port: Final[str | None] = os.getenv("FIND_PROVIDERS_AGENT_PORT")
find_providers_server_agent_name: Final[str] = "Find Providers Agent"

if not provider_port:
    raise ValueError("FIND_PROVIDERS_AGENT_PORT is not set")

provider_a2a_client_agent = A2AAgent(
    url=f"http://localhost:{provider_port}",
    memory=UnconstrainedMemory(),
)
print("[ProviderA2AAgent] Provider A2A client created")
asyncio.run(provider_a2a_client_agent.check_agent_exists())
print("[ProviderA2AAgent] Completed checking A2A agent card")

server = Server()


@server.agent(
    name=find_providers_server_agent_name,
)
async def provider_agent_wrapper(
    input: Message,
):
    """Proxy to the remote find-providers A2A agent; exposed on Agent Stack for handoff."""
    prompt = get_message_text(input)
    response = await provider_a2a_client_agent.run(prompt)
    response_text = getattr(response, "last_message", response).text
    yield AgentMessage(text=response_text)


def run() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("FIND_PROVIDERS_AGENTSTACK_PORT"))
    server.run(host=host, port=port)


if __name__ == "__main__":
    run()
