import streamlit as st
import requests
import time

FASTAPI_URL = "http://127.0.0.1:8000/ask"  # Replace with your FastAPI server URL

# Set up the page title, layout, and dark theme
st.set_page_config(page_title="Crypto Market Analysis Chatbot", layout="wide")
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

# User input box for chat
user_input = st.text_input("Ask a question:", key="user_input", placeholder="e.g., What is the price of BTC?")

# When the user presses the "Ask the Chatbot" button
if st.button("Ask the Chatbot"):
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
    # Display a slider to scroll through the history
    history_index = st.slider("View Chat History", 0, history_length - 1, history_length - 1)
    
    # Display the entire chat history up to the selected index
    for i in range(history_index + 1):
        chat = st.session_state.history[i]
        if chat["role"] == "user":
            st.markdown(f"""
                <div style="background-color:#D5F5E3; padding: 10px; border-radius: 10px; margin-top: 5px;">
                    <strong style="color:#34495E;">User:</strong> {chat['message']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color:#ECF0F1; padding: 10px; border-radius: 10px; margin-top: 5px;">
                    <strong style="color:#34495E;">Chatbot:</strong> {chat['message']}
                </div>
                """, unsafe_allow_html=True)

# Add footer
st.markdown("""
    <p style='text-align: center; font-size: 12px; color: #95A5A6;'>Made with ❤️ by Your Name</p>
    """, unsafe_allow_html=True)
