FROM python:3.9-slim


WORKDIR /workspaces/ai-agent
COPY . .
COPY requirements_dev.txt ./
COPY *.sh /workspaces/ai-agent/

RUN apt-get update && apt-get install -y --no-install-recommends


# RUN apt-get update && apt-get install -y --no-install-recommends \
#     protobuf-compiler \
#     libprotobuf-dev \
#     git-lfs \
#     python3 \
#     python3-pip \
#     python3-setuptools \
#     python-is-python3 \
#     moreutils \
#     && rm -rf /var/lib/apt/lists/*

# RUN chmod +x /*.sh
# ENTRYPOINT ["entrypoint.sh"]

# Install curl and dependencies, add ngrok repository, and install ngrok
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl gnupg apt-transport-https && \
#     curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | gpg --dearmor -o /usr/share/keyrings/ngrok-archive-keyring.gpg && \
#     echo "deb [signed-by=/usr/share/keyrings/ngrok-archive-keyring.gpg] https://ngrok-agent.s3.amazonaws.com buster main" \
#     | tee /etc/apt/sources.list.d/ngrok.list && \
#     apt-get update && \
#     apt-get install -y ngrok && \
#     rm -rf /var/lib/apt/lists/*


# RUN ngrok config add-authtoken 2aJZGAB3U1nVUR0B6eCIYBWYkoS_3VGCNJUn1pEeSJJyeiExY

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     g++ \
#     figlet \
#     protobuf-compiler \
#     libprotobuf-dev \
#     git-lfs \
#     python3 \
#     python3-pip \
#     python3-setuptools \
#     python-is-python3 \
#     moreutils \
#     vmtouch \
#     locales \
#     curl \
#     sudo \
#     nano \
#     tree \
#     zip unzip wget \
#     software-properties-common \
#     && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip

RUN pip install --upgrade pip
RUN pip install -r requirements_dev.txt
RUN pip install llama-index-vector-stores-qdrant
RUN pip install llama-index-readers-file
RUN pip install llama-index-llms-openai
RUN pip install langchain-openai
RUN python3 -m pip install --upgrade pip
RUN pip install langchain-core==0.3.21 langchain-community==0.3.8 SQLAlchemy==2.0.35

RUN pip install langchain-qdrant
RUN pip install langchain-huggingface
RUN pip install -U langgraph
RUN pip install langchain
RUN pip install langchain-core
RUN pip install ta
RUN pip install PyPDF2
RUN pip install -U duckduckgo-search
RUN pip install streamlit

EXPOSE 4444 4444

CMD ["tail", "-f", "/dev/null"]
# CMD ["uvicorn", "src.agents.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# CMD ["sh", "-c", "uvicorn src.agents.main:app --host 0.0.0.0 --port 8000 --reload && streamlit run src/chatbot_interface.py --server.address=0.0.0.0 --server.port=8501"]
# COPY start.sh /start.sh
# CMD ["/start.sh"]