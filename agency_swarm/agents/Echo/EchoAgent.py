from agency_swarm.agents import Agent
from agency_swarm.tools import FAQTool, SupportTicketTool  # Replace with actual tools as necessary
from typing_extensions import override
import re

class EchoAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Echo",
            description="Echo specializes in customer support, assisting users with inquiries and troubleshooting issues.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[FAQTool, SupportTicketTool],  # Replace with appropriate tools
            tools_folder="./tools",
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
