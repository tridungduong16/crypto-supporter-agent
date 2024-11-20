import streamlit as st
import requests
import time

FASTAPI_URL = "http://127.0.0.1:8000/chat"  # Replace with your FastAPI server URL
st.set_page_config(page_title="Crypto Market Analysis Chatbot", layout="wide")
st.markdown("""
    <h1 style='text-align: center; color: #2C3E50;'>Crypto Market Analysis Chatbot</h1>
    <p style='text-align: center; font-size: 20px; color: #95A5A6;'>Ask about crypto trends, price predictions, and more!</p>
    """, unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
user_input = st.text_input("Ask a question:", key="user_input", placeholder="e.g., What is the price of BTC?")
if st.button("Ask the Chatbot"):
    with st.spinner("Processing your query..."):
        time.sleep(2)  # Simulate the processing time (for demonstration purposes)
        if user_input:
            # Send the user input to FastAPI for processing
            response = requests.post(FASTAPI_URL, json={"query": user_input})

            # Check if the response from FastAPI is successful
            if response.status_code == 200:
                answer = response.json().get("response", "Sorry, I couldn't understand your query.")
            else:
                answer = "Error: Unable to get a response from the API."

            # Display the response in a beautiful container
            st.markdown(f"""
                <div style="background-color:#ECF0F1; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 10px;">
                    <h3 style="color: #34495E;">Chatbot Response:</h3>
                    <p style="color: #2C3E50; font-size: 16px;">{answer}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Please enter a valid question!")
        
# Add some footer text
st.markdown("""
    <p style='text-align: center; font-size: 12px; color: #95A5A6;'>Made with ❤️ by Your Name</p>
    """, unsafe_allow_html=True)
