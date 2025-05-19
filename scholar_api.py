"""
scholar_api.py  ·  Role Radar helper
------------------------------------
Search Google Scholar author pages and detect veterans
(≥10 years experience) based on publication dates in public snippets.
"""
from __future__ import annotations
import os, re, requests, datetime as dt
from typing import List, Dict
from config import SERPER_API_KEY
import bs4

SERPER_KEY = SERPER_API_KEY
if not SERPER_KEY:
    raise RuntimeError("SERPER_API_KEY missing — add to .env or config.py")

HEADERS = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
SERPER_URL = "https://google.serper.dev/search"


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _serper_search(q: str, num: int = 10) -> list[dict]:
    """Call Serper /search and return organic results list."""
    payload = {"q": q, "num": num}
    r = requests.post(SERPER_URL, headers=HEADERS, json=payload, timeout=15)
    r.raise_for_status()
    return r.json().get("organic", [])


def _is_veteran(snippet: str) -> bool:
    """True if snippet suggests ≥10 yrs experience."""
    if not snippet:
        return False

    s = snippet.lower()

    # Explicit “12 years”, “15 yrs” pattern
    if re.search(r'\b(1[0-9]|[2-9][0-9])\s*(years?|yrs?)\b', s):
        return True

    # Look for earliest year and diff
    years = [int(y) for y in re.findall(r'(19|20)\d{2}', s)]
    if years and dt.datetime.now().year - min(years) >= 10:
        return True

    return False

def homepage_from_scholar(profile_url):
    html = requests.get(profile_url, timeout=10,
                        headers={"User-Agent":"Mozilla/5.0"}).text
    soup = bs4.BeautifulSoup(html, "html.parser")

    # anchor that literally says “Homepage”
    link = soup.find("a", string=re.compile(r'homepage', re.I))
    if link and link.get("href"):
        return requests.compat.urljoin(profile_url, link["href"])
    return None


# -------------------------------------------------
# Public function
# -------------------------------------------------
def search_scholar_veterans(domain: str, keywords: str = "",
                            max_results: int = 15) -> List[Dict]:
    """
    Return list of veteran author profiles with structure:
    {name, contact, location, confidence, scholar_url, source, snippet}
    """
    query = f'site:scholar.google.com/citations "{domain}" {keywords}'.strip()
    items = _serper_search(query, num=max_results)

    veterans = []
    for item in items:
        if not _is_veteran(item.get("snippet", "")):
            continue

        profile_url = item["link"]           # from Serper search hit
        home = homepage_from_scholar(profile_url)

        veterans.append({
            "name":        item["title"].split(" - ")[0],
            "contact":     home or None,          # Scholar has no email; use profile URL
            "location":    "—",                   # Not exposed publicly
            "confidence":  70,                    # Base; tune later
            "url": item["link"],
            "source":      "Google Scholar",
            "snippet":     item.get("snippet")
        })
    return veterans
