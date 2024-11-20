import os
import requests
from dotenv import load_dotenv
load_dotenv()
url = "http://127.0.0.1:8000/ask"
query = "what is the greedy index currently in crypto market?"
data = {
    "query": query
}
response = requests.post(url, json=data)
if response.status_code == 200:
    print(f"Response: {response.json()}")
else:
    print(f"Error: {response.status_code}")

query = "give me the top volume in binance"
data = {
    "query": query
}
response = requests.post(url, json=data)
if response.status_code == 200:
    print(f"Response: {response.json()}")
else:
    print(f"Error: {response.status_code}")