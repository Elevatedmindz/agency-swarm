from agency_swarm.agents import Agent
from typing_extensions import override
import re

class AceAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Ace",
            description="Ace specializes in market analysis, tracking trends, and providing insights.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],  # Tools can be added in the next phase
            tools_folder="./tools",
            validation_attempts=1,
            temperature=0.7,
            max_prompt_tokens=1500,
        )

    @override
    def response_validator(self, message):
        pattern = r'(market\sanalysis|trend|forecast|insight)'
        
        if not re.search(pattern, message, re.IGNORECASE):
            raise ValueError("Response did not provide the necessary market insights. Please ensure your response focuses on relevant market analysis.")

        return message
