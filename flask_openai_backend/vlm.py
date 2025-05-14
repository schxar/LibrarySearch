import os
import base64
import traceback
from openai import OpenAI
from flask import jsonify

class VLMService:
    def __init__(self):
        """初始化VLM客户端"""
        self.client = OpenAI(
            api_key=os.environ.get("ARK_API_KEY"),
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )
        self.model_name = "doubao-1-5-thinking-vision-pro-250428"

    def analyze_image(self, image_data: str, prompt: str = "请描述这张图片的内容"):
        """
        分析图片内容
        :param image_data: base64编码的图片数据
        :param prompt: 分析提示词
        :return: 分析结果
        """
        if not image_data.startswith("data:image/"):
            raise ValueError("Invalid DATAURI format")
            
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                max_tokens=1024,
                timeout=30
            )
            
            if not response.choices or not response.choices[0].message.content:
                return {"error": "图片分析服务返回空结果"}
                
            return {
                "content": response.choices[0].message.content,
                "is_image_response": True
            }
            
        except Exception as e:
            return {
                "error": f"图片处理失败: {str(e)}",
                "traceback": traceback.format_exc()
            }

    def validate_image(self, file):
        """
        验证图片文件
        :param file: 上传的文件对象
        :return: 验证结果或base64编码的图片数据
        """
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return {"error": "仅支持PNG/JPG/JPEG/GIF格式的图片"}
            
        # 验证文件大小(不超过5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        if file_size > 5 * 1024 * 1024:
            return {"error": "图片大小不能超过5MB"}
        file.seek(0)
        
        # 编码图片
        image_base64 = base64.b64encode(file.read()).decode('utf-8')
        if not image_base64 or len(image_base64) < 100:
            return {"error": "图片编码失败"}
            
        return {
            "data": f"data:{file.content_type};base64,{image_base64}",
            "content_type": file.content_type
        }

# 全局VLM服务实例
vlm_service = VLMService()
