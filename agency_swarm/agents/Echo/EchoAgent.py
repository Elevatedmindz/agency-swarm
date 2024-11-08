from agency_swarm.agents import Agent
from typing_extensions import override
import re

class EchoAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Echo",
            description="Echo specializes in customer support, assisting users with inquiries and troubleshooting issues.",
            instructions="./instructions.md",
            files_folder=None,
            schemas_folder=None,
            tools=[],  # Tools can be added in the next phase
            tools_folder=None,
            validation_attempts=1,
            temperature=0.7,
            max_prompt_tokens=1500,
        )

    @override
    def response_validator(self, message):
        keywords = r'(support|help|inquiry|issue|troubleshoot|FAQ)'
        
        if not re.search(keywords, message, re.IGNORECASE):
            raise ValueError("The response did not sufficiently address customer support concerns. Ensure the response aligns with support and troubleshooting tasks.")

        return message
