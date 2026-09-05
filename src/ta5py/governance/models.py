from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

CandidateState = Literal[
    "detected",
    "integrating",
    "awaiting_approval",
    "live",
    "failed",
    "rejected",
]

DetectionStatus = Literal["ok", "failed", "partial"]
Decision = Literal["approve", "reject"]


@dataclass
class OfficialPublication:
    id: str
    bucket: str
    filename: str
    path: str
    version: int | str
    stand_date: str | None = None
    in_scope: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, in_scope: bool | None = None) -> OfficialPublication:
        scope = in_scope if in_scope is not None else bool(data.get("in_scope", True))
        return cls(
            id=str(data["id"]),
            bucket=str(data["bucket"]),
            filename=str(data["filename"]),
            path=str(data["path"]),
            version=data["version"],
            stand_date=data.get("stand_date"),
            in_scope=scope,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DetectionRun:
    id: str
    started_at: str
    finished_at: str
    status: DetectionStatus
    error_message: str | None = None
    found_publication_ids: list[str] = field(default_factory=list)
    new_or_changed_ids: list[str] = field(default_factory=list)
    out_of_scope_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DetectionRun:
        return cls(
            id=str(data["id"]),
            started_at=str(data["started_at"]),
            finished_at=str(data["finished_at"]),
            status=data["status"],
            error_message=data.get("error_message"),
            found_publication_ids=list(data.get("found_publication_ids") or []),
            new_or_changed_ids=list(data.get("new_or_changed_ids") or []),
            out_of_scope_ids=list(data.get("out_of_scope_ids") or []),
        )


@dataclass
class ApprovalDecision:
    decision: Decision
    actor: str
    decided_at: str
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApprovalDecision:
        return cls(
            decision=data["decision"],
            actor=str(data["actor"]),
            decided_at=str(data["decided_at"]),
            note=data.get("note"),
        )


@dataclass
class IntegrationCandidate:
    id: str
    package_label: str
    branch_name: str
    source_publication_ids: list[str]
    state: CandidateState
    created_at: str
    updated_at: str
    change_summary_path: str | None = None
    approval: ApprovalDecision | None = None
    error_message: str | None = None
    source_publications: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.approval is None:
            d["approval"] = None
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IntegrationCandidate:
        approval = data.get("approval")
        return cls(
            id=str(data["id"]),
            package_label=str(data["package_label"]),
            branch_name=str(data["branch_name"]),
            source_publication_ids=list(data["source_publication_ids"]),
            state=data["state"],
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
            change_summary_path=data.get("change_summary_path"),
            approval=ApprovalDecision.from_dict(approval) if approval else None,
            error_message=data.get("error_message"),
            source_publications=list(data.get("source_publications") or []),
        )


@dataclass
class LiveVersionBinding:
    package_label: str
    activated_at: str
    activated_by: str
    approval_ref: str
    previous_package_label: str | None = None
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LiveVersionBinding:
        return cls(
            package_label=str(data["package_label"]),
            activated_at=str(data["activated_at"]),
            activated_by=str(data["activated_by"]),
            approval_ref=str(data["approval_ref"]),
            previous_package_label=data.get("previous_package_label"),
            note=data.get("note"),
        )
