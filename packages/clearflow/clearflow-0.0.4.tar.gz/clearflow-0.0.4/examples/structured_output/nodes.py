"""Node implementations for structured output extraction."""

from dataclasses import dataclass
from typing import override

from models import ExtractedResume, ExtractorState
from openai import AsyncOpenAI

from clearflow import Node, NodeResult


@dataclass(frozen=True)
class ExtractorNode(Node[ExtractorState]):
    """Extracts structured data from resume text using OpenAI."""

    model: str = "gpt-4o-2024-08-06"

    @override
    async def exec(self, state: ExtractorState) -> NodeResult[ExtractorState]:
        """Extract structured resume data from input text."""
        input_text = state.get("input_text", "")

        if not input_text:
            print("  ⚠️  No input text provided")
            error_state: ExtractorState = {
                **state,
                "validation_errors": ["No input text provided"],
            }
            return NodeResult(error_state, outcome="no_input")

        try:
            print("  🤖 Calling OpenAI API...")
            client = AsyncOpenAI()

            # Use OpenAI's structured output with Pydantic
            completion = await client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract structured information from the resume text. "
                            "Be thorough and accurate."
                        ),
                    },
                    {"role": "user", "content": input_text},
                ],
                response_format=ExtractedResume,
            )

            # The completion object itself is the ParsedChatCompletion
            # Access the parsed data directly
            parsed_data = completion.choices[0].message.parsed

            if parsed_data:
                msg = (
                    f"  ✅ Extracted: {parsed_data.name} "
                    f"({len(parsed_data.skills)} skills, "
                    f"{len(parsed_data.experiences)} experiences)"
                )
                print(msg)
                success_state: ExtractorState = {
                    **state,
                    "extracted_data": parsed_data,
                    "validation_errors": [],
                }
                return NodeResult(success_state, outcome="extracted")
            # Handle refusal or parsing failure
            refusal_msg = (
                completion.choices[0].message.refusal or "Failed to parse resume"
            )
            refusal_state: ExtractorState = {
                **state,
                "validation_errors": [f"Extraction failed: {refusal_msg}"],
            }
            return NodeResult(refusal_state, outcome="failed")

        except (ValueError, TypeError, KeyError) as exc:
            error_msg = f"API error: {exc!s}"
            exception_state: ExtractorState = {
                **state,
                "validation_errors": [error_msg],
            }
            return NodeResult(exception_state, outcome="failed")


@dataclass(frozen=True)
class ValidatorNode(Node[ExtractorState]):
    """Validates extracted resume data meets requirements."""

    min_experiences: int = 1
    min_skills: int = 3

    @override
    async def exec(self, state: ExtractorState) -> NodeResult[ExtractorState]:
        """Validate the extracted data meets minimum requirements."""
        print("→ Validating extracted data...")
        extracted_data = state.get("extracted_data")
        errors: list[str] = []

        if not extracted_data:
            errors.append("No extracted data to validate")
            no_data_state: ExtractorState = {**state, "validation_errors": errors}
            return NodeResult(no_data_state, outcome="invalid")

        # Validate required fields
        if not extracted_data.name:
            errors.append("Name is required")
        if not extracted_data.email or "@" not in extracted_data.email:
            errors.append("Valid email is required")

        # Validate minimum requirements
        if len(extracted_data.experiences) < self.min_experiences:
            errors.append(
                f"At least {self.min_experiences} work experience(s) required"
            )
        if len(extracted_data.skills) < self.min_skills:
            errors.append(f"At least {self.min_skills} skill(s) required")

        if errors:
            print(f"  ❌ Validation failed: {len(errors)} error(s)")
            invalid_state: ExtractorState = {**state, "validation_errors": errors}
            return NodeResult(invalid_state, outcome="invalid")

        # Valid data
        print("  ✅ Validation passed")
        valid_state: ExtractorState = {**state, "validation_errors": []}
        return NodeResult(valid_state, outcome="valid")


@dataclass(frozen=True)
class FormatterNode(Node[ExtractorState]):
    """Formats extracted resume data for display."""

    @override
    async def exec(self, state: ExtractorState) -> NodeResult[ExtractorState]:
        """Format the extracted data into a readable string."""
        print("→ Formatting output...")
        extracted_data = state.get("extracted_data")

        if not extracted_data:
            return NodeResult(state, outcome="no_data")

        # Build formatted output
        lines = [
            "=" * 60,
            f"Name: {extracted_data.name}",
            f"Email: {extracted_data.email}",
        ]

        if extracted_data.phone:
            lines.append(f"Phone: {extracted_data.phone}")

        if extracted_data.summary:
            lines.extend(["", "SUMMARY:", extracted_data.summary])

        if extracted_data.experiences:
            lines.extend(["", "WORK EXPERIENCE:"])
            for exp in extracted_data.experiences:
                lines.extend([
                    f"  • {exp.role} at {exp.company} ({exp.duration})",
                ])
                if exp.description:
                    lines.append(f"    {exp.description}")

        if extracted_data.education:
            lines.extend(["", "EDUCATION:"])
            lines.extend(
                f"  • {edu.degree} from {edu.institution} ({edu.year})"
                for edu in extracted_data.education
            )

        if extracted_data.skills:
            lines.extend(["", f"SKILLS: {', '.join(extracted_data.skills)}"])

        lines.append("=" * 60)
        formatted = "\n".join(lines)

        print("  ✅ Formatting complete")
        new_state: ExtractorState = {**state, "formatted_output": formatted}
        return NodeResult(new_state, outcome="formatted")


@dataclass(frozen=True)
class CompleteNode(Node[ExtractorState]):
    """Final node that handles all termination paths."""

    @override
    async def exec(self, state: ExtractorState) -> NodeResult[ExtractorState]:
        """Complete the flow - single termination point."""
        print("→ Flow complete")
        # This node simply passes through the state
        # All display logic is handled in main.py
        return NodeResult(state, outcome="done")
