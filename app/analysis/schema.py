from pydantic import BaseModel, Field


class IncidentAnalysis(BaseModel):
    """
    Structured output produced by the LLM
    after analyzing incident evidence.
    """

    root_cause: str = Field(
        description=(
            "The most likely root cause of the incident."
        )
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Confidence in the root-cause hypothesis "
            "between 0 and 1."
        ),
    )

    reasoning: str = Field(
        description=(
            "Reasoning explaining how the evidence "
            "supports the root-cause hypothesis."
        )
    )

    supporting_evidence: list[str] = Field(
        description=(
            "Important pieces of evidence supporting "
            "the root-cause hypothesis."
        )
    )

    