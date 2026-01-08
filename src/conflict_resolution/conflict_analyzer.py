from typing import Dict, Any, Optional
from loguru import logger
from src.models.nodes import Severity

class ConflictAnalyzer:
    """
    Analyzes verified contradictions to determine severity and resolution strategies.
    """
    
    def analyze(self, verification_result: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Refines the LLM verification result and adds additional context-based analysis.
        """
        is_contradiction = verification_result.get("is_contradiction", False)
        if not is_contradiction:
            return verification_result

        severity_str = verification_result.get("severity", "medium").lower()
        try:
            severity = Severity(severity_str)
        except ValueError:
            severity = Severity.MEDIUM

        reasoning = verification_result.get("reasoning", "No reasoning provided.")
        suggestion = verification_result.get("resolution_suggestion", "Manual review required.")

        # Additional logic could be added here to check recency, confidence scores, etc.
        # For now, we'll just structure the response.
        
        analysis = {
            "is_contradiction": True,
            "severity": severity,
            "reasoning": reasoning,
            "resolution_suggestion": suggestion,
            "requires_manual_intervention": severity in [Severity.HIGH, Severity.CRITICAL]
        }
        
        logger.info(f"Conflict analyzed: Severity={severity}, Manual={analysis['requires_manual_intervention']}")
        return analysis

