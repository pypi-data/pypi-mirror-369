from .pagination_result import PaginationResult

class SyncJob:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all sync jobs with pagination support."""
        return PaginationResult(self.api_client, "sync-job", query_params)

    def get(self, sync_job_id: str):
        """Get a specific sync_job by ID."""
        return self.api_client._get(f"sync-job/{sync_job_id}")

    def create(self, sync_job_data: dict):
        """Create a new sync_job."""
        return self.api_client._post("sync-job", data=sync_job_data)

    def update(self, sync_job_id: str, sync_job_data: dict):
        """Update an existing sync_job."""
        return self.api_client._patch(f"sync-job/{sync_job_id}", data=sync_job_data)

    def delete(self, sync_job_id: str):
        """Delete an sync_job by ID."""
        return self.api_client._delete(f"sync-job/{sync_job_id}")