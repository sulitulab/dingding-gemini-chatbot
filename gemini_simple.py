#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版 Gemini 客户端 - 使用 REST API 直接调用
避免复杂的依赖版本问题
"""

import os
import time
import json
import logging
from typing import Optional

import requests
from google.auth import default
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

class SimpleGeminiClient:
    """简化版 Gemini AI 客户端"""
    
    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-1.5-flash"):
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
        self.credentials = None
        
    def initialize(self) -> bool:
        """
        初始化认证
        
        Returns:
            bool: 是否初始化成功
        """
        try:
            # 获取默认认证
            self.credentials, _ = default()
            
            # 测试认证
            self.credentials.refresh(Request())
            
            logger.info(f"Gemini 客户端初始化成功，模型: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Gemini 客户端初始化失败: {e}")
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
        if not self.credentials:
            return "AI服务未初始化，请稍后再试。"
        
        try:
            # 开始计时
            start_time = time.time()
            
            # 刷新认证令牌
            self.credentials.refresh(Request())
            
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
                },
                "safety_settings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            # 发送请求
            headers = {
                "Authorization": f"Bearer {self.credentials.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # 结束计时
            end_time = time.time()
            response_time = end_time - start_time
            
            # 解析响应
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        logger.info(f"Gemini响应成功，耗时: {response_time:.2f}秒")
                        return parts[0]["text"].strip()
            
            logger.warning("Gemini返回空响应")
            return "抱歉，我无法处理这个问题，请换个方式提问。"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"
        except Exception as e:
            logger.error(f"调用 Gemini 模型失败: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"

# 全局简单客户端实例
_simple_gemini_client: Optional[SimpleGeminiClient] = None

def get_simple_gemini_client() -> Optional[SimpleGeminiClient]:
    """获取全局简单 Gemini 客户端实例"""
    return _simple_gemini_client

def initialize_simple_gemini_client(project_id: str, location: str = "us-central1", model_name: str = "gemini-1.5-flash") -> bool:
    """
    初始化全局简单 Gemini 客户端
    
    Args:
        project_id: GCP项目ID
        location: 区域
        model_name: 模型名称
        
    Returns:
        bool: 是否初始化成功
    """
    global _simple_gemini_client
    
    try:
        _simple_gemini_client = SimpleGeminiClient(project_id, location, model_name)
        return _simple_gemini_client.initialize()
    except Exception as e:
        logger.error(f"初始化简单 Gemini 客户端失败: {e}")
        return False