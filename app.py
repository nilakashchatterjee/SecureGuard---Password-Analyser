# Core dependencies
import hashlib
import requests
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Security constants
MAX_PASSWORD_LENGTH = 512
MIN_PASSWORD_LENGTH = 12

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable frontend-backend communication

# Add security headers to all responses
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com; style-src 'self'; img-src 'self'"
    return response

def validate_password_strength(password):
    """Check password meets security requirements"""
    requirements = {
        'length': len(password) >= MIN_PASSWORD_LENGTH,
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'number': bool(re.search(r'[0-9]', password)),
        'symbol': bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>\/?]', password))
    }
    all_met = all(requirements.values())
    return requirements, all_met

def calculate_realistic_strength(requirements_met, zxcvbn_score=None):
    """
    Calculate realistic password strength combining structural requirements and entropy.
    
    Rules for real-world security:
    - If all 5 requirements NOT met: max strength is 1 (Weak)
    - If all 5 requirements met but entropy is low: strength is 2 (Moderate)
    - If all 5 requirements met and entropy is high: use entropy score (3-4)
    
    Args:
        requirements_met (int): Number of requirements met (0-5)
        zxcvbn_score (int): Entropy score from zxcvbn (0-4), optional
    
    Returns:
        dict: Strength assessment with score and explanation
    """
    strength_levels = {
        0: {'label': 'Critically Weak', 'score': 0},
        1: {'label': 'Weak', 'score': 1},
        2: {'label': 'Moderate', 'score': 2},
        3: {'label': 'Strong', 'score': 3},
        4: {'label': 'Unbreakable', 'score': 4}
    }
    
    if requirements_met < 5:
        # Missing structural requirements = not truly secure
        return {
            'score': 1,
            'label': 'Weak',
            'reason': f'Missing {5 - requirements_met} security requirement(s)',
            'is_compliant': False
        }
    else:
        # All requirements met
        return {
            'score': 3 if zxcvbn_score is None else max(2, zxcvbn_score),
            'label': 'Strong' if zxcvbn_score is None or zxcvbn_score >= 3 else 'Moderate',
            'reason': 'Meets all security requirements',
            'is_compliant': True
        }

# Serve the main HTML interface
@app.route('/')
def index():
    return render_template('index.html')

# Check password against breach database
@app.route('/check-breach', methods=['POST'])
def check_breach():
    # Validate content type
    if not request.is_json:
        return jsonify({"error": "Invalid content type"}), 400
    
    data = request.get_json()
    password = data.get('password')
    
    # Input validation
    if not password or not isinstance(password, str):
        return jsonify({"error": "Invalid password input"}), 400
    
    # Limit password length
    if len(password) > MAX_PASSWORD_LENGTH:
        return jsonify({"error": "Password exceeds maximum length"}), 400
    
    password = password.strip()
    
    # Check password strength requirements
    strength_reqs, all_met = validate_password_strength(password)
    requirements_met_count = sum(strength_reqs.values())
    
    # Calculate realistic strength score
    strength_assessment = calculate_realistic_strength(requirements_met_count)
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1_password[:5]  # Send to API
    suffix = sha1_password[5:]  # Keep locally for verification

    # Query Have I Been Pwned API with prefix
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Security API Unreachable"}), 500

    # Verify suffix locally against API response
    hashes = (line.split(':') for line in response.text.splitlines())
    count = 0
    for h, c in hashes:
        if h == suffix:
            count = int(c)
            break

    return jsonify({
        "count": count,
        "strength_requirements": strength_reqs,
        "meets_all_requirements": all_met,
        "requirements_met_count": requirements_met_count,
        "strength_assessment": strength_assessment
    })

@app.route('/password-requirements', methods=['GET'])
def get_password_requirements():
    """Return password strength requirements"""
    return jsonify({
        "min_length": MIN_PASSWORD_LENGTH,
        "requirements": [
            "At least 12 characters",
            "Contains uppercase letters (A-Z)",
            "Contains lowercase letters (a-z)",
            "Contains numbers (0-9)",
            "Contains symbols (!@#$%^&*...)"
        ]
    })

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)