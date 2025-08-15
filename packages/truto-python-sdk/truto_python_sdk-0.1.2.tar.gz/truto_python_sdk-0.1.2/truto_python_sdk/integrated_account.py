from .pagination_result import PaginationResult

class IntegratedAccount:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all integrated_accounts with pagination support."""
        return PaginationResult(self.api_client, "integrated-account", query_params)

    def get(self, integrated_account_id: str):
        """Get a specific integrated_account by ID."""
        return self.api_client._get(f"integrated-account/{integrated_account_id}")

    def _import(self, integrated_account_data: dict):
        """Create a new integrated_account."""
        return self.api_client._post("integrated-account", data=integrated_account_data)

    def update(self, integrated_account_id: str, integrated_account_data: dict):
        """Update an existing integrated_account."""
        return self.api_client._patch(f"integrated-account/{integrated_account_id}", data=integrated_account_data)

    def delete(self, integrated_account_id: str):
        """Delete an integrated_account by ID."""
        return self.api_client._delete(f"integrated-account/{integrated_account_id}")

    def create_integrated_account_token(self, integrated_account_id: str):
        """Create a new token for the integrated account."""
        return self.api_client._post(f"integrated-account/token", data={"integrated_account_id": integrated_account_id})

    def refresh_credentials(self, integrated_account_id: str):
        """Refresh the credentials for the integrated account."""
        return self.api_client._post(f"integrated-account/refresh-credentials", data={"id": integrated_account_id})

    def run_post_install_actions(self, integrated_account_id: str):
        """Run post install actions for the integrated account."""
        return self.api_client._post(f"integrated-account/run-post-install-actions", data={"id": integrated_account_id})