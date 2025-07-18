# 完整钉钉机器人系统部署指南

## 🎯 系统架构

```
钉钉群用户 @机器人
    ↓
钉钉服务器 POST → 您的接口(/webhook)
    ↓
提取用户消息 → Gemini AI处理
    ↓
发送响应 → 钉钉机器人webhook
    ↓
钉钉群显示机器人回复
```

## 📋 需要准备的内容

### 1. 钉钉机器人信息
- ✅ 机器人webhook地址：`https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN`
- ✅ 机器人加签密钥（如果设置了安全验证）

### 2. 您的服务器信息
- ✅ 公网可访问的地址（用于接收钉钉消息）
- ✅ GCP项目和认证信息

## 🔧 配置步骤

### 第1步：配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

在 `.env` 文件中设置：

```bash
# 钉钉机器人配置
# 从webhook地址提取: https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN
DINGTALK_ACCESS_TOKEN=YOUR_ACCESS_TOKEN_HERE

# 如果设置了加签安全验证，填写密钥
DINGTALK_SECRET=YOUR_SECRET_HERE

# GCP Vertex AI 配置
GCP_PROJECT_ID=your_gcp_project_id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# 应用配置
PORT=5000
DEBUG=False
```

### 第2步：启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python complete_bot.py
```

看到以下输出表示成功：
```
钉钉机器人初始化成功
Gemini客户端初始化成功
启动钉钉机器人服务，端口: 5000
```

### 第3步：配置公网访问

**本地开发（使用ngrok）：**
```bash
# 新终端窗口
ngrok http 5000

# 复制https地址，如：https://abc123.ngrok.io
```

**云服务器部署：**
```bash
# 使用您的域名，如：https://your-domain.com
```

### 第4步：配置钉钉机器人

1. **在钉钉群中找到您的机器人**
2. **编辑机器人设置**
3. **配置Outgoing Webhook**（重要！）
   - URL：`https://your-domain.com/webhook`
   - 或：`https://abc123.ngrok.io/webhook`

## 🚀 测试系统

### 1. 健康检查
```bash
curl http://localhost:5000/health
```

应该返回：
```json
{
  "status": "healthy",
  "services": {
    "dingtalk": "ready",
    "gemini": "ready"
  }
}
```

### 2. 测试AI功能
```bash
curl "http://localhost:5000/test?msg=你好"
```

### 3. 在钉钉群中测试
```
@您的机器人 你好，请介绍一下你自己
```

## 📊 完整工作流程

### 当用户在钉钉群中发消息时：

1. **用户发送**：`@机器人 什么是人工智能？`

2. **钉钉发送到您的接口**：
   ```json
   POST https://your-domain.com/webhook
   {
     "msgtype": "text",
     "text": {
       "content": "@机器人 什么是人工智能？"
     },
     "senderStaffId": "user123",
     "senderNick": "张三"
   }
   ```

3. **您的程序处理**：
   - 提取消息：`什么是人工智能？`
   - 调用Gemini生成回复
   - 获取AI响应

4. **发送回复到钉钉**：
   ```json
   POST https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN
   {
     "msgtype": "text",
     "text": {
       "content": "@张三 人工智能是..."
     },
     "at": {
       "atUserIds": ["user123"]
     }
   }
   ```

5. **钉钉群显示**：`@张三 人工智能是...`

## 🔍 故障排除

### 问题1：机器人没有回复
**检查项：**
- [ ] 服务是否正常运行？
- [ ] 钉钉机器人Outgoing Webhook是否配置正确？
- [ ] 服务器日志是否有错误？

**调试命令：**
```bash
# 查看服务状态
curl http://localhost:5000/health

# 查看日志
tail -f app.log
```

### 问题2：接收到消息但AI处理失败
**检查项：**
- [ ] GCP_PROJECT_ID 是否正确？
- [ ] 认证文件是否存在？
- [ ] Vertex AI API是否启用？

**调试命令：**
```bash
# 测试AI功能
curl "http://localhost:5000/test?msg=测试消息"

# 测试GCP认证
gcloud auth application-default print-access-token
```

### 问题3：消息发送到钉钉失败
**检查项：**
- [ ] DINGTALK_ACCESS_TOKEN 是否正确？
- [ ] 网络连接是否正常？
- [ ] 钉钉机器人是否被禁用？

**调试命令：**
```bash
# 测试发送消息
curl -X POST "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"测试消息"}}'
```

## 🎉 部署完成

配置完成后，您的钉钉机器人系统就可以正常工作了：

1. **用户在群里@机器人**
2. **钉钉发送消息到您的接口**
3. **您的程序调用Gemini处理**
4. **程序发送AI回复到钉钉群**
5. **用户看到机器人回复**

现在您有一个完整的钉钉AI机器人系统！🚀