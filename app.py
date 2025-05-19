from flask import Flask, render_template, request, redirect, url_for, jsonify
import github_api
from nlp_scoring import analyze_profile
import serper_api
import scholar_api

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/finder')
def finder():
    return render_template('finder.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    domain = ""
    keywords = ""
    
    if request.method == 'POST':
        domain = request.form.get('domain', '')
        keywords = request.form.get('keywords', '')
    
    keywords_list = keywords.split(",") if keywords else []
    experts_list = []
    users = github_api.search_users_by_topic(domain, keywords_list)
    for user in users:
        username = user["login"]
        result = github_api.estimate_experience(username)
        if result:
          if result['is_veteran']:
            experts_list.append({
                "name":     result['username'],
                "contact": result['email'], # later change to github link if contact is not available
                "location": "----", # Placeholder for location
                "confidence": 90 ,             # dummy score for now
                "url": result["html_url"]
            })
        else:
            print("Failed to retrieve user info.")
    
    li_results = serper_api.search_linkedin_profiles(f"{domain} {' '.join(keywords_list)}")
    for item in li_results.get("organic", []):
        snippet = item.get("snippet", "")
        if not serper_api.has_10_years_experience(snippet):
            continue

        experts_list.append({
            "name":       item["title"].split(" | ")[0],  # crude split
            "contact":    item["link"],
            "location":   "—",
            "confidence": 75,  # lower until cross‑source verified
            "url": item["link"],
            "source":     "LinkedIn"
        })

    for sc in scholar_api.search_scholar_veterans(domain, keywords):
        experts_list.append(sc)

    return render_template('results.html', 
                          experts=experts_list, 
                          domain=domain, 
                          keywords=keywords)

@app.route('/analyze', methods=['POST'])
def analyze():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    sources = data.get('sources')
    domain_keywords = data.get('domain_keywords')

    if not sources or not isinstance(sources, dict):
        return jsonify({'error': 'Invalid or missing sources'}), 400
        
    if not domain_keywords or not isinstance(domain_keywords, dict):
        return jsonify({'error': 'Invalid or missing domain_keywords'}), 400

    try:
        result = analyze_profile(sources, domain_keywords)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)