
from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY")
)

@app.route('/api/doubao/vlm', methods=['POST'])
def doubao_vlm():
    """
    火山方舟多模态API接口
    支持文本和图像输入
    """
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        response = client.chat.completions.create(
            model="doubao-1.5-vision-pro-250328",
            messages=messages
        )
        
        return jsonify({
            "response": response.choices[0].message.content
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
