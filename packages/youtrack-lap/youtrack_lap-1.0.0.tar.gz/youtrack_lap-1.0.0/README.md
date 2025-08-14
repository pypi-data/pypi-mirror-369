# YouTrack REST Client

A very limited client library for accessing YouTrack REST API

## Installation

Using UV:
```bash
uv add youtrack-rest-client
```

## Usage

```python
from youtrack_rest_client import Connection, Issue, Project

# Initialize client
client = Connection(base_url="https://your-instance.youtrack.cloud", token="your-token")

# Get projects
projects = client.get_projects()

# Work with a specific project
project = Project(client, 'PROJECT-ID')
issues = project.get_issues()

# Work with a specific issue
issue = Issue(client, 'PROJECT-123')
work_items = issue.get_work_items()
```

## Development

Install dependencies:
```bash
uv sync --dev
```

Create token file:
```bash
mkdir -p secrets
echo "your-youtrack-token" > secrets/yt_token.txt
```

Run example:
```bash
uv run python examples/basic_usage.py
```