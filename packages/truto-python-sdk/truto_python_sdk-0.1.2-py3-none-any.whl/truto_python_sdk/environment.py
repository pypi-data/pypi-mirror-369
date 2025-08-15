from .pagination_result import PaginationResult

class Environment:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all environments with pagination support."""
        return PaginationResult(self.api_client, "environment", query_params)

    def get(self, environment_id: str):
        """Get a specific environment by ID."""
        return self.api_client._get(f"environment/{environment_id}")