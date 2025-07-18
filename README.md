# 钉钉机器人 Webhook 处理应用

这是一个基于 Flask 的钉钉机器人 webhook 处理应用，集成了 GCP Vertex AI 的 Gemini-2.5-Flash 模型，可以在钉钉群聊中响应用户的 @机器人 消息。

## 功能特性

- ✅ 钉钉群聊 @机器人 消息处理
- ✅ GCP Vertex AI Gemini-2.5-Flash 模型集成
- ✅ 快速响应，关闭 CoT 处理
- ✅ 消息签名验证
- ✅ 支持 @用户 回复
- ✅ 完整的错误处理和日志记录
- ✅ 健康检查和测试接口

## 项目结构

```
dingding-gemini-chatbot/
├── app.py                 # 原始版本应用主文件
├── app_v2.py             # 改进版本应用主文件（推荐）
├── config.py             # 配置管理
├── utils.py              # 工具函数
├── gemini_client.py      # Gemini AI 客户端
├── run.py                # 启动脚本
├── requirements.txt      # 依赖包
├── .env.example         # 环境变量示例
├── gunicorn.conf.py     # Gunicorn 配置
└── README.md            # 说明文档
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并修改相应配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# 钉钉机器人配置
DINGTALK_WEBHOOK_SECRET=your_webhook_secret_here
DINGTALK_BOT_TOKEN=your_bot_token_here

# GCP Vertex AI 配置
GCP_PROJECT_ID=your_gcp_project_id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# 应用配置
PORT=5000
DEBUG=False
```

### 3. GCP 配置

1. 创建 GCP 项目并启用 Vertex AI API
2. 创建服务账号并下载密钥文件
3. 设置 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量指向密钥文件路径

### 4. 钉钉机器人配置

1. 在钉钉群中创建自定义机器人
2. 获取 Webhook URL 和安全设置中的密钥
3. 设置机器人的 Webhook URL 为你的服务地址 `https://your-domain.com/webhook`

## 运行应用

### 开发模式

```bash
python app_v2.py
```

或者：

```bash
python run.py
```

### 生产模式

使用 Gunicorn：

```bash
gunicorn -c gunicorn.conf.py app_v2:app
```

## API 接口

### 1. Webhook 接口

- **URL**: `/webhook`
- **方法**: POST
- **描述**: 处理钉钉机器人的 webhook 消息

### 2. 健康检查

- **URL**: `/health`
- **方法**: GET
- **描述**: 检查应用和 AI 服务状态

### 3. 测试接口

- **URL**: `/test?q=你好`
- **方法**: GET
- **描述**: 测试 AI 模型响应

### 4. 配置信息

- **URL**: `/info`
- **方法**: GET
- **描述**: 查看应用配置信息

## 使用方法

1. 在钉钉群中 @机器人 并发送消息
2. 机器人会调用 Gemini-2.5-Flash 模型生成回复
3. 机器人会在群里回复并 @提问者

示例：
```
@机器人 请解释一下什么是人工智能？
```

机器人会回复：
```
@[提问者] 人工智能（AI）是指让计算机模拟人类智能的技术...
```

## 性能优化

- 使用 Gemini-2.5-Flash 模型确保快速响应
- 关闭 CoT（Chain of Thought）处理提高速度
- 设置合适的超时时间
- 使用 Gunicorn 多进程部署

## 部署建议

### Docker 部署

可以创建 Dockerfile 进行容器化部署：

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app_v2:app"]
```

### 云平台部署

- **Google Cloud Run**: 推荐，与 Vertex AI 集成良好
- **AWS Lambda**: 需要配置 GCP 认证
- **Azure Container Instances**: 需要配置 GCP 认证

## 注意事项

1. 确保 GCP 项目已启用 Vertex AI API
2. 服务账号需要有 Vertex AI 的访问权限
3. 钉钉机器人需要正确配置 Webhook URL 和密钥
4. 生产环境建议使用 HTTPS
5. 注意 API 调用频率限制和费用

## 故障排除

### 常见问题

1. **AI 服务不可用**
   - 检查 GCP 项目 ID 和认证配置
   - 确认 Vertex AI API 已启用
   - 检查服务账号权限

2. **钉钉消息收不到**
   - 检查 Webhook URL 是否正确
   - 确认安全设置和签名验证
   - 查看应用日志

3. **回复消息发送失败**
   - 检查钉钉机器人配置
   - 确认 Webhook URL 有效性
   - 检查网络连接

### 日志查看

应用会输出详细的日志信息，包括：
- 请求处理过程
- AI 模型调用时间
- 错误信息和堆栈

## 扩展功能

可以考虑添加的功能：
- 多轮对话支持
- 消息历史记录
- 用户权限管理
- 自定义指令
- 多模态输入支持

## 许可证

MIT License