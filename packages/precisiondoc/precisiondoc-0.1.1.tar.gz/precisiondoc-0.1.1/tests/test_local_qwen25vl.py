from openai import OpenAI
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    base_url=os.getenv("QWEN_BASES_URL"),
    api_key="no-key-required"
)

png_file = "test_images/page_029.png"
jpg_file = "test_images/qwen3-coder-main.jpg"

with open(jpg_file, "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

prompt = "请描述这张图片的内容"


image_url = f"data:image/png;base64,{image_data}"
        
# Add image and prompt to user message
user_message = {
    "role": "user",
    "content": [
        {"type": "image_url", "image_url": {"url": image_url}},
        {"type": "text", "text": prompt}
    ]
}

messages = []
messages.append(user_message)

try:
    completion = client.chat.completions.create(
        model="Qwen2.5-VL",
        messages=messages,
        temperature=0.3,
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Error calling Qwen API with image: {str(e)}")
