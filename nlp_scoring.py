import re
from collections import defaultdict, Counter
from math import log

def score_domains(text, domain_keywords):
    text_lower = text.lower()
    scores = defaultdict(int)
    word_count = len(re.findall(r'\b\w+\b', text_lower))
    
    # Base weight for keyword occurrences
    for domain, keywords in domain_keywords.items():
        domain_score = 0
        for kw in keywords:
            # Find all occurrences
            occurrences = len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', text_lower))
            
            # Weight by keyword length (longer keywords get more weight)
            keyword_weight = 1 + (len(kw) / 10)
            
            # Apply TF (Term Frequency) weighting - normalize by document length
            if word_count > 0:
                tf = occurrences / word_count
                domain_score += tf * keyword_weight * 100  # Scale up for readability
                
        scores[domain] = round(domain_score, 2)
    
    return scores

def normalize_scores(domain_score_list):
    # Combine all scores
    total_scores = Counter()
    for scores in domain_score_list:
        # Apply source weighting here if needed
        total_scores.update(scores)
    
    # Find max score for normalization
    max_score = max(total_scores.values()) if total_scores else 1
    
    # Apply logarithmic scaling for better differentiation
    normalized = {}
    for domain, score in total_scores.items():
        if score > 0:
            # Log transformation helps differentiate small differences
            normalized[domain] = round((score / max_score) * 0.5 + log(1 + score) / log(1 + max_score) * 0.5, 2)
        else:
            normalized[domain] = 0
    
    return normalized

def extract_experience(texts):
    experience_levels = {
        "entry": 0,
        "junior": 1,
        "mid": 2, 
        "senior": 3,
        "lead": 4,
        "principal": 5,
        "director": 6,
        "vp": 7,
        "c-level": 8
    }
    
    # First check for years of experience
    for text in texts:
        # Look for patterns like "10+ years", "10 yrs", etc.
        match = re.search(r'(\d+)\s*\+?\s*(years?|yrs?)', text.lower())
        if match:
            years = int(match.group(1))
            if years >= 15:
                return "Expert (15+ years)"
            elif years >= 10:
                return f"Senior (10+ years)"
            elif years >= 5:
                return f"Mid-level (5+ years)"
            else:
                return f"Junior ({years}+ years)"
    
    # Check for educational qualifications
    for text in texts:
        if "phd" in text.lower() or "doctorate" in text.lower():
            return "PhD Level"
        elif "masters" in text.lower() or "msc" in text.lower() or "m.sc" in text.lower():
            return "Masters Level"
    
    # Check titles across all sources
    highest_level = -1
    for text in texts:
        text_lower = text.lower()
        for level, rank in experience_levels.items():
            if level in text_lower:
                highest_level = max(highest_level, rank)
    
    if highest_level >= 0:
        for level, rank in experience_levels.items():
            if rank == highest_level:
                return level.capitalize() + " Level"
    
    return "Unknown"

def calculate_source_weight(source_name):
    """
    Assigns weights to different sources based on reliability
    """
    source_name = source_name.lower()
    if "resume" in source_name or "cv" in source_name:
        return 2.0
    elif "linkedin" in source_name:
        return 1.5
    elif "portfolio" in source_name or "project" in source_name:
        return 1.3
    else:
        return 1.0

def analyze_profile(sources, domain_keywords):
    # sources is a dict: {source_name: text}
    domain_score_list = []
    weighted_scores = defaultdict(float)
    source_scores = {}
    domain_appearance_count = Counter()
    
    # First pass - score each source
    for name, text in sources.items():
        source_weight = calculate_source_weight(name)
        scores = score_domains(text, domain_keywords)
        source_scores[name] = scores
        
        # Apply source weighting
        weighted_source_scores = {k: v * source_weight for k, v in scores.items()}
        domain_score_list.append(weighted_source_scores)
        
        # Track domains that appear across multiple sources
        for domain, count in scores.items():
            if count > 0:
                domain_appearance_count[domain] += 1
                weighted_scores[domain] += weighted_source_scores[domain]
    
    # Apply multi-source bonus (domains that appear in multiple sources get a boost)
    for domain, count in domain_appearance_count.items():
        if count >= 2:
            weighted_scores[domain] *= (1 + (count / 10))
    
    # Normalize the final scores
    max_score = max(weighted_scores.values()) if weighted_scores else 1
    normalized_scores = {k: round(v / max_score, 2) for k, v in weighted_scores.items()}
    
    # Get verified domains (appears in 2+ sources)
    verified_domains = [domain for domain, count in domain_appearance_count.items() if count >= 2]
    
    # Extract experience level
    experience = extract_experience(list(sources.values()))
    
    # Sort domains by score
    sorted_domains = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
    top_domains = [d for d, s in sorted_domains if s > 0.1]  # Threshold to filter noise
    
    # Per-source domain scores for detailed analysis
    source_domain_scores = {name: {k: round(v, 2) for k, v in scores.items() if v > 0} 
                           for name, scores in source_scores.items()}
    
    return {
        "domains": top_domains,
        "verified_domains": verified_domains,
        "domain_scores": normalized_scores,
        "experience": experience,
        "source_domain_scores": source_domain_scores
    }