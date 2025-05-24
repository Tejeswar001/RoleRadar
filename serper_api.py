from config import SERPER_API_KEY
import requests
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

SERPER_HEADERS = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json"
}

def generate_query_variants(domain):
    base = f"site:linkedin.com/in/ {domain}"
    return [
        base,
        f"{domain} expert site:linkedin.com/in/",
        f"senior {domain} engineer site:linkedin.com/in/",
        f"lead {domain} specialist site:linkedin.com/in/",
        f"{domain} professional 10 years site:linkedin.com/in/"
    ]

def fetch_variant(query):
    payload = {"q": query}
    response = requests.post("https://google.serper.dev/search", headers=SERPER_HEADERS, json=payload)
    if response.ok:
        return response.json().get("organic", [])
    return []

def search_linkedin_profiles_concurrent(domain):
    query_variants = generate_query_variants(domain)
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_variant, query_variants))
    return [item for sublist in results for item in sublist]

def has_10_years_experience(snippet: str) -> bool:
    if not snippet:
        return False
    snippet = snippet.lower()
    if re.search(r"\b(over\s*)?(1[0-9]|[2-9][0-9])\+?\s*(years?|yrs?)\b", snippet):
        return True
    year_matches = re.findall(r"\b(19|20)\d{2}\b", snippet)
    for year_str in year_matches:
        year = int(year_str)
        if datetime.now().year - year >= 10:
            return True
    return False

if __name__ == "__main__":
    domain_input = input("Enter domain (e.g., AI, Cybersecurity, ML): ").strip()
    results = search_linkedin_profiles_concurrent(domain_input)
    for item in results:
        if has_10_years_experience(item.get("snippet", "")):
            print("🔍 Veteran Found:")
            print(item["title"])
            print(item["link"])
            print(item.get("snippet"))
            print("-----")
