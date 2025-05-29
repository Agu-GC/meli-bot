
FROM python:3.10
RUN pip install transformers torch
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('mistralai/Mistral-7B-Instruct-v0.1')"
COPY . /app
WORKDIR /app

FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
    
COPY ./documents ./documents

COPY ./api ./api
RUN pip install -e ./api
