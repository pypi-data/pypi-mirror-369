from pydantic import Field

from .common import BrazeBaseModel


class Integration(BrazeBaseModel):
    """Model representing a single CDI integration."""

    integration_id: str = Field(..., description="Integration ID")
    app_group_id: str = Field(..., description="App group ID")
    integration_name: str = Field(..., description="Integration name")
    integration_type: str = Field(..., description="Integration type")
    integration_status: str = Field(..., description="Integration status")
    contact_emails: str = Field(..., description="Contact email(s)")
    last_updated_at: str | None = Field(
        None, description="Last timestamp that was synced in ISO 8601"
    )
    warehouse_type: str = Field(..., description="Data warehouse type")
    last_job_start_time: str | None = Field(
        None, description="Timestamp of the last sync run in ISO 8601"
    )
    last_job_status: str | None = Field(None, description="Status of the last sync run")
    next_scheduled_run: str | None = Field(
        None, description="Timestamp of the next scheduled sync in ISO 8601"
    )


class IntegrationsListResponse(BrazeBaseModel):
    """Response model for CDI integrations list endpoint."""

    results: list[Integration] = Field(..., description="Array of integration objects")
    message: str = Field(..., description="Success message")


class JobSyncStatus(BrazeBaseModel):
    """Model representing a single job sync status."""

    job_status: str = Field(
        ..., description="Status of the sync (running, success, partial, error, config_error)"
    )
    sync_start_time: str = Field(..., description="Time the sync started in ISO 8601")
    sync_finish_time: str = Field(..., description="Time the sync finished in ISO 8601")
    last_timestamp_synced: str = Field(
        ..., description="Last UPDATED_AT timestamp processed by the sync in ISO 8601"
    )
    rows_synced: int = Field(..., description="Number of rows successfully synced to Braze")
    rows_failed_with_errors: int = Field(..., description="Number of rows failed because of errors")


class JobSyncStatusResponse(BrazeBaseModel):
    """Response model for CDI integration job sync status endpoint."""

    results: list[JobSyncStatus] = Field(..., description="Array of job sync status objects")
    message: str = Field(..., description="Success message")
