import requests

FASTAPI_URL = "http://127.0.0.1:8000/ask"  # Replace with your FastAPI server URL

# Example query
query = "what is the greedy index currently in the crypto market?"

# Sending the request to FastAPI and handling the streamed response
response = requests.post(FASTAPI_URL, json={"query": query}, stream=True)

# Check if the response is successful
if response.status_code == 200:
    # Print the streamed response token by token as they arrive
    for token in response.iter_lines(decode_unicode=True):
        if token:  # Only process non-empty tokens
            print(token)
else:
    print(f"Error: {response.status_code} - {response.text}")


# Example query
query = "what is the top volume in binance?"

# Sending the request to FastAPI and handling the streamed response
response = requests.post(FASTAPI_URL, json={"query": query}, stream=True)

# Check if the response is successful
if response.status_code == 200:
    # Print the streamed response token by token as they arrive
    for token in response.iter_lines(decode_unicode=True):
        if token:  # Only process non-empty tokens
            print(token)
else:
    print(f"Error: {response.status_code} - {response.text}")
