import unittest

from services.incidents import parse_builder_proposal


class BuilderProposalParserTests(unittest.TestCase):
    def test_parses_builder_proposal(self):
        output = """
ACTION_TYPE: operational
TARGET: OPENAI_API_KEY server environment
RATIONALE: Current code already blocks placeholders.
CHANGE: Set a valid key and restart the server.
TEST: Execute a new run and confirm it reaches the model.
RISK: low
APPROVAL_NEEDED: no
"""

        result = parse_builder_proposal(output)

        self.assertEqual(result["action_type"], "operational")
        self.assertIn("OPENAI_API_KEY", result["target"])
        self.assertEqual(result["risk"], "low")
        self.assertEqual(result["approval_needed"], "no")

    def test_missing_fields_remain_none(self):
        result = parse_builder_proposal(
            "ACTION_TYPE: no_action\nRISK: low"
        )

        self.assertEqual(result["action_type"], "no_action")
        self.assertEqual(result["risk"], "low")
        self.assertIsNone(result["target"])
        self.assertIsNone(result["change"])
        self.assertIsNone(result["test"])
        self.assertIsNone(result["approval_needed"])


if __name__ == "__main__":
    unittest.main()
