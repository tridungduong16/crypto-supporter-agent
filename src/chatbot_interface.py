import streamlit as st
import requests

# FastAPI endpoint
FASTAPI_URL = "http://127.0.0.1:8000/ask"  # Replace with your FastAPI server URL

# Page configuration
st.set_page_config(page_title="SatoshiSeal", layout="wide")

# Sidebar for clickable links
with st.sidebar:
    st.header("Quick Options")
    queries = {
        "Top Volume": "Tell me the top volume trading pairs on Binance.",
        "Greedy Index": "What is the current Fear and Greed Index?",
        "Price Check": "What is the current price of Bitcoin or Ethereum?",
        "Volume for Symbol": "Show me the trading volume for BTCUSDT.",
        "Pump Activity": "Detect recent pump activity in the crypto market.",
        "Aggregate News": "Fetch the latest news related to cryptocurrency.",
        "Technical Indicators": "Calculate technical indicators for BTC, such as RSI or moving averages.",
        "Telegram Posts": "What are the latest posts from Telegram channels about cryptocurrency?"
    }

    
    # Process query immediately when a button is clicked
    for label, query in queries.items():
        if st.button(label):
            if "messages" not in st.session_state:
                st.session_state.messages = []
            # Treat the button's query as real input
            st.session_state.messages.append({"role": "user", "content": query})
            st.session_state["process_query"] = query

# Header
st.markdown("""
    <h1 style='text-align: center;'>🤖 SatoshiSeal 🤖</h1>
    <p style='text-align: center; font-size: 16px;'>Cryptocurrency advisor</p>
    <hr>
    """, unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# Check if there is a query to process
if "process_query" in st.session_state:
    query_to_process = st.session_state["process_query"]
    del st.session_state["process_query"]

    # Display the query immediately as the user's message
    st.chat_message("user").write(query_to_process)

    # Process the query via FastAPI
    with st.spinner("Thinking..."):
        try:
            response = requests.post(FASTAPI_URL, json={"query": query_to_process})
            if response.status_code == 200:
                answer = response.json().get("response", "Sorry, I couldn't understand your query.")
            else:
                answer = "Error: Unable to get a response from the API."
        except Exception as e:
            answer = f"Error: {str(e)}"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)

# Input box for user query
if prompt := st.chat_input(placeholder="Your message"):
    # Append user query to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Process the query via FastAPI
    with st.spinner("Thinking..."):
        try:
            response = requests.post(FASTAPI_URL, json={"query": prompt})
            if response.status_code == 200:
                answer = response.json().get("response", "Sorry, I couldn't understand your query.")
            else:
                answer = "Error: Unable to get a response from the API."
        except Exception as e:
            answer = f"Error: {str(e)}"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
