#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人Webhook处理应用启动脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    from app import app, init_vertex_ai
    
    # 初始化 Vertex AI
    init_vertex_ai()
    
    # 获取配置
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 启动应用
    print(f"启动钉钉机器人webhook服务，端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)