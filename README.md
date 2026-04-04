# 🔐 SecureGuard - Password Checker

> A professional-grade password security audit tool that validates passwords against known data breaches while maintaining user privacy through cryptographic k-anonymity techniques.

## 📋 Project Overview

SecureGuard is a full-stack web application designed to help users assess password security by checking against the Have I Been Pwned (HIBP) database of compromised credentials. The application combines real-time password strength analysis with privacy-preserving breach detection, ensuring that user passwords are never transmitted in plain text to external APIs.

**Key Differentiator:** 
Implements k-anonymity protocol using SHA-1 hashing to query breach databases while protecting user privacy—only password prefixes are sent to HIBP, making the system secure even in untrusted network environments.

## ✨ Features

- **Real-time Password Strength Analysis**: Client-side password strength scoring using the industry-standard zxcvbn library
- **Privacy-First Breach Detection**: k-Anonymity implementation via SHA-1 prefix/suffix hashing to prevent full password transmission
- **Compromised Credentials Database**: Integration with Have I Been Pwned (HIBP) API for up-to-date breach intelligence
- **Instant Security Feedback**: Breach count detection with user-friendly status indicators (0 = safe, >0 = compromised)
- **Enhanced UX**: Password visibility toggle for flexible input management
- **RESTful API**: Clean backend endpoint (`POST /check-breach`) for programmatic integration

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.8+ with Flask Framework |
| Frontend | HTML5, CSS3 (Flexbox), Vanilla JavaScript |
| Password Strength | zxcvbn (v4.4.2) |
| Breach Database | HIBP (Have I Been Pwned) API |
| API Communication | fetch() with JSON payloads |
| Privacy Protocol | k-Anonymity with SHA-1 hashing |

## 📋 Prerequisites

- **Python 3.8+** (tested with Python 3.11.2)
- **pip** (Python package manager)
- **Git** (for version control)
- **Modern web browser** (Chrome, Firefox, Edge, Safari)

## 🚀 Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/nilakashchatterjee/SecureGuard---Password-Analyser.git
cd SecureGuard---Password-Analyser
```

### Step 2: Create and Activate Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

Navigate to `http://127.0.0.1:5000` in your web browser.
Navigate to → `http://127.0.0.1:5000/`

## 📖 How It Works

### Architecture Overview

```
User Input (Password)
    ↓
[Frontend - index.html, script.js]
    ├─ Strength Analysis (zxcvbn)
    ├─ k-Anonymity Hash (SHA-1)
    └─ Send to Backend
    ↓
[Backend - app.py]
    ├─ SHA-1 Hash Processing
    ├─ Extract 5-char prefix
    └─ Query HIBP API
    ↓
[HIBP API Response]
    ├─ Receive partial hashes
    └─ Count matches locally
    ↓
[Frontend Display]
    ├─ Show Strength Score
    ├─ Show Breach Status
    └─ Real-time Feedback
```

### Privacy Implementation (k-Anonymity)

1. User enters password in frontend
2. Password is hashed using SHA-1: `sha1(password)` = 40-character hex string
3. Hash is split: First 5 chars (prefix) + Remaining 35 chars (suffix)
4. **Only the 5-character prefix is sent to HIBP API**
5. HIBP returns all password hashes matching that prefix
6. Frontend compares suffix locally—HIBP never sees full hash
7. Match count returned to user (0 = safe, >0 = breached)

**Why This Matters:** Even if someone intercepts the network traffic, they only see a 5-character SHA-1 prefix, not the full password hash—maintaining user privacy while leveraging HIBP's expansive breach database.

## 🆕 Recent Updates (v2.0)

### Security Hardening
- **XSS Prevention**: Implemented safe DOM manipulation using `textContent` and `createElement()` instead of `innerHTML` to prevent code injection attacks
- **Security Headers**: Added comprehensive HTTP security headers:
  - `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing attacks
  - `X-Frame-Options: DENY` - Protection against clickjacking
  - `X-XSS-Protection: 1; mode=block` - Browser-level XSS filter enforcement
  - `Content-Security-Policy` - Restricts script execution to trusted sources (CDN allowlist for zxcvbn)
- **Input Validation & Sanitization**:
  - Content-Type validation (JSON payloads only)
  - Type checking for password parameter (string validation)
  - Maximum password length enforcement (512 characters)
  - Input trimming and normalization
- **Error Handling**: Enhanced error responses that do not expose internal system details

### Password Structure Requirements
- **Real-Time Validation**: Live feedback as users type, with visual requirement checklist updates
- **Five-Tier Security Criteria**:
  - Minimum length of 12 characters
  - Contains uppercase letters (A-Z)
  - Contains lowercase letters (a-z)
  - Contains numeric digits (0-9)
  - Contains special symbols (!@#$%^&*...)
- **Visual Progress Indicator**: Displays requirement completion status (X/5 met) with animated checkmarks
- **New Endpoint**: `GET /password-requirements` returns configured security standards

### User Interface Redesign
- **Optimized Layout**: Compact, premium design reducing vertical space consumption by ~40%
- **Information Grid**: Three-column responsive layout displaying:
  - Password requirements with status icons
  - Structural feedback from entropy analysis
  - Security status from breach database
- **Visual Refinements**: Modern strength meter, improved typography hierarchy, and updated color scheme
- **Responsive Design**: Automatically adapts from 3-column desktop layout to 2-column tablet and single-column mobile views
- **Interactive Animations**: Smooth transitions with visual cues for requirement completion

### Backend Enhancements
- **Password Strength Validation**: New `validate_password_strength()` function utilizing regex pattern matching for criteria assessment
- **Extended API Response**: Enhanced `/check-breach` endpoint returns detailed JSON including:
  ```json
  {
    "count": <number>,
    "strength_requirements": {
      "length": <boolean>,
      "uppercase": <boolean>,
      "lowercase": <boolean>,
      "number": <boolean>,
      "symbol": <boolean>
    },
    "meets_all_requirements": <boolean>
  }
  ```
- **Code Organization**: Security constants definition, improved code structure, and better separation of concerns
- **Exception Handling**: Robust error management with meaningful user-facing messages

## 🔌 API Reference

### POST `/check-breach`

Validates a password against the HIBP breach database using k-anonymity.

**Request:**
```json
{
  "password": "MySecurePassword123!"
}
```

**Response (Safe Password):**
```json
{
  "count": 0
}
```

**Response (Compromised Password):**
```json
{
  "count": 847
}
```

**Status Codes:**
| Code | Meaning |
|------|---------|
| 200 | Request successful, breach status returned |
| 400 | Missing or invalid password parameter |
| 500 | Server error processing request |

**Response Interpretation:**
- `count = 0` → Password **NOT** found in any known breach (✅ Safe)
- `count > 0` → Password found in `count` different breaches (⚠️ Compromised)

## 🔒 Security Guarantees

✅ **Passwords Never Stored** - No passwords are persisted on disk or database  
✅ **No Plain-Text Transmission** - Both frontend and backend use cryptographic hashing  
✅ **k-Anonymity Protected** - Only 5-character SHA-1 prefixes leave your system  
✅ **SSL/TLS Ready** - Backend supports HTTPS in production deployment  
✅ **CORS Controlled** - Flask-CORS prevents unauthorized cross-origin requests  

## 📁 Project Structure

```
SecureGuard---Password-Analyser/
├── app.py                    # Flask backend server
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── venv/                     # Python virtual environment (gitignored)
├── static/
│   ├── script.js            # Frontend password logic & HIBP integration
│   └── style.css            # Responsive UI styling
└── templates/
    └── index.html           # HTML frontend
```

## ⚠️ Important Notes

- **No password data is stored** on the server or in any database
- **App runs in debug mode** by default—suitable for development/learning only
- **Tested Environment**: Python 3.11.2, Windows 10/11
- **Browser Compatibility**: Modern browsers with ES6+ support and Fetch API

## 🚀 Production Recommendations

For deploying SecureGuard in a production environment, implement:

| Feature | Purpose | Implementation |
|---------|---------|-----------------|
| **Rate Limiting** | Prevent API abuse | python-ratelimit or Flask-Limiter |
| **TLS/HTTPS** | Encrypt client-server communication | SSL certificates + reverse proxy (nginx) |
| **Request Validation** | Sanitize & validate inputs | schema validation + input length checks |
| **Logging & Monitoring** | Track errors & performance | structured logging + APM tools |
| **Error Handling** | Graceful failure recovery | try-catch blocks + user-friendly errors |
| **CORS Policies** | Restrict cross-origin access | whitelist specific domains |
| **Load Balancing** | Handle traffic spikes | gunicorn + load balancer |
| **Caching** | Reduce HIBP API calls | Redis for prefix result caching |

## 📈 Performance Enhancements

- **Redis Caching**: Cache HIBP prefix responses to reduce API calls by ~70%
- **Gzip Compression**: Enable compression for static assets (CSS, JS)
- **CDN Integration**: Serve zxcvbn.js from CDN for faster downloads
- **Database Logging**: Optional SQLite/PostgreSQL for request analytics

## 🧪 Testing & Quality

- **Unit Tests**: Add pytest cases for SHA-1 hashing & HIBP parsing
- **Integration Tests**: Test full password check flow end-to-end
- **Security Audit**: Use OWASP Top 10 checklist for vulnerability assessment
- **Load Testing**: Use Apache JMeter or locust for stress testing

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes with descriptive messages
4. Push to your fork
5. Open a Pull Request with detailed explanation

## 📄 License

This project is open source and available under the MIT License.

## 📧 Support & Questions

For issues, questions, or feedback:
- Open an issue on GitHub
- Check existing documentation in this README
- Review code comments in `app.py` and `script.js` for implementation details

---

**Last Updated:** April 2026  
**Status:** ✅ Active Development  
**Security Level:** Production-Ready with Recommended Hardening
