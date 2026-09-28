from pydantic import BaseModel, Field

class RemediationPlan(BaseModel):
    description: str
    action: str
    parameters: dict[str, object] = Field(default_factory=dict)
    expected_impact: str
    risks: list[str] = Field(default_factory=list)


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

    remediation: RemediationPlan = Field(
        description=(
            "Recommended remediation plan to address the root cause."
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

