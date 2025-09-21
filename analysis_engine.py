import google.generativeai as genai
import config

class AnalysisEngine:
    """
    Uses the Gemini API to analyze code changes and provide feedback.
    """
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API key is not configured in the .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash') # Using a fast and capable model

    def analyze_code_changes(self, diff_text):
        """
        Analyzes a diff text and generates structured feedback.
        """
        if not diff_text:
            return "Could not perform analysis because the diff text was empty."

        # This is the "prompt" that instructs the AI how to behave.
        prompt = (
            "As an expert senior software engineer, review the following pull request.\n"
            "Provide clear, constructive, and actionable feedback.\n"
            "Analyze the code for the following:\n"
            "1.  **Bugs or Logic Errors:** Identify any potential bugs, edge cases, or logical flaws.\n"
            "2.  **Best Practices:** Check for adherence to SOLID principles, DRY, and other best practices.\n"
            "3.  **Readability & Maintainability:** Suggest improvements for clarity, naming, and code structure.\n"
            "4.  **Security Vulnerabilities:** Look for any common security risks.\n\n"
            "Format your review in markdown. Start with a one-paragraph summary. Then, provide specific suggestions "
            "as a bulleted list. If there are no issues, state that the code looks good.\n\n"
            "Here is the diff to review:\n"
            f"```diff\n{diff_text}\n```"
        )

        try:
            print("Sending code diff to Gemini for analysis...")
            response = self.model.generate_content(prompt)
            print("Successfully received analysis from Gemini.")
            return response.text
        except Exception as e:
            print(f"An error occurred during AI analysis: {e}")
            return f"Error: Could not analyze the code. Details: {e}"

def get_analysis_engine():
    """Factory function to initialize and return the analysis engine."""
    return AnalysisEngine(api_key=config.GEMINI_API_KEY)