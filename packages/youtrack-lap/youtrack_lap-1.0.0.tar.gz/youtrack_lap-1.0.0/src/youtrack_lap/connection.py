import requests

class Connection:
    def __init__(self, base_url, token):
        """
        Initialize YouTrack client.
        
        Args:
            base_url: YouTrack instance URL (e.g., 'https://example.youtrack.cloud')
            token: Permanent token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }