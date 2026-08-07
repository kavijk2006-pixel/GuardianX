import os
from typing import Dict, Any, Optional


class ProductionLLMProvider:
    def __init__(self, api_key_env: str = "LLM_API_KEY"):
        self.api_key = os.environ.get(api_key_env)

    def generate(self, prompt: str) -> str:
        # Production provider is a stub here — explicit failure if not configured
        if not self.api_key:
            raise RuntimeError("Production LLM provider not configured. Set LLM_API_KEY.")
        # Placeholder: in a real implementation, call the external LLM SDK
        raise NotImplementedError("Production LLM calls are not implemented in this stub.")

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        # Same as above but returns structured output
        if not self.api_key:
            raise RuntimeError("Production LLM provider not configured. Set LLM_API_KEY.")
        raise NotImplementedError("Production LLM structured generation is not implemented in this stub.")


class TestLLMProvider:
    """Deterministic provider used for testing — returns templated text based on prompt."""

    def generate(self, prompt: str) -> str:
        # Return a short echo-like reply useful for tests
        return "(LLM_TEST_REPLY) " + (prompt[:200] if prompt else "")

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        # Return a predictable structured response
        return {"text": "(LLM_TEST_STRUCTURED_REPLY)", "meta_prompt": prompt}


class LLMProvider:
    def __init__(self, provider: Optional[str] = None):
        # provider: 'production' or 'test' (default)
        if provider == "production":
            self._impl = ProductionLLMProvider()
        else:
            self._impl = TestLLMProvider()

    def generate(self, prompt: str) -> str:
        return self._impl.generate(prompt)

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        return self._impl.generate_structured(prompt)
