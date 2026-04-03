# Import hashlib to perform cryptographic hashing (turning the password into a secure string of characters)
# Import requests to make HTTP calls to external servers (like the Have I Been Pwned API)
# Import necessary tools from Flask to build our web server
# Flask: The core app, request: To read incoming data, jsonify: To send back JSON data, render_template: To serve HTML files
# Import CORS to allow our frontend (HTML/JS) to communicate with our backend without security blockages from the browser

import hashlib
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)

# Apply CORS to our app so the browser allows requests from our local frontend to our local backend
CORS(app)

# Define the "root" route. When a user visits http://127.0.0.1:5000/, this function runs.
@app.route('/')
def index():
    # render_template looks inside the "templates" folder and sends the index.html file to the user's browser
    return render_template('index.html')

# Define the route that handles the password breach check. It only accepts POST requests (secure data submission).
@app.route('/check-breach', methods=['POST'])
def check_breach():
    # Read the incoming JSON data sent by the JavaScript fetch() function
    data = request.get_json()
    # Extract the 'password' field from that data
    password = data.get('password')
    
    # If the frontend sent an empty request, return a 400 Bad Request error
    if not password:
        return jsonify({"error": "No password provided"}), 400

    # 1. k-Anonymity Hashing Phase
    # Convert the raw password into a SHA-1 hash (a 40-character hexadecimal string).
    # We use .upper() because the API expects uppercase letters.
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    
    # Split the hash into two parts to protect the user's privacy
    # prefix: The first 5 characters (we send this to the internet)
    prefix = sha1_password[:5]
    # suffix: The remaining 35 characters (we keep this a secret on our local machine)
    suffix = sha1_password[5:]

    # 2. Querying the External API
    # Ask the API for a list of ALL compromised passwords that start with our 5-character prefix
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        # Make the request with a 5-second timeout so the server doesn't hang if the internet is down
        response = requests.get(url, timeout=5)
        # Check if the API returned an error (like a 404 or 500 status code)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        # If the network fails, send an error back to the frontend
        return jsonify({"error": "Security API Unreachable"}), 500

    # 3. Local Verification Phase
    # The API returns a large text block. We split it line by line.
    # Each line looks like this: SUFFIX:COUNT (e.g., 0018A45C4D1DEF81644B54AB7F969B88D83:15)
    hashes = (line.split(':') for line in response.text.splitlines())
    
    count = 0
    # Loop through the list provided by the API
    for h, c in hashes:
        # If the suffix from the API matches our secret suffix, the password is in the database!
        if h == suffix:
            # Save how many times it was leaked
            count = int(c)
            # Stop searching, we found our match
            break

    # Send the final count back to the JavaScript frontend as a JSON object
    return jsonify({"count": count})

# This ensures the server only starts if we run this file directly (not if we import it into another script)
if __name__ == '__main__':
    # Run the server on the local loopback address (127.0.0.1) on port 5000. Debug=True auto-restarts the server when we save changes.
    app.run(host='127.0.0.1', port=5000, debug=True)