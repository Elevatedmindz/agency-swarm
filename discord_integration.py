import os
import discord
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

# Load environment variables directly from Render’s environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Verify environment variables
if not DISCORD_TOKEN:
    print("ERROR: DISCORD_TOKEN is missing. Check your environment variables.")
    exit(1)
else:
    print("DISCORD_TOKEN is loaded.")

# Initialize specific agents for Discord roles
shadow_agent = ShadowAgent()
echo_agent = EchoAgent()
lyra_agent = LyraAgent()
eve_agent = EveAgent()
nova_agent = NovaAgent()
miles_agent = MilesAgent()
aiden_agent = AidenAgent()
ace_agent = AceAgent()
scout_agent = ScoutAgent()

# Define an agency_chart with the appropriate hierarchy or communication flow
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
agency = Agency(
    agency_chart=agency_chart,
    shared_instructions="Guidelines for managing tasks and coordinating cross-agent interactions."
)
print("Agency initialized with chart and shared instructions.")

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

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}. Ready to serve!')

@bot.event
async def on_message(message):
    print(f"Received message from {message.author}: {message.content}")

    if message.author == bot.user:
        return

    user_question = message.content.lower()
    response = None

    try:
        async with message.channel.typing():
            if bot.user.mentioned_in(message):
                print("Bot was mentioned directly.")
                response = await shadow_agent.process_input(user_question)
            elif any(phrase in user_question for phrase in trigger_phrases):
                print("Trigger phrase detected.")
                response = await shadow_agent.process_input(user_question)

        if response:
            print(f"Sending response: {response}")
            await message.channel.send(response)
        else:
            print("No response generated.")
    
    except Exception as e:
        print(f"Error processing message: {e}")

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
    print("Pinecone initialized successfully.")
except Exception as e:
    print(f"Error initializing Pinecone: {e}")

# Run the bot
print("Starting Discord bot...")
bot.run(DISCORD_TOKEN)
