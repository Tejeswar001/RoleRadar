import requests
from datetime import datetime

HEADERS = {"Accept": "application/json"}

def fetch_orcid_ids(domain, keywords=None, max_results=10):
    query = f'"{domain}"'
    if keywords:
        kw_str = " OR ".join(f'"{kw}"' for kw in keywords)
        query = f'({query}) AND ({kw_str})'
    
    url = f"https://pub.orcid.org/v3.0/expanded-search?q={query}&rows={max_results}"
    print(f"Querying ORCID with: {query}")
    response = requests.get(url, headers=HEADERS)
    
    if not response.ok:
        print("Failed to fetch ORCID IDs")
        return []

    data = response.json()
    return [entry["orcid-id"] for entry in data.get("expanded-result", [])]

def get_earliest_pub_year(orcid_id):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    r = requests.get(url, headers=HEADERS)
    if not r.ok:
        return None

    data = r.json()
    years = []

    for group in data.get("group", []):
        for summary in group.get("work-summary", []):
            pub_date = summary.get("publication-date")
            if pub_date and pub_date.get("year") and pub_date["year"].get("value"):
                year = pub_date["year"]["value"]
                if year.isdigit():
                    years.append(int(year))

    return min(years) if years else None

def get_publication_titles(orcid_id, max_titles=5):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    response = requests.get(url, headers=HEADERS)
    if not response.ok:
        return []

    data = response.json()
    titles = []
    for group in data.get("group", []):
        for summary in group.get("work-summary", []):
            title = summary.get("title", {}).get("title", {}).get("value")
            if title:
                titles.append(title)
            if len(titles) >= max_titles:
                return titles
    return titles

def get_orcid_profile(orcid_id):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}"
    response = requests.get(url, headers=HEADERS)
    if not response.ok:
        return {}

    data = response.json()
    profile = {}

    # Name
    try:
        name = data["person"]["name"]
        profile["name"] = f"{name['given-names']['value']} {name['family-name']['value']}"
    except:
        profile["name"] = "Unknown"

    # Email
    try:
        profile["email"] = data["person"]["emails"]["email"][0]["email"]
    except:
        profile["email"] = "Not public"

    # Affiliations
    try:
        affiliations = data["activities-summary"]["employments"]["employment-summary"]
        profile["affiliations"] = [a["organization"]["name"] for a in affiliations]
    except:
        profile["affiliations"] = []

    return profile

def get_veteran_profiles(domain, keywords=None, max_profiles=10):
    veterans = []
    ids = fetch_orcid_ids(domain, keywords, max_profiles)

    for orcid_id in ids:
        pub_year = get_earliest_pub_year(orcid_id)
        if pub_year and datetime.now().year - pub_year >= 10:
            base_url = f"https://orcid.org/{orcid_id}"
            profile = get_orcid_profile(orcid_id)
            pubs = get_publication_titles(orcid_id)

            #confidence = nlp_scoring.gemini_api_score_for_orcid(pubs,domain)

            veterans.append({
                "orcid_id": orcid_id,
                "profile_link": base_url,
                "name": profile.get("name", "Unknown"),
                "email": profile.get("email", "Not public"),
                "affiliations": profile.get("affiliations", []),
                "earliest_publication_year": pub_year,
                "publications": pubs,
                "confidence": 40,  # Ensure minimum confidence
                "source": "ORCID"
            })

    return veterans

if __name__ == "__main__":
    domain = "AI"  # Mandatory
    #keywords = ["machine learning", "deep learning"]  # Optional

    results = get_veteran_profiles(domain, max_profiles=10)
    
    for r in results:
        print("\n--- Profile ---")
        print(f"Name: {r['name']}")
        print(f"Profile: {r['profile_link']}")
        print(f"Email: {r['email']}")
        print(f"Affiliations: {', '.join(r['affiliations'])}")
        print(f"Earliest Publication: {r['earliest_publication_year']}")
        print(f"Top Publications: {r['publications']}")
        print(f"Confidence: {r['confindence']}")
        print(f"Source: {r['source']}")
        print("----------------")
