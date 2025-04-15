
https://x.convai.com/?xpid=1fc1757a-9090-4e67-b311-43b1c3bf893e&type=private

jak pripojit conversational api na telefonii

Let me search through the documentation to help you with connecting Conversational AI to telephony.

Based on the documentation, you can integrate ElevenLabs generated speech with telephony using Twilio. Here's how to set it up:

First, create a new project and install dependencies:
```
mkdir elevenlabs-twilio
cd elevenlabs-twilio
npm init -y
npm install elevenlabs express express-ws twilio
npm i @types/node @types/express @types/express-ws @types/ws dotenv tsx typescript
```

Set up environment variables in .env:
SERVER_DOMAIN=
ELEVENLABS_API_KEY=

The integration uses WebSocket connections to stream the audio through Twilio. The key components include:
Setting up an incoming call handler
Creating a WebSocket connection for streaming
Converting text to speech and sending it through the WebSocket
For local testing, you'll need to use ngrok:
ngrok http 5000

Then update your .env file with the ngrok URL:

SERVER_DOMAIN=*******.ngrok.app
ELEVENLABS_API_KEY=*************************

Run the application:
npm run dev

Note: Regarding your question about API updates for April 14, 2025 - I don't see any specific documentation about recent API updates in the provided documents. I would need access to changelog or release notes documentation to provide that information.

Was this response helpful?
Yes
No
muzes udelat aplikaci v nodejs ktera tohle vyresi

Yes, I can help you with creating a Node.js application that integrates ElevenLabs Conversational AI with Twilio. Here's a step-by-step guide based on the documentation:

First, create a new project and install the required dependencies:
mkdir conversational-ai-twilio
cd conversational-ai-twilio
npm init -y
npm pkg set type="module"
npm install @fastify/formbody @fastify/websocket dotenv fastify ws

Create a .env file with your ElevenLabs Agent ID:
ELEVENLABS_AGENT_ID=<your-agent-id>

Create an index.js file with this code that handles the Twilio-ElevenLabs integration:


Start the server:
node index.js

To expose your local server to the internet (required for Twilio), use ngrok:
ngrok http 8000

Key features of this implementation:

Uses Fastify for the web server
Handles bidirectional audio streaming between Twilio and ElevenLabs
Manages WebSocket connections for real-time communication
Processes audio chunks in base64 format
Handles conversation state and events
Make sure to:

Replace <your-agent-id> in the .env file with your actual ElevenLabs Agent ID
Configure your Twilio webhook URL to point to your ngrok URL at the /twilio/inbound_call endpoint
Ensure your ElevenLabs Agent is properly configured
This implementation creates a bridge between Twilio's voice calls and ElevenLabs' Conversational AI, allowing for real-time voice conversations with your AI agent.