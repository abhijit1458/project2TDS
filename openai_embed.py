import requests
import json
import os

AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")

def find_embed(ques):
    url = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "input": ques,  # Make sure this is a fresh input each time
        "model": "text-embedding-3-small",
        "encoding_format": "float"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    return response.json()['data'][0]['embedding']

