#!/usr/bin/env python3
"""
Start all AgentStack servers:
- policy proxy
- research proxy
- find-providers proxy
- healthcare concierge

Each runs in its own process. Load env from pythonA2A/.env (run from repo root).

Required for backends (remote A2A):
  POLICY_AGENT_PORT, RESEARCH_AGENT_PORT, FIND_PROVIDERS_AGENT_PORT

Listen ports (read from environment after .env is loaded; defaults shown):
  POLICY_AGENTSTACK_PORT — default 8887
  RESEARCH_AGENTSTACK_PORT — default 8889
  FIND_PROVIDERS_AGENTSTACK_PORT — default 8890
  HEALTHCARE_CONCIERGE_AGENTSTACK_PORT — default 8888

Usage (from pythonA2A):

  uv run python src/servers/run_all_agentstack.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import asyncio
import time
from pathlib import Path
from logger import get_logger

logger = get_logger(name="RunAgentStack")


def _python_a2a_root() -> Path:
  # .../pythonA2A/src/servers/run_all_agentstack.py -> .../pythonA2A
  return Path(__file__).resolve().parent.parent.parent


def _servers_dir() -> Path:
  return Path(__file__).resolve().parent


def main() -> int:
  project_root = _python_a2a_root()
  servers_dir = _servers_dir()

  try:
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")
  except ImportError:
    pass

  env = os.environ.copy()
  py_path = str(servers_dir)
  env["PYTHONPATH"] = (
    py_path if not env.get("PYTHONPATH") else py_path + os.pathsep + env["PYTHONPATH"]
  )

  # Stack listen ports: os.environ includes values from the shell and load_dotenv().
  policy_agentstack_port = os.getenv("POLICY_AGENTSTACK_PORT", "8887")
  research_agentstack_port = os.getenv("RESEARCH_AGENTSTACK_PORT", "8889")
  find_providers_agentstack_port = os.getenv("FIND_PROVIDERS_AGENTSTACK_PORT", "8890")
  healthcare_concierge_agentstack_port = os.getenv("HEALTHCARE_CONCIERGE_AGENTSTACK_PORT", "8888")

  specs: list[tuple[str, str, str, str]] = [
    ("policy", "agentstack.policy_a2a", "POLICY_AGENTSTACK_PORT", policy_agentstack_port),
    ("research", "agentstack.research_a2a", "RESEARCH_AGENTSTACK_PORT", research_agentstack_port),
    (
      "find_providers",
      "agentstack.find_providers_a2a",
      "FIND_PROVIDERS_AGENTSTACK_PORT",
      find_providers_agentstack_port,
    ),
    (
      "healthcare_concierge",
      "healthcare_concierge_agentstack",
      "HEALTHCARE_CONCIERGE_AGENTSTACK_PORT",
      healthcare_concierge_agentstack_port,
    ),
  ]

  processes: list[subprocess.Popen] = []
  try:
    for label, module, port_key, port in specs:
      child_env = {**env, port_key: str(port)}
      logger.info(f"Starting {label} ({module}) {port_key}={port}")
      proc = subprocess.Popen(
        [sys.executable, "-m", module],
        cwd=str(project_root),
        env=child_env,
      )
      processes.append(proc)

    logger.info("All AgentStack servers running. Ctrl+C to stop.")
    while True:
      for proc in processes:
        code = proc.poll()
        if code is not None:
          logger.error(f"A child exited with code {code}")
          return int(code) if code else 1
      time.sleep(0.3)
  except KeyboardInterrupt:
    print("Stopped by user.")
  except asyncio.CancelledError:
    print("Stopped by user.")
  finally:
    for proc in processes:
      if proc.poll() is None:
        proc.terminate()
        try:
          proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
          proc.kill()


if __name__ == "__main__":
  raise SystemExit(main())
