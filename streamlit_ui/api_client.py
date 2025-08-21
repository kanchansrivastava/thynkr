import requests
from config import API_BASE

def upload_file(file):
    files = {"file": (file.name, file, file.type)}
    return requests.post(f"{API_BASE}/upload", files=files)

def summarize_content(content_id):
    return requests.post(f"{API_BASE}/summarize", json={"content_id": content_id})

def ask_question(content_id, query):
    return requests.post(f"{API_BASE}/ask", json={"content_id": content_id, "query": query})

def fetch_history():
    return requests.get(f"{API_BASE}/history")

def call_agent(query):
    return requests.post(f"{API_BASE}/agent", json={"query": query})