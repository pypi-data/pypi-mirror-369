"""Flow builder for structured output extraction."""

from models import ExtractorState
from nodes import CompleteNode, ExtractorNode, FormatterNode, ValidatorNode

from clearflow import Flow, Node


def create_extraction_flow() -> Node[ExtractorState]:
    """Create the resume extraction flow with explicit routing.

    Flow structure:
    1. Extract structured data from text
    2. Validate the extracted data (if extraction succeeded)
    3. Format for display (if validation passed)
    4. Complete (single termination point)

    Each step has clear outcomes that determine the next step.
    """
    # Initialize nodes
    extractor = ExtractorNode(name="extractor")
    validator = ValidatorNode(name="validator")
    formatter = FormatterNode(name="formatter")
    complete = CompleteNode(name="complete")

    # Build flow with explicit routing and single termination
    return (
        Flow[ExtractorState]("ResumeExtraction")
        # Start with extraction
        .start_with(extractor)
        # Route based on extraction outcome
        .route(extractor, "extracted", validator)  # Success: validate
        .route(extractor, "failed", complete)  # API error: complete
        .route(extractor, "no_input", complete)  # No input: complete
        # Route based on validation outcome
        .route(validator, "valid", formatter)  # Valid: format
        .route(validator, "invalid", complete)  # Invalid: complete
        # Route based on formatting outcome
        .route(formatter, "formatted", complete)  # Formatted: complete
        .route(formatter, "no_data", complete)  # No data: complete
        # Single termination point
        .route(complete, "done", None)
        # Build the flow
        .build()
    )
