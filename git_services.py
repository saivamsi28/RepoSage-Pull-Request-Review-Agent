import requests
import config
from abc import ABC, abstractmethod
import base64
import json

class GitService(ABC):
    def __init__(self):
        self.owner = None
        self.repo_name = None
        self.token = config.GITHUB_TOKEN
    
    def set_repository(self, owner, repo_name):
        self.owner = owner
        self.repo_name = repo_name
    
    @abstractmethod
    def get_pull_request_diff(self, pr_number):
        pass
    
    @abstractmethod
    def post_review_comment(self, pr_number, comment):
        pass
    
    @abstractmethod
    def get_pr_metadata(self, pr_number):
        pass

class GitHubService(GitService):
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
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR diff from GitHub: {e}")
            return None

    def post_review_comment(self, pr_number, comment):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {"body": comment}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            print("Successfully posted review comment to GitHub.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error posting comment to GitHub: {e}")
            return False
    
    def get_pr_metadata(self, pr_number):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/pulls/{pr_number}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'title': data.get('title'),
                'description': data.get('body'),
                'author': data.get('user', {}).get('login'),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'state': data.get('state')
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR metadata from GitHub: {e}")
            return None

class GitLabService(GitService):
    def __init__(self):
        super().__init__()
        self.base_url = "https://gitlab.com/api/v4"
        
    def get_pull_request_diff(self, mr_number):
        project_id = f"{self.owner}%2F{self.repo_name}"
        url = f"{self.base_url}/projects/{project_id}/merge_requests/{mr_number}/changes"
        headers = {
            "PRIVATE-TOKEN": self.token
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            diff_text = ""
            for change in data.get('changes', []):
                diff_text += f"diff --git a/{change['old_path']} b/{change['new_path']}\n"
                diff_text += change.get('diff', '')
                diff_text += "\n"
            
            return diff_text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching MR diff from GitLab: {e}")
            return None

    def post_review_comment(self, mr_number, comment):
        project_id = f"{self.owner}%2F{self.repo_name}"
        url = f"{self.base_url}/projects/{project_id}/merge_requests/{mr_number}/notes"
        headers = {
            "PRIVATE-TOKEN": self.token,
            "Content-Type": "application/json"
        }
        payload = {"body": comment}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            print("Successfully posted review comment to GitLab.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error posting comment to GitLab: {e}")
            return False
    
    def get_pr_metadata(self, mr_number):
        project_id = f"{self.owner}%2F{self.repo_name}"
        url = f"{self.base_url}/projects/{project_id}/merge_requests/{mr_number}"
        headers = {
            "PRIVATE-TOKEN": self.token
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'title': data.get('title'),
                'description': data.get('description'),
                'author': data.get('author', {}).get('username'),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'state': data.get('state')
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching MR metadata from GitLab: {e}")
            return None

class BitbucketService(GitService):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.bitbucket.org/2.0"
        
    def get_pull_request_diff(self, pr_number):
        url = f"{self.base_url}/repositories/{self.owner}/{self.repo_name}/pullrequests/{pr_number}/diff"
        
        auth_header = base64.b64encode(f"{self.owner}:{self.token}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR diff from Bitbucket: {e}")
            return None

    def post_review_comment(self, pr_number, comment):
        url = f"{self.base_url}/repositories/{self.owner}/{self.repo_name}/pullrequests/{pr_number}/comments"
        
        auth_header = base64.b64encode(f"{self.owner}:{self.token}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        payload = {"content": {"raw": comment}}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            print("Successfully posted review comment to Bitbucket.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error posting comment to Bitbucket: {e}")
            return False
    
    def get_pr_metadata(self, pr_number):
        url = f"{self.base_url}/repositories/{self.owner}/{self.repo_name}/pullrequests/{pr_number}"
        
        auth_header = base64.b64encode(f"{self.owner}:{self.token}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'title': data.get('title'),
                'description': data.get('description'),
                'author': data.get('author', {}).get('username'),
                'created_at': data.get('created_on'),
                'updated_at': data.get('updated_on'),
                'state': data.get('state')
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR metadata from Bitbucket: {e}")
            return None

class GitServiceFactory:
    @staticmethod
    def create_service(git_server):
        services = {
            'github': GitHubService,
            'gitlab': GitLabService,
            'bitbucket': BitbucketService
        }
        
        service_class = services.get(git_server.lower())
        if not service_class:
            raise ValueError(f"Unsupported git server: {git_server}")
        
        if not config.GITHUB_TOKEN:
            raise ValueError("Authentication token is missing in configuration")
        
        return service_class()

def get_git_service(git_server='github'):
    service = GitServiceFactory.create_service(git_server)
    
    if config.REPO_OWNER and config.REPO_NAME:
        service.set_repository(config.REPO_OWNER, config.REPO_NAME)
    
    return service