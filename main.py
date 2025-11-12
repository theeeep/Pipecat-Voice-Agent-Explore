import os

from dotenv import load_dotenv
from loguru import logger

# print("🚀 Starting Pipecat bot...")
# print("⏳ Loading models and imports (20 seconds, first run only)\n")
# logger.info("Loading Local Smart Turn Analyzer V3...")
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3

# logger.info("✅ Local Smart Turn Analyzer V3 loaded")
# logger.info("Loading Silero VAD model...")
from pipecat.audio.vad.silero import SileroVADAnalyzer

# logger.info("✅ Silero VAD model loaded")
from pipecat.audio.vad.vad_analyzer import VADParams

# logger.info("Loading pipeline components...")
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams

# Pipecat Flows imports
from pipecat_flows import FlowArgs, FlowManager, FlowsFunctionSchema, NodeConfig

logger.info("✅ All components loaded successfully!")

load_dotenv(override=True)


def create_greeting_node() -> NodeConfig:
    return NodeConfig(
        name="greeting",
        task_messages=[
            {
                "role": "system",
                "content": "Greet the user warmly, introduce yourself, and ask for their name. Wait for their response.",
            }
        ],
        functions=[
            FlowsFunctionSchema(
                name="record_name",
                handler=handler_name,
                description="",
                properties={"name": {"type": "string"}},
                required=["name"],
            )
        ],
    )


## handler
async def handler_name(args: FlowArgs, flow_manager: FlowManager) -> tuple[None, NodeConfig]:
    logger.info(f"User's name is {args['name']}")
    flow_manager.state.update({"name": args["name"]})
    return (None, create_greeting_node())


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting bot")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="6ccbfb76-1fc6-48f7-b71d-91ac6298247b",  # Tessa
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    context = LLMContext()
    context_aggregator = LLMContextAggregatorPair(context)

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,  # RTVI processor
            stt,
            context_aggregator.user(),  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    # Initialize flow Manager in dynamic mode
    flow_manager = FlowManager(task=task, llm=llm, context_aggregator=context_aggregator, transport=transport)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")
        # Kick off the conversation.
        await flow_manager.initialize(create_greeting_node())

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)

    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""

    transport_params = {
        "daily": lambda: DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
    }

    transport = await create_transport(runner_args, transport_params)

    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
