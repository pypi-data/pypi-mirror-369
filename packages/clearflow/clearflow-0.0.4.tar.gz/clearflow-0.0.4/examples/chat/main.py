#!/usr/bin/env python3
"""Main entry point for the chat application - handles all UI concerns."""

import asyncio
import os
import sys
from typing import Any

from dotenv import load_dotenv
from flow import create_chat_flow

ChatState = dict[str, Any]


def print_welcome() -> None:
    """Print welcome message."""
    print("Welcome to ClearFlow Chat!")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("-" * 50)


def get_user_input() -> str | None:
    """Get input from user. Returns None if user wants to exit."""
    try:
        user_input = input("You: ")
        if user_input.lower() in {"quit", "exit", "bye"}:
            return None
    except (EOFError, KeyboardInterrupt):
        # Handle Ctrl+C or Ctrl+D gracefully
        return None
    else:
        return user_input


def display_response(response: str) -> None:
    """Display the assistant's response."""
    print(f"\nAssistant: {response}")
    print("-" * 50)


async def run_chat_session() -> None:
    """Run the interactive chat session - pure UI orchestration."""
    # Initialize flow (business logic component)
    flow = create_chat_flow()

    # Initialize state - let the flow handle conversation initialization
    state: ChatState = {}

    # Display welcome
    print_welcome()

    # Main UI loop
    while True:
        # Get user input (pure UI)
        user_input = get_user_input()
        if user_input is None:
            print("\nGoodbye!")
            break

        # Pass user input to flow (business logic handles conversation management)
        # Create new state with user input
        state = {**state, "user_input": user_input}
        result = await flow(state)

        # Preserve conversation state for next iteration
        state = result.state

        # Display response (pure UI)
        if result.outcome == "responded":
            last_response = result.state.get("last_response")
            if last_response:
                display_response(last_response)


async def main() -> None:
    """Main application entry point."""
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    try:
        await run_chat_session()
    except (KeyboardInterrupt, EOFError):
        # User interrupted - exit gracefully
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
