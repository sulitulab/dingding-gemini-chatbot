#!/bin/bash

# 钉钉机器人应用启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 钉钉机器人 Webhook 应用启动脚本 ===${NC}"

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
echo -e "${YELLOW}Python版本: ${python_version}${NC}"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
echo -e "${YELLOW}安装依赖包...${NC}"
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo -e "${RED}警告: .env 文件不存在！${NC}"
    echo -e "${YELLOW}请复制 .env.example 到 .env 并配置相应的环境变量${NC}"
    echo -e "${YELLOW}cp .env.example .env${NC}"
    exit 1
fi

# 检查必要的环境变量
source .env

if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}错误: GCP_PROJECT_ID 环境变量未设置${NC}"
    exit 1
fi

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${RED}错误: GOOGLE_APPLICATION_CREDENTIALS 环境变量未设置${NC}"
    exit 1
fi

if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${RED}错误: GCP 服务账号密钥文件不存在: $GOOGLE_APPLICATION_CREDENTIALS${NC}"
    exit 1
fi

echo -e "${GREEN}环境检查通过！${NC}"

# 启动应用
echo -e "${GREEN}启动钉钉机器人应用...${NC}"
python3 app_v2.py