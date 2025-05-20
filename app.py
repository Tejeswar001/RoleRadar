from flask import Flask, render_template, request, jsonify
import github_api
from nlp_scoring import analyze_profile
import serper_api
import scholar_api
import random

opted_out = set()

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
        domain = request.form.get('domain', '').strip()
        keywords = request.form.get('keywords', '').strip()

    keywords_list = [k.strip() for k in keywords.split(",")] if keywords else []
    domain_keywords = {domain: keywords_list}

    scholar_experts = []
    linkedin_experts = []
    github_experts = []

    # --- Scholar veterans ---
    for sc in scholar_api.search_scholar_veterans(domain, keywords_list):
        profile_text = sc.get('profile_text') or (sc.get('title', '') + ' ' + sc.get('interests', ''))
        sources = {'scholar': profile_text}
        scores_data = analyze_profile(sources, domain_keywords)
        confidence_score = max([int(round(score)) for score in scores_data.values()], default=0)

        sc['confidence'] = confidence_score
        sc['source'] = "Scholar"
        scholar_experts.append(sc)

    # --- LinkedIn results via Serper API ---
    li_results = serper_api.search_linkedin_profiles(f"{domain} {' '.join(keywords_list)}")
    for item in li_results.get("organic", []):
        snippet = item.get("snippet", "")
        if not serper_api.has_10_years_experience(snippet):
            continue

        sources = {'linkedin': snippet}
        scores_data = analyze_profile(sources, domain_keywords)
        confidence_score = max([int(round(score)) for score in scores_data.values()], default=0)

        linkedin_experts.append({
            "name": item.get("title", "").split(" | ")[0],
            "contact": item.get("link"),
            "location": None,
            "confidence": confidence_score,
            "url": item.get("link"),
            "source": "LinkedIn"
        })

    # --- GitHub Users ---
    users = github_api.search_users_by_topic(domain, keywords_list)
    for user in users:
        username = user.get("login")
        if not username:
            continue

        result = github_api.estimate_experience(username)
        if result and result.get('is_veteran'):
            sources = {
                'github': " ".join([
                    result.get('bio', '') or '',
                    result.get('repos_description', '') or '',
                    result.get('topics', '') or '',
                    result.get('contributions', '') or ''
                ])
            }

            scores_data = analyze_profile(sources, domain_keywords)
            confidence_score = max(
                [int(round(score)) for score in scores_data.values()],
                default=0
            )

            github_experts.append({
                "name": result.get('username'),
                "bio": result.get('bio', ''),
                "contact": result.get('email', None) or result.get('html_url', ''),
                "location": "----",
                "confidence": confidence_score,
                "url": result.get("html_url"),
                "source": "GitHub"
            })
        else:
            print(f"Skipped: {username} (Not enough experience or failed lookup)")

    # --- Merge in required order ---
    experts_list = scholar_experts + linkedin_experts + github_experts

    # --- Sort all experts descending by confidence score ---
    experts_list.sort(key=lambda x: x.get('confidence', 0), reverse=True)

    return render_template('results.html',
                           experts=experts_list,
                           domain=domain,
                           keywords=keywords)


@app.post("/opt-out/<profile_id>")
def opt_out(profile_id):
    opted_out.add(profile_id)
    return jsonify({"status": "ok"})

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
