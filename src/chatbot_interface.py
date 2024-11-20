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
    /* Center the chat container */
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        border-radius: 10px;
        background-color: #1e1e1e;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        margin: 0 auto;  /* Center the container */
    }
    .chat-message {
        margin-bottom: 15px;
        padding: 12px;
        border-radius: 15px;
    }
    /* User message styling */
    .user-message {
        background-color: #3f8f8f; /* Lighter background for user */
        color: #fff;
    }
    /* Chatbot message styling */
    .chatbot-message {
        background-color: #2c3e50; /* Darker background for chatbot */
        color: #fff;
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
            response = requests.post(FASTAPI_URL, json={"query": user_input})

            # Check if the response from FastAPI is successful
            if response.status_code == 200:
                answer = response.json().get("response", "Sorry, I couldn't understand your query.")
            else:
                answer = "Error: Unable to get a response from the API."

            # Append the user input and chatbot response to the session state history
            st.session_state.history.append({"role": "user", "message": user_input})
            st.session_state.history.append({"role": "chatbot", "message": answer})

    else:
        st.error("Please enter a valid question!")

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

# Place the input box at the bottom of the page
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.text_input("Ask a question:", key="user_input", placeholder="e.g., What is the price of BTC?", on_change=on_query_submit)
