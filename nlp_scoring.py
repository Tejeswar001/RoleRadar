import re
from collections import defaultdict

def score_domains(text, domain_keywords):
    text_lower = text.lower()
    scores = defaultdict(int)

    for domain, keywords in domain_keywords.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', text_lower):
                scores[domain] += 1

    total = sum(scores.values()) or 1
    normalized = {k: round(v / total, 2) for k, v in scores.items()}
    return normalized

def extract_experience(text):
    match = re.search(r'(\d+)\s*\+?\s*(years|yrs)', text.lower())
    if match:
        return f"{match.group(1)}+ years"
    elif any(term in text.lower() for term in ["senior", "lead", "principal"]):
        return "Senior Level"
    elif "phd" in text.lower():
        return "PhD Level"
    else:
        return "Unknown"

def analyze_profile(text, domain_keywords):
    domain_scores = score_domains(text, domain_keywords)
    experience = extract_experience(text)

    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    top_domains = [d for d, s in sorted_domains if s > 0]

    return {
        "domains": top_domains,
        "domain_scores": domain_scores,
        "experience": experience
    }
