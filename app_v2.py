#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版钉钉机器人Webhook处理应用
使用模块化架构，提供更好的可维护性和扩展性
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from config import get_config
from utils import (
    verify_dingtalk_signature, 
    send_dingtalk_message, 
    parse_at_users, 
    validate_webhook_data,
    truncate_text
)
from gemini_client import initialize_gemini_client, get_gemini_client

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(get_config())

# 配置日志
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 Gemini 客户端
def init_ai_client():
    """初始化AI客户端"""
    try:
        success = initialize_gemini_client(
            project_id=app.config['GCP_PROJECT_ID'],
            location=app.config['GCP_LOCATION'],
            model_name=app.config['MODEL_NAME']
        )
        
        if success:
            logger.info("AI客户端初始化成功")
        else:
            logger.error("AI客户端初始化失败")
            
        return success
    except Exception as e:
        logger.error(f"AI客户端初始化异常: {e}")
        return False

# 处理钉钉webhook消息
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """处理钉钉webhook消息"""
    try:
        # 验证签名
        timestamp = request.headers.get('timestamp', '')
        sign = request.headers.get('sign', '')
        
        if not verify_dingtalk_signature(
            timestamp, 
            app.config['DINGTALK_WEBHOOK_SECRET'], 
            sign
        ):
            logger.warning("签名验证失败")
            return jsonify({"error": "签名验证失败"}), 401
        
        # 解析请求数据
        data = request.get_json()
        if not data:
            logger.warning("无效的请求数据")
            return jsonify({"error": "无效的请求数据"}), 400
        
        logger.info(f"收到钉钉webhook消息")
        logger.debug(f"消息详情: {json.dumps(data, ensure_ascii=False)}")
        
        # 验证数据格式
        is_valid, error_msg = validate_webhook_data(data)
        if not is_valid:
            logger.warning(f"数据验证失败: {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # 获取消息内容
        text_data = data.get('text', {})
        content = text_data.get('content', '').strip()
        webhook_url = data.get('sessionWebhook', '')
        
        # 解析并清理@用户的文本
        question = parse_at_users(content)
        
        if not question:
            logger.info("消息内容为空，发送帮助信息")
            help_message = "您好！我是AI助手，请问有什么可以帮助您的吗？"
            send_dingtalk_message(webhook_url, help_message)
            return jsonify({"success": True})
        
        # 获取AI客户端
        gemini_client = get_gemini_client()
        if not gemini_client:
            logger.error("AI客户端未初始化")
            error_message = "抱歉，AI服务暂时不可用，请稍后再试。"
            send_dingtalk_message(webhook_url, error_message)
            return jsonify({"error": "AI服务不可用"}), 503
        
        # 调用AI模型处理问题
        logger.info(f"处理问题: {question}")
        ai_response = gemini_client.generate_content(question)
        
        # 截断过长的回复
        ai_response = truncate_text(ai_response, 2000)
        
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
    gemini_client = get_gemini_client()
    ai_status = "ready" if gemini_client else "not_ready"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "model": app.config['MODEL_NAME'],
        "ai_status": ai_status
    })

# 测试接口
@app.route('/test', methods=['GET'])
def test_endpoint():
    """测试接口"""
    test_question = request.args.get('q', '你好')
    
    gemini_client = get_gemini_client()
    if not gemini_client:
        return jsonify({
            "error": "AI客户端未初始化",
            "timestamp": datetime.now().isoformat()
        }), 503
    
    response = gemini_client.generate_content(test_question)
    
    return jsonify({
        "question": test_question,
        "response": response,
        "timestamp": datetime.now().isoformat()
    })

# 配置信息接口
@app.route('/info', methods=['GET'])
def info_endpoint():
    """配置信息接口"""
    return jsonify({
        "project_id": app.config['GCP_PROJECT_ID'],
        "location": app.config['GCP_LOCATION'],
        "model": app.config['MODEL_NAME'],
        "version": "1.0.0",
        "debug": app.config['DEBUG']
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "接口不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"内部服务器错误: {error}")
    return jsonify({"error": "内部服务器错误"}), 500

@app.errorhandler(503)
def service_unavailable(error):
    logger.error(f"服务不可用: {error}")
    return jsonify({"error": "服务暂时不可用"}), 503

if __name__ == '__main__':
    # 初始化AI客户端
    if not init_ai_client():
        logger.error("AI客户端初始化失败，应用将无法正常工作")
        exit(1)
    
    # 启动应用
    logger.info(f"启动钉钉机器人webhook服务，端口: {app.config['PORT']}")
    app.run(
        host='0.0.0.0', 
        port=app.config['PORT'], 
        debug=app.config['DEBUG']
    )