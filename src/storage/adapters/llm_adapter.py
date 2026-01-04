import os
import json
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI
from anthropic import Anthropic
from src.config.environment import settings
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMAdapter:
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        self.provider = provider.lower()
        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = model or "gpt-4-turbo-preview"
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = model or "claude-3-opus-20240229"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logger.info(f"Initialized LLMAdapter with provider: {self.provider}, model: {self.model}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def complete(self, prompt: str, system_prompt: str = "You are a cognitive memory engine assistant.", **kwargs) -> str:
        """Get a completion from the LLM with retry logic."""
        logger.debug(f"Calling LLM ({self.provider}) with prompt: {prompt[:50]}...")
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    **kwargs
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=kwargs.get("max_tokens", 1024),
                    **{k: v for k, v in kwargs.items() if k != "max_tokens"}
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error calling {self.provider} API: {str(e)}")
            raise

    async def acomplete(self, prompt: str, system_prompt: str = "You are a cognitive memory engine assistant.", **kwargs) -> str:
        """Async completion (simulated for now, can be expanded with AsyncOpenAI/AsyncAnthropic)."""
        return self.complete(prompt, system_prompt, **kwargs)

    def structured_completion(self, prompt: str, system_prompt: str = "You are a cognitive memory engine assistant.", **kwargs) -> Any:
        """Get a JSON structured completion from the LLM."""
        if self.provider == "openai":
            # Use OpenAI JSON mode
            kwargs["response_format"] = {"type": "json_object"}
            if "json" not in prompt.lower() and "json" not in system_prompt.lower():
                system_prompt += " Return response in valid JSON format."
        else:
            # For Anthropic or others, emphasize JSON in the system prompt
            if "json" not in prompt.lower() and "json" not in system_prompt.lower():
                system_prompt += " Return ONLY a valid JSON object. No preamble."

        raw_response = self.complete(prompt, system_prompt, **kwargs)
        
        try:
            # Try parsing the raw response as JSON
            return json.loads(raw_response)
        except json.JSONDecodeError:
            # Fallback: Try to extract JSON from the text if it's wrapped in markers or preamble
            logger.warning(f"Failed to parse direct JSON from {self.provider} response. Attempting extraction.")
            json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw_response)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            logger.error(f"Could not extract valid JSON from response: {raw_response[:200]}...")
            raise ValueError("LLM failed to return valid structured JSON.")

    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text in a structured format."""
        system_prompt = (
            "You are an entity extraction expert. Extract all relevant entities from the text. "
            "For each entity, provide its 'name', its 'type' (e.g., Person, Organization, Location, Concept, Technology), "
            "and an 'importance' score between 0.0 and 1.0. "
            "Respond ONLY with a JSON object containing an 'entities' list."
        )
        prompt = f"Text to analyze: {text}"
        
        try:
            result = self.structured_completion(prompt, system_prompt)
            return result.get("entities", [])
        except Exception as e:
            logger.error(f"Error in extract_entities: {e}")
            return []

    async def derive_principles(self, text: str) -> List[Dict[str, Any]]:
        """Derive high-level principles or causal patterns from text."""
        system_prompt = (
            "You are a cognitive scientist. Analyze the text and derive high-level principles, "
            "lessons, or causal patterns. For each principle, provide 'content' (the rule/lesson) "
            "and a 'confidence' score between 0.0 and 1.0. "
            "Respond ONLY with a JSON object containing a 'principles' list."
        )
        prompt = f"Text to analyze: {text}"
        
        try:
            result = self.structured_completion(prompt, system_prompt)
            return result.get("principles", [])
        except Exception as e:
            logger.error(f"Error in derive_principles: {e}")
            return []
