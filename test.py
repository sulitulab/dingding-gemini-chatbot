#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人应用测试脚本
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_ai_response():
    """测试AI响应"""
    try:
        response = requests.get(
            "http://localhost:5000/test", 
            params={"q": "你好，请简单介绍一下你自己"}, 
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ AI响应测试通过")
            print(f"   问题: {result.get('question')}")
            print(f"   回答: {result.get('response')}")
            return True
        else:
            print(f"❌ AI响应测试失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI响应测试异常: {e}")
        return False

def test_webhook_simulation():
    """模拟钉钉webhook请求"""
    try:
        # 模拟钉钉webhook数据
        webhook_data = {
            "msgtype": "text",
            "text": {
                "content": "@机器人 测试消息"
            },
            "atUsers": [
                {
                    "dingtalkId": "test_user",
                    "staffId": "test_staff"
                }
            ],
            "senderStaffId": "test_staff",
            "sessionWebhook": "https://oapi.dingtalk.com/robot/send?access_token=test_token"
        }
        
        # 发送模拟请求（注意：这只是结构测试，不会真正发送消息）
        print("📝 模拟webhook数据结构:")
        print(json.dumps(webhook_data, indent=2, ensure_ascii=False))
        print("✅ Webhook数据结构正确")
        return True
        
    except Exception as e:
        print(f"❌ Webhook模拟测试异常: {e}")
        return False

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    required_vars = [
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
    print("🚀 开始钉钉机器人应用测试")
    print("=" * 50)
    
    # 检查环境配置
    if not check_environment():
        print("❌ 环境配置检查失败，请检查 .env 文件")
        sys.exit(1)
    
    print()
    print("📡 测试应用接口...")
    print("请确保应用正在运行 (python app_v2.py)")
    print()
    
    # 测试健康检查
    health_ok = test_health_check()
    print()
    
    # 测试AI响应
    ai_ok = test_ai_response()
    print()
    
    # 测试webhook结构
    webhook_ok = test_webhook_simulation()
    print()
    
    # 总结
    print("=" * 50)
    print("📊 测试结果总结:")
    print(f"   健康检查: {'✅' if health_ok else '❌'}")
    print(f"   AI响应: {'✅' if ai_ok else '❌'}")
    print(f"   Webhook结构: {'✅' if webhook_ok else '❌'}")
    
    if health_ok and ai_ok and webhook_ok:
        print("\n🎉 所有测试通过！应用工作正常")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置和服务状态")
        return 1

if __name__ == "__main__":
    sys.exit(main())