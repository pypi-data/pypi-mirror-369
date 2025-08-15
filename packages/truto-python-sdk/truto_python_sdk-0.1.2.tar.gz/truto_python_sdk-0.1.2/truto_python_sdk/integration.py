from .pagination_result import PaginationResult

class Integration:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all integrations with pagination support."""
        return PaginationResult(self.api_client, "integration", query_params)

    def get(self, integration_id: str):
        """Get a specific integration by ID."""
        return self.api_client._get(f"integration/{integration_id}")

    def create(self, integration_data: dict):
        """Create a new integration."""
        return self.api_client._post("integration", data=integration_data)

    def update(self, integration_id: str, integration_data: dict):
        """Update an existing integration."""
        return self.api_client._patch(f"integration/{integration_id}", data=integration_data)

    def delete(self, integration_id: str):
        """Delete an integration by ID."""
        return self.api_client._delete(f"integration/{integration_id}")

    def install(self, integration_id: str, is_enabled: bool = True):
        """Install an integration by ID."""
        return self.api_client._post(f"environment-integration", data={"integration_id": integration_id, "is_enabled": is_enabled})

    def uninstall(self, integration_id: str):
        """Uninstall an integration by ID."""
        return self.api_client._delete(f"environment-integration/{integration_id}")