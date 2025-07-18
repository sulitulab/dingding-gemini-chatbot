# 使用示例

## 场景描述

您有一个钉钉群，想要添加一个AI机器人来回答群友的问题。

## 步骤演示

### 1. 在钉钉群中添加机器人

1. 打开钉钉群聊
2. 点击群设置（右上角三点）
3. 选择"智能群助手"
4. 点击"添加机器人"
5. 选择"自定义机器人"
6. 设置机器人名称，例如："AI助手"
7. 获取 Webhook URL（保存好，后面要用）

### 2. 配置应用

复制并编辑环境变量：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```bash
# 钉钉机器人配置（自定义机器人留空即可）
DINGTALK_WEBHOOK_SECRET=
DINGTALK_BOT_TOKEN=

# GCP Vertex AI 配置（必需填写）
GCP_PROJECT_ID=my-gcp-project-123
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# 应用配置
PORT=5000
DEBUG=False
```

### 3. 启动应用

```bash
./start.sh
```

应用启动后会显示：
```
✅ 环境变量配置正确
✅ Vertex AI 初始化成功
🚀 启动钉钉机器人webhook服务，端口: 5000
```

### 4. 配置公网访问

如果在本地开发，可以使用 ngrok 等工具：

```bash
# 安装 ngrok
npm install -g ngrok

# 启动隧道
ngrok http 5000
```

获得类似这样的公网地址：
```
https://abc123.ngrok.io
```

### 5. 设置钉钉机器人 Webhook

在钉钉机器人设置中，将 Webhook URL 设置为：
```
https://abc123.ngrok.io/webhook
```

### 6. 测试机器人

在群聊中@机器人发送消息：

**用户消息：**
```
@AI助手 请解释一下什么是人工智能？
```

**机器人回复：**
```
@张三 人工智能（AI）是指让计算机模拟人类智能的技术。它包括机器学习、深度学习、自然语言处理等多个领域。AI系统可以学习、推理和做出决策，应用于图像识别、语音识别、自动驾驶等多个场景。现代AI技术通过大量数据训练，能够在特定任务上达到甚至超越人类的表现。
```

### 7. 更多使用场景

**问答场景：**
```
用户：@AI助手 Python中如何读取JSON文件？
机器人：@用户 在Python中读取JSON文件可以使用json模块...
```

**创意场景：**
```
用户：@AI助手 帮我写一个周末计划
机器人：@用户 这里是一个充实的周末计划建议...
```

**技术支持：**
```
用户：@AI助手 我的代码报错了，怎么办？
机器人：@用户 请提供具体的错误信息，我来帮您分析...
```

### 8. 监控和维护

**查看应用状态：**
```bash
curl http://localhost:5000/health
```

**测试AI功能：**
```bash
curl "http://localhost:5000/test?q=你好"
```

**查看日志：**
```bash
tail -f /tmp/gunicorn_error.log
```

### 9. 生产部署建议

**使用 Docker 部署：**
```bash
docker build -t dingtalk-bot .
docker run -d --name dingtalk-bot -p 5000:5000 dingtalk-bot
```

**使用 Google Cloud Run 部署：**
```bash
gcloud run deploy dingtalk-bot --source . --region us-central1
```

### 10. 常见问题解决

**问题1：机器人没有回复**
- 检查应用是否正常运行
- 确认 webhook URL 配置正确
- 查看应用日志

**问题2：AI 回复"服务不可用"**
- 检查 GCP 配置是否正确
- 确认 Vertex AI API 已启用
- 检查服务账号权限

**问题3：回复很慢**
- 这是正常的，AI 模型需要时间处理
- 可以调整模型参数优化速度
- 考虑添加"正在思考..."的提示

---

现在您的钉钉群就有了一个智能AI助手！🎉