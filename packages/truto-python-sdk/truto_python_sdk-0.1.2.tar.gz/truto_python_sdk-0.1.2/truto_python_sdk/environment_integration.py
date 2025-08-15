from .pagination_result import PaginationResult

class EnvironmentIntegration:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all environment integrations with pagination support."""
        return PaginationResult(self.api_client, "environment-integration", query_params)

    def get(self, environment_integration_id: str):
        """Get a specific environment_integration by ID."""
        return self.api_client._get(f"environment-integration/{environment_integration_id}")

    def update(self, environment_integration_id: str, environment_integration_data: dict):
        """Update an existing environment_integration."""
        return self.api_client._patch(f"environment-integration/{environment_integration_id}", data=environment_integration_data)