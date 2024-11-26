import streamlit as st
import requests

# FastAPI endpoint
FASTAPI_URL = "http://127.0.0.1:8000/ask"  # Replace with your FastAPI server URL

# Page configuration
st.set_page_config(page_title="SatoshiSeal", layout="wide")
logo_url = "icon.png"  # Replace with your logo file path or URL

# Sidebar for clickable links
with st.sidebar:
    st.header("Quick Options")
    queries = {
        "Khối lượng giao dịch lớn nhất trên binance": "Hiển thị các cặp giao dịch có khối lượng lớn nhất trên Binance.",
        "Chỉ số Tham lam & Sợ hãi": "Chỉ số Tham lam & Sợ hãi hiện tại là bao nhiêu?",
        "Kiểm tra giá": "Giá hiện tại của BTCUSDT là bao nhiêu?",
        # "Khối lượng giao dịch của PEPE": "Hiển thị khối lượng giao dịch cho cặp PEPEUSDT.",
        # "Hoạt động Pump": "Phát hiện hoạt động pump gần đây trong thị trường tiền mã hóa.",
        "Tổng hợp tin tức từ google và reddits cho bitcoin": "Lấy tin tức mới nhất liên quan đến bitcoin trên google news và reddits",
        "Phân tích kỹ thuật bitcoin": "Tính toán các chỉ báo kỹ thuật cho BTC",
        # "Thông tin mới nhất trên Telegram": "Bài viết mới nhất từ kênh Telegram @FinancialStreetVN về crypto",
        "Có nên mua bitcoin không?": "Tôi có nên mua bitcoin dựa vào tin tức và các phân tích kĩ thuật hiện tại không?"
    }

    
    for label, query in queries.items():
        if st.button(label):
            st.session_state["pending_input"] = query  # Set the pending input for chat

# Header
# st.image(logo_url, width=100)  # Adjust width as needed
# st.image(logo_url, width=150)  # Adjust the width as needed

# Use Streamlit's layout for centering the image
col1, col2, col3, col4, col5 = st.columns([1, 1.4, 1,  1, 1])  # Create three columns
with col3:  # Center the image in the middle column
    st.image(logo_url, width=200)  # Adjust the width as needed

st.markdown("""
    <h1 style='text-align: center;'>🤖 SatoshiSeal 🤖</h1>
    <p style='text-align: center; font-size: 16px;'>Cryptocurrency advisor</p>
    <hr>
    """, unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I am SatoshiSeal, a cryptocurrenty agent. How can I help you today?"}
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
            response = requests.post(FASTAPI_URL, json={"query": user_input})
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
    with st.spinner("Processing..."):
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
