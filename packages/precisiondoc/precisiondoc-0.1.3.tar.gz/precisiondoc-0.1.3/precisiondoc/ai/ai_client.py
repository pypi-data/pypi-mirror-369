import os
import openai
import base64
from typing import Dict, Optional
import json

from precisiondoc.utils.log_utils import setup_logger
from precisiondoc.config.promptes import page_type_classification_prompt_cn

# Setup logger for this module
logger = setup_logger(__name__)

class AIClient:
    """Client for interacting with AI APIs (OpenAI)"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initialize the AI client.
        
        Args:
            api_key: API key for OpenAI. If None, will try to load from environment variables.
            base_url: Base URL for API. If None, will try to load from environment variables.
            model: Model to use for OpenAI API calls. If None, will try to load from environment variables.
        """
        # If API key is not provided, try to load from environment variables
        if api_key is None:
            self.api_key = os.getenv("API_KEY")
            if not self.api_key:
                raise ValueError("API_KEY environment variable not set")
        else:
            self.api_key = api_key
            
        # Get base URL from parameter or environment variables
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = os.getenv("BASE_URL", "https://api.openai.com/v1")
        
        # Get model from parameter or environment variables
        if model:
            self.model = model
        else:
            self.model = os.getenv("TEXT_MODEL", "gpt-4")
    
    def identify_page_type(self, text: str) -> Dict:
        """
        Identify the type of page (content, table of contents, references, etc.)
        
        Args:
            text: Text extracted from the page
            
        Returns:
            Dictionary with page type information
        """
        # prompt = """
        # 请根据页面文本的内容判断这个PDF页面的类型。可能的类型包括：
        # 1. 目录页 (table_of_contents) - 全部内容均为章节列表和页码, 且无其他类型内容
        # 2. 作者页 (author) - 全部内容均为作者信息, 且无其他类型内容
        # 3. 参考文献页 (references) - 全部内容均为引用的文献列表, 且无其他类型内容
        # 4. 内容页 (content) - 包含实际的医疗指南内容, 也许包含一些图片, 但图片内容与医疗指南内容有关
        
        # 请仅返回一个单词作为页面类型：table_of_contents、references 或 content
        # """
        prompt = page_type_classification_prompt_cn
        # Use text-based identification
        prompt += f"\n\n页面文本内容：\n{text[:1000]}..."  # Limit text length
        response = self._call_openai_api(prompt)
        
        # Extract page type from response
        if response.get("success", False):
            content = response.get("content", "").lower().strip()
            
            # Match the page type based on the enumeration values in the prompt
            if "cover" in content:
                page_type = "cover"
            elif "toc" in content:
                page_type = "toc"
            elif "reference" in content:
                page_type = "reference"
            elif "appendix" in content:
                page_type = "appendix"
            else:
                page_type = "content"  # Default to content if no specific match
            
            return {"success": True, "page_type": page_type}
        else:
            # Default to content if identification fails
            return {"success": False, "page_type": "content", "error": response.get("error")}
    
    def process_text(self, text: str) -> Dict:
        """
        Process text with OpenAI.
        
        Args:
            text: Text to process
            
        Returns:
            Dictionary containing the AI's response
        """
        # Prepare prompt for AI - specialized for precision medicine
        prompt = f"""
        请分析以下医疗文本，判断文字中是否能提供精准医疗相关的用药证据，即是否涉及某个基因或基因变异与特定肿瘤疾病在使用某种药物（或药物组合）后的疗效（敏感性/耐药性等）或疗效预测关系。

        文本内容：
        {text}

        如果是，请提取并输出如下结构化证据信息（未提及的字段请填 null）：
        - 相关基因（symbol）及变异（alteration）
        - 疾病的中文名和英文名
        - 药物中文名和英文名，及药物组合（如果有）
        - 证据等级（A/B/C/D）、响应性（敏感/耐药）、证据类型
            A1(FDA-approved therapies)
            A2(Professional guidelines)
            B(Well-powered studies with consensus)
            C1(Multiple small studies with some consensus)
            C2(inclusion criteria for CT)
            C3(A-evidence for a different Ca)
            D1(Cases)
            D2(Preclinical)

        输出格式为 JSON，包含以下字段：
        {
          "text": "原文提取的文本",
          "is_precision_evidence": true/false,
          "symbol": "基因符号",
          "alteration": "基因变异",
          "disease_name_cn": "疾病中文名",
          "disease_name_en": "疾病英文名",
          "drug_name_cn": "药物中文名",
          "drug_name_en": "药物英文名",
          "drug_combination": "药物组合",
          "evidence_level": "证据等级",
          "response_type": "敏感/耐药",
          "evidence_type": "证据类型"
        }

        如果该文本内容不涉及基因变异与疾病的药物疗效关系，请只返回：{"is_precision_evidence": false}
        """
        
        return self._call_openai_api(prompt)
    
    def process_image(self, image_path: str) -> Dict:
        """
        Process image with OpenAI.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing the AI's response
        """
        try:
            # Initialize OpenAI client with custom base URL if provided
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            # Read image file
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Prepare prompt for AI - specialized for precision medicine
            prompt = """
            请分析以下医疗图像，判断图像中是否能提供精准医疗相关的用药证据，即是否涉及某个基因或基因变异与特定肿瘤疾病在使用某种药物（或药物组合）后的疗效（敏感性/耐药性等）或疗效预测关系。

            如果是，请提取并输出如下结构化证据信息（未提及的字段请填 null）：
            - 相关基因（symbol）及变异（alteration）
            - 疾病的中文名和英文名
            - 药物中文名和英文名，及药物组合（如果有）
            - 证据等级（A/B/C/D）、响应性（敏感/耐药）、证据类型
                A1(FDA-approved therapies)
                A2(Professional guidelines)
                B(Well-powered studies with consensus)
                C1(Multiple small studies with some consensus)
                C2(inclusion criteria for CT)
                C3(A-evidence for a different Ca)
                D1(Cases)
                D2(Preclinical)

            输出格式为 JSON，包含以下字段：
            {
              "text": "原文提取的文本",
              "is_precision_evidence": true/false,
              "symbol": "基因符号",
              "alteration": "基因变异",
              "disease_name_cn": "疾病中文名",
              "disease_name_en": "疾病英文名",
              "drug_name_cn": "药物中文名",
              "drug_name_en": "药物英文名",
              "drug_combination": "药物组合",
              "evidence_level": "证据等级",
              "response_type": "敏感/耐药",
              "evidence_type": "证据类型"
            }

            如果该图像内容不涉及基因变异与疾病的药物疗效关系，请只返回：{"text": "原文提取的文本", "is_precision_evidence": false}
            """
            
            # Call the API with image
            response = client.chat.completions.create(
                model=self.model,  # Use the model specified in the constructor
                messages=[
                    {"role": "system", "content": "You are an expert in precision oncology and personalized cancer medicine, specializing in genetic alterations, targeted therapies, and evidence-based treatment recommendations."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}"}}
                    ]}
                ],
                temperature=0.1
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            
            # Try to parse JSON from content
            try:
                result = json.loads(content)
                return {"success": True, "content": content, **result}
            except json.JSONDecodeError:
                # If not valid JSON, return the raw content
                return {"success": True, "content": content}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Process PDF with OpenAI.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing the AI's response
        """
        try:
            # Initialize OpenAI client with custom base URL if provided
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            # Read PDF file
            with open(pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            
            # Prepare prompt for AI - specialized for precision medicine
            prompt = """
            请分析以下医疗PDF文档，判断文档中是否能提供精准医疗相关的用药证据，即是否涉及某个基因或基因变异与特定肿瘤疾病在使用某种药物（或药物组合）后的疗效（敏感性/耐药性等）或疗效预测关系。

            如果是，请提取并输出如下结构化证据信息（未提及的字段请填 null）：
            - 相关基因（symbol）及变异（alteration）
            - 疾病的中文名和英文名
            - 药物中文名和英文名，及药物组合（如果有）
            - 证据等级（A/B/C/D）、响应性（敏感/耐药）、证据类型
                A1(FDA-approved therapies)
                A2(Professional guidelines)
                B(Well-powered studies with consensus)
                C1(Multiple small studies with some consensus)
                C2(inclusion criteria for CT)
                C3(A-evidence for a different Ca)
                D1(Cases)
                D2(Preclinical)

            输出格式为 JSON，包含以下字段：
            {
              "text": "原文提取的文本",
              "is_precision_evidence": true/false,
              "symbol": "基因符号",
              "alteration": "基因变异",
              "disease_name_cn": "疾病中文名",
              "disease_name_en": "疾病英文名",
              "drug_name_cn": "药物中文名",
              "drug_name_en": "药物英文名",
              "drug_combination": "药物组合",
              "evidence_level": "证据等级",
              "response_type": "敏感/耐药",
              "evidence_type": "证据类型"
            }

            如果该文档内容不涉及基因变异与疾病的药物疗效关系，请只返回：{"is_precision_evidence": false}
            """
            
            # Call the API with PDF
            response = client.chat.completions.create(
                model=self.model,  # Use the model specified in the constructor
                messages=[
                    {"role": "system", "content": "You are an expert in precision oncology and personalized cancer medicine, specializing in genetic alterations, targeted therapies, and evidence-based treatment recommendations."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:application/pdf;base64,{base64.b64encode(pdf_data).decode('utf-8')}"}}
                    ]}
                ],
                temperature=0.1
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            
            # Try to parse JSON from content
            try:
                result = json.loads(content)
                return {"success": True, "content": content, **result}
            except json.JSONDecodeError:
                # If not valid JSON, return the raw content
                return {"success": True, "content": content}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _call_openai_api(self, prompt: str) -> Dict:
        """
        Call OpenAI API with the given prompt.
        
        Args:
            prompt: Prompt to send to OpenAI API
            
        Returns:
            Dictionary containing the API response
        """
        try:
            # Initialize OpenAI client with custom base URL if provided
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            # Call the API
            response = client.chat.completions.create(
                model=self.model,  # Use the model specified in the constructor
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specialized in medical text analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1  # Low temperature for more consistent results
            )
            
            # Extract and return the content
            content = response.choices[0].message.content
            return {"success": True, "content": content}
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return {"success": False, "error": str(e)}
