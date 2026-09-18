from pydantic import BaseModel, Field


class IncidentAnalysis(BaseModel):
    root_cause: str = Field(
        description="The most likely root cause of the incident."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Model confidence in the root-cause hypothesis "
            "between 0 and 1."
        ),
    )

    reasoning: str = Field(
        description=(
            "Explain how the available evidence supports "
            "the root-cause hypothesis."
        )
    )

    supporting_evidence: list[str] = Field(
        description=(
            "Important evidence supporting the root-cause hypothesis."
        )
    )

    remediation: str = Field(
        description=(
            "Explain how the incident could be remediated. "
            "Describe the recommended solution in human-readable "
            "terms. Do not generate shell commands or execute actions."
        )
    )

    expected_impact: str = Field(
        description=(
            "Explain the expected effect of applying the remediation."
        )
    )

    risks: list[str] = Field(
        description=(
            "Potential risks or side effects of the recommended remediation."
        )
    )