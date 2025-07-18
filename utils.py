#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人工具函数
"""

import os
import json
import hmac
import hashlib
import base64
import logging
from typing import Dict, Any, Optional, List

import requests

logger = logging.getLogger(__name__)

def verify_dingtalk_signature(timestamp: str, secret: str, sign: str) -> bool:
    """
    验证钉钉webhook签名
    
    Args:
        timestamp: 时间戳
        secret: 机器人密钥
        sign: 签名
        
    Returns:
        bool: 签名是否有效
    """
    if not secret:
        logger.warning("未配置钉钉webhook密钥，跳过签名验证")
        return True
    
    try:
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        expected_sign = base64.b64encode(hmac_code).decode('utf-8')
        
        return hmac.compare_digest(sign, expected_sign)
    except Exception as e:
        logger.error(f"签名验证失败: {e}")
        return False

def send_dingtalk_message(
    webhook_url: str, 
    message: str, 
    at_mobiles: Optional[List[str]] = None, 
    at_userids: Optional[List[str]] = None,
    is_at_all: bool = False
) -> bool:
    """
    发送消息到钉钉群
    
    Args:
        webhook_url: 钉钉webhook URL
        message: 消息内容
        at_mobiles: @手机号列表
        at_userids: @用户ID列表
        is_at_all: 是否@所有人
        
    Returns:
        bool: 发送是否成功
    """
    try:
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        # 添加@功能
        if at_mobiles or at_userids or is_at_all:
            data["at"] = {
                "atMobiles": at_mobiles or [],
                "atUserIds": at_userids or [],
                "isAtAll": is_at_all
            }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            webhook_url, 
            json=data, 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("errcode") == 0:
            logger.info("消息发送成功")
            return True
        else:
            logger.error(f"消息发送失败: {result}")
            return False
            
    except Exception as e:
        logger.error(f"发送钉钉消息失败: {e}")
        return False

def parse_at_users(content: str) -> str:
    """
    解析并清理@用户的文本
    
    Args:
        content: 原始消息内容
        
    Returns:
        str: 清理后的消息内容
    """
    import re
    
    # 移除@用户的文本
    clean_content = re.sub(r'@\w+\s*', '', content).strip()
    
    # 移除多余的空白字符
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    
    return clean_content

def format_error_message(error: Exception) -> str:
    """
    格式化错误消息
    
    Args:
        error: 异常对象
        
    Returns:
        str: 格式化后的错误消息
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    return f"[{error_type}] {error_message}"

def validate_webhook_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    验证webhook数据格式
    
    Args:
        data: webhook数据
        
    Returns:
        tuple: (是否有效, 错误消息)
    """
    if not isinstance(data, dict):
        return False, "数据格式不正确"
    
    msg_type = data.get('msgtype')
    if msg_type != 'text':
        return False, f"不支持的消息类型: {msg_type}"
    
    text_data = data.get('text', {})
    if not isinstance(text_data, dict):
        return False, "文本数据格式不正确"
    
    content = text_data.get('content', '').strip()
    if not content:
        return False, "消息内容为空"
    
    webhook_url = data.get('sessionWebhook', '')
    if not webhook_url:
        return False, "缺少webhook URL"
    
    return True, ""

def truncate_text(text: str, max_length: int = 2000) -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."