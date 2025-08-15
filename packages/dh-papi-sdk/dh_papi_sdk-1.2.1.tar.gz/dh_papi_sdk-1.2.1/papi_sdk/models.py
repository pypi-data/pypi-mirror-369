"""
Stable dataclass models generated from API specifications.

DO NOT EDIT: This file is auto-generated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Union


@dataclass
class BulkJobListResponse:
    """
    Stable model representing VrmV1JobsIngestGet200Response.
    """

    done: Optional[bool] = None
    next_record_url: Optional[str] = None
    records: Optional[List[BulkJobRecord]] = None


@dataclass
class BulkJobRecord:
    """
    Stable model representing VrmV1JobsIngestGet200ResponseRecordsInner.
    """

    api_version: Optional[Union[float, int]] = None
    column_delimiter: Optional[str] = None
    concurrency_mode: Optional[str] = None
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    created_by_id: Optional[str] = None
    created_date: Optional[str] = None
    id: Optional[str] = None
    job_type: Optional[str] = None
    line_ending: Optional[str] = None
    object: Optional[str] = None
    operation: Optional[str] = None
    state: Optional[str] = None
    system_modstamp: Optional[str] = None


@dataclass
class BulkJobInfoResponse:
    """
    Stable model representing VrmV1JobsIngestJobIdGet200Response.
    """

    apex_processing_time: Optional[Union[float, int]] = None
    api_active_processing_time: Optional[Union[float, int]] = None
    api_version: Optional[Union[float, int]] = None
    assignment_rule_id: Optional[str] = None
    column_delimiter: Optional[str] = None
    concurrency_mode: Optional[str] = None
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    created_by_id: Optional[str] = None
    created_date: Optional[str] = None
    error_message: Optional[str] = None
    external_id_field_name: Optional[str] = None
    id: Optional[str] = None
    job_type: Optional[str] = None
    line_ending: Optional[str] = None
    number_records_failed: Optional[Union[float, int]] = None
    number_records_processed: Optional[Union[float, int]] = None
    number_records_succeeded: Optional[Union[float, int]] = None
    object: Optional[str] = None
    operation: Optional[str] = None
    retries: Optional[Union[float, int]] = None
    state: Optional[str] = None
    system_modstamp: Optional[str] = None


@dataclass
class BulkJobErrorResponse:
    """
    Stable model representing VrmV1JobsIngestJobIdGet404Response.
    """

    errors: Optional[List[BulkJobError]] = None


@dataclass
class BulkJobError:
    """
    Stable model representing VrmV1JobsIngestJobIdGet404ResponseErrorsInner.
    """

    code: Optional[str] = None
    message: Optional[str] = None


@dataclass
class BulkJobUpdateResponse:
    """
    Stable model representing VrmV1JobsIngestJobIdPatch200Response.
    """

    api_version: Optional[Union[float, int]] = None
    assignment_rule_id: Optional[str] = None
    column_delimiter: Optional[str] = None
    concurrency_mode: Optional[str] = None
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    created_by_id: Optional[str] = None
    created_date: Optional[str] = None
    external_id_field_name: Optional[str] = None
    id: Optional[str] = None
    job_type: Optional[str] = None
    line_ending: Optional[str] = None
    object: Optional[str] = None
    operation: Optional[str] = None
    state: Optional[str] = None
    system_modstamp: Optional[str] = None


@dataclass
class BulkJobUpdateRequest:
    """
    Stable model representing VrmV1JobsIngestJobIdPatchRequest.
    """

    state: Optional[str] = None


@dataclass
class BulkJobCreateResponse:
    """
    Stable model representing VrmV1JobsIngestPost200Response.
    """

    api_version: Optional[Union[float, int]] = None
    concurrency_mode: Optional[str] = None
    content_url: Optional[str] = None
    created_by_id: Optional[str] = None
    created_date: Optional[str] = None
    id: Optional[str] = None
    job_type: Optional[str] = None
    state: Optional[str] = None
    system_modstamp: Optional[str] = None
    object: Optional[str] = None
    operation: Optional[str] = None
    assignment_rule: Optional[str] = None
    column_delimiter: Optional[str] = None
    content_type: Optional[str] = None
    external_id_field_name: Optional[str] = None
    line_ending: Optional[str] = None


@dataclass
class BulkJobCreateRequest:
    """
    Stable model representing VrmV1JobsIngestPostRequest.
    """

    object: str
    operation: str
    assignment_rule: Optional[str] = None
    column_delimiter: Optional[str] = None
    content_type: Optional[str] = None
    external_id_field_name: Optional[str] = None
    line_ending: Optional[str] = None
