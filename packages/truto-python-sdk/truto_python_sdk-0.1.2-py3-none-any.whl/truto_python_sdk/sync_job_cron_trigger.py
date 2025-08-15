from .pagination_result import PaginationResult

class SyncJobCronTrigger:
    def __init__(self, api_client):
        self.api_client = api_client

    def list(self, **query_params):
        """List all sync job cron triggers with pagination support."""
        return PaginationResult(self.api_client, "sync-job-cron-trigger", query_params)

    def get(self, sync_job_cron_trigger_id: str):
        """Get a specific sync_job_cron_trigger by ID."""
        return self.api_client._get(f"sync-job-cron-trigger/{sync_job_cron_trigger_id}")

    def create(self, sync_job_cron_trigger_data: dict):
        """Create a new sync_job_cron_trigger."""
        return self.api_client._post("sync-job-cron-trigger", data=sync_job_cron_trigger_data)

    def update(self, sync_job_cron_trigger_id: str, sync_job_cron_trigger_data: dict):
        """Update an existing sync_job_cron_trigger."""
        return self.api_client._patch(f"sync-job-cron-trigger/{sync_job_cron_trigger_id}", data=sync_job_cron_trigger_data)

    def delete(self, sync_job_cron_trigger_id: str):
        """Delete an sync_job_cron_trigger by ID."""
        return self.api_client._delete(f"sync-job-cron-trigger/{sync_job_cron_trigger_id}")

    def schedule(self, sync_job_cron_trigger_id: str):
        """Schedule a sync job cron trigger by ID."""
        return self.api_client._post(f"sync-job-cron-trigger/{sync_job_cron_trigger_id}/schedule")