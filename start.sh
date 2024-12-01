#!/bin/bash
# Start uvicorn in the background
uvicorn src.agents.main:app --host 0.0.0.0 --port 8000 --reload &

# Start streamlit
streamlit run src/chatbot_interface.py --server.address=0.0.0.0 --server.port=8501
