#!/usr/bin/env python3
"""Main entry point for structured output extraction example."""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flow import create_extraction_flow
from models import ExtractorState


def load_resume_text(file_path: str = "data.txt") -> str:
    """Load resume text from file."""
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: Could not find {file_path}")
        print("Please create a data.txt file with resume content.")
        sys.exit(1)


def display_errors(errors: list[str]) -> None:
    """Display validation or extraction errors."""
    print("\n❌ Errors encountered:")
    for error in errors:
        print(f"  • {error}")


def display_result(state: ExtractorState, outcome: str) -> None:
    """Display the result based on flow outcome."""
    print(f"\nFlow completed with outcome: {outcome}")

    # Check for errors
    errors = state.get("validation_errors", [])
    if errors:
        display_errors(errors)
        return

    # Display formatted output if available
    formatted = state.get("formatted_output")
    if formatted:
        print("\n✅ Successfully extracted resume:")
        print(formatted)
    elif outcome == "no_input":
        print("\n⚠️  No input text provided")
    else:
        print("\n⚠️  No data extracted")


async def main() -> None:
    """Run the structured output extraction example."""
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    print("🔍 ClearFlow Structured Output Example")
    print("=" * 50)

    # Load resume text
    print("Loading resume from data.txt...")
    resume_text = load_resume_text()
    print(f"Loaded {len(resume_text)} characters")

    # Create initial state
    initial_state: ExtractorState = {"input_text": resume_text}

    # Create and run flow
    print("\nStarting extraction flow...")
    print("→ Extracting structured data from resume...")
    flow = create_extraction_flow()
    result = await flow(initial_state)

    # Display results
    display_result(result.state, result.outcome)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
