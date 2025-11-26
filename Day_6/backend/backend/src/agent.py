import logging
import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
# murf may be provided as a local/custom plugin in some environments.
# Try importing it first and fall back gracefully if it's not installed.
try:
    from livekit.plugins import murf
except Exception:
    murf = None

from livekit.plugins import silero, google, deepgram
try:
    from livekit.plugins import noise_cancellation
except Exception:
    noise_cancellation = None

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Paths to data files
FAQ_CONTENT_PATH = "zomato_faq.json"
LEADS_LOG_PATH = "leads.json"

# Global FAQ data (loaded once at startup for performance)
FAQ_DATA = None


def load_faq_content():
    """Load the Zomato FAQ content from JSON file."""
    if os.path.exists(FAQ_CONTENT_PATH):
        try:
            with open(FAQ_CONTENT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("FAQ content file is corrupted")
            return {"company_info": {}, "faq": [], "pricing": {}, "target_audience": []}
    return {"company_info": {}, "faq": [], "pricing": {}, "target_audience": []}


def load_leads():
    """Load existing leads from JSON file."""
    if os.path.exists(LEADS_LOG_PATH):
        try:
            with open(LEADS_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Leads log file is corrupted, starting fresh")
            return []
    return []


def save_leads(leads_data):
    """Save leads to JSON file."""
    try:
        with open(LEADS_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(leads_data, f, indent=2, ensure_ascii=False)
        logger.info("Leads saved successfully")
    except Exception as e:
        logger.error(f"Error saving leads: {e}")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a Sales Development Representative (SDR) for Zomato, India's leading food delivery and restaurant discovery platform. Your role is to qualify leads, answer questions, and capture potential customer information.

**Your Personality:**
- Friendly, professional, and enthusiastic about food and technology
- Consultative approach - understand needs before pitching
- Warm and conversational, not pushy or sales-y
- Knowledgeable about Zomato's full ecosystem

**Conversation Flow:**
1. **Warm Greeting**: Welcome the visitor and introduce yourself as a Zomato representative
2. **Discovery**: Ask what brought them here today and what they're working on
   - Are they a restaurant owner looking to grow?
   - A business needing food solutions?
   - Exploring partnership opportunities?
3. **Needs Assessment**: Listen actively and ask follow-up questions to understand their:
   - Current challenges with food delivery or restaurant management
   - Business goals and timeline
   - Team size and operation scale
4. **Answer Questions**: When asked about Zomato, use the search_faq tool to provide accurate answers
   - Never make up information not in the FAQ
   - If unsure, acknowledge it and offer to connect them with specialists
5. **Lead Capture**: Naturally collect information during conversation:
   - Name, Company, Email (essential)
   - Role, Use case, Team size, Timeline
   - Don't ask all at once - gather organically through conversation
6. **Summary & Next Steps**: When wrapping up:
   - Provide a brief summary of what you discussed
   - Confirm their interest level and timeline
   - Save the lead information
   - Offer next steps (demo, consultation, send materials)

**Important Guidelines:**
- Keep responses concise and voice-friendly
- Use the search_faq tool whenever asked specific questions about Zomato
- Focus on understanding their needs before presenting solutions
- Be honest if something is outside your knowledge - don't guess
- Save lead information only after collecting the essential details
- Make the conversation feel natural, not like an interrogation
- Show genuine interest in helping them succeed

**Key Information to Remember:**
- Zomato serves: Restaurants, cloud kitchens, delivery-only brands, QSRs
- Solutions: Food delivery platform, restaurant technology, Hyperpure supplies, Blinkit quick commerce
- Geographic reach: 1000+ cities across India
- Different offerings for different business sizes and needs

Remember: You're here to help potential partners understand how Zomato can solve their problems. Build rapport, understand needs, and capture quality lead information!""",
        )

    @function_tool
    async def search_faq(
        self,
        context: RunContext,
        query: str,
    ):
        """Search the Zomato FAQ to answer customer questions accurately.
        
        Use this tool whenever the user asks questions about:
        - What Zomato does or offers
        - Pricing and plans
        - How services work
        - City coverage
        - Partnership details
        - Features and capabilities
        
        Args:
            query: The user's question or topic (e.g., "pricing", "delivery", "Zomato Gold", "restaurant partnership")
        """
        logger.info(f"Searching FAQ for: {query}")
        
        global FAQ_DATA
        if FAQ_DATA is None:
            FAQ_DATA = load_faq_content()
        
        query_lower = query.lower()
        relevant_answers = []
        
        # Search through FAQ entries
        for faq in FAQ_DATA.get("faq", []):
            question = faq["question"].lower()
            answer = faq["answer"]
            
            # Simple keyword matching
            if any(word in question for word in query_lower.split()) or any(word in query_lower for word in question.split()):
                relevant_answers.append(f"Q: {faq['question']}\nA: {answer}")
        
        if not relevant_answers:
            # Return general company info if no specific match
            company_info = FAQ_DATA.get("company_info", {})
            desc = company_info.get("description", "Leading food delivery platform")
            services = ", ".join(company_info.get("services", []))
            return f"Company: {company_info.get('name', 'Zomato')}\n{desc}\n\nServices: {services}"
        
        # Return top 2 most relevant answers to keep response concise
        return "\n\n".join(relevant_answers[:2])

    @function_tool
    async def save_lead(
        self,
        context: RunContext,
        name: str,
        email: str,
        company: Optional[str] = None,
        role: Optional[str] = None,
        use_case: Optional[str] = None,
        team_size: Optional[str] = None,
        timeline: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        """Save lead information after gathering details from the conversation.
        
        Call this tool when you have collected the essential information (name, email, and ideally company).
        The user doesn't need to explicitly ask to save - do it naturally when wrapping up.
        
        Args:
            name: Lead's full name
            email: Lead's email address
            company: Company/Restaurant name (if applicable)
            role: Their role/position (e.g., "Owner", "Manager", "Marketing Head")
            use_case: What they want to use Zomato for (e.g., "grow restaurant delivery", "manage multiple locations")
            team_size: Size of their team or business (e.g., "5-10", "single location", "chain of 20 outlets")
            timeline: When they're looking to start (e.g., "immediately", "next month", "exploring options")
            notes: Any additional context from the conversation
        """
        logger.info(f"Saving lead - Name: {name}, Email: {email}, Company: {company}")
        
        # Load existing leads
        leads = load_leads()
        
        # Create new lead entry
        lead = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "name": name,
            "email": email,
            "company": company,
            "role": role,
            "use_case": use_case,
            "team_size": team_size,
            "timeline": timeline,
            "notes": notes,
            "source": "Voice SDR Agent"
        }
        
        # Add to leads
        leads.append(lead)
        
        # Save to file
        save_leads(leads)
        
        return f"Lead information saved successfully! I've captured {name}'s details. Thank you for your interest in Zomato!"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector

    # Select TTS implementation: prefer Murf if available, otherwise fall back to Google TTS if installed.
    # If neither is available, leave TTS unset (None) so the session can still run in text-only mode.
    try:
        if murf is not None:
            tts_obj = murf.TTS(
                voice="en-US-matthew",
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True,
            )
        else:
            try:
                tts_obj = google.TTS(voice="alloy")
            except Exception:
                tts_obj = None
    except Exception:
        tts_obj = None

    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=tts_obj,
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        # Using VAD-based turn detection for Windows compatibility
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    assistant = Assistant()
    await session.start(
        agent=assistant,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()
    
    # Send initial greeting when user connects
    await session.say("Hello! Thanks for connecting with Zomato. I'm here to help answer any questions about our services and explore how we can support your business. What brings you here today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))




