# 钉钉机器人Webhook配置指南

## 当前状态
- ✅ 您的Flask应用正在运行
- ✅ 钉钉群中有自定义机器人
- ❌ 还没有配置机器人的Webhook地址

## 关键理解

**钉钉机器人有两个URL：**

1. **钉钉给您的URL**（发送消息用）
   - 格式：`https://oapi.dingtalk.com/robot/send?access_token=xxxxx`
   - 用途：您的程序向钉钉发送回复消息

2. **您给钉钉的URL**（接收消息用）⚠️ **这个还没配置**
   - 格式：`https://your-domain.com/webhook`
   - 用途：钉钉向您的程序发送用户消息

## 配置步骤

### 第1步：获取公网地址

**如果您在本地开发：**

1. 确保应用正在运行：
   ```bash
   python app_simple.py
   ```

2. 在新的终端窗口中运行：
   ```bash
   # 如果没有安装ngrok
   # macOS: brew install ngrok
   # Linux: 访问 https://ngrok.com/download 下载

   # 启动ngrok隧道
   ngrok http 5000
   ```

3. 复制ngrok提供的HTTPS地址，例如：
   ```
   https://abc123.ngrok.io
   ```

**如果您在云服务器：**
- 使用您的域名或IP地址，例如：
  ```
  https://your-domain.com
  ```

### 第2步：配置钉钉机器人

1. **找到您的机器人设置**
   - 在钉钉群中，点击群设置（右上角三个点）
   - 选择"智能群助手"
   - 找到您创建的机器人

2. **编辑机器人配置**
   - 点击机器人旁边的"设置"或"编辑"
   - 找到"Webhook URL"配置项

3. **设置Webhook URL**
   ```
   https://abc123.ngrok.io/webhook
   ```
   
   **注意：**
   - 必须是HTTPS（ngrok默认提供）
   - 路径是 `/webhook`（这是您程序中定义的路径）
   - 如果使用自己的域名，确保SSL证书有效

4. **保存配置**

### 第3步：测试机器人

1. 在钉钉群中@机器人：
   ```
   @您的机器人名称 你好
   ```

2. 观察您的程序日志，应该看到：
   ```
   收到钉钉webhook消息
   处理问题: 你好
   Gemini响应成功，耗时: 2.34秒
   回复消息发送成功
   ```

3. 机器人应该会在群里回复

## 完整的消息流程

```
1. 用户在群里: @机器人 你好
   ↓
2. 钉钉发送POST请求到: https://abc123.ngrok.io/webhook
   ↓
3. 您的程序收到请求，处理消息
   ↓
4. 程序调用Gemini AI生成回复
   ↓
5. 程序发送回复到钉钉的sessionWebhook
   ↓
6. 机器人在群里回复: @用户 您好！我是AI助手...
```

## 故障排除

### 问题1：机器人没有回复
**检查项：**
- [ ] 应用是否正在运行？
- [ ] ngrok隧道是否正常？
- [ ] 钉钉Webhook URL配置是否正确？
- [ ] 程序日志是否有错误？

**测试命令：**
```bash
# 测试应用健康状态
curl http://localhost:5000/health

# 测试AI功能
curl "http://localhost:5000/test?q=你好"

# 测试公网访问
curl https://abc123.ngrok.io/health
```

### 问题2：程序收到消息但处理失败
**检查项：**
- [ ] GCP配置是否正确？
- [ ] 环境变量是否设置？
- [ ] AI服务是否可用？

**测试命令：**
```bash
# 检查环境变量
echo $GCP_PROJECT_ID
echo $GOOGLE_APPLICATION_CREDENTIALS

# 测试GCP认证
gcloud auth application-default print-access-token
```

### 问题3：回复发送失败
**检查项：**
- [ ] 钉钉返回的错误信息
- [ ] 消息格式是否正确？
- [ ] 网络连接是否正常？

## 重要提醒

1. **ngrok免费版限制**
   - 每次重启ngrok，URL会变化
   - 需要重新配置钉钉机器人的Webhook URL

2. **生产环境建议**
   - 使用固定的域名和SSL证书
   - 部署到云服务器
   - 使用反向代理（如Nginx）

3. **安全考虑**
   - 可以在钉钉机器人中启用"加签"验证
   - 添加IP白名单（如果需要）

## 快速配置命令

```bash
# 1. 启动应用
python app_simple.py

# 2. 新终端启动ngrok（如果本地开发）
ngrok http 5000

# 3. 复制HTTPS地址，在钉钉中配置：
# https://abc123.ngrok.io/webhook

# 4. 在群里测试：
# @机器人 你好
```

配置完成后，您的钉钉机器人就能正常工作了！🎉