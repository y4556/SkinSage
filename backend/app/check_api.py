import os
from dotenv import load_dotenv
import httpx

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = httpx.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers=headers,
    json={
        "model": "llama3-70b-8192",
        "messages": [{"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": "Hello!"}]
    }
)

print("STATUS:", response.status_code)
print("BODY:", response.text)
