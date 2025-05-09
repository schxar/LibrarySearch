from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# 设置OpenAI API配置
openai.api_key = os.environ.get('OPENAI_API_KEY')  # 替换为实际的默认API Key
openai.base_url = os.environ.get('OPENAI_PROXY_URL')
openai.default_headers = {"x-foo": "true"}

@app.route('/api/chat', methods=['POST'])
def chat_with_openai():
    try:
        data = request.json
        messages = data.get('messages', [])
        model = data.get('model', 'gpt-4o-mini')

        # 调用OpenAI API
        response = openai.chat.completions.create(
            model=model,
            messages=messages
        )

        # 使用 model_dump 将响应转为字典
        response_dict = response.model_dump()

        # 返回完整字典或提取需要的数据
        return jsonify({
            'response': response_dict["choices"][0]["message"]["content"]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10802, debug=True)
