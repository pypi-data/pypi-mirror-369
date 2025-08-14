import os
from datetime import datetime
from youtrack_lap import Connection, ProjectsCollection, ProjectsResource, IssueResource, IssueCollection

YOUTRACK_URL = "https://r3recube.myjetbrains.com/youtrack/"

def read_token_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Token file not found: {file_path}")
        exit(1)

def main():
    token_file = os.path.expanduser("secrets/yt_token.txt")
    token = read_token_from_file(token_file)
    client = Connection(base_url=YOUTRACK_URL, token=token)

    print("\nI'm printing all projects on Youtrack")
    collection = ProjectsCollection(client)
    list_of_project = collection.list_projects()
    for project in list_of_project:
        print(f"Project {project['id']}: {project['name']}")
    
    print("\nI'm printing all issues of a specific project")
    collection = ProjectsCollection(client)
    list_of_project = collection.list_projects()
    project_id = list_of_project[0]['id']
    resource = ProjectsResource(client, project_id)
    issues = resource.list_issues(limit=500)
    for issue in issues:
        print(f"Issue {issue['id']}: {issue['summary']}")

    print("\nI'm printing all work items of a specific issue")
    collection = ProjectsCollection(client)
    list_of_project = collection.list_projects()
    project_id = list_of_project[0]['id']
    resource = ProjectsResource(client, project_id)
    issues = resource.list_issues(limit=500)
    issue_id = issues[0]['id']
    issue = IssueResource(client, issue_id)
    work_items = issue.list_work_items(limit=100)
    for item in work_items:
        print(f"Work item {item['id']}: {item['text']}")

if __name__ == "__main__":
    main()