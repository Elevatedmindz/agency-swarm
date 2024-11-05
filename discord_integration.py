import os
import discord
from discord.ext import commands
from agency_swarm import Agent, Agency
import pinecone

# Load environment variables directly from Render’s environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Initialize the main Agency Swarm agents
shadow_agent = Agent(
    name="Shadow",
    description="Lead assistant for ElevatedFX operations.",
    instructions="Manage user interactions and guide through ElevatedFX resources."
)

# You can add additional agents as needed
echo_agent = Agent(
    name="Echo",
    description="Customer support specialist",
    instructions="Handle all customer queries and assist with platform navigation."
)

# Define an Agency for managing communication flow
agency = Agency(
    agents=[shadow_agent, echo_agent],
    shared_instructions="Guidelines for managing tasks and coordinating cross-agent interactions."
)

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} - Ready to serve!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Process the message with Shadow or relevant agent
    if message.content.startswith("!ask-shadow"):
        user_question = message.content[len("!ask-shadow "):]
        response = agency.agents[0].process_input(user_question)  # Calls Shadow by default
        await message.channel.send(response)

    elif message.content.startswith("!ask-echo"):
        user_question = message.content[len("!ask-echo "):]
        response = agency.agents[1].process_input(user_question)  # Calls Echo for support queries
        await message.channel.send(response)

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Example: Creating a Pinecone index (you can adjust based on your project needs)
index_name = "your_index_name"  # Replace with your desired index name

# Check if the index already exists, create if it doesn’t
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=1536)  # 1536 is typical for OpenAI embeddings

# Run the bot
bot.run(DISCORD_TOKEN)
