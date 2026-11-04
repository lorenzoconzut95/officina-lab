import unittest

from services.project_files import (
    list_project_files,
    read_project_file
)


class ProjectFileToolsTests(unittest.TestCase):
    def test_lists_source_and_test_files(self):
        files = list_project_files(limit=200)

        self.assertIn(
            "services/llm_provider.py",
            files
        )
        self.assertIn(
            "tests/test_api_key_config.py",
            files
        )

    def test_reads_allowed_project_file(self):
        result = read_project_file(
            "services/llm_provider.py"
        )

        self.assertEqual(
            result["path"],
            "services/llm_provider.py"
        )
        self.assertIn(
            "get_api_key_status",
            result["content"]
        )

    def test_blocks_database_file(self):
        result = read_project_file(
            "tasks.db"
        )

        self.assertEqual(
            result["error"],
            "file_not_allowed"
        )

    def test_blocks_path_traversal(self):
        result = read_project_file(
            "../secret.txt"
        )

        self.assertEqual(
            result["error"],
            "file_not_allowed"
        )


if __name__ == "__main__":
    unittest.main()
