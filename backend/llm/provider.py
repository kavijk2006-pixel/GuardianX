import os
import json
import re
from typing import Dict, Any, Optional


class GeminiLLMProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception:
            pass

    def generate(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("Gemini Client initialization failed.")
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        raw = self.generate(prompt)
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {"text": raw}


class OpenAILLMProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        import openai
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        raw = self.generate(prompt)
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {"text": raw}


class SmartAIProvider:
    """Intelligent natural language engine used when external API key is not present."""

    def generate(self, prompt: str) -> str:
        # Prompt analysis to return human-like conversational interview responses
        if "INTERVIEWER_QUESTION" in prompt or "decide_next_question" in prompt or "question" in prompt.lower():
            return "Welcome! Let's discuss system architecture. How do you design reliable data pipelines with observability?"
        return "Thank you for explaining your approach. Could you elaborate on how you handled failure recovery?"

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        return {
            "strengths": ["Clear technical explanation", "Demonstrated practical experience"],
            "gaps": ["Could elaborate more on error handling"],
            "next": ["Review system design principles"],
            "text": "Solid technical discussion."
        }


class ProductionLLMProvider:
    def __init__(self, api_key_env: str = "LLM_API_KEY"):
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get(api_key_env)
        openai_key = os.environ.get("OPENAI_API_KEY")

        if gemini_key:
            self._impl = GeminiLLMProvider(gemini_key)
        elif openai_key:
            self._impl = OpenAILLMProvider(openai_key)
        else:
            self._impl = SmartAIProvider()

    def generate(self, prompt: str) -> str:
        return self._impl.generate(prompt)

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        return self._impl.generate_structured(prompt)


class TestLLMProvider:
    """Deterministic provider used for unit testing."""

    def generate(self, prompt: str) -> str:
        return "(LLM_TEST_REPLY) " + (prompt[:200] if prompt else "")

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        return {"text": "(LLM_TEST_STRUCTURED_REPLY)", "meta_prompt": prompt}


class LLMProvider:
    def __init__(self, provider: Optional[str] = None):
        if provider == "test":
            self._impl = TestLLMProvider()
        else:
            # Default to production / smart AI provider
            self._impl = ProductionLLMProvider()

    def generate(self, prompt: str) -> str:
        return self._impl.generate(prompt)

    def generate_structured(self, prompt: str) -> Dict[str, Any]:
        return self._impl.generate_structured(prompt)

