
import os
from openai import OpenAI

# 从doubao.txt文件中读取API Key
with open(os.path.join(os.path.dirname(__file__), 'doubao.txt'), 'r') as f:
    api_key = f.read().strip()

# 初始化Ark客户端
client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3/bots",
    # 从文件中获取API Key
    api_key=api_key,
)

# 标准请求
print("----- 标准请求 -----")
completion = client.chat.completions.create(
    model="bot-20250506042211-5bscp",
    messages=[
        {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
        {"role": "user", "content": "常见的十字花科植物有哪些？"},
    ],
)
print(completion.choices[0].message.content)
if hasattr(completion, "references"):
    print(completion.references)

# 多轮对话
print("\n----- 多轮对话 -----")
completion = client.chat.completions.create(
    model="bot-20250506042211-5bscp",
    messages=[
        {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
        {"role": "user", "content": "花椰菜是什么？"},
        {"role": "assistant", "content": "花椰菜又称菜花、花菜，是一种常见的蔬菜。"},
        {"role": "user", "content": "再详细点"},
    ],
)
print(completion.choices[0].message.content)
if hasattr(completion, "references"):
    print(completion.references)

# 流式请求
print("\n----- 流式请求 -----")
stream = client.chat.completions.create(
    model="bot-20250506042211-5bscp",
    messages=[
        {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
        {"role": "user", "content": "常见的十字花科植物有哪些？"},
    ],
    stream=True,
)
for chunk in stream:
    if hasattr(chunk, "references"):
        print(chunk.references)
    if not chunk.choices:
        continue
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
print()
