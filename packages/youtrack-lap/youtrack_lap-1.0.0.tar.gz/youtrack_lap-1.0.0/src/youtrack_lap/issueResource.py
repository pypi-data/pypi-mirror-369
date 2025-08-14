import requests

ISSUE_URL='/api/issues'

class IssueResource:
    def __init__(self, client, issue_id):
        """
        Initialize Issue Resource.
        
        Args:
            client: YouTrackClient instance
            issue_id: ID of the issue (e.g., 'AI-123')
        """
        self.client = client
        self.issue_id = issue_id
    
    #GET /api/issues/{issueID}?{fields}
    def read(self, fields=None):
        """Get issue details."""
        url = f"{self.client.base_url}{ISSUE_URL}/{self.issue_id}"
        params = {
            'fields': fields or 'id,summary,description'
        }
        
        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    #POST /api/issues/{issueID}?{fields}&{muteUpdateNotifications}
    def update(self, issue_data, fields=None, mute_notifications=None):
        """Update issue."""
        url = f"{self.client.base_url}{ISSUE_URL}/{self.issue_id}"
        params = {
            'fields': fields or 'id',
            'muteUpdateNotifications': mute_notifications
        }
        
        response = requests.post(url, headers=self.client.headers, json=issue_data, params=params)
        response.raise_for_status()
        
        return response.json()
    
    #DELETE /api/issues/{issueID}
    def delete(self):
        """Delete issue."""
        url = f"{self.client.base_url}{ISSUE_URL}/{self.issue_id}"
        
        response = requests.delete(url, headers=self.client.headers)
        response.raise_for_status()
        
        if response.text:
            return response.json()
        else:
            return {"status": "deleted", "id": self.issue_id}
    
    #GET /api/issues/{issueID}/timeTracking/workItems?{fields}&{$top}&{$skip}
    def list_work_items(self, fields=None, limit=None, skip=None):
        """Get work items for the issue."""
        url = f"{self.client.base_url}{ISSUE_URL}/{self.issue_id}/timeTracking/workItems"
        params = {
            'fields': fields or 'id,author(name),date,text,duration(minutes),type(name)',
            '$top': limit,
            '$skip': skip
        }
        
        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    #POST /api/issues/{issueID}/timeTracking/workItems?{fields}&{muteUpdateNotifications}
    def add_work_item(self, work_item_data, fields=None, mute_notifications=None):
        """Add work item to the issue."""
        url = f"{self.client.base_url}{ISSUE_URL}/{self.issue_id}/timeTracking/workItems"
        params = {
            'fields': fields or 'id',
            'muteUpdateNotifications': mute_notifications
        }
        
        response = requests.post(url, headers=self.client.headers, json=work_item_data, params=params)
        response.raise_for_status()
        
        return response.json()
    
    #GET /api/issues/{issueID}/timeTracking/workItems/{itemID}?{fields}
    def get_work_item(self, item_id, fields=None):
        """Get a specific work item."""
        url = f"{self.client.base_url}{ISSUE_URL}/{self.issue_id}/timeTracking/workItems/{item_id}"
        params = {
            'fields': fields or 'id,author(name),date,text,duration(minutes),type(name)'
        }
        
        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    #POST /api/issues/{issueID}/timeTracking/workItems/{itemID}?{fields}&{muteUpdateNotifications}
    def update_work_item(self, item_id, work_item_data, fields=None, mute_notifications=None):
        """Update a specific work item."""
        url = f"{self.client.base_url}{ISSUE_URL}/{self.issue_id}/timeTracking/workItems/{item_id}"
        params = {
            'fields': fields or 'id',
            'muteUpdateNotifications': mute_notifications
        }
        
        response = requests.post(url, headers=self.client.headers, json=work_item_data, params=params)
        response.raise_for_status()
        
        return response.json()
    
    #DELETE /api/issues/{issueID}/timeTracking/workItems/{itemID}
    def delete_work_item(self, item_id):
        """Delete a specific work item."""
        url = f"{self.client.base_url}{ISSUE_URL}/{self.issue_id}/timeTracking/workItems/{item_id}"
        
        response = requests.delete(url, headers=self.client.headers)
        response.raise_for_status()
        
        if response.text:
            return response.json()
        else:
            return {"status": "deleted", "id": item_id}