import os
import discord
from discord.ext import commands
from agency_swarm import Agent, Agency
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

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

# Run the bot
bot.run(DISCORD_TOKEN)
