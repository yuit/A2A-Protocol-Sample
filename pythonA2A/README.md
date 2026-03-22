uv run adk web

## Run all AgentStack proxy servers (policy + research + find-providers)

From `pythonA2A`, with remote A2A ports in `.env` (`POLICY_AGENT_PORT`, `RESEARCH_AGENT_PORT`, `FIND_PROVIDERS_AGENT_PORT`):

```bash
uv run python src/servers/run_all_agentstack.py
```

AgentStack sub-agents listen ports: `POLICY_AGENTSTACK_PORT`, `RESEARCH_AGENTSTACK_PORT`, `FIND_PROVIDERS_AGENTSTACK_PORT` (defaults `8887`, `8889`, `8890`).
