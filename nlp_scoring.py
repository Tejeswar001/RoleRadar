import re
from collections import defaultdict, Counter

def score_domains(text, domain_keywords):
    text_lower = text.lower()
    scores = defaultdict(int)

    for domain, keywords in domain_keywords.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', text_lower):
                scores[domain] += 1

    return scores

def normalize_scores(domain_score_list):
    total_scores = Counter()
    for scores in domain_score_list:
        total_scores.update(scores)

    total = sum(total_scores.values()) or 1
    return {k: round(v / total, 2) for k, v in total_scores.items()}

def extract_experience(texts):
    for text in texts:
        match = re.search(r'(\d+)\s*\+?\s*(years|yrs)', text.lower())
        if match:
            return f"{match.group(1)}+ years"
        if "phd" in text.lower():
            return "PhD Level"
    # Check titles across all sources
    for text in texts:
        if any(term in text.lower() for term in ["senior", "lead", "principal"]):
            return "Senior Level"
    return "Unknown"

def analyze_profile(sources, domain_keywords):
    # sources is a dict: {source_name: text}
    domain_score_list = []
    domain_appearance_count = Counter()

    for name, text in sources.items():
        scores = score_domains(text, domain_keywords)
        domain_score_list.append(scores)
        for domain, count in scores.items():
            if count > 0:
                domain_appearance_count[domain] += 1

    normalized_scores = normalize_scores(domain_score_list)
    verified_domains = [domain for domain, count in domain_appearance_count.items() if count >= 2]  # Appears in 2+ sources

    experience = extract_experience(list(sources.values()))

    sorted_domains = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
    top_domains = [d for d, s in sorted_domains if s > 0]

    return {
        "domains": top_domains,
        "verified_domains": verified_domains,
        "domain_scores": normalized_scores,
        "experience": experience
    }
