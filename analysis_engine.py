import google.generativeai as genai
import config
import re
import hashlib
from datetime import datetime

class AnalysisEngine:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API key is not configured in the .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.analysis_history = []
    
    def preprocess_diff(self, diff_text):
        lines = diff_text.split('\n')
        processed_lines = []
        
        for line in lines:
            if line.startswith('+++') or line.startswith('---'):
                processed_lines.append(line)
            elif line.startswith('+'):
                processed_lines.append(f"ADDED: {line[1:]}")
            elif line.startswith('-'):
                processed_lines.append(f"REMOVED: {line[1:]}")
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def generate_structured_prompt(self, diff_text, review_extension=""):
        preprocessed_diff = self.preprocess_diff(diff_text)
        
        base_prompt = (
            "You are an experienced software architect conducting a thorough code review.\n"
            "Analyze the provided code changes systematically and provide actionable feedback.\n\n"
            "Review Framework:\n"
            "1. Critical Issues: Bugs, logic errors, runtime exceptions, memory leaks\n"
            "2. Security Analysis: Authentication flaws, injection risks, data exposure\n"
            "3. Code Quality: Design patterns, SOLID principles, DRY violations\n"
            "4. Performance: Algorithm efficiency, database queries, resource usage\n"
            "5. Maintainability: Code clarity, documentation, test coverage implications\n"
            "6. Best Practices: Industry standards, framework conventions, error handling\n\n"
            f"{review_extension}\n"
            "Structure your response as follows:\n"
            "- Executive Summary (2-3 sentences)\n"
            "- Critical Issues (if any)\n"
            "- Improvements Suggested\n"
            "- Positive Observations\n"
            "- Recommendation Score (1-10)\n\n"
            "Code Diff:\n"
            f"```diff\n{preprocessed_diff}\n```"
        )
        
        return base_prompt
    
    def analyze_code_changes(self, diff_text, review_extension=""):
        if not diff_text:
            return "Unable to analyze: diff text is empty."
        
        diff_hash = hashlib.md5(diff_text.encode()).hexdigest()[:8]
        
        prompt = self.generate_structured_prompt(diff_text, review_extension)
        
        try:
            print(f"Initiating analysis for diff {diff_hash}")
            response = self.model.generate_content(prompt)
            
            analysis_record = {
                'timestamp': datetime.now().isoformat(),
                'diff_hash': diff_hash,
                'diff_size': len(diff_text),
                'success': True
            }
            self.analysis_history.append(analysis_record)
            
            print(f"Analysis {diff_hash} completed successfully")
            return self.format_analysis_output(response.text)
            
        except Exception as e:
            error_message = f"Analysis failed: {str(e)}"
            print(error_message)
            
            analysis_record = {
                'timestamp': datetime.now().isoformat(),
                'diff_hash': diff_hash,
                'diff_size': len(diff_text),
                'success': False,
                'error': str(e)
            }
            self.analysis_history.append(analysis_record)
            
            return self.generate_fallback_analysis(diff_text)
    
    def format_analysis_output(self, raw_output):
        formatted_output = raw_output.replace("## ", "**").replace("### ", "**")
        
        score_pattern = r'Recommendation Score:\s*(\d+)'
        match = re.search(score_pattern, formatted_output)
        if match:
            score = int(match.group(1))
            emoji = "✅" if score >= 8 else "⚠️" if score >= 5 else "❌"
            formatted_output = re.sub(
                score_pattern,
                f'**Recommendation Score: {score}/10 {emoji}**',
                formatted_output
            )
        
        formatted_output = re.sub(r'\n\s*\n', '\n\n', formatted_output)
        
        return formatted_output
    
    def generate_fallback_analysis(self, diff_text):
        lines = diff_text.split('\n')
        added_lines = sum(1 for line in lines if line.startswith('+'))
        removed_lines = sum(1 for line in lines if line.startswith('-'))
        modified_files = len(re.findall(r'^diff --git', diff_text, re.MULTILINE))
        
        return (
            "**Automated Analysis Summary**\n\n"
            f"This pull request modifies {modified_files} file(s) with "
            f"{added_lines} additions and {removed_lines} deletions.\n\n"
            "**General Recommendations:**\n"
            "• Ensure all changes are properly tested\n"
            "• Verify no sensitive data is exposed\n"
            "• Check for proper error handling\n"
            "• Confirm changes align with coding standards\n"
            "• Review for potential performance impacts\n\n"
            "Note: Detailed AI analysis temporarily unavailable. "
            "Manual review recommended for critical changes."
        )
    
    def get_analysis_statistics(self):
        if not self.analysis_history:
            return None
        
        total = len(self.analysis_history)
        successful = sum(1 for a in self.analysis_history if a['success'])
        
        return {
            'total_analyses': total,
            'successful_analyses': successful,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'last_analysis': self.analysis_history[-1]['timestamp'] if self.analysis_history else None
        }

class AnalysisEnginePool:
    def __init__(self, api_key, pool_size=3):
        self.engines = [AnalysisEngine(api_key) for _ in range(pool_size)]
        self.current_index = 0
    
    def get_engine(self):
        engine = self.engines[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.engines)
        return engine
    
    def analyze_code_changes(self, diff_text, review_extension=""):
        engine = self.get_engine()
        return engine.analyze_code_changes(diff_text, review_extension)

_engine_pool = None

def get_analysis_engine():
    global _engine_pool
    if _engine_pool is None:
        _engine_pool = AnalysisEnginePool(api_key=config.GEMINI_API_KEY, pool_size=1)
    return _engine_pool