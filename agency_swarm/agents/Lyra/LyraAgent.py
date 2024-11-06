from agency_swarm.agents import Agent
from typing_extensions import override
import re

class LyraAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Lyra",
            description="Lyra specializes in community engagement, facilitating interactions and sharing updates within the community.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            validation_attempts=1,
            temperature=0.7,
            max_prompt_tokens=1500,
        )

    @override
    def response_validator(self, message):
        # Validator ensures Lyra’s responses focus on community engagement
        keywords = r'(community|engagement|events|poll|feedback|update|motivation|announcement|discussion|support)'

        if not re.search(keywords, message, re.IGNORECASE):
            raise ValueError("The response does not address community engagement topics. Ensure responses stay on topic.")

        return message
