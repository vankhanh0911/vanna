from typing import Any
from typing import Dict
from typing import List

from langfuse import get_client
from vanna.core.system_prompt import SystemPromptBuilder
from vanna.core.user import User


class LangfuseManagedSystemPromptBuilder(SystemPromptBuilder):
    """
    System prompt builder using Langfuse Prompt Management

    Benefits:
    - Version control for prompts
    - A/B testing different prompts
    - Track which prompt version was used in each trace
    - Update prompts without code changes
    """

    def __init__(self, prompt_name: str = "SystemPrompt"):
        self.langfuse = get_client()
        self.prompt_name = prompt_name

    async def build_system_prompt(
        self, user: User, tool_schemas: List[Dict[str, Any]], context: Dict[str, Any] = None
    ) -> str:
        """
        Fetch system prompt from Langfuse and compile with variables
        """

        try:
            # Fetch prompt from Langfuse
            prompt = self.langfuse.get_prompt(
                name=self.prompt_name,
                version=None,  # Get latest version
                # Or specify version: version=1
            )

            # Compile prompt with variables
            system_prompt = prompt.compile(
                num_tools=len(tool_schemas),
                user_id=user.id if hasattr(user, "id") else "anonymous",
                database_name="antsomi_cdp",
                # Add any other variables your prompt template uses
            )

            # Log which prompt version was used (automatically done by Langfuse)
            # This will appear in the trace metadata

            return system_prompt

        except Exception as e:
            # Fallback to default prompt if Langfuse fetch fails
            print(f"Failed to fetch prompt from Langfuse: {e}")
            return self._get_fallback_prompt(user, tool_schemas, context)

    def _get_fallback_prompt(self, user: User, tool_schemas: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Fallback prompt if Langfuse is unavailable"""
        return """You are a helpful AI assistant for data analysis.
        
Available tools: {num_tools}
Please help the user query and analyze their data.""".format(
            num_tools=len(tool_schemas)
        )
