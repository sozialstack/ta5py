"""Format spec publication governance (detect / integrate / approve)."""

from ta5py.governance.approve import approve_candidate, go_live, older_over_newer_warning
from ta5py.governance.detect import run_detection
from ta5py.governance.discover import parse_overview_html
from ta5py.governance.integrate import DuplicateCandidateError, integrate_candidate
from ta5py.governance.models import (
    ApprovalDecision,
    DetectionRun,
    IntegrationCandidate,
    LiveVersionBinding,
    OfficialPublication,
)
from ta5py.governance.status import gather_status

__all__ = [
    "ApprovalDecision",
    "DetectionRun",
    "DuplicateCandidateError",
    "IntegrationCandidate",
    "LiveVersionBinding",
    "OfficialPublication",
    "approve_candidate",
    "gather_status",
    "go_live",
    "integrate_candidate",
    "older_over_newer_warning",
    "parse_overview_html",
    "run_detection",
]
