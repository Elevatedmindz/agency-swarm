import os
import discord
from discord.ext import commands
from agency_swarm import Agent, Agency
from pinecone import Pinecone, ServerlessSpec  # Updated import

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

    try:
        # Show typing indicator while generating a response
        async with message.channel.typing():
            # If Shadow is mentioned (@Shadow), respond directly
            if bot.user.mentioned_in(message):
                response = await shadow_agent.process_input(user_question)

            # Check if the message contains a trigger phrase for proactive help
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
                    # Default response if no specific role is identified
                    response = await shadow_agent.process_input(
                        f"{message.author.mention}, how can I assist you today?"
                    )

            # Default delegation for Shadow based on detected context
            elif "support" in user_question or "help" in user_question:
                response = await echo_agent.process_input(user_question)  # Customer support via Echo
            elif "psychology" in user_question or "mindset" in user_question:
                response = await eve_agent.process_input(user_question)  # Trading psychology via Eve
            elif "community" in user_question or "event" in user_question:
                response = await lyra_agent.process_input(user_question)  # Community engagement via Lyra
            else:
                # If no specific context, Shadow handles the response
                response = await shadow_agent.process_input(user_question)

        # Send the response if any was generated
        if response:
            await message.channel.send(response)
    
    except Exception as e:
        print(f"Error processing message: {e}")

# Initialize Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Example: Creating a Pinecone index (you can adjust based on your project needs)
    index_name = "elevatedfx-index"  # Replace with your desired index name

    # Check if the index already exists, create if it doesn’t
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,  # Typical for OpenAI embeddings
            metric="euclidean",  # Choose a suitable metric
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)  # Adjust region as needed
        )
except Exception as e:
    print(f"Error initializing Pinecone: {e}")

# Run the bot
bot.run(DISCORD_TOKEN)
