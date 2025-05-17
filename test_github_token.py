import os
from dotenv import load_dotenv
import requests

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("No GitHub token found in environment variables.")
    exit(1)

headers = {
    "Authorization": f"token {GITHUB_TOKEN}"
}

response = requests.get("https://api.github.com/user", headers=headers)

if response.status_code == 200:
    user_data = response.json()
    print(f"Success! Authenticated as: {user_data['login']}")
else:
    print(f"Failed to authenticate. Status code: {response.status_code}")
    print(f"Response: {response.text}")
