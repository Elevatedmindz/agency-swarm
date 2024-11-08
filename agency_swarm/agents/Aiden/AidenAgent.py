from agency_swarm.agents import Agent
from typing_extensions import override
import re

class AidenAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Aiden",
            description="Aiden manages marketing tasks and schedules content for timely distribution.",
            instructions="./instructions.md",
            files_folder=None,
            schemas_folder=None,
            tools=[],  # Tools can be added in the next phase
            tools_folder=None,
            validation_attempts=1,
            temperature=0.8,
            max_prompt_tokens=1200,
        )

    @override
    def response_validator(self, message):
        pattern = r'(schedule|content|marketing|campaign)'
        
        if not re.search(pattern, message, re.IGNORECASE):
            raise ValueError("Response did not address the scheduling or marketing requirements. Please ensure your response is focused on relevant tasks.")

        return message
