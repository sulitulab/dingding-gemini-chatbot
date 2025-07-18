#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人交互式聊天工具
"""

import os
import sys
import time
from dotenv import load_dotenv
from dingtalk_bot import DingTalkBot, GeminiClient

# 加载环境变量
load_dotenv()

def main():
    """交互式聊天主函数"""
    print("🤖 钉钉机器人 AI 助手")
    print("=" * 50)
    
    # 检查环境变量
    access_token = os.getenv('DINGTALK_ACCESS_TOKEN')
    secret = os.getenv('DINGTALK_SECRET', '')
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    
    if not access_token:
        print("❌ 请设置 DINGTALK_ACCESS_TOKEN 环境变量")
        print("   从您的钉钉机器人webhook地址中提取access_token")
        print("   例如：https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN")
        return
    
    if not gcp_project_id:
        print("❌ 请设置 GCP_PROJECT_ID 环境变量")
        return
    
    # 初始化组件
    print("🔧 初始化钉钉机器人...")
    bot = DingTalkBot(access_token, secret)
    
    print("🔧 初始化Gemini AI...")
    gemini = GeminiClient(gcp_project_id)
    if not gemini.initialize():
        print("❌ Gemini初始化失败")
        return
    
    print("✅ 初始化完成！")
    print()
    print("使用说明：")
    print("- 输入消息，AI会生成回复并发送到钉钉群")
    print("- 输入 'quit' 或 'exit' 退出程序")
    print("- 输入 'test' 发送测试消息")
    print()
    
    # 交互式循环
    while True:
        try:
            user_input = input("💬 请输入消息: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit']:
                print("👋 再见！")
                break
            
            if user_input.lower() == 'test':
                print("📤 发送测试消息到钉钉群...")
                result = bot.send_message("🧪 这是一条测试消息！")
                if result.get("errcode") == 0:
                    print("✅ 测试消息发送成功！")
                else:
                    print(f"❌ 测试消息发送失败：{result.get('errmsg')}")
                continue
            
            print("🤔 AI正在思考...")
            
            # 生成AI回复
            ai_response = gemini.generate_content(user_input)
            
            print(f"🤖 AI回复: {ai_response}")
            
            # 发送到钉钉
            print("📤 发送到钉钉群...")
            
            message = f"🤖 AI助手回复：\n\n问题：{user_input}\n\n回答：{ai_response}"
            
            result = bot.send_message(message)
            
            if result.get("errcode") == 0:
                print("✅ 消息发送成功！")
            else:
                print(f"❌ 消息发送失败：{result.get('errmsg')}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误：{e}")

if __name__ == '__main__':
    main()