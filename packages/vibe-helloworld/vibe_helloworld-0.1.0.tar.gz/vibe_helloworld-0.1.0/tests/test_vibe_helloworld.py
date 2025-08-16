import os
from unittest.mock import AsyncMock, patch

import pytest

from vibe_helloworld import VibeHelloWorld


class TestVibeHelloWorld:
    """Test VibeHelloWorld function with mocked API responses."""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            yield

    @pytest.fixture
    def mock_structured_response(self):
        """Mock structured response for chat_with_nlp=True."""
        return {"choices": [{"message": {"content": '{"message": "hello world"}'}}]}

    @pytest.fixture
    def mock_chat_response(self):
        """Mock chat response for chat_with_nlp=False."""
        return {
            "choices": [
                {
                    "message": {
                        "content": "Hello! I'm an AI assistant. How can I help you today?"  # noqa: E501
                    }
                }
            ]
        }

    @patch("aiohttp.ClientSession.post")
    def test_structured_output_mode(
        self, mock_post, mock_env_vars, mock_structured_response
    ):
        """Test structured output mode (chat_with_nlp=True)."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_structured_response)
        mock_post.return_value.__aenter__.return_value = mock_response

        result = VibeHelloWorld("test message", chat_with_nlp=True)
        assert result == "hello world"

        # Verify the request was made with structured format
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args.kwargs["json"]
        assert "response_format" in payload
        assert payload["response_format"]["type"] == "json_schema"

    @patch("aiohttp.ClientSession.post")
    def test_chat_mode(self, mock_post, mock_env_vars, mock_chat_response):
        """Test normal chat mode (chat_with_nlp=False)."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_chat_response)
        mock_post.return_value.__aenter__.return_value = mock_response

        result = VibeHelloWorld("How are you?", chat_with_nlp=False)
        assert result == "Hello! I'm an AI assistant. How can I help you today?"

        # Verify the request was made without structured format
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args.kwargs["json"]
        assert "response_format" not in payload

    @patch("aiohttp.ClientSession.post")
    def test_default_behavior(self, mock_post, mock_env_vars, mock_structured_response):
        """Test that default behavior is structured mode."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_structured_response)
        mock_post.return_value.__aenter__.return_value = mock_response

        # Test without specifying chat_with_nlp parameter
        result = VibeHelloWorld("test message")
        assert result == "hello world"

    def test_missing_api_key(self):
        """Test error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                VibeHelloWorld("test message")

    @patch("aiohttp.ClientSession.post")
    def test_api_error_handling(self, mock_post, mock_env_vars):
        """Test handling of API errors."""
        # Mock failed HTTP response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")
        mock_post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(
            Exception, match="OpenAI API request failed with status 401"
        ):
            VibeHelloWorld("test message")

    @patch("aiohttp.ClientSession.post")
    def test_print_functionality(
        self, mock_post, mock_env_vars, mock_structured_response, capsys
    ):
        """Test that results can be printed correctly."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_structured_response)
        mock_post.return_value.__aenter__.return_value = mock_response

        # Test structured output print
        result = VibeHelloWorld("test message", chat_with_nlp=True)
        print(result)

        captured = capsys.readouterr()
        assert "hello world" in captured.out

    @patch("aiohttp.ClientSession.post")
    def test_chat_print_functionality(
        self, mock_post, mock_env_vars, mock_chat_response, capsys
    ):
        """Test that chat results can be printed correctly."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_chat_response)
        mock_post.return_value.__aenter__.return_value = mock_response

        # Test chat output print
        result = VibeHelloWorld("How are you?", chat_with_nlp=False)
        print(result)

        captured = capsys.readouterr()
        assert "Hello! I'm an AI assistant" in captured.out
