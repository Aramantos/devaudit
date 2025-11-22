"""
Vertex AI Analyzer for DevAudit - Intelligent Security Recommendations

This module provides AI-powered analysis of DevAudit scan results using
Google Vertex AI (Gemini). It's completely optional and privacy-respecting.

Privacy Notes:
- Only enabled if user explicitly configures it
- No telemetry or external logging
- Uses user's own GCP project (they control the data)
- Can be disabled anytime
"""

import logging
import warnings
from typing import Dict, Optional, List
import json

# Suppress Vertex AI deprecation warnings (cosmetic only, feature still works)
warnings.filterwarnings('ignore', category=UserWarning, module='vertexai.generative_models')

# Vertex AI imports (optional dependency)
try:
    import vertexai
    from vertexai.preview import generative_models
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False
    logging.info("Vertex AI SDK not available. AI recommendations disabled.")


class VertexConfig:
    """Configuration for Vertex AI integration."""

    # Default to Project Freya's config (can be overridden)
    PROJECT_ID = "artful-winter-473414-q1"
    LOCATION = "us-central1"
    MODEL = "gemini-2.0-flash"  # Fast, cost-effective

    @classmethod
    def from_env(cls):
        """Load config from environment variables if available."""
        import os
        return {
            "project_id": os.getenv("DEVAUDIT_VERTEX_PROJECT", cls.PROJECT_ID),
            "location": os.getenv("DEVAUDIT_VERTEX_LOCATION", cls.LOCATION),
            "model": os.getenv("DEVAUDIT_VERTEX_MODEL", cls.MODEL),
        }


class SecurityRecommendationAnalyzer:
    """Analyzes DevAudit scan results and provides intelligent recommendations."""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize analyzer with Vertex AI config.

        Args:
            config: Optional config dict with project_id, location, model

        Raises:
            RuntimeError: If Vertex AI SDK is not available
        """
        if not VERTEX_AVAILABLE:
            raise RuntimeError(
                "Vertex AI SDK not available. Install with: "
                "pip install 'devaudit[ai]' or pip install google-cloud-aiplatform"
            )

        self.config = config or VertexConfig.from_env()
        self.project_id = self.config["project_id"]
        self.location = self.config["location"]
        self.model_name = self.config["model"]

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        logging.info(f"Vertex AI initialized: {self.project_id} / {self.location}")

    def analyze(self, scan_results: Dict) -> Dict:
        """
        Analyze scan results and generate intelligent recommendations.

        Args:
            scan_results: Complete DevAudit scan results dictionary

        Returns:
            Dict with AI-generated insights and recommendations
        """
        try:
            logging.info("🤖 Generating AI recommendations with Vertex AI...")

            # Construct prompt
            prompt = self._construct_prompt(scan_results)

            # Call Gemini
            model = generative_models.GenerativeModel(self.model_name)
            response = model.generate_content(
                [prompt],
                generation_config=generative_models.GenerationConfig(
                    temperature=0.3,  # Slightly creative but focused
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,  # Longer responses for detailed advice
                ),
                stream=False,
            )

            # Parse response
            return self._parse_response(response.text, scan_results)

        except Exception as e:
            logging.error(f"Vertex AI analysis failed: {e}")
            return {
                "error": str(e),
                "message": "AI analysis unavailable",
                "fallback": True
            }

    def _construct_prompt(self, scan_results: Dict) -> str:
        """
        Construct a structured prompt for Gemini.

        Args:
            scan_results: Scan results to analyze

        Returns:
            Formatted prompt string
        """
        # Extract key information
        summary = scan_results.get("summary", {})
        results = scan_results.get("results", {})

        # Count critical issues
        critical_count = summary.get("risk_counts", {}).get("critical", 0)
        high_count = summary.get("risk_counts", {}).get("high", 0)
        vulnerabilities = summary.get("total_vulnerabilities", 0)

        # Build issue list
        issues = []
        for auditor_name, auditor_result in results.items():
            if isinstance(auditor_result, dict):
                risk_level = auditor_result.get("risk_level", "none")
                if risk_level in ["critical", "high"]:
                    recommendation = auditor_result.get("recommendation", "")
                    issues.append(f"- {auditor_name}: {risk_level.upper()} - {recommendation}")

        prompt = f"""You are a security advisor analyzing a DevAudit security scan report.

SCAN SUMMARY:
- Total Issues: {critical_count} critical, {high_count} high priority
- Vulnerabilities: {vulnerabilities} CVEs found
- Total Auditors: {summary.get('tools_detected', 0)} of {summary.get('total_tools', 0)} detected

KEY ISSUES FOUND:
{chr(10).join(issues) if issues else "- No critical issues detected"}

Your task is to provide:
1. **Priority Action** - What should the user fix FIRST and WHY (1-2 sentences)
2. **Top 3 Recommendations** - Specific, actionable steps prioritized by impact
3. **Security Score** - Rate overall security posture (0-100)
4. **Risk Summary** - One sentence explaining the biggest risk

Respond ONLY in this exact format:

Priority Action: [First thing to fix and why it matters most]

Top Recommendations:
1. [Specific action with clear benefit]
2. [Specific action with clear benefit]
3. [Specific action with clear benefit]

Security Score: [0-100]

Risk Summary: [One sentence about biggest current risk]

Keep responses concise, educational, and actionable. Focus on what matters most to the user's security."""

        return prompt

    def _parse_response(self, response_text: str, scan_results: Dict) -> Dict:
        """
        Parse Gemini's response into structured data.

        Args:
            response_text: Raw response from Gemini
            scan_results: Original scan results for context

        Returns:
            Structured recommendations dictionary
        """
        import re

        # Extract sections using regex
        priority_match = re.search(
            r"Priority Action:\s*(.+?)(?=\n\n|Top Recommendations:)",
            response_text,
            re.DOTALL | re.IGNORECASE
        )

        recommendations_match = re.search(
            r"Top Recommendations:\s*(.+?)(?=\n\n|Security Score:)",
            response_text,
            re.DOTALL | re.IGNORECASE
        )

        score_match = re.search(
            r"Security Score:\s*(\d+)",
            response_text,
            re.IGNORECASE
        )

        risk_match = re.search(
            r"Risk Summary:\s*(.+?)(?=\n\n|$)",
            response_text,
            re.DOTALL | re.IGNORECASE
        )

        # Parse priority action
        priority_action = priority_match.group(1).strip() if priority_match else "Review scan results"

        # Parse recommendations (extract numbered list)
        recommendations = []
        if recommendations_match:
            rec_text = recommendations_match.group(1).strip()
            # Extract lines starting with numbers
            rec_lines = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)', rec_text, re.DOTALL)
            recommendations = [r.strip() for r in rec_lines if r.strip()]

        # Parse security score
        security_score = int(score_match.group(1)) if score_match else 50

        # Parse risk summary
        risk_summary = risk_match.group(1).strip() if risk_match else "Security assessment in progress"

        # Determine severity color
        if security_score >= 80:
            severity = "low"
            color = "green"
        elif security_score >= 60:
            severity = "medium"
            color = "yellow"
        elif security_score >= 40:
            severity = "high"
            color = "orange"
        else:
            severity = "critical"
            color = "red"

        return {
            "priority_action": priority_action,
            "recommendations": recommendations,
            "security_score": security_score,
            "risk_summary": risk_summary,
            "severity": severity,
            "color": color,
            "raw_response": response_text,
            "model": self.model_name,
            "timestamp": scan_results.get("timestamp"),
        }


def is_vertex_available() -> bool:
    """Check if Vertex AI is available."""
    return VERTEX_AVAILABLE


def analyze_scan_results(scan_results: Dict, config: Optional[Dict] = None) -> Dict:
    """
    Convenience function to analyze scan results with Vertex AI.

    Args:
        scan_results: DevAudit scan results
        config: Optional Vertex AI config

    Returns:
        AI-generated recommendations or error dict
    """
    if not VERTEX_AVAILABLE:
        return {
            "error": "Vertex AI not available",
            "message": "Install google-cloud-aiplatform to enable AI recommendations",
            "fallback": True
        }

    try:
        analyzer = SecurityRecommendationAnalyzer(config)
        return analyzer.analyze(scan_results)
    except Exception as e:
        logging.error(f"Failed to analyze scan results: {e}")
        return {
            "error": str(e),
            "message": "AI analysis failed",
            "fallback": True
        }
