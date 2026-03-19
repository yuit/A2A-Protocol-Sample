"""
Simple Python A2A client tester for local agents.

Usage:
  python src/a2a_client_tester.py policy "What does my plan cover?"
  python src/a2a_client_tester.py research "Best treatment for migraine?"
  python src/a2a_client_tester.py findProviders "Find a PCP in Austin, TX"
  python src/a2a_client_tester.py concierge "Help me find therapy and coverage details"
"""

from typing import Final
import argparse
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
try:
  import beeai_framework  # noqa: F401
  from beeai_framework.adapters.a2a.agents import A2AAgent 
  from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
  from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
except ModuleNotFoundError as e:
  raise ModuleNotFoundError(
    "beeai-framework is not installed in the current environment. "
    "Install it from `clients/` (and use Python >= 3.11) before running this file."
  ) from e

load_dotenv()

async def main() -> None:
  agent = A2AAgent(
    url=f"http://localhost:{os.getenv('HEALTHCARE_CONCIERGE_AGENT_PORT')}", 
    memory=UnconstrainedMemory()
  )
  output_file = Path("logs/a2a_healthcare_concierge_client.agent.trajectory")
  output_file.parent.mkdir(exist_ok=True, parents=True)
  with open(output_file, "w", encoding="utf-8") as target_log_file:
    response = await agent.run(
      "I'm based in Austin, TX. How do I get mental health therapy near me and what does my insurance cover?"
    ).middleware(GlobalTrajectoryMiddleware(
      target=target_log_file,
    ))
    print(response.last_message.text)

if __name__ == "__main__":
  asyncio.run(main())
