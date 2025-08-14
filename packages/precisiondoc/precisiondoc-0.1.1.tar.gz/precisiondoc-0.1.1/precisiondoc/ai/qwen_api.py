import os
import requests
import json
from typing import Dict, Any, Optional
import base64
from openai import OpenAI
from dotenv import load_dotenv

from precisiondoc.utils.log_utils import setup_logger
from precisiondoc.config.promptes import page_type_classification_prompt_cn

# Setup logger for this module
logger = setup_logger(__name__)

class QwenClient:
    """Client for interacting with Qwen API using OpenAI compatible mode"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize the Qwen client.
        
        Args:
            api_key: API key for Qwen. If None, will try to load from environment variables.
            base_url: Base URL for Qwen API. If None, will try to load from environment variables.
        """
        if api_key is None:
            self.api_key = os.getenv("API_KEY")
            if not self.api_key:
                raise ValueError("API_KEY environment variable not set")
        else:
            self.api_key = api_key
        
        # Get base URL from parameter, environment or use default
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        # Initialize OpenAI client with DashScope compatible endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Get model names from environment variables or use defaults
        self.text_model = os.getenv("QWEN_TEXT_MODEL", "qwen-max")  # or qwen-max, qwen-plus, qwen-turbo
        self.multimodal_model = os.getenv("QWEN_MULTIMODAL_MODEL", "qwen-vl-max")  # or qwen-vl-plus
    
    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a chat request to Qwen API.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Response from Qwen API
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.text_model,
                messages=messages,
                temperature=0.3,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Qwen API: {str(e)}")
            return f"Error: {str(e)}"
    
    def chat_with_image(self, prompt: str, image_data: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a chat request with image to Qwen API.
        
        Args:
            prompt: User prompt
            image_data: Base64 encoded image data
            system_prompt: Optional system prompt
            
        Returns:
            Response from Qwen API
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Create image URL from base64 data
        image_url = f"data:image/png;base64,{image_data}"
        
        # Add image and prompt to user message
        user_message = {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt}
            ]
        }
        messages.append(user_message)
        
        try:
            completion = self.client.chat.completions.create(
                model=self.multimodal_model,
                messages=messages,
                temperature=0.3,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Qwen API with image: {str(e)}")
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Create client
    client = QwenClient()
    
    # Test text chat
    response = client.chat("请简要介绍一下高血压的治疗方法")
    print(f"Text response: {response}")
    
    # Test image chat (if you have an image)
    # with open("example.png", "rb") as image_file:
    #     import base64
    #     image_data = base64.b64encode(image_file.read()).decode("utf-8")
    #     response = client.chat_with_image("这张图片显示了什么？", image_data)
    #     print(f"Image response: {response}")
