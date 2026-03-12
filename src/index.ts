import { policyAgent } from './policyPrompt';

async function main() {
  const policy = new policyAgent();

  const question = 'What is my deductible?';
  const answer = await policy.answerQuery(question);

  console.log('Question:', question);
  console.log('Answer:', answer);
}

void main();

