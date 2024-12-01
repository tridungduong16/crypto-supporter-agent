import streamlit as st
import requests

# FastAPI endpoint
# FASTAPI_URL = "http://127.0.0.1:8000/ask"  # Replace with your FastAPI server URL
FASTAPI_URL = "http://uvicorn:8000/ask"  # Use the service name 'uvicorn' as the hostname

# Page configuration
st.set_page_config(page_title="SatoshiSeal", layout="wide")
logo_url = "icon.png"  # Replace with your logo file path or URL

# Sidebar for clickable links
with st.sidebar:
    st.header("Quick Options")
    queries = {
        "Khối lượng giao dịch lớn nhất trên Binance": "Hiển thị các cặp giao dịch có khối lượng lớn nhất trên Binance.",
        "Chỉ số Tham lam & Sợ hãi": "Chỉ số Tham lam & Sợ hãi hiện tại là bao nhiêu?",
        "Kiểm tra giá": "Giá hiện tại của BTCUSDT là bao nhiêu?",
        "Tổng hợp tin tức từ Google và Reddit cho Bitcoin": "Lấy tin tức mới nhất liên quan đến Bitcoin trên Google News và Reddit.",
        "Phân tích kỹ thuật Bitcoin": "Tính toán các chỉ báo kỹ thuật cho BTC.",
        "Có nên mua Bitcoin không?": "Tôi có nên mua Bitcoin dựa vào tin tức và các phân tích kỹ thuật hiện tại không?"
    }

    for label, query in queries.items():
        if st.button(label):
            st.session_state["pending_input"] = query  # Set the pending input for chat

# Header and logo
col1, col2, col3, col4, col5 = st.columns([1, 1.4, 1, 1, 1])
with col3:
    st.image(logo_url, width=200)

st.markdown("""
    <h1 style='text-align: center;'>🤖 SatoshiSeal 🤖</h1>
    <p style='text-align: center; font-size: 16px;'>Cryptocurrency Advisor</p>
    <hr>
    """, unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I am SatoshiSeal, a cryptocurrency agent. How can I help you today?"}
    ]

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# Process pending input from sidebar buttons
if "pending_input" in st.session_state:
    user_input = st.session_state["pending_input"]
    del st.session_state["pending_input"]  # Clear after use
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Process the query via FastAPI
    with st.spinner("Thinking..."):
        try:
            response = requests.post(FASTAPI_URL, json={"message": user_input})
            if response.status_code == 200:
                answer = response.json().get("response", "Sorry, I couldn't understand your query.")
            else:
                answer = f"Error: {response.status_code} - Unable to get a response from the API."
        except requests.exceptions.RequestException as e:
            answer = f"Error: {str(e)}"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)

# Input box for user query
if prompt := st.chat_input(placeholder="Type your message here..."):
    # Append user query to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Process the query via FastAPI
    with st.spinner("Processing..."):
        try:
            response = requests.post(FASTAPI_URL, json={"message": prompt})
            if response.status_code == 200:
                answer = response.json().get("response", "Sorry, I couldn't understand your query.")
            else:
                answer = f"Error: {response.status_code} - Unable to get a response from the API."
        except requests.exceptions.RequestException as e:
            answer = f"Error: {str(e)}"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
