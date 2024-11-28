import requests

BASE_URL = "http://127.0.0.1:8000"  # Update if running on a different host or port

def test_root():
    """Test the root endpoint."""
    response = requests.get(f"{BASE_URL}/")
    print("Testing Root Endpoint:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_process_message(message):
    """Test the /ask endpoint with a user message."""
    payload = {"message": message}
    response = requests.post(f"{BASE_URL}/ask", json=payload)
    print(f"Testing /ask Endpoint with message: '{message}'")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.json()}")
    print()

if __name__ == "__main__":
    # Test the root endpoint
    test_root()

    # Test /ask with various messages
    test_process_message("Get technical analysis for BTC")
    test_process_message("How about news for Ethereum?")
    test_process_message("What is the weather in New York?")
    test_process_message("")  # Testing with an empty message
