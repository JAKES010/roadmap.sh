import contextlib
import importlib.util
import io
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "github_user_actvity"
    / "main.py"
)
SPEC = importlib.util.spec_from_file_location("github_user_activity", SCRIPT_PATH)
github_user_activity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(github_user_activity)


class FormatEventTests(unittest.TestCase):
    def test_formats_push_event(self):
        event = {
            "type": "PushEvent",
            "created_at": "2026-10-19T10:00:00Z",
            "repo": {"name": "octo/project"},
            "payload": {"size": 2},
        }

        self.assertEqual(
            github_user_activity.format_event(event),
            "2026-10-19T10:00:00Z: pushed 2 commit(s) to octo/project",
        )

    def test_formats_issue_and_pull_request_events(self):
        issue = {
            "type": "IssuesEvent",
            "repo": {"name": "octo/project"},
            "payload": {"action": "opened", "issue": {"title": "Add search"}},
        }
        pull_request = {
            "type": "PullRequestEvent",
            "repo": {"name": "octo/project"},
            "payload": {
                "action": "closed",
                "pull_request": {"title": "Improve search"},
            },
        }

        self.assertIn("opened issue 'Add search'", github_user_activity.format_event(issue))
        self.assertIn(
            "closed pull request 'Improve search'",
            github_user_activity.format_event(pull_request),
        )

    def test_formats_unknown_event_without_crashing(self):
        summary = github_user_activity.format_event({"type": "NewEvent"})

        self.assertIn("NewEvent", summary)
        self.assertIn("an unknown repository", summary)


class FetchEventsTests(unittest.TestCase):
    @patch.object(github_user_activity.urllib.request, "urlopen")
    def test_fetches_events_with_github_headers(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = json.dumps([]).encode("utf-8")
        urlopen.return_value = response

        events = github_user_activity.fetch_events("sample-user")

        self.assertEqual(events, [])
        request = urlopen.call_args.args[0]
        self.assertIn("/users/sample-user/events", request.full_url)
        self.assertEqual(request.get_header("User-agent"), "github-user-activity-cli")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 10)

    @patch.object(github_user_activity.urllib.request, "urlopen")
    def test_rejects_unexpected_response_shape(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"message":"not an event list"}'
        urlopen.return_value = response

        with self.assertRaisesRegex(ValueError, "unexpected activity response"):
            github_user_activity.fetch_events("sample-user")


class MainTests(unittest.TestCase):
    def test_empty_activity_has_friendly_output(self):
        output = io.StringIO()
        with patch.object(github_user_activity, "fetch_events", return_value=[]):
            with contextlib.redirect_stdout(output):
                exit_code = github_user_activity.main(["sample-user"])

        self.assertEqual(exit_code, 0)
        self.assertIn("No recent public activity", output.getvalue())

    def test_http_and_network_errors_are_reported(self):
        for failure, expected_message in (
            (HTTPError("url", 404, "Not Found", {}, None), "not found on GitHub"),
            (HTTPError("url", 403, "Forbidden", {}, None), "rate limited"),
            (URLError("timed out"), "Could not reach GitHub"),
        ):
            with self.subTest(failure=failure):
                error_output = io.StringIO()
                with patch.object(
                    github_user_activity, "fetch_events", side_effect=failure
                ):
                    with contextlib.redirect_stderr(error_output):
                        exit_code = github_user_activity.main(["sample-user"])

                self.assertEqual(exit_code, 1)
                self.assertIn(expected_message, error_output.getvalue())

    def test_requires_exactly_one_username(self):
        error_output = io.StringIO()
        with contextlib.redirect_stderr(error_output):
            exit_code = github_user_activity.main([])

        self.assertEqual(exit_code, 2)
        self.assertIn("Usage:", error_output.getvalue())


if __name__ == "__main__":
    unittest.main()
