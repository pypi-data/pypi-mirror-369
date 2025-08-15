from .pagination_result import PaginationResult

class BaseResource:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all base_resources with pagination support."""
        return PaginationResult(self.api_client, "base_resource", query_params)

    def get(self, base_resource_id: str):
        """Get a specific base_resource by ID."""
        return self.api_client._get(f"base_resource/{base_resource_id}")

    def create(self, base_resource_data: dict):
        """Create a new base_resource."""
        return self.api_client._post("base_resource", data=base_resource_data)

    def update(self, base_resource_id: str, base_resource_data: dict):
        """Update an existing base_resource."""
        return self.api_client._patch(f"base_resource/{base_resource_id}", data=base_resource_data)

    def delete(self, base_resource_id: str):
        """Delete a base_resource by ID."""
        return self.api_client._delete(f"base_resource/{base_resource_id}")