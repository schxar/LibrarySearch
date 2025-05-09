from flask import Flask, render_template_string, request, jsonify
from functools import wraps
import requests

app = Flask(__name__)

# Replace with your actual Clerk publishable key and API key
CLERK_PUBLISHABLE_KEY = "pk_test_bGFyZ2UtY3JheWZpc2gtMzIuY2xlcmsuYWNjb3VudHMuZGV2JA"
CLERK_API_KEY = "YOUR_CLERK_API_KEY"  # Replace with your Clerk API key

HTML_LOGIN = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Test with Clerk Authentication</title>
</head>
<body>
    <h1>Flask Test with Clerk Authentication</h1>
    <script
        async
        crossorigin="anonymous"
        data-clerk-publishable-key="{{ CLERK_PUBLISHABLE_KEY }}"
        src="https://intense-guppy-8.clerk.accounts.dev/npm/@clerk/clerk-js@latest/dist/clerk.browser.js"
        type="text/javascript"
    ></script>

    <div id="app"></div>
    <div id="loading" class="text-center mb-3" style="display: none;">
        <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <a href="/protected">Go to test login</a>
    <a href="https://notebooklm.google.com/">Go to NotebookLM</a>

    <script>
        window.addEventListener('load', async function () {
            await Clerk.load();
            if (Clerk.user) {
                document.getElementById('app').innerHTML = '<div id="user-button"></div>';
                Clerk.mountUserButton(document.getElementById('user-button'));
            } else {
                document.getElementById('app').innerHTML = '<div id="sign-in"></div>';
                Clerk.mountSignIn(document.getElementById('sign-in'));
            }

            // Get the JWT token from Clerk
            const token = await Clerk.user.getToken();
            window.customFetch = function(url, options) {
                options = options || {};
                options.headers = options.headers || {};
                options.headers.Authorization = `Bearer ${token}`;
                return fetch(url, options);
            };
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        jwt_token = auth_header[len('Bearer '):]
        response = requests.post(
            'https://api.clerk.dev/v1/tokens/verify',
            headers={
                'Authorization': f'Bearer {CLERK_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={'token': jwt_token}
        )
        if response.status_code == 200:
            user_email = response.json().get('email')
            print(f"User Email: {user_email}")
    return render_template_string(HTML_LOGIN, CLERK_PUBLISHABLE_KEY=CLERK_PUBLISHABLE_KEY)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"message": "Unauthorized"}), 401
        jwt_token = auth_header[len('Bearer '):]
        response = requests.post(
            'https://api.clerk.dev/v1/tokens/verify',
            headers={
                'Authorization': f'Bearer {CLERK_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={'token': jwt_token}
        )
        if response.status_code != 200:
            return jsonify({"message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({'message': 'You are logged in!'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10809)