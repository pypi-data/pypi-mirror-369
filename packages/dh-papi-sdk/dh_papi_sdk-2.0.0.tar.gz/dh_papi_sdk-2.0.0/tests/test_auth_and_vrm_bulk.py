# /sdk/py/papi-sdk/tests/test_auth_and_vrm_bulk.py
"""
Fixed tests for Authentication and VRM Bulk Client with stable models
"""

import pytest
import json
from unittest.mock import Mock, patch


class TestAuthentication:
    """Test authentication functionality"""
    
    @patch('requests.post')
    def test_standard_auth_success(self, mock_post):
        """Test standard authentication works"""
        # Mock successful auth response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "auth-token-12345",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        from papi_sdk.auth import AuthClient
        
        auth_client = AuthClient(
            "https://test-api.com", 
            "test-client-id", 
            "test-client-secret"
        )
        
        # Get token should trigger auth
        token = auth_client.get_token()
        
        assert token == "auth-token-12345"
        assert auth_client._token == "auth-token-12345"
        assert auth_client._token_expires is not None
        
        # Verify correct auth request was made
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check the actual params structure
        assert call_args[1]['params']['grant_type'] == 'client_credentials'
        assert call_args[1]['data']['client_id'] == "test-client-id"
        assert call_args[1]['data']['client_secret'] == "test-client-secret"
        assert call_args[1]['headers']['Content-Type'] == "application/x-www-form-urlencoded"
    
    @patch('requests.post')
    def test_standard_auth_error(self, mock_post):
        """Test standard authentication handles errors"""
        # Mock auth failure
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 401: Unauthorized")
        mock_post.return_value = mock_response
        
        from papi_sdk.auth import AuthClient
        
        auth_client = AuthClient("https://test-api.com", "bad-id", "bad-secret")
        
        # Match the actual error message pattern
        with pytest.raises(Exception, match="Token refresh failed"):
            auth_client.get_token()
    
    @patch('http.client.HTTPSConnection')
    def test_urllib3_free_auth_success(self, mock_https_conn):
        """Test urllib3-free authentication works"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.reason = "OK"
        mock_response.read.return_value = json.dumps({
            "access_token": "urllib3-free-token-67890",
            "expires_in": 7200,
            "token_type": "Bearer"
        }).encode('utf-8')
        
        mock_conn_instance = Mock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_https_conn.return_value = mock_conn_instance
        
        from papi_sdk.urllib3_free_auth import Urllib3FreeAuthClient
        
        auth_client = Urllib3FreeAuthClient(
            "https://test-api.com", 
            "test-client-id", 
            "test-client-secret"
        )
        
        # Test token refresh
        auth_client._refresh_token()
        
        assert auth_client._token == "urllib3-free-token-67890"
        assert auth_client._token_expires is not None
        
        # Verify http.client was used correctly
        mock_https_conn.assert_called_once()
        mock_conn_instance.request.assert_called_once()
        mock_conn_instance.close.assert_called_once()
        
        # Check request details
        request_call = mock_conn_instance.request.call_args[0]
        assert request_call[0] == "POST"  # HTTP method
        assert "/auth/v2/token" in request_call[1]  # URL path
    
    @patch('http.client.HTTPSConnection')
    def test_urllib3_free_auth_error(self, mock_https_conn):
        """Test urllib3-free authentication handles errors"""
        # Mock auth failure
        mock_response = Mock()
        mock_response.status = 401
        mock_response.reason = "Unauthorized"
        mock_response.read.return_value = b'{"error": "invalid_client"}'
        
        mock_conn_instance = Mock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_https_conn.return_value = mock_conn_instance
        
        from papi_sdk.urllib3_free_auth import Urllib3FreeAuthClient
        
        auth_client = Urllib3FreeAuthClient("https://test-api.com", "bad-id", "bad-secret")
        
        with pytest.raises(Exception, match="HTTP 401: Unauthorized"):
            auth_client._refresh_token()


class TestBulkAPI:
    """Test VRM Bulk Client functionality with stable models"""
    
    @patch('papi_sdk.vrm_bulk_client.VrmBulkApi')
    @patch('papi_sdk.vrm_bulk_client.from_bulk_job_create_request')
    @patch('papi_sdk.vrm_bulk_client.to_bulk_job_create_response')
    def test_create_job(self, mock_to_converter, mock_from_converter, mock_vrm_api):
        """Test creating a bulk job with stable models"""
        # Mock the generated API response
        mock_generated_response = Mock()
        mock_generated_response.id = "bulk-job-12345"
        mock_generated_response.state = "Open"
        mock_generated_response.object = "Account"
        mock_generated_response.operation = "insert"
        
        # Mock the generated API
        mock_api_instance = Mock()
        mock_api_instance.vrm_v1_jobs_ingest_post.return_value = mock_generated_response
        mock_vrm_api.return_value = mock_api_instance
        
        # Mock the converters
        mock_generated_request = Mock()
        mock_from_converter.return_value = mock_generated_request
        
        # Import stable models
        from papi_sdk.models import BulkJobCreateResponse
        stable_response = BulkJobCreateResponse(
            id="bulk-job-12345",
            state="Open",
            object="Account",
            operation="insert"
        )
        mock_to_converter.return_value = stable_response
        
        # Test the client
        from papi_sdk.vrm_bulk_client import BulkAPI
        mock_api_client = Mock()
        
        bulk_client = BulkAPI(mock_api_client)
        result = bulk_client.create_job("Account", "insert")
        
        # Assert stable model response
        assert result.id == "bulk-job-12345"
        assert result.state == "Open"
        assert result.object == "Account"
        assert result.operation == "insert"
        
        # Verify the conversion chain was called
        mock_from_converter.assert_called_once()  # Stable -> Generated
        mock_api_instance.vrm_v1_jobs_ingest_post.assert_called_once()  # API call
        mock_to_converter.assert_called_once_with(mock_generated_response)  # Generated -> Stable
    
    @patch('papi_sdk.vrm_bulk_client.VrmBulkApi')
    def test_upload_job_data(self, mock_vrm_api):
        """Test uploading CSV data to a job"""
        mock_api_instance = Mock()
        mock_api_instance.vrm_v1_jobs_ingest_job_id_batches_put.return_value = None
        mock_vrm_api.return_value = mock_api_instance
        
        from papi_sdk.vrm_bulk_client import BulkAPI
        mock_api_client = Mock()
        
        bulk_client = BulkAPI(mock_api_client)
        csv_data = """Name,Type,Industry
"Test Corp","Customer","Technology"
"Demo Ltd","Partner","Retail"
"""
        
        result = bulk_client.upload_job_data("bulk-job-12345", csv_data)
        
        assert result is None  # Upload returns None on success
        
        # Verify API was called with correct data
        mock_api_instance.vrm_v1_jobs_ingest_job_id_batches_put.assert_called_once_with(
            job_id="bulk-job-12345",
            body=csv_data
        )
    
    @patch('papi_sdk.vrm_bulk_client.VrmBulkApi')
    @patch('papi_sdk.vrm_bulk_client.from_bulk_job_update_request')
    @patch('papi_sdk.vrm_bulk_client.to_bulk_job_update_response')
    def test_close_job(self, mock_to_converter, mock_from_converter, mock_vrm_api):
        """Test closing a job for processing with stable models"""
        # Mock generated API response
        mock_generated_response = Mock()
        mock_generated_response.state = "UploadComplete"
        mock_generated_response.id = "bulk-job-12345"
        
        mock_api_instance = Mock()
        mock_api_instance.vrm_v1_jobs_ingest_job_id_patch.return_value = mock_generated_response
        mock_vrm_api.return_value = mock_api_instance
        
        # Mock converters
        mock_generated_request = Mock()
        mock_from_converter.return_value = mock_generated_request
        
        from papi_sdk.models import BulkJobUpdateResponse
        stable_response = BulkJobUpdateResponse(
            state="UploadComplete",
            id="bulk-job-12345"
        )
        mock_to_converter.return_value = stable_response
        
        # Test the client
        from papi_sdk.vrm_bulk_client import BulkAPI
        mock_api_client = Mock()
        
        bulk_client = BulkAPI(mock_api_client)
        result = bulk_client.close_job("bulk-job-12345")
        
        # Assert stable model response
        assert result.state == "UploadComplete"
        assert result.id == "bulk-job-12345"
        
        # Verify the conversion chain
        mock_from_converter.assert_called_once()  # Stable -> Generated
        mock_api_instance.vrm_v1_jobs_ingest_job_id_patch.assert_called_once()  # API call
        mock_to_converter.assert_called_once_with(mock_generated_response)  # Generated -> Stable
    
    @patch('papi_sdk.vrm_bulk_client.VrmBulkApi')
    @patch('papi_sdk.vrm_bulk_client.to_bulk_job_info_response')
    def test_get_job_info(self, mock_to_converter, mock_vrm_api):
        """Test getting job status information with stable models"""
        # Mock generated API response
        mock_generated_response = Mock()
        mock_generated_response.id = "bulk-job-12345"
        mock_generated_response.state = "JobComplete"
        mock_generated_response.object = "Account"
        mock_generated_response.operation = "insert"
        mock_generated_response.created_date = "2023-01-01T12:00:00Z"
        mock_generated_response.number_records_processed = 100
        mock_generated_response.number_records_succeeded = 95
        mock_generated_response.number_records_failed = 5
        
        mock_api_instance = Mock()
        mock_api_instance.vrm_v1_jobs_ingest_job_id_get.return_value = mock_generated_response
        mock_vrm_api.return_value = mock_api_instance
        
        # Mock converter
        from papi_sdk.models import BulkJobInfoResponse
        stable_response = BulkJobInfoResponse(
            id="bulk-job-12345",
            state="JobComplete",
            object="Account",
            operation="insert",
            created_date="2023-01-01T12:00:00Z",
            number_records_processed=100,
            number_records_succeeded=95,
            number_records_failed=5
        )
        mock_to_converter.return_value = stable_response
        
        # Test the client
        from papi_sdk.vrm_bulk_client import BulkAPI
        mock_api_client = Mock()
        
        bulk_client = BulkAPI(mock_api_client)
        result = bulk_client.get_job_info("bulk-job-12345")
        
        # Assert stable model response
        assert result.id == "bulk-job-12345"
        assert result.state == "JobComplete"
        assert result.object == "Account"
        assert result.operation == "insert"
        assert result.number_records_processed == 100
        assert result.number_records_succeeded == 95
        assert result.number_records_failed == 5
        
        # Verify API call and conversion
        mock_api_instance.vrm_v1_jobs_ingest_job_id_get.assert_called_once_with(
            job_id="bulk-job-12345"
        )
        mock_to_converter.assert_called_once_with(mock_generated_response)


class TestStableModels:
    """Test stable model creation and validation"""
    
    def test_bulk_job_create_request(self):
        """Test BulkJobCreateRequest creation"""
        from papi_sdk.models import BulkJobCreateRequest
        
        request = BulkJobCreateRequest(
            object="Account",
            operation="insert",
            external_id_field_name="External_ID__c"
        )
        
        assert request.object == "Account"
        assert request.operation == "insert"
        assert request.external_id_field_name == "External_ID__c"
    
    def test_bulk_job_create_response(self):
        """Test BulkJobCreateResponse creation"""
        from papi_sdk.models import BulkJobCreateResponse
        
        response = BulkJobCreateResponse(
            id="job-123",
            state="Open",
            object="Contact",
            operation="upsert"
        )
        
        assert response.id == "job-123"
        assert response.state == "Open"
        assert response.object == "Contact"
        assert response.operation == "upsert"


class TestConverters:
    """Test converter functions work correctly"""
    
    def test_from_bulk_job_create_request(self):
        """Test converting stable request to generated request"""
        from papi_sdk.models import BulkJobCreateRequest
        from papi_sdk.converters import from_bulk_job_create_request
        
        stable_request = BulkJobCreateRequest(
            object="Account",
            operation="insert"
        )
        
        # This will call the actual converter
        generated_request = from_bulk_job_create_request(stable_request)
        
        # Verify the conversion worked
        assert generated_request.object == "Account"
        assert generated_request.operation == "insert"
    
    def test_to_bulk_job_create_response(self):
        """Test converting generated response to stable response"""
        from papi_sdk.converters import to_bulk_job_create_response
        
        # Mock a generated response
        mock_generated = Mock()
        mock_generated.id = "test-job-123"
        mock_generated.state = "Open"
        mock_generated.object = "Account"
        mock_generated.operation = "insert"
        mock_generated.api_version = None
        mock_generated.concurrency_mode = None
        mock_generated.content_url = None
        mock_generated.created_by_id = None
        mock_generated.created_date = None
        mock_generated.job_type = None
        mock_generated.system_modstamp = None
        mock_generated.assignment_rule = None
        mock_generated.column_delimiter = None
        mock_generated.content_type = None
        mock_generated.external_id_field_name = None
        mock_generated.line_ending = None
        
        stable_response = to_bulk_job_create_response(mock_generated)
        
        # Verify the conversion
        assert stable_response.id == "test-job-123"
        assert stable_response.state == "Open"
        assert stable_response.object == "Account"
        assert stable_response.operation == "insert"


class TestIntegratedWorkflow:
    """Test complete workflow with auth + VRM operations using stable models"""
    
    @patch('papi_sdk.client.AuthClient')
    @patch('papi_sdk.client.BulkAPI')
    def test_complete_bulk_workflow_stable_models(self, mock_vrm_bulk_class, mock_auth_class):
        """Test complete workflow with stable models"""
        
        # Mock authentication
        mock_auth_instance = Mock()
        mock_auth_instance.get_token.return_value = "workflow-token-12345"
        mock_auth_class.return_value = mock_auth_instance
        
        # Mock VRM bulk operations with stable models
        mock_vrm_instance = Mock()
        
        # Import stable models for responses
        from papi_sdk.models import (
            BulkJobCreateResponse, 
            BulkJobUpdateResponse, 
            BulkJobInfoResponse
        )
        
        # Create job response
        mock_job = BulkJobCreateResponse(
            id="workflow-job-12345",
            state="Open",
            object="Contact",
            operation="upsert"
        )
        mock_vrm_instance.create_job.return_value = mock_job
        
        # Upload response (None = success)
        mock_vrm_instance.upload_job_data.return_value = None
        
        # Close job response
        mock_close_result = BulkJobUpdateResponse(
            id="workflow-job-12345",
            state="UploadComplete"
        )
        mock_vrm_instance.close_job.return_value = mock_close_result
        
        # Job status response
        mock_job_status = BulkJobInfoResponse(
            id="workflow-job-12345",
            state="JobComplete",
            object="Contact",
            operation="upsert",
            number_records_processed=2,
            number_records_succeeded=2,
            number_records_failed=0
        )
        mock_vrm_instance.get_job_info.return_value = mock_job_status
        
        mock_vrm_bulk_class.return_value = mock_vrm_instance
        
        from papi_sdk import Client
        
        # Initialize client
        client = Client(
            client_id="workflow-test-id",
            client_secret="workflow-test-secret",
            environment="stg"
        )
        
        # Step 1: Create bulk job
        job = client.vrm_bulk.create_job("Contact", "upsert", "Email")
        assert job.id == "workflow-job-12345"
        assert job.state == "Open"
        assert job.object == "Contact"
        assert job.operation == "upsert"
        
        # Step 2: Upload CSV data
        csv_data = """FirstName,LastName,Email
John,Doe,john.doe@example.com
Jane,Smith,jane.smith@example.com
"""
        client.vrm_bulk.upload_job_data(job.id, csv_data)
        
        # Step 3: Close job for processing
        close_result = client.vrm_bulk.close_job(job.id)
        assert close_result.state == "UploadComplete"
        assert close_result.id == "workflow-job-12345"
        
        # Step 4: Check job status
        job_status = client.vrm_bulk.get_job_info(job.id)
        assert job_status.id == "workflow-job-12345"
        assert job_status.state == "JobComplete"
        assert job_status.number_records_processed == 2
        assert job_status.number_records_succeeded == 2
        assert job_status.number_records_failed == 0
        
        # Verify all operations were called with correct parameters
        mock_vrm_instance.create_job.assert_called_once_with("Contact", "upsert", "Email")
        mock_vrm_instance.upload_job_data.assert_called_once_with(job.id, csv_data)
        mock_vrm_instance.close_job.assert_called_once_with(job.id)
        mock_vrm_instance.get_job_info.assert_called_once_with(job.id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
