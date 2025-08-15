from .pagination_result import PaginationResult

class SyncJobRun:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all sync job runs with pagination support."""
        return PaginationResult(self.api_client, "sync-job-run", query_params)

    def get(self, sync_job_run_id: str):
        """Get a specific sync_job_run by ID."""
        return self.api_client._get(f"sync-job-run/{sync_job_run_id}")

    def create(self, sync_job_run_data: dict):
        """Create a new sync_job_run."""
        return self.api_client._post("sync-job-run", data=sync_job_run_data)

    def update(self, sync_job_run_id: str, sync_job_run_data: dict):
        """Update an existing sync_job_run."""
        return self.api_client._patch(f"sync-job-run/{sync_job_run_id}", data=sync_job_run_data)

    def delete(self, sync_job_run_id: str):
        """Delete an sync_job_run by ID."""
        return self.api_client._delete(f"sync-job-run/{sync_job_run_id}")