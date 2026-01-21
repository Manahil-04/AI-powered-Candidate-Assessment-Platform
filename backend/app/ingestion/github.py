import requests
from app.core.config import settings

_github_cache = {}


def fetch_github_profile(username: str) -> dict:
    """
    Fetch public GitHub data for a user.
    This uses GitHub's official public API.
    """

    if username in _github_cache:
        return _github_cache[username]

    user_resp = requests.get(f"{settings.GITHUB_API_BASE}/users/{username}")
    repos_resp = requests.get(f"{settings.GITHUB_API_BASE}/users/{username}/repos")

    if user_resp.status_code != 200:
        return {"error": "GitHub user not found"}

    user_data = user_resp.json()
    repos_data = repos_resp.json()

    languages = set()
    for repo in repos_data:
        if repo.get("language"):
            languages.add(repo["language"])

    return {
        "username": user_data.get("login"),
        "public_repos": user_data.get("public_repos"),
        "followers": user_data.get("followers"),
        "top_languages": list(languages),
        "stars": sum(repo.get("stargazers_count", 0) for repo in repos_data),
    }

    _github_cache[username] = result
    return result