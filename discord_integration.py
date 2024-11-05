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

# Define roles for Discord-based agents
roles = {
    "lead_assistant": "Lead Operations Coordinator",
    "customer_support": "Customer Support Specialist",
    "community_engagement": "Community Engagement",
    "trade_psychologist": "Trading Psychology Support"
}

# Initialize Discord agents
shadow_agent = Agent(
    name="Shadow",
    description=roles["lead_assistant"],
    instructions="Manage user interactions and guide through ElevatedFX resources."
)

echo_agent = Agent(
    name="Echo",
    description=roles["customer_support"],
    instructions="Handle all customer queries and assist with platform navigation."
)

lyra_agent = Agent(
    name="Lyra",
    description=roles["community_engagement"],
    instructions="Engage with the community, share updates, and foster interactions on Discord."
)

eve_agent = Agent(
    name="Eve",
    description=roles["trade_psychologist"],
    instructions="Assist users with trading psychology, provide emotional support, and offer mindset advice."
)

# Define an Agency for managing communication flow
agency = Agency(
    [shadow_agent, echo_agent, lyra_agent, eve_agent],
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

# Discord bot setup
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

    # If Shadow is mentioned (@Shadow), respond directly
    if bot.user.mentioned_in(message):
        response = shadow_agent.process_input(user_question)

    # Check if the message contains a trigger phrase for proactive help
    elif any(phrase in user_question for phrase in trigger_phrases):
        if "help" in user_question or "support" in user_question:
            response = echo_agent.process_input(
                f"{message.author.mention}, it seems you need some assistance. Echo is here to help!"
            )
        elif "trading psychology" in user_question or "mindset" in user_question:
            response = eve_agent.process_input(
                f"{message.author.mention}, it sounds like you're interested in trading psychology. Eve can offer insights on mindset and emotional support."
            )
        elif "community" in user_question or "event" in user_question:
            response = lyra_agent.process_input(
                f"{message.author.mention}, it looks like you're curious about community events! Lyra can provide more details on upcoming activities."
            )
        else:
            # Default response if no specific role is identified
            response = shadow_agent.process_input(
                f"{message.author.mention}, how can I assist you today?"
            )

    # Default delegation for Shadow based on detected context
    elif "support" in user_question or "help" in user_question:
        response = echo_agent.process_input(user_question)  # Customer support via Echo
    elif "psychology" in user_question or "mindset" in user_question:
        response = eve_agent.process_input(user_question)  # Trading psychology via Eve
    elif "community" in user_question or "event" in user_question:
        response = lyra_agent.process_input(user_question)  # Community engagement via Lyra
    else:
        # If no specific context, Shadow handles the response
        response = shadow_agent.process_input(user_question)

    # Send the response if any was generated
    if response:
        await message.channel.send(response)

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Example: Creating a Pinecone index (you can adjust based on your project needs)
index_name = "elevatedfx_index"  # Replace with your desired index name

# Check if the index already exists, create if it doesn’t
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=1536)  # 1536 is typical for OpenAI embeddings

# Run the bot
bot.run(DISCORD_TOKEN)
