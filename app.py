# Core dependencies
import hashlib
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable frontend-backend communication

# Serve the main HTML interface
@app.route('/')
def index():
    return render_template('index.html')

# Check password against breach database
@app.route('/check-breach', methods=['POST'])
def check_breach():
    data = request.get_json()
    password = data.get('password')
    
    if not password:
        return jsonify({"error": "No password provided"}), 400

    # Generate SHA-1 hash and split for k-anonymity
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1_password[:5]  # Send to API
    suffix = sha1_password[5:]  # Keep locally for verification

    # Query Have I Been Pwned API with prefix
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return jsonify({"error": "Security API Unreachable"}), 500

    # Verify suffix locally against API response
    hashes = (line.split(':') for line in response.text.splitlines())
    count = 0
    for h, c in hashes:
        if h == suffix:
            count = int(c)
            break

    return jsonify({"count": count})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)