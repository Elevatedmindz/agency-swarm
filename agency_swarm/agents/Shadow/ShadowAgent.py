from typing_extensions import override
import re
from agency_swarm.agents import Agent
from agency_swarm.tools import FileSearch
from agency_swarm.util.validators import llm_validator


class ShadowAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Shadow",
            description="Shadow is the lead operations coordinator, responsible for managing user interactions and guiding through ElevatedFX resources.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[FileSearch],
            tools_folder="./tools",
            validation_attempts=1,
            temperature=0.5,  # Adjusted for a more conversational tone
            max_prompt_tokens=25000,
        )

    @override
    def response_validator(self, message):
        # Pattern to detect code snippets, ensuring Shadow avoids technical or developer-specific responses.
        pattern = r'(```)((.*\n){5,})(```)'

        if re.search(pattern, message):
            # Raise an error if a code snippet is detected, since Shadow should not provide coding output
            raise ValueError(
                "Please avoid returning code snippets. Shadow’s role is to assist with operations and provide guidance, not code-related tasks."
            )

        # Validate the response to ensure it's appropriately conversational and operations-focused
        llm_validator(statement="Verify that the response from Shadow provides clear guidance or information related "
                                "to the user's query without including code. Ensure that Shadow's message is "
                                "conversational and supports operations or guidance.",
                      client=self.client)(message)

        return message
