// Step 1: Grab elements from the HTML by their ID so we can manipulate them.
const input = document.getElementById('password-input');
const btn = document.getElementById('check-btn');
const toggleBtn = document.getElementById('toggle-btn');
const eyeIcon = document.getElementById('eye-icon');
const resultsSection = document.getElementById('results-section');
const strengthText = document.getElementById('strength-text');
const strengthBar = document.getElementById('strength-bar'); // Now points to meter-fill
const feedback = document.getElementById('feedback');
const breachStatus = document.getElementById('breach-status');

// Requirements elements
const reqLength = document.getElementById('req-length');
const reqUppercase = document.getElementById('req-uppercase');
const reqLowercase = document.getElementById('req-lowercase');
const reqNumber = document.getElementById('req-number');
const reqSymbol = document.getElementById('req-symbol');

// Define arrays that map a numerical score (0 to 4) to specific text and colors.
const labels = ['Critically Weak', 'Weak', 'Moderate', 'Strong', 'Unbreakable'];
const colors = ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#16a34a'];

// Step 2: Handle the Password Visibility Toggle
// Listen for a 'click' event on the eye icon button
toggleBtn.addEventListener('click', () => {
    // Check the current type of the input field
    if (input.type === 'password') {
        // If it's a password (dots), change it to 'text' (readable characters)
        input.type = 'text';
        // Replace the SVG inside the button with a "slashed eye" icon
        eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /> 
        `;
    } else {
        // If it is text, change it back to 'password' (dots)
        input.type = 'password';
        // Replace the SVG with the default "open eye" icon
        eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        `;
    }
});

// Step 2.5: Real-time password requirements checker
function updateRequirements(password) {
    const requirements = {
        length: password.length >= 12,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        symbol: /[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>\/?]/.test(password)
    };
    
    updateRequirementIcon(reqLength, requirements.length);
    updateRequirementIcon(reqUppercase, requirements.uppercase);
    updateRequirementIcon(reqLowercase, requirements.lowercase);
    updateRequirementIcon(reqNumber, requirements.number);
    updateRequirementIcon(reqSymbol, requirements.symbol);
    
    return requirements;
}

function updateRequirementIcon(element, isMet) {
    if (isMet) {
        element.classList.add('met');
    } else {
        element.classList.remove('met');
    }
}

// Listen for real-time input changes
input.addEventListener('input', () => {
    if (!input.value) return;
    updateRequirements(input.value);
})

// Step 3: Define the core analysis logic
// We use 'async' because we need to make an HTTP network request, which takes time.
async function triggerAnalysis() {
    // Get the exact string the user typed into the box
    const pwd = input.value;
    
    // Stop the function immediately if the box is empty
    if (!pwd) return;

    // Remove the 'hidden' class from the CSS, causing the results box to fade in and slide up
    resultsSection.classList.remove('hidden');
    
    // Set a temporary loading message so the user knows the network request is happening
    breachStatus.innerText = 'Querying databases...';
    breachStatus.style.color = '#94a3b8';

    // -- Local Execution (Fast) --
    // Run the zxcvbn library against the password to check for entropy, patterns, and dictionary words.
    const result = zxcvbn(pwd);
    // Score is an integer from 0 to 4.
    const score = result.score;

    // Update the UI based on the array indexes matching the score
    strengthText.innerText = labels[score];
    strengthText.style.color = colors[score];
    // Calculate the width. If score is 0, width is 20%. If score is 4, width is 100%.
    strengthBar.style.width = `${(score + 1) * 20}%`;
    strengthBar.style.backgroundColor = colors[score];
    
    // Join the array of text suggestions provided by zxcvbn into a single string. Provide a fallback if array is empty.
    const feedbackText = result.feedback.suggestions.join(' ') || 'Password structure is mathematically sound.';
    feedback.textContent = feedbackText; // Use textContent to prevent XSS
    feedback.style.color = '#f8fafc';

    // -- External Execution (Slow) --
    // Only send to the backend if the password is 4 or more characters to avoid wasting API calls on "123"
    if (pwd.length >= 4) {
        try {
            // The fetch API sends a network request to our Flask app. 'await' tells the code to pause here until the server responds.
            const response = await fetch('/check-breach', {
                method: 'POST', // Send data securely
                headers: { 'Content-Type': 'application/json' }, // Tell Python we are sending JSON data
                body: JSON.stringify({ password: pwd }) // Convert our JavaScript object into a JSON string
            });
            
            // If the server crashes or returns an error code, manually trigger the 'catch' block
            if (!response.ok) throw new Error('API failure');
            
            // Convert the server's JSON response back into a JavaScript object
            const data = await response.json();

            // Check the count returned by Python
            if (data.count > 0) {
                // Safely create DOM elements to prevent XSS
                breachStatus.innerHTML = ''; // Clear previous content
                const strong = document.createElement('strong');
                strong.textContent = 'Compromised. ';
                const text = document.createTextNode(`Found in ${data.count.toLocaleString()} known data breaches. Do not use.`);
                breachStatus.appendChild(strong);
                breachStatus.appendChild(text);
                breachStatus.style.color = '#ef4444'; // Red
            } else {
                breachStatus.innerHTML = ''; // Clear previous content
                const strong = document.createElement('strong');
                strong.textContent = 'Secure. ';
                const text = document.createTextNode('No matches found in known data breaches.');
                breachStatus.appendChild(strong);
                breachStatus.appendChild(text);
                breachStatus.style.color = '#22c55e'; // Green
            }
            
            // Display strength requirements status
            if (data.strength_requirements) {
                const reqStatus = data.strength_requirements;
                const allMet = data.meets_all_requirements;
                
                // Add strength requirements note
                const br = document.createElement('br');
                const reqNote = document.createElement('div');
                reqNote.style.marginTop = '0.75rem';
                reqNote.style.fontSize = '0.85rem';
                reqNote.style.opacity = '0.8';
                
                const metCount = Object.values(reqStatus).filter(v => v).length;
                const totalReqs = Object.keys(reqStatus).length;
                
                if (allMet) {
                    reqNote.textContent = `✓ All ${totalReqs} security requirements met!`;
                    reqNote.style.color = '#22c55e';
                } else {
                    reqNote.textContent = `${metCount}/${totalReqs} security requirements met`;
                    reqNote.style.color = '#f59e0b';
                }
                
                breachStatus.appendChild(br);
                breachStatus.appendChild(reqNote);
            }
        } catch (error) {
            // If the fetch fails (e.g., the Python server is not running), show an error message
            breachStatus.innerText = 'Error connecting to local Python server. Is app.py running?';
            breachStatus.style.color = '#ef4444';
        }
    } else {
        // Handle short passwords
        breachStatus.innerText = 'Password too short to reliably query databases.';
        breachStatus.style.color = '#f59e0b'; // Yellow
    }
}

// Step 4: Attach the logic to user actions
// Run the triggerAnalysis function when the blue "Analyze" button is clicked
btn.addEventListener('click', triggerAnalysis);

// Run the triggerAnalysis function if the user presses the 'Enter' key while typing in the input box
input.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        triggerAnalysis();
    }
});