from .pagination_result import PaginationResult

class EnvironmentUnifiedModel:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all environment unified models with pagination support."""
        return PaginationResult(self.api_client, "environment-unified-model", query_params)

    def get(self, environment_unified_model_id: str):
        """Get a specific environment_unified_model by ID."""
        return self.api_client._get(f"environment-unified-model/{environment_unified_model_id}")

    def update(self, environment_unified_model_id: str, environment_unified_model_data: dict):
        """Update an existing environment_unified_model."""
        return self.api_client._patch(f"environment-unified-model/{environment_unified_model_id}", data=environment_unified_model_data)