This repository is a multi-agent A2A sample project.

- `pythonA2A/` contains Python-based A2A/AgentStack servers and orchestration.
- `tsServers/` contains TypeScript-based services used by the agent workflow.
- The healthcare concierge server coordinates policy, research, and provider sub-agents.

## Run the Concierge
### Requirement
- [Node.js](https://nodejs.org/en/download)
- Python >= 3.11
- [Agent Stack](https://agentstack.beeai.dev/stable/introduction/quickstart)
- API Keys:
  - in tsServers:
    - `GOOGLE_GENAI_API_KEY`
    - `ANTHROPIC_API_KEY`
  - in PythonA2A:
    - `GEMINI_API_KEY`

### Run A2A Servers
In `tsServers` folder,

```bash
npm install
npm run build
npm run server
```

### In PythonA2A
Run healthcare concierge and its sub-agents on Agent stack
```bash
uv sync
uv run python src/servers/run_all_agentstack.py
```

### Chat with the concierge
Launch web-based UI through agentstack. 
```bash
agentstack ui
```
Then select `Healthcare Concierge`
