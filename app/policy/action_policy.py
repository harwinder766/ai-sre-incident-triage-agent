from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RemediationDecision:
    def __init__(
        self,
        remediation: str,
        expected_impact: str,
        risks: list[str],
    ):
        self.remediation = remediation
        self.expected_impact = expected_impact
        self.risks = risks
        self.approval_status = ApprovalStatus.PENDING

    def approve(self) -> None:
        self.approval_status = ApprovalStatus.APPROVED

    def reject(self) -> None:
        self.approval_status = ApprovalStatus.REJECTED

    def is_approved(self) -> bool:
        return self.approval_status == ApprovalStatus.APPROVED