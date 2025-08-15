# /sdk/py/papi-sdk/tests/test_stable_models_integration.py
"""
Integration tests specifically for stable models and converters.
These tests verify that the stable model architecture works correctly.
"""

import pytest
from unittest.mock import Mock


class TestStableModelsIntegration:
    """Test stable models work correctly end-to-end"""
    
    def test_stable_models_can_be_imported(self):
        """Test that all stable models can be imported"""
        from papi_sdk.models import (
            BulkJobCreateRequest,
            BulkJobCreateResponse,
            BulkJobListResponse,
            BulkJobInfoResponse,
            BulkJobUpdateRequest,
            BulkJobUpdateResponse,
            BulkJobRecord,
            BulkJobError,
            BulkJobErrorResponse
        )
        
        # Verify all models are available
        assert BulkJobCreateRequest is not None
        assert BulkJobCreateResponse is not None
        assert BulkJobListResponse is not None
        assert BulkJobInfoResponse is not None
        assert BulkJobUpdateRequest is not None
        assert BulkJobUpdateResponse is not None
        assert BulkJobRecord is not None
        assert BulkJobError is not None
        assert BulkJobErrorResponse is not None
    
    def test_converters_can_be_imported(self):
        """Test that all converter functions can be imported"""
        from papi_sdk.converters import (
            to_bulk_job_create_request,
            from_bulk_job_create_request,
            to_bulk_job_create_response,
            from_bulk_job_create_response,
            to_bulk_job_info_response,
            from_bulk_job_info_response,
            to_bulk_job_update_request,
            from_bulk_job_update_request,
            to_bulk_job_update_response,
            from_bulk_job_update_response,
            to_bulk_job_list_response,
            from_bulk_job_list_response,
            to_bulk_job_record,
            from_bulk_job_record,
            to_bulk_job_error,
            from_bulk_job_error,
            to_bulk_job_error_response,
            from_bulk_job_error_response
        )
        
        # Verify all converters are callable
        converters = [
            to_bulk_job_create_request, from_bulk_job_create_request,
            to_bulk_job_create_response, from_bulk_job_create_response,
            to_bulk_job_info_response, from_bulk_job_info_response,
            to_bulk_job_update_request, from_bulk_job_update_request,
            to_bulk_job_update_response, from_bulk_job_update_response,
            to_bulk_job_list_response, from_bulk_job_list_response,
            to_bulk_job_record, from_bulk_job_record,
            to_bulk_job_error, from_bulk_job_error,
            to_bulk_job_error_response, from_bulk_job_error_response
        ]
        
        for converter in converters:
            assert callable(converter), f"Converter {converter.__name__} is not callable"
    
    def test_stable_model_creation_and_access(self):
        """Test creating stable models and accessing their attributes"""
        from papi_sdk.models import BulkJobCreateRequest, BulkJobCreateResponse
        
        # Test request model
        request = BulkJobCreateRequest(
            object="Account",
            operation="insert",
            external_id_field_name="External_ID__c",
            column_delimiter="COMMA",
            content_type="CSV"
        )
        
        assert request.object == "Account"
        assert request.operation == "insert"
        assert request.external_id_field_name == "External_ID__c"
        assert request.column_delimiter == "COMMA"
        assert request.content_type == "CSV"
        assert request.assignment_rule is None  # Optional field defaults to None
        
        # Test response model
        response = BulkJobCreateResponse(
            id="stable-job-123",
            state="Open",
            object="Account",
            operation="insert",
            created_date="2023-01-01T12:00:00Z",
            api_version=52.0
        )
        
        assert response.id == "stable-job-123"
        assert response.state == "Open"
        assert response.object == "Account"
        assert response.operation == "insert"
        assert response.created_date == "2023-01-01T12:00:00Z"
        assert response.api_version == 52.0
    
    def test_converter_round_trip(self):
        """Test that stable -> generated -> stable conversion works"""
        from papi_sdk.models import BulkJobCreateRequest
        from papi_sdk.converters import from_bulk_job_create_request, to_bulk_job_create_request
        
        # Create original stable model
        original = BulkJobCreateRequest(
            object="Contact",
            operation="upsert",
            external_id_field_name="Email",
            column_delimiter="COMMA"
        )
        
        # Convert to generated model
        generated = from_bulk_job_create_request(original)
        
        # Convert back to stable model
        round_trip = to_bulk_job_create_request(generated)
        
        # Verify round trip worked
        assert round_trip.object == original.object
        assert round_trip.operation == original.operation
        assert round_trip.external_id_field_name == original.external_id_field_name
        assert round_trip.column_delimiter == original.column_delimiter
    
    def test_nested_model_types(self):
        """Test that nested model types work correctly"""
        from papi_sdk.models import BulkJobListResponse, BulkJobRecord, BulkJobErrorResponse, BulkJobError
        
        # Create nested record
        record = BulkJobRecord(
            id="record-123",
            state="JobComplete",
            object="Account",
            operation="insert",
            created_date="2023-01-01T12:00:00Z"
        )
        
        # Create list response with nested record
        list_response = BulkJobListResponse(
            done=True,
            next_record_url=None,
            records=[record]
        )
        
        assert list_response.done is True
        assert len(list_response.records) == 1
        assert list_response.records[0].id == "record-123"
        assert list_response.records[0].state == "JobComplete"
        
        # Create error with nested error items
        error_item = BulkJobError(
            code="INVALID_FIELD",
            message="No such column 'InvalidField' on sobject of type Account"
        )
        
        error_response = BulkJobErrorResponse(
            errors=[error_item]
        )
        
        assert len(error_response.errors) == 1
        assert error_response.errors[0].code == "INVALID_FIELD"
        assert "InvalidField" in error_response.errors[0].message
    
    def test_optional_fields_behavior(self):
        """Test that optional fields work correctly"""
        from papi_sdk.models import BulkJobCreateRequest, BulkJobInfoResponse
        
        # Test minimal request (only required fields)
        minimal_request = BulkJobCreateRequest(
            object="Account",
            operation="insert"
        )
        
        assert minimal_request.object == "Account"
        assert minimal_request.operation == "insert"
        assert minimal_request.external_id_field_name is None
        assert minimal_request.assignment_rule is None
        assert minimal_request.column_delimiter is None
        
        # Test response with some fields populated
        partial_response = BulkJobInfoResponse(
            id="partial-job-123",
            state="JobComplete",
            number_records_processed=100,
            number_records_succeeded=95,
            number_records_failed=5
        )
        
        assert partial_response.id == "partial-job-123"
        assert partial_response.state == "JobComplete"
        assert partial_response.number_records_processed == 100
        assert partial_response.number_records_succeeded == 95
        assert partial_response.number_records_failed == 5
        # Optional fields should be None
        assert partial_response.object is None
        assert partial_response.operation is None
        assert partial_response.created_date is None
    
    def test_type_annotations_work(self):
        """Test that type annotations are preserved and work correctly"""
        from papi_sdk.models import BulkJobInfoResponse
        from typing import Union, get_type_hints
        
        # Get type hints for the model
        hints = get_type_hints(BulkJobInfoResponse)
        
        # Check some specific type annotations
        assert 'id' in hints
        assert 'state' in hints
        assert 'number_records_processed' in hints
        
        # Test Union types work (for number fields that can be int or float)
        response = BulkJobInfoResponse(
            id="type-test-123",
            state="JobComplete",
            number_records_processed=100,  # int
            api_version=52.0  # float
        )
        
        assert isinstance(response.number_records_processed, int)
        assert isinstance(response.api_version, float)
    
    def test_forward_references_resolved(self):
        """Test that forward references in type annotations work"""
        from papi_sdk.models import BulkJobListResponse
        
        # This should work without NameError thanks to __future__ annotations
        response = BulkJobListResponse(
            done=True,
            records=[]  # This should accept List[BulkJobRecord] even though BulkJobRecord is defined later
        )
        
        assert response.done is True
        assert response.records == []
        assert isinstance(response.records, list)


class TestClientStableModelIntegration:
    """Test that the client correctly uses stable models"""
    
    def test_vrm_bulk_client_uses_stable_models(self):
        """Test that VRM bulk client methods use stable models"""
        from papi_sdk.vrm_bulk_client import BulkAPI
        
        # Create a mock API client
        mock_api_client = Mock()
        client = BulkAPI(mock_api_client)
        
        # Check method signatures exist (we can't easily test the full flow without complex mocking)
        assert hasattr(client, 'create_job')
        assert hasattr(client, 'get_job_info')
        assert hasattr(client, 'close_job')
        assert hasattr(client, 'upload_job_data')
        assert hasattr(client, 'get_all_jobs')
        assert hasattr(client, 'delete_job')
        
        # These methods should be callable
        assert callable(client.create_job)
        assert callable(client.get_job_info)
        assert callable(client.close_job)
    
    def test_imports_from_client_work(self):
        """Test that importing through the main client works"""
        from papi_sdk import Client
        from papi_sdk.models import BulkJobCreateRequest
        from papi_sdk.vrm_bulk_client import BulkAPI
        
        # These should all work without errors
        assert Client is not None
        assert BulkJobCreateRequest is not None
        assert BulkAPI is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
