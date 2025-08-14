import requests

RESOURCE_URL='/api/admin/projects'

class ProjectsResource:
    def __init__(self, client, project_id):
        """
        Initialize Project object.
        
        Args:
            client: YouTrackClient instance
            project_id: ID of the project (e.g., 'AI')
        """
        self.client = client
        self.project_id = project_id
    
    #GET /api/admin/projects/{projectID}?{fields}
    def get_details(self):
        """Get project details."""
        url = f"{self.client.base_url}{RESOURCE_URL}/{self.project_id}"
        params = {
            'fields': 'id,name,description,created'
        }
            
        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    #POST /api/admin/projects/{projectID}?{fields}
    def update(self, project_data):
        """Update project details."""
        url = f"{self.client.base_url}{RESOURCE_URL}/{self.project_id}"
        params = {
            'fields': 'id'
        }

        response = requests.put(url, headers=self.client.headers, json=project_data, params=params)
        response.raise_for_status()

        return response.json()
    
    #DELETE /api/admin/projects/{projectID}
    def delete(self):
        """Delete the project."""
        url = f"{self.client.base_url}{RESOURCE_URL}/{self.project_id}"
        response = requests.delete(url, headers=self.client.headers)
        response.raise_for_status()

        return response.json()
    
    # GET /api/admin/projects/{projectID}/issues/{issueID}?{fields}
    def get_issue(self, issue_id):
        """Get a single issue."""
        url = f"{self.client.base_url}{RESOURCE_URL}/{self.project_id}/issues/{issue_id}"
        params = {
            'fields': 'id,summary,description'
        }

        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()

        return response.json()
    
    #POST /api/admin/projects/{projectID}/issues/{issueID}?{fields}&{muteUpdateNotifications}
    def update_issue(self, issue_id, issue_data):
        """Update an issue."""
        url = f"{self.client.base_url}{RESOURCE_URL}/{self.project_id}/issues/{issue_id}"
        params = {
            'fields': 'id'
        }

        response = requests.put(url, headers=self.client.headers, json=issue_data)
        response.raise_for_status()

        return response.json()
    
    #DELETE /api/admin/projects/{projectID}/issues/{issueID}
    def delete_issue(self, issue_id):
        """Delete an issue."""
        url = f"{self.client.base_url}{RESOURCE_URL}/{self.project_id}/issues/{issue_id}"
        response = requests.delete(url, headers=self.client.headers)
        response.raise_for_status()

        return response.json()
    
    def list_issues(self, limit=None):
        """Get issues for the project."""
        #url = f"{self.client.base_url}/api/issues"
        url = f"{self.client.base_url}{RESOURCE_URL}/{self.project_id}/issues/"
        params = {
            'fields': 'id,summary,description',
            '$top': limit,
        }
            
        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()
        
        return response.json()