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
    shadow_agent,  # Main agent who coordinates
    [shadow_agent, echo_agent],  # Shadow communicates with Echo
    [shadow_agent, lyra_agent],  # Shadow communicates with Lyra
    [shadow_agent, eve_agent],  # Shadow communicates with Eve
    [shadow_agent, nova_agent],  # Shadow communicates with Nova
    [shadow_agent, miles_agent],  # Shadow communicates with Miles
    [shadow_agent, aiden_agent],  # Shadow communicates with Aiden
    [shadow_agent, ace_agent],  # Shadow communicates with Ace
    [shadow_agent, scout_agent]  # Shadow communicates with Scout
]

# Initialize the Agency with the defined agency_chart
agency = Agency(
    agency_chart=agency_chart,
    shared_instructions="Guidelines for managing tasks and coordinating cross-agent interactions."
)

# Define trigger phrases for proactive help
trigger_phrases = [
    "I need help",
    "when is the next live call",
    "trading psychology",
    "mindset",
    "community event",
    "how do I",
    "content creation",
    "data analysis",
    "marketing",
    "project management",
    "market analysis"
]

# Discord bot setup with relevant intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} - Ready to serve!')

@bot.event
async def on_message(message):
    print(f"Message received: {message.content}")  # Log every message the bot receives

    if message.author == bot.user:
        return

    try:
        # Check for direct mention of Shadow and proactive help
        response = None
        if bot.user.mentioned_in(message):
            print("Shadow agent directly mentioned.")
            response = await shadow_agent.process_input(message.content)
        elif any(phrase in message.content.lower() for phrase in trigger_phrases):
            print("Proactive trigger phrase detected.")
            response = await shadow_agent.process_input(message.content)

        # Send the response if one was generated
        if response:
            await message.channel.send(response)
        else:
            print("No response generated for the message.")
    
    except Exception as e:
        print(f"Error in on_message processing: {e}")

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
except Exception as e:
    print(f"Error initializing Pinecone: {e}")

# Run the bot
bot.run(DISCORD_TOKEN)
