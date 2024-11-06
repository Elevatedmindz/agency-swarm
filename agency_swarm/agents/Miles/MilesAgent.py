from agency_swarm.agents import Agent
from typing_extensions import override
import re

class MilesAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Miles",
            description="Miles specializes in data analysis, interpreting market data, and providing insights for informed decision-making.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            validation_attempts=2,
            temperature=0.6,
            max_prompt_tokens=2000,
        )

    @override
    def response_validator(self, message):
        # Validator to ensure responses align with data analysis and market insights
        keywords = r'(data analysis|market|insights|trend|performance|report|metrics|statistics|patterns|forecast|interpret)'

        if not re.search(keywords, message, re.IGNORECASE):
            raise ValueError("The response does not relate to data analysis or market insights. Ensure responses stay on topic.")

        return message
