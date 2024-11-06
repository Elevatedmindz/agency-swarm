from typing_extensions import override
import re
from agency_swarm.agents import Agent
from agency_swarm.tools import FileSearch
from agency_swarm.util.validators import llm_validator
import logging

logger = logging.getLogger(__name__)

class ShadowAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Shadow",
            description="Shadow is the lead operations coordinator, responsible for managing user interactions and guiding through ElevatedFX resources.",
            instructions="./instructions.md",
            files_folder=None,
            schemas_folder=None,
            tools=[],
            tools_folder=None,
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
                "Please avoid returning code snippets. Shadow's role is to assist with operations and provide guidance, not code-related tasks."
            )
        # Validate the response to ensure it's appropriately conversational and operations-focused
        llm_validator(statement="Verify that the response from Shadow provides clear guidance or information related "
                              "to the user's query without including code. Ensure that Shadow's message is "
                              "conversational and supports operations or guidance.",
                     client=self.client)(message)
        return message

    async def execute(self, message: str) -> str:
        """
        Process incoming messages and generate responses.
        
        Args:
            message (str): The incoming message from the user
            
        Returns:
            str: The generated response
        """
        try:
            logger.info(f"Processing message in ShadowAgent: {message[:100]}...")  # Log first 100 chars
            
            # Generate the initial response
            response = await self.llm.agenerate_response(message)
            
            # Validate the response using the existing validator
            try:
                validated_response = self.response_validator(response)
                logger.info("Response validated successfully")
                return validated_response
            except ValueError as ve:
                logger.warning(f"Response validation failed: {str(ve)}")
                # If validation fails, generate a new, more appropriate response
                return "I apologize, but I need to focus on providing operational guidance rather than technical details. How can I help you with ElevatedFX resources or general guidance?"
            except Exception as e:
                logger.error(f"Unexpected error in response validation: {str(e)}")
                return "I apologize, but I encountered an issue processing your request. Please try restating your question."
                
        except Exception as e:
            logger.error(f"Error in ShadowAgent execute method: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."
