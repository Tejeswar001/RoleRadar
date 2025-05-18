import requests, time
from datetime import datetime
from config import GITHUB_TOKEN

HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def search_users_by_topic(topic, keywords=None, limit=10):
    """Initial user search looking at bios."""
    kw = " ".join(keywords) if keywords else ""
    query = f'{topic} {kw} in:bio'.strip()
    r = requests.get("https://api.github.com/search/users",
                     headers=HEADERS,
                     params={"q": query, "per_page": limit})
    if r.status_code != 200:
        print("User search error:", r.status_code, r.json().get("message"))
        return []
    return r.json()["items"]


def keyword_in_readmes(username, keywords):
    """Returns True if *all* keywords appear in any README of user’s repos."""
    if not keywords:
        return True   # nothing to check
    # Build query: keyword1+keyword2+...+in:file+filename:README.md+user:username
    kw_query = "+".join(keywords)
    code_q = f"{kw_query}+in:file+filename:README.md+user:{username}"
    r = requests.get("https://api.github.com/search/code",
                     headers=HEADERS,
                     params={"q": code_q, "per_page": 1})
    if r.status_code != 200:
        print("Code search error:", username, r.status_code)
        return False
    return r.json()["total_count"] > 0


def find_relevant_users(topic, keywords=None, limit=10):
    """Combine bio search + README check."""
    users = search_users_by_topic(topic, keywords, limit=limit*2)  # fetch extra to filter
    qualified = []
    for u in users:
        uname = u["login"]
        if keyword_in_readmes(uname, keywords or []):
            qualified.append(uname)
            if len(qualified) >= limit:
                break
        time.sleep(0.2)   # be gentle to the API
    return qualified

def get_user_data(username):
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching user data: {response.json()}")
        return None
    data = response.json()
    return {
        "login": data.get("login"),
        "name": data.get("name"),
        "email": data.get("email"),
        "blog": data.get("blog"),
        "bio": data.get("bio"),
        "html_url": data.get("html_url"),
        "created_at": data.get("created_at")
    }

def get_user_repos(username):
    url = f'https://api.github.com/users/{username}/repos?per_page=100&type=owner&sort=created'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching repos: {response.json()}")
        return []
    return response.json()

def get_earliest_commit_date(repo_owner, repo_name):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits?per_page=1&order=asc'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return None
    data = response.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]['commit']['author']['date']
    return None

def estimate_experience(username):
    user_data = get_user_data(username)
    if not user_data:
        return None

    created_at = user_data.get('created_at')
    created_year = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").year
    current_year = datetime.now().year
    account_age = current_year - created_year
    email = user_data.get('email')

    repos = get_user_repos(username)
    earliest_repo_year = None
    for repo in repos:
        repo_created_at = repo.get('created_at')
        if repo_created_at:
            year = datetime.strptime(repo_created_at, "%Y-%m-%dT%H:%M:%SZ").year
            if earliest_repo_year is None or year < earliest_repo_year:
                earliest_repo_year = year

    experience_years = max(account_age, current_year - earliest_repo_year) if earliest_repo_year else account_age

    return {
        "username": username,
        "created_at": created_at,
        "earliest_repo_year": earliest_repo_year,
        "estimated_experience_years": experience_years,
        "is_veteran": experience_years >= 10,
        "html_url": user_data.get('html_url'),
        "email": email
    }
 
if __name__ == "__main__":
    users = find_relevant_users("machine learning", ["ai", "data"])
    for user in users:
        username = user["login"]
        result = estimate_experience(username)
        if result:
          if result['is_veteran']:
            print("----- GitHub Experience Report -----")
            print(f"Username       : {result['username']}")
            print(f"Account Created: {result['created_at']}")
            print(f"Earliest Repo  : {result['earliest_repo_year']}")
            print(f"Experience     : {result['estimated_experience_years']} years")
            print(f"Contact Information : {result['email']}")
            print(result)
        else:
            print("Failed to retrieve user info.")
