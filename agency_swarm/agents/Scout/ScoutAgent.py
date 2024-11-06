from agency_swarm.agents import Agent
from typing_extensions import override
import re

class ScoutAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Scout",
            description="Scout is the Project Management Agent responsible for task assignment, project tracking, and timeline management.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],  # Add relevant tools if needed later
            tools_folder="./tools",
            validation_attempts=1,
            temperature=0.5,
            max_prompt_tokens=2000,
        )

    @override
    def response_validator(self, message):
        # Validator to ensure responses align with project management tasks
        keywords = r'(task|project|timeline|schedule|status|assign|progress|update|deadline|prioritize|overview|milestone)'

        if not re.search(keywords, message, re.IGNORECASE):
            raise ValueError("The response does not seem relevant to project management tasks. Please refocus on project and task coordination.")

        return message
