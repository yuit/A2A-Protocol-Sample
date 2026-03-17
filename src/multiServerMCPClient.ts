import { MultiServerMCPClient as LangChainMultiServerMCPClient } from '@langchain/mcp-adapters';
import { createAgent } from 'langchain';
import { ChatAnthropic } from '@langchain/anthropic';
import dotenv from 'dotenv';

// Load configuration from .env at project root
dotenv.config();

const mcpClient = new LangChainMultiServerMCPClient({
  findDoctors: {
    transport: 'stdio',
    command: 'node',
    args: ['dist/mcpServer/findDoctors.js'],
  },
});

/**
 * Builds the MCP-backed agent: loads tools from the multi-server MCP client and
 * creates a LangChain ReAct agent using Anthropic Claude.
 */
export async function createMcpAgent() {
  const tools = await mcpClient.getTools();

  const model = new ChatAnthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
    model: process.env.ANTHROPIC_MODEL ?? 'claude-haiku-4-5-20251001',
    temperature: 0,
  });

  const agent = createAgent({
    model,
    tools,
  });

  return { agent, mcpClient, tools };
}

/**
 * Example: run the agent and then close the MCP client.
 *
 * const { agent, mcpClient } = await createMcpAgent();
 * const result = await agent.invoke({
 *   messages: [{ role: 'user', content: 'Find doctors in Atlanta, GA' }],
 * });
 * await mcpClient.close();
 */
// Example usage (uncomment to run directly):
const { agent } = await createMcpAgent();
const response = await agent.invoke({
  messages: [
    { role: 'user',
      content: 'Find doctors in Peachy, GA'
    }
  ],
});
const messages = response.messages; 
console.info(messages[messages.length - 1].content);
await mcpClient.close();