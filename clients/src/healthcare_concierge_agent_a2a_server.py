import asyncio
import os

from dotenv import load_dotenv

from healthcare_concierge_agent import build_health_care_concierge_agent

try:
  from beeai_framework.adapters.a2a.serve.server import A2AServer, A2AServerConfig
  from beeai_framework.serve.utils import LRUMemoryManager
except ModuleNotFoundError as e:
  raise ModuleNotFoundError(
    "beeai-framework is not installed in the current environment. "
    "Install it from `clients/` (and use Python >= 3.11) before running this file."
  ) from e  # type: ignore[reportMissingImports]

load_dotenv()

async def _build_server() -> A2AServer:
  healthcare_concierge_agent = await build_health_care_concierge_agent()
  port = os.getenv("HEALTHCARE_CONCIERGE_AGENT_PORT")
  if not port:
    raise ValueError("HEALTHCARE_CONCIERGE_AGENT_PORT is not set")
  server = A2AServer(
    config=A2AServerConfig(host="127.0.0.1", port=port, protocol="jsonrpc"),
    memory_manager=LRUMemoryManager(maxsize=100),
  )
  return server.register(healthcare_concierge_agent, send_trajectory=True)


def main() -> None:
  # Build the agent in an async step, then run the blocking server.
  server = asyncio.run(_build_server())
  print(f"Server is running on port {server._config.port}")
  server.serve()

if __name__ == "__main__":
  main()
