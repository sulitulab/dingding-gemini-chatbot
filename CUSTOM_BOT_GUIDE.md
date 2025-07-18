# 自定义钉钉机器人快速配置指南

## 🚀 针对自定义机器人的简化配置

如果您使用的是钉钉的自定义机器人（只有webhook URL），这是最简单的配置方式。

### 1. 环境变量配置

创建 `.env` 文件：

```bash
# 钉钉机器人配置（自定义机器人通常留空）
DINGTALK_WEBHOOK_SECRET=
DINGTALK_BOT_TOKEN=

# GCP Vertex AI 配置（必需）
GCP_PROJECT_ID=your_gcp_project_id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# 应用配置
PORT=5000
DEBUG=False
```

### 2. 钉钉机器人设置

1. **在钉钉群中添加机器人：**
   - 群设置 → 智能群助手 → 添加机器人
   - 选择"自定义机器人"
   - 设置机器人名称

2. **获取 Webhook URL：**
   - 钉钉会给您一个类似这样的URL：
   ```
   https://oapi.dingtalk.com/robot/send?access_token=xxxxx
   ```

3. **配置您的服务地址：**
   - 确保您的应用运行在公网可访问的地址
   - 钉钉机器人会向您的 `/webhook` 端点发送消息
   - 完整地址格式：`https://your-domain.com/webhook`

### 3. 启动应用

```bash
# 克隆代码（如果需要）
git clone <your-repo>
cd dingding-gemini-chatbot

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 一键启动
./start.sh
```

### 4. 测试机器人

在钉钉群中@机器人发送消息：

```
@你的机器人名称 你好，请介绍一下你自己
```

机器人会调用 Gemini AI 生成回复。

### 5. 常见问题

**Q: 机器人没有回复？**
- 检查应用是否正常运行（访问 `http://localhost:5000/health`）
- 确认公网地址可访问
- 查看应用日志是否有错误信息

**Q: 提示 AI 服务不可用？**
- 检查 GCP 项目 ID 是否正确
- 确认 Vertex AI API 已启用
- 检查服务账号密钥文件路径和权限

**Q: 想要添加安全验证？**
- 在钉钉机器人设置中启用"加签"验证
- 将密钥添加到 `DINGTALK_WEBHOOK_SECRET` 环境变量
- 重启应用

### 6. 部署到生产环境

**使用 Docker：**
```bash
# 构建镜像
docker build -t dingtalk-bot .

# 运行容器
docker run -d \
  --name dingtalk-bot \
  -p 5000:5000 \
  -e GCP_PROJECT_ID=your-project-id \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json \
  -v /path/to/your/service-account-key.json:/app/service-account-key.json \
  dingtalk-bot
```

**使用云平台：**
- Google Cloud Run（推荐）
- AWS ECS
- Azure Container Instances

### 7. 进阶配置

如果需要更高级的功能，可以：

1. **启用签名验证：**
   ```bash
   DINGTALK_WEBHOOK_SECRET=your_secret_from_dingtalk
   ```

2. **调整 AI 模型参数：**
   - 编辑 `gemini_client.py` 中的 `temperature`、`top_p` 等参数
   - 根据需要调整 `max_output_tokens` 控制回复长度

3. **添加日志监控：**
   - 查看 `/tmp/gunicorn_*.log` 文件
   - 使用 `python test.py` 进行功能测试

### 8. 成本优化

- 监控 Vertex AI 的使用量
- 设置合理的 `max_output_tokens` 参数
- 考虑添加消息缓存以减少重复请求

---

这样就完成了！您的钉钉机器人现在可以使用 Gemini AI 来回答群聊中的问题了。🎉