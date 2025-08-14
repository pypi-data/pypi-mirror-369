import json
import botocore.exceptions

from sagemaker_jupyterlab_emr_extension.utils.logging_utils import (
    EmrErrorHandler,
)


def test_get_error_message_from_client():
    """Given"""
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": "SomeServiceException",
                "Message": "Details/context around the exception or error",
            },
            "ResponseMetadata": {
                "RequestId": "1234567890ABCDEF",
                "HostId": "host ID data will appear here as a hash",
                "HTTPStatusCode": 400,
                "HTTPHeaders": {"header metadata key/values will appear here"},
                "RetryAttempts": 0,
            },
        },
        "AWSSERVICEOPERATION",
    )

    expected_result = {
        "http_code": 400,
        "message": {
            "code": "SomeServiceException",
            "errorMessage": "Details/context around the exception or error",
        },
    }
    """When"""
    actual_result = EmrErrorHandler.get_boto_error(error)

    """Then"""
    assert expected_result == actual_result
