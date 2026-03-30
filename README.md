This repository explores multi-agent using A2A protocol using various agentic development frameworks:

- [Google ADK](https://google.github.io/adk-docs/)
- [Microsfot Agent Framework](https://learn.microsoft.com/en-us/agent-framework/integrations/a2a?tabs=dotnet-cli%2Cuser-secrets&pivots=programming-language-csharp)
- [A2A JS SDK](https://github.com/a2aproject/a2a-js)
- [Langchain MCP](https://docs.langchain.com/oss/python/langchain/mcp)
- [BeeAI Framework](https://framework.beeai.dev/introduction/welcome)
- [Agent Stack](https://framework.beeai.dev/integrations/agent-stack)

Data and frameworks based on Deep Learning A2A course
## Project Structure
```text
A2A-Protocol-Sample
├── pythonA2A                         
│   └── src/
│       ├── clients/           # A2A clients using BeeAI Agent Framework           
│       └── servers/           # BeeAI Agent Stack servers wrapping around A2A clients. Run as a standalone chat app via Agent Stack Web UI.
│           └── agentstack/                     
├── pythonAdk                  # A2A clients using Google Adk. Run as a standalone chat app via ADK web UI.
│   └── agent/                 # Policy and research A2A client agents
└── tsServers                  # A2A servers (remote agents)   
│   ├── data/                  # "database"    
│   └── src/
│       ├── a2aServer/         # A2A servers implementation
│       └── mcpServer/         # MCP servers implementation
```

## Setup
- [Node.js](https://nodejs.org/en/download)
- Python >= 3.11
- [Agent Stack](https://agentstack.beeai.dev/stable/introduction/quickstart)
- API Keys in tsServers:
  - `GOOGLE_GENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
- API Keys in PythonA2A:
  - `GEMINI_API_KEY`

## Run A2A TypeScipt servers
```bash
# In tsServers folder
npm install
npm run build
npm run server
```

## Run Full Concierge with AgentStack
1. Run A2A Python clients on Agent Stack
```bash
# In pythonA2A folder
uv sync
uv run python src/servers/run_all_agentstack.py
```

2. Launch Agent Stack Web UI
```bash
agentstack ui
```
Select `Healthcare Concierge`

## Run A2A Clients on ADK
```bash
# In pythonAdk
uv sync
uv run adk web
```
