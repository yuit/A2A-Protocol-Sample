"""
Healthcare Concierge scaffold using BeeAI's RequirementAgent.

This file is intentionally a scaffold: it sets up the core RequirementAgent
structure and shows where to plug in additional tools (including your A2A
remote agents).
"""

import os
from typing import Final, Tuple
from dotenv import load_dotenv
from pathlib import Path
import asyncio
import sys
try:
  import beeai_framework  # noqa: F401
  from beeai_framework.agents.requirement import RequirementAgent
  from beeai_framework.agents.requirement.requirements.conditional import (
    ConditionalRequirement,
  )
  from beeai_framework.adapters.gemini import GeminiChatModel
  from beeai_framework.adapters.a2a.agents import A2AAgent 
  from beeai_framework.adapters.a2a.serve.server import A2AServer, A2AServerConfig
  from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
  from beeai_framework.tools.handoff import HandoffTool
  from beeai_framework.tools.think import ThinkTool
  from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
  from beeai_framework.serve.utils import LRUMemoryManager
except ModuleNotFoundError as e:
  raise ModuleNotFoundError(
    "beeai-framework is not installed in the current environment. "
    "Install it from `clients/` (and use Python >= 3.11) before running this file."
  ) from e

load_dotenv()

async def create_a2a_client_sub_agents() -> Tuple[A2AAgent, A2AAgent, A2AAgent]:
  """
  Create three BeeAI A2A clients:
  - policy
  - research
  - find_providers
  """
  policy_port: Final[str] = os.getenv("POLICY_AGENT_PORT")
  research_port: Final[str] = os.getenv("RESEARCH_AGENT_PORT")
  find_providers_port: Final[str] = os.getenv("FIND_PROVIDERS_AGENT_PORT")

  if not policy_port or not research_port or not find_providers_port:
    raise ValueError("POLICY_AGENT_PORT, RESEARCH_AGENT_PORT, or FIND_PROVIDERS_AGENT_PORT is not set")

  policy_client = A2AAgent(
    url=f"http://localhost:{policy_port}",
    memory=UnconstrainedMemory()
  )
  
  research_client = A2AAgent(
    url=f"http://localhost:{research_port}",
    memory=UnconstrainedMemory()
  )

  find_providers_client = A2AAgent(
    url=f"http://localhost:{find_providers_port}",
    memory=UnconstrainedMemory()
  )

  await policy_client.check_agent_exists()
  await research_client.check_agent_exists()
  await find_providers_client.check_agent_exists()

  return policy_client, research_client, find_providers_client

async def build_health_care_concierge_agent() -> RequirementAgent:
  """
  Create a RequirementAgent with rule-based tool execution constraints.

  Replace the `tools` and `requirements` lists with your actual concierge
  workflow (e.g., call FindProviders via A2A, then decide next steps, etc.).
  """
  
  policy_a2a, research_a2a, find_providers_a2a = await create_a2a_client_sub_agents()
  print("Created BeeAI A2A clients:")
  print(f"- policy: {getattr(policy_a2a, '_url', None)}")
  print(f"- research: {getattr(research_a2a, '_url', None)}")
  print(f"- find_providers: {getattr(find_providers_a2a, '_url', None)}")

  # Core tools (minimal scaffold).
  tools = [
    think_tool:=ThinkTool(),
    policy_tool:=HandoffTool(
      target=policy_a2a,
      name="Insurance Policy Agent",
      description=policy_a2a.agent_card.description
    ),
    research_tool:=HandoffTool(
      target=research_a2a,
      name="Healthcare Research Agent",
      description=research_a2a.agent_card.description
    ),
    find_providers_tool:=HandoffTool(
      target=find_providers_a2a,
      name="Find Providers Agent",
      description=find_providers_a2a.agent_card.description
    ),
  ]

  requirement_agent = RequirementAgent(
    # GeminiChatModel will load model and api key from the environment variables.
    llm=GeminiChatModel(
      allow_parallel_tool_calls=True,
    ),
    tools=tools,
    requirements=[
      ConditionalRequirement(
          ThinkTool,
          name="Condition: Use ThinkTool before and after calling any other tool",
          force_at_step=1,
          force_after=tools, 
          consecutive_allowed=False
      ),
    ],
    instructions=(
      f"""You are a concierge for healthcare services. Your task is 
        to handoff to one or more agents to answer questions and provide 
        a detailed summary of their answers. Be sure that all of their 
        questions are answered before responding.
        
        IMPORTANT:
        For insurance-related questions, first use  `{policy_a2a.name}` to try and answer the question.
        If the policy agent cannot answer the question, then use the `{research_a2a.name}` to find relevant information.
        For finding providers, use only ${find_providers_a2a.name} to find relevant providers.
        For general healthcare questions, use `{research_a2a.name}`.

        REASON: output the reasoning for calling each agent.
        RESPONSE: return a detailed summary of the answers from the agents.
        """
    )
  )

  return requirement_agent

async def run_health_care_concierge_agent() -> None:
  """
  Minimal local smoke test: create A2A clients, then (optionally) run the concierge
  RequirementAgent if you have LLM credentials configured.
  """

  agent = await build_health_care_concierge_agent()

  output_file = Path("logs/healthcare_concierge_agent.tools.trajectory")
  output_file.parent.mkdir(exist_ok=True, parents=True)
  with open(output_file, "w", encoding="utf-8") as target_log_file:
    response = await agent.run(
      "I'm based in Austin, TX. How do I get mental health therapy near me and what does my insurance cover?"
    ).middleware(GlobalTrajectoryMiddleware(
      target=target_log_file,
      included=[ThinkTool, HandoffTool],
      excluded=[GeminiChatModel]
    ));

    # BeeAI response shape can change; this keeps the scaffold resilient.
    print(
      getattr(response, "last_message", response).text
      if hasattr(response, "last_message")
      else response
    )

async def run_health_care_concierge_agent_a2a_server() -> A2AServer:
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
  try:
    mode = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""
    if mode == "a2a":
      # Build the agent in an async step, then run the blocking server.
      server = asyncio.run(run_health_care_concierge_agent_a2a_server())
      print(f"Server is running on port {server._config.port}")
      server.serve()
      return
    # Default mode: run the agent without wrapping in a server.
    asyncio.run(run_health_care_concierge_agent())
  except KeyboardInterrupt:
    print("Stopped by user.")
  except asyncio.CancelledError:
    print("Stopped by user.")

if __name__ == "__main__":
  main()
