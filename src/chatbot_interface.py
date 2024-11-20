import streamlit as st
import requests
import time

FASTAPI_URL = "http://127.0.0.1:8000/ask"  # Replace with your FastAPI server URL

# Set up the page title, layout, and dark theme
st.set_page_config(page_title="Crypto Market Analysis Chatbot", layout="wide")

# Custom CSS for styling the page
st.markdown(
    """
    <style>
    body {
        background-color: #2c3e50;
        color: #ecf0f1;
    }
    .stTextInput>div>div>input {
        background-color: #34495e;
        color: #ecf0f1;
    }
    .stButton>button {
        background-color: #3498db;
        color: #ecf0f1;
    }
    .stTextInput>div>label {
        color: #ecf0f1;
    }
    .stMarkdown>p {
        color: #ecf0f1;
    }
    .chat-message {
        margin-bottom: 15px;
        padding: 12px;
        border-radius: 15px;
    }
    .user-message {
        background-color: #3f8f8f;
        color: #fff;
    }
    .chatbot-message {
        background-color: #2c3e50;
        color: #fff;
    }
    .bubble {
        background-color: #3498db;
        padding: 10px;
        border-radius: 15px;
        margin: 5px;
        color: white;
        cursor: pointer;
        display: inline-block;
    }
    .bubble:hover {
        background-color: #2980b9;
    }
    </style>
    """, unsafe_allow_html=True
)

# Header
st.markdown("""
    <h1 style='text-align: center; color: #ecf0f1;'>Crypto Market Analysis Chatbot</h1>
    <p style='text-align: center; font-size: 20px; color: #95A5A6;'>Ask about crypto trends, price predictions, and more!</p>
    """, unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Initialize chat history in session state if not already
if "history" not in st.session_state:
    st.session_state.history = []

# Function to handle when user submits input by pressing "Enter"
def on_query_submit():
    user_input = st.session_state.user_input
    if user_input:
        with st.spinner("Processing your query..."):
            time.sleep(2)  # Simulate the processing time

            # Send the user input to FastAPI for processing
            response = requests.post(FASTAPI_URL, json={"query": user_input}, stream=True)

            final_answer = ''
            for token in response.iter_lines(decode_unicode=True):
                if token:  # Only process non-empty tokens
                    final_answer += token

            # Check if the response from FastAPI is successful
            # if response.status_code == 200:
            #     answer = response.json().get("response", "Sorry, I couldn't understand your query.")
            # else:
            #     answer = "Error: Unable to get a response from the API."

            # Append the user input and chatbot response to the session state history
            st.session_state.history.append({"role": "user", "message": user_input})
            st.session_state.history.append({"role": "chatbot", "message": final_answer})

    else:
        st.error("Please enter a valid question!")

# Display clickable bubbles
def display_bubbles():
    bubbles = [
        ("average price BTCUSDT", "Retrieves the average price of BTCUSDT pair from Binance?"),
        ("Top Volume in Binance", "What is the top  10 volume in Binance?"),
        ("Greedy Index", "What is the current Fear and Greed Index for Bitcoin?"),
        ("News about Solana", "Get news about Solana")
    ]
    
    for bubble_text, query in bubbles:
        # This will set the user input field when clicked
        if st.button(bubble_text):
            st.session_state.user_input = query  # Set the user input to the clicked bubble's query

# Scrollable history
history_length = len(st.session_state.history)
if history_length > 0:
    # Create a column-based layout to center the chat container
    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust these values to change margins

    with col2:  # This is the center column
        # Display the entire chat history
        for chat in st.session_state.history:
            if chat["role"] == "user":
                st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>User:</strong> {chat['message']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message chatbot-message">
                        <strong>Chatbot:</strong> {chat['message']}
                    </div>
                    """, unsafe_allow_html=True)

# Footer and the input box at the bottom (in a new container)
st.markdown("""
    <p style='text-align: center; font-size: 12px; color: #95A5A6;'>Made with ❤️ by Your Name</p>
    """, unsafe_allow_html=True)

# Add the clickable bubbles
display_bubbles()

# Place the input box at the bottom of the page
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.text_input("Ask a question:", key="user_input", placeholder="e.g., What is the price of BTC?", on_change=on_query_submit)