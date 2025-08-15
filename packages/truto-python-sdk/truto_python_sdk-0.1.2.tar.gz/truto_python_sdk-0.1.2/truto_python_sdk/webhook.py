from .pagination_result import PaginationResult

class Webhook:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all webhooks with pagination support."""
        return PaginationResult(self.api_client, "webhook", query_params)

    def get(self, webhook_id: str):
        """Get a specific webhook by ID."""
        return self.api_client._get(f"webhook/{webhook_id}")

    def create(self, webhook_data: dict):
        """Create a new webhook."""
        return self.api_client._post("webhook", data=webhook_data)

    def update(self, webhook_id: str, webhook_data: dict):
        """Update an existing webhook."""
        return self.api_client._patch(f"webhook/{webhook_id}", data=webhook_data)

    def delete(self, webhook_id: str):
        """Delete a webhook by ID."""
        return self.api_client._delete(f"webhook/{webhook_id}")

    def test(self, webhook_id: str):
        """Test a webhook by ID."""
        return self.api_client._post(f"webhook/test", data={"id": webhook_id})