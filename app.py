from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import BadRequest
import config
from git_services import get_git_service
from analysis_engine import get_analysis_engine
import traceback
import re
import logging
from functools import wraps
import time
from datetime import datetime, timedelta
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
rate_limit_storage = {}

def rate_limit(max_requests=10, window_minutes=1):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
            now = datetime.now()
            window_start = now - timedelta(minutes=window_minutes)
            
            rate_limit_storage[client_ip] = [
                req_time for req_time in rate_limit_storage.get(client_ip, [])
                if req_time > window_start
            ]
            
            if len(rate_limit_storage.get(client_ip, [])) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
            
            rate_limit_storage.setdefault(client_ip, []).append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_github_url(url):
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    url = url.strip()
    patterns = [
        r"https://github\.com/([a-zA-Z0-9._-]+)/([a-zA-Z0-9._-]+)/pull/(\d+)/?$",
        r"https://www\.github\.com/([a-zA-Z0-9._-]+)/([a-zA-Z0-9._-]+)/pull/(\d+)/?$"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            owner, repo, pr_number = match.groups()
            
            if len(owner) > 39 or len(repo) > 100:
                raise ValueError("Repository owner or name is too long")
            
            pr_num = int(pr_number)
            if pr_num <= 0 or pr_num > 999999:
                raise ValueError("Invalid pull request number")
            
            return owner, repo, pr_num
    
    raise ValueError("Invalid GitHub PR URL format")

def sanitize_input(text):
    if not text:
        return text
    
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/analyze', methods=['POST'])
@rate_limit(max_requests=5, window_minutes=1)
def analyze():
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] Starting analysis")
    
    try:
        if not request.is_json:
            raise BadRequest("Content-Type must be application/json")
        
        data = request.get_json()
        pr_url = data.get('pull_request_url')
        
        if not pr_url:
            return jsonify({'error': 'Pull Request URL is required'}), 400

        pr_url = sanitize_input(pr_url)
        
        try:
            repo_owner, repo_name, pr_number = validate_github_url(pr_url)
            logger.info(f"[{request_id}] Analyzing {repo_owner}/{repo_name}#{pr_number}")
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        try:
            git_service = get_git_service()
            git_service.owner = repo_owner
            git_service.repo_name = repo_name
            analysis_engine = get_analysis_engine()
        except ValueError as e:
            return jsonify({'error': 'Service configuration error'}), 500

        diff_text = git_service.get_pull_request_diff(pr_number)
        
        if not diff_text:
            return jsonify({
                'error': 'Failed to fetch pull request diff. Verify URL and repository access.'
            }), 400

        if len(diff_text) > 50000:
            return jsonify({
                'error': 'Pull request diff is too large for analysis.'
            }), 400

        analysis_result = analysis_engine.analyze_code_changes(diff_text)
        
        if not analysis_result or "Could not perform analysis" in analysis_result:
            return jsonify({'error': 'Analysis failed. Please try again later.'}), 500

        logger.info(f"[{request_id}] Analysis completed")
        return jsonify({
            'feedback': analysis_result,
            'metadata': {
                'repository': f"{repo_owner}/{repo_name}",
                'pr_number': pr_number,
                'analyzed_at': datetime.now().isoformat(),
                'request_id': request_id
            }
        })

    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"[{request_id}] Error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)