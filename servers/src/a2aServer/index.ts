import { initA2AServer } from '../utils/utils.js';
import {
  APP_NAME as FIND_PROVIDERS_AGENT_APP_NAME,
  FindProvidersAgentExecutor,
  FIND_PROVIDERS_AGENT_CARD,
  FIND_PROVIDERS_AGENT_BASE_URL,
  FIND_PROVIDERS_AGENT_PORT,
} from './findProvidersAgent.js';
import {
  APP_NAME as POLICY_AGENT_APP_NAME,
  PolicyAgentTaskExecutor,
  POLICY_AGENT_CARD,
  POLICY_AGENT_BASE_URL,
  POLICY_AGENT_PORT,
} from './policyAgent.js';
import {
  APP_NAME as RESEARCH_AGENT_APP_NAME,
  RESEARCH_A2A_AGENT_EXECUTOR,
  RESEARCH_AGENT_CARD,
  RESEARCH_AGENT_BASE_URL,
  RESEARCH_AGENT_PORT,
} from './researchAgent.js';

initA2AServer({
  executor: new FindProvidersAgentExecutor(),
  name: FIND_PROVIDERS_AGENT_APP_NAME,
  agentCard: FIND_PROVIDERS_AGENT_CARD,
  url: FIND_PROVIDERS_AGENT_BASE_URL,
  port: FIND_PROVIDERS_AGENT_PORT,
});

initA2AServer({
  executor: new PolicyAgentTaskExecutor(),
  name: POLICY_AGENT_APP_NAME,
  agentCard: POLICY_AGENT_CARD,
  url: POLICY_AGENT_BASE_URL,
  port: POLICY_AGENT_PORT,
});

initA2AServer({
  executor: RESEARCH_A2A_AGENT_EXECUTOR,
  name: RESEARCH_AGENT_APP_NAME,
  agentCard: RESEARCH_AGENT_CARD,
  url: RESEARCH_AGENT_BASE_URL,
  port: RESEARCH_AGENT_PORT,
});