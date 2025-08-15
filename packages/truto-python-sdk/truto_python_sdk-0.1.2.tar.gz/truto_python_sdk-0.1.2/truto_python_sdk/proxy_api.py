from .pagination_result import PaginationResult

class ProxyApi:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, resource: str, query_params: dict):
        """List all proxy api resources with pagination support."""
        return PaginationResult(self.api_client, f"proxy/{resource}", query_params)

    def get(self, resource: str, id: str, query_params: dict):
        """Get a specific proxy api resource by ID."""
        return self.api_client._get(f"proxy/{resource}/{id}", params=query_params)

    def create(self, resource: str, data: dict, query_params: dict):
        """Create a new proxy api resource."""
        return self.api_client._post(f"proxy/{resource}", data=data, params=query_params)

    def update(self, resource: str, id: str, data: dict, query_params: dict):
        """Update an existing proxy api resource."""
        return self.api_client._patch(f"proxy/{resource}/{id}", data=data, params=query_params)

    def delete(self, resource: str, id: str, query_params: dict):
        """Delete a proxy api resource by ID."""
        return self.api_client._delete(f"proxy/{resource}/{id}", query_params)

    def custom_method(self, resource: str, method: str, data: dict, query_params: dict):
        """Call a custom method on a proxy api resource."""
        return self.api_client._post(method, f"proxy/{resource}/{method}", data=data, params=query_params)