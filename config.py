#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人应用配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    # 钉钉机器人配置
    DINGTALK_WEBHOOK_SECRET = os.getenv('DINGTALK_WEBHOOK_SECRET', '')
    DINGTALK_BOT_TOKEN = os.getenv('DINGTALK_BOT_TOKEN', '')
    
    # GCP Vertex AI 配置
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', '')
    GCP_LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
    MODEL_NAME = 'gemini-2.5-flash'
    
    # Google Cloud 认证
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # 应用配置
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 超时配置
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    AI_TIMEOUT = int(os.getenv('AI_TIMEOUT', 15))

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """获取当前配置"""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])