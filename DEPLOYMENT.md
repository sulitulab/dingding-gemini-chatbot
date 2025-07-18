# 钉钉机器人应用部署指南

## 快速开始

### 1. 环境准备

确保您的系统已安装：
- Python 3.9+ 
- pip
- git

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd dingding-gemini-chatbot
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

必须配置的环境变量：
- `GCP_PROJECT_ID`: 您的 GCP 项目 ID
- `GOOGLE_APPLICATION_CREDENTIALS`: GCP 服务账号密钥文件路径
- `DINGTALK_WEBHOOK_SECRET`: 钉钉机器人密钥（可选）

### 4. 启动应用

使用启动脚本（推荐）：
```bash
./start.sh
```

或者手动启动：
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app_v2.py
```

### 5. 测试应用

```bash
# 测试健康检查
curl http://localhost:5000/health

# 测试AI响应
curl "http://localhost:5000/test?q=你好"

# 运行完整测试
python test.py
```

## 部署方式

### 1. 本地开发部署

```bash
# 开发模式
export FLASK_ENV=development
python app_v2.py
```

### 2. 生产环境部署

#### 使用 Gunicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动生产服务
gunicorn -c gunicorn.conf.py app_v2:app
```

#### 使用 Docker

```bash
# 构建镜像
docker build -t dingtalk-gemini-bot .

# 运行容器
docker run -d \
  --name dingtalk-bot \
  -p 5000:5000 \
  -e GCP_PROJECT_ID=your-project-id \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json \
  -v /path/to/your/service-account-key.json:/app/service-account-key.json \
  dingtalk-gemini-bot
```

### 3. 云平台部署

#### Google Cloud Run

```bash
# 构建并推送镜像
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/dingtalk-bot

# 部署到 Cloud Run
gcloud run deploy dingtalk-bot \
  --image gcr.io/YOUR_PROJECT_ID/dingtalk-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID
```

#### AWS ECS 或 Azure Container Instances

参考相应平台的容器部署文档。

## 钉钉机器人配置

### 1. 创建钉钉机器人

1. 在钉钉群中，点击群设置 → 智能群助手 → 添加机器人
2. 选择"自定义机器人"
3. 设置机器人名称和头像
4. 配置安全设置（推荐使用"加签"方式）
5. 获取 Webhook URL

### 2. 配置 Webhook

1. 将您的服务地址设置为机器人的 Webhook URL
2. 格式：`https://your-domain.com/webhook`
3. 如果使用了加签安全设置，将密钥配置到 `DINGTALK_WEBHOOK_SECRET` 环境变量

### 3. 测试机器人

在群中@机器人发送消息，例如：
```
@你的机器人 你好，请介绍一下你自己
```

## GCP 配置

### 1. 创建 GCP 项目

1. 访问 [GCP Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 记录项目 ID

### 2. 启用 API

```bash
# 启用 Vertex AI API
gcloud services enable aiplatform.googleapis.com

# 启用 Cloud Build API（如果使用 Cloud Run）
gcloud services enable cloudbuild.googleapis.com
```

### 3. 创建服务账号

```bash
# 创建服务账号
gcloud iam service-accounts create dingtalk-bot-sa \
  --display-name "DingTalk Bot Service Account"

# 授予权限
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:dingtalk-bot-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/aiplatform.user"

# 创建密钥文件
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account dingtalk-bot-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## 监控和日志

### 应用日志

应用会输出详细的日志信息，包括：
- 请求处理过程
- AI 模型调用时间
- 错误信息

### 健康检查

- 端点：`/health`
- 返回应用状态和 AI 服务状态

### 监控指标

建议监控以下指标：
- 请求响应时间
- 错误率
- AI 模型调用成功率
- 内存和 CPU 使用率

## 故障排除

### 常见错误

1. **"AI客户端未初始化"**
   - 检查 GCP_PROJECT_ID 环境变量
   - 确认 Vertex AI API 已启用
   - 检查服务账号权限

2. **"签名验证失败"**
   - 检查 DINGTALK_WEBHOOK_SECRET 配置
   - 确认钉钉机器人加签设置正确

3. **"模型调用超时"**
   - 检查网络连接
   - 增加超时时间配置
   - 检查 GCP 服务状态

### 调试命令

```bash
# 检查环境变量
env | grep -E "(GCP|DINGTALK|GOOGLE)"

# 测试 GCP 认证
gcloud auth application-default print-access-token

# 查看应用日志
tail -f /tmp/gunicorn_error.log

# 测试网络连接
curl -I https://aiplatform.googleapis.com/
```

## 性能优化

### 1. 模型参数调优

在 `gemini_client.py` 中调整：
- `temperature`: 控制回复的随机性
- `top_p` 和 `top_k`: 控制词汇选择
- `max_output_tokens`: 控制回复长度

### 2. 缓存策略

考虑添加：
- 相似问题的缓存
- 用户会话缓存
- 模型结果缓存

### 3. 并发处理

- 使用 Gunicorn 多进程
- 调整 worker 数量
- 使用异步处理

## 安全考虑

1. **环境变量保护**
   - 不要将 .env 文件提交到版本控制
   - 使用密钥管理服务

2. **API 安全**
   - 启用钉钉消息签名验证
   - 添加 IP 白名单（如果需要）
   - 使用 HTTPS

3. **服务账号权限**
   - 仅授予必要的权限
   - 定期轮换密钥
   - 使用 IAM 条件

## 费用优化

1. **Vertex AI 使用**
   - 监控 API 调用次数
   - 设置预算告警
   - 优化模型参数减少 token 使用

2. **云资源**
   - 使用合适的实例规格
   - 设置自动缩放
   - 定期清理不用的资源

## 更新和维护

### 版本更新

```bash
# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
systemctl restart dingtalk-bot  # 或相应的服务管理命令
```

### 数据备份

定期备份：
- 应用配置
- 聊天历史（如果存储）
- 服务账号密钥

## 扩展功能

可以考虑添加：
- 多轮对话支持
- 用户权限管理
- 消息历史记录
- 自定义指令
- 多模态支持（图片、语音）
- 群聊管理功能

## 技术支持

如果遇到问题：
1. 查看应用日志
2. 运行测试脚本
3. 检查环境配置
4. 参考故障排除部分

更多详细信息请参考 [README.md](README.md) 文件。