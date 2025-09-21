import requests
import config

class GitHubService:
    def __init__(self, token, owner, repo_name):
        self.token = token
        self.owner = owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        self.diff_headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.diff"
        }
        self.comment_headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_pull_request_diff(self, pr_number):
        url = f"{self.base_url}/pulls/{pr_number}"
        try:
            response = requests.get(url, headers=self.diff_headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR diff from GitHub: {e}")
            return None

    def post_review_comment(self, pr_number, comment):
        url = f"{self.base_url}/issues/{pr_number}/comments"
        payload = {"body": comment}
        try:
            response = requests.post(url, headers=self.comment_headers, json=payload)
            response.raise_for_status()
            print("Successfully posted review comment to GitHub.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error posting comment to GitHub: {e}")
            print(f"Response body: {response.text}")
            return False

def get_git_service():
    if not all([config.GITHUB_TOKEN, config.REPO_OWNER, config.REPO_NAME]):
        raise ValueError("GitHub configuration (TOKEN, OWNER, NAME) is missing in .env file.")
    
    return GitHubService(config.GITHUB_TOKEN, config.REPO_OWNER, config.REPO_NAME)