from flask import Flask, render_template, request, redirect, url_for, jsonify,request
from nlp_scoring import analyze_profile

app = Flask(__name__)

# Dummy data for results
dummy_experts = [
    {"name": "Dr. Alice Chen", "contact": "alice@cybersecpro.com", "location": "Boston", "confidence": 92},
    {"name": "Raj Kumar", "contact": "linkedin.com/in/rajkumar", "location": "Hyderabad", "confidence": 85},
    {"name": "Elena Costa", "contact": "github.com/elenac", "location": "Milan", "confidence": 78}
]

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
    
    return render_template('results.html', 
                          experts=dummy_experts, 
                          domain=domain, 
                          keywords=keywords)
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text')
    domain_keywords = data.get('domain_keywords')

    if not text or not domain_keywords:
        return jsonify({'error': 'Missing text or domain_keywords'}), 400

    result = analyze_profile(text, domain_keywords)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
