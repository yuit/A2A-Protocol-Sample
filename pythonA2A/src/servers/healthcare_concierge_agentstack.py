"""
Healthcare Concierge Agent using AgentStack.
"""
import asyncio
import os
from typing import Annotated
from time import sleep
import json
from a2a.types import Message
from a2a.utils.message import get_message_text
from agentstack_sdk.server import Server
from agentstack_sdk.server.context import RunContext
from agentstack_sdk.a2a.types import AgentMessage
from beeai_framework.agents.types import AgentExecutionConfig
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.tools.think import ThinkTool
from beeai_framework.adapters.gemini import GeminiChatModel
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.adapters.agentstack.agents import AgentStackAgent
from agentstack_sdk.a2a.extensions import (
  AgentDetail,
  AgentDetailTool,
  TrajectoryExtensionServer,
  TrajectoryExtensionSpec,
)
from beeai_framework.agents.requirement.requirements.conditional import (
  ConditionalRequirement,
)
from logger import get_logger

logger = get_logger(
  name='HealthcareConciergeAgent',
  filename='logs/healthcare_concierge_agentstack.trajectory.log'
)
# Make other AgentStack agents discoverable that have been deployed to the platform and make them available via handoff tools
sub_agents = asyncio.run(AgentStackAgent.from_agent_stack())
policy_agentstack_name = os.getenv("POLICY_AGENTSTACK_NAME")
research_agentstack_name = os.getenv("RESEARCH_AGENTSTACK_NAME")
find_providers_agentstack_name = os.getenv("FIND_PROVIDERS_AGENTSTACK_NAME")

class HealthcareConciergeAgent:
  def __init__(self) -> None:
    handoff_agents = {
      a.name: a
      for a in sub_agents
      if a.name
      in {
        policy_agentstack_name,
        research_agentstack_name,
        find_providers_agentstack_name,
      }
    }
    logger.info(f"Active AgentStack Agents: {[a.name for a in sub_agents]}")
    policy_handoff = HandoffTool(handoff_agents[policy_agentstack_name])
    research_handoff = HandoffTool(handoff_agents[research_agentstack_name])
    find_providers_handoff = HandoffTool(handoff_agents[find_providers_agentstack_name])

    self._instructions = f"""
    You are a concierge for healthcare services. Your task is 
    to handoff to one or more agents to answer questions and provide 
    a detailed summary of their answers. Be sure that all of their 
    questions are answered before responding. Use the tools provided to you to answer the question.
    
    IMPORTANT:
    For insurance-related questions, first use  `{policy_handoff.name}` to try and answer the question.
    For finding providers, use only ${find_providers_handoff.name} to find relevant providers.
    For general healthcare questions, use `{research_handoff.name}`.

    RESPONSE:
    Return a detailed summary of the answers from the agents. Each topic should be in its own section.
    """ 
   
    tools = [
      # Thinktool is used to capture thoughts of the LLM by having LLM call the tools with arguments `thoughts`
      ThinkTool(),
      policy_handoff,
      research_handoff,
      find_providers_handoff,
    ]
    self._agent = RequirementAgent(
      # GeminiChatModel will load model and api key from the environment variables.
      llm=GeminiChatModel(
        allow_parallel_tool_calls=True,
      ),
      tools=tools,
      requirements=[
        ConditionalRequirement(
          ThinkTool,
          name="Condition: Use ThinkTool before and after calling any other tool",
          force_after=tools, 
          force_at_step=1,
          consecutive_allowed=False
        ),
      ],
      instructions=self._instructions,
    )

  def get_agent(self):
    return self._agent

server = Server()
healthcare_concierge_agent = HealthcareConciergeAgent()

@server.agent(
  name="Healthcare Concierge",
  default_input_modes=["text", "text/plain"],
  default_output_modes=["text", "text/plain"],
  detail=AgentDetail(
      interaction_mode="multi-turn",
      user_greeting="Hi there! I can help navigate benefits, providers, and coverage details.",
      input_placeholder="Ask a healthcare question...",
      programming_language="Python",
      framework="BeeAI",
      tools=[
        AgentDetailTool(
            name="Think",
            description="Plans the best approach before responding.",
        ),
        AgentDetailTool(
            name="Handoff",
            description="Hands off to a sub-agent to answer the question.",
        ),
      ],
  ),
)
async def wrap_health_care_concierge_agent_in_agentstack(
  input: Message,
  context: RunContext,
  trajectory: Annotated[TrajectoryExtensionServer, TrajectoryExtensionSpec()],
):
  yield trajectory.trajectory_metadata(
    title="Planning",
    content="Analyzing the user request to determine the best approach..."
  )
  await context.store(input)
  user_message = get_message_text(input)
  response_text = ""
  # Have to get agent and call run directly here so trajectory will print the text correctly
  agent = healthcare_concierge_agent.get_agent()
  async for event, meta in agent.run(
    user_message,
    execution=AgentExecutionConfig(max_iterations=20, max_retries_per_step=2),
  ):
    if meta.name == "final_answer":
      if getattr(event, "delta", None):
        logger.info(f"Event Meta:{meta.name}.Event Delta:{event.delta}")
        yield event.delta
      elif getattr(event, "text", None):
        logger.info(f"Event Meta:{meta.name}.Event Text:{event.text}")
        response_text += event.text
    elif meta.name == "success" and event.state.steps:
      step = event.state.steps[-1]
      tool = step.tool
      tool_name = tool.name if tool else None
      step_input = step.input
      logger.info(f"Event Meta:{meta.name}.At Step ({step.iteration}) Tool Call:{tool_name}")
      match tool_name:
        case "think":
          thoughts = step_input.get("thoughts", "Planning response.")
          logger.info(f"Thoughts:{thoughts}")
          yield trajectory.trajectory_metadata(
            title="Thinking",
            content=thoughts
          ) 
        case "final_answer":
          response = step_input.get("response", "No response")
          logger.info(f"Reponse:{response}")
          yield response_text
        case _ if tool_name in {
            policy_agentstack_name,
            research_agentstack_name,
            find_providers_agentstack_name,
        }:
          task = step_input.get("task", "No task")
          logger.info(f"Task:{task}")
          yield trajectory.trajectory_metadata(
            title=f"Tool Call:{tool_name}",
            content=task,
          )

  agent_message = AgentMessage(text=response_text)
  # yield agent_message
  await context.store(agent_message)

def run():
  try:
    server.run(
      host=os.getenv("HOST", "127.0.0.1"),
      port=int(os.getenv("HEALTHCARE_CONCIERGE_AGENTSTACK_PORT"))
    )
  except KeyboardInterrupt:
    print("Stopped by user.")
  except asyncio.CancelledError:
    print("Stopped by user.")

if __name__ == "__main__":
    run()
