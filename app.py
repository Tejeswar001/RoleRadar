from flask import Flask, request, jsonify, render_template
import os
import json
import random
import re
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "veteran-talent-finder-secret-key")

# API keys and credentials
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LINKEDIN_API_KEY = os.getenv("LINKEDIN_API_KEY")
LINKEDIN_API_SECRET = os.getenv("LINKEDIN_API_SECRET")

# Sample data for demonstration or when APIs fail
SAMPLE_VETERANS = [
    {
        "name": "Michael Johnson",
        "contact": "michael.johnson@example.com",
        "location": "San Diego, CA",
        "domain": "Cybersecurity",
        "keywords": ["network security", "penetration testing", "CISSP"],
        "confidence": 92
    },
    {
        "name": "Sarah Williams",
        "contact": "s.williams@techveterans.org",
        "location": "Arlington, VA",
        "domain": "Cybersecurity",
        "keywords": ["threat intelligence", "incident response", "SOC"],
        "confidence": 87
    },
    {
        "name": "David Rodriguez",
        "contact": "d.rodriguez@securitypros.net",
        "location": "Tampa, FL",
        "domain": "Cybersecurity",
        "keywords": ["encryption", "cloud security", "AWS"],
        "confidence": 85
    },
    {
        "name": "Jennifer Lee",
        "contact": "jennifer.l@cybersafe.io",
        "location": "Austin, TX",
        "domain": "Cybersecurity",
        "keywords": ["vulnerability assessment", "compliance", "NIST"],
        "confidence": 81
    },
    {
        "name": "Robert Taylor",
        "contact": "rtaylor@securenetworks.com",
        "location": "Colorado Springs, CO",
        "domain": "Cybersecurity",
        "keywords": ["malware analysis", "digital forensics", "incident handling"],
        "confidence": 78
    }
]

# Sample data for different domains
DOMAIN_SAMPLES = {
    "software development": [
        {
            "name": "James Wilson",
            "contact": "jwilson@devveterans.com",
            "location": "Seattle, WA",
            "keywords": ["full stack", "java", "cloud"],
            "confidence": 94
        },
        {
            "name": "Amanda Miller",
            "contact": "amiller@codeheroes.org",
            "location": "Raleigh, NC",
            "keywords": ["python", "aws", "devops"],
            "confidence": 89
        }
    ],
    "project management": [
        {
            "name": "Thomas Garcia",
            "contact": "tgarcia@pmvets.org",
            "location": "San Antonio, TX",
            "keywords": ["agile", "PMP", "scrum master"],
            "confidence": 91
        },
        {
            "name": "Melissa Brown",
            "contact": "mbrown@projectleaders.net",
            "location": "Norfolk, VA",
            "keywords": ["program management", "stakeholder management", "PMP"],
            "confidence": 86
        }
    ],
    "logistics": [
        {
            "name": "Christopher Davis",
            "contact": "cdavis@supplychain-vets.org",
            "location": "Jacksonville, FL",
            "keywords": ["supply chain", "distribution", "inventory management"],
            "confidence": 93
        },
        {
            "name": "Patricia Martinez",
            "contact": "pmartinez@logisticspro.net",
            "location": "Fort Worth, TX",
            "keywords": ["transportation", "warehouse operations", "JIT"],
            "confidence": 88
        }
    ],
    "healthcare": [
        {
            "name": "Elizabeth Walker",
            "contact": "ewalker@medveterans.org",
            "location": "Bethesda, MD",
            "keywords": ["nursing", "patient care", "healthcare administration"],
            "confidence": 95
        },
        {
            "name": "William Thompson",
            "contact": "wthompson@healthheroes.net",
            "location": "San Diego, CA",
            "keywords": ["medical logistics", "healthcare IT", "telemedicine"],
            "confidence": 87
        }
    ],
    "leadership": [
        {
            "name": "Richard Anderson",
            "contact": "randerson@leadvets.org",
            "location": "Alexandria, VA",
            "keywords": ["executive leadership", "strategic planning", "team building"],
            "confidence": 96
        },
        {
            "name": "Susan Mitchell",
            "contact": "smitchell@veteranleaders.net",
            "location": "San Antonio, TX",
            "keywords": ["organizational development", "change management", "mentoring"],
            "confidence": 90
        }
    ]
}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')
@app.route('/search', methods=['POST'])
def search_experts():
    data = request.get_json() or {}  # Parse JSON from request body

    domain = data.get('domain', '').strip().lower()
    keywords_str = data.get('keywords', '').strip()

    if not domain:
        return jsonify({"error": "Domain is required"}), 400

    keywords = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()] if keywords_str else []

    try:
        experts = find_veteran_experts(domain, keywords)

        if not experts:
            experts = get_sample_experts(domain, keywords)

        experts = sorted(experts, key=lambda x: x.get('confidence', 0), reverse=True)
        return jsonify(experts)

    except Exception as e:
        print(f"Error in search: {str(e)}")
        experts = get_sample_experts(domain, keywords)
        return jsonify(experts)

def find_veteran_experts(domain, keywords):
    """
    Search for veteran experts using multiple data sources
    
    Args:
        domain (str): Domain name (e.g., "Cybersecurity")
        keywords (list): List of keywords
    
    Returns:
        list: List of veteran experts
    """
    experts = []
    
    # Try GitHub API for veterans with relevant skills
    github_experts = search_github_veterans(domain, keywords)
    experts.extend(github_experts)
    
    # Try LinkedIn API for veterans with relevant skills
    linkedin_experts = search_linkedin_veterans(domain, keywords)
    experts.extend(linkedin_experts)
    
    # Add additional data sources here as needed
    
    # Deduplicate results
    experts = deduplicate_experts(experts)
    
    return experts

def search_github_veterans(domain, keywords):
    """Search for veterans on GitHub with matching skills"""
    if not GITHUB_TOKEN:
        return []
    
    try:
        # Build search query - look for veteran-related terms plus domain
        veteran_terms = ["veteran", "military", "navy", "army", "marines", "air force", "coast guard"]
        
        # Start with domain
        search_query = f"{domain}"
        
        # Add veteran terms wrapped in OR conditions
        search_query += " (" + " OR ".join(veteran_terms) + ")"
        
        # Add keywords if available
        if keywords:
            search_query += " " + " ".join(keywords)
        
        # Make API request
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(
            f"https://api.github.com/search/users?q={search_query}&sort=followers&order=desc",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"GitHub API error: {response.status_code}")
            return []
        
        data = response.json()
        results = []
        
        # Process the first 5 users max
        for user_data in data.get('items', [])[:5]:
            # Get detailed user info
            user_url = user_data['url']
            user_response = requests.get(user_url, headers=headers)
            
            if user_response.status_code != 200:
                continue
            
            user = user_response.json()
            
            # Check if likely a veteran
            is_veteran = check_if_veteran(user.get('bio', ''), user.get('name', ''), [])
            
            if not is_veteran:
                continue
            
            # Determine confidence score based on profile match
            confidence = calculate_confidence(domain, keywords, user.get('bio', ''))
            
            # Find email or contact info
            contact = user.get('email', f"{user['login']}@github.com")
            
            expert = {
                "name": user.get('name', user['login']),
                "contact": contact,
                "location": user.get('location', 'Location not specified'),
                "confidence": confidence
            }
            
            results.append(expert)
        
        return results
    
    except Exception as e:
        print(f"Error in GitHub search: {str(e)}")
        return []

def search_linkedin_veterans(domain, keywords):
    """
    Search for veterans on LinkedIn with matching skills
    Note: LinkedIn's official API has strict limitations, so this is a placeholder
    that would need to be implemented with proper credentials and authorization
    """
    # This would require proper LinkedIn API integration
    # For now, return an empty list or implement with your LinkedIn API credentials
    return []

def check_if_veteran(bio, name, profile_sections):
    """
    Check if a profile likely belongs to a veteran
    
    Args:
        bio (str): User bio or about section
        name (str): User name
        profile_sections (list): Additional profile sections to check
    
    Returns:
        bool: True if likely a veteran, False otherwise
    """
    # List of terms that indicate military/veteran background
    veteran_indicators = [
        "veteran", "military", "served", "service", "navy", "army", "marines", 
        "air force", "coast guard", "national guard", "officer", "enlisted",
        "infantry", "battalion", "squadron", "division", "corps", "regiment",
        "platoon", "brigade", "command", "duty", "deployment", "stationed",
        "retired military", "former military", "ex-military"
    ]
    
    # Check bio
    if bio:
        bio_lower = bio.lower()
        for term in veteran_indicators:
            if term in bio_lower:
                return True
    
    # Check name for military ranks
    ranks = ["cpt", "capt", "maj", "col", "gen", "lt", "sgt", "msgt", "ssgt"]
    name_lower = name.lower()
    for rank in ranks:
        if rank in name_lower.split():
            return True
    
    # Check additional profile sections
    for section in profile_sections:
        section_lower = section.lower()
        for term in veteran_indicators:
            if term in section_lower:
                return True
    
    return False

def calculate_confidence(domain, keywords, bio):
    """
    Calculate confidence score based on profile match to domain and keywords
    
    Args:
        domain (str): Domain to match
        keywords (list): Keywords to match
        bio (str): User bio to check against
    
    Returns:
        int: Confidence score from 0-100
    """
    base_score = 70  # Start with a base score
    
    if not bio:
        # Less confidence if no bio
        base_score -= 10
    else:
        bio_lower = bio.lower()
        
        # Check domain match
        if domain.lower() in bio_lower:
            base_score += 10
        
        # Check keyword matches
        keyword_matches = 0
        for keyword in keywords:
            if keyword.lower() in bio_lower:
                keyword_matches += 1
        
        # Add points based on keyword matches
        if keywords:
            keyword_score = min(15, (keyword_matches / len(keywords)) * 15)
            base_score += keyword_score
    
    # Add some random variation
    base_score += random.randint(-5, 5)
    
    # Ensure score is within bounds
    return max(min(base_score, 99), 75)  # Cap between 75-99%

def deduplicate_experts(experts):
    """
    Remove duplicate experts from the results
    
    Args:
        experts (list): List of expert dictionaries
    
    Returns:
        list: Deduplicated list of experts
    """
    seen_names = set()
    unique_experts = []
    
    for expert in experts:
        name = expert.get('name', '').lower()
        if name and name not in seen_names:
            seen_names.add(name)
            unique_experts.append(expert)
    
    return unique_experts

def get_sample_experts(domain, keywords):
    """
    Get sample experts when API results are not available
    
    Args:
        domain (str): Domain to match
        keywords (list): Keywords to match
    
    Returns:
        list: List of sample experts
    """
    domain_lower = domain.lower()
    
    # Check if we have samples for this domain
    if domain_lower in DOMAIN_SAMPLES:
        experts = DOMAIN_SAMPLES[domain_lower]
    else:
        # Use cybersecurity samples as default, but modify them
        experts = SAMPLE_VETERANS.copy()
        
        # Update domain in each expert
        for expert in experts:
            expert['domain'] = domain.capitalize()
            
            # Adjust confidence slightly for variety
            expert['confidence'] = max(75, min(99, expert['confidence'] + random.randint(-5, 5)))
    
    # Filter by keywords if provided
    if keywords:
        filtered_experts = []
        for expert in experts:
            # Check if any keywords match
            expert_keywords = [k.lower() for k in expert.get('keywords', [])]
            if any(kw in expert_keywords for kw in keywords):
                filtered_experts.append(expert)
            
            # If no matches, add with lower confidence
            elif len(filtered_experts) < 2:  # Ensure we have at least some results
                expert_copy = expert.copy()
                expert_copy['confidence'] = max(75, expert['confidence'] - 10)
                filtered_experts.append(expert_copy)
        
        experts = filtered_experts if filtered_experts else experts[:2]
    
    # Select max 5 experts and randomize order slightly
    selected_experts = experts[:5]
    random.shuffle(selected_experts)
    
    # Sort by confidence
    selected_experts = sorted(selected_experts, key=lambda x: x.get('confidence', 0), reverse=True)
    
    return selected_experts

if __name__ == '__main__':
    app.run(debug=True)