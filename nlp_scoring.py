import re
import json
from collections import defaultdict
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def score_domains_keywords(text, domain_keywords):
    text_lower = text.lower()
    scores = defaultdict(float)
    word_count = len(re.findall(r'\b\w+\b', text_lower))
    if word_count == 0:
        return {domain: 0.0 for domain in domain_keywords}
    
    for domain, keywords in domain_keywords.items():
        score = 0.0
        for kw in keywords:
            occurrences = len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', text_lower))
            tf = occurrences / word_count
            score += tf * (1 + len(kw) / 10)
        scores[domain] = score * 100  # scale up to ~100 for easier combination
    return scores

def parse_gemini_response(raw_text):
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].endswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}

def gemini_api_score(text, domain_keywords):
    prompt = f"""
You are an expert evaluator.

Evaluate the text below and rate how well it aligns (0 to 1) with the following domains:
{', '.join(domain_keywords.keys())}

Be strict and score based on actual capability or experience shown.

Text:
\"\"\"
{text}
\"\"\"

Return a JSON object with domain names as keys and scores (0-1) as values, like:
{{"domain1": 0.85, "domain2": 0.3, ...}}
Make sure to return a valid JSON object.
"""
    try:
        response = model.generate_content(prompt)
        gemini_scores = parse_gemini_response(response.text)
        # Scale to 0-100, ignore unknown domains
        return {d: float(gemini_scores.get(d, 0)) * 100 for d in domain_keywords}
    except Exception:
        return {d: 0 for d in domain_keywords}

def analyze_profile(texts_dict, domain_keywords):
    if not texts_dict:
        return {}
    
    combined_scores = defaultdict(list)

    for source_name, text in texts_dict.items():
        keyword_scores = score_domains_keywords(text, domain_keywords)
        gemini_scores = gemini_api_score(text, domain_keywords)

        for domain in domain_keywords:
            default_score = 100  # baseline/default contribution
            combined = (
                keyword_scores.get(domain, 0) * 0.30 +
                gemini_scores.get(domain, 0) * 0.50 +
                default_score * 0.40
            )
            combined = 100 if combined > 100 else combined
            combined_scores[domain].append(combined)
    
    avg_scores = {}
    for domain, scores in combined_scores.items():
        avg_scores[domain] = round(sum(scores) / len(scores), 2) if scores else 0.0

    return avg_scores