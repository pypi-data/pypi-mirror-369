"""
Tests for the intelligence module.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock

from dacp.intelligence import invoke_intelligence


class TestInvokeIntelligence(unittest.TestCase):
    """Test the main invoke_intelligence function."""

    def test_missing_engine_raises_error(self):
        """Test that missing engine raises ValueError."""
        config = {"model": "gpt-4"}
        with self.assertRaises(ValueError, msg="Engine must be specified"):
            invoke_intelligence("test prompt", config)

    def test_unsupported_engine_raises_error(self):
        """Test that unsupported engine raises ValueError."""
        config = {"engine": "unsupported_engine"}
        with self.assertRaises(ValueError, msg="Unsupported engine"):
            invoke_intelligence("test prompt", config)

    @patch("dacp.intelligence._invoke_openai")
    def test_openai_engine_calls_correct_function(self, mock_openai):
        """Test that OpenAI engine calls the correct function."""
        mock_openai.return_value = "OpenAI response"
        config = {"engine": "openai", "model": "gpt-4"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "OpenAI response")
        mock_openai.assert_called_once_with("test prompt", config)

    @patch("dacp.intelligence._invoke_anthropic")
    def test_anthropic_engine_calls_correct_function(self, mock_anthropic):
        """Test that Anthropic engine calls the correct function."""
        mock_anthropic.return_value = "Anthropic response"
        config = {"engine": "anthropic", "model": "claude-3-haiku-20240307"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "Anthropic response")
        mock_anthropic.assert_called_once_with("test prompt", config)

    @patch("dacp.intelligence._invoke_azure_openai")
    def test_azure_engine_calls_correct_function(self, mock_azure):
        """Test that Azure engine calls the correct function."""
        mock_azure.return_value = "Azure response"
        config = {"engine": "azure", "model": "gpt-4"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "Azure response")
        mock_azure.assert_called_once_with("test prompt", config)

    @patch("dacp.intelligence._invoke_local")
    def test_local_engine_calls_correct_function(self, mock_local):
        """Test that local engine calls the correct function."""
        mock_local.return_value = "Local response"
        config = {"engine": "local", "model": "llama2"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "Local response")
        mock_local.assert_called_once_with("test prompt", config)

    @patch("dacp.intelligence._invoke_grok")
    def test_grok_engine_calls_correct_function(self, mock_grok):
        """Test that Grok engine calls the correct function."""
        mock_grok.return_value = "Grok response"
        config = {"engine": "grok", "model": "grok-3-latest"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "Grok response")
        mock_grok.assert_called_once_with("test prompt", config)

    @patch("dacp.intelligence._invoke_grok")
    def test_xai_engine_alias_calls_grok_function(self, mock_grok):
        """Test that 'xai' engine alias calls the Grok function."""
        mock_grok.return_value = "xAI Grok response"
        config = {"engine": "xai", "model": "grok-3-latest"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "xAI Grok response")
        mock_grok.assert_called_once_with("test prompt", config)

    def test_supported_engines_include_grok(self):
        """Test that Grok is included in supported engines."""
        # Test that Grok is in the available engines list
        config = {"engine": "grok"}
        try:
            invoke_intelligence("test prompt", config)
        except ValueError as e:
            # If we get a ValueError, it should NOT be about unsupported engine
            self.assertNotIn("Unsupported engine: grok", str(e))
            # It might fail for other reasons (missing API key, etc.) which is fine
        except Exception:
            # Other exceptions are expected (missing API key, network, etc.)
            pass


class TestGrokIntelligence(unittest.TestCase):
    """Test Grok-specific intelligence functionality."""

    @patch("os.getenv")
    def test_grok_invoke_with_api_key(self, mock_getenv):
        """Test Grok invocation with API key."""
        # Mock the openai module
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client

        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Grok analysis result"
        mock_client.chat.completions.create.return_value = mock_response

        # Patch sys.modules to include our mock
        with patch.dict("sys.modules", {"openai": mock_openai}):
            from dacp.intelligence import _invoke_grok

            # Mock environment variable
            mock_getenv.return_value = "test-xai-api-key"

            config = {
                "engine": "grok",
                "model": "grok-3-latest",
                "temperature": 0.7,
                "max_tokens": 1500,
            }

            result = _invoke_grok("Analyze this security event", config)

            # Verify API key was retrieved
            mock_getenv.assert_called_with("XAI_API_KEY")

            # Verify OpenAI client was created with xAI endpoint
            mock_openai.OpenAI.assert_called_once_with(
                api_key="test-xai-api-key", base_url="https://api.x.ai/v1"
            )

            # Verify chat completion was called with correct parameters
            mock_client.chat.completions.create.assert_called_once_with(
                model="grok-3-latest",
                messages=[{"role": "user", "content": "Analyze this security event"}],
                temperature=0.7,
                max_tokens=1500,
            )

            self.assertEqual(result, "Grok analysis result")

    @patch("os.getenv")
    def test_grok_invoke_missing_api_key(self, mock_getenv):
        """Test Grok invocation fails with missing API key."""
        # Mock the openai module
        mock_openai = MagicMock()

        # Patch sys.modules to include our mock
        with patch.dict("sys.modules", {"openai": mock_openai}):
            from dacp.intelligence import _invoke_grok

            # Mock missing API key
            mock_getenv.return_value = None

            config = {"engine": "grok", "model": "grok-3-latest"}

            with self.assertRaises(ValueError) as context:
                _invoke_grok("test prompt", config)

            self.assertIn("xAI API key not found", str(context.exception))

    @patch("os.getenv")
    def test_grok_invoke_with_custom_config(self, mock_getenv):
        """Test Grok invocation with custom configuration."""
        # Mock the openai module
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client

        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Custom Grok response"
        mock_client.chat.completions.create.return_value = mock_response

        # Patch sys.modules to include our mock
        with patch.dict("sys.modules", {"openai": mock_openai}):
            from dacp.intelligence import _invoke_grok

            mock_getenv.return_value = "test-key"

            config = {
                "engine": "grok",
                "model": "grok-3-latest",
                "base_url": "https://custom.api.endpoint/v1",
                "temperature": 0.2,
                "max_tokens": 2000,
            }

            result = _invoke_grok("Custom prompt", config)

            # Verify custom endpoint was used
            mock_openai.OpenAI.assert_called_once_with(
                api_key="test-key", base_url="https://custom.api.endpoint/v1"
            )

            # Verify custom parameters were used
            mock_client.chat.completions.create.assert_called_once_with(
                model="grok-3-latest",
                messages=[{"role": "user", "content": "Custom prompt"}],
                temperature=0.2,
                max_tokens=2000,
            )

            self.assertEqual(result, "Custom Grok response")


if __name__ == "__main__":
    unittest.main()
