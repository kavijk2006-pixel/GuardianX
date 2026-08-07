import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from backend.models.schemas import Candidate, Mission


class CandidateService:
    def __init__(self, data_path: Optional[str] = None):
        self.repo_root = Path(__file__).resolve().parents[2]
        self.data_path = Path(data_path) if data_path else self.repo_root / "candidates.json"
        self._candidates = {}
        self.load_candidates()

    def load_candidates(self) -> Dict[str, Any]:
        if not self.data_path.exists():
            raise FileNotFoundError(f"candidates.json not found at {self.data_path}")
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "candidates" not in data or not isinstance(data["candidates"], list):
            raise ValueError("Invalid candidates.json structure: 'candidates' list required")
        self._candidates = {c["member"]["id"]: c for c in data["candidates"]}
        return self._candidates

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        return self._candidates.get(candidate_id)

    def validate_candidate_object(self, candidate_obj: Dict[str, Any]) -> Dict[str, Any]:
        # Accept full candidate object (member + missions + signals) or just member with id
        if not isinstance(candidate_obj, dict):
            raise ValueError("candidate must be an object")
        if "member" in candidate_obj and "id" in candidate_obj["member"]:
            cid = candidate_obj["member"]["id"]
            existing = self.get_candidate(cid)
            if existing:
                return existing
            # If full object provided but not in file, still accept but warn
            return candidate_obj
        # maybe candidate_obj is the id
        if "id" in candidate_obj:
            cid = candidate_obj["id"]
            existing = self.get_candidate(cid)
            if existing:
                return existing
        raise ValueError("Invalid candidate object: missing member.id")

    def build_candidate_context(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        # Use actual fields: member, missions, signals
        member = candidate.get("member", {})
        missions = candidate.get("missions", [])
        signals = candidate.get("signals", {})

        completed = [m for m in missions if m.get("passed")]
        skipped = [m for m in missions if m.get("skipped")]
        failed = [m for m in missions if m.get("passed") is False]
        repeated = [m for m in missions if isinstance(m.get("attempts"), int) and m.get("attempts") > 2]

        context = {
            "member": member,
            "missions": missions,
            "signals": signals,
            "completed_missions": completed,
            "skipped_missions": skipped,
            "failed_missions": failed,
            "repeated_attempts": repeated,
        }
        return context

    def get_completed_missions(self, candidate: Dict[str, Any]) -> List[Mission]:
        return [Mission(**m) for m in candidate.get("missions", []) if m.get("passed")]

    def get_skipped_missions(self, candidate: Dict[str, Any]) -> List[Mission]:
        return [Mission(**m) for m in candidate.get("missions", []) if m.get("skipped")]

    def get_repeated_attempts(self, candidate: Dict[str, Any]) -> List[Mission]:
        return [Mission(**m) for m in candidate.get("missions", []) if m.get("attempts") and m.get("attempts") > 2]
