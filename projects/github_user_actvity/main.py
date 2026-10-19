import json
import sys
import urllib.error
import urllib.parse
import urllib.request


API_URL = "https://api.github.com/users/{username}/events"
REQUEST_TIMEOUT = 10


def format_event(event):
    event_type = event.get("type", "UnknownEvent")
    repository = event.get("repo")
    repository_name = repository.get("name") if isinstance(repository, dict) else None
    repository_name = repository_name or "an unknown repository"
    payload = event.get("payload")
    payload = payload if isinstance(payload, dict) else {}

    if event_type == "PushEvent":
        commit_count = payload.get("size")
        if not isinstance(commit_count, int) or isinstance(commit_count, bool):
            commits = payload.get("commits")
            commit_count = len(commits) if isinstance(commits, list) else 0
        description = f"pushed {commit_count} commit(s) to {repository_name}"
    elif event_type == "IssuesEvent":
        action = payload.get("action", "updated")
        issue = payload.get("issue")
        title = issue.get("title") if isinstance(issue, dict) else None
        description = f"{action} issue"
        if title:
            description += f" '{title}'"
        description += f" in {repository_name}"
    elif event_type == "PullRequestEvent":
        action = payload.get("action", "updated")
        pull_request = payload.get("pull_request")
        title = pull_request.get("title") if isinstance(pull_request, dict) else None
        description = f"{action} pull request"
        if title:
            description += f" '{title}'"
        description += f" in {repository_name}"
    elif event_type == "IssueCommentEvent":
        issue = payload.get("issue")
        title = issue.get("title") if isinstance(issue, dict) else None
        description = "commented on"
        if title:
            description += f" '{title}'"
        else:
            description += " an issue"
        description += f" in {repository_name}"
    elif event_type == "WatchEvent":
        description = f"starred {repository_name}"
    elif event_type == "ForkEvent":
        description = f"forked {repository_name}"
    elif event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "resource")
        ref = payload.get("ref")
        description = f"created {ref_type}"
        if ref:
            description += f" '{ref}'"
        description += f" in {repository_name}"
    elif event_type == "DeleteEvent":
        ref_type = payload.get("ref_type", "resource")
        ref = payload.get("ref")
        description = f"deleted {ref_type}"
        if ref:
            description += f" '{ref}'"
        description += f" in {repository_name}"
    elif event_type == "ReleaseEvent":
        release = payload.get("release")
        release_name = release.get("name") if isinstance(release, dict) else None
        release_name = release_name or "a release"
        description = f"published {release_name} in {repository_name}"
    else:
        description = f"had a {event_type} in {repository_name}"

    created_at = event.get("created_at", "Unknown time")
    return f"{created_at}: {description}"


def fetch_events(username):
    escaped_username = urllib.parse.quote(username, safe="")
    request = urllib.request.Request(
        API_URL.format(username=escaped_username),
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-user-activity-cli",
        },
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        try:
            events = json.loads(response.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError("GitHub returned an invalid JSON response.") from error

    if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
        raise ValueError("GitHub returned an unexpected activity response.")
    return events


def main(arguments):
    if len(arguments) != 1:
        print("Usage: python3 main.py <github_username>", file=sys.stderr)
        return 2

    username = arguments[0]
    try:
        events = fetch_events(username)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            print(f"Error: User '{username}' not found on GitHub.", file=sys.stderr)
        elif error.code == 403:
            print("Error: GitHub API access was denied or rate limited.", file=sys.stderr)
        else:
            print(f"Error: GitHub API returned HTTP {error.code}.", file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(f"Error: Could not reach GitHub: {error.reason}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if not events:
        print(f"No recent public activity found for '{username}'.")
        return 0

    for event in events:
        print(f"- {format_event(event)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
