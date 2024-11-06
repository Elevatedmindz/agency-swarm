from typing_extensions import override
import re
from agency_swarm.agents import Agent
from agency_swarm.tools import FileSearch
from agency_swarm.util.validators import llm_validator
import logging
from openai import AsyncOpenAI  # Add this import
import os

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
            temperature=0.5,
            max_prompt_tokens=25000,
        )
        # Initialize the OpenAI client
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    @override
    def response_validator(self, message):
        pattern = r'(```)((.*\n){5,})(```)'
        if re.search(pattern, message):
            raise ValueError(
                "Please avoid returning code snippets. Shadow's role is to assist with operations and provide guidance, not code-related tasks."
            )
        llm_validator(statement="Verify that the response from Shadow provides clear guidance or information related "
                              "to the user's query without including code. Ensure that Shadow's message is "
                              "conversational and supports operations or guidance.",
                     client=self.client)(message)
        return message

    async def execute(self, message: str) -> str:
        """
        Process incoming messages and generate responses.
        """
        try:
            logger.info(f"Processing message in ShadowAgent: {message[:100]}...")

            # Create the message for the GPT model
            messages = [
                {"role": "system", "content": self.description},
                {"role": "user", "content": message}
            ]

            # Generate response using the OpenAI API directly
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # or whichever model you prefer
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_prompt_tokens
            )

            # Extract the response text
            response_text = response.choices[0].message.content

            # Validate the response
            try:
                validated_response = self.response_validator(response_text)
                logger.info("Response validated successfully")
                return validated_response
            except ValueError as ve:
                logger.warning(f"Response validation failed: {str(ve)}")
                return "I apologize, but I need to focus on providing operational guidance rather than technical details. How can I help you with ElevatedFX resources or general guidance?"
            except Exception as e:
                logger.error(f"Unexpected error in response validation: {str(e)}")
                return "I apologize, but I encountered an issue processing your request. Please try restating your question."

        except Exception as e:
            logger.error(f"Error in ShadowAgent execute method: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."
