import requests

GITHUB_API_URL = "https://api.github.com/repos/"

class GitHubClient:
    @staticmethod
    def get_last_update(repo_url):
        repo_name = repo_url.replace("https://github.com/", "")
        response = requests.get(f"{GITHUB_API_URL}{repo_name}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("updated_at")
        return None
