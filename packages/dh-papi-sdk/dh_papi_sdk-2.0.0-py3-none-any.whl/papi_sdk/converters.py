"""
Converter functions between generated and stable models.

DO NOT EDIT: This file is auto-generated.
"""

from typing import Optional, List, Dict, Any

# Generated models imports
from papi_sdk.generated.generated.models import (
    VrmV1JobsIngestGet200Response,
    VrmV1JobsIngestGet200ResponseRecordsInner,
    VrmV1JobsIngestJobIdGet200Response,
    VrmV1JobsIngestJobIdGet404Response,
    VrmV1JobsIngestJobIdGet404ResponseErrorsInner,
    VrmV1JobsIngestJobIdPatch200Response,
    VrmV1JobsIngestJobIdPatchRequest,
    VrmV1JobsIngestPost200Response,
    VrmV1JobsIngestPostRequest,
)

from papi_sdk.models import (
    BulkJobCreateRequest,
    BulkJobCreateResponse,
    BulkJobError,
    BulkJobErrorResponse,
    BulkJobInfoResponse,
    BulkJobListResponse,
    BulkJobRecord,
    BulkJobUpdateRequest,
    BulkJobUpdateResponse,
)


def to_bulk_job_list_response(
    generated: VrmV1JobsIngestGet200Response,
) -> BulkJobListResponse:
    """Convert VrmV1JobsIngestGet200Response to BulkJobListResponse."""
    return BulkJobListResponse(
        done=generated.done,
        next_record_url=generated.next_record_url,
        records=generated.records,
    )


def from_bulk_job_list_response(
    stable: BulkJobListResponse,
) -> VrmV1JobsIngestGet200Response:
    """Convert BulkJobListResponse to VrmV1JobsIngestGet200Response."""
    return VrmV1JobsIngestGet200Response(
        done=stable.done,
        next_record_url=stable.next_record_url,
        records=stable.records,
    )


def to_bulk_job_record(
    generated: VrmV1JobsIngestGet200ResponseRecordsInner,
) -> BulkJobRecord:
    """Convert VrmV1JobsIngestGet200ResponseRecordsInner to BulkJobRecord."""
    return BulkJobRecord(
        api_version=generated.api_version,
        column_delimiter=generated.column_delimiter,
        concurrency_mode=generated.concurrency_mode,
        content_type=generated.content_type,
        content_url=generated.content_url,
        created_by_id=generated.created_by_id,
        created_date=generated.created_date,
        id=generated.id,
        job_type=generated.job_type,
        line_ending=generated.line_ending,
        object=generated.object,
        operation=generated.operation,
        state=generated.state,
        system_modstamp=generated.system_modstamp,
    )


def from_bulk_job_record(
    stable: BulkJobRecord,
) -> VrmV1JobsIngestGet200ResponseRecordsInner:
    """Convert BulkJobRecord to VrmV1JobsIngestGet200ResponseRecordsInner."""
    return VrmV1JobsIngestGet200ResponseRecordsInner(
        api_version=stable.api_version,
        column_delimiter=stable.column_delimiter,
        concurrency_mode=stable.concurrency_mode,
        content_type=stable.content_type,
        content_url=stable.content_url,
        created_by_id=stable.created_by_id,
        created_date=stable.created_date,
        id=stable.id,
        job_type=stable.job_type,
        line_ending=stable.line_ending,
        object=stable.object,
        operation=stable.operation,
        state=stable.state,
        system_modstamp=stable.system_modstamp,
    )


def to_bulk_job_info_response(
    generated: VrmV1JobsIngestJobIdGet200Response,
) -> BulkJobInfoResponse:
    """Convert VrmV1JobsIngestJobIdGet200Response to BulkJobInfoResponse."""
    return BulkJobInfoResponse(
        apex_processing_time=generated.apex_processing_time,
        api_active_processing_time=generated.api_active_processing_time,
        api_version=generated.api_version,
        assignment_rule_id=generated.assignment_rule_id,
        column_delimiter=generated.column_delimiter,
        concurrency_mode=generated.concurrency_mode,
        content_type=generated.content_type,
        content_url=generated.content_url,
        created_by_id=generated.created_by_id,
        created_date=generated.created_date,
        error_message=generated.error_message,
        external_id_field_name=generated.external_id_field_name,
        id=generated.id,
        job_type=generated.job_type,
        line_ending=generated.line_ending,
        number_records_failed=generated.number_records_failed,
        number_records_processed=generated.number_records_processed,
        number_records_succeeded=generated.number_records_succeeded,
        object=generated.object,
        operation=generated.operation,
        retries=generated.retries,
        state=generated.state,
        system_modstamp=generated.system_modstamp,
    )


def from_bulk_job_info_response(
    stable: BulkJobInfoResponse,
) -> VrmV1JobsIngestJobIdGet200Response:
    """Convert BulkJobInfoResponse to VrmV1JobsIngestJobIdGet200Response."""
    return VrmV1JobsIngestJobIdGet200Response(
        apex_processing_time=stable.apex_processing_time,
        api_active_processing_time=stable.api_active_processing_time,
        api_version=stable.api_version,
        assignment_rule_id=stable.assignment_rule_id,
        column_delimiter=stable.column_delimiter,
        concurrency_mode=stable.concurrency_mode,
        content_type=stable.content_type,
        content_url=stable.content_url,
        created_by_id=stable.created_by_id,
        created_date=stable.created_date,
        error_message=stable.error_message,
        external_id_field_name=stable.external_id_field_name,
        id=stable.id,
        job_type=stable.job_type,
        line_ending=stable.line_ending,
        number_records_failed=stable.number_records_failed,
        number_records_processed=stable.number_records_processed,
        number_records_succeeded=stable.number_records_succeeded,
        object=stable.object,
        operation=stable.operation,
        retries=stable.retries,
        state=stable.state,
        system_modstamp=stable.system_modstamp,
    )


def to_bulk_job_error_response(
    generated: VrmV1JobsIngestJobIdGet404Response,
) -> BulkJobErrorResponse:
    """Convert VrmV1JobsIngestJobIdGet404Response to BulkJobErrorResponse."""
    return BulkJobErrorResponse(
        errors=generated.errors,
    )


def from_bulk_job_error_response(
    stable: BulkJobErrorResponse,
) -> VrmV1JobsIngestJobIdGet404Response:
    """Convert BulkJobErrorResponse to VrmV1JobsIngestJobIdGet404Response."""
    return VrmV1JobsIngestJobIdGet404Response(
        errors=stable.errors,
    )


def to_bulk_job_error(
    generated: VrmV1JobsIngestJobIdGet404ResponseErrorsInner,
) -> BulkJobError:
    """Convert VrmV1JobsIngestJobIdGet404ResponseErrorsInner to BulkJobError."""
    return BulkJobError(
        code=generated.code,
        message=generated.message,
    )


def from_bulk_job_error(
    stable: BulkJobError,
) -> VrmV1JobsIngestJobIdGet404ResponseErrorsInner:
    """Convert BulkJobError to VrmV1JobsIngestJobIdGet404ResponseErrorsInner."""
    return VrmV1JobsIngestJobIdGet404ResponseErrorsInner(
        code=stable.code,
        message=stable.message,
    )


def to_bulk_job_update_response(
    generated: VrmV1JobsIngestJobIdPatch200Response,
) -> BulkJobUpdateResponse:
    """Convert VrmV1JobsIngestJobIdPatch200Response to BulkJobUpdateResponse."""
    return BulkJobUpdateResponse(
        api_version=generated.api_version,
        assignment_rule_id=generated.assignment_rule_id,
        column_delimiter=generated.column_delimiter,
        concurrency_mode=generated.concurrency_mode,
        content_type=generated.content_type,
        content_url=generated.content_url,
        created_by_id=generated.created_by_id,
        created_date=generated.created_date,
        external_id_field_name=generated.external_id_field_name,
        id=generated.id,
        job_type=generated.job_type,
        line_ending=generated.line_ending,
        object=generated.object,
        operation=generated.operation,
        state=generated.state,
        system_modstamp=generated.system_modstamp,
    )


def from_bulk_job_update_response(
    stable: BulkJobUpdateResponse,
) -> VrmV1JobsIngestJobIdPatch200Response:
    """Convert BulkJobUpdateResponse to VrmV1JobsIngestJobIdPatch200Response."""
    return VrmV1JobsIngestJobIdPatch200Response(
        api_version=stable.api_version,
        assignment_rule_id=stable.assignment_rule_id,
        column_delimiter=stable.column_delimiter,
        concurrency_mode=stable.concurrency_mode,
        content_type=stable.content_type,
        content_url=stable.content_url,
        created_by_id=stable.created_by_id,
        created_date=stable.created_date,
        external_id_field_name=stable.external_id_field_name,
        id=stable.id,
        job_type=stable.job_type,
        line_ending=stable.line_ending,
        object=stable.object,
        operation=stable.operation,
        state=stable.state,
        system_modstamp=stable.system_modstamp,
    )


def to_bulk_job_update_request(
    generated: VrmV1JobsIngestJobIdPatchRequest,
) -> BulkJobUpdateRequest:
    """Convert VrmV1JobsIngestJobIdPatchRequest to BulkJobUpdateRequest."""
    return BulkJobUpdateRequest(
        state=generated.state,
    )


def from_bulk_job_update_request(
    stable: BulkJobUpdateRequest,
) -> VrmV1JobsIngestJobIdPatchRequest:
    """Convert BulkJobUpdateRequest to VrmV1JobsIngestJobIdPatchRequest."""
    return VrmV1JobsIngestJobIdPatchRequest(
        state=stable.state,
    )


def to_bulk_job_create_response(
    generated: VrmV1JobsIngestPost200Response,
) -> BulkJobCreateResponse:
    """Convert VrmV1JobsIngestPost200Response to BulkJobCreateResponse."""
    return BulkJobCreateResponse(
        api_version=generated.api_version,
        concurrency_mode=generated.concurrency_mode,
        content_url=generated.content_url,
        created_by_id=generated.created_by_id,
        created_date=generated.created_date,
        id=generated.id,
        job_type=generated.job_type,
        state=generated.state,
        system_modstamp=generated.system_modstamp,
        object=generated.object,
        operation=generated.operation,
        assignment_rule=generated.assignment_rule,
        column_delimiter=generated.column_delimiter,
        content_type=generated.content_type,
        external_id_field_name=generated.external_id_field_name,
        line_ending=generated.line_ending,
    )


def from_bulk_job_create_response(
    stable: BulkJobCreateResponse,
) -> VrmV1JobsIngestPost200Response:
    """Convert BulkJobCreateResponse to VrmV1JobsIngestPost200Response."""
    return VrmV1JobsIngestPost200Response(
        api_version=stable.api_version,
        concurrency_mode=stable.concurrency_mode,
        content_url=stable.content_url,
        created_by_id=stable.created_by_id,
        created_date=stable.created_date,
        id=stable.id,
        job_type=stable.job_type,
        state=stable.state,
        system_modstamp=stable.system_modstamp,
        object=stable.object,
        operation=stable.operation,
        assignment_rule=stable.assignment_rule,
        column_delimiter=stable.column_delimiter,
        content_type=stable.content_type,
        external_id_field_name=stable.external_id_field_name,
        line_ending=stable.line_ending,
    )


def to_bulk_job_create_request(
    generated: VrmV1JobsIngestPostRequest,
) -> BulkJobCreateRequest:
    """Convert VrmV1JobsIngestPostRequest to BulkJobCreateRequest."""
    return BulkJobCreateRequest(
        object=generated.object,
        operation=generated.operation,
        assignment_rule=generated.assignment_rule,
        column_delimiter=generated.column_delimiter,
        content_type=generated.content_type,
        external_id_field_name=generated.external_id_field_name,
        line_ending=generated.line_ending,
    )


def from_bulk_job_create_request(
    stable: BulkJobCreateRequest,
) -> VrmV1JobsIngestPostRequest:
    """Convert BulkJobCreateRequest to VrmV1JobsIngestPostRequest."""
    return VrmV1JobsIngestPostRequest(
        object=stable.object,
        operation=stable.operation,
        assignment_rule=stable.assignment_rule,
        column_delimiter=stable.column_delimiter,
        content_type=stable.content_type,
        external_id_field_name=stable.external_id_field_name,
        line_ending=stable.line_ending,
    )
