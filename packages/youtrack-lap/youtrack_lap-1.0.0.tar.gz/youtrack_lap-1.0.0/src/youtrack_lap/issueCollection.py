import requests

ISSUE_URL='/api/issues'

class IssueCollection:
    def __init__(self, client):
        """
        Initialize Issue Collection.
        
        Args:
            client: YouTrackClient instance
        """
        self.client = client
    
    #GET /api/issues?{fields}&{$top}&{$skip}&{query}&{customFields}
    def list_issues(self, fields=None, limit=None, skip=None, query=None, custom_fields=None):
        """Get issues list."""
        url = f"{self.client.base_url}{ISSUE_URL}"
        params = {
            'fields': fields or 'id,summary,description',
            '$top': limit,
            '$skip': skip,
            'query': query,
            'customFields': custom_fields
        }
        
        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    #POST /api/issues?{fields}&{draftId}&{muteUpdateNotifications}
    def create_issue(self, issue_data, fields=None, draft_id=None, mute_notifications=None):
        """Create a new issue."""
        url = f"{self.client.base_url}{ISSUE_URL}"
        params = {
            'fields': fields or 'id',
            'draftId': draft_id,
            'muteUpdateNotifications': mute_notifications
        }
        
        response = requests.post(url, headers=self.client.headers, json=issue_data, params=params)
        response.raise_for_status()
        
        return response.json()