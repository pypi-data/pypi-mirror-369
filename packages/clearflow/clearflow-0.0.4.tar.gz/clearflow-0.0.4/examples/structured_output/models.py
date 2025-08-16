"""Type definitions for structured output example."""

from typing import TypedDict

from pydantic import BaseModel, Field


def _empty_work_list() -> list["WorkExperience"]:
    """Factory function for empty work experience list."""
    return []


def _empty_education_list() -> list["Education"]:
    """Factory function for empty education list."""
    return []


class WorkExperience(BaseModel):
    """A single work experience entry."""

    company: str = Field(description="Company name")
    role: str = Field(description="Job title/role")
    duration: str = Field(description="Employment period (e.g., 'Jan 2020 - Dec 2022')")
    description: str = Field(
        default="", description="Brief description of responsibilities"
    )


class Education(BaseModel):
    """Education entry."""

    institution: str = Field(description="School/University name")
    degree: str = Field(description="Degree or certification")
    year: str = Field(description="Graduation year or period")


class ExtractedResume(BaseModel):
    """Structured resume data extracted from text."""

    name: str = Field(description="Full name")
    email: str = Field(description="Email address")
    phone: str = Field(default="", description="Phone number")
    summary: str = Field(default="", description="Professional summary")
    experiences: list[WorkExperience] = Field(
        default_factory=_empty_work_list, description="Work experience entries"
    )
    education: list[Education] = Field(
        default_factory=_empty_education_list, description="Education entries"
    )
    skills: list[str] = Field(default_factory=list, description="List of skills")


class ExtractorState(TypedDict, total=False):
    """State for the extraction flow."""

    input_text: str
    extracted_data: ExtractedResume | None
    validation_errors: list[str]
    formatted_output: str
