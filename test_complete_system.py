#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整钉钉机器人系统测试脚本
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def test_health_check():
    """测试健康检查"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ 健康检查通过")
            print(f"   钉钉状态: {result['services']['dingtalk']}")
            print(f"   Gemini状态: {result['services']['gemini']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_ai_functionality():
    """测试AI功能"""
    try:
        response = requests.get(
            "http://localhost:5000/test", 
            params={"msg": "你好，请简单介绍一下你自己"}, 
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ AI功能测试通过")
            print(f"   测试消息: {result['test_message']}")
            print(f"   AI回复: {result['ai_response']}")
            print(f"   发送状态: {result['send_status']}")
            return True
        else:
            print(f"❌ AI功能测试失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI功能测试异常: {e}")
        return False

def test_webhook_simulation():
    """模拟钉钉webhook请求"""
    try:
        # 模拟钉钉发送的消息
        webhook_data = {
            "msgtype": "text",
            "text": {
                "content": "@机器人 什么是人工智能？"
            },
            "senderStaffId": "test_user_123",
            "senderNick": "测试用户",
            "atUsers": [
                {
                    "dingtalkId": "test_user_123",
                    "staffId": "test_user_123"
                }
            ]
        }
        
        print("📝 模拟钉钉webhook请求...")
        print(f"   请求数据: {json.dumps(webhook_data, ensure_ascii=False)}")
        
        response = requests.post(
            "http://localhost:5000/webhook",
            json=webhook_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook模拟测试通过")
            print(f"   响应: {result}")
            return True
        else:
            print(f"❌ Webhook模拟测试失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook模拟测试异常: {e}")
        return False

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    required_vars = [
        'DINGTALK_ACCESS_TOKEN',
        'GCP_PROJECT_ID',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要环境变量: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ 环境变量配置正确")
        return True

def main():
    """主测试函数"""
    print("🚀 完整钉钉机器人系统测试")
    print("=" * 50)
    
    # 检查环境配置
    if not check_environment():
        print("❌ 环境配置检查失败，请检查 .env 文件")
        return 1
    
    print()
    print("📡 测试系统各个组件...")
    print("请确保应用正在运行 (python complete_bot.py)")
    print()
    
    # 测试健康检查
    health_ok = test_health_check()
    print()
    
    # 测试AI功能
    ai_ok = test_ai_functionality()
    print()
    
    # 测试webhook模拟
    webhook_ok = test_webhook_simulation()
    print()
    
    # 总结
    print("=" * 50)
    print("📊 测试结果总结:")
    print(f"   健康检查: {'✅' if health_ok else '❌'}")
    print(f"   AI功能: {'✅' if ai_ok else '❌'}")
    print(f"   Webhook处理: {'✅' if webhook_ok else '❌'}")
    
    if health_ok and ai_ok and webhook_ok:
        print("\n🎉 所有测试通过！系统工作正常")
        print("\n📋 下一步:")
        print("1. 确保服务运行在公网可访问的地址")
        print("2. 在钉钉机器人中配置 Outgoing Webhook")
        print("3. 在钉钉群中@机器人测试")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置和服务状态")
        return 1

if __name__ == "__main__":
    exit(main())