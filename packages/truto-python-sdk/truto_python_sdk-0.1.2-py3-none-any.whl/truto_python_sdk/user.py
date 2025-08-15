from .pagination_result import PaginationResult

class User:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all users with pagination support."""
        return PaginationResult(self.api_client, "user", query_params)

    def get(self, user_id: str):
        """Get a specific user by ID."""
        return self.api_client._get(f"user/{user_id}")