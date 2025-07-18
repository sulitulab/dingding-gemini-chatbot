# 钉钉机器人直接发送消息 - 使用指南

## 🎯 理解您的需求

您有：
- ✅ 钉钉自定义机器人webhook地址（如：`https://oapi.dingtalk.com/robot/send?access_token=bdc07d35...`）
- ✅ 想要程序处理完gemini响应后，直接发送到钉钉群

## 📋 配置步骤

### 1. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

在 `.env` 文件中设置：

```bash
# 从您的钉钉机器人webhook地址中提取access_token
DINGTALK_ACCESS_TOKEN=bdc07d35b864929979e5c137971203bfe6ed2b54fb4bc0261546b35d8d1ac034

# 如果您的机器人设置了加签安全验证，填写secret
DINGTALK_SECRET=

# GCP配置
GCP_PROJECT_ID=your_gcp_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 测试运行

**方式1：交互式聊天**
```bash
python interactive_chat.py
```

这会启动一个交互式程序，您可以：
- 输入问题，AI生成回复并发送到钉钉群
- 输入 `test` 发送测试消息
- 输入 `quit` 退出程序

**方式2：直接使用API**
```bash
python dingtalk_bot.py
```

这会运行一个示例，展示如何发送消息到钉钉群。

### 4. 编程使用

```python
from dingtalk_bot import DingTalkBot, GeminiClient

# 初始化
bot = DingTalkBot(access_token="你的access_token")
gemini = GeminiClient(project_id="你的GCP项目ID")
gemini.initialize()

# 生成AI回复
question = "什么是人工智能？"
ai_response = gemini.generate_content(question)

# 发送到钉钉群
result = bot.send_message(f"🤖 AI回复：\n\n{ai_response}")

if result.get("errcode") == 0:
    print("发送成功！")
```

## 🔧 功能特性

### DingTalkBot 类
- `send_message()` - 发送消息到钉钉群
- 支持 @特定用户 (`at_user_ids`)
- 支持 @手机号 (`at_mobiles`)
- 支持 @所有人 (`is_at_all`)
- 支持加签安全验证

### GeminiClient 类
- `generate_content()` - 生成AI回复
- 使用 Gemini-1.5-Flash 模型
- 优化的参数设置

## 📝 使用示例

### 示例1：发送简单消息
```python
from dingtalk_bot import DingTalkBot

bot = DingTalkBot("你的access_token")
bot.send_message("Hello, 钉钉！")
```

### 示例2：@特定用户
```python
bot.send_message(
    msg="这是一条重要消息",
    at_user_ids=["user123", "user456"]
)
```

### 示例3：AI问答
```python
from dingtalk_bot import DingTalkBot, GeminiClient

bot = DingTalkBot("你的access_token")
gemini = GeminiClient("你的GCP项目ID")
gemini.initialize()

question = "请解释量子计算"
answer = gemini.generate_content(question)

bot.send_message(f"❓ {question}\n\n🤖 {answer}")
```

## 🚀 立即试用

1. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑.env文件，设置DINGTALK_ACCESS_TOKEN和GCP_PROJECT_ID
   ```

2. **运行交互式聊天**
   ```bash
   python interactive_chat.py
   ```

3. **输入问题**
   ```
   💬 请输入消息: 什么是人工智能？
   ```

4. **查看钉钉群**
   您的机器人会在群里发送AI生成的回复！

## 🔍 故障排除

### 问题1：发送失败
- 检查 `DINGTALK_ACCESS_TOKEN` 是否正确
- 确认钉钉机器人是否正常工作
- 查看错误日志

### 问题2：AI回复失败
- 检查 `GCP_PROJECT_ID` 和认证文件
- 确认Vertex AI API已启用
- 检查网络连接

### 问题3：签名验证失败
- 如果设置了加签安全验证，确保 `DINGTALK_SECRET` 正确
- 检查时间戳和签名计算

---

现在您可以直接向钉钉群发送AI生成的消息了！🎉