# app.py
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import BadRequest
import re
import logging
import hashlib
import time

from config import config
from git_services import get_git_service
from analysis_engine import get_analysis_engine

logger = logging.getLogger(__name__)
app = Flask(__name__)

def validate_github_url(url: str):
    """
    Validates a GitHub PR URL and extracts owner, repo, and PR number.
    Returns a tuple (owner, repo, pr_number) or raises ValueError.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string.")
    
    pattern = r"https://(www\.)?github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)/pull/(\d+)"
    match = re.match(pattern, url.strip())
    
    if match:
        owner, repo, pr_number_str = match.group(2), match.group(3), match.group(4)
        return owner, repo, int(pr_number_str)
    
    raise ValueError("Invalid GitHub PR URL format. Expected: https://github.com/owner/repo/pull/123")

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Provides a simple health check endpoint."""
    return jsonify({'status': 'ok'})

@app.route('/analyze', methods=['POST'])
def analyze():
    """The main endpoint for analyzing a pull request."""
    request_id = hashlib.md5(f"{time.time()}{request.remote_addr}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] Received analysis request.")

    try:
        data = request.get_json()
        if not data or 'pull_request_url' not in data:
            raise BadRequest("Missing 'pull_request_url' in request body.")
        
        pr_url = data['pull_request_url']
        
        try:
            repo_owner, repo_name, pr_number = validate_github_url(pr_url)
            logger.info(f"[{request_id}] Validated URL for {repo_owner}/{repo_name}#{pr_number}")
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        git_service = get_git_service('github')
        git_service.set_repository(repo_owner, repo_name)
        
        diff_text = git_service.get_pull_request_diff(pr_number)
        
        if diff_text is None:
            return jsonify({'error': 'Failed to fetch diff. Check if the URL is correct and the repository is public.'}), 404

        if len(diff_text) > config.MAX_DIFF_SIZE:
            return jsonify({'error': f'Diff is too large ({len(diff_text)} bytes). Max size is {config.MAX_DIFF_SIZE} bytes.'}), 413

        analysis_engine = get_analysis_engine()
        analysis_result = analysis_engine.analyze_code_changes(diff_text)

        if analysis_result.startswith("Error:"):
            return jsonify({'error': analysis_result}), 500

        logger.info(f"[{request_id}] Analysis completed successfully.")
        return jsonify({
            'feedback': analysis_result,
            'metadata': {
                'repository': f"{repo_owner}/{repo_name}",
                'pr_number': pr_number
            }
        })

    except BadRequest as e:
        logger.warning(f"[{request_id}] Bad request: {e.description}")
        return jsonify({'error': e.description}), 400
    except Exception:
        logger.error(f"[{request_id}] An unexpected error occurred in /analyze endpoint.", exc_info=True)
        return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)