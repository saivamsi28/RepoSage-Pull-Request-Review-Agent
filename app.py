from flask import Flask, render_template, request, jsonify
import config
from git_services import get_git_service
from analysis_engine import get_analysis_engine
import traceback
import re

app = Flask(__name__)

def parse_github_url(url):
    """
    Parses a GitHub pull request URL and extracts owner, repo, and PR number.
    Returns a tuple (owner, repo, pr_number) or None if the URL is invalid.
    """
    pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.match(pattern, url)
    if match:
        return match.groups()
    return None

@app.route('/')
def index():
    # The context is now empty as we don't need to pre-fill the form
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        pr_url = request.json.get('pull_request_url')
        if not pr_url:
            return jsonify({'error': 'Pull Request URL is required.'}), 400

        parsed_data = parse_github_url(pr_url)
        if not parsed_data:
            return jsonify({'error': 'Invalid GitHub PR URL format. Expected format: https://github.com/owner/repo/pull/123'}), 400
        
        repo_owner, repo_name, pr_number = parsed_data
        
        git_service = get_git_service()
        git_service.owner = repo_owner
        git_service.repo = repo_name
        
        analysis_engine = get_analysis_engine()

        diff_text = git_service.get_pull_request_diff(pr_number)
        
        if not diff_text:
            return jsonify({'error': 'Failed to fetch pull request diff. Check if the URL is correct and the repository is public.'}), 400

        analysis_result = analysis_engine.analyze_code_changes(diff_text)
        
        if "Could not perform analysis" in analysis_result:
             return jsonify({'error': analysis_result}), 400

        return jsonify({'feedback': analysis_result})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)