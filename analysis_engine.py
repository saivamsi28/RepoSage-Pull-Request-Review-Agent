# analysis_engine.py
import google.generativeai as genai
import hashlib
import logging
from config import config

logger = logging.getLogger(__name__)

class AnalysisEngine:
    """Handles interaction with the Gemini AI model for code analysis."""
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API key is not configured.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _generate_prompt(self, diff_text):
        """Creates a structured and effective prompt for the AI model."""
        return (
            "Act as a senior software engineer performing a code review. "
            "Analyze the following code changes from a pull request diff. "
            "Provide clear, actionable feedback. Focus on identifying potential bugs, security vulnerabilities, "
            "violations of best practices, and areas for improvement in readability and maintainability.\n\n"
            "Structure your review in markdown format with the following sections:\n"
            "### Executive Summary\n"
            "A brief, 2-3 sentence overview of the changes.\n\n"
            "### Critical Issues\n"
            "List any bugs, security risks, or major design flaws. If none, state 'None'.\n\n"
            "### Suggestions for Improvement\n"
            "List recommendations for code quality, performance, or maintainability.\n\n"
            "### Positive Feedback\n"
            "Mention what was done well.\n\n"
            "### Quality Score\n"
            "Provide a score from 1 to 100, where 100 is excellent.\n\n"
            "---\n\n"
            "**Code Diff to Analyze:**\n"
            f"```diff\n{diff_text}\n```"
        )

    def analyze_code_changes(self, diff_text):
        """Analyzes the provided diff text and returns formatted feedback."""
        if not diff_text:
            logger.warning("Analysis attempted on empty diff text.")
            return "Error: Diff text is empty. Cannot perform analysis."

        prompt = self._generate_prompt(diff_text)
        
        try:
            diff_hash = hashlib.md5(diff_text.encode()).hexdigest()[:8]
            logger.info(f"[{diff_hash}] Submitting diff for analysis...")
            
            response = self.model.generate_content(prompt)
            
            logger.info(f"[{diff_hash}] Analysis completed successfully.")
            return response.text
            
        except Exception as e:
            logger.error(f"AI model analysis failed: {e}", exc_info=True)
            return "Error: The AI analysis failed. This could be due to a network issue or a problem with the AI service. Please try again later."

_analysis_engine = None

def get_analysis_engine():
    """Provides a singleton instance of the AnalysisEngine."""
    global _analysis_engine
    if _analysis_engine is None:
        _analysis_engine = AnalysisEngine(api_key=config.GEMINI_API_KEY)
    return _analysis_engine