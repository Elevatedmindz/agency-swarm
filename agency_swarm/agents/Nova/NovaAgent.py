from agency_swarm.agents import Agent
from typing_extensions import override
import re

class NovaAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Nova",
            description="Nova is responsible for creating and curating high-quality content for ElevatedFX.",
            instructions="./instructions.md",
            files_folder=None,
            schemas_folder=None,
            tools=[],
            tools_folder=None,
            validation_attempts=2,
            temperature=0.7,
            max_prompt_tokens=3000,
        )

    @override
    def response_validator(self, message):
        # Validator to ensure responses align with content creation tasks
        keywords = r'(content|post|article|blog|social media|graphic|video|marketing|creative|draft|story|engagement|writing)'

        if not re.search(keywords, message, re.IGNORECASE):
            raise ValueError("The response does not seem relevant to content creation or marketing tasks. Please refocus on creating content.")

        return message
