FROM python:3.9-slim

WORKDIR /workspaces/ai-agent
COPY . .
COPY requirements_dev.txt ./
COPY *.sh /workspaces/ai-agent/
# RUN chmod +x /*.sh
# ENTRYPOINT ["entrypoint.sh"]
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    figlet \
    protobuf-compiler \
    libprotobuf-dev \
    git-lfs \
    python3 \
    python3-pip \
    python3-setuptools \
    python-is-python3 \
    moreutils \
    vmtouch \
    locales \
    curl \
    sudo \
    nano \
    tree \
    zip unzip wget \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements_dev.txt
RUN pip install llama-index-vector-stores-qdrant
RUN pip install llama-index-readers-file
RUN pip install llama-index-llms-openai
RUN python -m pip install TA-Lib

EXPOSE 4444 4444

CMD ["tail", "-f", "/dev/null"]
