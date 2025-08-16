import asyncio
import json
import os
from typing import Literal

import aiohttp


async def _generate_with_ai_async(
    message: str, chat_with_nlp: bool = True
) -> Literal["hello world"] | str:
    """Use OpenAI API to generate output."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
        )

    base_url = os.getenv(
        "OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if chat_with_nlp:
        # 结构化输出模式
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": f"Generate hello world message for: {message}",
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "hello_world_message",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "enum": ["hello world"]}
                        },
                        "required": ["message"],
                    },
                },
            },
        }
    else:
        # 正常聊天对话模式
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],
        }

    async with aiohttp.ClientSession() as session:
        async with session.post(base_url, headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(
                    f"OpenAI API request failed with status {response.status}: {await response.text()}"  # noqa: E501
                )

            result = await response.json()
            content = result["choices"][0]["message"]["content"]

            if chat_with_nlp:
                parsed_content = json.loads(content)
                return parsed_content["message"]
            else:
                return content


def VibeHelloWorld(
    message: str, chat_with_nlp: bool = True
) -> Literal["hello world"] | str:
    """AI-powered Hello World generator function.

    Args:
        message: Input message
        chat_with_nlp: If True, returns structured "hello world" output.
                      If False, returns normal chat response.

    Raises:
        TypeError: If message is not a string or chat_with_nlp is not a boolean.
    """
    # Type validation
    if not isinstance(message, str):
        raise TypeError(f"message must be a string, got {type(message).__name__}")

    if not isinstance(chat_with_nlp, bool):
        raise TypeError(
            f"chat_with_nlp must be a boolean, got {type(chat_with_nlp).__name__}"
        )

    return asyncio.run(_generate_with_ai_async(message, chat_with_nlp))
