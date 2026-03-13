import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { GoogleGenAI } from '@google/genai';
import { v4 as uuidv4 } from 'uuid';
import {
  Message,
  Task,
  TaskArtifactUpdateEvent,
  TaskStatusUpdateEvent,
  TextPart,
} from '@a2a-js/sdk';
import {
  AgentExecutor,
  ExecutionEventBus,
  RequestContext,
} from '@a2a-js/sdk/server';

// Load configuration from .env at project root
dotenv.config();

const vertexai = process.env.VERTEX_AI === 'true';
const apiKey = process.env.VERTEX_API_KEY ?? '';
const modelName = process.env.VERTEX_MODEL ?? 'gemini-3-flash-preview';

const systemInstruction = 
`
    You are healthcare policy expert. Answer the user's question based on the given document.
    If there is no information in the document, answer that YOU DON'T KNOW.
`;

class policyAgent {
  private readonly pdfData: Buffer;

  constructor(pdfRelativePath: string = path.join(__dirname, '..', 'data', '2026AnthemgHIPSBC.pdf')) {
    this.pdfData = fs.readFileSync(pdfRelativePath);
  }

  async answerQuery(userPrompt: string): Promise<string> {
    const client = new GoogleGenAI({
      apiKey,
      vertexai,
    });

    const response = await client.models.generateContent({
      model: modelName,
      config: {
        systemInstruction,
      },
      contents: [
        {
          role: 'user',
          parts: [
            { text: userPrompt },
            {
              inlineData: {
                data: this.pdfData.toString('base64'),
                mimeType: 'application/pdf',
              },
            },
          ],
        },
      ],
    });

    return response.text ?? '';
  }
}

export class policyAgentMessageExecutor implements AgentExecutor {
  private readonly agent: policyAgent;

  constructor() {
    this.agent = new policyAgent();
  }

  async execute(requestContext: RequestContext, eventBus: ExecutionEventBus): Promise<void> {
    const { userMessage, contextId } = requestContext;

    // Log basic info about the incoming request
    console.log(
      '[PolicyAgentExecutor] Incoming request',
      `contextId=${contextId ?? userMessage.contextId ?? 'none'}`
    );

    // Extract the user's text message from the RequestContext
    const textParts = (userMessage.parts ?? []).filter(
      (p): p is TextPart => p.kind === 'text'
    );
    const userText = textParts.map((p) => p.text).join('\n');

    const answer = await this.agent.answerQuery(userText);

    const responseMessage: Message = {
      kind: 'message',
      role: 'agent',
      messageId: uuidv4(),
      parts: [{ kind: 'text', text: answer }],
      contextId,
    };

    eventBus.publish(responseMessage);
    eventBus.finished();
  }

  async cancelTask(_taskId: string, _eventBus: ExecutionEventBus): Promise<void> {
    // No internal long-running work to cancel yet; placeholder for future extension.
    // You might track in-flight tasks here if policyAgent does streaming or long operations.
    return;
  }
}

/**
 * A2A AgentExecutor that returns a Task: init task, create artifact, then finish task.
 */
export class policyAgentTaskExecutor implements AgentExecutor {
  private readonly agent: policyAgent;

  constructor() {
    this.agent = new policyAgent();
  }
  
  async execute(requestContext: RequestContext, eventBus: ExecutionEventBus): Promise<void> {
    const { taskId, contextId, userMessage, task } = requestContext;

    const effectiveTaskId = taskId ?? uuidv4();
    const effectiveContextId = contextId ?? userMessage.contextId ?? uuidv4();

    // 1. Init task: create and publish the initial task if it doesn't exist
    if (!task) {
      const initialTask: Task = {
        kind: 'task',
        id: effectiveTaskId,
        contextId: effectiveContextId,
        status: {
          state: 'submitted',
          timestamp: new Date().toISOString(),
        },
        history: [userMessage],
      };
      eventBus.publish(initialTask);
    }
    
    // Extract the user's text message from the RequestContext
    const textParts = (userMessage.parts ?? []).filter(
      (p): p is TextPart => p.kind === 'text'
    );
    const userText = textParts.map((p) => p.text).join('\n');

    const answer = await this.agent.answerQuery(userText);

    // 2. Create artifact: publish an artifact for this task
    const artifactUpdate: TaskArtifactUpdateEvent = {
      kind: 'artifact-update',
      taskId: effectiveTaskId,
      contextId: effectiveContextId,
      artifact: {
        artifactId: `artifact-${effectiveTaskId}`,
        name: 'result.txt',
        parts: [{ kind: 'text', text: `\n\nTask ${effectiveTaskId} completed.\n\nHere is the answer: ${answer}` }],
      },
    };
    eventBus.publish(artifactUpdate);

    // 3. Finish task: publish final status and signal completion
    const finalUpdate: TaskStatusUpdateEvent = {
      kind: 'status-update',
      taskId: effectiveTaskId,
      contextId: effectiveContextId,
      status: {
        state: 'completed',
        timestamp: new Date().toISOString(),
      },
      final: true,
    };
    eventBus.publish(finalUpdate);
    eventBus.finished();
  }

  async cancelTask(_taskId: string, _eventBus: ExecutionEventBus): Promise<void> {
    // Placeholder for cancellation support.
    return;
  }
}