import dotenv from 'dotenv';
import { createUserContent } from '@google/genai';
import { InMemoryRunner, isFinalResponse, SequentialAgent } from 'adk/core';
import { logger } from './logger.js';
import { RemoteA2AClientAgent } from './remoteA2AClientAgent.js';

dotenv.config();

const policyA2AClientAgent = new RemoteA2AClientAgent({
  name: "PolicyA2AClientAgent",
  description: `Provides healthcare information about symptoms, health
    conditions, treatments, and procedures using up-to-date web resources.`,
  a2aServerUrl: `http://localhost:${process.env.POLICY_AGENT_PORT}`,
});

const researchA2AClientAgent = new RemoteA2AClientAgent({
  name: "ResearchA2AClientAgent",
  description: `Provides healthcare information about symptoms, health
    conditions, treatments, and procedures using up-to-date web resources.`,
  a2aServerUrl: `http://localhost:${process.env.RESEARCH_AGENT_PORT}`,
});

const rootAgent = new SequentialAgent({
  name: "Root-Sequential-Agent",
  description: "Healthcare Routing Agent",
  subAgents: [policyA2AClientAgent, researchA2AClientAgent],
});

const runner = new InMemoryRunner({
  agent: rootAgent,
  appName: 'Healthcare Runner',
});

async function runAgent(prompt: string) {
  for await (const event of runner.runEphemeral({
    userId: 'user',
    newMessage: createUserContent(prompt),
  })) {
    if (isFinalResponse(event) && event.content?.parts?.[0]?.text) {
      logger.info(`${runner.appName} Final Response: ${event.content.parts[0].text}`);
    }
  }
}

void runAgent('How can I get mental health therapy?');