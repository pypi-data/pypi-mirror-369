import os

import requests


def check_url_accessible(url: str) -> bool:
    try:
        response = requests.head(url, timeout=3)
        return response.ok  # True si status_code ∈ [200, 399]
    except requests.RequestException:
        return False

def check_gitlab_url(gitlab_url: str) -> bool:
    return check_url_accessible(gitlab_url)

def check_gitlab_token(gitlab_url: str, gitlab_token: str) -> bool:
    headers = {
        'Private-Token': gitlab_token
    }

    try:
        response = requests.get(gitlab_url + 'api/v4/user', headers=headers, timeout=3)
        return response.ok  # True si status_code ∈ [200, 399]
    except requests.RequestException:
        return False

def check_gitlab_group(gitlab_url: str, gitlab_token: str, gitlab_group: str) -> bool:
    headers = {
        'Private-Token': gitlab_token
    }

    try:
        response = requests.get(gitlab_url + f'api/v4/groups/{gitlab_group}', headers=headers, timeout=3)
        return response.ok  # True si status_code ∈ [200, 399]
    except requests.RequestException:
        return False

def check_gitlab_username(gitlab_url: str, gitlab_token: str, gitlab_username: str) -> bool:
    headers = {
        'Private-Token': gitlab_token
    }

    try:
        response = requests.get(gitlab_url + f'api/v4/users/{gitlab_username}', headers=headers, timeout=3)
        return response.ok  # True si status_code ∈ [200, 399]
    except requests.RequestException:
        return False

def check_github_repo(github_repo: str) -> bool:
    if not github_repo:
        return False

    parts = github_repo.split('/')
    if len(parts) != 2:
        return False

    owner, repo_name = parts
    if not owner or not repo_name:
        return False

    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    return check_url_accessible(url)

def check_config_variables(key: str, value: str) -> bool:
    if key == "GITHUB_REPO":
        return check_github_repo(value)
    elif key == "GITLAB_REPO":
        return True
    elif key == "GITLAB_URL":
        return check_gitlab_url(value)
    elif key == "GITLAB_TOKEN":
        return True
    elif key == "GITLAB_GROUP":
        return True
    elif key == "GITLAB_USERNAME":
        return True
    else:
        return False
