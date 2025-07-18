#!/bin/bash

# 完整钉钉机器人系统启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 钉钉机器人系统启动脚本${NC}"
echo "=" * 50

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
echo -e "${BLUE}Python版本: ${python_version}${NC}"

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

if [ -z "$DINGTALK_ACCESS_TOKEN" ]; then
    echo -e "${RED}错误: DINGTALK_ACCESS_TOKEN 环境变量未设置${NC}"
    echo -e "${YELLOW}请在.env文件中设置您的钉钉机器人access_token${NC}"
    exit 1
fi

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

echo -e "${GREEN}✅ 环境检查通过！${NC}"

# 运行测试
echo -e "${YELLOW}运行系统测试...${NC}"
python test_complete_system.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 系统测试通过！${NC}"
else
    echo -e "${RED}❌ 系统测试失败，请检查配置${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 启动完整钉钉机器人系统...${NC}"
echo -e "${BLUE}访问 http://localhost:5000/health 查看系统状态${NC}"
echo -e "${BLUE}在钉钉群中@机器人测试功能${NC}"
echo ""
echo -e "${YELLOW}重要提醒：请确保在钉钉机器人中配置 Outgoing Webhook${NC}"
echo -e "${YELLOW}Webhook URL: https://your-domain.com/webhook${NC}"
echo ""

# 启动应用
python complete_bot.py