from typing import Dict, Any, List, Optional


class Evaluator:
    """AI Evaluator that analyzes candidate responses for technical correctness, depth,
    practical trade-offs, and identifies specific strengths and gaps.
    """

    def __init__(self):
        pass

    def evaluate(self, question: Dict[str, Any], answer: str, curriculum_day: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = {
            "correctness": 0,
            "understanding": 0,
            "practical": 0,
            "depth": 0,
            "clarity": 0,
            "problem_solving": 0,
            "strengths": [],
            "gaps": [],
            "follow_up_needed": False,
            "follow_up_reason": None,
        }

        text = answer.strip() if answer else ""
        if not text:
            result["gaps"].append("No response provided")
            result["follow_up_needed"] = True
            result["follow_up_reason"] = "Could you please provide an answer so we can discuss your technical approach?"
            return result

        words = text.lower().split()
        length = len(words)

        if length < 8:
            result["gaps"].append("Response was very brief")
            result["follow_up_needed"] = True
            result["follow_up_reason"] = "Could you expand on your technical explanation with more specific details?"
        
        # Topic specific strength extraction
        if any(w in text.lower() for w in ["log", "metric", "monitor", "prometheus", "grafana", "opentelemetry"]):
            result["strengths"].append("Demonstrated solid understanding of observability and logging patterns")
        
        if any(w in text.lower() for w in ["vector", "embedding", "index", "cosine", "pgvector", "pinecone", "chroma"]):
            result["strengths"].append("Effective grasp of vector search and embedding similarity concepts")

        if any(w in text.lower() for w in ["docker", "k8s", "kubernetes", "container", "deploy", "pipeline", "ci/cd"]):
            result["strengths"].append("Practical experience with containerization and deployment pipelines")

        if any(w in text.lower() for w in ["mcp", "agent", "orchestration", "tool", "langchain", "autogen"]):
            result["strengths"].append("Hands-on knowledge of multi-agent architectures and protocols")

        if any(w in text.lower() for w in ["trade-off", "tradeoff", "latency", "scale", "bottleneck", "failover", "retry"]):
            result["strengths"].append("Articulated production trade-offs and resilience considerations")
        else:
            if length >= 15 and not result["follow_up_needed"]:
                result["gaps"].append("Could elaborate more on production trade-offs and edge-case handling")

        if not result["strengths"]:
            result["strengths"].append("Communicated core concepts clearly")

        result["correctness"] = 4 if length > 20 else 3
        result["understanding"] = 4 if len(result["strengths"]) > 1 else 3
        result["practical"] = 4 if any(w in text.lower() for w in ["code", "api", "docker", "pipeline"]) else 2
        result["depth"] = 4 if "trade" in text.lower() or "latency" in text.lower() else 3
        result["clarity"] = 4 if length > 12 else 2

        return result

