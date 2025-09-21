# git_services.py
import requests
from abc import ABC, abstractmethod
import logging
from config import config

logger = logging.getLogger(__name__)

class GitService(ABC):
    """Abstract base class for Git service interactions."""
    def __init__(self):
        self.owner = None
        self.repo_name = None
        self.token = config.GIT_SERVICE_TOKEN
        self.timeout = config.REQUEST_TIMEOUT

    def set_repository(self, owner, repo_name):
        self.owner = owner
        self.repo_name = repo_name

    @abstractmethod
    def get_pull_request_diff(self, pr_number):
        pass

    @abstractmethod
    def post_review_comment(self, pr_number, comment):
        pass

class GitHubService(GitService):
    """Interacts with the GitHub API."""
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.github.com"
        
    def get_pull_request_diff(self, pr_number):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/pulls/{pr_number}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.diff"
        }
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub Error: Failed to fetch PR diff for {self.owner}/{self.repo_name}#{pr_number}. Details: {e}")
            return None

    def post_review_comment(self, pr_number, comment):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {"body": comment}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Successfully posted review comment to GitHub PR #{pr_number}.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub Error: Failed to post comment to PR #{pr_number}. Details: {e}")
            return False

class GitServiceFactory:
    """Factory for creating Git service instances."""
    _services = {
        'github': GitHubService,
        # 'gitlab': GitLabService,
        # 'bitbucket': BitbucketService
    }

    @staticmethod
    def create_service(git_server: str):
        service_class = GitServiceFactory._services.get(git_server.lower())
        if not service_class:
            raise ValueError(f"Unsupported git server: {git_server}")
        logger.info(f"Creating git service for: {git_server.capitalize()}")
        return service_class()

def get_git_service(git_server='github'):
    return GitServiceFactory.create_service(git_server)