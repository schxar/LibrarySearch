import os
from openai import OpenAI

# 从doubao.txt文件中读取API Key
with open(os.path.join(os.path.dirname(__file__), 'doubao.txt'), 'r') as f:
    api_key = f.read().strip()

# 初始化Ark客户端
print("正在初始化VLM客户端...")
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=api_key,
)
print("VLM客户端初始化成功")

try:
    print("正在调用VLM接口...")
    response = client.chat.completions.create(
        model="doubao-1.5-vision-pro-250328",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                        },
                    },
                    {"type": "text", "text": "这是哪里？"},
                ],
            }
        ],
    )
    print("VLM接口调用成功！")
    print("响应内容:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"VLM接口调用失败: {str(e)}")
    import traceback
    traceback.print_exc()