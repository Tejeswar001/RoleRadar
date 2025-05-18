from config import SERPER_API_KEY
import requests
import re
from datetime import datetime

SERPER_HEADERS = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json"
}

def search_linkedin_profiles(query):
    url = "https://google.serper.dev/search"
    payload = {
        "q": f"site:linkedin.com/in/ {query}"
    }
    response = requests.post(url, headers=SERPER_HEADERS, json=payload)
    return response.json()

def has_10_years_experience(snippet):
    if not snippet:
        return False
    
    # Match phrases like "10+ years", "over 12 years", "15 yrs"
    match = re.search(r"(1[0-9]|[2-9][0-9])\+?\s*(years?|yrs?)", snippet.lower())
    if match:
        return True

    # Match any year (e.g., "since 2012") and calculate difference
    year_matches = re.findall(r"(19|20)\d{2}", snippet)
    for year_str in year_matches:
        year = int(year_str)
        if datetime.now().year - year >= 10:
            return True

    return False

if __name__ == "__main__":
    results = search_linkedin_profiles("AI")
    for item in results.get("organic", []):
        if has_10_years_experience(item.get("snippet", "")):
            print("🔍 Veteran Found:")
            print(item["title"])
            print(item["link"])
            print(item.get("snippet"))
            print("-----")