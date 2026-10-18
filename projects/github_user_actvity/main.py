import sys
import json
import urllib.request

if len(sys.argv) < 2:
    print("Usage: python main.py <github_username>")
    sys.exit(1)

github_username = sys.argv[1]
url = f"https://api.github.com/users/{github_username}/events"

try:
    with urllib.request.urlopen(url) as response:
        data =json.loads(response.read().decode())
        for item in data:
            print(item)

except urllib.error.HTTPError as e:
    if e.code == 404:
        print(f"Error: User '{github_username}' not found on GitHub.")
    else:
        print(f"HTTP Error:{e.code}")
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")
    sys.exit(1)
