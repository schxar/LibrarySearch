import requests

url = "http://localhost:10802/ai/generate"
params = {"message": "Write a poem about Spring"}

response = requests.get(url, params=params)
print(response.json())
