import Fastify from "fastify";
import WebSocket from "ws";
import dotenv from "dotenv";
import fastifyFormBody from "@fastify/formbody";
import fastifyWs from "@fastify/websocket";
dotenv.config();
const { ELEVENLABS_AGENT_ID } = process.env;
if (!ELEVENLABS_AGENT_ID) {
    console.error("Missing ELEVENLABS_AGENT_ID in environment variables");
    process.exit(1);
}
const fastify = Fastify();
fastify.register(fastifyFormBody);
fastify.register(fastifyWs);
const PORT = process.env.PORT || 8000;
// Root route for health check
fastify.get("/", async (_, reply) => {
    reply.send({ message: "Server is running" });
});
// Handle incoming Twilio calls
fastify.all("/twilio/inbound_call", async (request, reply) => {
    const twimlResponse = `<?xml version="1.0" encoding="UTF-8"?>
        <Response>
        <Connect>
            <Stream url="wss://${request.headers.host}/media-stream" />
        </Connect>
        </Response>`;
    reply.type("text/xml").send(twimlResponse);
});
// WebSocket handler for media streams
fastify.register(async (fastifyInstance) => {
    fastifyInstance.get("/media-stream", { websocket: true }, (connection, req) => {
        console.info("[Server] Twilio connected to media stream.");
        
        let streamSid = null;
        
        // Connect to ElevenLabs WebSocket
        const elevenLabsWs = new WebSocket(
            `wss://api.elevenlabs.io/v1/convai/conversation?agent_id=${ELEVENLABS_AGENT_ID}`
        );
        // Handle ElevenLabs messages
        elevenLabsWs.on("message", (data) => {
            try {
                const message = JSON.parse(data);
                handleElevenLabsMessage(message, connection);
            } catch (error) {
                console.error("[II] Error parsing message:", error);
            }
        });
        // Handle messages from Twilio
        connection.on("message", async (message) => {
            try {
                const data = JSON.parse(message);
                switch (data.event) {
                    case "start":
                        streamSid = data.start.streamSid;
                        console.log(`[Twilio] Stream started with ID: ${streamSid}`);
                        break;
                    case "media":
                        if (elevenLabsWs.readyState === WebSocket.OPEN) {
                            const audioMessage = {
                                user_audio_chunk: Buffer.from(
                                    data.media.payload,
                                    "base64"
                                ).toString("base64"),
                            };
                            elevenLabsWs.send(JSON.stringify(audioMessage));
                        }
                        break;
                    case "stop":
                        elevenLabsWs.close();
                        break;
                }
            } catch (error) {
                console.error("[Twilio] Error processing message:", error);
            }
        });
    });
});
// Start server
fastify.listen({ port: PORT }, (err) => {
    if (err) {
        console.error("Error starting server:", err);
        process.exit(1);
    }
    console.log(`[Server] Listening on port ${PORT}`);
});