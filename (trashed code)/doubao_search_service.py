
from flask import Flask, jsonify, request
import json
import os
from openai import OpenAI

app = Flask(__name__)

# 豆包搜索服务配置
try:
    with open(os.path.join(os.path.dirname(__file__), 'templates', 'doubao.txt'), 'r') as f:
        Doubao_API_KEY = f.read().strip()
    
    # 标准聊天客户端
    doubao_client = OpenAI(
        api_key=Doubao_API_KEY,
        base_url="https://ark.cn-beijing.volces.com/api/v3/bots"
    )
    
    # 测试连接
    test_completion = doubao_client.chat.completions.create(
        model="bot-20250506042211-5bscp",
        messages=[{"role": "system", "content": "测试连接"}]
    )
    print("豆包客户端初始化成功")
except Exception as e:
    print(f"豆包客户端初始化失败: {str(e)}")
    doubao_client = None

@app.route('/api/doubao/search', methods=['POST'])
def search():
    """豆包搜索API接口"""
    if not doubao_client:
        return jsonify({"error": "豆包客户端未初始化"}), 500
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体必须为JSON格式"}), 400
    
    model = data.get('model', 'bot-20250506042211-5bscp')
    messages = data.get('messages', [])
    stream = data.get('stream', False)
    
    if not messages:
        return jsonify({"error": "messages参数不能为空"}), 400
    
    try:
        if stream:
            # 流式响应
            def generate():
                stream = doubao_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            return Response(generate(), mimetype='text/plain')
        else:
            # 标准响应
            response = doubao_client.chat.completions.create(
                model=model,
                messages=messages
            )
            result = {
                "content": response.choices[0].message.content,
                "references": getattr(response, "references", None)
            }
            print("API返回结果:", json.dumps(result, indent=2, ensure_ascii=False))
            return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/doubao/websearch', methods=['POST'])
def websearch():
    """豆包web搜索API接口"""
    if not doubao_client:
        return jsonify({"error": "豆包客户端未初始化"}), 500
        
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({"error": "请求体必须包含query参数"}), 400
    
    try:
        response = doubao_client.chat.completions.create(
            model="bot-20250506042211-5bscp",
            messages=[
                {
                    "role": "user",
                    "content": f"请帮我搜索关于'{data['query']}'的信息，返回格式为JSON数组，每个结果包含title和url字段"
                }
            ]
        )
        
        result = response.choices[0].message.content
        try:
            parsed_result = json.loads(result)
            return jsonify(parsed_result)
        except json.JSONDecodeError:
            return jsonify({"content": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=10807)
