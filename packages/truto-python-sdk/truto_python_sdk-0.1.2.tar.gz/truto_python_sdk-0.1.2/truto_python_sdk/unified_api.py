from .pagination_result import PaginationResult

class UnifiedApi:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, unified_model_name: str, unified_model_resource: str, query_params: dict):
        """List all unified api resources with pagination support."""
        return PaginationResult(self.api_client, f"unified/{unified_model_name}/{unified_model_resource}", query_params)

    def get(self, unified_model_name: str, unified_model_resource: str, id: str, query_params: dict):
        """Get a specific unified api resource by ID."""
        return self.api_client._get(f"unified/{unified_model_name}/{unified_model_resource}/{id}", query_params)

    def create(self, unified_model_name: str, unified_model_resource: str, data: dict, query_params: dict):
        """Create a new unified api resource."""
        return self.api_client._post(f"unified/{unified_model_name}/{unified_model_resource}", data=data, params=query_params)

    def update(self, unified_model_name: str, unified_model_resource: str, id: str, data: dict, query_params: dict):
        """Update an existing unified api resource."""
        return self.api_client._patch(f"unified/{unified_model_name}/{unified_model_resource}/{id}", data=data, params=query_params)

    def delete(self, unified_model_name: str, unified_model_resource: str, id: str, query_params: dict):
        """Delete an unified api resource by ID."""
        return self.api_client._delete(f"unified/{unified_model_name}/{unified_model_resource}/{id}", query_params)

    def custom_method(self, unified_model_name: str, unified_model_resource: str, method: str, data: dict, query_params: dict):
        """Call a custom method on a unified api resource."""
        return self.api_client._post(method, f"unified/{unified_model_name}/{unified_model_resource}/{method}", data=data, params=query_params)