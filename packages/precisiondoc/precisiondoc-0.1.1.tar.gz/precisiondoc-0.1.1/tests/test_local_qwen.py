from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    base_url=os.getenv("QWEN_BASES_URL"),
    api_key="no-key-required"
)

response = client.chat.completions.create(
    model="Qwen3-32B",
    # model="/mnt/ai/models/Qwen/Qwen3-32B",
    messages=[{"role": "user", "content": "你好！你是谁？"}],
    max_tokens=512
)
print(response.choices[0].message.content)
