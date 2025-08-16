"""Chat node implementation - pure business logic."""

from dataclasses import dataclass
from typing import Any, cast, override

from openai import AsyncOpenAI

from clearflow import Node, NodeResult

# Type for chat state with properly typed messages
ChatMessage = dict[str, str]  # {"role": "...", "content": "..."}
ChatState = dict[str, Any]  # Still need Any for other fields


@dataclass(frozen=True)
class ChatNode(Node[ChatState]):
    """Node that processes chat messages through a language model.

    This node handles the complete conversation management:
    1. Maintains conversation history
    2. Adds user messages when provided
    3. Ensures system prompt is present
    4. Processes through language model
    5. Returns updated conversation state
    """

    model: str = "gpt-4o-2024-08-06"
    system_prompt: str = "You are a helpful assistant."

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        """Process user input and generate language model response."""
        # Get conversation history and current user input
        messages: list[ChatMessage] = state.get("messages", [])
        user_input: str | None = state.get("user_input")

        # Initialize with system message if needed
        if not messages:
            messages = [{"role": "system", "content": self.system_prompt}]

        # If no user input provided, this is just initialization
        if user_input is None:
            init_state: ChatState = {**state, "messages": messages}
            return NodeResult(init_state, outcome="awaiting_input")

        # Add user message to conversation
        messages = [*messages, {"role": "user", "content": user_input}]

        # Call OpenAI API
        client = AsyncOpenAI()
        response = await client.chat.completions.create(
            model=self.model,
            messages=cast("Any", messages),  # Cast needed for OpenAI's complex types
        )

        # Extract assistant's response
        assistant_response = response.choices[0].message.content
        if not assistant_response:
            assistant_response = ""

        # Add assistant message to conversation
        messages = [*messages, {"role": "assistant", "content": assistant_response}]

        # Return updated state with full conversation
        new_state: ChatState = {
            **state,
            "messages": messages,
            "last_response": assistant_response,
            "user_input": None,  # Clear user input after processing
        }

        return NodeResult(new_state, outcome="responded")
