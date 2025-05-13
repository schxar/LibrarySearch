import os
from openai import OpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

print("----- embeddings request -----")
resp = client.embeddings.create(
    model="doubao-embedding-large-text-240915",
    input=["花椰菜又称菜花、花菜，是一种常见的蔬菜。"],
    encoding_format="float"
)
print(resp)
