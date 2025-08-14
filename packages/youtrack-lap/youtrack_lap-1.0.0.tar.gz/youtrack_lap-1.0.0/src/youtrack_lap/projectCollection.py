import requests

COLLECTION_URL='/api/admin/projects'

class ProjectsCollection:
    def __init__(self, client):
        """
        Description
        """
        self.client = client

    #GET /api/admin/projects?{fields}&{$top}&{$skip}
    def list_projects(self):
        url = f"{self.client.base_url}{COLLECTION_URL}"
        params = {
            'fields': 'id,name,shortName,createdBy(name)',
            '$top': 10,
            '$skip': 0
        }
        response = requests.get(url, headers=self.client.headers, params=params)
        response.raise_for_status()
        return response.json()

    #POST /api/admin/projects?{fields}&{template}
    def create_project(self, project_data):
        url = f"{self.client.base_url}{COLLECTION_URL}"
        params = {
            'fields': 'id'
        }
        response = requests.post(url, headers=self.client.headers, json=project_data)
        response.raise_for_status()
        return response.json()
    
            
    