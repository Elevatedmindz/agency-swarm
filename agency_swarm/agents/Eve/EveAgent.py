from agency_swarm.agents import Agent
from typing_extensions import override
import re

class EveAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Eve",
            description="Eve specializes in trading psychology, providing users with mindset support and emotional guidance.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            validation_attempts=1,
            temperature=0.8,
            max_prompt_tokens=1200,
        )

    @override
    def response_validator(self, message):
        # Validator ensures Eve’s responses stay focused on mindset and trading psychology
        keywords = r'(mindset|emotions|psychology|focus|discipline|trading stress|patience|confidence)'

        if not re.search(keywords, message, re.IGNORECASE):
            raise ValueError("The response does not address trading psychology or mindset topics. Ensure responses stay on topic.")

        return message
