from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

gemini_key_path = "flask_openai_backend/Gemini.txt"

try:
    # Open the file and read its content as a string
    with open(gemini_key_path, "r") as file:
        GOOGLE_API_KEY = file.read().strip()  # Use .strip() to remove any leading/trailing whitespace or newlines

    # Print the API key or use it as needed
    print(f"API Key: {GOOGLE_API_KEY}")
except FileNotFoundError:
    print("Error: The file was not found.")
except IOError as e:
    print(f"Error reading the file: {e}")


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def get_search_results(query):
    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 初始化 WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 构建搜索 URL
        search_url = f"https://cse.google.com/cse?cx=b7a4dfc41bb40428c&key=AIzaSyCa4mngFulV3OzlW3Dw2Y-4xAJ3DsupgMg&q={query}"
        driver.get(search_url)

        # 等待页面加载并获取结果
        # 根据实际页面结构调整以下代码
        results = driver.find_elements(By.CSS_SELECTOR, "div.g")  # 示例选择器
        search_results = []
        for result in results:
            title = result.find_element(By.TAG_NAME, "h3").text
            link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
            snippet = result.find_element(By.CSS_SELECTOR, "div.IsZvec").text
            search_results.append({"title": title, "link": link, "snippet": snippet})

        return search_results
    finally:
        driver.quit()


# Configure the Gemini API

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the Flask app
app = Flask(__name__)

# Default model
model_name = "gemini-1.5-flash-002"
model = genai.GenerativeModel(model_name)



# HTML template for the web interface
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat with Gemini</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f9;
            color: #333;
        }
        h1 {
            text-align: center;
            color: #444;
            font-size: 2.5em;
        }
        #chatbox {
            width: 100%;
            height: 400px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background: white;
            overflow-y: auto;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            margin-bottom: 15px;
            font-size: 1.2em; /* Increase font size for better visibility */
            line-height: 1.8; /* Adjust line height for readability */
        }
        .message {
            margin: 10px 0;
        }
        .message.user {
            text-align: right;
            color: #2a9d8f;
            font-weight: bold;
        }
        .message.gemini {
            text-align: left;
            color: #e76f51;
        }
        #input-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        #user-input {
            flex-grow: 1;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 1.2em;
        }
        select, button {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #2a9d8f;
            color: white;
            font-size: 1.2em;
            cursor: pointer;
        }
        select {
            font-size: 1.2em;
        }
        button:hover {
            background-color: #21867a;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        footer {
            margin-top: 20px;
            text-align: center;
            font-size: 1em;
            color: #aaa;
        }
    </style>
</head>
<body>
    <h1>Chat with Gemini</h1>
    <div id="chatbox"></div>
    <div id="input-container">
        <input type="text" id="user-input" placeholder="Type your message here..." />
        <button onclick="sendMessage()">Send</button>
        <select id="model" onchange="changeModel()">
            <option value="gemini-1.5-flash-002">gemini-1.5-flash-002</option>
            <option value="gemini-1.5-pro-002">gemini-1.5-pro-002</option>
            <option value="gemini-1.0-pro">gemini-1.0-pro</option>
        </select>
    </div>
    <footer>Powered by Gemini | © 2024</footer>
    <script>
        function formatResponseText(text) {
            // Replace periods with a period and a line break for better readability
            return text.replace(/\./g, '.<br><br>');
        }

        async function sendMessage() {
            const userInput = document.getElementById("user-input").value;
            if (!userInput.trim()) return;
            
            const chatbox = document.getElementById("chatbox");
            chatbox.innerHTML += `<div class="message user"><strong>You:</strong> ${userInput}</div>`;
            document.getElementById("user-input").value = "";
            chatbox.scrollTop = chatbox.scrollHeight;

            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userInput })
            });

            const data = await response.json();
            const reply = data.response || data.error || "No response from Gemini.";
            const formattedReply = formatResponseText(reply); // Format response text
            chatbox.innerHTML += `<div class="message gemini"><strong>Gemini:</strong> ${formattedReply}</div>`;
            chatbox.scrollTop = chatbox.scrollHeight;
        }

        async function changeModel() {
            const selectedModel = document.getElementById("model").value;
            const chatbox = document.getElementById("chatbox");
            chatbox.innerHTML += `<div class="message"><em>Switching model to: ${selectedModel}...</em></div>`;

            const response = await fetch('/set_model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_name: selectedModel })
            });

            const data = await response.json();
            if (data.message) {
                chatbox.innerHTML += `<div class="message"><em>${data.message}</em></div>`;
            } else {
                chatbox.innerHTML += `<div class="message"><em>Error switching model: ${data.error}</em></div>`;
            }
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    </script>
</body>
</html>


"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/generate', methods=['POST'])
def generate_content():
    global model
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid input, expected JSON with 'message' key."}), 400

    user_message = data['message']
    try:
        # Call the Gemini 1.5 model to generate a response
        response = model.generate_content(
            user_message,
            safety_settings={"HARASSMENT": "block_none","SEXUALLY_EXPLICIT": "block_none",
                             "HATE_SPEECH": "block_none"},#tools='google_search_retrieval'#

            )
        generated_text = response.text
        return jsonify({"response": generated_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/set_model', methods=['POST'])
def set_model():
    global model, model_name
    data = request.get_json()
    if not data or 'model_name' not in data:
        return jsonify({"error": "Invalid input, expected JSON with 'model_name' key."}), 400

    new_model_name = data['model_name']
    try:
        model = genai.GenerativeModel(new_model_name)
        model_name = new_model_name
        return jsonify({"message": f"Model switched to {new_model_name}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=10803)
