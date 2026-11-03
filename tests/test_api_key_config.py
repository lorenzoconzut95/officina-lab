import os
import unittest
from unittest.mock import patch

from services.llm_provider import (
    get_api_key_status,
    is_configured
)


class ApiKeyConfigurationTests(unittest.TestCase):
    def test_missing_key_is_not_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            status = get_api_key_status()

        self.assertFalse(status["configured"])
        self.assertEqual(status["reason"], "missing")

    def test_placeholder_key_is_rejected(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "LA_TUA_CHIAVE"},
            clear=True
        ):
            status = get_api_key_status()

        self.assertFalse(status["configured"])
        self.assertEqual(status["reason"], "placeholder")
        self.assertFalse(is_configured())

    def test_realistic_key_shape_is_accepted(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "sk-proj-example-valid-looking-key"},
            clear=True
        ):
            status = get_api_key_status()

            self.assertTrue(status["configured"])
            self.assertEqual(status["reason"], "ok")
            self.assertTrue(is_configured())


if __name__ == "__main__":
    unittest.main()
