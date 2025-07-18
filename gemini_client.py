#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GCP Vertex AI 集成模块
"""

import os
import time
import logging
from typing import Optional

try:
    # 尝试新版本的导入方式
    import vertexai
    from vertexai.generative_models import GenerativeModel, ChatSession
    USE_VERTEXAI = True
except ImportError:
    try:
        # 尝试旧版本的导入方式
        from google.cloud import aiplatform
        from google.cloud.aiplatform.gapic.schema import predict
        USE_VERTEXAI = False
    except ImportError:
        raise ImportError("请安装 vertexai 或 google-cloud-aiplatform 包")

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini AI 客户端"""
    
    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-2.5-flash"):
        """
        初始化 Gemini 客户端
        
        Args:
            project_id: GCP项目ID
            location: 区域
            model_name: 模型名称
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.model: Optional[GenerativeModel] = None
        self.chat_session: Optional[ChatSession] = None
        
    def initialize(self) -> bool:
        """
        初始化 Vertex AI 和模型
        
        Returns:
            bool: 是否初始化成功
        """
        try:
            if USE_VERTEXAI:
                # 使用新版本 vertexai
                vertexai.init(
                    project=self.project_id,
                    location=self.location
                )
                self.model = GenerativeModel(self.model_name)
            else:
                # 使用旧版本 google-cloud-aiplatform
                from google.cloud import aiplatform
                aiplatform.init(
                    project=self.project_id,
                    location=self.location
                )
                # 旧版本不支持 GenerativeModel，需要使用不同的方法
                self.model = None
            
            logger.info(f"Vertex AI 初始化成功，模型: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Vertex AI 初始化失败: {e}")
            return False
    
    def generate_content(
        self, 
        prompt: str, 
        temperature: float = 0.3,
        top_p: float = 0.8,
        top_k: int = 40,
        max_output_tokens: int = 1000
    ) -> str:
        """
        生成内容
        
        Args:
            prompt: 输入提示
            temperature: 温度参数
            top_p: top_p参数
            top_k: top_k参数
            max_output_tokens: 最大输出token数
            
        Returns:
            str: 生成的内容
        """
        try:
            # 开始计时
            start_time = time.time()
            
            if USE_VERTEXAI and self.model:
                # 使用新版本 vertexai
                generation_config = {
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "max_output_tokens": max_output_tokens,
                }
                
                safety_settings = {
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
                }
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                
                if response.text:
                    end_time = time.time()
                    response_time = end_time - start_time
                    logger.info(f"Gemini响应成功，耗时: {response_time:.2f}秒")
                    return response.text.strip()
                else:
                    logger.warning("Gemini返回空响应")
                    return "抱歉，我无法处理这个问题，请换个方式提问。"
            else:
                # 使用旧版本方式或降级处理
                return self._generate_content_legacy(prompt, temperature, top_p, top_k, max_output_tokens)
                
        except Exception as e:
            logger.error(f"调用 Gemini 模型失败: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"
    
    def _generate_content_legacy(self, prompt: str, temperature: float, top_p: float, top_k: int, max_output_tokens: int) -> str:
        """
        使用旧版本API生成内容
        """
        try:
            import requests
            import json
            
            # 使用 REST API 调用
            from google.auth import default
            from google.auth.transport.requests import Request
            
            # 获取认证
            credentials, project_id = default()
            credentials.refresh(Request())
            
            # 构建API URL
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}:generateContent"
            
            # 构建请求数据
            data = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": prompt}]
                }],
                "generation_config": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "max_output_tokens": max_output_tokens
                }
            }
            
            # 发送请求
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # 解析响应
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"].strip()
            
            return "抱歉，我无法处理这个问题，请换个方式提问。"
            
        except Exception as e:
            logger.error(f"使用旧版本API调用失败: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"
    
    def start_chat(self) -> bool:
        """
        开始聊天会话
        
        Returns:
            bool: 是否成功
        """
        if not self.model:
            logger.error("模型未初始化")
            return False
        
        try:
            self.chat_session = self.model.start_chat()
            logger.info("聊天会话创建成功")
            return True
        except Exception as e:
            logger.error(f"创建聊天会话失败: {e}")
            return False
    
    def send_message(self, message: str) -> str:
        """
        发送消息到聊天会话
        
        Args:
            message: 消息内容
            
        Returns:
            str: 回复内容
        """
        if not self.chat_session:
            logger.warning("聊天会话未创建，使用单次生成")
            return self.generate_content(message)
        
        try:
            start_time = time.time()
            
            response = self.chat_session.send_message(message)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.text:
                logger.info(f"聊天回复成功，耗时: {response_time:.2f}秒")
                return response.text.strip()
            else:
                logger.warning("聊天回复为空")
                return "抱歉，我无法处理这个问题，请换个方式提问。"
                
        except Exception as e:
            logger.error(f"发送聊天消息失败: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"
    
    def reset_chat(self):
        """重置聊天会话"""
        self.chat_session = None
        logger.info("聊天会话已重置")

# 全局 Gemini 客户端实例
_gemini_client: Optional[GeminiClient] = None

def get_gemini_client() -> Optional[GeminiClient]:
    """获取全局 Gemini 客户端实例"""
    return _gemini_client

def initialize_gemini_client(project_id: str, location: str = "us-central1", model_name: str = "gemini-2.5-flash") -> bool:
    """
    初始化全局 Gemini 客户端
    
    Args:
        project_id: GCP项目ID
        location: 区域
        model_name: 模型名称
        
    Returns:
        bool: 是否初始化成功
    """
    global _gemini_client
    
    try:
        _gemini_client = GeminiClient(project_id, location, model_name)
        return _gemini_client.initialize()
    except Exception as e:
        logger.error(f"初始化 Gemini 客户端失败: {e}")
        return False