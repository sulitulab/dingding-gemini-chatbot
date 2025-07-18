#!/bin/bash
# 配置公网访问脚本

echo "=== 钉钉机器人公网访问配置 ==="

# 检查应用是否运行
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "❌ 应用未运行，请先启动应用："
    echo "   python app_simple.py"
    exit 1
fi

echo "✅ 应用正在运行"

# 检查是否安装了 ngrok
if ! command -v ngrok &> /dev/null; then
    echo "📦 ngrok 未安装，正在安装..."
    
    # 根据系统类型安装 ngrok
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
        echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
        sudo apt update && sudo apt install ngrok
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ngrok/ngrok/ngrok
        else
            echo "请手动安装 ngrok: https://ngrok.com/download"
            exit 1
        fi
    else
        echo "请手动安装 ngrok: https://ngrok.com/download"
        exit 1
    fi
fi

echo "✅ ngrok 已安装"

# 启动 ngrok
echo "🚀 启动 ngrok 隧道..."
echo "请在另一个终端窗口运行以下命令："
echo ""
echo "    ngrok http 5000"
echo ""
echo "然后复制 https://xxx.ngrok.io 地址"
echo "在钉钉机器人设置中配置 Webhook URL 为："
echo "    https://xxx.ngrok.io/webhook"
echo ""
echo "配置完成后，在钉钉群中@机器人测试！"