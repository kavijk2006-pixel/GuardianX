from pathlib import Path
import json
from typing import List, Dict, Any, Optional


class CurriculumService:
    def __init__(self, data_path: Optional[str] = None):
        self.repo_root = Path(__file__).resolve().parents[2]
        self.data_path = Path(data_path) if data_path else self.repo_root / "curriculum.json"
        self.curriculum = {}
        self.load_curriculum()

    def load_curriculum(self) -> Dict[str, Any]:
        if not self.data_path.exists():
            raise FileNotFoundError(f"curriculum.json not found at {self.data_path}")
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Basic validation
        if "days" not in data or not isinstance(data["days"], list):
            raise ValueError("Invalid curriculum.json structure: 'days' list required")
        self.curriculum = data
        # Build day index for fast lookup
        self._days_by_number = {d["day"]: d for d in data.get("days", [])}
        self._modules_by_n = {m["n"]: m for m in data.get("modules", [])}
        return self.curriculum

    def get_day(self, day_number: int) -> Optional[Dict[str, Any]]:
        return self._days_by_number.get(day_number)

    def get_days(self, day_numbers: List[int]) -> List[Dict[str, Any]]:
        return [self._days_by_number[d] for d in day_numbers if d in self._days_by_number]

    def get_module(self, module_number: int) -> Optional[Dict[str, Any]]:
        return self._modules_by_n.get(module_number)

    def get_curriculum_context(self, day_numbers: List[int]) -> List[Dict[str, Any]]:
        return self.get_days(day_numbers)

    def get_relevant_topics(self, candidate_context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Determine relevant curriculum topics for a candidate based on completed, skipped, and repeated missions.
        Returns a dict with keys: completed, skipped, repeated, other
        Each value is a list of day objects from curriculum.json
        """
        completed = candidate_context.get("completed_missions", [])
        skipped = candidate_context.get("skipped_missions", [])
        repeated = candidate_context.get("repeated_attempts", [])

        def day_from_mission(m):
            day_num = m.get("day")
            return self.get_day(day_num)

        completed_days = [day_from_mission(m) for m in completed if day_from_mission(m)]
        skipped_days = [day_from_mission(m) for m in skipped if day_from_mission(m)]
        repeated_days = [day_from_mission(m) for m in repeated if day_from_mission(m)]

        # Other useful days: choose a few days near the completed ones or core AI days
        other = []
        # Simple heuristic: include day 7 (Embeddings), 10 (Retrieval), 16 (Chatbot Backend), 21 (Agents) if present
        for d in [7, 10, 16, 21]:
            day_obj = self.get_day(d)
            if day_obj and day_obj not in completed_days and day_obj not in skipped_days and day_obj not in repeated_days:
                other.append(day_obj)

        return {
            "completed": completed_days,
            "skipped": skipped_days,
            "repeated": repeated_days,
            "other": other,
        }
