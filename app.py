#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人Webhook处理应用
基于Flask框架，集成GCP Vertex AI Gemini-2.5-Flash模型
"""

import os
import json
import hmac
import hashlib
import base64
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

import requests
from flask import Flask, request, jsonify
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置参数
class Config:
    # 钉钉机器人配置
    DINGTALK_WEBHOOK_SECRET = os.getenv('DINGTALK_WEBHOOK_SECRET', '')
    DINGTALK_BOT_TOKEN = os.getenv('DINGTALK_BOT_TOKEN', '')
    
    # GCP Vertex AI 配置
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', '')
    GCP_LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
    MODEL_NAME = 'gemini-2.5-flash'
    
    # 应用配置
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

config = Config()

# 全局变量存储模型实例
model = None

# 初始化 Vertex AI
def init_vertex_ai():
    """初始化 Vertex AI 客户端"""
    global model
    try:
        # 初始化 Vertex AI
        aiplatform.init(
            project=config.GCP_PROJECT_ID, 
            location=config.GCP_LOCATION
        )
        
        # 创建生成模型实例
        model = GenerativeModel(config.MODEL_NAME)
        
        logger.info("Vertex AI 初始化成功")
    except Exception as e:
        logger.error(f"Vertex AI 初始化失败: {e}")
        raise

# 钉钉签名验证
def verify_dingtalk_signature(timestamp: str, secret: str, sign: str) -> bool:
    """验证钉钉webhook签名"""
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

# 与 Gemini 模型对话
def chat_with_gemini(question: str) -> str:
    """调用 Gemini-2.5-Flash 模型处理问题"""
    global model
    
    if not model:
        logger.error("Gemini模型未初始化")
        return "抱歉，AI服务暂时不可用，请稍后再试。"
    
    try:
        # 开始计时
        start_time = time.time()
        
        # 生成配置 - 关闭CoT，追求快速响应
        generation_config = {
            "temperature": 0.3,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1000,
            "response_mime_type": "text/plain"
        }
        
        # 安全设置
        safety_settings = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE", 
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        }
        
        # 调用模型生成响应
        response = model.generate_content(
            question,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # 结束计时
        end_time = time.time()
        response_time = end_time - start_time
        
        # 检查响应
        if response.text:
            logger.info(f"Gemini响应成功，耗时: {response_time:.2f}秒")
            return response.text.strip()
        else:
            logger.warning("Gemini返回空响应")
            return "抱歉，我无法处理这个问题，请换个方式提问。"
        
    except Exception as e:
        logger.error(f"调用 Gemini 模型失败: {e}")
        return "抱歉，AI服务暂时不可用，请稍后再试。"

# 发送钉钉消息
def send_dingtalk_message(webhook_url: str, message: str, at_mobiles: list = None, at_userids: list = None):
    """发送消息到钉钉群"""
    try:
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        # 添加@功能
        if at_mobiles or at_userids:
            data["at"] = {
                "atMobiles": at_mobiles or [],
                "atUserIds": at_userids or [],
                "isAtAll": False
            }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(webhook_url, json=data, headers=headers, timeout=10)
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

# 处理钉钉webhook消息
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """处理钉钉webhook消息"""
    try:
        # 验证签名
        timestamp = request.headers.get('timestamp', '')
        sign = request.headers.get('sign', '')
        
        if not verify_dingtalk_signature(timestamp, config.DINGTALK_WEBHOOK_SECRET, sign):
            logger.warning("签名验证失败")
            return jsonify({"error": "签名验证失败"}), 401
        
        # 解析请求数据
        data = request.get_json()
        if not data:
            logger.warning("无效的请求数据")
            return jsonify({"error": "无效的请求数据"}), 400
        
        logger.info(f"收到钉钉webhook消息: {json.dumps(data, ensure_ascii=False)}")
        
        # 检查是否是文本消息且包含机器人被@的情况
        msg_type = data.get('msgtype')
        if msg_type != 'text':
            logger.info("忽略非文本消息")
            return jsonify({"success": True})
        
        # 获取消息内容
        text_data = data.get('text', {})
        content = text_data.get('content', '').strip()
        
        # 检查是否@了机器人
        at_data = data.get('atUsers', [])
        webhook_url = data.get('sessionWebhook', '')
        
        if not content or not webhook_url:
            logger.warning("消息内容或webhook URL为空")
            return jsonify({"error": "消息内容或webhook URL为空"}), 400
        
        # 提取问题内容（移除@机器人的部分）
        question = content
        # 移除可能的@机器人文本
        if '@' in question:
            # 简单的@文本清理
            import re
            question = re.sub(r'@\w+\s*', '', question).strip()
        
        if not question:
            logger.info("消息内容为空，发送帮助信息")
            help_message = "您好！我是AI助手，请问有什么可以帮助您的吗？"
            send_dingtalk_message(webhook_url, help_message)
            return jsonify({"success": True})
        
        # 调用AI模型处理问题
        logger.info(f"处理问题: {question}")
        ai_response = chat_with_gemini(question)
        
        # 获取发送者信息，用于@回复
        sender_info = data.get('senderStaffId', '')
        at_userids = [sender_info] if sender_info else []
        
        # 发送回复消息
        if send_dingtalk_message(webhook_url, ai_response, at_userids=at_userids):
            logger.info("回复消息发送成功")
        else:
            logger.error("回复消息发送失败")
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"处理webhook消息失败: {e}")
        return jsonify({"error": "内部服务器错误"}), 500

# 健康检查接口
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "model": config.MODEL_NAME
    })

# 测试接口
@app.route('/test', methods=['GET'])
def test_endpoint():
    """测试接口"""
    test_question = request.args.get('q', '你好')
    response = chat_with_gemini(test_question)
    return jsonify({
        "question": test_question,
        "response": response,
        "timestamp": datetime.now().isoformat()
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "接口不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"内部服务器错误: {error}")
    return jsonify({"error": "内部服务器错误"}), 500

if __name__ == '__main__':
    # 初始化 Vertex AI
    init_vertex_ai()
    
    # 启动应用
    logger.info(f"启动钉钉机器人webhook服务，端口: {config.PORT}")
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)