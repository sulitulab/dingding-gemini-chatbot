#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的钉钉机器人对话系统
1. 接收钉钉发送的用户消息
2. 调用Gemini处理消息
3. 将响应发送到钉钉机器人webhook
"""

import os
import json
import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, List

import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)


class DingTalkBot:
    """钉钉机器人消息发送类"""
    
    def __init__(self, access_token: str, secret: str = ""):
        self.access_token = access_token
        self.secret = secret
    
    def send_message(
        self, 
        msg: str, 
        at_user_ids: Optional[List[str]] = None,
        at_mobiles: Optional[List[str]] = None,
        is_at_all: bool = False
    ) -> dict:
        """发送消息到钉钉群"""
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
            logger.info("钉钉消息发送成功")
            return result
            
        except Exception as e:
            logger.error(f"钉钉消息发送失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}


class GeminiClient:
    """Gemini AI客户端"""
    
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
            logger.error(f"Gemini客户端初始化失败: {e}")
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
            
            start_time = time.time()
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            response_time = time.time() - start_time
            
            # 解析响应
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        logger.info(f"Gemini响应成功，耗时: {response_time:.2f}秒")
                        return parts[0]["text"].strip()
            
            return "抱歉，我无法处理这个问题。"
            
        except Exception as e:
            logger.error(f"调用Gemini失败: {e}")
            return "抱歉，AI服务暂时不可用。"


# 全局实例
dingtalk_bot = None
gemini_client = None


def init_services():
    """初始化服务"""
    global dingtalk_bot, gemini_client
    
    # 初始化钉钉机器人
    access_token = os.getenv('DINGTALK_ACCESS_TOKEN')
    secret = os.getenv('DINGTALK_SECRET', '')
    
    if not access_token:
        logger.error("请设置 DINGTALK_ACCESS_TOKEN 环境变量")
        return False
    
    dingtalk_bot = DingTalkBot(access_token, secret)
    logger.info("钉钉机器人初始化成功")
    
    # 初始化Gemini客户端
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    if not gcp_project_id:
        logger.error("请设置 GCP_PROJECT_ID 环境变量")
        return False
    
    gemini_client = GeminiClient(gcp_project_id)
    if not gemini_client.initialize():
        logger.error("Gemini客户端初始化失败")
        return False
    
    return True


def extract_user_message(data: Dict[str, Any]) -> str:
    """从钉钉请求中提取用户消息"""
    try:
        # 获取消息内容
        text_data = data.get('text', {})
        content = text_data.get('content', '').strip()
        
        if not content:
            return ""
        
        # 移除@机器人的部分
        import re
        # 移除@符号后的内容（通常是机器人名称）
        clean_content = re.sub(r'@\w+\s*', '', content).strip()
        
        # 移除多余的空白字符
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        return clean_content
        
    except Exception as e:
        logger.error(f"提取用户消息失败: {e}")
        return ""


def get_at_user_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """获取需要@的用户信息"""
    try:
        # 获取发送者信息
        sender_staff_id = data.get('senderStaffId', '')
        sender_nick = data.get('senderNick', '')
        
        # 获取@用户信息
        at_users = data.get('atUsers', [])
        
        at_user_ids = []
        at_mobiles = []
        
        # 添加发送者到@列表
        if sender_staff_id:
            at_user_ids.append(sender_staff_id)
        
        # 添加其他@用户
        for user in at_users:
            user_id = user.get('dingtalkId', '')
            if user_id and user_id not in at_user_ids:
                at_user_ids.append(user_id)
        
        return {
            'at_user_ids': at_user_ids,
            'at_mobiles': at_mobiles,
            'sender_nick': sender_nick
        }
        
    except Exception as e:
        logger.error(f"获取@用户信息失败: {e}")
        return {'at_user_ids': [], 'at_mobiles': [], 'sender_nick': ''}


@app.route('/webhook', methods=['POST'])
def handle_dingtalk_webhook():
    """处理钉钉机器人webhook请求"""
    try:
        # 1. 接收钉钉发送的消息
        data = request.get_json()
        if not data:
            logger.warning("收到空的请求数据")
            return jsonify({"error": "无效的请求数据"}), 400
        
        logger.info("收到钉钉webhook请求")
        logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
        
        # 检查消息类型
        msg_type = data.get('msgtype')
        if msg_type != 'text':
            logger.info(f"忽略非文本消息类型: {msg_type}")
            return jsonify({"success": True})
        
        # 2. 提取用户消息
        user_message = extract_user_message(data)
        if not user_message:
            logger.warning("提取到空的用户消息")
            # 发送帮助信息
            help_msg = "您好！我是AI助手，请@我并发送您的问题。"
            dingtalk_bot.send_message(help_msg)
            return jsonify({"success": True})
        
        logger.info(f"提取到用户消息: {user_message}")
        
        # 获取@用户信息
        at_info = get_at_user_info(data)
        
        # 3. 调用Gemini处理消息
        logger.info("调用Gemini处理消息...")
        ai_response = gemini_client.generate_content(user_message)
        logger.info(f"Gemini响应: {ai_response}")
        
        # 4. 发送响应到钉钉机器人webhook
        # 构建回复消息
        if at_info['sender_nick']:
            reply_message = f"@{at_info['sender_nick']} {ai_response}"
        else:
            reply_message = ai_response
        
        logger.info("发送响应到钉钉群...")
        result = dingtalk_bot.send_message(
            msg=reply_message,
            at_user_ids=at_info['at_user_ids']
        )
        
        if result.get("errcode") == 0:
            logger.info("消息发送成功")
            return jsonify({"success": True})
        else:
            logger.error(f"消息发送失败: {result.get('errmsg')}")
            return jsonify({"error": "消息发送失败"}), 500
    
    except Exception as e:
        logger.error(f"处理webhook请求失败: {e}")
        return jsonify({"error": "内部服务器错误"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    global dingtalk_bot, gemini_client
    
    dingtalk_status = "ready" if dingtalk_bot else "not_ready"
    gemini_status = "ready" if gemini_client else "not_ready"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "dingtalk": dingtalk_status,
            "gemini": gemini_status
        }
    })


@app.route('/test', methods=['GET'])
def test_endpoint():
    """测试接口"""
    test_message = request.args.get('msg', '你好')
    
    if not gemini_client:
        return jsonify({"error": "Gemini客户端未初始化"}), 503
    
    # 测试Gemini
    ai_response = gemini_client.generate_content(test_message)
    
    # 测试发送到钉钉
    if dingtalk_bot:
        result = dingtalk_bot.send_message(f"🧪 测试消息: {ai_response}")
        send_status = "success" if result.get("errcode") == 0 else "failed"
    else:
        send_status = "dingtalk_not_ready"
    
    return jsonify({
        "test_message": test_message,
        "ai_response": ai_response,
        "send_status": send_status,
        "timestamp": datetime.now().isoformat()
    })


if __name__ == '__main__':
    # 初始化服务
    if not init_services():
        logger.error("服务初始化失败")
        exit(1)
    
    # 启动Flask应用
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"启动钉钉机器人服务，端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)