"""
Unit tests for the OpenRouter service layer.

All external API calls are mocked. Tests cover:
- Successful response
- Malformed JSON response
- Timeout
- Retry behavior
- Fallback response
- Prompt loading
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services.openrouter import (
    ReviewSummary,
    _call_llm,
    _format_prompt,
    _get_config,
    _load_prompt,
    _try_parse_and_validate,
    generate_review_summary,
    get_config,
    reset_config,
)


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def clear_config():
    """Reset the config singleton before and after each test."""
    reset_config()
    yield
    reset_config()


@pytest.fixture
def mock_env_api_key():
    """Set a fake API key in the environment."""
    old = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "test-key-12345"
    yield
    if old is None:
        del os.environ["OPENROUTER_API_KEY"]
    else:
        os.environ["OPENROUTER_API_KEY"] = old


@pytest.fixture
def mock_env_no_key():
    """Ensure no API key is set."""
    old = os.environ.get("OPENROUTER_API_KEY")
    if "OPENROUTER_API_KEY" in os.environ:
        del os.environ["OPENROUTER_API_KEY"]
    yield
    if old is not None:
        os.environ["OPENROUTER_API_KEY"] = old


@pytest.fixture
def sample_reviews() -> List[str]:
    return [
        "This milk is so fresh and creamy, my kids love it!",
        "Great quality, stays fresh for a long time.",
        "Best milk for coffee, froths perfectly.",
        "A bit expensive but worth the quality.",
    ]


@pytest.fixture
def valid_llm_response() -> Dict[str, Any]:
    return {
        "summary": "Customers love the fresh and creamy quality of this milk.",
        "pros": [
            "Fresh and creamy taste",
            "Stays fresh for a long time",
            "Froths perfectly for coffee",
        ],
        "cons": [
            "A bit expensive",
        ],
        "trust_reason": "Consistent positive feedback on freshness and quality builds trust.",
    }


# ── Prompt loading tests ─────────────────────────────────────────────


class TestPromptLoading:
    def test_load_prompt_success(self):
        """Should load the prompt template file successfully."""
        content = _load_prompt("review_summary.txt")
        assert "{product_name}" in content
        assert "{reviews_text}" in content
        assert "summary" in content
        assert "pros" in content
        assert "cons" in content
        assert "trust_reason" in content

    def test_load_prompt_file_not_found(self):
        """Should raise FileNotFoundError for missing prompt file."""
        with pytest.raises(FileNotFoundError):
            _load_prompt("nonexistent_prompt.txt")

    def test_load_prompt_caching(self):
        """Should cache prompt content after first load."""
        # Clear cache by accessing internal state
        from app.services.openrouter import _PROMPT_CACHE
        _PROMPT_CACHE.clear()

        content1 = _load_prompt("review_summary.txt")
        content2 = _load_prompt("review_summary.txt")
        assert content1 == content2

    def test_format_prompt(self):
        """Should substitute placeholders correctly."""
        template = "Product: {product_name}\nReviews: {reviews_text}"
        result = _format_prompt(
            template,
            product_name="Test Milk",
            reviews_text="- Great!\n- Awesome!",
        )
        assert "Product: Test Milk" in result
        assert "Reviews: - Great!\n- Awesome!" in result


# ── Configuration tests ──────────────────────────────────────────────


class TestConfiguration:
    def test_config_from_env_defaults(self):
        """Should use defaults when env vars are not set."""
        config = _get_config()
        assert config.api_key == ""
        assert config.base_url == "https://openrouter.ai/api/v1"
        assert config.model == "deepseek/deepseek-chat-v3"
        assert config.request_timeout == 30.0
        assert config.max_retries == 3
        assert config.initial_retry_delay == 1.0
        assert config.max_retry_delay == 10.0
        assert config.backoff_multiplier == 2.0

    def test_config_from_env_custom(self, mock_env_api_key):
        """Should read custom values from environment variables."""
        os.environ["OPENROUTER_BASE_URL"] = "https://custom.example.com/v1"
        os.environ["OPENROUTER_MODEL"] = "custom/model"
        os.environ["OPENROUTER_TIMEOUT"] = "15.0"
        os.environ["OPENROUTER_MAX_RETRIES"] = "5"
        os.environ["OPENROUTER_INITIAL_RETRY_DELAY"] = "0.5"
        os.environ["OPENROUTER_MAX_RETRY_DELAY"] = "20.0"
        os.environ["OPENROUTER_BACKOFF_MULTIPLIER"] = "3.0"

        reset_config()
        config = _get_config()

        assert config.api_key == "test-key-12345"
        assert config.base_url == "https://custom.example.com/v1"
        assert config.model == "custom/model"
        assert config.request_timeout == 15.0
        assert config.max_retries == 5
        assert config.initial_retry_delay == 0.5
        assert config.max_retry_delay == 20.0
        assert config.backoff_multiplier == 3.0

        # Cleanup
        for key in [
            "OPENROUTER_BASE_URL", "OPENROUTER_MODEL", "OPENROUTER_TIMEOUT",
            "OPENROUTER_MAX_RETRIES", "OPENROUTER_INITIAL_RETRY_DELAY",
            "OPENROUTER_MAX_RETRY_DELAY", "OPENROUTER_BACKOFF_MULTIPLIER",
        ]:
            os.environ.pop(key, None)

    def test_get_config_and_reset(self):
        """Should return the same instance and reset properly."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

        reset_config()
        config3 = get_config()
        assert config3 is not config1


# ── Response validation and repair tests ─────────────────────────────


class TestResponseValidation:
    def test_parse_valid_json(self):
        """Should parse and validate a valid JSON response."""
        content = json.dumps({
            "summary": "Great product",
            "pros": ["Fresh"],
            "cons": [],
            "trust_reason": "Trustworthy",
        })
        parsed, error = _try_parse_and_validate(content, ReviewSummary)
        assert parsed is not None
        assert error is None
        assert parsed.summary == "Great product"
        assert parsed.pros == ["Fresh"]
        assert parsed.cons == []
        assert parsed.trust_reason == "Trustworthy"

    def test_parse_malformed_json(self):
        """Should return None for completely invalid content."""
        parsed, error = _try_parse_and_validate("not json at all", ReviewSummary)
        assert parsed is None
        assert error is not None

    def test_repair_code_fences(self):
        """Should strip markdown code fences and parse."""
        content = """```json
{
    "summary": "Great product",
    "pros": ["Fresh"],
    "cons": [],
    "trust_reason": "Trustworthy"
}
```"""
        parsed, error = _try_parse_and_validate(content, ReviewSummary)
        assert parsed is not None
        assert error is None
        assert parsed.summary == "Great product"

    def test_repair_code_fences_no_lang(self):
        """Should strip code fences without language specifier."""
        content = """```
{
    "summary": "Great product",
    "pros": ["Fresh"],
    "cons": [],
    "trust_reason": "Trustworthy"
}
```"""
        parsed, error = _try_parse_and_validate(content, ReviewSummary)
        assert parsed is not None
        assert error is None
        assert parsed.summary == "Great product"

    def test_repair_extract_json_object(self):
        """Should extract JSON object from surrounding text."""
        content = "Here is the result: {\"summary\": \"Great\", \"pros\": [\"Fresh\"], \"cons\": [], \"trust_reason\": \"Good\"}. Hope this helps!"
        parsed, error = _try_parse_and_validate(content, ReviewSummary)
        assert parsed is not None
        assert error is None
        assert parsed.summary == "Great"

    def test_repair_accepts_partial_json(self):
        """Should accept JSON with missing fields and use defaults."""
        content = json.dumps({"unexpected_field": "value"})
        parsed, error = _try_parse_and_validate(content, ReviewSummary)
        assert parsed is not None
        assert error is None
        assert parsed.summary == ""
        assert parsed.pros == []
        assert parsed.cons == []
        assert parsed.trust_reason == ""


# ── _call_llm tests ──────────────────────────────────────────────────


class TestCallLlm:
    def test_no_api_key_returns_none(self, mock_env_no_key):
        """Should return None when no API key is configured."""
        config = _get_config()
        result = _call_llm(config, "system", "user")
        assert result is None

    @patch("app.services.openrouter.httpx.Client")
    def test_successful_call(self, mock_client_class, mock_env_api_key):
        """Should return the response content on success."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "{\"key\": \"value\"}"}}]
        }
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance

        config = _get_config()
        result = _call_llm(config, "system prompt", "user prompt")
        assert result == '{"key": "value"}'

    @patch("app.services.openrouter.httpx.Client")
    def test_timeout_triggers_retry(self, mock_client_class, mock_env_api_key):
        """Should retry on timeout and eventually return None."""
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.side_effect = httpx.TimeoutException("timeout")
        mock_client_class.return_value = mock_instance

        config = _get_config()
        config.max_retries = 2
        config.initial_retry_delay = 0.01
        config.max_retry_delay = 0.1

        result = _call_llm(config, "system", "user")
        assert result is None
        assert mock_instance.post.call_count == 2

    @patch("app.services.openrouter.httpx.Client")
    def test_http_error_triggers_retry(self, mock_client_class, mock_env_api_key):
        """Should retry on HTTP errors and eventually return None."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )

        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance

        config = _get_config()
        config.max_retries = 3
        config.initial_retry_delay = 0.01
        config.max_retry_delay = 0.1

        result = _call_llm(config, "system", "user")
        assert result is None
        assert mock_instance.post.call_count == 3

    @patch("app.services.openrouter.httpx.Client")
    def test_success_on_retry(self, mock_client_class, mock_env_api_key):
        """Should succeed on the second attempt after a failure."""
        mock_response_success = MagicMock()
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.json.return_value = {
            "choices": [{"message": {"content": "{\"ok\": true}"}}]
        }

        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 502
        mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad gateway", request=MagicMock(), response=mock_response_fail
        )

        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.side_effect = [mock_response_fail, mock_response_success]
        mock_client_class.return_value = mock_instance

        config = _get_config()
        config.max_retries = 3
        config.initial_retry_delay = 0.01
        config.max_retry_delay = 0.1

        result = _call_llm(config, "system", "user")
        assert result == '{"ok": true}'
        assert mock_instance.post.call_count == 2


# ── generate_review_summary tests ────────────────────────────────────


class TestGenerateReviewSummary:
    def test_no_api_key_returns_fallback(self, mock_env_no_key, sample_reviews):
        """Should return fallback when no API key is configured."""
        result = generate_review_summary("Test Milk", sample_reviews)
        assert result == {"summary": "", "pros": [], "cons": [], "trust_reason": ""}

    def test_empty_reviews_returns_fallback(self, mock_env_api_key):
        """Should return fallback when reviews list is empty."""
        result = generate_review_summary("Test Milk", [])
        assert result == {"summary": "", "pros": [], "cons": [], "trust_reason": ""}

    @patch("app.services.openrouter.httpx.Client")
    def test_successful_response(
        self, mock_client_class, mock_env_api_key, sample_reviews, valid_llm_response
    ):
        """Should return parsed and validated response on success."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(valid_llm_response)}}]
        }
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance

        result = generate_review_summary("Fresh Milk", sample_reviews)
        assert result["summary"] == valid_llm_response["summary"]
        assert result["pros"] == valid_llm_response["pros"]
        assert result["cons"] == valid_llm_response["cons"]
        assert result["trust_reason"] == valid_llm_response["trust_reason"]

    @patch("app.services.openrouter.httpx.Client")
    def test_malformed_json_response(
        self, mock_client_class, mock_env_api_key, sample_reviews
    ):
        """Should return fallback when LLM returns malformed JSON."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "not valid json at all"}}]
        }
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance

        result = generate_review_summary("Fresh Milk", sample_reviews)
        assert result == {"summary": "", "pros": [], "cons": [], "trust_reason": ""}

    @patch("app.services.openrouter.httpx.Client")
    def test_timeout_returns_fallback(
        self, mock_client_class, mock_env_api_key, sample_reviews
    ):
        """Should return fallback on timeout."""
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.side_effect = httpx.TimeoutException("timeout")
        mock_client_class.return_value = mock_instance

        config = _get_config()
        config.max_retries = 2
        config.initial_retry_delay = 0.01
        config.max_retry_delay = 0.1

        result = generate_review_summary("Fresh Milk", sample_reviews)
        assert result == {"summary": "", "pros": [], "cons": [], "trust_reason": ""}

    @patch("app.services.openrouter.httpx.Client")
    def test_retry_then_success(
        self, mock_client_class, mock_env_api_key, sample_reviews, valid_llm_response
    ):
        """Should succeed after a retry."""
        mock_response_success = MagicMock()
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.json.return_value = {
            "choices": [{"message": {"content": json.dumps(valid_llm_response)}}]
        }

        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 502
        mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad gateway", request=MagicMock(), response=mock_response_fail
        )

        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.side_effect = [mock_response_fail, mock_response_success]
        mock_client_class.return_value = mock_instance

        config = _get_config()
        config.max_retries = 3
        config.initial_retry_delay = 0.01
        config.max_retry_delay = 0.1

        result = generate_review_summary("Fresh Milk", sample_reviews)
        assert result["summary"] == valid_llm_response["summary"]
        assert mock_instance.post.call_count == 2

    @patch("app.services.openrouter.httpx.Client")
    def test_repair_code_fences_in_response(
        self, mock_client_class, mock_env_api_key, sample_reviews, valid_llm_response
    ):
        """Should repair response wrapped in markdown code fences."""
        fenced_content = f"```json\n{json.dumps(valid_llm_response)}\n```"
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": fenced_content}}]
        }
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance

        result = generate_review_summary("Fresh Milk", sample_reviews)
        assert result["summary"] == valid_llm_response["summary"]

    @patch("app.services.openrouter.httpx.Client")
    def test_repair_extract_json(
        self, mock_client_class, mock_env_api_key, sample_reviews, valid_llm_response
    ):
        """Should extract JSON object from surrounding text."""
        wrapped_content = f"Here is the analysis: {json.dumps(valid_llm_response)}. Hope this helps!"
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": wrapped_content}}]
        }
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_instance

        result = generate_review_summary("Fresh Milk", sample_reviews)
        assert result["summary"] == valid_llm_response["summary"]

    def test_prompt_loading_integration(self, mock_env_api_key):
        """Should load and format the prompt correctly (without calling LLM)."""
        from app.services.openrouter import _load_prompt, _format_prompt

        template = _load_prompt("review_summary.txt")
        reviews = ["Great product!", "Love it!"]
        reviews_text = "\n".join(f"- {r}" for r in reviews)
        formatted = _format_prompt(
            template,
            product_name="Test Product",
            reviews_text=reviews_text,
        )

        assert "Test Product" in formatted
        assert "- Great product!" in formatted
        assert "- Love it!" in formatted
        assert "summary" in formatted
        assert "pros" in formatted
        assert "cons" in formatted
        assert "trust_reason" in formatted