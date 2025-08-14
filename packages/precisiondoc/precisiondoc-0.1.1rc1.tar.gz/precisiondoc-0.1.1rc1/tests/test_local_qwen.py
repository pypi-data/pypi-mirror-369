from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.environ.get("API_KEY")
)

response = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "What is the capital of China?"}],
    max_tokens=512
)
print(response.choices[0].message.content)
