import os
import discord
from discord.ext import commands
from agency_swarm import Agency
from agency_swarm.agents.Shadow.ShadowAgent import ShadowAgent
from agency_swarm.agents.Echo.EchoAgent import EchoAgent
from agency_swarm.agents.Lyra.LyraAgent import LyraAgent
from agency_swarm.agents.Eve.EveAgent import EveAgent
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

# Define an Agency for managing communication flow between agents
agency = Agency(
    agents=[shadow_agent, echo_agent, lyra_agent, eve_agent],
    shared_instructions="Guidelines for managing tasks and coordinating cross-agent interactions."
)

# Define trigger phrases for proactive help
trigger_phrases = [
    "I need help",
    "when is the next live call",
    "trading psychology",
    "mindset",
    "community event",
    "how do I"
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
    if message.author == bot.user:
        return

    user_question = message.content.lower()
    response = None

    try:
        # Show typing indicator while generating a response
        async with message.channel.typing():
            # Directly respond if Shadow is mentioned
            if bot.user.mentioned_in(message):
                response = await shadow_agent.process_input(user_question)

            # Check for proactive help based on trigger phrases
            elif any(phrase in user_question for phrase in trigger_phrases):
                if "help" in user_question or "support" in user_question:
                    response = await echo_agent.process_input(
                        f"{message.author.mention}, it seems you need some assistance. Echo is here to help!"
                    )
                elif "trading psychology" in user_question or "mindset" in user_question:
                    response = await eve_agent.process_input(
                        f"{message.author.mention}, it sounds like you're interested in trading psychology. Eve can offer insights on mindset and emotional support."
                    )
                elif "community" in user_question or "event" in user_question:
                    response = await lyra_agent.process_input(
                        f"{message.author.mention}, it looks like you're curious about community events! Lyra can provide more details on upcoming activities."
                    )
                else:
                    response = await shadow_agent.process_input(
                        f"{message.author.mention}, how can I assist you today?"
                    )

            # If no specific phrase, use context-based delegation
            elif "support" in user_question or "help" in user_question:
                response = await echo_agent.process_input(user_question)
            elif "psychology" in user_question or "mindset" in user_question:
                response = await eve_agent.process_input(user_question)
            elif "community" in user_question or "event" in user_question:
                response = await lyra_agent.process_input(user_question)
            else:
                response = await shadow_agent.process_input(user_question)

        # Send the response if any was generated
        if response:
            await message.channel.send(response)
    
    except Exception as e:
        print(f"Error processing message: {e}")

# Initialize Pinecone with improved error handling
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Example: Creating a Pinecone index
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
