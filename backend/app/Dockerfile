FROM python:3.11-slim

WORKDIR /

COPY . /app
RUN pip install -r /app/requirements.txt


CMD uvicorn app.server:app --host 0.0.0.0 --port 8000