# /sdk/py/papi-sdk/tests/test_basic.py
"""
Basic tests for PAPI SDK - Just the essentials with stable models
"""

import pytest
from unittest.mock import Mock, patch


def test_imports_work():
    """Test that basic imports work including stable models"""
    from papi_sdk import Client, AuthClient, BulkAPI
    from papi_sdk.models import BulkJobCreateRequest, BulkJobCreateResponse
    from papi_sdk.converters import to_bulk_job_create_response, from_bulk_job_create_request
    
    assert Client is not None
    assert AuthClient is not None
    assert BulkAPI is not None
    assert BulkJobCreateRequest is not None
    assert BulkJobCreateResponse is not None
    assert to_bulk_job_create_response is not None
    assert from_bulk_job_create_request is not None


def test_stable_models_creation():
    """Test that stable models can be created"""
    from papi_sdk.models import BulkJobCreateRequest, BulkJobCreateResponse, BulkJobInfoResponse
    
    # Test request model
    request = BulkJobCreateRequest(
        object="Account",
        operation="insert"
    )
    assert request.object == "Account"
    assert request.operation == "insert"
    assert request.external_id_field_name is None
    
    # Test response model
    response = BulkJobCreateResponse(
        id="test-job-123",
        state="Open",
        object="Account",
        operation="insert"
    )
    assert response.id == "test-job-123"
    assert response.state == "Open"
    
    # Test info response model
    info = BulkJobInfoResponse(
        id="info-job-123",
        state="JobComplete",
        number_records_processed=100,
        number_records_succeeded=95,
        number_records_failed=5
    )
    assert info.id == "info-job-123"
    assert info.state == "JobComplete"
    assert info.number_records_processed == 100


@patch('papi_sdk.client.AuthClient')
def test_client_creation(mock_auth):
    """Test client can be created"""
    mock_auth_instance = Mock()
    mock_auth_instance.get_token.return_value = "test-token"
    mock_auth.return_value = mock_auth_instance
    
    from papi_sdk import Client
    
    client = Client(
        client_id="test-id",
        client_secret="test-secret",
        environment="stg"
    )
    
    assert client.environment == "stg"
    assert "stg" in client.base_url
    assert hasattr(client, 'vrm_bulk')
    assert hasattr(client, 'bulk')  # Alias


@patch('requests.post')
def test_auth_client(mock_post):
    """Test auth client works"""
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test-token",
        "expires_in": 3600
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    from papi_sdk.auth import AuthClient
    
    client = AuthClient("https://test.com", "id", "secret")
    token = client.get_token()
    
    assert token == "test-token"
    mock_post.assert_called_once()


@patch('http.client.HTTPSConnection')
def test_urllib3_free_auth(mock_conn):
    """Test urllib3-free authentication works"""
    # Mock response
    mock_response = Mock()
    mock_response.status = 200
    mock_response.read.return_value = b'{"access_token": "urllib3-free-token", "expires_in": 3600}'
    
    mock_conn_instance = Mock()
    mock_conn_instance.getresponse.return_value = mock_response
    mock_conn.return_value = mock_conn_instance
    
    from papi_sdk.urllib3_free_auth import Urllib3FreeAuthClient
    
    client = Urllib3FreeAuthClient("https://test.com", "id", "secret")
    client._refresh_token()
    
    assert client._token == "urllib3-free-token"
    mock_conn.assert_called_once()


@patch('papi_sdk.vrm_bulk_client.VrmBulkApi')
@patch('papi_sdk.vrm_bulk_client.from_bulk_job_create_request')
@patch('papi_sdk.vrm_bulk_client.to_bulk_job_create_response')
def test_vrm_bulk_client_with_stable_models(mock_to_converter, mock_from_converter, mock_api):
    """Test VRM bulk client works with stable models"""
    from papi_sdk.vrm_bulk_client import BulkAPI
    from papi_sdk.models import BulkJobCreateResponse
    
    # Mock the generated API
    mock_api_instance = Mock()
    mock_generated_job = Mock()
    mock_generated_job.id = "job-123"
    mock_generated_job.state = "Open"
    mock_api_instance.vrm_v1_jobs_ingest_post.return_value = mock_generated_job
    mock_api.return_value = mock_api_instance
    
    # Mock converters
    mock_generated_request = Mock()
    mock_from_converter.return_value = mock_generated_request
    
    stable_response = BulkJobCreateResponse(
        id="job-123",
        state="Open",
        object="Account",
        operation="insert"
    )
    mock_to_converter.return_value = stable_response
    
    # Test the client
    mock_api_client = Mock()
    client = BulkAPI(mock_api_client)
    result = client.create_job("Account", "insert")
    
    # Verify stable model response
    assert result.id == "job-123"
    assert result.state == "Open"
    assert result.object == "Account"
    assert result.operation == "insert"
    
    # Verify conversion chain
    mock_from_converter.assert_called_once()
    mock_api_instance.vrm_v1_jobs_ingest_post.assert_called_once()
    mock_to_converter.assert_called_once_with(mock_generated_job)


def test_converter_functions():
    """Test converter functions work"""
    from papi_sdk.models import BulkJobCreateRequest
    from papi_sdk.converters import from_bulk_job_create_request, to_bulk_job_create_response
    
    # Test stable -> generated conversion
    stable_request = BulkJobCreateRequest(
        object="Contact",
        operation="upsert",
        external_id_field_name="Email"
    )
    
    generated_request = from_bulk_job_create_request(stable_request)
    assert generated_request.object == "Contact"
    assert generated_request.operation == "upsert"
    assert generated_request.external_id_field_name == "Email"
    
    # Test generated -> stable conversion
    mock_generated_response = Mock()
    mock_generated_response.id = "conv-job-123"
    mock_generated_response.state = "Open"
    mock_generated_response.object = "Contact" 
    mock_generated_response.operation = "upsert"
    # Set all other required fields to None
    for field in ['api_version', 'concurrency_mode', 'content_url', 'created_by_id', 
                  'created_date', 'job_type', 'system_modstamp', 'assignment_rule',
                  'column_delimiter', 'content_type', 'external_id_field_name', 'line_ending']:
        setattr(mock_generated_response, field, None)
    
    stable_response = to_bulk_job_create_response(mock_generated_response)
    assert stable_response.id == "conv-job-123"
    assert stable_response.state == "Open"
    assert stable_response.object == "Contact"
    assert stable_response.operation == "upsert"


@patch('papi_sdk.client.AuthClient')  
@patch('papi_sdk.client.BulkAPI')
def test_full_workflow_with_stable_models(mock_vrm, mock_auth):
    """Test complete workflow works with stable models"""
    # Mock auth
    mock_auth_instance = Mock()
    mock_auth_instance.get_token.return_value = "workflow-token"
    mock_auth.return_value = mock_auth_instance
    
    # Import stable models
    from papi_sdk.models import BulkJobCreateResponse, BulkJobUpdateResponse
    
    # Mock VRM with stable model responses
    mock_vrm_instance = Mock()
    
    stable_job = BulkJobCreateResponse(
        id="workflow-job",
        state="Open",
        object="Contact",
        operation="insert"
    )
    mock_vrm_instance.create_job.return_value = stable_job
    mock_vrm_instance.upload_job_data.return_value = None
    
    stable_close_response = BulkJobUpdateResponse(
        id="workflow-job",
        state="UploadComplete"
    )
    mock_vrm_instance.close_job.return_value = stable_close_response
    mock_vrm.return_value = mock_vrm_instance
    
    from papi_sdk import Client
    
    # Create client
    client = Client(
        client_id="workflow-id",
        client_secret="workflow-secret",
        environment="stg"
    )
    
    # Create job
    job = client.vrm_bulk.create_job("Contact", "insert")
    assert job.id == "workflow-job"
    assert job.state == "Open"
    assert job.object == "Contact"
    assert job.operation == "insert"
    
    # Upload data
    client.vrm_bulk.upload_job_data(job.id, "Name,Email\nTest,test@test.com")
    
    # Close job
    result = client.vrm_bulk.close_job(job.id)
    assert result.state == "UploadComplete"
    assert result.id == "workflow-job"
    
    # Verify calls with stable models
    mock_vrm_instance.create_job.assert_called_once_with("Contact", "insert")
    mock_vrm_instance.upload_job_data.assert_called_once_with("workflow-job", "Name,Email\nTest,test@test.com")
    mock_vrm_instance.close_job.assert_called_once_with("workflow-job")


def test_bulk_api_methods_exist():
    """Test that all expected BulkAPI methods exist"""
    from papi_sdk.vrm_bulk_client import BulkAPI
    
    mock_api_client = Mock()
    client = BulkAPI(mock_api_client)
    
    # Check all expected methods exist
    expected_methods = [
        'create_job', 'get_all_jobs', 'get_job_info', 'delete_job',
        'upload_job_data', 'close_job', 'get_successful_results',
        'get_failed_results', 'get_unprocessed_records',
        'list_available_methods', 'get_job_results_summary'
    ]
    
    for method in expected_methods:
        assert hasattr(client, method), f"BulkAPI missing method: {method}"
        assert callable(getattr(client, method)), f"BulkAPI.{method} is not callable"


def test_environment_urls():
    """Test that different environments map to correct URLs"""
    from papi_sdk.client import Client
    
    # Test different environment mappings
    test_cases = [
        ("prod", "https://platformapi.salesforce.deliveryhero.io"),
        ("stg", "https://platformapi-stg.salesforce.deliveryhero.io"),
        ("dev", "https://platformapi-dev.salesforce.deliveryhero.io")
    ]
    
    for env, expected_url in test_cases:
        with patch('papi_sdk.client.AuthClient'):
            client = Client(
                client_id="test-id",
                client_secret="test-secret", 
                environment=env
            )
            assert client.base_url == expected_url
            assert client.environment == env


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
