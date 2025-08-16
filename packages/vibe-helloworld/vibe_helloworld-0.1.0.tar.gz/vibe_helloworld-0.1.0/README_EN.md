# vibe-helloworld

<div align="center">
An entertaining AI-powered Hello World generator project
<br>
<a href="README.md">中文</a> | English
</div>

## System Requirements

- Python 3.10+

## Installation

```bash
pip install vibe-helloworld
```

## Usage

```python
from vibe_helloworld import VibeHelloWorld

# Set environment variables
# export OPENAI_API_KEY="your_api_key_here"
# export OPENAI_BASE_URL="https://api.openai.com/v1/chat/completions"  # Optional, defaults to official API

# Structured output mode (default) - returns "hello world"
result = VibeHelloWorld("This is my first AI project")
print(result)  # "hello world"

# Normal chat mode - returns AI's natural response
response = VibeHelloWorld("How are you today?", chat_with_nlp=False)
print(response)  # AI's normal chat response

# More examples
structured = VibeHelloWorld("Test message", chat_with_nlp=True)
print(structured)  # "hello world"

chat = VibeHelloWorld("Hello, please introduce yourself", chat_with_nlp=False)
print(chat)  # AI's self-introduction
```

## Parameters

- `message: str`: Input message
- `chat_with_nlp: bool = True`: 
  - `True`: Use structured output, force return `"hello world"`
  - `False`: Normal chat mode, return AI's natural response

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key (required)
- `OPENAI_BASE_URL`: API base URL (optional, defaults to official address)

## License

[MIT](LICENSE)