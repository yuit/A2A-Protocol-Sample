import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import type { Doctor } from './doctor.d.ts';

/**
 * Basic MCP server scaffold for listing doctors.
 *
 * This does NOT connect to any A2A agents; it just exposes
 * a simple `listDoctors` tool over MCP using stdio transport.
 */
const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Load doctors from JSON file in the shared data folder.
const doctorsDBPath = path.join(__dirname, '../..', 'data', 'doctors.json');
const doctorsDB = JSON.parse(fs.readFileSync(doctorsDBPath, 'utf-8')) as Doctor[];

interface QueryDoctorsDBResult {
  type: 'text';
  text: string;
}
async function queryDoctorsDB(
  state: string,
  city: string,
): Promise<QueryDoctorsDBResult[]> {
  const targetState = state.toLowerCase();
  const targetCity = city.toLowerCase();

  const matchesdoctors = doctorsDB.filter((doctor) => {
    const docState = doctor.address.state.toLowerCase();
    const docCity = doctor.address.city.toLowerCase();
    return docState === targetState && docCity === targetCity;
  });
  if (matchesdoctors.length === 0) {
    return [
      {
        type: 'text',
        text: `No doctors found for the given state ${state} and city ${city}`,
      } as QueryDoctorsDBResult
    ];
  }
  return matchesdoctors.map((doctor) => ({
    type: 'text',
    text: JSON.stringify(doctor),
  })) as QueryDoctorsDBResult[];
}

async function main() {
  const server = new McpServer({
    name: 'list-doctors-mcp',
    version: '0.1.0',
  });

  server.registerTool(
    'listDoctors',
    {
      description: 'List doctors',
      inputSchema: {
        state: z.string().describe('The state to list doctors for'),
        city: z.string().describe('The city to list doctors for'),
      },
    },
    async ({ state, city }) => {
      if (!state && !city) {
        return {
          isError: true,
          content: [
            {
              type: "text",
              text: "Invalid inputs: No state and no city are provided",
            }      
          ]
        }
      }
      return {
        content: await queryDoctorsDB(state, city)
      }
    }
  );

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

// Run when invoked directly via Node.
void main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error('listDoctorsMCP server failed:', err);
  process.exit(1);
});

