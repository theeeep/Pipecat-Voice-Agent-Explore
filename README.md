# Pipecat AI Lead VA

A voice-enabled AI assistant built with Pipecat, an open-source Python framework for real-time voice and multimodal conversational AI applications.

## What Pipecat Does

**Pipecat** is an open-source Python framework for building real-time voice and multimodal conversational AI applications using a pipeline-based architecture. It orchestrates audio, video, AI services, and conversation pipelines through a frame-based processing system designed for streaming and low-latency interactions.

### Core Capabilities

Pipecat enables developers to build sophisticated conversational AI applications including:

- **Voice Assistants** - Natural conversation flow with speech-to-text and text-to-speech
- **Meeting Assistants** - Real-time transcription and intelligent responses during meetings
- **Customer Support Bots** - Voice-enabled support with function calling capabilities
- **Multimodal AI Agents** - Applications that can see, hear, and respond naturally
- **Real-time Conversational Interfaces** - Low-latency voice interactions for any application

### Key Features

- **Pipeline Architecture** - Data flows through connected services as typed "frames"
- **Real-time Processing** - Streaming audio/video with minimal latency
- **Service Integrations** - Support for OpenAI, Anthropic, Deepgram, ElevenLabs, and more
- **Interruption Handling** - Users can naturally cut off bot responses mid-conversation
- **Voice Activity Detection (VAD)** - Intelligent turn-taking for natural conversations
- **Function Calling** - Integrate external APIs and services seamlessly
- **Multiple Transports** - WebRTC, WebSocket, local audio, and telephony support
- **Multimodal Support** - Process both audio and video streams simultaneously
- **Metrics & Monitoring** - Built-in performance tracking and usage analytics

### How It Works

Pipecat operates on a simple but powerful concept: data flows through pipelines as typed frames processed by connected services and processors. Each component transforms, aggregates, or generates frames—whether audio samples, text transcriptions, LLM responses, or control signals.

The framework handles:
- Frame routing and context management
- Real-time synchronization across services
- Conversation state and history
- Error handling and recovery
- Performance optimization

### Architecture

```
User Audio → STT → LLM → TTS → Bot Audio
     ↓           ↓      ↓      ↓
   VAD      Context  Function  Transport
   ↓        Aggregator  Calling    ↓
Turn              ↓        ↓      ↓
Detection    Memory    Tools   Output
```

## Project Structure

```
pipecat-ai-lead-va/
├── main.py              # Main application entry point
├── pyproject.toml       # Python project configuration
├── README.md           # This file
└── .venv/              # Python virtual environment
```

## Getting Started

### Prerequisites

- Python 3.13 or higher
- API keys for chosen AI services (OpenAI, Deepgram, ElevenLabs, etc.)

### Installation

1. Clone or download this project
2. Set up virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install pipecat
   # Add additional services as needed:
   # pip install pipecat[openai] pipecat[deepgram] pipecat[elevenlabs]
   ```

### Basic Usage

```python
import os
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.transports.local.audio import LocalAudioTransport

# Initialize services
llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
tts = ElevenLabsTTSService(api_key=os.getenv("ELEVENLABS_API_KEY"))
transport = LocalAudioTransport()

# Build pipeline
pipeline = Pipeline([
    transport.input(),
    stt,
    llm,
    tts,
    transport.output()
])

# Run the application
async def main():
    task = PipelineTask(pipeline)
    runner = PipelineRunner()
    await runner.run(task)
```

## Development

This project is set up for voice AI development using Pipecat. You can:

1. **Start with the basics** - Implement simple voice echo or greeting
2. **Add conversational AI** - Integrate with LLMs for intelligent responses
3. **Implement function calling** - Connect external APIs and services
4. **Add multimodal features** - Process video alongside audio
5. **Deploy to production** - Use WebRTC or cloud transports

## Resources

- [Pipecat Documentation](https://docs.pipecat.ai/)
- [Pipecat GitHub Repository](https://github.com/pipecat-ai/pipecat)
- [Example Applications](https://github.com/pipecat-ai/pipecat/tree/main/examples)

## License

This project uses the Pipecat framework under its respective license terms.
