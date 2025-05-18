from flask import Flask, render_template, request, jsonify
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
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    text = data.get('text')
    domain_keywords = data.get('domain_keywords')

    if not text or not isinstance(text, str):
        return jsonify({'error': 'Invalid or missing text'}), 400
        
    if not domain_keywords or not isinstance(domain_keywords, dict):
        return jsonify({'error': 'Invalid or missing domain_keywords'}), 400

    try:
        result = analyze_profile(text, domain_keywords)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)