import unittest

from services.incidents import parse_structured_analysis


class IncidentReportParserTests(unittest.TestCase):
    def test_parses_all_structured_fields(self):
        output = """
SYMPTOM: API call fails with 401.
EVIDENCE: Error log shows invalid_api_key.
ROOT_CAUSE: Placeholder key reached provider.
CONFIDENCE: high
MINIMAL_TEST: Set OPENAI_API_KEY=LA_TUA_CHIAVE and execute.
SMALLEST_FIX: Reject placeholder before run_llm().
"""

        result = parse_structured_analysis(output)

        self.assertEqual(
            result["symptom"],
            "API call fails with 401."
        )
        self.assertEqual(
            result["evidence"],
            "Error log shows invalid_api_key."
        )
        self.assertEqual(
            result["root_cause"],
            "Placeholder key reached provider."
        )
        self.assertEqual(result["confidence"], "high")
        self.assertIn(
            "LA_TUA_CHIAVE",
            result["minimal_test"]
        )
        self.assertIn(
            "run_llm",
            result["smallest_fix"]
        )

    def test_missing_sections_remain_none(self):
        result = parse_structured_analysis(
            "SYMPTOM: Something failed.\nCONFIDENCE: low"
        )

        self.assertEqual(
            result["symptom"],
            "Something failed."
        )
        self.assertEqual(
            result["confidence"],
            "low"
        )
        self.assertIsNone(result["evidence"])
        self.assertIsNone(result["root_cause"])
        self.assertIsNone(result["minimal_test"])
        self.assertIsNone(result["smallest_fix"])


if __name__ == "__main__":
    unittest.main()
