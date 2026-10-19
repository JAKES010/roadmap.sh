import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_SOURCE = PROJECT_ROOT / "projects" / "task_tracker" / "main.py"


class TaskTrackerCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.project_directory = self.root / "task_tracker"
        self.project_directory.mkdir()
        self.caller_directory = self.root / "caller"
        self.caller_directory.mkdir()
        self.script = self.project_directory / "main.py"
        self.data_file = self.project_directory / "task_file.json"
        shutil.copy2(SCRIPT_SOURCE, self.script)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(self.script), *arguments],
            cwd=self.caller_directory,
            capture_output=True,
            text=True,
        )

    def read_tasks(self):
        return json.loads(self.data_file.read_text(encoding="utf-8"))

    def test_help_works_without_loading_task_data(self):
        result = self.run_cli("--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Commands:", result.stdout)
        self.assertFalse(self.data_file.exists())

    def test_crud_status_changes_and_listing(self):
        added = self.run_cli("add", "Buy groceries")
        self.assertEqual(added.returncode, 0, added.stderr)
        self.assertIn("ID: 1", added.stdout)

        marked = self.run_cli("mark-in-progress", "1")
        self.assertEqual(marked.returncode, 0, marked.stderr)
        filtered = self.run_cli("list", "in-progress")
        self.assertEqual(filtered.returncode, 0, filtered.stderr)
        self.assertIn("[IN-PROGRESS]", filtered.stdout)

        updated = self.run_cli("update", "1", "Buy groceries and cook dinner")
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual(
            self.read_tasks()[0]["description"],
            "Buy groceries and cook dinner",
        )

        marked_done = self.run_cli("mark-done", "1")
        self.assertEqual(marked_done.returncode, 0, marked_done.stderr)
        self.assertEqual(self.read_tasks()[0]["status"], "done")

        deleted = self.run_cli("delete", "1")
        self.assertEqual(deleted.returncode, 0, deleted.stderr)
        self.assertEqual(self.read_tasks(), [])

    def test_empty_list_is_successful(self):
        result = self.run_cli("list")

        self.assertEqual(result.returncode, 0)
        self.assertIn("No tasks found.", result.stdout)

    def test_invalid_json_and_task_data_are_preserved(self):
        for invalid_data in (b"{invalid", b'{"not": "a list"}'):
            with self.subTest(invalid_data=invalid_data):
                self.data_file.write_bytes(invalid_data)

                result = self.run_cli("add", "Do not overwrite this file")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("file was left unchanged", result.stderr)
                self.assertEqual(self.data_file.read_bytes(), invalid_data)

    def test_invalid_arguments_and_empty_descriptions_do_not_write(self):
        self.data_file.write_text("[]", encoding="utf-8")
        original_data = self.data_file.read_bytes()

        for arguments in (
            ("add", "   "),
            ("add", "valid", "extra"),
            ("list", "todo", "extra"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.data_file.read_bytes(), original_data)

    def test_task_file_is_relative_to_script_not_caller(self):
        result = self.run_cli("add", "Run from another directory")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.data_file.exists())
        self.assertFalse((self.caller_directory / "task_file.json").exists())


if __name__ == "__main__":
    unittest.main()
