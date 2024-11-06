import os
import discord
import traceback
import asyncio
from discord.ext import commands
from agency_swarm import Agency
from agency_swarm.agents.Shadow.ShadowAgent import ShadowAgent
from agency_swarm.agents.Echo.EchoAgent import EchoAgent
from agency_swarm.agents.Lyra.LyraAgent import LyraAgent
from agency_swarm.agents.Eve.EveAgent import EveAgent
from agency_swarm.agents.Nova.NovaAgent import NovaAgent
from agency_swarm.agents.Miles.MilesAgent import MilesAgent
from agency_swarm.agents.Aiden.AidenAgent import AidenAgent
from agency_swarm.agents.Ace.AceAgent import AceAgent
from agency_swarm.agents.Scout.ScoutAgent import ScoutAgent
from pinecone import Pinecone, ServerlessSpec

# Enhanced logging setup
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables directly from Render's environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Verify environment variables
if not DISCORD_TOKEN:
    logger.error("ERROR: DISCORD_TOKEN is missing. Check your environment variables.")
    exit(1)
else:
    logger.info("DISCORD_TOKEN is loaded.")

# Initialize specific agents for Discord roles
try:
    shadow_agent = ShadowAgent()
    echo_agent = EchoAgent()
    lyra_agent = LyraAgent()
    eve_agent = EveAgent()
    nova_agent = NovaAgent()
    miles_agent = MilesAgent()
    aiden_agent = AidenAgent()
    ace_agent = AceAgent()
    scout_agent = ScoutAgent()
    logger.info("All agents initialized successfully")
except Exception as e:
    logger.error(f"Error initializing agents: {str(e)}")
    logger.error(traceback.format_exc())
    exit(1)

# Define agency_chart with the appropriate hierarchy or communication flow
agency_chart = [
    shadow_agent,
    [shadow_agent, echo_agent],
    [shadow_agent, lyra_agent],
    [shadow_agent, eve_agent],
    [shadow_agent, nova_agent],
    [shadow_agent, miles_agent],
    [shadow_agent, aiden_agent],
    [shadow_agent, ace_agent],
    [shadow_agent, scout_agent]
]

# Initialize the Agency
try:
    agency = Agency(
        agency_chart=agency_chart,
        shared_instructions="Guidelines for managing tasks and coordinating cross-agent interactions."
    )
    logger.info("Agency initialized successfully")
except Exception as e:
    logger.error(f"Error initializing agency: {str(e)}")
    logger.error(traceback.format_exc())
    exit(1)

# Define trigger phrases for proactive help
trigger_phrases = [
    "I need help", "when is the next live call", "trading psychology", "mindset",
    "community event", "how do I", "content creation", "data analysis",
    "marketing", "project management", "market analysis"
]

# Discord bot setup with relevant intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def process_message_with_timeout(agent, question, timeout=30):
    """Process message with timeout to prevent hanging"""
    try:
        response = await asyncio.wait_for(
            agent.execute(question),  # Changed from process_input to execute
            timeout=timeout
        )
        return response
    except asyncio.TimeoutError:
        logger.error(f"Processing timed out after {timeout} seconds")
        return "I apologize, but the response took too long to generate. Please try again."
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(traceback.format_exc())
        return None

@bot.event
async def on_ready():
    logger.info(f'Bot logged in as {bot.user}')
    logger.info(f'Bot is connected to the following guilds:')
    for guild in bot.guilds:
        logger.info(f'- {guild.name} (id: {guild.id})')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    logger.info(f"Received message from {message.author} in {message.channel}: {message.content}")
    user_question = message.content.lower()
    response = None

    try:
        should_respond = False
        if bot.user.mentioned_in(message):
            logger.info("Bot was mentioned directly")
            should_respond = True
        elif any(phrase in user_question for phrase in trigger_phrases):
            logger.info(f"Trigger phrase detected: {[phrase for phrase in trigger_phrases if phrase in user_question]}")
            should_respond = True

        if should_respond:
            async with message.channel.typing():
                logger.info("Processing message with shadow_agent")
                response = await process_message_with_timeout(shadow_agent, user_question)
                
                if response:
                    logger.info(f"Generated response: {response[:100]}...")  # Log first 100 chars
                    await message.channel.send(response)
                else:
                    logger.warning("No response generated")
                    await message.channel.send("I apologize, but I encountered an error processing your request. Please try again.")

    except Exception as e:
        logger.error(f"Error in message handling: {str(e)}")
        logger.error(traceback.format_exc())
        try:
            await message.channel.send("I encountered an error processing your message. Please try again later.")
        except:
            logger.error("Failed to send error message to channel")

# Initialize Pinecone with improved error handling
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "elevatedfx-index"

    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="euclidean",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
        )
    logger.info("Pinecone initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Pinecone: {str(e)}")
    logger.error(traceback.format_exc())

# Run the bot
logger.info("Starting Discord bot...")
bot.run(DISCORD_TOKEN)
