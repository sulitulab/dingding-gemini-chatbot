#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人消息发送工具
基于官方demo修改，集成Gemini AI
"""

import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import logging
from datetime import datetime
from typing import Optional, List

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)


class DingTalkBot:
    """钉钉机器人消息发送类"""
    
    def __init__(self, access_token: str, secret: str = ""):
        """
        初始化钉钉机器人
        
        Args:
            access_token: 机器人webhook的access_token
            secret: 机器人安全设置的加签secret（可选）
        """
        self.access_token = access_token
        self.secret = secret
    
    def send_message(
        self, 
        msg: str, 
        at_user_ids: Optional[List[str]] = None,
        at_mobiles: Optional[List[str]] = None,
        is_at_all: bool = False
    ) -> dict:
        """
        发送钉钉自定义机器人群消息
        
        Args:
            msg: 消息内容
            at_user_ids: @的用户ID列表
            at_mobiles: @的手机号列表
            is_at_all: 是否@所有人
            
        Returns:
            dict: 钉钉API响应
        """
        try:
            # 构建请求URL
            url = f'https://oapi.dingtalk.com/robot/send?access_token={self.access_token}'
            
            # 如果有secret，添加签名
            if self.secret:
                timestamp = str(round(time.time() * 1000))
                string_to_sign = f'{timestamp}\n{self.secret}'
                hmac_code = hmac.new(
                    self.secret.encode('utf-8'), 
                    string_to_sign.encode('utf-8'), 
                    digestmod=hashlib.sha256
                ).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                url += f'&timestamp={timestamp}&sign={sign}'
            
            # 构建消息体
            body = {
                "at": {
                    "isAtAll": is_at_all,
                    "atUserIds": at_user_ids or [],
                    "atMobiles": at_mobiles or []
                },
                "text": {
                    "content": msg
                },
                "msgtype": "text"
            }
            
            # 发送请求
            headers = {'Content-Type': 'application/json'}
            resp = requests.post(url, json=body, headers=headers, timeout=10)
            resp.raise_for_status()
            
            result = resp.json()
            logger.info("钉钉消息发送成功：%s", result)
            return result
            
        except Exception as e:
            logger.error("钉钉消息发送失败：%s", e)
            return {"errcode": -1, "errmsg": str(e)}


class GeminiClient:
    """简化版Gemini客户端"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.model_name = "gemini-1.5-flash"
        self.credentials = None
    
    def initialize(self) -> bool:
        """初始化认证"""
        try:
            from google.auth import default
            from google.auth.transport.requests import Request
            
            self.credentials, _ = default()
            self.credentials.refresh(Request())
            
            logger.info("Gemini客户端初始化成功")
            return True
        except Exception as e:
            logger.error("Gemini客户端初始化失败：%s", e)
            return False
    
    def generate_content(self, prompt: str) -> str:
        """生成AI回复"""
        if not self.credentials:
            return "AI服务未初始化"
        
        try:
            from google.auth.transport.requests import Request
            
            # 刷新令牌
            self.credentials.refresh(Request())
            
            # 构建API请求
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}:generateContent"
            
            data = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": prompt}]
                }],
                "generation_config": {
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1000
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.token}",
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
            
            return "抱歉，我无法处理这个问题。"
            
        except Exception as e:
            logger.error("调用Gemini失败：%s", e)
            return "抱歉，AI服务暂时不可用。"


def main():
    """主函数 - 演示如何使用"""
    # 从环境变量获取配置
    access_token = os.getenv('DINGTALK_ACCESS_TOKEN')
    secret = os.getenv('DINGTALK_SECRET', '')
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    
    if not access_token:
        logger.error("请设置 DINGTALK_ACCESS_TOKEN 环境变量")
        return
    
    if not gcp_project_id:
        logger.error("请设置 GCP_PROJECT_ID 环境变量")
        return
    
    # 初始化钉钉机器人
    bot = DingTalkBot(access_token, secret)
    
    # 初始化Gemini客户端
    gemini = GeminiClient(gcp_project_id)
    if not gemini.initialize():
        logger.error("Gemini初始化失败")
        return
    
    # 示例：发送AI回复
    question = "请简单介绍一下人工智能"
    
    logger.info("向AI提问：%s", question)
    ai_response = gemini.generate_content(question)
    
    logger.info("AI回复：%s", ai_response)
    
    # 发送到钉钉群
    result = bot.send_message(
        msg=f"🤖 AI助手回复：\n\n{ai_response}",
        is_at_all=False  # 可以根据需要@特定用户
    )
    
    if result.get("errcode") == 0:
        logger.info("消息发送成功！")
    else:
        logger.error("消息发送失败：%s", result.get("errmsg"))


if __name__ == '__main__':
    main()