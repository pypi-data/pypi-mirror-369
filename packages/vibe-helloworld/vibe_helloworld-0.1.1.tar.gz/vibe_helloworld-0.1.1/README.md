# vibe-helloworld

<div align="center">
一个有趣的AI驱动的Hello World生成器项目
<br>
中文 | <a href="README_EN.md">English</a>
</div>

## 系统要求

- Python 3.10+

## 安装

```bash
pip install vibe-helloworld
```

## 使用方法

```python
from vibe_helloworld import VibeHelloWorld

# 设置环境变量
# export OPENAI_API_KEY="your_api_key_here"
# export OPENAI_BASE_URL="https://api.openai.com/v1/chat/completions"  # 可选，默认使用官方地址
# export OPENAI_MODEL="gpt-4o-mini"  # 可选，默认使用 gpt-4o-mini

# 结构化输出模式（默认）- 返回 "hello world"
result = VibeHelloWorld("This is my first AI project")
print(result)  # "hello world"

# 正常聊天对话模式 - 返回 AI 的正常回复
response = VibeHelloWorld("How are you today?", chat_with_nlp=False)
print(response)  # AI的正常聊天回复

# 更多示例
structured = VibeHelloWorld("测试消息", chat_with_nlp=True)
print(structured)  # "hello world"

chat = VibeHelloWorld("你好，请介绍一下自己", chat_with_nlp=False)
print(chat)  # AI的自我介绍
```

## 参数说明

- `message: str`: 输入消息
- `chat_with_nlp: bool = True`: 
  - `True`: 使用结构化输出，强制返回 `"hello world"`
  - `False`: 正常聊天对话模式，返回 AI 的自然回复

## 环境变量

- `OPENAI_API_KEY`: OpenAI API 密钥（必需）
- `OPENAI_BASE_URL`: API 基础地址（可选，默认为官方地址）
- `OPENAI_MODEL`: 使用的模型（可选，默认为 `gpt-4o-mini`）

## License

[MIT](LICENSE)